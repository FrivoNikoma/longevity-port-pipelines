from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import polars as pl
from scripts.analyze_saved_embeddings_mapped import (
    embedding_path,
    resolve_interfaces_for_row,
    species_name,
)

from longevity_port_pipelines.config import REFERENCE_SPECIES, PipelineConfig
from longevity_port_pipelines.models import OrthologMapping
from longevity_port_pipelines.stages.analyze import align_and_compute_deltas
from longevity_port_pipelines.stages.embed import PerResidueEmbedding


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export per-residue mapped embedding deltas for mini-pilot complexes."
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_mini_pilot_selection.csv",
        help="Selection CSV path.",
    )
    parser.add_argument(
        "--coverage",
        default="data/output/sirt6_mini_pilot_ortholog_coverage.csv",
        help="Ortholog coverage CSV path.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_residue_deltas_mapped.parquet",
        help="Output residue-level parquet path.",
    )
    parser.add_argument(
        "--embedding-dir",
        default="data/output/embeddings",
        help=(
            "Directory containing saved embedding model subdirectories. "
            "Defaults to data/output/embeddings for backwards compatibility."
        ),
    )
    parser.add_argument(
        "--distance-cutoff",
        type=float,
        default=8.0,
        help="Heavy-atom distance cutoff for interface residues.",
    )
    return parser.parse_args()


def _mapping_value(mapping: OrthologMapping, name: str, default: object = None) -> object:
    return getattr(mapping, name, default)


def residue_delta_rows(
    *,
    ref: PerResidueEmbedding,
    orth: PerResidueEmbedding,
    interface_residues: list[int],
    complex_id: str,
    pdb_id: str,
    chain_role: str,
    source_uniprot: str,
    mapping: OrthologMapping,
) -> list[dict[str, object]]:
    deltas, aligned_positions = align_and_compute_deltas(ref, orth)
    interface_set = set(interface_residues)

    rows: list[dict[str, object]] = []
    target_species_taxid = int(mapping.target_species_taxid)
    target_uniprot = str(_mapping_value(mapping, "target_uniprot", ""))

    for delta, ref_pos in zip(deltas, aligned_positions, strict=True):
        residue_index = int(ref_pos)
        residue_aa = ref.sequence[residue_index] if residue_index < len(ref.sequence) else "X"

        rows.append(
            {
                "complex_id": complex_id,
                "pdb_id": pdb_id,
                "chain": chain_role,
                "source_species": species_name(REFERENCE_SPECIES.taxid),
                "target_species": species_name(target_species_taxid),
                "source_species_taxid": REFERENCE_SPECIES.taxid,
                "target_species_taxid": target_species_taxid,
                "source_uniprot": source_uniprot,
                "target_uniprot": target_uniprot,
                "residue_index": residue_index,
                "residue_number_1based": residue_index + 1,
                "residue_aa": residue_aa,
                "delta": float(delta),
                "is_interface": residue_index in interface_set,
                "model_name": ref.model_name,
                "is_predicted_structure": bool(orth.is_predicted_structure),
            }
        )

    return rows


