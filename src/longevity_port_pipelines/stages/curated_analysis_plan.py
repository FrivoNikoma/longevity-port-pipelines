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
DEFAULT_SELECTION = Path("data/output/selection.csv")
DEFAULT_OUTPUT_DIR = Path("data/output")
DEFAULT_PLAN_OUTPUT = Path("data/output/curated_ortholog_analysis_plan.csv")

PREFLIGHT_SCHEMA = {
    "complex_id": pl.Utf8,
    "chain": pl.Utf8,
    "target_species": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "target_accession": pl.Utf8,
    "model_name": pl.Utf8,
    "selection_match_count": pl.Int64,
    "selection_id_column": pl.Utf8,
    "pdb_id": pl.Utf8,
    "pdb_chain_R": pl.Utf8,
    "pdb_chain_L": pl.Utf8,
    "chain_sequence_column": pl.Utf8,
    "chain_uniprot_column": pl.Utf8,
    "selection_source_uniprot": pl.Utf8,
    "reference_sequence_length": pl.Int64,
    "target_sequence_length": pl.Int64,
    "reference_embedding_path": pl.Utf8,
    "reference_embedding_exists": pl.Boolean,
    "target_embedding_path": pl.Utf8,
    "target_embedding_exists": pl.Boolean,
    "interface_residue_source": pl.Utf8,
    "interface_residue_status": pl.Utf8,
    "analysis_plan_ready": pl.Boolean,
    "blocking_reason": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def empty_curated_ortholog_analysis_plan() -> pl.DataFrame:
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


def _optional_str(row: dict[str, object] | None, column: str) -> str | None:
    if row is None or column not in row:
        return None
    value = row[column]
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _id_column(selection: pl.DataFrame) -> str:
    for column in selection.columns:
        if column.lower() in ("id", "pinder_id", "system_id"):
            return column
    return selection.columns[0]


def _sequence_column(selection: pl.DataFrame, chain: str) -> str | None:
    if chain == "receptor":
        candidates = ("receptor_sequence", "sequence_R", "sequence_r")
    elif chain == "ligand":
        candidates = ("ligand_sequence", "sequence_L", "sequence_l")
    else:
        raise ValueError(f"Unsupported chain role: {chain!r}")

    for column in candidates:
        if column in selection.columns:
            return column
    return None


def _uniprot_column(chain: str) -> str:
    if chain == "receptor":
        return "uniprot_R"
    if chain == "ligand":
        return "uniprot_L"
    raise ValueError(f"Unsupported chain role: {chain!r}")


def _first_row_or_none(df: pl.DataFrame) -> dict[str, object] | None:
    if df.is_empty():
        return None
    return df.row(0, named=True)


def _has_interface_metadata(selection_row: dict[str, object] | None) -> bool:
    if selection_row is None:
        return False
    return all(_optional_str(selection_row, column) for column in ("pdb_id", "chain_R", "chain_L"))


def build_curated_ortholog_analysis_plan(
    candidates: pl.DataFrame,
    selection: pl.DataFrame,
    *,
    output_dir: Path,
    model_name: str,
) -> pl.DataFrame:
    """Build a dry analysis plan for primary curated ortholog candidates.

    This command does not call Biohub/ESMC, does not call Boltz, does not
    extract interface residues, and does not run enrichment analysis.
    """
    validate_schema(candidates)

    primary_candidates = filter_primary_curated_ortholog_candidates(candidates)
    if primary_candidates.is_empty():
        return empty_curated_ortholog_analysis_plan()

    selection_id_column = _id_column(selection)

    rows: list[dict[str, object]] = []
    for row in primary_candidates.iter_rows(named=True):
        complex_id = _as_str(row, "complex_id")
        chain = _as_str(row, "chain")
        target_species = _as_str(row, "target_species")
        source_uniprot = _as_str(row, "source_uniprot")
        source_species_taxid = _as_int(row, "source_species_taxid")
        target_species_taxid = _as_int(row, "target_species_taxid")
        target_accession = _as_str(row, "target_accession")
        target_sequence_length = _as_int(row, "target_sequence_length")

        selection_matches = selection.filter(pl.col(selection_id_column) == complex_id)
        selection_row = _first_row_or_none(selection_matches)

        seq_col = _sequence_column(selection, chain)
        up_col = _uniprot_column(chain)

        reference_sequence = (
            _optional_str(selection_row, seq_col)
            if selection_row is not None and seq_col is not None
            else None
        )
        selection_source_uniprot = (
            _optional_str(selection_row, up_col)
            if selection_row is not None and up_col in selection.columns
            else None
        )

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

        interface_metadata_present = _has_interface_metadata(selection_row)

        blocking_reasons: list[str] = []
        if selection_matches.is_empty():
            blocking_reasons.append("selection_missing")
        elif selection_matches.height > 1:
            blocking_reasons.append("selection_ambiguous")

        if seq_col is None:
            blocking_reasons.append("sequence_column_missing")
        elif reference_sequence is None:
            blocking_reasons.append("reference_sequence_missing")

        if up_col not in selection.columns:
            blocking_reasons.append("uniprot_column_missing")
        elif selection_source_uniprot != source_uniprot:
            blocking_reasons.append("selection_source_uniprot_mismatch")

        if not ref_path.exists():
            blocking_reasons.append("reference_embedding_missing")
        if not target_path.exists():
            blocking_reasons.append("target_embedding_missing")

        if not interface_metadata_present:
            blocking_reasons.append("interface_metadata_missing")

        analysis_plan_ready = not blocking_reasons

        rows.append(
            {
                "complex_id": complex_id,
                "chain": chain,
                "target_species": target_species,
                "source_uniprot": source_uniprot,
                "target_species_taxid": target_species_taxid,
                "target_accession": target_accession,
                "model_name": model_name,
                "selection_match_count": selection_matches.height,
                "selection_id_column": selection_id_column,
                "pdb_id": _optional_str(selection_row, "pdb_id"),
                "pdb_chain_R": _optional_str(selection_row, "chain_R"),
                "pdb_chain_L": _optional_str(selection_row, "chain_L"),
                "chain_sequence_column": seq_col,
                "chain_uniprot_column": up_col,
                "selection_source_uniprot": selection_source_uniprot,
                "reference_sequence_length": len(reference_sequence) if reference_sequence else 0,
                "target_sequence_length": target_sequence_length,
                "reference_embedding_path": str(ref_path),
                "reference_embedding_exists": ref_path.exists(),
                "target_embedding_path": str(target_path),
                "target_embedding_exists": target_path.exists(),
                "interface_residue_source": "pdb_interface_extraction",
                "interface_residue_status": (
                    "metadata_present" if interface_metadata_present else "metadata_missing"
                ),
                "analysis_plan_ready": analysis_plan_ready,
                "blocking_reason": "ready" if analysis_plan_ready else ";".join(blocking_reasons),
            }
        )

    return (
        pl.DataFrame(rows)
        .select(list(PREFLIGHT_SCHEMA))
        .sort(["analysis_plan_ready", "complex_id", "chain"], descending=True)
    )


@app.command()
def main(
    curated_orthologs: Path = DEFAULT_CURATED_ORTHOLOGS,
    selection: Path = DEFAULT_SELECTION,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    model_name: str = DEFAULT_MODEL_NAME,
    output: Path = DEFAULT_PLAN_OUTPUT,
) -> None:
    """Dry-run curated ortholog analysis plan without enrichment."""
    if not curated_orthologs.exists():
        raise FileNotFoundError(f"Missing curated ortholog input: {curated_orthologs}")
    if not selection.exists():
        raise FileNotFoundError(f"Missing selection file: {selection}")

    candidates = pl.read_csv(curated_orthologs)
    selection_df = pl.read_csv(selection)

    plan = build_curated_ortholog_analysis_plan(
        candidates,
        selection_df,
        output_dir=output_dir,
        model_name=model_name,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    plan.write_csv(output)

    ready = plan.filter(pl.col("analysis_plan_ready")).height
    blocked = plan.filter(~pl.col("analysis_plan_ready")).height

    typer.echo(f"primary curated candidates: {plan.height}")
    typer.echo(f"ready analysis plans: {ready}")
    typer.echo(f"blocked analysis plans: {blocked}")

    if blocked:
        typer.echo("Blocked curated analysis plans:")
        for row in plan.filter(~pl.col("analysis_plan_ready")).iter_rows(named=True):
            typer.echo(
                "  "
                f"{row['complex_id']} "
                f"{row['chain']} "
                f"taxid={row['target_species_taxid']} "
                f"reason={row['blocking_reason']}"
            )

    typer.echo(f"Wrote curated analysis plan -> {output}")


if __name__ == "__main__":
    app()
