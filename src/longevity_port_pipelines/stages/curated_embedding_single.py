from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

import polars as pl
import typer
from dotenv import load_dotenv

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.embed import (
    embed_or_load_sequence,
    embedding_path,
    get_biohub_token,
)
from longevity_port_pipelines.stages.ortholog_inputs import (
    filter_primary_curated_ortholog_candidates,
    validate_schema,
)

DEFAULT_CURATED_ORTHOLOGS = Path("data/input/curated_ortholog_candidates.csv")
DEFAULT_OUTPUT_DIR = Path("data/output")

EmbeddingRunStatus = Literal[
    "dry_run_missing",
    "dry_run_present",
    "skipped_existing",
    "live_completed",
]

app = typer.Typer(add_completion=False)


def load_runtime_env() -> None:
    """Load local runtime secrets from .env before live Biohub calls."""
    load_dotenv(dotenv_path=Path(".env"))


@dataclass(frozen=True)
class SingleCuratedEmbeddingPlan:
    complex_id: str
    chain: str
    target_species: str
    source_uniprot: str
    source_species_taxid: int
    target_species_taxid: int
    target_accession: str
    target_accession_db: str
    target_sequence: str
    target_sequence_length: int
    actual_sequence_length: int
    sequence_length_status: str
    model_name: str
    embedding_path: Path
    embedding_exists: bool


@dataclass(frozen=True)
class SingleCuratedEmbeddingResult:
    plan: SingleCuratedEmbeddingPlan
    status: EmbeddingRunStatus
    embedding_shape: str | None = None


