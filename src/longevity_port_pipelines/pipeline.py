"""Plain-Python stage runners for all 7 stages.

These functions hold the per-stage orchestration logic. Both the Prefect flow
(flow.py) and the per-stage CLI commands (cli.py) call into them — so the
pipeline runs identically with or without Prefect in the loop.
"""

from __future__ import annotations

import logging

import polars as pl

from longevity_port_pipelines.config import (
    REFERENCE_SPECIES,
    TARGET_SPECIES,
    PipelineConfig,
)
from longevity_port_pipelines.models import EnrichmentResult, OrthologMapping
from longevity_port_pipelines.stages import fetch_orthologs, load_foldseek, load_pinder, load_string
from longevity_port_pipelines.stages.embed import (
    PerResidueEmbedding,
    embed_pair,
    get_biohub_token,
    save_embeddings,
)
from longevity_port_pipelines.stages.interface import download_pdb, extract_interface_residues
from longevity_port_pipelines.stages.negatome_controls import (
    NegatomePairLookup,
    apply_negatome_control_to_result,
    build_negatome_pair_lookup,
    embed_negatome_control_partners,
    load_negatome_control_pairs,
)

logger = logging.getLogger(__name__)

# (reference embedding, ortholog embedding, interface residue indices,
#  source species name, target species name)
EmbeddingPair = tuple[PerResidueEmbedding, PerResidueEmbedding, list[int], str, str]


def run_stages_1_to_4(cfg: PipelineConfig) -> tuple[pl.LazyFrame, list[OrthologMapping]]:
    """Stages 1–4: load, filter, annotate, fetch orthologs.

    Writes selection.csv and ortholog_coverage.csv for human audit.
    """
    logger.info("=== Stage 1: Load PINDER ===")
    candidates = load_pinder.run_stage(cfg)

    logger.info("=== Stage 2: Foldseek conservation filter ===")
    candidates = load_foldseek.run_stage(candidates, cfg)

    logger.info("=== Stage 3: STRING hub annotation ===")
    candidates = load_string.run_stage(candidates, cfg)

    logger.info("=== Stage 4: Fetch orthologs ===")
    candidates, mappings = fetch_orthologs.run_stage(candidates, cfg)

    return candidates, mappings


def _load_negatome_pair_lookup(
    cfg: PipelineConfig,
) -> tuple[pl.DataFrame | None, NegatomePairLookup | None]:
    pairs = load_negatome_control_pairs(cfg.negatome_control_pairs_path)
    if pairs is None or pairs.is_empty():
        return None, None
    return pairs, build_negatome_pair_lookup(pairs)


def run_stage_5(
    candidates: pl.LazyFrame,
    mappings: list[OrthologMapping],
    cfg: PipelineConfig,
) -> list[EmbeddingPair]:
    """Stage 5: Embed reference + ortholog sequences.

    Returns list of (ref_embedding, orth_embedding, interface_residues,
    source_species, target_species) tuples.
    """
    logger.info("=== Stage 5: Embed sequences (Biohub API) ===")

    token = get_biohub_token()

    negatome_pairs, _ = _load_negatome_pair_lookup(cfg)
    if negatome_pairs is not None:
        embedded_count = embed_negatome_control_partners(negatome_pairs, cfg, token)
        logger.info("Embedded %d NEGATOME negative partner sequences", embedded_count)

    df = candidates.collect()
    cols = df.columns
    id_col = next((c for c in cols if c.lower() in ("id", "pinder_id", "system_id")), cols[0])
    pdb_col = "pdb_id" if "pdb_id" in cols else None
    chain_r_col = "chain_R" if "chain_R" in cols else None
    chain_l_col = "chain_L" if "chain_L" in cols else None
    seq_r_col = next((c for c in cols if c.lower() in ("receptor_sequence", "sequence_r")), None)
    seq_l_col = next((c for c in cols if c.lower() in ("ligand_sequence", "sequence_l")), None)

    mapping_by_source: dict[str, list[OrthologMapping]] = {}
    for m in mappings:
        mapping_by_source.setdefault(m.source_uniprot, []).append(m)

    results: list[EmbeddingPair] = []

    for row in df.iter_rows(named=True):
        complex_id = str(row[id_col])

        interface_r: list[int] = []
        interface_l: list[int] = []
        if pdb_col and chain_r_col and chain_l_col:
            pdb_id = row.get(pdb_col)
            ch_r = row.get(chain_r_col)
            ch_l = row.get(chain_l_col)
            if pdb_id and ch_r and ch_l:
                try:
                    pdb_path = download_pdb(str(pdb_id), cfg.interim_dir / "pdb")
                    interface_r, interface_l = extract_interface_residues(
                        pdb_path, str(ch_r), str(ch_l), cfg.interface_distance_cutoff
                    )
                except Exception:
                    logger.warning("Could not extract interface for %s", complex_id)

        for chain_label, seq_col, interface_res, up_col in [
            ("receptor", seq_r_col, interface_r, "uniprot_R"),
            ("ligand", seq_l_col, interface_l, "uniprot_L"),
        ]:
            if seq_col is None:
                continue
            ref_seq = row.get(seq_col)
            uniprot_id = row.get(up_col)
            if not ref_seq or not uniprot_id:
                continue

            chain_mappings = mapping_by_source.get(str(uniprot_id), [])
            for m in chain_mappings:
                target_species = next(
                    (s.name for s in TARGET_SPECIES if s.taxid == m.target_species_taxid),
                    str(m.target_species_taxid),
                )
                ref_emb, orth_emb = embed_pair(
                    complex_id=complex_id,
                    chain=chain_label,
                    ref_sequence=str(ref_seq),
                    orth_sequence=m.target_sequence,
                    ref_taxid=REFERENCE_SPECIES.taxid,
                    orth_taxid=m.target_species_taxid,
                    model=cfg.esmc_model,
                    api_url=cfg.biohub_api_url,
                    token=token,
                    is_predicted=not m.is_reviewed,
                )
                save_embeddings(ref_emb, cfg.output_dir)
                save_embeddings(orth_emb, cfg.output_dir)
                results.append(
                    (
                        ref_emb,
                        orth_emb,
                        interface_res,
                        REFERENCE_SPECIES.name,
                        target_species,
                    )
                )

    return results


