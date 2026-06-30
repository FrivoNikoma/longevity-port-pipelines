from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

DEFAULT_CONTRAST_READY_INPUT = Path("data/interim/sirt6_contrast_ready_subset.csv")
DEFAULT_NEGATOME_READINESS_INPUT = Path(
    "data/interim/sirt6_candidate_negatome_readiness_matrix.csv"
)
DEFAULT_OUTPUT = Path("data/interim/sirt6_candidate_contrast_gate.csv")

KEY_COLUMNS = ["candidate_id", "pdb_id", "chain", "source_uniprot", "priority"]

CONTRAST_REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "n_coverage_ready_species",
    "n_long_lived_ready",
    "n_short_lived_ready",
    "ready_long_lived_species",
    "ready_short_lived_species",
    "contrast_readiness_status",
}

NEGATOME_REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "baseline_input_status",
    "species_coverage_status",
    "negatome_status",
    "negative_partner_uniprot",
    "missing_negatome_species",
}

CONTRAST_GATE_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "contrast_readiness_status": pl.Utf8,
    "n_coverage_ready_species": pl.Int64,
    "n_long_lived_ready": pl.Int64,
    "n_short_lived_ready": pl.Int64,
    "ready_long_lived_species": pl.Utf8,
    "ready_short_lived_species": pl.Utf8,
    "baseline_input_status": pl.Utf8,
    "species_coverage_status": pl.Utf8,
    "negatome_status": pl.Utf8,
    "negative_partner_uniprot": pl.Utf8,
    "missing_negatome_species": pl.Utf8,
    "strict_contrast_gate_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "gate_note": pl.Utf8,
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


def _as_int(row: dict[str, Any], column: str) -> int:
    value = row.get(column)
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)

    text = str(value).strip()
    if not text:
        return 0

    return int(text)


def _key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        _as_str(row, "candidate_id"),
        _as_str(row, "pdb_id"),
        _as_str(row, "chain"),
        _as_str(row, "source_uniprot"),
        _as_str(row, "priority"),
    )


def empty_contrast_gate() -> pl.DataFrame:
    return pl.DataFrame(schema=CONTRAST_GATE_SCHEMA)


def _gate_status(
    *,
    contrast_readiness_status: str,
    baseline_input_status: str,
    species_coverage_status: str,
    negatome_status: str,
) -> str:
    if contrast_readiness_status != "contrast_ready":
        return "blocked_contrast_coverage"

    if baseline_input_status != "input_prepared":
        return "blocked_baseline_input"

    if species_coverage_status != "complete_species_coverage":
        return "blocked_species_coverage"

    if negatome_status != "present_existing":
        return "blocked_negatome_controls"

    return "eligible_for_contrast_dry_run"


def _recommended_next_action(gate_status: str) -> str:
    if gate_status == "blocked_contrast_coverage":
        return "repair_contrast_species_coverage"
    if gate_status == "blocked_baseline_input":
        return "fix_baseline_input"
    if gate_status == "blocked_species_coverage":
        return "fix_species_coverage"
    if gate_status == "blocked_negatome_controls":
        return "fix_negatome_controls"
    return "prepare_contrast_dry_run"


def _gate_note(gate_status: str) -> str:
    if gate_status == "blocked_contrast_coverage":
        return (
            "Coverage-only long-lived vs short-lived contrast readiness is incomplete; "
            "do not run or claim contrast results."
        )

    if gate_status == "blocked_baseline_input":
        return "Baseline PINDER input is not prepared; candidate contrast cannot proceed."

    if gate_status == "blocked_species_coverage":
        return (
            "Strict species provenance coverage is incomplete; contrast remains a "
            "dry-run planning layer only."
        )

    if gate_status == "blocked_negatome_controls":
        return "NEGATOME-style controls are incomplete; controlled enrichment cannot be claimed."

    return (
        "Candidate passes dry-run gate checks, but no enrichment statistic or biological "
        "claim is computed here."
    )


def _gate_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return empty_contrast_gate()

    return pl.DataFrame(rows).select(
        [pl.col(column).cast(dtype).alias(column) for column, dtype in CONTRAST_GATE_SCHEMA.items()]
    )


