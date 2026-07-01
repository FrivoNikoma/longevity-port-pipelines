from __future__ import annotations

import math
from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages.gated_contrast_readiness import (
    CONSERVATIVE_CLAIM_POLICY,
    gated_contrast_readiness_for_statuses,
)

DEFAULT_INPUT = Path("data/interim/generic_gated_contrast_input.csv")
DEFAULT_OUTPUT = Path("data/interim/generic_gated_contrast_summary.csv")

DIVERGENT_THRESHOLD = 1.2
CONSTRAINED_THRESHOLD = 0.8
BASELINE_NEUTRAL_UPPER = 1.1
BASELINE_NEUTRAL_LOWER = 0.9
MIN_ENRICHMENT_DELTA = 0.2
MIN_ABS_EFFECT = 0.2

KEY_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "priority",
]

REQUIRED_METRIC_COLUMNS = [
    "enrichment_ratio",
    "effect_size",
    "interface_mean_delta",
    "noninterface_mean_delta",
    "p_two_sided",
]

REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "strict_panel_status",
    "contrast_dry_run_allowed",
    "controlled_claim_allowed",
    "target_species",
    "target_species_taxid",
    "species_group",
    *REQUIRED_METRIC_COLUMNS,
    "is_predicted_structure",
    "claim_policy",
}

