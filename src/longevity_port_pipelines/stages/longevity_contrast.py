from __future__ import annotations

import importlib
from pathlib import Path
from typing import Annotated, Any, cast

import polars as pl
import typer

from longevity_port_pipelines.config import LONG_LIVED_SPECIES, SHORT_LIVED_SPECIES
from longevity_port_pipelines.stages import candidate_contrast_gate as gate_stage

DEFAULT_ENRICHMENT_INPUT = Path("data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet")
DEFAULT_GATE_INPUT = gate_stage.DEFAULT_OUTPUT
DEFAULT_OUTPUT = Path("data/output/sirt6_gated_longevity_contrast.csv")
DEFAULT_BLOCKED_OUTPUT = Path("data/output/sirt6_gated_longevity_contrast_blocked.csv")

ELIGIBLE_GATE_STATUS = "eligible_for_contrast_dry_run"

DEFAULT_SHORT_LIVED_SPECIES = [species.name for species in SHORT_LIVED_SPECIES]
DEFAULT_LONG_LIVED_SPECIES = [species.name for species in LONG_LIVED_SPECIES]

GATE_REQUIRED_COLUMNS = {
    "candidate_id",
    "chain",
    "strict_contrast_gate_status",
    "recommended_next_action",
    "gate_note",
}

BLOCKED_GATE_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "strict_contrast_gate_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "gate_note": pl.Utf8,
}

GATED_CONTRAST_SCHEMA = {
    "complex_id": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "long_lived_species": pl.Utf8,
    "short_lived_species": pl.Utf8,
    "short_lived_control_count": pl.Int64,
    "long_enrichment_ratio": pl.Float64,
    "short_enrichment_ratio": pl.Float64,
    "enrichment_delta": pl.Float64,
    "enrichment_log2_ratio": pl.Float64,
    "long_effect_size": pl.Float64,
    "short_effect_size": pl.Float64,
    "effect_size_delta": pl.Float64,
    "long_interface_mean_delta": pl.Float64,
    "short_interface_mean_delta": pl.Float64,
    "interface_mean_delta_delta": pl.Float64,
    "long_noninterface_mean_delta": pl.Float64,
    "short_noninterface_mean_delta": pl.Float64,
    "noninterface_mean_delta_delta": pl.Float64,
    "long_p_two_sided": pl.Float64,
    "short_p_two_sided": pl.Float64,
    "long_is_predicted_structure": pl.Boolean,
    "short_is_predicted_structure": pl.Boolean,
    "contrast_class": pl.Utf8,
    "contrast_priority": pl.Int64,
    "contrast_note": pl.Utf8,
    "abs_enrichment_delta": pl.Float64,
    "abs_effect_size_delta": pl.Float64,
    "strict_contrast_gate_status": pl.Utf8,
    "gate_recommended_next_action": pl.Utf8,
    "gate_note": pl.Utf8,
    "contrast_checkpoint_policy": pl.Utf8,
    "contrast_checkpoint_note": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def _contrast_module() -> Any:
    """Load the existing script module without duplicating contrast logic."""
    return importlib.import_module("scripts.compute_longevity_contrast")


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


def _empty_blocked_gate() -> pl.DataFrame:
    return pl.DataFrame(schema=BLOCKED_GATE_SCHEMA)


def _empty_gated_contrast() -> pl.DataFrame:
    return pl.DataFrame(schema=GATED_CONTRAST_SCHEMA)


def _select_blocked_schema(frame: pl.DataFrame) -> pl.DataFrame:
    if frame.is_empty():
        return _empty_blocked_gate()

    columns = []
    for column, dtype in BLOCKED_GATE_SCHEMA.items():
        if column in frame.columns:
            columns.append(pl.col(column).cast(dtype).alias(column))
        else:
            columns.append(pl.lit("").cast(dtype).alias(column))

    return frame.select(columns)


def _select_gated_contrast_schema(frame: pl.DataFrame) -> pl.DataFrame:
    if frame.is_empty():
        return _empty_gated_contrast()

    return frame.select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in GATED_CONTRAST_SCHEMA.items()
        ]
    )