def build_candidate_contrast_gate(
    *,
    contrast_ready: pl.DataFrame,
    negatome_readiness: pl.DataFrame,
) -> pl.DataFrame:
    validate_required_columns(contrast_ready, CONTRAST_REQUIRED_COLUMNS, "contrast_ready")
    validate_required_columns(
        negatome_readiness,
        NEGATOME_REQUIRED_COLUMNS,
        "negatome_readiness",
    )

    contrast_by_key = {_key(row): row for row in contrast_ready.iter_rows(named=True)}
    negatome_by_key = {_key(row): row for row in negatome_readiness.iter_rows(named=True)}

    rows: list[dict[str, Any]] = []

    for key in sorted(set(contrast_by_key) | set(negatome_by_key)):
        contrast = contrast_by_key.get(key, {})
        negatome = negatome_by_key.get(key, {})

        contrast_status = _as_str(
            contrast,
            "contrast_readiness_status",
            "missing_contrast_readiness_row",
        )
        baseline_status = _as_str(negatome, "baseline_input_status", "not_audited")
        species_status = _as_str(negatome, "species_coverage_status", "not_audited")
        negatome_status = _as_str(negatome, "negatome_status", "not_audited")

        gate_status = _gate_status(
            contrast_readiness_status=contrast_status,
            baseline_input_status=baseline_status,
            species_coverage_status=species_status,
            negatome_status=negatome_status,
        )

        rows.append(
            {
                "candidate_id": key[0],
                "pdb_id": key[1],
                "chain": key[2],
                "source_uniprot": key[3],
                "priority": key[4],
                "contrast_readiness_status": contrast_status,
                "n_coverage_ready_species": _as_int(
                    contrast,
                    "n_coverage_ready_species",
                ),
                "n_long_lived_ready": _as_int(contrast, "n_long_lived_ready"),
                "n_short_lived_ready": _as_int(contrast, "n_short_lived_ready"),
                "ready_long_lived_species": _as_str(
                    contrast,
                    "ready_long_lived_species",
                ),
                "ready_short_lived_species": _as_str(
                    contrast,
                    "ready_short_lived_species",
                ),
                "baseline_input_status": baseline_status,
                "species_coverage_status": species_status,
                "negatome_status": negatome_status,
                "negative_partner_uniprot": _as_str(
                    negatome,
                    "negative_partner_uniprot",
                ),
                "missing_negatome_species": _as_str(
                    negatome,
                    "missing_negatome_species",
                ),
                "strict_contrast_gate_status": gate_status,
                "recommended_next_action": _recommended_next_action(gate_status),
                "gate_note": _gate_note(gate_status),
            }
        )

    return _gate_from_rows(rows).sort(["strict_contrast_gate_status", "priority", "candidate_id"])


def gate_status_counts(gate: pl.DataFrame) -> dict[str, int]:
    if gate.is_empty():
        return {}

    counts: dict[str, int] = {}
    grouped = gate.group_by("strict_contrast_gate_status").len()

    for row in grouped.iter_rows(named=True):
        counts[str(row["strict_contrast_gate_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    contrast_ready_input: Annotated[
        Path,
        typer.Option(
            help=(
                "CSV/parquet contrast-ready subset produced by candidate-species-coverage-matrix."
            )
        ),
    ] = DEFAULT_CONTRAST_READY_INPUT,
    negatome_readiness_input: Annotated[
        Path,
        typer.Option(
            help=(
                "CSV/parquet NEGATOME readiness matrix produced by "
                "cofolding-candidate-preflight-batch."
            )
        ),
    ] = DEFAULT_NEGATOME_READINESS_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the candidate contrast gate table."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Join coverage and NEGATOME diagnostics into a no-claims contrast gate table."""
    contrast_ready = read_table(contrast_ready_input)
    negatome_readiness = read_table(negatome_readiness_input)

    gate = build_candidate_contrast_gate(
        contrast_ready=contrast_ready,
        negatome_readiness=negatome_readiness,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    gate.write_csv(output)

    typer.echo(f"candidate contrast gate rows: {gate.height}")
    for status, count in sorted(gate_status_counts(gate).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote candidate contrast gate -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No enrichment statistics or biological claims were computed.")


if __name__ == "__main__":
    app()
