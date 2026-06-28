from __future__ import annotations

from pathlib import Path

import polars as pl
import typer

from longevity_port_pipelines.config import REFERENCE_SPECIES
from longevity_port_pipelines.models import EnrichmentResult
from longevity_port_pipelines.stages.analyze import analyze_pair
from longevity_port_pipelines.stages.curated_analysis_plan import (
    DEFAULT_CURATED_ORTHOLOGS,
    DEFAULT_MODEL_NAME,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SELECTION,
    build_curated_ortholog_analysis_plan,
)
from longevity_port_pipelines.stages.embed import load_saved_embedding
from longevity_port_pipelines.stages.interface import download_pdb, extract_interface_residues
from longevity_port_pipelines.stages.negative_controls import (
    control_evidence_tier,
    passes_controls,
)
from longevity_port_pipelines.stages.negatome_controls import (
    build_negatome_pair_lookup,
    load_negatome_control_pairs,
    negatome_lookup_key,
    resolve_negatome_control_ratio,
)
from longevity_port_pipelines.stages.ortholog_inputs import (
    filter_primary_curated_ortholog_candidates,
    validate_schema,
)

DEFAULT_INTERIM_DIR = Path("data/interim")
DEFAULT_PDB_DIR = DEFAULT_INTERIM_DIR / "pdb"
DEFAULT_NEGATOME_CONTROL_PAIRS = DEFAULT_INTERIM_DIR / "negatome_control_pairs.csv"
DEFAULT_ENRICHMENT_OUTPUT = Path("data/output/curated_ortholog_enrichment.csv")

ENRICHMENT_SCHEMA = {
    "complex_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "target_species": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "target_accession": pl.Utf8,
    "model_name": pl.Utf8,
    "run_mode": pl.Utf8,
    "analysis_plan_ready": pl.Boolean,
    "status": pl.Utf8,
    "blocking_reason": pl.Utf8,
    "control_status": pl.Utf8,
    "interpretation_status": pl.Utf8,
    "interface_residue_count": pl.Int64,
    "reference_embedding_shape": pl.Utf8,
    "target_embedding_shape": pl.Utf8,
    "source_species": pl.Utf8,
    "is_predicted_structure": pl.Boolean,
    "interface_mean_delta": pl.Float64,
    "noninterface_mean_delta": pl.Float64,
    "enrichment_ratio": pl.Float64,
    "shuffled_control_ratio": pl.Float64,
    "negatome_control_ratio": pl.Float64,
    "mann_whitney_p": pl.Float64,
    "p_interface_greater": pl.Float64,
    "p_interface_less": pl.Float64,
    "p_two_sided": pl.Float64,
    "effect_size_cohens_d": pl.Float64,
}

app = typer.Typer(add_completion=False)


def empty_curated_ortholog_enrichment_report() -> pl.DataFrame:
    return pl.DataFrame(schema=ENRICHMENT_SCHEMA)


def _frame_from_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    if not rows:
        return empty_curated_ortholog_enrichment_report()

    return pl.DataFrame(rows).select(
        [pl.col(column).cast(dtype).alias(column) for column, dtype in ENRICHMENT_SCHEMA.items()]
    )


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


def _base_row(
    plan_row: dict[str, object],
    *,
    model_name: str,
    yes_run: bool,
    status: str,
    blocking_reason: str,
) -> dict[str, object]:
    return {
        "complex_id": _as_str(plan_row, "complex_id"),
        "chain": _as_str(plan_row, "chain"),
        "source_uniprot": _as_str(plan_row, "source_uniprot"),
        "target_species": _as_str(plan_row, "target_species"),
        "target_species_taxid": _as_int(plan_row, "target_species_taxid"),
        "target_accession": _as_str(plan_row, "target_accession"),
        "model_name": model_name,
        "run_mode": "yes-run" if yes_run else "dry-run",
        "analysis_plan_ready": _as_bool(plan_row, "analysis_plan_ready"),
        "status": status,
        "blocking_reason": blocking_reason,
        "control_status": "not_run",
        "interpretation_status": "not_computed",
        "interface_residue_count": 0,
        "reference_embedding_shape": None,
        "target_embedding_shape": None,
        "source_species": REFERENCE_SPECIES.name,
        "is_predicted_structure": True,
        "interface_mean_delta": None,
        "noninterface_mean_delta": None,
        "enrichment_ratio": None,
        "shuffled_control_ratio": None,
        "negatome_control_ratio": None,
        "mann_whitney_p": None,
        "p_interface_greater": None,
        "p_interface_less": None,
        "p_two_sided": None,
        "effect_size_cohens_d": None,
    }


