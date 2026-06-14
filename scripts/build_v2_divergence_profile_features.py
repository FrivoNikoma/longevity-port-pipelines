from __future__ import annotations

import argparse
import math
import statistics
from pathlib import Path
from typing import Any

import polars as pl

PROFILE_KEY_COLUMNS = [
    "complex_id",
    "pdb_id",
    "chain",
    "source_species",
    "target_species",
    "source_uniprot",
    "target_uniprot",
    "model_name",
    "is_predicted_structure",
]

REQUIRED_RESIDUE_DELTA_COLUMNS = {
    "complex_id",
    "pdb_id",
    "chain",
    "source_species",
    "target_species",
    "source_uniprot",
    "target_uniprot",
    "residue_number_1based",
    "delta",
    "is_interface",
    "model_name",
    "is_predicted_structure",
}

FEATURE_COLUMNS = [
    "interface_mean_delta",
    "noninterface_mean_delta",
    "delta_mean_difference",
    "enrichment_ratio",
    "log2_enrichment_ratio",
    "effect_size_cohens_d_computed",
    "interface_median_delta",
    "noninterface_median_delta",
    "median_difference",
    "interface_q75_delta",
    "noninterface_q75_delta",
    "q75_difference",
    "interface_q90_delta",
    "noninterface_q90_delta",
    "q90_difference",
    "interface_top10_mean_delta",
    "noninterface_top10_mean_delta",
    "top10_mean_difference",
    "interface_max_delta",
    "noninterface_max_delta",
    "max_difference",
    "global_q90_delta",
    "fraction_interface_above_global_q90",
    "interface_fraction_above_global_q90",
    "n_total_residues",
    "n_interface_residues",
    "n_noninterface_residues",
    "interface_fraction",
]

ANNOTATION_COLUMNS = [
    "signal_class",
    "p_interface_greater",
    "p_interface_less",
    "p_two_sided",
    "p_directional",
    "effect_size_cohens_d",
    "biological_context",
    "interpretation",
    "short_lived_species",
    "contrast_class",
    "contrast_priority",
    "contrast_note",
    "enrichment_delta",
    "enrichment_log2_ratio",
    "effect_size_delta",
    "long_enrichment_ratio",
    "short_enrichment_ratio",
    "long_effect_size",
    "short_effect_size",
    "qc_status",
    "remapped_fraction_within_interface_cutoff",
    "remapped_fraction_found",
]

DEFAULT_RESIDUE_DELTAS = "data/output/sirt6_mini_pilot_v2_residue_deltas_mapped.parquet"
DEFAULT_SIGNAL_SUMMARY = "data/output/sirt6_mini_pilot_v2_embedding_signal_summary.csv"
DEFAULT_LONGEVITY_CONTRAST = "data/output/sirt6_mini_pilot_v2_longevity_contrast.csv"
DEFAULT_STRUCTURE_QC = "data/output/sirt6_mini_pilot_v2_structure_selection_qc.csv"
DEFAULT_OUTPUT_CSV = "data/output/sirt6_mini_pilot_v2_divergence_profile_features.csv"
DEFAULT_OUTPUT_PARQUET = "data/output/sirt6_mini_pilot_v2_divergence_profile_features.parquet"
DEFAULT_OUTPUT_MD = "data/output/sirt6_mini_pilot_v2_divergence_profile_features.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build v2 divergence-profile feature vectors from residue-level mapped deltas."
        )
    )
    parser.add_argument(
        "--residue-deltas",
        default=DEFAULT_RESIDUE_DELTAS,
        help="Input residue-level mapped delta parquet.",
    )
    parser.add_argument(
        "--signal-summary",
        default=DEFAULT_SIGNAL_SUMMARY,
        help="Optional embedding signal summary CSV.",
    )
    parser.add_argument(
        "--longevity-contrast",
        default=DEFAULT_LONGEVITY_CONTRAST,
        help="Optional longevity contrast CSV.",
    )
    parser.add_argument(
        "--structure-qc",
        default=DEFAULT_STRUCTURE_QC,
        help="Optional structure-selection QC CSV.",
    )
    parser.add_argument(
        "--output-csv",
        default=DEFAULT_OUTPUT_CSV,
        help="Output divergence-profile feature CSV.",
    )
    parser.add_argument(
        "--output-parquet",
        default=DEFAULT_OUTPUT_PARQUET,
        help="Output divergence-profile feature parquet.",
    )
    parser.add_argument(
        "--output-md",
        default=DEFAULT_OUTPUT_MD,
        help="Output Markdown feature summary.",
    )
    parser.add_argument(
        "--min-interface-residues",
        type=int,
        default=5,
        help="Minimum interface residues for clustering-ready flag.",
    )
    parser.add_argument(
        "--min-noninterface-residues",
        type=int,
        default=20,
        help="Minimum non-interface residues for clustering-ready flag.",
    )
    return parser.parse_args()


