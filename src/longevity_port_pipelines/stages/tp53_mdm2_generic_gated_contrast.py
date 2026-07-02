from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages.gated_contrast import GATED_CONTRAST_SCHEMA

DEFAULT_REPAIR_INPUT = Path("data/input/tp53_mdm2_ortholog_repair_decisions.csv")
DEFAULT_OUTPUT = Path("data/interim/tp53_mdm2_generic_gated_contrast_summary.csv")

CANDIDATE_SET = "tp53_mdm2_elephant"
LANE_NAME = "tp53_mdm2_elephant"

BLOCKED_CONTRAST_STATUS = "blocked_strict_panel_not_ready"
BLOCKED_ROBUSTNESS_STATUS = "blocked_before_robustness_review"
BLOCKED_CONTRAST_CLASS = "weak_or_unresolved_contrast"
CONSERVATIVE_CLAIM_POLICY = "no_biological_claims_until_validation"

REPAIR_REQUIRED_COLUMNS = {
    "candidate_set",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "target_species",
    "coverage_preflight_status",
    "repair_decision",
    "repair_priority",
    "claim_policy",
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


def _empty_summary() -> pl.DataFrame:
    return pl.DataFrame(schema=GATED_CONTRAST_SCHEMA)


def _summary_from_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    if not rows:
        return _empty_summary()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in GATED_CONTRAST_SCHEMA.items()
        ]
    )


def _claim_policy(row: dict[str, Any]) -> str:
    claim_policy = _as_str(row, "claim_policy")
    if claim_policy:
        return claim_policy
    return CONSERVATIVE_CLAIM_POLICY


def _contrast_note(row: dict[str, Any]) -> str:
    coverage_status = _as_str(row, "coverage_preflight_status", "unknown_coverage_status")
    repair_decision = _as_str(row, "repair_decision", "unknown_repair_decision")
    source_ortholog_status = _as_str(
        row, "source_ortholog_status", "unknown_source_ortholog_status"
    )
    local_candidate_row_status = _as_str(
        row,
        "local_candidate_row_status",
        "unknown_local_candidate_row_status",
    )

    return (
        "TP53/MDM2 is wired into generic Gate 8 as a blocked technical checkpoint only; "
        f"coverage_preflight_status={coverage_status}; "
        f"repair_decision={repair_decision}; "
        f"source_ortholog_status={source_ortholog_status}; "
        f"local_candidate_row_status={local_candidate_row_status}; "
        "no contrast metrics, cofolding dry-run, live structural calls, or biological claims are allowed."
    )


def build_tp53_mdm2_generic_gated_contrast_blocked_summary(
    repair_decisions: pl.DataFrame,
) -> pl.DataFrame:
    """Build a TP53/MDM2 generic Gate 8-compatible blocked summary.

    This is a calibration-lane wiring checkpoint. It records that TP53/MDM2 can
    enter the generic Gate 8 evidence trail while remaining blocked by current
    coverage/strict-panel policy. It does not compute enrichment metrics, does
    not call Biohub or Boltz, does not generate embeddings, does not generate
    cofolding inputs, does not submit live structural jobs, and does not make
    biological claims.
    """
    validate_required_columns(repair_decisions, REPAIR_REQUIRED_COLUMNS, "repair_decisions")

    output_rows: list[dict[str, object]] = []
    for row in repair_decisions.iter_rows(named=True):
        output_rows.append(
            {
                "candidate_set": _as_str(row, "candidate_set", CANDIDATE_SET),
                "lane_name": LANE_NAME,
                "candidate_id": _as_str(row, "candidate_id"),
                "pdb_id": _as_str(row, "pdb_id"),
                "chain": _as_str(row, "chain"),
                "source_uniprot": _as_str(row, "source_uniprot"),
                "priority": _as_str(row, "repair_priority", "blocked"),
                "long_lived_species": _as_str(row, "target_species"),
                "short_lived_species": "",
                "short_lived_control_count": 0,
                "long_enrichment_ratio": None,
                "short_enrichment_ratio": None,
                "enrichment_delta": None,
                "enrichment_log2_ratio": None,
                "contrast_class": BLOCKED_CONTRAST_CLASS,
                "contrast_priority": 99,
                "has_multiple_short_lived_controls": False,
                "has_multiple_long_lived_species": False,
                "short_lived_baseline_is_single_species": False,
                "contrast_class_is_directional": False,
                "contrast_requires_review": True,
                "robustness_status": BLOCKED_ROBUSTNESS_STATUS,
                "robustness_note": (
                    "TP53/MDM2 remains blocked before robustness review because the "
                    "coverage/strict-panel prerequisites are not ready."
                ),
                "contrast_status": BLOCKED_CONTRAST_STATUS,
                "recommended_next_action": "resolve_tp53_mdm2_coverage_repair_before_gate8_contrast",
                "contrast_dry_run_allowed": False,
                "controlled_claim_allowed": False,
                "claim_policy": _claim_policy(row),
                "claim_status": "blocked_before_gate8_contrast",
                "contrast_note": _contrast_note(row),
            }
        )

    return _summary_from_rows(output_rows).sort(
        [
            "priority",
            "candidate_id",
            "long_lived_species",
        ]
    )


def tp53_mdm2_generic_gate8_status_counts(summary: pl.DataFrame) -> dict[str, int]:
    if summary.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in summary.group_by("contrast_status").len().iter_rows(named=True):
        counts[str(row["contrast_status"])] = int(row["len"])

    return counts


def write_tp53_mdm2_generic_gated_contrast_blocked_summary(
    *,
    repair_decisions: pl.DataFrame,
    output: Path,
) -> pl.DataFrame:
    summary = build_tp53_mdm2_generic_gated_contrast_blocked_summary(repair_decisions)

    output.parent.mkdir(parents=True, exist_ok=True)
    summary.write_csv(output)

    return summary


@app.command()
def main(
    repair_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet TP53/MDM2 ortholog repair-decision table."),
    ] = DEFAULT_REPAIR_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for TP53/MDM2 generic Gate 8 blocked summary."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Build a TP53/MDM2 generic Gate 8 blocked summary without live actions."""
    repair_decisions = read_table(repair_input)
    summary = write_tp53_mdm2_generic_gated_contrast_blocked_summary(
        repair_decisions=repair_decisions,
        output=output,
    )

    typer.echo(f"TP53/MDM2 generic Gate 8 blocked summary rows: {summary.height}")
    for status, count in sorted(tp53_mdm2_generic_gate8_status_counts(summary).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote TP53/MDM2 generic Gate 8 blocked summary -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No embeddings were generated.")
    typer.echo("No enrichment metrics were computed.")
    typer.echo("No cofolding inputs were generated.")
    typer.echo("No cofolding jobs were submitted.")
    typer.echo("No live structural calls were made.")
    typer.echo("No biological validation claim was made.")


if __name__ == "__main__":
    app()