def _control_status(negatome_control_ratio: float | None) -> str:
    if negatome_control_ratio is not None and negatome_control_ratio > 0.0:
        return "has_shuffled_and_negatome"
    return "missing_negatome"


def _interpretation_status(result: EnrichmentResult, control_status: str) -> str:
    passes = passes_controls(
        enrichment_ratio=result.enrichment_ratio,
        shuffled_control_ratio=result.shuffled_control_ratio,
        negatome_control_ratio=result.negatome_control_ratio,
        p_interface_greater=result.p_interface_greater,
        p_interface_less=result.p_interface_less,
        control_status=control_status,
    )
    return control_evidence_tier(control_status=control_status, passes=passes)


def _status_counts(report: pl.DataFrame) -> dict[str, int]:
    if report.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in report.group_by("status").len().iter_rows(named=True):
        counts[_as_str(row, "status")] = _as_int(row, "len")
    return counts


def run_curated_ortholog_enrichment(
    candidates: pl.DataFrame,
    selection: pl.DataFrame,
    *,
    output_dir: Path,
    pdb_dir: Path,
    model_name: str,
    yes_run: bool,
    interim_dir: Path = DEFAULT_INTERIM_DIR,
    negatome_control_pairs: Path | None = DEFAULT_NEGATOME_CONTROL_PAIRS,
    interface_distance_cutoff: float = 8.0,
    n_permutations: int = 1000,
) -> pl.DataFrame:
    """Dry-run or compute a technical enrichment checkpoint for curated candidates.

    This runner never calls Biohub/ESMC, never calls Boltz, and never generates
    embeddings. In yes-run mode it loads already-saved embeddings, extracts
    interface residues, and calls analyze_pair.

    The resulting enrichment remains preliminary until NEGATOME control is
    populated and the strict control gate is evaluated.
    """
    plan = build_curated_ortholog_analysis_plan(
        candidates,
        selection,
        output_dir=output_dir,
        model_name=model_name,
    )

    if plan.is_empty():
        return empty_curated_ortholog_enrichment_report()

    negatome_pairs = (
        load_negatome_control_pairs(negatome_control_pairs)
        if negatome_control_pairs is not None
        else None
    )
    negatome_lookup = (
        build_negatome_pair_lookup(negatome_pairs) if negatome_pairs is not None else {}
    )

    rows: list[dict[str, object]] = []
    for plan_row in plan.iter_rows(named=True):
        complex_id = _as_str(plan_row, "complex_id")
        chain = _as_str(plan_row, "chain")
        target_species_taxid = _as_int(plan_row, "target_species_taxid")
        analysis_plan_ready = _as_bool(plan_row, "analysis_plan_ready")

        if not analysis_plan_ready:
            rows.append(
                _base_row(
                    plan_row,
                    model_name=model_name,
                    yes_run=yes_run,
                    status="blocked_plan",
                    blocking_reason=_as_str(plan_row, "blocking_reason"),
                )
            )
            continue

        if not yes_run:
            rows.append(
                _base_row(
                    plan_row,
                    model_name=model_name,
                    yes_run=False,
                    status="dry_run_ready",
                    blocking_reason="ready",
                )
            )
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

        pdb_path = download_pdb(_as_str(selection_row, "pdb_id"), pdb_dir)
        receptor_interface, ligand_interface = extract_interface_residues(
            pdb_path,
            _as_str(selection_row, "chain_R"),
            _as_str(selection_row, "chain_L"),
            interface_distance_cutoff,
        )
        selected_interface = _selected_interface_residues(
            chain=chain,
            receptor_interface=receptor_interface,
            ligand_interface=ligand_interface,
        )

        if not selected_interface:
            blocked_row = _base_row(
                plan_row,
                model_name=model_name,
                yes_run=True,
                status="blocked_empty_interface",
                blocking_reason="interface_residues_empty",
            )
            blocked_row.update(
                {
                    "reference_embedding_shape": _shape_text(ref_embedding.embeddings.shape),
                    "target_embedding_shape": _shape_text(target_embedding.embeddings.shape),
                    "control_status": "not_run",
                    "interpretation_status": "blocked",
                }
            )
            rows.append(blocked_row)
            continue

        target_species = _as_str(plan_row, "target_species")
        source_uniprot = _as_str(plan_row, "source_uniprot")
        negatome_control_ratio = resolve_negatome_control_ratio(
            ref=ref_embedding,
            orth=target_embedding,
            interface_residues=selected_interface,
            pair_rows=negatome_lookup.get(
                negatome_lookup_key(complex_id, chain, target_species),
                [],
            ),
            interim_dir=interim_dir,
            model_name=model_name,
            source_uniprot=source_uniprot,
        )

        result = analyze_pair(
            ref=ref_embedding,
            orth=target_embedding,
            interface_residues=selected_interface,
            source_species_name=REFERENCE_SPECIES.name,
            target_species_name=target_species,
            n_permutations=n_permutations,
            negatome_enrichment=negatome_control_ratio,
        )
        control_status = _control_status(result.negatome_control_ratio)
        interpretation_status = _interpretation_status(result, control_status)

        result_row = _base_row(
            plan_row,
            model_name=model_name,
            yes_run=True,
            status="enrichment_completed",
            blocking_reason="ready",
        )
        result_row.update(
            {
                "control_status": control_status,
                "interpretation_status": interpretation_status,
                "interface_residue_count": len(selected_interface),
                "reference_embedding_shape": _shape_text(ref_embedding.embeddings.shape),
                "target_embedding_shape": _shape_text(target_embedding.embeddings.shape),
                "source_species": result.source_species,
                "is_predicted_structure": result.is_predicted_structure,
                "interface_mean_delta": result.interface_mean_delta,
                "noninterface_mean_delta": result.noninterface_mean_delta,
                "enrichment_ratio": result.enrichment_ratio,
                "shuffled_control_ratio": result.shuffled_control_ratio,
                "negatome_control_ratio": result.negatome_control_ratio,
                "mann_whitney_p": result.mann_whitney_p,
                "p_interface_greater": result.p_interface_greater,
                "p_interface_less": result.p_interface_less,
                "p_two_sided": result.p_two_sided,
                "effect_size_cohens_d": result.effect_size_cohens_d,
            }
        )
        rows.append(result_row)

    return _frame_from_rows(rows).sort(["status", "complex_id", "chain", "target_species_taxid"])


