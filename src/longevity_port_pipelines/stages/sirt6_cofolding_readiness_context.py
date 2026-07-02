from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages import sirt6_generic_gated_contrast

DEFAULT_GATE8_SUMMARY = sirt6_generic_gated_contrast.DEFAULT_OUTPUT
DEFAULT_PARTNER_CONTEXT = Path("data/input/sirt6_cofolding_partner_context.csv")
DEFAULT_OUTPUT = Path("data/interim/sirt6_generic_cofolding_readiness_context.csv")

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
    "priority",
    "long_lived_species",
}

PARTNER_CONTEXT_REQUIRED_COLUMNS = {
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "partner_uniprot",
}

SIRT6_COFOLDING_CONTEXT_SCHEMA = {
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
    return pl.DataFrame(schema=SIRT6_COFOLDING_CONTEXT_SCHEMA)


def _context_from_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    if not rows:
        return _empty_context()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in SIRT6_COFOLDING_CONTEXT_SCHEMA.items()
        ]
    )


def _partner_context_lookup(
    partner_context: pl.DataFrame | None,
) -> dict[tuple[str, str, str, str], str]:
    if partner_context is None:
        return {}

    validate_required_columns(
        partner_context,
        PARTNER_CONTEXT_REQUIRED_COLUMNS,
        "partner_context",
    )

    lookup: dict[tuple[str, str, str, str], str] = {}
    for row in partner_context.iter_rows(named=True):
        key = (
            _as_str(row, "candidate_id"),
            _as_str(row, "pdb_id"),
            _as_str(row, "chain"),
            _as_str(row, "source_uniprot"),
        )
        if key in lookup:
            raise ValueError(f"partner_context has duplicate SIRT6 cofolding key: {key}")

        partner_uniprot = _as_str(row, "partner_uniprot")
        if partner_uniprot:
            lookup[key] = partner_uniprot

    return lookup


def _uniprot_tokens_from_candidate_id(candidate_id: str) -> list[str]:
    tokens: list[str] = []
    for half in candidate_id.split("--"):
        match = re.search(r"_([A-Z0-9]{6,10})$", half.strip())
        if match:
            tokens.append(match.group(1))

    return tokens


def _partner_from_candidate_id(
    *,
    candidate_id: str,
    chain: str,
    source_uniprot: str,
) -> str:
    tokens = _uniprot_tokens_from_candidate_id(candidate_id)
    if len(tokens) != 2:
        return ""

    if source_uniprot == tokens[0]:
        return tokens[1]
    if source_uniprot == tokens[1]:
        return tokens[0]

    if chain == "receptor":
        return tokens[1]
    if chain == "ligand":
        return tokens[0]

    return ""


def _partner_uniprot_for_row(
    row: dict[str, Any],
    partner_by_key: dict[tuple[str, str, str, str], str],
) -> str:
    candidate_id = _as_str(row, "candidate_id")
    pdb_id = _as_str(row, "pdb_id")
    chain = _as_str(row, "chain")
    source_uniprot = _as_str(row, "source_uniprot")

    key = (candidate_id, pdb_id, chain, source_uniprot)
    explicit_partner = partner_by_key.get(key)
    if explicit_partner:
        return explicit_partner

    return _partner_from_candidate_id(
        candidate_id=candidate_id,
        chain=chain,
        source_uniprot=source_uniprot,
    )


def build_sirt6_cofolding_readiness_context(
    *,
    gate8_summary: pl.DataFrame,
    partner_context: pl.DataFrame | None = None,
    cofolding_input_review_status: str = DRY_RUN_INPUTS_UNREVIEWED,
) -> pl.DataFrame:
    """Build SIRT6 Gate 9 context rows for the generic cofolding readiness runtime.

    This is a lane-specific context bridge. It records partner/provenance/review
    context for SIRT6 generic Gate 8 rows. It does not call Biohub, does not call
    Boltz, does not generate embeddings, does not generate cofolding inputs, does
    not submit live structural jobs, and does not make biological claims.
    """
    validate_required_columns(gate8_summary, GATE8_REQUIRED_COLUMNS, "gate8_summary")

    if gate8_summary.is_empty():
        return _empty_context()

    partner_by_key = _partner_context_lookup(partner_context)
    output_rows: list[dict[str, object]] = []

    for row in gate8_summary.iter_rows(named=True):
        source_uniprot = _as_str(row, "source_uniprot")
        partner_uniprot = _partner_uniprot_for_row(row, partner_by_key)

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


def sirt6_cofolding_context_status_counts(context: pl.DataFrame) -> dict[str, int]:
    if context.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in context.group_by("partner_context_status").len().iter_rows(named=True):
        counts[str(row["partner_context_status"])] = int(row["len"])

    return counts


def write_sirt6_cofolding_readiness_context(
    *,
    gate8_summary: pl.DataFrame,
    output: Path,
    partner_context: pl.DataFrame | None = None,
    cofolding_input_review_status: str = DRY_RUN_INPUTS_UNREVIEWED,
) -> pl.DataFrame:
    context = build_sirt6_cofolding_readiness_context(
        gate8_summary=gate8_summary,
        partner_context=partner_context,
        cofolding_input_review_status=cofolding_input_review_status,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    context.write_csv(output)

    return context


@app.command()
def main(
    gate8_summary: Annotated[
        Path,
        typer.Option(help="CSV/parquet SIRT6 generic Gate 8 summary table."),
    ] = DEFAULT_GATE8_SUMMARY,
    partner_context_input: Annotated[
        Path | None,
        typer.Option(
            help=(
                "Optional CSV/parquet SIRT6 partner context table. If omitted or missing, "
                "partner UniProt is inferred from PINDER-style candidate_id when possible."
            ),
        ),
    ] = DEFAULT_PARTNER_CONTEXT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for SIRT6 generic Gate 9 context rows."),
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
    """Build SIRT6 cofolding readiness context rows without live actions."""
    gate8 = read_table(gate8_summary)
    partner_context = (
        read_table(partner_context_input)
        if partner_context_input is not None and partner_context_input.exists()
        else None
    )

    context = write_sirt6_cofolding_readiness_context(
        gate8_summary=gate8,
        output=output,
        partner_context=partner_context,
        cofolding_input_review_status=cofolding_input_review_status,
    )

    typer.echo(f"SIRT6 cofolding readiness context rows: {context.height}")
    for status, count in sorted(sirt6_cofolding_context_status_counts(context).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote SIRT6 cofolding readiness context -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No embeddings were generated.")
    typer.echo("No cofolding inputs were generated.")
    typer.echo("No cofolding jobs were submitted.")
    typer.echo("No live structural calls were made.")
    typer.echo("No biological validation claim was made.")


if __name__ == "__main__":
    app()