def run_stage_6(
    embedding_pairs: list[EmbeddingPair],
    cfg: PipelineConfig,
) -> list[EnrichmentResult]:
    """Stage 6: Analyze enrichment."""
    from longevity_port_pipelines.stages.analyze import analyze_pair

    logger.info("=== Stage 6: Analyze enrichment ===")

    _, negatome_lookup = _load_negatome_pair_lookup(cfg)

    results: list[EnrichmentResult] = []
    for ref_emb, orth_emb, interface_res, source_sp, target_sp in embedding_pairs:
        if not interface_res:
            logger.warning(
                "Skipping %s/%s — no interface residues", ref_emb.complex_id, ref_emb.chain
            )
            continue

        result = analyze_pair(
            ref=ref_emb,
            orth=orth_emb,
            interface_residues=interface_res,
            source_species_name=source_sp,
            target_species_name=target_sp,
            n_permutations=cfg.n_permutations,
        )
        if negatome_lookup is not None:
            result = apply_negatome_control_to_result(
                result,
                ref=ref_emb,
                orth=orth_emb,
                interface_residues=interface_res,
                pair_lookup=negatome_lookup,
                interim_dir=cfg.interim_dir,
            )
        results.append(result)

    enrichment_df = pl.DataFrame([r.model_dump() for r in results]) if results else pl.DataFrame()
    out_path = cfg.output_dir / "enrichment.parquet"
    enrichment_df.write_parquet(out_path)
    logger.info("Wrote enrichment table: %d results -> %s", len(results), out_path)

    return results


def run_stage_7(results: list[EnrichmentResult], cfg: PipelineConfig) -> None:
    """Stage 7: Generate plots."""
    from longevity_port_pipelines.stages.plot import plot_enrichment_summary, plot_pvalue_volcano

    logger.info("=== Stage 7: Plot ===")
    plot_enrichment_summary(results, cfg.output_dir)
    plot_pvalue_volcano(results, cfg.output_dir)


def run_pipeline(cfg: PipelineConfig | None = None) -> list[EnrichmentResult]:
    """Run the full 7-stage pipeline."""
    if cfg is None:
        cfg = PipelineConfig()
    cfg.ensure_dirs()

    candidates, mappings = run_stages_1_to_4(cfg)

    logger.info(
        "=== PRE-GPU CHECKPOINT: review data/output/selection.csv and "
        "data/output/ortholog_coverage.csv before continuing ==="
    )

    embedding_pairs = run_stage_5(candidates, mappings, cfg)
    results = run_stage_6(embedding_pairs, cfg)
    run_stage_7(results, cfg)

    logger.info("Pipeline complete. Results in %s", cfg.output_dir)
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