def require_columns(frame: pl.DataFrame, required: set[str], path: Path) -> None:
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")


def as_float_list(values: list[Any]) -> list[float]:
    out = []
    for value in values:
        if value is None:
            continue
        number = float(value)
        if math.isfinite(number):
            out.append(number)
    return out


def safe_mean(values: list[float]) -> float | None:
    if not values:
        return None
    return float(sum(values) / len(values))


def safe_median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def safe_quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None

    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return float(sorted_values[0])

    position = q * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])

    lower_value = sorted_values[lower]
    upper_value = sorted_values[upper]
    weight = position - lower
    return float(lower_value * (1.0 - weight) + upper_value * weight)


def safe_max(values: list[float]) -> float | None:
    if not values:
        return None
    return float(max(values))


def safe_top_n_mean(values: list[float], n: int = 10) -> float | None:
    if not values:
        return None
    top_values = sorted(values, reverse=True)[:n]
    return safe_mean(top_values)


def safe_difference(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return float(left - right)


def safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return float(numerator / denominator)


def safe_log2(value: float | None) -> float | None:
    if value is None or value <= 0:
        return None
    return float(math.log2(value))


def safe_sample_variance(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    return float(statistics.variance(values))


def cohens_d(interface_values: list[float], noninterface_values: list[float]) -> float | None:
    if len(interface_values) < 2 or len(noninterface_values) < 2:
        return None

    interface_mean = safe_mean(interface_values)
    noninterface_mean = safe_mean(noninterface_values)
    interface_var = safe_sample_variance(interface_values)
    noninterface_var = safe_sample_variance(noninterface_values)

    if (
        interface_mean is None
        or noninterface_mean is None
        or interface_var is None
        or noninterface_var is None
    ):
        return None

    n_interface = len(interface_values)
    n_noninterface = len(noninterface_values)
    pooled_variance = (
        (n_interface - 1) * interface_var + (n_noninterface - 1) * noninterface_var
    ) / (n_interface + n_noninterface - 2)

    if pooled_variance <= 0:
        return None

    return float((interface_mean - noninterface_mean) / math.sqrt(pooled_variance))


def feature_qc_status(
    n_interface: int,
    n_noninterface: int,
    min_interface_residues: int,
    min_noninterface_residues: int,
) -> str:
    if n_interface == 0:
        return "no_interface_residues"
    if n_noninterface == 0:
        return "no_noninterface_residues"
    if n_interface < min_interface_residues:
        return "small_interface"
    if n_noninterface < min_noninterface_residues:
        return "small_noninterface_background"
    return "ok"


def profile_features_for_group(
    group: pl.DataFrame,
    min_interface_residues: int,
    min_noninterface_residues: int,
) -> dict[str, Any]:
    first = group.row(0, named=True)

    interface_values = as_float_list(group.filter(pl.col("is_interface"))["delta"].to_list())
    noninterface_values = as_float_list(group.filter(~pl.col("is_interface"))["delta"].to_list())
    all_values = as_float_list(group["delta"].to_list())

    interface_mean = safe_mean(interface_values)
    noninterface_mean = safe_mean(noninterface_values)
    enrichment_ratio = safe_ratio(interface_mean, noninterface_mean)

    interface_median = safe_median(interface_values)
    noninterface_median = safe_median(noninterface_values)

    interface_q75 = safe_quantile(interface_values, 0.75)
    noninterface_q75 = safe_quantile(noninterface_values, 0.75)

    interface_q90 = safe_quantile(interface_values, 0.90)
    noninterface_q90 = safe_quantile(noninterface_values, 0.90)

    interface_top10_mean = safe_top_n_mean(interface_values, 10)
    noninterface_top10_mean = safe_top_n_mean(noninterface_values, 10)

    interface_max = safe_max(interface_values)
    noninterface_max = safe_max(noninterface_values)

    global_q90 = safe_quantile(all_values, 0.90)
    n_high_global = 0
    n_interface_high_global = 0
    if global_q90 is not None:
        for row in group.select(["delta", "is_interface"]).iter_rows(named=True):
            delta = float(row["delta"])
            if delta >= global_q90:
                n_high_global += 1
                if bool(row["is_interface"]):
                    n_interface_high_global += 1

    n_total = len(all_values)
    n_interface = len(interface_values)
    n_noninterface = len(noninterface_values)

    fraction_interface_above_global_q90 = (
        n_interface_high_global / n_high_global if n_high_global else None
    )
    interface_fraction_above_global_q90 = (
        n_interface_high_global / n_interface if n_interface else None
    )

    qc_status = feature_qc_status(
        n_interface=n_interface,
        n_noninterface=n_noninterface,
        min_interface_residues=min_interface_residues,
        min_noninterface_residues=min_noninterface_residues,
    )

    output = {
        "complex_id": first["complex_id"],
        "pdb_id": first["pdb_id"],
        "chain": first["chain"],
        "source_species": first["source_species"],
        "target_species": first["target_species"],
        "source_uniprot": first["source_uniprot"],
        "target_uniprot": first["target_uniprot"],
        "model_name": first["model_name"],
        "is_predicted_structure": first["is_predicted_structure"],
        "feature_space_version": "v1_interface_background_distribution_profile",
        "feature_qc_status": qc_status,
        "is_clustering_ready": qc_status == "ok",
        "interface_mean_delta": interface_mean,
        "noninterface_mean_delta": noninterface_mean,
        "delta_mean_difference": safe_difference(interface_mean, noninterface_mean),
        "enrichment_ratio": enrichment_ratio,
        "log2_enrichment_ratio": safe_log2(enrichment_ratio),
        "effect_size_cohens_d_computed": cohens_d(
            interface_values,
            noninterface_values,
        ),
        "interface_median_delta": interface_median,
        "noninterface_median_delta": noninterface_median,
        "median_difference": safe_difference(interface_median, noninterface_median),
        "interface_q75_delta": interface_q75,
        "noninterface_q75_delta": noninterface_q75,
        "q75_difference": safe_difference(interface_q75, noninterface_q75),
        "interface_q90_delta": interface_q90,
        "noninterface_q90_delta": noninterface_q90,
        "q90_difference": safe_difference(interface_q90, noninterface_q90),
        "interface_top10_mean_delta": interface_top10_mean,
        "noninterface_top10_mean_delta": noninterface_top10_mean,
        "top10_mean_difference": safe_difference(
            interface_top10_mean,
            noninterface_top10_mean,
        ),
        "interface_max_delta": interface_max,
        "noninterface_max_delta": noninterface_max,
        "max_difference": safe_difference(interface_max, noninterface_max),
        "global_q90_delta": global_q90,
        "fraction_interface_above_global_q90": fraction_interface_above_global_q90,
        "interface_fraction_above_global_q90": interface_fraction_above_global_q90,
        "n_total_residues": n_total,
        "n_interface_residues": n_interface,
        "n_noninterface_residues": n_noninterface,
        "interface_fraction": n_interface / n_total if n_total else None,
    }

    return output


def build_profile_features(
    residue_deltas: pl.DataFrame,
    *,
    min_interface_residues: int = 5,
    min_noninterface_residues: int = 20,
) -> pl.DataFrame:
    missing_group_columns = set(PROFILE_KEY_COLUMNS) - set(residue_deltas.columns)
    if missing_group_columns:
        raise ValueError(
            f"Residue delta table is missing profile key columns: {sorted(missing_group_columns)}"
        )

    rows = []
    groups = residue_deltas.sort(
        [
            "complex_id",
            "chain",
            "target_species",
            "residue_number_1based",
        ]
    ).partition_by(PROFILE_KEY_COLUMNS, maintain_order=True)

    for group in groups:
        rows.append(
            profile_features_for_group(
                group,
                min_interface_residues=min_interface_residues,
                min_noninterface_residues=min_noninterface_residues,
            )
        )

    return pl.DataFrame(rows).sort(["complex_id", "chain", "target_species"])


def optional_signal_annotations(path: Path) -> pl.DataFrame | None:
    if not path.exists():
        return None

    df = pl.read_csv(path)
    required = {
        "complex_id",
        "chain",
        "target_species",
        "signal_class",
        "p_interface_greater",
        "p_interface_less",
        "p_two_sided",
        "p_directional",
        "effect_size_cohens_d",
    }
    require_columns(df, required, path)

    keep = [
        column
        for column in [
            "complex_id",
            "chain",
            "target_species",
            "signal_class",
            "p_interface_greater",
            "p_interface_less",
            "p_two_sided",
            "p_directional",
            "effect_size_cohens_d",
            "biological_context",
            "interpretation",
        ]
        if column in df.columns
    ]
    return df.select(keep)


def optional_contrast_annotations(path: Path) -> pl.DataFrame | None:
    if not path.exists():
        return None

    df = pl.read_csv(path)
    required = {
        "complex_id",
        "chain",
        "long_lived_species",
        "short_lived_species",
        "contrast_class",
        "contrast_priority",
    }
    require_columns(df, required, path)

    keep = [
        column
        for column in [
            "complex_id",
            "chain",
            "target_species",
            "short_lived_species",
            "contrast_class",
            "contrast_priority",
            "contrast_note",
            "enrichment_delta",
            "enrichment_log2_ratio",
            "effect_size_delta",
            "long_enrichment_ratio",
            "short_enrichment_ratio",
            "long_effect_size",
            "short_effect_size",
        ]
        if column in df.columns or column == "target_species"
    ]

    return (
        df.with_columns(pl.col("long_lived_species").alias("target_species"))
        .select(keep)
        .unique(subset=["complex_id", "chain", "target_species"], keep="first")
    )


def optional_structure_qc_annotations(path: Path) -> pl.DataFrame | None:
    if not path.exists():
        return None

    df = pl.read_csv(path)
    required = {
        "complex_id",
        "chain",
        "target_species",
        "qc_status",
        "remapped_fraction_within_interface_cutoff",
    }
    require_columns(df, required, path)

    keep = [
        column
        for column in [
            "complex_id",
            "chain",
            "target_species",
            "qc_status",
            "remapped_fraction_within_interface_cutoff",
            "remapped_fraction_found",
        ]
        if column in df.columns
    ]

    return df.select(keep).unique(
        subset=["complex_id", "chain", "target_species"],
        keep="first",
    )


def add_optional_annotations(
    features: pl.DataFrame,
    *,
    signal_summary_path: Path,
    longevity_contrast_path: Path,
    structure_qc_path: Path,
) -> pl.DataFrame:
    out = features

    signal_annotations = optional_signal_annotations(signal_summary_path)
    if signal_annotations is not None:
        out = out.join(
            signal_annotations,
            on=["complex_id", "chain", "target_species"],
            how="left",
        )

    contrast_annotations = optional_contrast_annotations(longevity_contrast_path)
    if contrast_annotations is not None:
        out = out.join(
            contrast_annotations,
            on=["complex_id", "chain", "target_species"],
            how="left",
        )

    structure_qc_annotations = optional_structure_qc_annotations(structure_qc_path)
    if structure_qc_annotations is not None:
        out = out.join(
            structure_qc_annotations,
            on=["complex_id", "chain", "target_species"],
            how="left",
        )

    return out


def markdown_table(frame: pl.DataFrame) -> str:
    columns = frame.columns
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]

    for row in frame.iter_rows(named=True):
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                values.append(f"{value:.4g}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def value_counts_table(frame: pl.DataFrame, column: str) -> pl.DataFrame:
    if column not in frame.columns:
        return pl.DataFrame({column: [], "len": []})
    return frame.group_by(column).len().sort(["len", column], descending=[True, False])


def write_markdown_summary(features: pl.DataFrame, output_md: Path) -> None:
    clustering_ready = features.filter(pl.col("is_clustering_ready"))
    rankable = features.filter(
        pl.col("is_clustering_ready") & pl.col("log2_enrichment_ratio").is_not_null()
    )

    ranking_columns = [
        "complex_id",
        "chain",
        "target_species",
        "log2_enrichment_ratio",
        "effect_size_cohens_d_computed",
        "fraction_interface_above_global_q90",
        "signal_class",
        "contrast_class",
        "qc_status",
    ]
    ranking_columns = [column for column in ranking_columns if column in features.columns]

    top_divergent = (
        rankable.sort("log2_enrichment_ratio", descending=True).select(ranking_columns).head(12)
    )

    top_constrained = rankable.sort("log2_enrichment_ratio").select(ranking_columns).head(12)

    lines = [
        "# SIRT6 mini-pilot v2 divergence profile features",
        "",
        "This report defines the exploratory divergence-profile feature space used for downstream clustering.",
        "",
        "One point is one `complex_id + chain + target_species` profile.",
        "",
        "Each point summarizes the interface-vs-background distribution of residue-level embedding deltas.",
        "",
        "This is a feature export for prioritization and pilot expansion, not a clustering result and not biological validation.",
        "",
        "## Feature-space summary",
        "",
        f"- profile rows: {features.height}",
        f"- clustering-ready rows: {clustering_ready.height}",
        f"- rankable rows: {rankable.height}",
        f"- feature space version: `{features['feature_space_version'][0] if features.height else 'n/a'}`",
        "",
        "## Feature QC status counts",
        "",
        markdown_table(value_counts_table(features, "feature_qc_status")),
        "",
        "## Signal class counts",
        "",
        markdown_table(value_counts_table(features, "signal_class")),
        "",
        "## Contrast class counts",
        "",
        markdown_table(value_counts_table(features, "contrast_class")),
        "",
        "## Structure QC status counts",
        "",
        markdown_table(value_counts_table(features, "qc_status")),
        "",
        "## Top positive log2 enrichment profiles",
        "",
        markdown_table(top_divergent),
        "",
        "## Top negative log2 enrichment profiles",
        "",
        markdown_table(top_constrained),
        "",
        "## Interpretation notes",
        "",
        "- Positive `log2_enrichment_ratio` means interface deltas are higher than background deltas.",
        "- Negative `log2_enrichment_ratio` means interface deltas are lower than background deltas.",
        "- `fraction_interface_above_global_q90` asks whether the strongest residue-level deltas are concentrated at the interface.",
        "- `signal_class`, `contrast_class`, and `qc_status` are annotations, not coordinates that should be used to create clusters.",
        "- Top positive/negative tables exclude profiles that are not clustering-ready or have undefined `log2_enrichment_ratio`.",
        "- Downstream clustering should start from numeric feature columns, then inspect how biological annotations distribute across clusters.",
        "",
    ]

    output_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    residue_deltas_path = Path(args.residue_deltas)
    signal_summary_path = Path(args.signal_summary)
    longevity_contrast_path = Path(args.longevity_contrast)
    structure_qc_path = Path(args.structure_qc)
    output_csv = Path(args.output_csv)
    output_parquet = Path(args.output_parquet)
    output_md = Path(args.output_md)

    if not residue_deltas_path.exists():
        raise FileNotFoundError(f"Missing residue deltas parquet: {residue_deltas_path}")

    residue_deltas = pl.read_parquet(residue_deltas_path)
    require_columns(residue_deltas, REQUIRED_RESIDUE_DELTA_COLUMNS, residue_deltas_path)

    features = build_profile_features(
        residue_deltas,
        min_interface_residues=int(args.min_interface_residues),
        min_noninterface_residues=int(args.min_noninterface_residues),
    )
    features = add_optional_annotations(
        features,
        signal_summary_path=signal_summary_path,
        longevity_contrast_path=longevity_contrast_path,
        structure_qc_path=structure_qc_path,
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    features.write_csv(output_csv)
    features.write_parquet(output_parquet)
    write_markdown_summary(features, output_md)

    print(f"Wrote divergence profile features CSV -> {output_csv}")
    print(f"Wrote divergence profile features parquet -> {output_parquet}")
    print(f"Wrote divergence profile features Markdown -> {output_md}")
    print()
    print("Feature rows:", features.height)
    print("Feature QC status counts:")
    print(value_counts_table(features, "feature_qc_status"))
    print()
    print("Signal class counts:")
    print(value_counts_table(features, "signal_class"))
    print()
    print("Contrast class counts:")
    print(value_counts_table(features, "contrast_class"))
    print()
    if "qc_status" not in features.columns:
        features = features.with_columns(pl.lit(None).alias("qc_status"))

    print("Top feature preview:")
    print(
        features.select(
            [
                "complex_id",
                "chain",
                "target_species",
                "log2_enrichment_ratio",
                "effect_size_cohens_d_computed",
                "fraction_interface_above_global_q90",
                "signal_class",
                "contrast_class",
                "qc_status",
                "feature_qc_status",
            ]
        ).head(20)
    )


if __name__ == "__main__":
    main()
