from __future__ import annotations

from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from longevity_port_pipelines.stages import gated_contrast
from longevity_port_pipelines.stages import (
    sirt6_generic_gated_contrast_input as input_stage,
)

DEFAULT_ENRICHMENT_INPUT = input_stage.DEFAULT_ENRICHMENT_INPUT
DEFAULT_GATE_INPUT = input_stage.DEFAULT_GATE_INPUT
DEFAULT_GENERIC_INPUT_OUTPUT = input_stage.DEFAULT_OUTPUT
DEFAULT_OUTPUT = Path("data/output/sirt6_generic_gated_contrast_summary.csv")

app = typer.Typer(add_completion=False)


def build_sirt6_generic_gated_contrast_outputs(
    *,
    enrichment: pl.DataFrame,
    candidate_gate: pl.DataFrame,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Build SIRT6 generic Gate 8 input and summary outputs.

    This is a dry-run-compatible wrapper around the SIRT6 generic input bridge
    and the generic gated contrast runtime. It does not compute new enrichment
    statistics, call Biohub or Boltz, create cofolding inputs, run live
    structural calls, or make biological claims.
    """
    generic_input = input_stage.build_sirt6_generic_gated_contrast_input(
        enrichment=enrichment,
        candidate_gate=candidate_gate,
    )
    summary = gated_contrast.build_generic_gated_contrast(generic_input)

    return generic_input, summary


def write_sirt6_generic_gated_contrast_outputs(
    *,
    enrichment: pl.DataFrame,
    candidate_gate: pl.DataFrame,
    generic_input_output: Path,
    output: Path,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    generic_input, summary = build_sirt6_generic_gated_contrast_outputs(
        enrichment=enrichment,
        candidate_gate=candidate_gate,
    )

    generic_input_output.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    generic_input.write_csv(generic_input_output)
    summary.write_csv(output)

    return generic_input, summary


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
    generic_input_output: Annotated[
        Path,
        typer.Option(help="Output CSV path for SIRT6 generic gated contrast input rows."),
    ] = DEFAULT_GENERIC_INPUT_OUTPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the SIRT6 generic gated contrast summary."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Build SIRT6 generic gated contrast input and summary without live actions."""
    enrichment = input_stage.read_table(enrichment_input)
    candidate_gate = input_stage.read_table(gate_input)

    generic_input, summary = write_sirt6_generic_gated_contrast_outputs(
        enrichment=enrichment,
        candidate_gate=candidate_gate,
        generic_input_output=generic_input_output,
        output=output,
    )

    typer.echo(f"SIRT6 generic gated contrast input rows: {generic_input.height}")
    typer.echo(f"SIRT6 generic gated contrast summary rows: {summary.height}")
    for status, count in sorted(gated_contrast.gated_contrast_status_counts(summary).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote SIRT6 generic gated contrast input -> {generic_input_output}")
    typer.echo(f"Wrote SIRT6 generic gated contrast summary -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo(
        "No embeddings, cofolding inputs, live structural calls, or biological claims were computed."
    )


if __name__ == "__main__":
    app()
