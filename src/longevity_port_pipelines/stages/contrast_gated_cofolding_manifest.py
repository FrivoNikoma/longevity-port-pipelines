from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages import longevity_contrast as contrast_stage

DEFAULT_GATED_CONTRAST_INPUT = contrast_stage.DEFAULT_OUTPUT
DEFAULT_BLOCKED_CONTRAST_INPUT = contrast_stage.DEFAULT_BLOCKED_OUTPUT
DEFAULT_GATE_INPUT = contrast_stage.DEFAULT_GATE_INPUT
DEFAULT_OUTPUT = Path("data/interim/sirt6_contrast_gated_cofolding_manifest.csv")
DEFAULT_BLOCKED_OUTPUT = Path("data/interim/sirt6_contrast_gated_cofolding_blocked_manifest.csv")

ELIGIBLE_CONTRAST_STATUS = "eligible_for_contrast_dry_run"
TECHNICAL_CHECKPOINT_POLICY = "technical_checkpoint_no_claim"

ELIGIBLE_COFOLDING_STATUS = "eligible_for_cofolding_dry_run"
BLOCKED_BY_CONTRAST_GATE = "blocked_by_contrast_gate"
BLOCKED_PENDING_MANUAL_REVIEW = "blocked_pending_manual_review"
BLOCKED_PENDING_NEGATOME_REPAIR = "blocked_pending_negatome_repair"
BLOCKED_PENDING_SPECIES_COVERAGE_REPAIR = "blocked_pending_species_coverage_repair"

GATED_CONTRAST_REQUIRED_COLUMNS = {
    "candidate_id",
    "pdb_id",
    "chain",
    "long_lived_species",
    "contrast_class",
    "strict_contrast_gate_status",
    "contrast_checkpoint_policy",
    "gate_recommended_next_action",
    "gate_note",
}

BLOCKED_CONTRAST_REQUIRED_COLUMNS = {
    "candidate_id",
    "pdb_id",
    "chain",
    "strict_contrast_gate_status",
    "recommended_next_action",
    "gate_note",
}

GATE_METADATA_REQUIRED_COLUMNS = {
    "candidate_id",
    "chain",
    "source_uniprot",
}

COFOLDING_MANIFEST_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "target_species": pl.Utf8,
    "contrast_class": pl.Utf8,
    "strict_contrast_gate_status": pl.Utf8,
    "contrast_checkpoint_policy": pl.Utf8,
    "gate_recommended_next_action": pl.Utf8,
    "gate_note": pl.Utf8,
    "cofolding_plan_status": pl.Utf8,
    "cofolding_plan_note": pl.Utf8,
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


def empty_cofolding_manifest() -> pl.DataFrame:
    return pl.DataFrame(schema=COFOLDING_MANIFEST_SCHEMA)


def _as_str(row: dict[str, Any], column: str, default: str = "") -> str:
    value = row.get(column)
    if value is None:
        return default
    return str(value).strip()


def _manifest_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return empty_cofolding_manifest()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in COFOLDING_MANIFEST_SCHEMA.items()
        ]
    )


def _source_uniprot_by_key(
    candidate_gate: pl.DataFrame | None,
) -> dict[tuple[str, str], str]:
    if candidate_gate is None:
        return {}

    validate_required_columns(candidate_gate, GATE_METADATA_REQUIRED_COLUMNS, "candidate_gate")

    source_by_key: dict[tuple[str, str], str] = {}
    for row in candidate_gate.iter_rows(named=True):
        key = (_as_str(row, "candidate_id"), _as_str(row, "chain"))
        source_by_key[key] = _as_str(row, "source_uniprot")

    return source_by_key


def _blocked_plan_status(*, gate_status: str, recommended_next_action: str) -> str:
    text = f"{gate_status} {recommended_next_action}".lower()

    if "negatome" in text:
        return BLOCKED_PENDING_NEGATOME_REPAIR

    if "coverage" in text:
        return BLOCKED_PENDING_SPECIES_COVERAGE_REPAIR

    if "strict" in text or "review" in text:
        return BLOCKED_PENDING_MANUAL_REVIEW

    return BLOCKED_BY_CONTRAST_GATE


