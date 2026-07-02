from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages import tp53_mdm2_generic_gated_contrast

DEFAULT_GATE8_SUMMARY = tp53_mdm2_generic_gated_contrast.DEFAULT_OUTPUT
DEFAULT_REPAIR_CONTEXT = Path("data/input/tp53_mdm2_ortholog_repair_decisions.csv")
DEFAULT_OUTPUT = Path("data/interim/tp53_mdm2_generic_cofolding_readiness_context.csv")

PARTNER_CONTEXT_READY = "partner_context_ready"
PARTNER_CONTEXT_MISSING = "partner_context_missing"
SOURCE_PROVENANCE_READY = "source_provenance_ready"
SOURCE_PROVENANCE_MISSING = "source_provenance_missing"
DRY_RUN_INPUTS_UNREVIEWED = "dry_run_inputs_unreviewed"
DRY_RUN_INPUTS_REVIEWED = "dry_run_inputs_reviewed"
LIVE_NOT_REQUESTED = "live_not_requested"

GATE8_REQUIRED_COLUMNS = {
    "candidate_set",
    "lane_name",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "long_lived_species",
}

REPAIR_CONTEXT_REQUIRED_COLUMNS = {
    "candidate_set",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "partner_uniprot",
    "target_species",
}

TP53_MDM2_COFOLDING_CONTEXT_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "target_species": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "partner_context_status": pl.Utf8,
    "source_provenance_status": pl.Utf8,
    "cofolding_input_review_status": pl.Utf8,
    "live_opt_in_status": pl.Utf8,
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


def _empty_context() -> pl.DataFrame:
    return pl.DataFrame(schema=TP53_MDM2_COFOLDING_CONTEXT_SCHEMA)


def _context_from_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    if not rows:
        return _empty_context()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in TP53_MDM2_COFOLDING_CONTEXT_SCHEMA.items()
        ]
    )


def _context_key(
    row: dict[str, Any], *, target_species_column: str
) -> tuple[str, str, str, str, str, str]:
    return (
        _as_str(row, "candidate_set"),
        _as_str(row, "candidate_id"),
        _as_str(row, "pdb_id"),
        _as_str(row, "chain"),
        _as_str(row, "source_uniprot"),
        _as_str(row, target_species_column),
    )


def _repair_context_lookup(
    repair_context: pl.DataFrame,
) -> dict[tuple[str, str, str, str, str, str], str]:
    validate_required_columns(
        repair_context,
        REPAIR_CONTEXT_REQUIRED_COLUMNS,
        "repair_context",
    )

    lookup: dict[tuple[str, str, str, str, str, str], str] = {}
    for row in repair_context.iter_rows(named=True):
        key = _context_key(row, target_species_column="target_species")
        if key in lookup:
            raise ValueError(f"repair_context has duplicate TP53/MDM2 cofolding key: {key}")

        partner_uniprot = _as_str(row, "partner_uniprot")
        if partner_uniprot:
            lookup[key] = partner_uniprot

    return lookup


def _partner_uniprot_for_gate8_row(
    row: dict[str, Any],
    partner_by_key: dict[tuple[str, str, str, str, str, str], str],
) -> str:
    key = _context_key(row, target_species_column="long_lived_species")
    return partner_by_key.get(key, "")