def eligible_gate_rows(candidate_gate: pl.DataFrame) -> pl.DataFrame:
    validate_required_columns(candidate_gate, GATE_REQUIRED_COLUMNS, "candidate_gate")
    return candidate_gate.filter(pl.col("strict_contrast_gate_status") == ELIGIBLE_GATE_STATUS)


def blocked_contrast_gate_rows(candidate_gate: pl.DataFrame) -> pl.DataFrame:
    validate_required_columns(candidate_gate, GATE_REQUIRED_COLUMNS, "candidate_gate")
    blocked = candidate_gate.filter(pl.col("strict_contrast_gate_status") != ELIGIBLE_GATE_STATUS)
    return _select_blocked_schema(blocked)


def _eligible_enrichment_rows(
    *,
    enrichment: pl.DataFrame,
    candidate_gate: pl.DataFrame,
) -> pl.DataFrame:
    eligible = eligible_gate_rows(candidate_gate)
    if eligible.is_empty():
        return enrichment.clear()

    eligible_keys = (
        eligible.select(
            [
                pl.col("candidate_id").alias("complex_id"),
                pl.col("chain"),
            ]
        )
        .unique()
        .sort(["complex_id", "chain"])
    )

    return enrichment.join(eligible_keys, on=["complex_id", "chain"], how="inner")


def _eligible_gate_metadata(candidate_gate: pl.DataFrame) -> pl.DataFrame:
    eligible = eligible_gate_rows(candidate_gate)
    if eligible.is_empty():
        return pl.DataFrame(
            schema={
                "complex_id": pl.Utf8,
                "chain": pl.Utf8,
                "strict_contrast_gate_status": pl.Utf8,
                "gate_recommended_next_action": pl.Utf8,
                "gate_note": pl.Utf8,
            }
        )

    return eligible.select(
        [
            pl.col("candidate_id").alias("complex_id"),
            pl.col("chain"),
            pl.col("strict_contrast_gate_status"),
            pl.col("recommended_next_action").alias("gate_recommended_next_action"),
            pl.col("gate_note"),
        ]
    ).unique()


def build_gated_longevity_contrast(
    *,
    enrichment: pl.DataFrame,
    candidate_gate: pl.DataFrame,
    short_lived_species: list[str] | None = None,
    long_lived_species: list[str] | None = None,
    divergent_threshold: float = 1.2,
    constrained_threshold: float = 0.8,
    baseline_neutral_upper: float = 1.1,
    baseline_neutral_lower: float = 0.9,
    min_enrichment_delta: float = 0.2,
    min_abs_effect: float = 0.2,
) -> pl.DataFrame:
    """Build a gated technical longevity contrast checkpoint.

    This function reuses the existing longevity contrast calculator, but only
    after the candidate contrast gate has marked candidate/chain rows as eligible
    for dry-run contrast planning. The output remains a technical checkpoint and
    must not be interpreted as a validated biological signal.
    """
    validate_required_columns(candidate_gate, GATE_REQUIRED_COLUMNS, "candidate_gate")

    eligible_enrichment = _eligible_enrichment_rows(
        enrichment=enrichment,
        candidate_gate=candidate_gate,
    )
    if eligible_enrichment.is_empty():
        return _empty_gated_contrast()

    short_lived = short_lived_species or DEFAULT_SHORT_LIVED_SPECIES
    long_lived = long_lived_species or DEFAULT_LONG_LIVED_SPECIES

    technical_contrast = cast(
        pl.DataFrame,
        _contrast_module().build_longevity_contrast(
            eligible_enrichment,
            short_lived_species=short_lived,
            long_lived_species=long_lived,
            divergent_threshold=divergent_threshold,
            constrained_threshold=constrained_threshold,
            baseline_neutral_upper=baseline_neutral_upper,
            baseline_neutral_lower=baseline_neutral_lower,
            min_enrichment_delta=min_enrichment_delta,
            min_abs_effect=min_abs_effect,
        ),
    )

    gate_metadata = _eligible_gate_metadata(candidate_gate)
    gated = technical_contrast.join(gate_metadata, on=["complex_id", "chain"], how="left")

    gated = gated.with_columns(
        [
            pl.col("complex_id").alias("candidate_id"),
            pl.lit("technical_checkpoint_no_claim").alias("contrast_checkpoint_policy"),
            pl.lit(
                "Gated technical contrast checkpoint only; not a validated biological signal."
            ).alias("contrast_checkpoint_note"),
        ]
    )

    return _select_gated_contrast_schema(gated)


