from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import polars as pl
from dotenv import load_dotenv

from longevity_port_pipelines.config import REFERENCE_SPECIES, TARGET_SPECIES, PipelineConfig
from longevity_port_pipelines.models import EnrichmentResult, OrthologMapping
from longevity_port_pipelines.stages.embed import PerResidueEmbedding
from longevity_port_pipelines.stages.mapped_interface import resolve_interfaces_for_row
from longevity_port_pipelines.stages.negatome_controls import (
    apply_negatome_control_to_result,
    build_negatome_pair_lookup,
    load_negatome_control_pairs,
)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patch negatome_control_ratio onto an existing enrichment parquet."
    )
    parser.add_argument(
        "--input",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_enrichment_mapped.parquet",
        help="Input enrichment parquet.",
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_selection.csv",
        help="Selection CSV path.",
    )
    parser.add_argument(
        "--coverage",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage.csv",
        help="Ortholog coverage CSV path.",
    )
    parser.add_argument(
        "--embedding-dir",
        default="data/output/embeddings",
        help="Directory containing saved embedding model subdirectories.",
    )
    parser.add_argument(
        "--negatome-pairs",
        default="data/interim/negatome_control_pairs.csv",
        help="Curated NEGATOME-style negative-control partner CSV.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output enrichment parquet path. Defaults to in-place update of --input.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path
    selection_path = Path(args.selection)
    coverage_path = Path(args.coverage)
    embedding_dir = Path(args.embedding_dir)

    pairs = load_negatome_control_pairs(Path(args.negatome_pairs))
    if pairs is None:
        raise FileNotFoundError(f"Missing NEGATOME control pairs file: {args.negatome_pairs}")

    cfg = PipelineConfig()
    cfg.ensure_dirs()
    pair_lookup = build_negatome_pair_lookup(pairs)

    selection = pl.read_csv(selection_path)
    selection_by_id = {str(row["id"]): row for row in selection.to_dicts()}
    coverage_df = pl.read_csv(coverage_path)
    mappings = [OrthologMapping(**row) for row in coverage_df.to_dicts()]
    mapping_by_source: dict[str, list[OrthologMapping]] = {}
    for mapping in mappings:
        mapping_by_source.setdefault(mapping.source_uniprot, []).append(mapping)

    interface_cache: dict[tuple[str, str], list[int]] = {}
    updated_rows: list[dict[str, object]] = []
    populated = 0
    skipped = 0

    enrichment_df = pl.read_parquet(input_path)

    for row in enrichment_df.to_dicts():
        result = EnrichmentResult(**row)
        selection_row = selection_by_id.get(result.complex_id)
        if selection_row is None:
            updated_rows.append(result.model_dump())
            skipped += 1
            continue

        cache_key = (result.complex_id, result.chain)
        if cache_key not in interface_cache:
            interface_r, interface_l, _, _, _ = resolve_interfaces_for_row(
                selection_row,
                cfg,
                8.0,
            )
            interface_cache[(result.complex_id, "receptor")] = interface_r
            interface_cache[(result.complex_id, "ligand")] = interface_l

        interface_residues = interface_cache.get(cache_key, [])
        if not interface_residues:
            updated_rows.append(result.model_dump())
            skipped += 1
            continue

        up_col = "uniprot_R" if result.chain == "receptor" else "uniprot_L"
        seq_col = "receptor_sequence" if result.chain == "receptor" else "ligand_sequence"
        source_uniprot = str(selection_row[up_col])
        ref_sequence = str(selection_row[seq_col])

        mapping = next(
            (
                item
                for item in mapping_by_source.get(source_uniprot, [])
                if species_name(item.target_species_taxid) == result.target_species
            ),
            None,
        )
        if mapping is None:
            updated_rows.append(result.model_dump())
            skipped += 1
            continue

        ref_path = embedding_path(
            embedding_dir,
            result.model_name,
            result.complex_id,
            result.chain,
            REFERENCE_SPECIES.taxid,
        )
        orth_path = embedding_path(
            embedding_dir,
            result.model_name,
            result.complex_id,
            result.chain,
            mapping.target_species_taxid,
        )
        if not ref_path.exists() or not orth_path.exists():
            updated_rows.append(result.model_dump())
            skipped += 1
            continue

        ref_embedding = PerResidueEmbedding(
            complex_id=result.complex_id,
            chain=result.chain,
            species_taxid=REFERENCE_SPECIES.taxid,
            model_name=result.model_name,
            sequence=ref_sequence,
            embeddings=np.load(ref_path),
            is_predicted_structure=bool(result.is_predicted_structure),
        )
        orth_embedding = PerResidueEmbedding(
            complex_id=result.complex_id,
            chain=result.chain,
            species_taxid=mapping.target_species_taxid,
            model_name=result.model_name,
            sequence=mapping.target_sequence,
            embeddings=np.load(orth_path),
            is_predicted_structure=not mapping.is_reviewed,
        )

        updated = apply_negatome_control_to_result(
            result,
            ref=ref_embedding,
            orth=orth_embedding,
            interface_residues=interface_residues,
            pair_lookup=pair_lookup,
            interim_dir=cfg.interim_dir,
            source_uniprot=source_uniprot,
        )
        if updated.negatome_control_ratio is not None:
            populated += 1
        updated_rows.append(updated.model_dump())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(updated_rows).write_parquet(output_path)

    print(f"Patched enrichment with NEGATOME controls -> {output_path}")
    print(f"Populated negatome_control_ratio for {populated} / {len(updated_rows)} rows")
    print(f"Skipped rows: {skipped}")


if __name__ == "__main__":
    main()