def build_tp53_mdm2_cofolding_readiness_context(
    *,
    gate8_summary: pl.DataFrame,
    repair_context: pl.DataFrame,
    cofolding_input_review_status: str = DRY_RUN_INPUTS_UNREVIEWED,
) -> pl.DataFrame:
    """Build TP53/MDM2 Gate 9 context rows for the generic cofolding runtime.

    This is a lane-specific context bridge. It records partner/provenance/review
    context for TP53/MDM2 generic Gate 8 rows while preserving the blocked Gate 8
    policy. It does not call Biohub, does not call Boltz, does not generate
    embeddings, does not generate cofolding inputs, does not submit live
    structural jobs, and does not make biological claims.
    """
    validate_required_columns(gate8_summary, GATE8_REQUIRED_COLUMNS, "gate8_summary")

    if gate8_summary.is_empty():
        return _empty_context()

    partner_by_key = _repair_context_lookup(repair_context)
    output_rows: list[dict[str, object]] = []

    for row in gate8_summary.iter_rows(named=True):
        source_uniprot = _as_str(row, "source_uniprot")
        partner_uniprot = _partner_uniprot_for_gate8_row(row, partner_by_key)

        output_rows.append(
            {
                "candidate_set": _as_str(row, "candidate_set"),
                "lane_name": _as_str(row, "lane_name"),
                "candidate_id": _as_str(row, "candidate_id"),
                "pdb_id": _as_str(row, "pdb_id"),
                "chain": _as_str(row, "chain"),
                "source_uniprot": source_uniprot,
                "target_species": _as_str(row, "long_lived_species"),
                "partner_uniprot": partner_uniprot,
                "partner_context_status": (
                    PARTNER_CONTEXT_READY if partner_uniprot else PARTNER_CONTEXT_MISSING
                ),
                "source_provenance_status": (
                    SOURCE_PROVENANCE_READY if source_uniprot else SOURCE_PROVENANCE_MISSING
                ),
                "cofolding_input_review_status": cofolding_input_review_status,
                "live_opt_in_status": LIVE_NOT_REQUESTED,
            }
        )

    return _context_from_rows(output_rows).sort(
        [
            "candidate_id",
            "target_species",
            "chain",
        ]
    )


def tp53_mdm2_cofolding_context_status_counts(context: pl.DataFrame) -> dict[str, int]:
    if context.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in context.group_by("partner_context_status").len().iter_rows(named=True):
        counts[str(row["partner_context_status"])] = int(row["len"])

    return counts


def write_tp53_mdm2_cofolding_readiness_context(
    *,
    gate8_summary: pl.DataFrame,
    repair_context: pl.DataFrame,
    output: Path,
    cofolding_input_review_status: str = DRY_RUN_INPUTS_UNREVIEWED,
) -> pl.DataFrame:
    context = build_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8_summary,
        repair_context=repair_context,
        cofolding_input_review_status=cofolding_input_review_status,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    context.write_csv(output)

    return context


@app.command()
def main(
    gate8_summary: Annotated[
        Path,
        typer.Option(help="CSV/parquet TP53/MDM2 generic Gate 8 blocked summary table."),
    ] = DEFAULT_GATE8_SUMMARY,
    repair_context_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet TP53/MDM2 repair-decision table with partner context."),
    ] = DEFAULT_REPAIR_CONTEXT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for TP53/MDM2 generic Gate 9 context rows."),
    ] = DEFAULT_OUTPUT,
    cofolding_input_review_status: Annotated[
        str,
        typer.Option(
            help=(
                "Review status to record for cofolding inputs. Default is conservative: "
                "dry_run_inputs_unreviewed."
            ),
        ),
    ] = DRY_RUN_INPUTS_UNREVIEWED,
) -> None:
    """Build TP53/MDM2 cofolding readiness context rows without live actions."""
    gate8 = read_table(gate8_summary)
    repair_context = read_table(repair_context_input)

    context = write_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8,
        repair_context=repair_context,
        output=output,
        cofolding_input_review_status=cofolding_input_review_status,
    )

    typer.echo(f"TP53/MDM2 cofolding readiness context rows: {context.height}")
    for status, count in sorted(tp53_mdm2_cofolding_context_status_counts(context).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote TP53/MDM2 cofolding readiness context -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No embeddings were generated.")
    typer.echo("No cofolding inputs were generated.")
    typer.echo("No cofolding jobs were submitted.")
    typer.echo("No live structural calls were made.")
    typer.echo("No biological validation claim was made.")
    typer.echo("TP53/MDM2 remains blocked by the generic Gate 8 contrast status.")


if __name__ == "__main__":
    app()
