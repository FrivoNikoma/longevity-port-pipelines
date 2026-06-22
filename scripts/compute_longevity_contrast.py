from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import polars as pl

from longevity_port_pipelines.config import LONG_LIVED_SPECIES, SHORT_LIVED_SPECIES

DEFAULT_SHORT_LIVED_SPECIES = [species.name for species in SHORT_LIVED_SPECIES]
DEFAULT_LONG_LIVED_SPECIES = [species.name for species in LONG_LIVED_SPECIES]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Compute long-lived-vs-short-lived contrast from mapped enrichment outputs.")
    )
    parser.add_argument(
        "--input",
        default="data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet",
        help="Input mapped enrichment parquet path.",
    )
    parser.add_argument(
        "--output-csv",
        default="data/output/sirt6_mini_pilot_v2_longevity_contrast.csv",
        help="Output longevity contrast CSV path.",
    )
    parser.add_argument(
        "--output-md",
        default="data/output/sirt6_mini_pilot_v2_longevity_contrast.md",
        help="Output longevity contrast Markdown path.",
    )
    parser.add_argument(
        "--short-lived-species",
        nargs="+",
        default=DEFAULT_SHORT_LIVED_SPECIES,
        help=(
            "Short-lived control species used to build an aggregated baseline. "
            "Defaults to all short-lived species registered in config."
        ),
    )
    parser.add_argument(
        "--long-lived-species",
        nargs="+",
        default=DEFAULT_LONG_LIVED_SPECIES,
        help=(
            "Long-lived species to compare against the short-lived baseline. "
            "Defaults to all long-lived species registered in config."
        ),
    )
    parser.add_argument(
        "--divergent-threshold",
        type=float,
        default=1.2,
        help="Enrichment ratio threshold for interface divergence.",
    )
    parser.add_argument(
        "--constrained-threshold",
        type=float,
        default=0.8,
        help="Enrichment ratio threshold for interface constraint.",
    )
    parser.add_argument(
        "--baseline-neutral-upper",
        type=float,
        default=1.1,
        help="Upper enrichment ratio bound for a near-neutral short-lived baseline.",
    )
    parser.add_argument(
        "--baseline-neutral-lower",
        type=float,
        default=0.9,
        help="Lower enrichment ratio bound for a near-neutral short-lived baseline.",
    )
    parser.add_argument(
        "--min-enrichment-delta",
        type=float,
        default=0.2,
        help="Minimum long-vs-short enrichment-ratio difference for a species-specific call.",
    )
    parser.add_argument(
        "--min-abs-effect",
        type=float,
        default=0.2,
        help="Minimum absolute Cohen's d for directional contrast classes.",
    )
    return parser.parse_args()


