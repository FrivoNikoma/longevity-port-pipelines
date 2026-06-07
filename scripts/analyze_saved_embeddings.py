from pathlib import Path

import numpy as np
import polars as pl

from longevity_port_pipelines.config import (
    REFERENCE_SPECIES,
    TARGET_SPECIES,
    PipelineConfig,
)
from longevity_port_pipelines.models import OrthologMapping
from longevity_port_pipelines.stages.analyze import analyze_pair
from longevity_port_pipelines.stages.embed import PerResidueEmbedding
from longevity_port_pipelines.stages.interface import download_pdb, extract_interface_residues


def species_name(taxid: int) -> str:
    if taxid == REFERENCE_SPECIES.taxid:
        return REFERENCE_SPECIES.name

    for species in TARGET_SPECIES:
        if species.taxid == taxid:
            return species.name

    return str(taxid)


def embedding_path(
    output_dir: Path,
    model_name: str,
    complex_id: str,
    chain: str,
    taxid: int,
) -> Path:
    return output_dir / "embeddings" / model_name / f"{complex_id}_{chain}_{taxid}.npy"


def main() -> None:
    cfg = PipelineConfig()
    cfg.ensure_dirs()

    selection_path = cfg.output_dir / "selection.csv"
    coverage_path = cfg.output_dir / "ortholog_coverage.csv"

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing {selection_path}")

    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing {coverage_path}")

    selection = pl.read_csv(selection_path)
    coverage_df = pl.read_csv(coverage_path)

    mappings = [OrthologMapping(**row) for row in coverage_df.to_dicts()]

    mapping_by_source: dict[str, list[OrthologMapping]] = {}
    for mapping in mappings:
        mapping_by_source.setdefault(mapping.source_uniprot, []).append(mapping)

    results = []
    skipped_no_interface = 0
    skipped_missing_embedding = 0
    skipped_no_mapping = 0

    cols = selection.columns
    id_col = next((c for c in cols if c.lower() in ("id", "pinder_id", "system_id")), cols[0])

    for row in selection.iter_rows(named=True):
        complex_id = str(row[id_col])
        pdb_id = row.get("pdb_id")
        chain_r = row.get("chain_R")
        chain_l = row.get("chain_L")

        interface_r: list[int] = []
        interface_l: list[int] = []

        if pdb_id and chain_r and chain_l:
            try:
                pdb_path = download_pdb(str(pdb_id), cfg.interim_dir / "pdb")
                interface_r, interface_l = extract_interface_residues(
                    pdb_path,
                    str(chain_r),
                    str(chain_l),
                    cfg.interface_distance_cutoff,
                )
            except Exception as exc:
                print(f"[WARN] Could not extract interface for {complex_id}: {exc}")

        for chain_label, up_col, seq_col, interface_residues in [
            ("receptor", "uniprot_R", "receptor_sequence", interface_r),
            ("ligand", "uniprot_L", "ligand_sequence", interface_l),
        ]:
            source_uniprot = row.get(up_col)
            ref_sequence = row.get(seq_col)

            if not source_uniprot or not ref_sequence:
                continue

            if not interface_residues:
                skipped_no_interface += 1
                print(f"[SKIP] {complex_id}/{chain_label}: no interface residues")
                continue

            chain_mappings = mapping_by_source.get(str(source_uniprot), [])
            if not chain_mappings:
                skipped_no_mapping += 1
                print(f"[SKIP] {complex_id}/{chain_label}/{source_uniprot}: no ortholog mappings")
                continue

            ref_path = embedding_path(
                cfg.output_dir,
                cfg.esmc_model,
                complex_id,
                chain_label,
                REFERENCE_SPECIES.taxid,
            )

            if not ref_path.exists():
                skipped_missing_embedding += 1
                print(f"[SKIP] Missing reference embedding: {ref_path}")
                continue

            ref_embedding_array = np.load(ref_path)

            ref_embedding = PerResidueEmbedding(
                complex_id=complex_id,
                chain=chain_label,
                species_taxid=REFERENCE_SPECIES.taxid,
                model_name=cfg.esmc_model,
                sequence=str(ref_sequence),
                embeddings=ref_embedding_array,
                is_predicted_structure=bool(row.get("predicted_R"))
                if chain_label == "receptor"
                else bool(row.get("predicted_L")),
            )

            for mapping in chain_mappings:
                orth_path = embedding_path(
                    cfg.output_dir,
                    cfg.esmc_model,
                    complex_id,
                    chain_label,
                    mapping.target_species_taxid,
                )

                if not orth_path.exists():
                    skipped_missing_embedding += 1
                    print(f"[SKIP] Missing ortholog embedding: {orth_path}")
                    continue

                orth_embedding_array = np.load(orth_path)

                orth_embedding = PerResidueEmbedding(
                    complex_id=complex_id,
                    chain=chain_label,
                    species_taxid=mapping.target_species_taxid,
                    model_name=cfg.esmc_model,
                    sequence=mapping.target_sequence,
                    embeddings=orth_embedding_array,
                    is_predicted_structure=not mapping.is_reviewed,
                )

                result = analyze_pair(
                    ref=ref_embedding,
                    orth=orth_embedding,
                    interface_residues=interface_residues,
                    source_species_name=species_name(REFERENCE_SPECIES.taxid),
                    target_species_name=species_name(mapping.target_species_taxid),
                    n_permutations=cfg.n_permutations,
                )
                results.append(result)

    out_path = cfg.output_dir / "enrichment.parquet"

    if results:
        out_df = pl.DataFrame([result.model_dump() for result in results])
    else:
        out_df = pl.DataFrame()

    out_df.write_parquet(out_path)

    print()
    print(f"Wrote {len(results)} enrichment results -> {out_path}")
    print(f"Skipped no interface: {skipped_no_interface}")
    print(f"Skipped no mapping: {skipped_no_mapping}")
    print(f"Skipped missing embedding: {skipped_missing_embedding}")

    if results:
        print()
        print(
            out_df.select(
                [
                    "complex_id",
                    "chain",
                    "target_species",
                    "interface_mean_delta",
                    "noninterface_mean_delta",
                    "enrichment_ratio",
                    "mann_whitney_p",
                    "effect_size_cohens_d",
                ]
            )
            .sort("enrichment_ratio", descending=True)
            .head(20)
        )


if __name__ == "__main__":
    main()