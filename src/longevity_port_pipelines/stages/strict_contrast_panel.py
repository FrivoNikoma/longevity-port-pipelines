from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages.strict_contrast_panel_readiness import (
    CONSERVATIVE_CLAIM_POLICY,
    strict_panel_readiness_for_statuses,
)

DEFAULT_INPUT = Path("data/interim/generic_strict_panel_input.csv")
DEFAULT_OUTPUT = Path("data/interim/generic_strict_panel_summary.csv")

KEY_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "priority",
]

REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "target_species",
    "target_species_taxid",
    "species_group",
    "coverage_preflight_status",
    "control_readiness_status",
    "contrast_readiness_status",
    "claim_policy",
}

STRICT_PANEL_SUMMARY_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "n_strict_panel_ready_species": pl.Int64,
    "n_strict_panel_blocked_species": pl.Int64,
    "n_strict_long_lived_ready": pl.Int64,
    "n_strict_short_lived_ready": pl.Int64,
    "strict_long_lived_species": pl.Utf8,
    "strict_short_lived_species": pl.Utf8,
    "blocked_target_species": pl.Utf8,
    "coverage_preflight_statuses": pl.Utf8,
    "control_readiness_statuses": pl.Utf8,
    "strict_panel_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "contrast_dry_run_allowed": pl.Boolean,
    "controlled_claim_allowed": pl.Boolean,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "strict_panel_note": pl.Utf8,
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


def _normalise_species_group(group: str) -> str:
    return group.strip().lower().replace("-", "_")


def _is_long_lived_group(group: str) -> bool:
    return _normalise_species_group(group).startswith("long_lived")


def _is_short_lived_group(group: str) -> bool:
    return _normalise_species_group(group).startswith("short_lived")


def _is_coverage_ready(row: dict[str, Any]) -> bool:
    return _as_str(row, "coverage_preflight_status") == "coverage_preflight_ready"


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


def _empty_summary() -> pl.DataFrame:
    return pl.DataFrame(schema=STRICT_PANEL_SUMMARY_SCHEMA)


def _summary_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return _empty_summary()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in STRICT_PANEL_SUMMARY_SCHEMA.items()
        ]
    )


def build_generic_strict_panel_summary(strict_panel_input: pl.DataFrame) -> pl.DataFrame:
    validate_required_columns(
        strict_panel_input,
        REQUIRED_COLUMNS,
        "strict_panel_input",
    )
    if strict_panel_input.is_empty():
        return _empty_summary()

    rows: list[dict[str, Any]] = []
    for key_row in (
        strict_panel_input.select(KEY_COLUMNS).unique().sort(KEY_COLUMNS).iter_rows(named=True)
    ):
        candidate_frame = strict_panel_input
        for column in KEY_COLUMNS:
            candidate_frame = candidate_frame.filter(pl.col(column) == key_row[column])

        candidate_rows = list(candidate_frame.iter_rows(named=True))
        ready_rows = [row for row in candidate_rows if _is_coverage_ready(row)]
        blocked_rows = [row for row in candidate_rows if not _is_coverage_ready(row)]

        ready_long_lived = sorted(
            {
                _as_str(row, "target_species")
                for row in ready_rows
                if _is_long_lived_group(_as_str(row, "species_group"))
                and _as_str(row, "target_species")
            }
        )
        ready_short_lived = sorted(
            {
                _as_str(row, "target_species")
                for row in ready_rows
                if _is_short_lived_group(_as_str(row, "species_group"))
                and _as_str(row, "target_species")
            }
        )
        blocked_species = sorted(
            {
                _as_str(row, "target_species")
                for row in blocked_rows
                if _as_str(row, "target_species")
            }
        )

        coverage_statuses = _joined_unique_values(
            candidate_rows,
            "coverage_preflight_status",
        )
        control_statuses = _joined_unique_values(
            candidate_rows,
            "control_readiness_status",
        )
        readiness = strict_panel_readiness_for_statuses(
            n_candidate_rows=len(candidate_rows),
            n_strict_long_lived_ready=len(ready_long_lived),
            n_strict_short_lived_ready=len(ready_short_lived),
            coverage_preflight_statuses=coverage_statuses,
            control_readiness_statuses=control_statuses,
            claim_policy=_first_nonempty_value(
                candidate_rows,
                "claim_policy",
                CONSERVATIVE_CLAIM_POLICY,
            ),
        )

        rows.append(
            {
                **key_row,
                "n_strict_panel_ready_species": len(
                    {
                        _as_str(row, "target_species")
                        for row in ready_rows
                        if _as_str(row, "target_species")
                    }
                ),
                "n_strict_panel_blocked_species": len(blocked_species),
                "n_strict_long_lived_ready": len(ready_long_lived),
                "n_strict_short_lived_ready": len(ready_short_lived),
                "strict_long_lived_species": ",".join(ready_long_lived),
                "strict_short_lived_species": ",".join(ready_short_lived),
                "blocked_target_species": ",".join(blocked_species),
                "coverage_preflight_statuses": coverage_statuses,
                "control_readiness_statuses": control_statuses,
                "strict_panel_status": readiness.strict_panel_status,
                "recommended_next_action": readiness.recommended_next_action,
                "contrast_dry_run_allowed": readiness.contrast_dry_run_allowed,
                "controlled_claim_allowed": readiness.controlled_claim_allowed,
                "claim_policy": readiness.claim_policy,
                "claim_status": readiness.claim_status,
                "strict_panel_note": readiness.strict_panel_note,
            }
        )

    return _summary_from_rows(rows).sort(["strict_panel_status", "priority", "candidate_id"])


def strict_panel_status_counts(summary: pl.DataFrame) -> dict[str, int]:
    if summary.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in summary.group_by("strict_panel_status").len().iter_rows(named=True):
        counts[str(row["strict_panel_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    strict_panel_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet generic strict panel input table."),
    ] = DEFAULT_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the generic strict panel summary."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Build a generic strict panel summary without Biohub, Boltz, or claims."""
    input_frame = read_table(strict_panel_input)
    summary = build_generic_strict_panel_summary(input_frame)

    output.parent.mkdir(parents=True, exist_ok=True)
    summary.write_csv(output)

    typer.echo(f"generic strict panel summary rows: {summary.height}")
    for status, count in sorted(strict_panel_status_counts(summary).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote generic strict panel summary -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo(
        "No embeddings, enrichment statistics, cofolding inputs, or biological claims were computed."
    )


if __name__ == "__main__":
    app()
