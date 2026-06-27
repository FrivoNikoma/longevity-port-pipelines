from __future__ import annotations

from pathlib import Path

import polars as pl
import typer

from longevity_port_pipelines.stages.embed import embedding_path
from longevity_port_pipelines.stages.ortholog_inputs import (
    filter_primary_curated_ortholog_candidates,
    validate_schema,
)

DEFAULT_MODEL_NAME = "esmc-300m-2024-12"
DEFAULT_CURATED_ORTHOLOGS = Path("data/input/curated_ortholog_candidates.csv")
DEFAULT_MERGED_COVERAGE = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage_with_curated.csv"
)
DEFAULT_OUTPUT_DIR = Path("data/output")
DEFAULT_PREFLIGHT_OUTPUT = Path("data/output/curated_ortholog_analysis_preflight.csv")

REQUIRED_COVERAGE_COLUMNS = {
    "source_uniprot",
    "source_species_taxid",
    "target_uniprot",
    "target_species_taxid",
    "target_sequence",
    "is_reviewed",
    "source_db",
}

PREFLIGHT_SCHEMA = {
    "complex_id": pl.Utf8,
    "chain": pl.Utf8,
    "target_species": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "source_species_taxid": pl.Int64,
    "target_species_taxid": pl.Int64,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "model_name": pl.Utf8,
    "coverage_match_count": pl.Int64,
    "coverage_accession_match_count": pl.Int64,
    "coverage_target_uniprot": pl.Utf8,
    "coverage_source_db": pl.Utf8,
    "reference_embedding_path": pl.Utf8,
    "reference_embedding_exists": pl.Boolean,
    "target_embedding_path": pl.Utf8,
    "target_embedding_exists": pl.Boolean,
    "analysis_ready": pl.Boolean,
    "blocking_reason": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def empty_curated_ortholog_analysis_preflight() -> pl.DataFrame:
    return pl.DataFrame(schema=PREFLIGHT_SCHEMA)


def validate_coverage_schema(coverage: pl.DataFrame) -> None:
    missing = sorted(REQUIRED_COVERAGE_COLUMNS.difference(coverage.columns))
    if missing:
        raise ValueError(f"Missing required merged coverage columns: {missing}")


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


def _optional_str(row: dict[str, object] | None, column: str) -> str | None:
    if row is None or column not in row:
        return None
    value = row[column]
    if value is None:
        return None
    return str(value).strip()


def _first_row_or_none(df: pl.DataFrame) -> dict[str, object] | None:
    if df.is_empty():
        return None
    return df.row(0, named=True)


def build_curated_ortholog_analysis_preflight(
    candidates: pl.DataFrame,
    coverage: pl.DataFrame,
    *,
    output_dir: Path,
    model_name: str,
) -> pl.DataFrame:
    """Check whether curated ortholog candidates are ready for analysis.

    This is a dry preflight only. It does not call Biohub/ESMC, does not call
    Boltz, does not generate embeddings, and does not run enrichment analysis.
    """
    validate_schema(candidates)
    validate_coverage_schema(coverage)

    primary_candidates = filter_primary_curated_ortholog_candidates(candidates)
    if primary_candidates.is_empty():
        return empty_curated_ortholog_analysis_preflight()

    rows: list[dict[str, object]] = []
    for row in primary_candidates.iter_rows(named=True):
        complex_id = _as_str(row, "complex_id")
        chain = _as_str(row, "chain")
        target_species = _as_str(row, "target_species")
        source_uniprot = _as_str(row, "source_uniprot")
        source_species_taxid = _as_int(row, "source_species_taxid")
        target_species_taxid = _as_int(row, "target_species_taxid")
        target_accession = _as_str(row, "target_accession")
        target_accession_db = _as_str(row, "target_accession_db")

        coverage_matches = coverage.filter(
            (pl.col("source_uniprot") == source_uniprot)
            & (pl.col("source_species_taxid") == source_species_taxid)
            & (pl.col("target_species_taxid") == target_species_taxid)
        )
        accession_matches = coverage_matches.filter(pl.col("target_uniprot") == target_accession)
        selected_coverage = _first_row_or_none(accession_matches)

        ref_path = embedding_path(
            output_dir=output_dir,
            model_name=model_name,
            complex_id=complex_id,
            chain=chain,
            species_taxid=source_species_taxid,
        )
        target_path = embedding_path(
            output_dir=output_dir,
            model_name=model_name,
            complex_id=complex_id,
            chain=chain,
            species_taxid=target_species_taxid,
        )

        blocking_reasons: list[str] = []
        if coverage_matches.is_empty():
            blocking_reasons.append("coverage_missing")
        elif accession_matches.is_empty():
            blocking_reasons.append("coverage_accession_mismatch")

        if not ref_path.exists():
            blocking_reasons.append("reference_embedding_missing")
        if not target_path.exists():
            blocking_reasons.append("target_embedding_missing")

        analysis_ready = not blocking_reasons

        rows.append(
            {
                "complex_id": complex_id,
                "chain": chain,
                "target_species": target_species,
                "source_uniprot": source_uniprot,
                "source_species_taxid": source_species_taxid,
                "target_species_taxid": target_species_taxid,
                "target_accession": target_accession,
                "target_accession_db": target_accession_db,
                "model_name": model_name,
                "coverage_match_count": coverage_matches.height,
                "coverage_accession_match_count": accession_matches.height,
                "coverage_target_uniprot": _optional_str(selected_coverage, "target_uniprot"),
                "coverage_source_db": _optional_str(selected_coverage, "source_db"),
                "reference_embedding_path": str(ref_path),
                "reference_embedding_exists": ref_path.exists(),
                "target_embedding_path": str(target_path),
                "target_embedding_exists": target_path.exists(),
                "analysis_ready": analysis_ready,
                "blocking_reason": "ready" if analysis_ready else ";".join(blocking_reasons),
            }
        )

    return (
        pl.DataFrame(rows)
        .select(list(PREFLIGHT_SCHEMA))
        .sort(["analysis_ready", "complex_id", "chain", "target_species_taxid"], descending=True)
    )


@app.command()
def main(
    curated_orthologs: Path = DEFAULT_CURATED_ORTHOLOGS,
    merged_coverage: Path = DEFAULT_MERGED_COVERAGE,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    model_name: str = DEFAULT_MODEL_NAME,
    output: Path = DEFAULT_PREFLIGHT_OUTPUT,
) -> None:
    """Dry-run curated ortholog readiness for the next analysis layer."""
    if not curated_orthologs.exists():
        raise FileNotFoundError(f"Missing curated ortholog input: {curated_orthologs}")
    if not merged_coverage.exists():
        raise FileNotFoundError(f"Missing merged curated coverage: {merged_coverage}")

    candidates = pl.read_csv(curated_orthologs)
    coverage = pl.read_csv(merged_coverage)

    preflight = build_curated_ortholog_analysis_preflight(
        candidates,
        coverage,
        output_dir=output_dir,
        model_name=model_name,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    preflight.write_csv(output)

    ready = preflight.filter(pl.col("analysis_ready")).height
    blocked = preflight.filter(~pl.col("analysis_ready")).height

    typer.echo(f"primary curated candidates: {preflight.height}")
    typer.echo(f"ready for analysis: {ready}")
    typer.echo(f"blocked for analysis: {blocked}")

    if blocked:
        typer.echo("Blocked curated candidates:")
        for row in preflight.filter(~pl.col("analysis_ready")).iter_rows(named=True):
            typer.echo(
                "  "
                f"{row['complex_id']} "
                f"{row['chain']} "
                f"taxid={row['target_species_taxid']} "
                f"reason={row['blocking_reason']}"
            )

    typer.echo(f"Wrote curated analysis preflight -> {output}")


if __name__ == "__main__":
    app()