def build_contrast_gated_cofolding_manifest(
    *,
    gated_contrast: pl.DataFrame,
    candidate_gate: pl.DataFrame | None = None,
) -> pl.DataFrame:
    """Build eligible dry-run cofolding planning rows from gated technical contrast rows.

    This stage only writes a planning manifest. It does not submit Boltz jobs, does not
    call the Boltz API, does not spend credits, and does not make biological claims.
    """
    validate_required_columns(
        gated_contrast,
        GATED_CONTRAST_REQUIRED_COLUMNS,
        "gated_contrast",
    )

    source_by_key = _source_uniprot_by_key(candidate_gate)

    rows: list[dict[str, Any]] = []
    for row in gated_contrast.iter_rows(named=True):
        if _as_str(row, "strict_contrast_gate_status") != ELIGIBLE_CONTRAST_STATUS:
            continue

        if _as_str(row, "contrast_checkpoint_policy") != TECHNICAL_CHECKPOINT_POLICY:
            continue

        candidate_id = _as_str(row, "candidate_id")
        chain = _as_str(row, "chain")
        source_uniprot = _as_str(row, "source_uniprot") or source_by_key.get(
            (candidate_id, chain),
            "",
        )

        rows.append(
            {
                "candidate_id": candidate_id,
                "pdb_id": _as_str(row, "pdb_id"),
                "chain": chain,
                "source_uniprot": source_uniprot,
                "target_species": _as_str(row, "long_lived_species"),
                "contrast_class": _as_str(row, "contrast_class"),
                "strict_contrast_gate_status": _as_str(row, "strict_contrast_gate_status"),
                "contrast_checkpoint_policy": _as_str(row, "contrast_checkpoint_policy"),
                "gate_recommended_next_action": _as_str(
                    row,
                    "gate_recommended_next_action",
                ),
                "gate_note": _as_str(row, "gate_note"),
                "cofolding_plan_status": ELIGIBLE_COFOLDING_STATUS,
                "cofolding_plan_note": (
                    "Eligible for cofolding dry-run planning only; no live Boltz "
                    "submission is permitted by this manifest."
                ),
            }
        )

    return _manifest_from_rows(rows)


def build_blocked_contrast_gated_cofolding_manifest(
    *,
    blocked_contrast: pl.DataFrame,
) -> pl.DataFrame:
    """Build blocked cofolding planning rows from blocked contrast-gate rows."""
    validate_required_columns(
        blocked_contrast,
        BLOCKED_CONTRAST_REQUIRED_COLUMNS,
        "blocked_contrast",
    )

    rows: list[dict[str, Any]] = []
    for row in blocked_contrast.iter_rows(named=True):
        gate_status = _as_str(row, "strict_contrast_gate_status")
        recommended_next_action = _as_str(row, "recommended_next_action")

        rows.append(
            {
                "candidate_id": _as_str(row, "candidate_id"),
                "pdb_id": _as_str(row, "pdb_id"),
                "chain": _as_str(row, "chain"),
                "source_uniprot": _as_str(row, "source_uniprot"),
                "target_species": "",
                "contrast_class": "",
                "strict_contrast_gate_status": gate_status,
                "contrast_checkpoint_policy": "",
                "gate_recommended_next_action": recommended_next_action,
                "gate_note": _as_str(row, "gate_note"),
                "cofolding_plan_status": _blocked_plan_status(
                    gate_status=gate_status,
                    recommended_next_action=recommended_next_action,
                ),
                "cofolding_plan_note": (
                    "Blocked by contrast-gate policy; excluded from live Boltz planning by default."
                ),
            }
        )

    return _manifest_from_rows(rows)


@app.command()
def main(
    gated_contrast_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet gated technical contrast table."),
    ] = DEFAULT_GATED_CONTRAST_INPUT,
    blocked_contrast_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet blocked contrast-gate table."),
    ] = DEFAULT_BLOCKED_CONTRAST_INPUT,
    gate_input: Annotated[
        Path | None,
        typer.Option(help="Optional candidate contrast gate table for source UniProt metadata."),
    ] = DEFAULT_GATE_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for eligible cofolding dry-run manifest rows."),
    ] = DEFAULT_OUTPUT,
    blocked_output: Annotated[
        Path,
        typer.Option(help="Output CSV path for blocked cofolding manifest rows."),
    ] = DEFAULT_BLOCKED_OUTPUT,
) -> None:
    gated_contrast = read_table(gated_contrast_input)
    blocked_contrast = read_table(blocked_contrast_input)
    candidate_gate = (
        read_table(gate_input) if gate_input is not None and gate_input.exists() else None
    )

    manifest = build_contrast_gated_cofolding_manifest(
        gated_contrast=gated_contrast,
        candidate_gate=candidate_gate,
    )
    blocked_manifest = build_blocked_contrast_gated_cofolding_manifest(
        blocked_contrast=blocked_contrast,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    blocked_output.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_csv(output)
    blocked_manifest.write_csv(blocked_output)

    typer.echo(f"Wrote eligible cofolding dry-run manifest rows: {manifest.height} -> {output}")
    typer.echo(
        f"Wrote blocked cofolding manifest rows: {blocked_manifest.height} -> {blocked_output}"
    )
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No embeddings were generated.")
    typer.echo("No cofolding jobs were submitted.")
    typer.echo("No Boltz credits were spent.")
    typer.echo("No biological validation claim was made.")