def require_columns(df: pl.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def add_p_two_sided_if_missing(df: pl.DataFrame) -> pl.DataFrame:
    if "p_two_sided" in df.columns:
        return df

    if "mann_whitney_p" not in df.columns:
        return df.with_columns(pl.lit(None).cast(pl.Float64).alias("p_two_sided"))

    return df.with_columns(
        (2.0 * pl.col("mann_whitney_p").clip(0.0, 0.5)).clip(0.0, 1.0).alias("p_two_sided")
    )


def prefixed_species_frame(
    df: pl.DataFrame,
    *,
    prefix: str,
    species_column: str,
) -> pl.DataFrame:
    optional_columns = [
        "interface_mean_delta",
        "noninterface_mean_delta",
        "enrichment_ratio",
        "effect_size_cohens_d",
        "p_two_sided",
        "mann_whitney_p",
        "is_predicted_structure",
    ]

    selected = ["complex_id", "chain", "target_species"]
    selected.extend(column for column in optional_columns if column in df.columns)

    rename_map = {
        "target_species": species_column,
        "interface_mean_delta": f"{prefix}_interface_mean_delta",
        "noninterface_mean_delta": f"{prefix}_noninterface_mean_delta",
        "enrichment_ratio": f"{prefix}_enrichment_ratio",
        "effect_size_cohens_d": f"{prefix}_effect_size",
        "p_two_sided": f"{prefix}_p_two_sided",
        "mann_whitney_p": f"{prefix}_mann_whitney_p",
        "is_predicted_structure": f"{prefix}_is_predicted_structure",
    }

    return df.select(selected).rename(
        {old: new for old, new in rename_map.items() if old in selected}
    )


def safe_float(value: Any) -> float:
    if value is None:
        return float("nan")
    return float(value)


def safe_log2_ratio(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        return float("nan")
    if numerator <= 0.0 or denominator <= 0.0:
        return float("nan")
    return math.log2(numerator / denominator)


def is_divergent(
    ratio: float, effect: float, ratio_threshold: float, effect_threshold: float
) -> bool:
    return ratio >= ratio_threshold and effect >= effect_threshold


def is_constrained(
    ratio: float,
    effect: float,
    ratio_threshold: float,
    effect_threshold: float,
) -> bool:
    return ratio <= ratio_threshold and effect <= -effect_threshold


def classify_contrast(
    *,
    long_ratio: float,
    short_ratio: float,
    long_effect: float,
    short_effect: float,
    divergent_threshold: float,
    constrained_threshold: float,
    baseline_neutral_upper: float,
    baseline_neutral_lower: float,
    min_enrichment_delta: float,
    min_abs_effect: float,
) -> tuple[str, str]:
    # NOTE: the enrichment_delta vs min_enrichment_delta comparison below is exact
    # (>=). Under IEEE-754, nominal-boundary subtractions evaluate just under the
    # threshold (e.g. 1.3 - 1.1 == 0.19999999999999996 < 0.2), so such pairs fall
    # through from "specific" to "enhanced" rather than classifying as "specific".
    # This boundary behavior is locked in by tests/test_compute_longevity_contrast.py.
    enrichment_delta = long_ratio - short_ratio

    long_divergent = is_divergent(
        long_ratio,
        long_effect,
        divergent_threshold,
        min_abs_effect,
    )
    short_divergent = is_divergent(
        short_ratio,
        short_effect,
        divergent_threshold,
        min_abs_effect,
    )
    long_constrained = is_constrained(
        long_ratio,
        long_effect,
        constrained_threshold,
        min_abs_effect,
    )
    short_constrained = is_constrained(
        short_ratio,
        short_effect,
        constrained_threshold,
        min_abs_effect,
    )

    if long_divergent:
        if short_divergent:
            return (
                "shared_nonhuman_interface_divergence",
                "Long-lived and short-lived orthologs both show interface-enriched divergence.",
            )

        if short_ratio <= baseline_neutral_upper and enrichment_delta >= min_enrichment_delta:
            return (
                "long_lived_specific_interface_divergence",
                "Long-lived ortholog shows interface-enriched divergence relative to a near-neutral short-lived baseline.",
            )

        return (
            "long_lived_enhanced_interface_divergence",
            "Long-lived ortholog shows stronger interface-enriched divergence than the short-lived baseline.",
        )

    if long_constrained:
        if short_constrained:
            return (
                "shared_interface_constraint",
                "Long-lived and short-lived orthologs both show interface constraint.",
            )

        if short_ratio >= baseline_neutral_lower and -enrichment_delta >= min_enrichment_delta:
            return (
                "long_lived_specific_interface_constraint",
                "Long-lived ortholog shows interface constraint relative to a near-neutral short-lived baseline.",
            )

        return (
            "long_lived_enhanced_interface_constraint",
            "Long-lived ortholog shows stronger interface constraint than the short-lived baseline.",
        )

    if short_divergent or short_constrained:
        return (
            "short_lived_baseline_stronger_signal",
            "Short-lived baseline has the stronger directional interface signal.",
        )

    return (
        "weak_or_unresolved_contrast",
        "No clear long-lived-vs-short-lived directional contrast under current thresholds.",
    )


def class_priority(contrast_class: str) -> int:
    priorities = {
        "long_lived_specific_interface_divergence": 1,
        "long_lived_enhanced_interface_divergence": 2,
        "long_lived_specific_interface_constraint": 3,
        "long_lived_enhanced_interface_constraint": 4,
        "shared_nonhuman_interface_divergence": 5,
        "shared_interface_constraint": 6,
        "short_lived_baseline_stronger_signal": 7,
        "weak_or_unresolved_contrast": 8,
    }
    return priorities.get(contrast_class, 99)


def normalize_species_names(species: str | list[str]) -> list[str]:
    """Normalize CLI/test species arguments to a list of species names."""
    if isinstance(species, str):
        return [species]
    return list(species)


def mean_numeric(rows: list[dict[str, Any]], column: str) -> float:
    values = []
    for row in rows:
        value = safe_float(row.get(column))
        if not math.isnan(value):
            values.append(value)
    if not values:
        return math.nan
    return sum(values) / len(values)


def aggregate_short_lived_controls(short_df: pl.DataFrame) -> pl.DataFrame:
    """Aggregate available short-lived controls per complex/chain baseline."""
    records: list[dict[str, Any]] = []

    for (complex_id, chain), group in short_df.group_by(
        ["complex_id", "chain"], maintain_order=True
    ):
        rows = list(group.iter_rows(named=True))
        species_present = sorted({str(row["target_species"]) for row in rows})

        record: dict[str, Any] = {
            "complex_id": complex_id,
            "chain": chain,
            "target_species": ",".join(species_present),
            "short_lived_control_count": len(species_present),
            "interface_mean_delta": mean_numeric(rows, "interface_mean_delta"),
            "noninterface_mean_delta": mean_numeric(rows, "noninterface_mean_delta"),
            "enrichment_ratio": mean_numeric(rows, "enrichment_ratio"),
            "effect_size_cohens_d": mean_numeric(rows, "effect_size_cohens_d"),
        }

        if "p_two_sided" in short_df.columns:
            record["p_two_sided"] = mean_numeric(rows, "p_two_sided")

        if "is_predicted_structure" in short_df.columns:
            record["is_predicted_structure"] = any(
                bool(row.get("is_predicted_structure"))
                for row in rows
                if row.get("is_predicted_structure") is not None
            )

        records.append(record)

    return pl.DataFrame(records)


def prefixed_short_lived_baseline_frame(short_df: pl.DataFrame) -> pl.DataFrame:
    """Rename aggregated short-lived baseline columns to the short_* namespace."""
    rename_map = {
        "target_species": "short_lived_species",
        "interface_mean_delta": "short_interface_mean_delta",
        "noninterface_mean_delta": "short_noninterface_mean_delta",
        "enrichment_ratio": "short_enrichment_ratio",
        "effect_size_cohens_d": "short_effect_size",
        "p_two_sided": "short_p_two_sided",
        "is_predicted_structure": "short_is_predicted_structure",
    }
    columns = [
        "complex_id",
        "chain",
        "target_species",
        "short_lived_control_count",
        "interface_mean_delta",
        "noninterface_mean_delta",
        "enrichment_ratio",
        "effect_size_cohens_d",
        "p_two_sided",
        "is_predicted_structure",
    ]
    selected = [column for column in columns if column in short_df.columns]
    return short_df.select(selected).rename(
        {old: new for old, new in rename_map.items() if old in selected}
    )


def build_longevity_contrast(
    df: pl.DataFrame,
    *,
    short_lived_species: str | list[str],
    long_lived_species: list[str],
    divergent_threshold: float,
    constrained_threshold: float,
    baseline_neutral_upper: float,
    baseline_neutral_lower: float,
    min_enrichment_delta: float,
    min_abs_effect: float,
) -> pl.DataFrame:
    require_columns(
        df,
        [
            "complex_id",
            "chain",
            "target_species",
            "interface_mean_delta",
            "noninterface_mean_delta",
            "enrichment_ratio",
            "effect_size_cohens_d",
        ],
    )

    df = add_p_two_sided_if_missing(df)

    short_lived_species_names = normalize_species_names(short_lived_species)
    long_lived_species_names = normalize_species_names(long_lived_species)

    short_df = df.filter(pl.col("target_species").is_in(short_lived_species_names))
    long_df = df.filter(pl.col("target_species").is_in(long_lived_species_names))

    if short_df.is_empty():
        raise ValueError(f"No rows found for short-lived controls: {short_lived_species_names}")

    if long_df.is_empty():
        raise ValueError(f"No rows found for long-lived species: {long_lived_species_names}")

    short_aggregated = aggregate_short_lived_controls(short_df)
    short_prefixed = prefixed_short_lived_baseline_frame(short_aggregated)
    long_prefixed = prefixed_species_frame(
        long_df,
        prefix="long",
        species_column="long_lived_species",
    )

    joined = long_prefixed.join(short_prefixed, on=["complex_id", "chain"], how="inner")

    records: list[dict[str, Any]] = []

    for row in joined.iter_rows(named=True):
        long_ratio = safe_float(row["long_enrichment_ratio"])
        short_ratio = safe_float(row["short_enrichment_ratio"])
        long_effect = safe_float(row["long_effect_size"])
        short_effect = safe_float(row["short_effect_size"])
        enrichment_delta = long_ratio - short_ratio
        effect_size_delta = long_effect - short_effect

        contrast_class, contrast_note = classify_contrast(
            long_ratio=long_ratio,
            short_ratio=short_ratio,
            long_effect=long_effect,
            short_effect=short_effect,
            divergent_threshold=divergent_threshold,
            constrained_threshold=constrained_threshold,
            baseline_neutral_upper=baseline_neutral_upper,
            baseline_neutral_lower=baseline_neutral_lower,
            min_enrichment_delta=min_enrichment_delta,
            min_abs_effect=min_abs_effect,
        )

        record = {
            "complex_id": row["complex_id"],
            "pdb_id": str(row["complex_id"]).split("__", maxsplit=1)[0],
            "chain": row["chain"],
            "long_lived_species": row["long_lived_species"],
            "short_lived_species": row["short_lived_species"],
            "short_lived_control_count": row["short_lived_control_count"],
            "long_enrichment_ratio": long_ratio,
            "short_enrichment_ratio": short_ratio,
            "enrichment_delta": enrichment_delta,
            "enrichment_log2_ratio": safe_log2_ratio(long_ratio, short_ratio),
            "long_effect_size": long_effect,
            "short_effect_size": short_effect,
            "effect_size_delta": effect_size_delta,
            "long_interface_mean_delta": safe_float(row["long_interface_mean_delta"]),
            "short_interface_mean_delta": safe_float(row["short_interface_mean_delta"]),
            "interface_mean_delta_delta": safe_float(row["long_interface_mean_delta"])
            - safe_float(row["short_interface_mean_delta"]),
            "long_noninterface_mean_delta": safe_float(row["long_noninterface_mean_delta"]),
            "short_noninterface_mean_delta": safe_float(row["short_noninterface_mean_delta"]),
            "noninterface_mean_delta_delta": safe_float(row["long_noninterface_mean_delta"])
            - safe_float(row["short_noninterface_mean_delta"]),
            "long_p_two_sided": safe_float(row.get("long_p_two_sided")),
            "short_p_two_sided": safe_float(row.get("short_p_two_sided")),
            "long_is_predicted_structure": row.get("long_is_predicted_structure"),
            "short_is_predicted_structure": row.get("short_is_predicted_structure"),
            "contrast_class": contrast_class,
            "contrast_priority": class_priority(contrast_class),
            "contrast_note": contrast_note,
        }
        records.append(record)

    if not records:
        raise ValueError(
            "No long-lived-vs-short-lived contrast rows could be built. "
            "Check species names and complex/chain overlap."
        )

    out = pl.DataFrame(records)
    return out.with_columns(
        [
            pl.col("enrichment_delta").abs().alias("abs_enrichment_delta"),
            pl.col("effect_size_delta").abs().alias("abs_effect_size_delta"),
        ]
    ).sort(
        ["contrast_priority", "abs_enrichment_delta", "abs_effect_size_delta"],
        descending=[False, True, True],
    )


def markdown_table(frame: pl.DataFrame) -> str:
    columns = frame.columns
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")

    for row in frame.iter_rows(named=True):
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                if math.isnan(value):
                    values.append("nan")
                elif abs(value) < 0.001 and value != 0:
                    values.append(f"{value:.3e}")
                else:
                    values.append(f"{value:.6g}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def write_markdown_report(
    contrast: pl.DataFrame,
    *,
    output_path: Path,
    input_path: Path,
    short_lived_species: str | list[str],
    long_lived_species: list[str],
) -> None:
    counts = (
        contrast.group_by("contrast_class")
        .len()
        .sort("len", descending=True)
        .rename({"len": "rows"})
    )

    top = contrast.select(
        [
            "complex_id",
            "chain",
            "long_lived_species",
            "short_lived_species",
            "short_lived_control_count",
            "long_enrichment_ratio",
            "short_enrichment_ratio",
            "enrichment_delta",
            "enrichment_log2_ratio",
            "long_effect_size",
            "short_effect_size",
            "effect_size_delta",
            "contrast_class",
        ]
    ).head(20)

    short_lived_species_names = normalize_species_names(short_lived_species)

    lines = [
        "# SIRT6 mini-pilot v2 longevity contrast",
        "",
        f"Input: `{input_path}`",
        f"Short-lived controls: `{', '.join(short_lived_species_names)}`",
        f"Long-lived species: `{', '.join(long_lived_species)}`",
        "",
        "This report compares long-lived species rows against an aggregated short-lived control baseline within each `complex_id + chain` group.",
        "",
        "The goal is to separate shared non-human interface divergence from candidate longevity-specific interface signals.",
        "",
        "## Contrast class counts",
        "",
        markdown_table(counts),
        "",
        "## Top contrast rows",
        "",
        markdown_table(top),
        "",
        "## Interpretation notes",
        "",
        "- `long_lived_specific_interface_divergence`: long-lived species shows interface-enriched divergence while the short-lived baseline is near neutral.",
        "- `long_lived_enhanced_interface_divergence`: long-lived species shows stronger divergence than the short-lived baseline, but the baseline is not fully neutral.",
        "- `shared_nonhuman_interface_divergence`: both long-lived and short-lived species show interface-enriched divergence relative to human.",
        "- `long_lived_specific_interface_constraint`: long-lived species shows interface constraint while the short-lived baseline is near neutral.",
        "- `shared_interface_constraint`: both long-lived and short-lived species show interface constraint.",
        "- `short_lived_baseline_stronger_signal`: the aggregated short-lived baseline has the stronger directional signal.",
        "- `weak_or_unresolved_contrast`: no clear contrast under current thresholds.",
        "",
        "These classes are preliminary prioritization labels. They do not replace NEGATOME-style controls.",
    ]

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_csv = Path(args.output_csv)
    output_md = Path(args.output_md)

    if not input_path.exists():
        raise FileNotFoundError(f"Missing mapped enrichment parquet: {input_path}")

    df = pl.read_parquet(input_path)

    contrast = build_longevity_contrast(
        df,
        short_lived_species=args.short_lived_species,
        long_lived_species=args.long_lived_species,
        divergent_threshold=args.divergent_threshold,
        constrained_threshold=args.constrained_threshold,
        baseline_neutral_upper=args.baseline_neutral_upper,
        baseline_neutral_lower=args.baseline_neutral_lower,
        min_enrichment_delta=args.min_enrichment_delta,
        min_abs_effect=args.min_abs_effect,
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    contrast.write_csv(output_csv)
    write_markdown_report(
        contrast,
        output_path=output_md,
        input_path=input_path,
        short_lived_species=args.short_lived_species,
        long_lived_species=args.long_lived_species,
    )

    print(f"Wrote longevity contrast CSV -> {output_csv}")
    print(f"Wrote longevity contrast Markdown -> {output_md}")

    print()
    print("Contrast class counts:")
    print(contrast.group_by("contrast_class").len().sort("len", descending=True))

    print()
    print("Top contrast rows:")
    print(
        contrast.select(
            [
                "complex_id",
                "chain",
                "long_lived_species",
                "short_lived_species",
                "long_enrichment_ratio",
                "short_enrichment_ratio",
                "enrichment_delta",
                "enrichment_log2_ratio",
                "long_effect_size",
                "short_effect_size",
                "effect_size_delta",
                "contrast_class",
            ]
        ).head(20)
    )


if __name__ == "__main__":
    main()