@app.command()
def main(
    enrichment_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet mapped enrichment table."),
    ] = DEFAULT_ENRICHMENT_INPUT,
    gate_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet candidate contrast gate table."),
    ] = DEFAULT_GATE_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for gated longevity contrast rows."),
    ] = DEFAULT_OUTPUT,
    blocked_output: Annotated[
        Path | None,
        typer.Option(help="Optional output CSV path for blocked gate rows."),
    ] = DEFAULT_BLOCKED_OUTPUT,
    short_lived_species: Annotated[
        list[str] | None,
        typer.Option(help="Short-lived control species. Repeat option for multiple species."),
    ] = None,
    long_lived_species: Annotated[
        list[str] | None,
        typer.Option(help="Long-lived species. Repeat option for multiple species."),
    ] = None,
    divergent_threshold: Annotated[
        float,
        typer.Option(help="Enrichment ratio threshold for interface divergence."),
    ] = 1.2,
    constrained_threshold: Annotated[
        float,
        typer.Option(help="Enrichment ratio threshold for interface constraint."),
    ] = 0.8,
    baseline_neutral_upper: Annotated[
        float,
        typer.Option(help="Upper enrichment ratio bound for a near-neutral short-lived baseline."),
    ] = 1.1,
    baseline_neutral_lower: Annotated[
        float,
        typer.Option(help="Lower enrichment ratio bound for a near-neutral short-lived baseline."),
    ] = 0.9,
    min_enrichment_delta: Annotated[
        float,
        typer.Option(help="Minimum long-vs-short enrichment-ratio difference."),
    ] = 0.2,
    min_abs_effect: Annotated[
        float,
        typer.Option(help="Minimum absolute Cohen's d for directional contrast classes."),
    ] = 0.2,
) -> None:
    """Run gated longevity contrast as a technical checkpoint with no claims."""
    enrichment = read_table(enrichment_input)
    candidate_gate = read_table(gate_input)

    contrast = build_gated_longevity_contrast(
        enrichment=enrichment,
        candidate_gate=candidate_gate,
        short_lived_species=short_lived_species,
        long_lived_species=long_lived_species,
        divergent_threshold=divergent_threshold,
        constrained_threshold=constrained_threshold,
        baseline_neutral_upper=baseline_neutral_upper,
        baseline_neutral_lower=baseline_neutral_lower,
        min_enrichment_delta=min_enrichment_delta,
        min_abs_effect=min_abs_effect,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    contrast.write_csv(output)

    typer.echo(f"gated longevity contrast rows: {contrast.height}")
    typer.echo(f"Wrote gated longevity contrast -> {output}")

    if blocked_output is not None:
        blocked = blocked_contrast_gate_rows(candidate_gate)
        blocked_output.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_csv(blocked_output)
        typer.echo(f"blocked gate rows: {blocked.height}")
        typer.echo(f"Wrote blocked gate rows -> {blocked_output}")

    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No embeddings were generated.")
    typer.echo("No biological claims were made.")


if __name__ == "__main__":
    app()
