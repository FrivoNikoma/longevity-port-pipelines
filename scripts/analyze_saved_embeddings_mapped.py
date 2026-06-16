from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import polars as pl
from dotenv import load_dotenv

from longevity_port_pipelines.config import REFERENCE_SPECIES, TARGET_SPECIES, PipelineConfig
from longevity_port_pipelines.models import OrthologMapping
from longevity_port_pipelines.stages.analyze import analyze_pair
from longevity_port_pipelines.stages.embed import PerResidueEmbedding, get_biohub_token
from longevity_port_pipelines.stages.mapped_interface import resolve_interfaces_for_row
from longevity_port_pipelines.stages.negatome_controls import (
    apply_negatome_control_to_result,
    build_negatome_pair_lookup,
    embed_negatome_control_partners,
    load_negatome_control_pairs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze saved embeddings using sequence-mapped PDB/mmCIF interface extraction."
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
        default="data/output/sirt6_mini_pilot_enrichment_mapped.parquet",
        help="Output enrichment parquet path.",
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
    parser.add_argument(
        "--negatome-pairs",
        default="data/interim/negatome_control_pairs.csv",
        help="Curated NEGATOME-style negative-control partner CSV.",
    )
    parser.add_argument(
        "--embed-negatome-partners",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Embed missing negative-partner sequences via Biohub before analysis.",
    )
    return parser.parse_args()


def species_name(taxid: int) -> str:
    if taxid == REFERENCE_SPECIES.taxid:
        return REFERENCE_SPECIES.name

    for species in TARGET_SPECIES:
        if species.taxid == taxid:
            return species.name

    return str(taxid)


def embedding_path(
    embedding_dir: Path,
    model_name: str,
    complex_id: str,
    chain: str,
    taxid: int,
) -> Path:
    return embedding_dir / model_name / f"{complex_id}_{chain}_{taxid}.npy"


def main() -> None:
    load_dotenv()
    args = parse_args()
    cfg = PipelineConfig()
    cfg.ensure_dirs()

    selection_path = Path(args.selection)
    coverage_path = Path(args.coverage)
    output_path = Path(args.output)
    embedding_dir = Path(args.embedding_dir)

    negatome_pairs = load_negatome_control_pairs(Path(args.negatome_pairs))
    negatome_lookup = (
        build_negatome_pair_lookup(negatome_pairs) if negatome_pairs is not None else None
    )
    if negatome_pairs is not None and args.embed_negatome_partners:
        from longevity_port_pipelines.stages.negatome_controls import (
            negative_partner_embedding_path,
        )

        unique_partners = negatome_pairs.select("negative_partner_uniprot").unique()
        missing_partners = [
            str(row["negative_partner_uniprot"])
            for row in unique_partners.iter_rows(named=True)
            if not negative_partner_embedding_path(
                cfg.interim_dir,
                cfg.esmc_model,
                str(row["negative_partner_uniprot"]),
            ).exists()
        ]
        if missing_partners:
            token = get_biohub_token()
            embedded_count = embed_negatome_control_partners(negatome_pairs, cfg, token)
            print(f"[NEGATOME] Embedded {embedded_count} negative partner sequences")
        else:
            print("[NEGATOME] Reusing cached negative partner embeddings")

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

    results = []
    skipped_no_interface = 0
    skipped_no_mapping = 0
    skipped_missing_embedding = 0

    for row in selection.iter_rows(named=True):
        complex_id = str(row["id"])

        try:
            interface_r, interface_l, resolved_r, resolved_l, fmt = resolve_interfaces_for_row(
                row,
                cfg,
                args.distance_cutoff,
            )
            print(
                f"[INTERFACE] {complex_id}: {fmt} chains "
                f"{row['chain_R']}/{row['chain_L']} -> {resolved_r}/{resolved_l}; "
                f"R={len(interface_r)} L={len(interface_l)}"
            )
        except Exception as exc:
            skipped_no_interface += 2
            print(f"[SKIP] {complex_id}: could not resolve/extract interface: {exc}")
            continue

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
                embedding_dir,
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
                    embedding_dir,
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
                if negatome_lookup is not None:
                    result = apply_negatome_control_to_result(
                        result,
                        ref=ref_embedding,
                        orth=orth_embedding,
                        interface_residues=interface_residues,
                        pair_lookup=negatome_lookup,
                        interim_dir=cfg.interim_dir,
                        source_uniprot=str(source_uniprot),
                    )
                results.append(result)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df = (
        pl.DataFrame([result.model_dump() for result in results]) if results else pl.DataFrame()
    )
    out_df.write_parquet(output_path)

    print()
    print(f"Wrote {len(results)} enrichment results -> {output_path}")
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
            .head(30)
        )


if __name__ == "__main__":
    main()
