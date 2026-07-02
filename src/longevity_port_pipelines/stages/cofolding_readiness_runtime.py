from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages.cofolding_readiness import cofolding_readiness_for_row

DEFAULT_GATE8_SUMMARY = Path("data/interim/generic_gated_contrast_summary.csv")
DEFAULT_CONTEXT = Path("data/interim/generic_cofolding_readiness_context.csv")
DEFAULT_OUTPUT = Path("data/interim/generic_cofolding_readiness_summary.csv")

KEY_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
]

JOIN_COLUMNS = [
    *KEY_COLUMNS,
    "target_species",
]

GATE8_REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "priority",
    "long_lived_species",
    "short_lived_species",
    "short_lived_control_count",
    "contrast_class",
    "contrast_requires_review",
    "robustness_status",
    "robustness_note",
    "contrast_status",
    "recommended_next_action",
    "contrast_dry_run_allowed",
    "controlled_claim_allowed",
    "claim_policy",
    "claim_status",
    "contrast_note",
}

CONTEXT_REQUIRED_COLUMNS = {
    *JOIN_COLUMNS,
    "partner_uniprot",
    "partner_context_status",
    "source_provenance_status",
    "cofolding_input_review_status",
    "live_opt_in_status",
}

CONTEXT_COLUMNS = [
    *JOIN_COLUMNS,
    "partner_uniprot",
    "partner_context_status",
    "source_provenance_status",
    "cofolding_input_review_status",
    "live_opt_in_status",
]

COFOLDING_READINESS_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "target_species": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "contrast_class": pl.Utf8,
    "contrast_status": pl.Utf8,
    "robustness_status": pl.Utf8,
    "cofolding_input_review_status": pl.Utf8,
    "cofolding_readiness_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "cofolding_dry_run_allowed": pl.Boolean,
    "live_cofolding_allowed": pl.Boolean,
    "controlled_claim_allowed": pl.Boolean,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "cofolding_readiness_note": pl.Utf8,
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
    return pl.DataFrame(schema=COFOLDING_READINESS_SCHEMA)


def _summary_from_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    if not rows:
        return _empty_summary()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in COFOLDING_READINESS_SCHEMA.items()
        ]
    )


def _context_for_join(cofolding_context: pl.DataFrame) -> pl.DataFrame:
    return (
        cofolding_context.select(CONTEXT_COLUMNS)
        .sort(JOIN_COLUMNS)
        .unique(subset=JOIN_COLUMNS, keep="first", maintain_order=True)
    )


def build_generic_cofolding_readiness(
    gate8_summary: pl.DataFrame,
    cofolding_context: pl.DataFrame,
) -> pl.DataFrame:
    """Build a generic Gate 9 cofolding readiness summary.

    This is a table-only runtime checklist. It applies the generic Gate 9
    helper to Gate 8 rows plus reviewed cofolding context. It does not call
    Biohub, does not call Boltz, does not generate embeddings, does not build
    cofolding inputs, and does not submit live structural jobs.
    """
    validate_required_columns(gate8_summary, GATE8_REQUIRED_COLUMNS, "gate8_summary")
    validate_required_columns(cofolding_context, CONTEXT_REQUIRED_COLUMNS, "cofolding_context")

    if gate8_summary.is_empty():
        return _empty_summary()

    gate8_with_target = gate8_summary.with_columns(
        pl.col("long_lived_species").cast(pl.Utf8).alias("target_species")
    )
    context = _context_for_join(cofolding_context)
    joined = gate8_with_target.join(context, on=JOIN_COLUMNS, how="left")

    output_rows: list[dict[str, object]] = []
    for row in joined.iter_rows(named=True):
        readiness = cofolding_readiness_for_row(row)

        output_rows.append(
            {
                "candidate_set": _as_str(row, "candidate_set"),
                "lane_name": _as_str(row, "lane_name"),
                "candidate_id": _as_str(row, "candidate_id"),
                "pdb_id": _as_str(row, "pdb_id"),
                "chain": _as_str(row, "chain"),
                "source_uniprot": _as_str(row, "source_uniprot"),
                "priority": _as_str(row, "priority"),
                "target_species": _as_str(row, "target_species"),
                "partner_uniprot": _as_str(row, "partner_uniprot"),
                "contrast_class": _as_str(row, "contrast_class"),
                "contrast_status": _as_str(row, "contrast_status"),
                "robustness_status": _as_str(row, "robustness_status"),
                "cofolding_input_review_status": _as_str(
                    row,
                    "cofolding_input_review_status",
                ),
                **readiness.as_dict(),
            }
        )

    return _summary_from_rows(output_rows).sort(
        [
            "cofolding_readiness_status",
            "priority",
            "candidate_id",
            "target_species",
        ]
    )


def cofolding_readiness_status_counts(summary: pl.DataFrame) -> dict[str, int]:
    if summary.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in summary.group_by("cofolding_readiness_status").len().iter_rows(named=True):
        counts[str(row["cofolding_readiness_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    gate8_summary: Annotated[
        Path,
        typer.Option(help="CSV/parquet generic Gate 8 gated contrast summary table."),
    ] = DEFAULT_GATE8_SUMMARY,
    cofolding_context: Annotated[
        Path,
        typer.Option(help="CSV/parquet generic Gate 9 cofolding context table."),
    ] = DEFAULT_CONTEXT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the generic Gate 9 readiness summary."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Build a generic Gate 9 cofolding readiness summary without live actions."""
    gate8_frame = read_table(gate8_summary)
    context_frame = read_table(cofolding_context)
    summary = build_generic_cofolding_readiness(gate8_frame, context_frame)

    output.parent.mkdir(parents=True, exist_ok=True)
    summary.write_csv(output)

    typer.echo(f"generic cofolding readiness summary rows: {summary.height}")
    for status, count in sorted(cofolding_readiness_status_counts(summary).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote generic cofolding readiness summary -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo(
        "No embeddings, cofolding inputs, live structural calls, or biological claims were computed."
    )


if __name__ == "__main__":
    app()
