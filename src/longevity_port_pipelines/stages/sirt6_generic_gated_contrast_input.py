from __future__ import annotations

import math
from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages import candidate_contrast_gate as gate_stage
from longevity_port_pipelines.stages import longevity_contrast as sirt6_contrast_stage
from longevity_port_pipelines.stages.gated_contrast_readiness import CONSERVATIVE_CLAIM_POLICY

DEFAULT_ENRICHMENT_INPUT = sirt6_contrast_stage.DEFAULT_ENRICHMENT_INPUT
DEFAULT_GATE_INPUT = gate_stage.DEFAULT_OUTPUT
DEFAULT_OUTPUT = Path("data/interim/sirt6_generic_gated_contrast_input.csv")

CANDIDATE_SET = "sirt6_dna_repair"
LANE_NAME = "sirt6_dna_repair"

ENRICHMENT_REQUIRED_COLUMNS = {
    "complex_id",
    "chain",
    "target_species",
    "enrichment_ratio",
    "effect_size_cohens_d",
    "interface_mean_delta",
    "noninterface_mean_delta",
    "p_two_sided",
}

GATE_REQUIRED_COLUMNS = {
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "priority",
    "strict_contrast_gate_status",
}

GENERIC_GATED_CONTRAST_INPUT_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "strict_panel_status": pl.Utf8,
    "contrast_dry_run_allowed": pl.Boolean,
    "controlled_claim_allowed": pl.Boolean,
    "target_species": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "species_group": pl.Utf8,
    "enrichment_ratio": pl.Float64,
    "effect_size": pl.Float64,
    "interface_mean_delta": pl.Float64,
    "noninterface_mean_delta": pl.Float64,
    "p_two_sided": pl.Float64,
    "is_predicted_structure": pl.Boolean,
    "claim_policy": pl.Utf8,
}

SPECIES_METADATA = {
    "naked_mole_rat": (10181, "long_lived_small_body"),
    "myotis": (59463, "long_lived_small_body"),
    "myotis_lucifugus": (59463, "long_lived_small_body"),
    "bowhead_whale": (27622, "long_lived_large_body"),
    "elephant": (9785, "long_lived_extended"),
    "african_elephant": (9785, "long_lived_extended"),
    "brandt_bat": (109478, "long_lived_extended"),
    "brandts_bat": (109478, "long_lived_extended"),
    "mouse": (10090, "short_lived_control"),
    "rat": (10116, "short_lived_control"),
    "hamster": (10036, "short_lived_control"),
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


def _empty_generic_gated_contrast_input() -> pl.DataFrame:
    return pl.DataFrame(schema=GENERIC_GATED_CONTRAST_INPUT_SCHEMA)


def _rows_to_generic_input(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return _empty_generic_gated_contrast_input()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in GENERIC_GATED_CONTRAST_INPUT_SCHEMA.items()
        ]
    )


def _species_metadata(target_species: str) -> tuple[int, str]:
    species = target_species.strip()
    if species not in SPECIES_METADATA:
        raise ValueError(
            f"Unknown SIRT6 target species for generic gated contrast input: {target_species!r}"
        )

    return SPECIES_METADATA[species]


def _gate_lookup(candidate_gate: pl.DataFrame) -> dict[tuple[str, str], dict[str, Any]]:
    validate_required_columns(candidate_gate, GATE_REQUIRED_COLUMNS, "candidate_gate")

    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in candidate_gate.iter_rows(named=True):
        key = (_as_str(row, "candidate_id"), _as_str(row, "chain"))
        if key in lookup:
            raise ValueError(f"candidate_gate has duplicate candidate/chain key: {key}")
        lookup[key] = row

    return lookup


def _gate_allows_contrast(gate_row: dict[str, Any]) -> bool:
    return (
        _as_str(gate_row, "strict_contrast_gate_status")
        == sirt6_contrast_stage.ELIGIBLE_GATE_STATUS
    )


