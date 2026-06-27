from __future__ import annotations

from pathlib import Path

import polars as pl
import typer

from longevity_port_pipelines.stages.curated_analysis_plan import (
    DEFAULT_CURATED_ORTHOLOGS,
    DEFAULT_MODEL_NAME,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SELECTION,
    build_curated_ortholog_analysis_plan,
)
from longevity_port_pipelines.stages.embed import load_saved_embedding
from longevity_port_pipelines.stages.interface import download_pdb, extract_interface_residues
from longevity_port_pipelines.stages.ortholog_inputs import (
    filter_primary_curated_ortholog_candidates,
    validate_schema,
)

DEFAULT_PDB_DIR = Path("data/interim/pdb")
DEFAULT_RUNNER_OUTPUT = Path("data/output/curated_ortholog_analysis_runner.csv")

RUNNER_SCHEMA = {
    "complex_id": pl.Utf8,
    "chain": pl.Utf8,
    "target_species": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "target_accession": pl.Utf8,
    "model_name": pl.Utf8,
    "run_mode": pl.Utf8,
    "analysis_plan_ready": pl.Boolean,
    "reference_embedding_loaded": pl.Boolean,
    "target_embedding_loaded": pl.Boolean,
    "reference_embedding_shape": pl.Utf8,
    "target_embedding_shape": pl.Utf8,
    "pdb_id": pl.Utf8,
    "pdb_chain_R": pl.Utf8,
    "pdb_chain_L": pl.Utf8,
    "interface_residue_count": pl.Int64,
    "interface_residue_status": pl.Utf8,
    "status": pl.Utf8,
    "blocking_reason": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def empty_curated_ortholog_analysis_runner_report() -> pl.DataFrame:
    return pl.DataFrame(schema=RUNNER_SCHEMA)


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


def _as_bool(row: dict[str, object], column: str) -> bool:
    value = row[column]
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def _optional_str(row: dict[str, object], column: str) -> str | None:
    value = row.get(column)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _single_primary_candidate(
    candidates: pl.DataFrame,
    *,
    complex_id: str,
    chain: str,
    target_species_taxid: int,
) -> dict[str, object]:
    validate_schema(candidates)

    matches = filter_primary_curated_ortholog_candidates(candidates).filter(
        (pl.col("complex_id") == complex_id)
        & (pl.col("chain") == chain)
        & (pl.col("target_species_taxid") == target_species_taxid)
    )

    if matches.height == 0:
        raise ValueError(
            "No primary curated candidate found for "
            f"complex_id={complex_id!r}, chain={chain!r}, "
            f"target_species_taxid={target_species_taxid}"
        )

    if matches.height > 1:
        raise ValueError(
            "Multiple primary curated candidates found for "
            f"complex_id={complex_id!r}, chain={chain!r}, "
            f"target_species_taxid={target_species_taxid}"
        )

    return matches.row(0, named=True)


def _single_selection_row(
    selection: pl.DataFrame,
    *,
    selection_id_column: str,
    complex_id: str,
) -> dict[str, object]:
    matches = selection.filter(pl.col(selection_id_column) == complex_id)

    if matches.height == 0:
        raise ValueError(f"No selection row found for complex_id={complex_id!r}")

    if matches.height > 1:
        raise ValueError(f"Multiple selection rows found for complex_id={complex_id!r}")

    return matches.row(0, named=True)


def _selected_interface_residues(
    *,
    chain: str,
    receptor_interface: list[int],
    ligand_interface: list[int],
) -> list[int]:
    if chain == "receptor":
        return receptor_interface
    if chain == "ligand":
        return ligand_interface
    raise ValueError(f"Unsupported chain role: {chain!r}")


def _shape_text(shape: tuple[int, ...]) -> str:
    return "x".join(str(part) for part in shape)


def _runner_status_counts(report: pl.DataFrame) -> dict[str, int]:
    if report.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in report.group_by("status").len().iter_rows(named=True):
        counts[_as_str(row, "status")] = _as_int(row, "len")
    return counts


def run_curated_ortholog_analysis_runner(
    candidates: pl.DataFrame,
    selection: pl.DataFrame,
    *,
    output_dir: Path,
    pdb_dir: Path,
    model_name: str,
    yes_run: bool,
    interface_distance_cutoff: float = 8.0,
) -> pl.DataFrame:
    """Dry-run or minimally prepare curated candidates for analysis.

    Dry-run mode only reports whether the analysis plan is ready.

    yes-run mode loads already-saved reference/target embeddings and extracts
    interface residues. It does not call Biohub/ESMC, does not call Boltz, does
    not generate embeddings, and does not run enrichment analysis.
    """
    plan = build_curated_ortholog_analysis_plan(
        candidates,
        selection,
        output_dir=output_dir,
        model_name=model_name,
    )

    if plan.is_empty():
        return empty_curated_ortholog_analysis_runner_report()

    rows: list[dict[str, object]] = []
    for plan_row in plan.iter_rows(named=True):
        complex_id = _as_str(plan_row, "complex_id")
        chain = _as_str(plan_row, "chain")
        target_species_taxid = _as_int(plan_row, "target_species_taxid")
        analysis_plan_ready = _as_bool(plan_row, "analysis_plan_ready")

        base_row: dict[str, object] = {
            "complex_id": complex_id,
            "chain": chain,
            "target_species": _as_str(plan_row, "target_species"),
            "source_uniprot": _as_str(plan_row, "source_uniprot"),
            "target_species_taxid": target_species_taxid,
            "target_accession": _as_str(plan_row, "target_accession"),
            "model_name": model_name,
            "run_mode": "yes-run" if yes_run else "dry-run",
            "analysis_plan_ready": analysis_plan_ready,
            "reference_embedding_loaded": False,
            "target_embedding_loaded": False,
            "reference_embedding_shape": None,
            "target_embedding_shape": None,
            "pdb_id": _optional_str(plan_row, "pdb_id"),
            "pdb_chain_R": _optional_str(plan_row, "pdb_chain_R"),
            "pdb_chain_L": _optional_str(plan_row, "pdb_chain_L"),
            "interface_residue_count": 0,
            "interface_residue_status": _as_str(plan_row, "interface_residue_status"),
            "status": "dry_run_ready" if analysis_plan_ready else "blocked_plan",
            "blocking_reason": (
                "ready" if analysis_plan_ready else _as_str(plan_row, "blocking_reason")
            ),
        }

        if not analysis_plan_ready or not yes_run:
            rows.append(base_row)
            continue

        candidate_row = _single_primary_candidate(
            candidates,
            complex_id=complex_id,
            chain=chain,
            target_species_taxid=target_species_taxid,
        )
        selection_row = _single_selection_row(
            selection,
            selection_id_column=_as_str(plan_row, "selection_id_column"),
            complex_id=complex_id,
        )

        source_species_taxid = _as_int(candidate_row, "source_species_taxid")
        target_sequence = _as_str(candidate_row, "target_sequence")
        reference_sequence = _as_str(selection_row, _as_str(plan_row, "chain_sequence_column"))

        ref_embedding = load_saved_embedding(
            output_dir=output_dir,
            model_name=model_name,
            complex_id=complex_id,
            chain=chain,
            species_taxid=source_species_taxid,
            sequence=reference_sequence,
        )
        target_embedding = load_saved_embedding(
            output_dir=output_dir,
            model_name=model_name,
            complex_id=complex_id,
            chain=chain,
            species_taxid=target_species_taxid,
            sequence=target_sequence,
            is_predicted_structure=True,
        )

        pdb_id = _as_str(selection_row, "pdb_id")
        chain_r = _as_str(selection_row, "chain_R")
        chain_l = _as_str(selection_row, "chain_L")
        pdb_path = download_pdb(pdb_id, pdb_dir)
        receptor_interface, ligand_interface = extract_interface_residues(
            pdb_path,
            chain_r,
            chain_l,
            interface_distance_cutoff,
        )
        selected_interface = _selected_interface_residues(
            chain=chain,
            receptor_interface=receptor_interface,
            ligand_interface=ligand_interface,
        )

        interface_status = "present" if selected_interface else "empty"
        status = "run_ready" if selected_interface else "blocked_empty_interface"

        rows.append(
            {
                **base_row,
                "reference_embedding_loaded": True,
                "target_embedding_loaded": True,
                "reference_embedding_shape": _shape_text(ref_embedding.embeddings.shape),
                "target_embedding_shape": _shape_text(target_embedding.embeddings.shape),
                "interface_residue_count": len(selected_interface),
                "interface_residue_status": interface_status,
                "status": status,
                "blocking_reason": "ready" if selected_interface else "interface_residues_empty",
            }
        )

    return (
        pl.DataFrame(rows)
        .select(list(RUNNER_SCHEMA))
        .sort(["status", "complex_id", "chain", "target_species_taxid"])
    )


@app.command()
def main(
    curated_orthologs: Path = DEFAULT_CURATED_ORTHOLOGS,
    selection: Path = DEFAULT_SELECTION,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    pdb_dir: Path = DEFAULT_PDB_DIR,
    model_name: str = DEFAULT_MODEL_NAME,
    output: Path = DEFAULT_RUNNER_OUTPUT,
    yes_run: bool = typer.Option(
        False,
        "--yes-run",
        help="Load saved embeddings and extract interface residues.",
    ),
    interface_distance_cutoff: float = 8.0,
) -> None:
    """Dry-run or minimally prepare curated ortholog analysis inputs."""
    if not curated_orthologs.exists():
        raise FileNotFoundError(f"Missing curated ortholog input: {curated_orthologs}")
    if not selection.exists():
        raise FileNotFoundError(f"Missing selection file: {selection}")

    candidates = pl.read_csv(curated_orthologs)
    selection_df = pl.read_csv(selection)

    report = run_curated_ortholog_analysis_runner(
        candidates,
        selection_df,
        output_dir=output_dir,
        pdb_dir=pdb_dir,
        model_name=model_name,
        yes_run=yes_run,
        interface_distance_cutoff=interface_distance_cutoff,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    report.write_csv(output)

    typer.echo(f"primary curated candidates: {report.height}")
    typer.echo(f"mode: {'yes-run' if yes_run else 'dry-run'}")
    for status, count in sorted(_runner_status_counts(report).items()):
        typer.echo(f"{status}: {count}")

    blocked = report.filter(pl.col("status").str.starts_with("blocked"))
    if blocked.height > 0:
        typer.echo("Blocked curated analysis runner rows:")
        for row in blocked.iter_rows(named=True):
            typer.echo(
                "  "
                f"{row['complex_id']} "
                f"{row['chain']} "
                f"taxid={row['target_species_taxid']} "
                f"reason={row['blocking_reason']}"
            )

    typer.echo(f"Wrote curated analysis runner report -> {output}")


if __name__ == "__main__":
    app()