GATED_CONTRAST_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "long_lived_species": pl.Utf8,
    "short_lived_species": pl.Utf8,
    "short_lived_control_count": pl.Int64,
    "long_enrichment_ratio": pl.Float64,
    "short_enrichment_ratio": pl.Float64,
    "enrichment_delta": pl.Float64,
    "enrichment_log2_ratio": pl.Float64,
    "contrast_class": pl.Utf8,
    "contrast_priority": pl.Int64,
    "contrast_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "contrast_dry_run_allowed": pl.Boolean,
    "controlled_claim_allowed": pl.Boolean,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "contrast_note": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def read_table(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing table: {path}")

    if path.suffix.lower() == ".parquet":
        return pl.read_parquet(path)

    return pl.read_csv(path, infer_schema_length=10000)


def validate_required_columns(df: pl.DataFrame, required: set[str], label: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {sorted(missing)}")


def _as_str(row: dict[str, Any], column: str, default: str = "") -> str:
    value = row.get(column)
    if value is None:
        return default
    return str(value).strip()


def _as_float(row: dict[str, Any], column: str) -> float:
    value = row.get(column)
    if value is None:
        return math.nan

    number = float(value)
    if math.isfinite(number):
        return number

    return math.nan


def _as_bool(row: dict[str, Any], column: str, default: bool = False) -> bool:
    value = row.get(column)
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False

    return default


def _safe_log2_ratio(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        return math.nan
    if numerator <= 0.0 or denominator <= 0.0:
        return math.nan
    return math.log2(numerator / denominator)


def _mean(values: list[float]) -> float:
    finite_values = [value for value in values if math.isfinite(value)]
    if not finite_values:
        return math.nan
    return sum(finite_values) / len(finite_values)


def _normalise_species_group(group: str) -> str:
    return group.strip().lower().replace("-", "_")


def _is_long_lived_group(group: str) -> bool:
    return _normalise_species_group(group).startswith("long_lived")


def _is_short_lived_group(group: str) -> bool:
    return _normalise_species_group(group).startswith("short_lived")


def _joined_unique_values(rows: list[dict[str, Any]], column: str) -> str:
    values = {_as_str(row, column) for row in rows}
    return ",".join(sorted(value for value in values if value))


def _first_nonempty_value(
    rows: list[dict[str, Any]],
    column: str,
    default: str = "",
) -> str:
    for row in rows:
        value = _as_str(row, column)
        if value:
            return value
    return default


def _empty_contrast() -> pl.DataFrame:
    return pl.DataFrame(schema=GATED_CONTRAST_SCHEMA)


def _summary_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return _empty_contrast()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in GATED_CONTRAST_SCHEMA.items()
        ]
    )


def _class_priority(contrast_class: str) -> int:
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


def _is_divergent(ratio: float, effect: float) -> bool:
    return ratio >= DIVERGENT_THRESHOLD and effect >= MIN_ABS_EFFECT


def _is_constrained(ratio: float, effect: float) -> bool:
    return ratio <= CONSTRAINED_THRESHOLD and effect <= -MIN_ABS_EFFECT


def _classify_contrast(
    *,
    long_ratio: float,
    short_ratio: float,
    long_effect: float,
    short_effect: float,
) -> tuple[str, str]:
    enrichment_delta = long_ratio - short_ratio

    long_divergent = _is_divergent(long_ratio, long_effect)
    short_divergent = _is_divergent(short_ratio, short_effect)
    long_constrained = _is_constrained(long_ratio, long_effect)
    short_constrained = _is_constrained(short_ratio, short_effect)

    if long_divergent:
        if short_divergent:
            return (
                "shared_nonhuman_interface_divergence",
                "Long-lived and short-lived rows both show interface-enriched divergence.",
            )

        if short_ratio <= BASELINE_NEUTRAL_UPPER and enrichment_delta >= MIN_ENRICHMENT_DELTA:
            return (
                "long_lived_specific_interface_divergence",
                "Long-lived row shows interface-enriched divergence relative to a near-neutral short-lived baseline.",
            )

        return (
            "long_lived_enhanced_interface_divergence",
            "Long-lived row shows stronger interface-enriched divergence than the short-lived baseline.",
        )

    if long_constrained:
        if short_constrained:
            return (
                "shared_interface_constraint",
                "Long-lived and short-lived rows both show interface constraint.",
            )

        if short_ratio >= BASELINE_NEUTRAL_LOWER and -enrichment_delta >= MIN_ENRICHMENT_DELTA:
            return (
                "long_lived_specific_interface_constraint",
                "Long-lived row shows interface constraint relative to a near-neutral short-lived baseline.",
            )

        return (
            "long_lived_enhanced_interface_constraint",
            "Long-lived row shows stronger interface constraint than the short-lived baseline.",
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


def _required_metrics_ready(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        for column in REQUIRED_METRIC_COLUMNS:
            if not math.isfinite(_as_float(row, column)):
                return False
    return True


def _all_rows_allow_contrast(rows: list[dict[str, Any]]) -> bool:
    return all(_as_bool(row, "contrast_dry_run_allowed") for row in rows)


def _blocked_record(
    *,
    key_row: dict[str, Any],
    rows: list[dict[str, Any]],
    readiness_status: str,
    recommended_next_action: str,
    contrast_dry_run_allowed: bool,
    controlled_claim_allowed: bool,
    claim_policy: str,
    claim_status: str,
    contrast_note: str,
) -> dict[str, Any]:
    long_species = sorted(
        {
            _as_str(row, "target_species")
            for row in rows
            if _is_long_lived_group(_as_str(row, "species_group"))
            and _as_str(row, "target_species")
        }
    )
    short_species = sorted(
        {
            _as_str(row, "target_species")
            for row in rows
            if _is_short_lived_group(_as_str(row, "species_group"))
            and _as_str(row, "target_species")
        }
    )

    return {
        **key_row,
        "long_lived_species": ",".join(long_species),
        "short_lived_species": ",".join(short_species),
        "short_lived_control_count": len(short_species),
        "long_enrichment_ratio": math.nan,
        "short_enrichment_ratio": math.nan,
        "enrichment_delta": math.nan,
        "enrichment_log2_ratio": math.nan,
        "contrast_class": "weak_or_unresolved_contrast",
        "contrast_priority": _class_priority("weak_or_unresolved_contrast"),
        "contrast_status": readiness_status,
        "recommended_next_action": recommended_next_action,
        "contrast_dry_run_allowed": contrast_dry_run_allowed,
        "controlled_claim_allowed": controlled_claim_allowed,
        "claim_policy": claim_policy,
        "claim_status": claim_status,
        "contrast_note": contrast_note,
    }


def _short_lived_baseline(short_rows: list[dict[str, Any]]) -> dict[str, Any]:
    short_species = sorted(
        {_as_str(row, "target_species") for row in short_rows if _as_str(row, "target_species")}
    )
    return {
        "short_lived_species": ",".join(short_species),
        "short_lived_control_count": len(short_species),
        "short_enrichment_ratio": _mean([_as_float(row, "enrichment_ratio") for row in short_rows]),
        "short_effect_size": _mean([_as_float(row, "effect_size") for row in short_rows]),
    }


def _ready_records(
    *,
    key_row: dict[str, Any],
    long_rows: list[dict[str, Any]],
    short_baseline: dict[str, Any],
    readiness_status: str,
    recommended_next_action: str,
    contrast_dry_run_allowed: bool,
    controlled_claim_allowed: bool,
    claim_policy: str,
    claim_status: str,
    readiness_note: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    short_ratio = float(short_baseline["short_enrichment_ratio"])
    short_effect = float(short_baseline["short_effect_size"])

    for long_row in long_rows:
        long_ratio = _as_float(long_row, "enrichment_ratio")
        long_effect = _as_float(long_row, "effect_size")
        enrichment_delta = long_ratio - short_ratio

        contrast_class, class_note = _classify_contrast(
            long_ratio=long_ratio,
            short_ratio=short_ratio,
            long_effect=long_effect,
            short_effect=short_effect,
        )

        records.append(
            {
                **key_row,
                "long_lived_species": _as_str(long_row, "target_species"),
                "short_lived_species": short_baseline["short_lived_species"],
                "short_lived_control_count": short_baseline["short_lived_control_count"],
                "long_enrichment_ratio": long_ratio,
                "short_enrichment_ratio": short_ratio,
                "enrichment_delta": enrichment_delta,
                "enrichment_log2_ratio": _safe_log2_ratio(long_ratio, short_ratio),
                "contrast_class": contrast_class,
                "contrast_priority": _class_priority(contrast_class),
                "contrast_status": readiness_status,
                "recommended_next_action": recommended_next_action,
                "contrast_dry_run_allowed": contrast_dry_run_allowed,
                "controlled_claim_allowed": controlled_claim_allowed,
                "claim_policy": claim_policy,
                "claim_status": claim_status,
                "contrast_note": f"{class_note} {readiness_note}",
            }
        )

    return records


def build_generic_gated_contrast(gated_contrast_input: pl.DataFrame) -> pl.DataFrame:
    validate_required_columns(
        gated_contrast_input,
        REQUIRED_COLUMNS,
        "gated_contrast_input",
    )
    if gated_contrast_input.is_empty():
        return _empty_contrast()

    output_rows: list[dict[str, Any]] = []

    for key_row in (
        gated_contrast_input.select(KEY_COLUMNS).unique().sort(KEY_COLUMNS).iter_rows(named=True)
    ):
        candidate_frame = gated_contrast_input
        for column in KEY_COLUMNS:
            candidate_frame = candidate_frame.filter(pl.col(column) == key_row[column])

        candidate_rows = list(candidate_frame.iter_rows(named=True))
        long_rows = [
            row
            for row in candidate_rows
            if _is_long_lived_group(_as_str(row, "species_group"))
            and _as_str(row, "target_species")
        ]
        short_rows = [
            row
            for row in candidate_rows
            if _is_short_lived_group(_as_str(row, "species_group"))
            and _as_str(row, "target_species")
        ]

        metrics_ready = _required_metrics_ready(candidate_rows)
        readiness = gated_contrast_readiness_for_statuses(
            n_enrichment_rows=len(candidate_rows),
            n_long_lived_ready=len(long_rows),
            n_short_lived_control_ready=len(short_rows),
            strict_panel_statuses=_joined_unique_values(candidate_rows, "strict_panel_status"),
            strict_panel_contrast_dry_run_allowed=_all_rows_allow_contrast(candidate_rows),
            metrics_ready=metrics_ready,
            candidate_keys_matched=True,
            claim_policy=_first_nonempty_value(
                candidate_rows,
                "claim_policy",
                CONSERVATIVE_CLAIM_POLICY,
            ),
        )

        if not readiness.contrast_dry_run_allowed:
            output_rows.append(
                _blocked_record(
                    key_row=key_row,
                    rows=candidate_rows,
                    readiness_status=readiness.contrast_status,
                    recommended_next_action=readiness.recommended_next_action,
                    contrast_dry_run_allowed=readiness.contrast_dry_run_allowed,
                    controlled_claim_allowed=readiness.controlled_claim_allowed,
                    claim_policy=readiness.claim_policy,
                    claim_status=readiness.claim_status,
                    contrast_note=readiness.contrast_note,
                )
            )
            continue

        short_baseline = _short_lived_baseline(short_rows)
        output_rows.extend(
            _ready_records(
                key_row=key_row,
                long_rows=long_rows,
                short_baseline=short_baseline,
                readiness_status=readiness.contrast_status,
                recommended_next_action=readiness.recommended_next_action,
                contrast_dry_run_allowed=readiness.contrast_dry_run_allowed,
                controlled_claim_allowed=readiness.controlled_claim_allowed,
                claim_policy=readiness.claim_policy,
                claim_status=readiness.claim_status,
                readiness_note=readiness.contrast_note,
            )
        )

    return _summary_from_rows(output_rows).sort(
        ["contrast_priority", "priority", "candidate_id", "long_lived_species"]
    )


def gated_contrast_status_counts(summary: pl.DataFrame) -> dict[str, int]:
    if summary.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in summary.group_by("contrast_status").len().iter_rows(named=True):
        counts[str(row["contrast_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    gated_contrast_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet generic gated contrast input table."),
    ] = DEFAULT_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the generic gated contrast summary."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Build a generic gated contrast summary without Biohub, Boltz, or claims."""
    input_frame = read_table(gated_contrast_input)
    summary = build_generic_gated_contrast(input_frame)

    output.parent.mkdir(parents=True, exist_ok=True)
    summary.write_csv(output)

    typer.echo(f"generic gated contrast summary rows: {summary.height}")
    for status, count in sorted(gated_contrast_status_counts(summary).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote generic gated contrast summary -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo(
        "No embeddings, cofolding inputs, live structural calls, or biological claims were computed."
    )


if __name__ == "__main__":
    app()