def _strict_panel_status_for_generic_gate(gate_row: dict[str, Any]) -> str:
    strict_panel_status = _as_str(gate_row, "strict_panel_status")
    if strict_panel_status:
        return strict_panel_status

    if _gate_allows_contrast(gate_row):
        return "strict_panel_ready"

    return _as_str(
        gate_row,
        "strict_contrast_gate_status",
        "blocked_candidate_contrast_gate",
    )


def build_sirt6_generic_gated_contrast_input(
    *,
    enrichment: pl.DataFrame,
    candidate_gate: pl.DataFrame,
) -> pl.DataFrame:
    """Build generic Gate 8 input rows from the SIRT6 calibration lane.

    This is a bridge from the existing SIRT6 gated technical contrast checkpoint
    into the generic gated contrast runtime contract. It does not compute new
    enrichment statistics, does not call Biohub or Boltz, and does not make
    biological claims.
    """
    validate_required_columns(enrichment, ENRICHMENT_REQUIRED_COLUMNS, "enrichment")

    gate_by_key = _gate_lookup(candidate_gate)
    output_rows: list[dict[str, Any]] = []

    for enrichment_row in enrichment.iter_rows(named=True):
        key = (_as_str(enrichment_row, "complex_id"), _as_str(enrichment_row, "chain"))
        gate_row = gate_by_key.get(key)
        if gate_row is None:
            continue

        target_species = _as_str(enrichment_row, "target_species")
        target_species_taxid, species_group = _species_metadata(target_species)
        contrast_dry_run_allowed = _gate_allows_contrast(gate_row)

        output_rows.append(
            {
                "candidate_set": CANDIDATE_SET,
                "lane_name": LANE_NAME,
                "candidate_id": _as_str(gate_row, "candidate_id"),
                "pdb_id": _as_str(gate_row, "pdb_id"),
                "chain": _as_str(gate_row, "chain"),
                "source_uniprot": _as_str(gate_row, "source_uniprot"),
                "priority": _as_str(gate_row, "priority"),
                "strict_panel_status": _strict_panel_status_for_generic_gate(gate_row),
                "contrast_dry_run_allowed": contrast_dry_run_allowed,
                "controlled_claim_allowed": False,
                "target_species": target_species,
                "target_species_taxid": target_species_taxid,
                "species_group": species_group,
                "enrichment_ratio": _as_float(enrichment_row, "enrichment_ratio"),
                "effect_size": _as_float(enrichment_row, "effect_size_cohens_d"),
                "interface_mean_delta": _as_float(enrichment_row, "interface_mean_delta"),
                "noninterface_mean_delta": _as_float(
                    enrichment_row,
                    "noninterface_mean_delta",
                ),
                "p_two_sided": _as_float(enrichment_row, "p_two_sided"),
                "is_predicted_structure": _as_bool(
                    enrichment_row,
                    "is_predicted_structure",
                    default=False,
                ),
                "claim_policy": CONSERVATIVE_CLAIM_POLICY,
            }
        )

    return _rows_to_generic_input(output_rows)


@app.command()
def main(
    enrichment_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet SIRT6 enrichment rows."),
    ] = DEFAULT_ENRICHMENT_INPUT,
    gate_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet SIRT6 candidate contrast gate rows."),
    ] = DEFAULT_GATE_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for generic gated contrast input rows."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Build SIRT6 generic gated contrast input rows without live actions."""
    enrichment = read_table(enrichment_input)
    candidate_gate = read_table(gate_input)

    generic_input = build_sirt6_generic_gated_contrast_input(
        enrichment=enrichment,
        candidate_gate=candidate_gate,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    generic_input.write_csv(output)

    typer.echo(f"SIRT6 generic gated contrast input rows: {generic_input.height}")
    typer.echo(f"Wrote SIRT6 generic gated contrast input -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo(
        "No embeddings, cofolding inputs, live structural calls, or biological claims were computed."
    )


if __name__ == "__main__":
    app()