def _as_str(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        raise ValueError(f"Missing value for {column}")
    return str(value).strip()


def _as_int(row: dict[str, object], column: str) -> int:
    value = row[column]
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        return int(value.strip())
    raise ValueError(f"Cannot interpret integer value for {column}: {value!r}")


def select_single_primary_curated_candidate(
    candidates: pl.DataFrame,
    *,
    complex_id: str,
    chain: str,
    target_species_taxid: int,
) -> dict[str, object]:
    validate_schema(candidates)

    primary_candidates = filter_primary_curated_ortholog_candidates(candidates)
    matches = primary_candidates.filter(
        (pl.col("complex_id") == complex_id)
        & (pl.col("chain") == chain)
        & (pl.col("target_species_taxid") == target_species_taxid)
    )

    if matches.height == 0:
        raise ValueError(
            "No primary curated ortholog candidate found for "
            f"complex_id={complex_id!r}, chain={chain!r}, "
            f"target_species_taxid={target_species_taxid}"
        )

    if matches.height > 1:
        raise ValueError(
            "Multiple primary curated ortholog candidates found for "
            f"complex_id={complex_id!r}, chain={chain!r}, "
            f"target_species_taxid={target_species_taxid}"
        )

    return matches.row(0, named=True)


def build_single_curated_embedding_plan(
    candidates: pl.DataFrame,
    *,
    output_dir: Path,
    model_name: str,
    complex_id: str,
    chain: str,
    target_species_taxid: int,
) -> SingleCuratedEmbeddingPlan:
    row = select_single_primary_curated_candidate(
        candidates,
        complex_id=complex_id,
        chain=chain,
        target_species_taxid=target_species_taxid,
    )

    target_sequence = _as_str(row, "target_sequence")
    recorded_length = _as_int(row, "target_sequence_length")
    actual_length = len(target_sequence)

    path = embedding_path(
        output_dir=output_dir,
        model_name=model_name,
        complex_id=complex_id,
        chain=chain,
        species_taxid=target_species_taxid,
    )

    sequence_length_status = "matches"
    if recorded_length != actual_length:
        sequence_length_status = "mismatch"

    return SingleCuratedEmbeddingPlan(
        complex_id=complex_id,
        chain=chain,
        target_species=_as_str(row, "target_species"),
        source_uniprot=_as_str(row, "source_uniprot"),
        source_species_taxid=_as_int(row, "source_species_taxid"),
        target_species_taxid=target_species_taxid,
        target_accession=_as_str(row, "target_accession"),
        target_accession_db=_as_str(row, "target_accession_db"),
        target_sequence=target_sequence,
        target_sequence_length=recorded_length,
        actual_sequence_length=actual_length,
        sequence_length_status=sequence_length_status,
        model_name=model_name,
        embedding_path=path,
        embedding_exists=path.exists(),
    )


def _refreshed_plan_after_embedding(
    plan: SingleCuratedEmbeddingPlan,
) -> SingleCuratedEmbeddingPlan:
    return SingleCuratedEmbeddingPlan(
        complex_id=plan.complex_id,
        chain=plan.chain,
        target_species=plan.target_species,
        source_uniprot=plan.source_uniprot,
        source_species_taxid=plan.source_species_taxid,
        target_species_taxid=plan.target_species_taxid,
        target_accession=plan.target_accession,
        target_accession_db=plan.target_accession_db,
        target_sequence=plan.target_sequence,
        target_sequence_length=plan.target_sequence_length,
        actual_sequence_length=plan.actual_sequence_length,
        sequence_length_status=plan.sequence_length_status,
        model_name=plan.model_name,
        embedding_path=plan.embedding_path,
        embedding_exists=plan.embedding_path.exists(),
    )


def run_single_curated_embedding(
    plan: SingleCuratedEmbeddingPlan,
    *,
    output_dir: Path,
    api_url: str,
    yes_live: bool,
    skip_existing: bool = True,
) -> SingleCuratedEmbeddingResult:
    if not yes_live:
        status: EmbeddingRunStatus = "dry_run_missing"
        if plan.embedding_exists:
            status = "dry_run_present"
        return SingleCuratedEmbeddingResult(plan=plan, status=status)

    if plan.sequence_length_status != "matches":
        raise ValueError(
            "Refusing live embedding because recorded target_sequence_length "
            "does not match actual sequence length for "
            f"{plan.complex_id} {plan.chain} taxid={plan.target_species_taxid}: "
            f"recorded={plan.target_sequence_length}, "
            f"actual={plan.actual_sequence_length}"
        )

    if skip_existing and plan.embedding_path.exists():
        return SingleCuratedEmbeddingResult(plan=plan, status="skipped_existing")

    token = get_biohub_token()
    embedding = embed_or_load_sequence(
        complex_id=plan.complex_id,
        chain=plan.chain,
        sequence=plan.target_sequence,
        species_taxid=plan.target_species_taxid,
        model=plan.model_name,
        api_url=api_url,
        token=token,
        output_dir=output_dir,
        is_predicted_structure=True,
    )

    shape = f"{embedding.embeddings.shape[0]}x{embedding.embeddings.shape[1]}"

    return SingleCuratedEmbeddingResult(
        plan=_refreshed_plan_after_embedding(plan),
        status="live_completed",
        embedding_shape=shape,
    )


def _echo_plan(plan: SingleCuratedEmbeddingPlan) -> None:
    typer.echo(f"complex_id: {plan.complex_id}")
    typer.echo(f"chain: {plan.chain}")
    typer.echo(f"target_species: {plan.target_species}")
    typer.echo(f"target_species_taxid: {plan.target_species_taxid}")
    typer.echo(f"target_accession: {plan.target_accession}")
    typer.echo(f"target_accession_db: {plan.target_accession_db}")
    typer.echo(f"model_name: {plan.model_name}")
    typer.echo(f"target_sequence_length: {plan.target_sequence_length}")
    typer.echo(f"actual_sequence_length: {plan.actual_sequence_length}")
    typer.echo(f"sequence_length_status: {plan.sequence_length_status}")
    typer.echo(f"embedding_path: {plan.embedding_path}")
    typer.echo(f"embedding_exists: {plan.embedding_exists}")


@app.command()
def main(
    complex_id: Annotated[str, typer.Option(help="PINDER-style complex id")],
    chain: Annotated[str, typer.Option(help="Chain role: receptor or ligand")],
    target_species_taxid: Annotated[int, typer.Option(help="Target species NCBI taxid")],
    curated_orthologs: Annotated[
        Path,
        typer.Option(help="Curated ortholog candidate input CSV"),
    ] = DEFAULT_CURATED_ORTHOLOGS,
    output_dir: Annotated[
        Path,
        typer.Option(help="Pipeline output directory"),
    ] = DEFAULT_OUTPUT_DIR,
    model_name: Annotated[
        str | None,
        typer.Option(help="ESMC model name override"),
    ] = None,
    biohub_api_url: Annotated[
        str | None,
        typer.Option(help="Biohub API URL override"),
    ] = None,
    yes_live: Annotated[
        bool,
        typer.Option(
            "--yes-live",
            help="Actually call Biohub/ESMC if the embedding is missing.",
        ),
    ] = False,
    skip_existing: Annotated[
        bool,
        typer.Option(
            "--skip-existing/--no-skip-existing",
            help="Do not rewrite an existing embedding file.",
        ),
    ] = True,
) -> None:
    """Generate or dry-run exactly one primary curated ortholog embedding."""
    load_runtime_env()

    if not curated_orthologs.exists():
        raise FileNotFoundError(f"Missing curated ortholog input: {curated_orthologs}")

    cfg = PipelineConfig(output_dir=output_dir)
    resolved_model_name = model_name or cfg.esmc_model
    resolved_api_url = biohub_api_url or cfg.biohub_api_url

    candidates = pl.read_csv(curated_orthologs)
    plan = build_single_curated_embedding_plan(
        candidates,
        output_dir=output_dir,
        model_name=resolved_model_name,
        complex_id=complex_id,
        chain=chain,
        target_species_taxid=target_species_taxid,
    )

    typer.echo("Single curated embedding plan:")
    _echo_plan(plan)

    if not yes_live:
        typer.echo("mode: dry-run; add --yes-live to call Biohub/ESMC")
    else:
        typer.echo("mode: live")

    result = run_single_curated_embedding(
        plan,
        output_dir=output_dir,
        api_url=resolved_api_url,
        yes_live=yes_live,
        skip_existing=skip_existing,
    )

    typer.echo(f"status: {result.status}")
    if result.embedding_shape is not None:
        typer.echo(f"embedding_shape: {result.embedding_shape}")


if __name__ == "__main__":
    app()
