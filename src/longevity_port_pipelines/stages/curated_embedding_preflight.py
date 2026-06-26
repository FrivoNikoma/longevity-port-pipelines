from __future__ import annotations

from pathlib import Path

import polars as pl
import typer

from longevity_port_pipelines.stages.ortholog_inputs import (
    filter_primary_curated_ortholog_candidates,
    validate_schema,
)

DEFAULT_MODEL_NAME = "esmc-300m-2024-12"
DEFAULT_CURATED_ORTHOLOGS = Path("data/input/curated_ortholog_candidates.csv")
DEFAULT_OUTPUT_DIR = Path("data/output")
DEFAULT_PREFLIGHT_OUTPUT = Path("data/output/curated_ortholog_embedding_preflight.csv")

PREFLIGHT_SCHEMA = {
    "complex_id": pl.Utf8,
    "chain": pl.Utf8,
    "target_species": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "source_species_taxid": pl.Int64,
    "target_species_taxid": pl.Int64,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_sequence_length": pl.Int64,
    "actual_sequence_length": pl.Int64,
    "sequence_length_status": pl.Utf8,
    "model_name": pl.Utf8,
    "embedding_path": pl.Utf8,
    "embedding_exists": pl.Boolean,
    "embedding_status": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def canonical_embedding_path(
    output_dir: Path,
    model_name: str,
    complex_id: str,
    chain: str,
    species_taxid: int,
) -> Path:
    """Return the canonical saved embedding path without running ESMC."""
    return output_dir / "embeddings" / model_name / f"{complex_id}_{chain}_{species_taxid}.npy"


def empty_curated_ortholog_embedding_preflight() -> pl.DataFrame:
    return pl.DataFrame(schema=PREFLIGHT_SCHEMA)


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


def build_curated_ortholog_embedding_preflight(
    candidates: pl.DataFrame,
    *,
    output_dir: Path,
    model_name: str,
) -> pl.DataFrame:
    """Check whether primary curated ortholog embeddings already exist on disk.

    This is a dry preflight only. It does not call Biohub, does not generate embeddings,
    and does not modify ortholog coverage.
    """
    validate_schema(candidates)

    primary_candidates = filter_primary_curated_ortholog_candidates(candidates)
    if primary_candidates.is_empty():
        return empty_curated_ortholog_embedding_preflight()

    rows: list[dict[str, object]] = []
    for row in primary_candidates.iter_rows(named=True):
        complex_id = _as_str(row, "complex_id")
        chain = _as_str(row, "chain")
        target_species_taxid = _as_int(row, "target_species_taxid")
        target_sequence = _as_str(row, "target_sequence")
        target_sequence_length = _as_int(row, "target_sequence_length")
        actual_sequence_length = len(target_sequence)

        path = canonical_embedding_path(
            output_dir=output_dir,
            model_name=model_name,
            complex_id=complex_id,
            chain=chain,
            species_taxid=target_species_taxid,
        )
        embedding_exists = path.exists()

        rows.append(
            {
                "complex_id": complex_id,
                "chain": chain,
                "target_species": _as_str(row, "target_species"),
                "source_uniprot": _as_str(row, "source_uniprot"),
                "source_species_taxid": _as_int(row, "source_species_taxid"),
                "target_species_taxid": target_species_taxid,
                "target_accession": _as_str(row, "target_accession"),
                "target_accession_db": _as_str(row, "target_accession_db"),
                "target_sequence_length": target_sequence_length,
                "actual_sequence_length": actual_sequence_length,
                "sequence_length_status": (
                    "matches" if target_sequence_length == actual_sequence_length else "mismatch"
                ),
                "model_name": model_name,
                "embedding_path": str(path),
                "embedding_exists": embedding_exists,
                "embedding_status": "present" if embedding_exists else "missing",
            }
        )

    return (
        pl.DataFrame(rows)
        .select(list(PREFLIGHT_SCHEMA))
        .sort(["embedding_status", "complex_id", "chain", "target_species_taxid"])
    )


def embedding_status_counts(preflight: pl.DataFrame) -> dict[str, int]:
    if preflight.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in preflight.group_by("embedding_status").len().iter_rows(named=True):
        counts[_as_str(row, "embedding_status")] = _as_int(row, "len")
    return counts


@app.command()
def main(
    curated_orthologs: Path = DEFAULT_CURATED_ORTHOLOGS,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    model_name: str = DEFAULT_MODEL_NAME,
    output: Path = DEFAULT_PREFLIGHT_OUTPUT,
) -> None:
    """Dry-run curated ortholog embedding availability without Biohub calls."""
    if not curated_orthologs.exists():
        raise FileNotFoundError(f"Missing curated ortholog input: {curated_orthologs}")

    candidates = pl.read_csv(curated_orthologs)
    preflight = build_curated_ortholog_embedding_preflight(
        candidates,
        output_dir=output_dir,
        model_name=model_name,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    preflight.write_csv(output)

    typer.echo(f"primary curated candidates: {preflight.height}")
    for status, count in sorted(embedding_status_counts(preflight).items()):
        typer.echo(f"{status} embeddings: {count}")

    missing = preflight.filter(pl.col("embedding_status") == "missing")
    if missing.height > 0:
        typer.echo("Missing curated embeddings:")
        for row in missing.iter_rows(named=True):
            typer.echo(
                "  "
                f"{row['complex_id']} "
                f"{row['chain']} "
                f"taxid={row['target_species_taxid']} "
                f"path={row['embedding_path']}"
            )

    typer.echo(f"Wrote curated embedding preflight -> {output}")


if __name__ == "__main__":
    app()