@app.command()
def main(
    curated_orthologs: Path = DEFAULT_CURATED_ORTHOLOGS,
    selection: Path = DEFAULT_SELECTION,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    interim_dir: Path = DEFAULT_INTERIM_DIR,
    pdb_dir: Path = DEFAULT_PDB_DIR,
    negatome_control_pairs: Path = DEFAULT_NEGATOME_CONTROL_PAIRS,
    model_name: str = DEFAULT_MODEL_NAME,
    output: Path = DEFAULT_ENRICHMENT_OUTPUT,
    yes_run: bool = typer.Option(
        False,
        "--yes-run",
        help="Load saved embeddings, extract interfaces, and compute enrichment.",
    ),
    interface_distance_cutoff: float = 8.0,
    n_permutations: int = 1000,
) -> None:
    """Dry-run or compute curated ortholog technical enrichment."""
    if not curated_orthologs.exists():
        raise FileNotFoundError(f"Missing curated ortholog input: {curated_orthologs}")
    if not selection.exists():
        raise FileNotFoundError(f"Missing selection file: {selection}")

    candidates = pl.read_csv(curated_orthologs)
    selection_df = pl.read_csv(selection)

    report = run_curated_ortholog_enrichment(
        candidates,
        selection_df,
        output_dir=output_dir,
        pdb_dir=pdb_dir,
        model_name=model_name,
        yes_run=yes_run,
        interim_dir=interim_dir,
        negatome_control_pairs=negatome_control_pairs,
        interface_distance_cutoff=interface_distance_cutoff,
        n_permutations=n_permutations,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    report.write_csv(output)

    typer.echo(f"primary curated candidates: {report.height}")
    typer.echo(f"mode: {'yes-run' if yes_run else 'dry-run'}")
    for status, count in sorted(_status_counts(report).items()):
        typer.echo(f"{status}: {count}")

    completed = report.filter(pl.col("status") == "enrichment_completed")
    if completed.height > 0:
        for row in completed.iter_rows(named=True):
            typer.echo(
                "  "
                f"{row['complex_id']} "
                f"{row['chain']} "
                f"taxid={row['target_species_taxid']} "
                f"enrichment={row['enrichment_ratio']} "
                f"shuffled={row['shuffled_control_ratio']} "
                f"control_status={row['control_status']}"
            )

    blocked = report.filter(pl.col("status").str.starts_with("blocked"))
    if blocked.height > 0:
        typer.echo("Blocked curated enrichment rows:")
        for row in blocked.iter_rows(named=True):
            typer.echo(
                "  "
                f"{row['complex_id']} "
                f"{row['chain']} "
                f"taxid={row['target_species_taxid']} "
                f"reason={row['blocking_reason']}"
            )

    typer.echo(f"Wrote curated enrichment report -> {output}")


if __name__ == "__main__":
    app()
