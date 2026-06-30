from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages.tp53_mdm2_pilot_manifest_validator import (
    DEFAULT_INPUT,
    EXPECTED_CLAIM_POLICY,
    validate_tp53_mdm2_pilot_manifest,
)

DEFAULT_OUTPUT = Path("data/interim/tp53_mdm2_pilot_coverage_preflight.csv")

COVERAGE_PREFLIGHT_SCHEMA = {
    "candidate_set": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "target_species": pl.Utf8,
    "strict_contrast_gate_status": pl.Utf8,
    "coverage_preflight_status": pl.Utf8,
    "source_ortholog_status": pl.Utf8,
    "local_candidate_row_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "claim_policy": pl.Utf8,
    "coverage_preflight_note": pl.Utf8,
}


app = typer.Typer(
    help=(
        "Build a TP53/MDM2 pilot coverage preflight table without live API calls "
        "or biological claims."
    )
)


def _as_str(row: dict[str, Any], column: str) -> str:
    value = row.get(column)
    if value is None:
        return ""
    return str(value).strip()


def _empty_preflight() -> pl.DataFrame:
    return pl.DataFrame(schema=COVERAGE_PREFLIGHT_SCHEMA)


def _preflight_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return _empty_preflight()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in COVERAGE_PREFLIGHT_SCHEMA.items()
        ]
    )


def coverage_preflight_status(strict_contrast_gate_status: str) -> str:
    if strict_contrast_gate_status == "blocked_contrast_coverage":
        return "blocked_pending_coverage_repair"
    if strict_contrast_gate_status == "eligible_for_contrast_dry_run":
        return "coverage_marked_ready_in_manifest"
    return "blocked_by_noncoverage_gate"


def recommended_next_action(coverage_status: str) -> str:
    if coverage_status == "blocked_pending_coverage_repair":
        return "curate_or_fetch_tp53_mdm2_source_ortholog_coverage"
    if coverage_status == "coverage_marked_ready_in_manifest":
        return "run_contrast_gate_before_cofolding"
    return "resolve_manifest_gate_blocker_before_coverage_preflight"


def build_tp53_mdm2_pilot_coverage_preflight(manifest: pl.DataFrame) -> pl.DataFrame:
    """Build a conservative TP53/MDM2 coverage preflight table from manifest rows."""

    validate_tp53_mdm2_pilot_manifest(manifest)

    rows: list[dict[str, Any]] = []
    for row in manifest.iter_rows(named=True):
        gate_status = _as_str(row, "strict_contrast_gate_status")
        coverage_status = coverage_preflight_status(gate_status)

        rows.append(
            {
                "candidate_set": _as_str(row, "candidate_set"),
                "candidate_id": _as_str(row, "candidate_id"),
                "pdb_id": _as_str(row, "pdb_id"),
                "chain": _as_str(row, "chain"),
                "source_uniprot": _as_str(row, "source_uniprot"),
                "partner_uniprot": _as_str(row, "partner_uniprot"),
                "target_species": _as_str(row, "target_species"),
                "strict_contrast_gate_status": gate_status,
                "coverage_preflight_status": coverage_status,
                "source_ortholog_status": "not_checked",
                "local_candidate_row_status": "not_checked",
                "recommended_next_action": recommended_next_action(coverage_status),
                "claim_policy": _as_str(row, "claim_policy"),
                "coverage_preflight_note": (
                    "Coverage preflight uses committed manifest fields only; "
                    "no Biohub, Boltz, embeddings, cofolding jobs, or biological "
                    "claims are introduced."
                ),
            }
        )

    return _preflight_from_rows(rows).sort(["coverage_preflight_status", "candidate_id", "chain"])


def status_counts(preflight: pl.DataFrame) -> dict[str, int]:
    if preflight.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in preflight.group_by("coverage_preflight_status").len().iter_rows(named=True):
        counts[str(row["coverage_preflight_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            help="TP53/MDM2 pilot manifest CSV to preflight.",
        ),
    ] = DEFAULT_INPUT,
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            help="Output CSV path for the TP53/MDM2 coverage preflight table.",
        ),
    ] = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    """Build a TP53/MDM2 pilot coverage preflight table."""

    manifest = pl.read_csv(input_path)
    preflight = build_tp53_mdm2_pilot_coverage_preflight(manifest)

    output.parent.mkdir(parents=True, exist_ok=True)
    preflight.write_csv(output)

    typer.echo(f"TP53/MDM2 pilot coverage preflight rows: {preflight.height}")
    for status, count in sorted(status_counts(preflight).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote TP53/MDM2 pilot coverage preflight -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No orthologs were fetched.")
    typer.echo("No embeddings were generated.")
    typer.echo("No cofolding jobs were submitted.")
    typer.echo("No Boltz credits were spent.")
    typer.echo("No biological validation claim was made.")

    return {
        "input": str(input_path),
        "output": str(output),
        "rows": preflight.height,
        "claim_policy": EXPECTED_CLAIM_POLICY,
        "no_live_actions": True,
    }


if __name__ == "__main__":
    app()