def main() -> None:
    args = parse_args()
    cfg = PipelineConfig()
    cfg.ensure_dirs()

    selection_path = Path(args.selection)
    coverage_path = Path(args.coverage)
    output_path = Path(args.output)
    embedding_dir = Path(args.embedding_dir)

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing selection CSV: {selection_path}")
    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing ortholog coverage CSV: {coverage_path}")

    selection = pl.read_csv(selection_path)
    coverage_df = pl.read_csv(coverage_path)

    mappings = [OrthologMapping(**row) for row in coverage_df.to_dicts()]
    mapping_by_source: dict[str, list[OrthologMapping]] = {}
    for mapping in mappings:
        mapping_by_source.setdefault(mapping.source_uniprot, []).append(mapping)

    rows: list[dict[str, object]] = []
    skipped_no_interface = 0
    skipped_no_mapping = 0
    skipped_missing_embedding = 0

    for row in selection.iter_rows(named=True):
        complex_id = str(row["id"])
        pdb_id = str(row["pdb_id"])

        try:
            interface_r, interface_l, resolved_r, resolved_l, _fmt = resolve_interfaces_for_row(
                row,
                cfg,
                args.distance_cutoff,
            )
        except Exception as exc:
            skipped_no_interface += 1
            print(f"[SKIP] {complex_id}: could not resolve mapped interface: {exc}")
            continue

        chain_specs = [
            (
                "receptor",
                str(row["uniprot_R"]),
                str(row["receptor_sequence"]),
                interface_r,
                resolved_r,
            ),
            (
                "ligand",
                str(row["uniprot_L"]),
                str(row["ligand_sequence"]),
                interface_l,
                resolved_l,
            ),
        ]

        for (
            chain_role,
            source_uniprot,
            ref_sequence,
            interface_residues,
            resolved_chain,
        ) in chain_specs:
            if not interface_residues:
                skipped_no_interface += 1
                print(f"[SKIP] {complex_id}/{chain_role}: empty interface")
                continue

            chain_mappings = mapping_by_source.get(source_uniprot, [])
            if not chain_mappings:
                skipped_no_mapping += 1
                print(f"[SKIP] {complex_id}/{chain_role}/{source_uniprot}: no ortholog mappings")
                continue

            ref_path = embedding_path(
                embedding_dir,
                cfg.esmc_model,
                complex_id,
                chain_role,
                REFERENCE_SPECIES.taxid,
            )

            if not ref_path.exists():
                skipped_missing_embedding += 1
                print(f"[SKIP] Missing reference embedding: {ref_path}")
                continue

            ref_embedding = PerResidueEmbedding(
                complex_id=complex_id,
                chain=chain_role,
                species_taxid=REFERENCE_SPECIES.taxid,
                model_name=cfg.esmc_model,
                sequence=ref_sequence,
                embeddings=np.load(ref_path),
                is_predicted_structure=bool(row.get("predicted_R"))
                if chain_role == "receptor"
                else bool(row.get("predicted_L")),
            )

            for mapping in chain_mappings:
                orth_path = embedding_path(
                    embedding_dir,
                    cfg.esmc_model,
                    complex_id,
                    chain_role,
                    mapping.target_species_taxid,
                )

                if not orth_path.exists():
                    skipped_missing_embedding += 1
                    print(f"[SKIP] Missing ortholog embedding: {orth_path}")
                    continue

                orth_embedding = PerResidueEmbedding(
                    complex_id=complex_id,
                    chain=chain_role,
                    species_taxid=mapping.target_species_taxid,
                    model_name=cfg.esmc_model,
                    sequence=mapping.target_sequence,
                    embeddings=np.load(orth_path),
                    is_predicted_structure=not mapping.is_reviewed,
                )

                new_rows = residue_delta_rows(
                    ref=ref_embedding,
                    orth=orth_embedding,
                    interface_residues=interface_residues,
                    complex_id=complex_id,
                    pdb_id=pdb_id,
                    chain_role=chain_role,
                    source_uniprot=source_uniprot,
                    mapping=mapping,
                )
                rows.extend(new_rows)

                print(
                    f"[OK] {complex_id}/{chain_role}/{source_uniprot} -> "
                    f"{species_name(mapping.target_species_taxid)}; "
                    f"structure_chain={resolved_chain}; residues={len(new_rows)}"
                )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df = pl.DataFrame(rows) if rows else pl.DataFrame()
    out_df.write_parquet(output_path)

    print()
    print(f"Wrote {len(rows)} residue-level delta rows -> {output_path}")
    print(f"Skipped no interface: {skipped_no_interface}")
    print(f"Skipped no mapping: {skipped_no_mapping}")
    print(f"Skipped missing embedding: {skipped_missing_embedding}")

    if rows:
        print()
        print(
            out_df.group_by(["complex_id", "chain", "target_species", "is_interface"])
            .agg(
                [
                    pl.len().alias("n_residues"),
                    pl.mean("delta").alias("mean_delta"),
                    pl.median("delta").alias("median_delta"),
                ]
            )
            .sort(["complex_id", "chain", "target_species", "is_interface"])
        )

        print()
        print("Top divergent interface residues:")
        print(
            out_df.filter(pl.col("is_interface"))
            .sort("delta", descending=True)
            .select(
                [
                    "complex_id",
                    "chain",
                    "target_species",
                    "source_uniprot",
                    "residue_number_1based",
                    "residue_aa",
                    "delta",
                ]
            )
            .head(30)
        )

        print()
        print("Most constrained interface residues:")
        print(
            out_df.filter(pl.col("is_interface"))
            .sort("delta")
            .select(
                [
                    "complex_id",
                    "chain",
                    "target_species",
                    "source_uniprot",
                    "residue_number_1based",
                    "residue_aa",
                    "delta",
                ]
            )
            .head(30)
        )


if __name__ == "__main__":
    main()
