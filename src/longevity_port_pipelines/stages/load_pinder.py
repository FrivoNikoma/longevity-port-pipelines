"""Stage 1: Load PINDER PPI dataset from HuggingFace, select candidates."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

import polars as pl
from huggingface_hub import hf_hub_download

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.config_utils import load_candidate_sets

logger = logging.getLogger(__name__)

PINDER_PARQUET_FILES = [
    "data/train-00000-of-00002.parquet",
    "data/train-00001-of-00002.parquet",
]


def load_candidate_uniprots(cfg: PipelineConfig) -> set[str]:
    """Load UniProt IDs from the curated longevity candidate list.

    Prefer data/output/candidates.csv because it is generated and clean.
    Fall back to data/input/candidates.csv, skipping comment lines.
    """
    candidate_paths = [
        cfg.output_dir / "candidates.csv",
        cfg.input_dir / "candidates.csv",
    ]

    for path in candidate_paths:
        if not path.exists():
            continue

        with path.open(encoding="utf-8", newline="") as handle:
            lines = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
            reader = csv.DictReader(lines)
            uniprots = {
                row["uniprot_id"].strip() for row in reader if row.get("uniprot_id", "").strip()
            }

        if uniprots:
            logger.info("Loaded %d candidate UniProt IDs from %s", len(uniprots), path)
            return uniprots

    logger.warning(
        "No candidate UniProt IDs found; PINDER selection will not be candidate-filtered"
    )
    return set()


def load_candidate_set_genes(cfg: PipelineConfig) -> set[str]:
    """Load focus genes and explicit partner genes for the configured candidate set."""
    candidate_sets = load_candidate_sets(cfg.candidate_sets_path)

    if cfg.candidate_set not in candidate_sets:
        valid_sets = ", ".join(sorted(candidate_sets))
        raise ValueError(
            f"Unknown candidate set: {cfg.candidate_set!r}. Available candidate sets: {valid_sets}"
        )

    candidate_set = candidate_sets[cfg.candidate_set]
    focus_genes = candidate_set.get("focus_genes", [])
    partner_genes = candidate_set.get("partners", [])

    genes = {str(gene).strip() for gene in [*focus_genes, *partner_genes] if str(gene).strip()}

    if not genes:
        logger.warning(
            "Candidate set %s has no focus_genes or partners; using direct candidate UniProt IDs",
            cfg.candidate_set,
        )

    logger.info(
        "Loaded %d configured genes from candidate set %s",
        len(genes),
        cfg.candidate_set,
    )
    return genes


def load_candidate_set_uniprots(cfg: PipelineConfig) -> set[str]:
    """Load explicit UniProt IDs from the configured candidate set."""
    candidate_sets = load_candidate_sets(cfg.candidate_sets_path)

    if cfg.candidate_set not in candidate_sets:
        valid_sets = ", ".join(sorted(candidate_sets))
        raise ValueError(
            f"Unknown candidate set: {cfg.candidate_set!r}. Available candidate sets: {valid_sets}"
        )

    candidate_set = candidate_sets[cfg.candidate_set]
    uniprot_ids = candidate_set.get("uniprot_ids", [])

    ids = {str(uniprot_id).strip() for uniprot_id in uniprot_ids if str(uniprot_id).strip()}

    logger.info(
        "Loaded %d explicit UniProt IDs from candidate set %s",
        len(ids),
        cfg.candidate_set,
    )
    return ids


def load_partner_aware_uniprots(cfg: PipelineConfig) -> set[str]:
    """Load focus longevity candidates plus strong post-translational partners.

    This avoids selecting random PINDER complexes while broadening beyond cases
    where the exact candidate protein itself appears in PINDER.
    """

    focus_genes = load_candidate_set_genes(cfg)
    configured_uniprots = load_candidate_set_uniprots(cfg)

    if not focus_genes and not configured_uniprots:
        return load_candidate_uniprots(cfg)

    if cfg.candidate_selection_mode == "explicit_only":
        logger.info(
            "Using explicit-only candidate selection for candidate set %s: %d UniProt IDs",
            cfg.candidate_set,
            len(configured_uniprots),
        )
        return configured_uniprots

    if cfg.candidate_selection_mode != "partner_aware":
        raise ValueError(
            f"Unknown candidate_selection_mode: {cfg.candidate_selection_mode!r}. "
            "Expected 'partner_aware' or 'explicit_only'."
        )

    candidates_path = cfg.output_dir / "candidates.csv"
    partners_path = cfg.output_dir / "interactome_partners.parquet"

    if not candidates_path.exists() or not partners_path.exists():
        logger.warning(
            "No candidates/interactome partner files found; using configured/direct candidate UniProt IDs"
        )
        return configured_uniprots | load_candidate_uniprots(cfg)

    candidates = pl.read_csv(candidates_path)
    focus_ids = (
        candidates.filter(pl.col("gene_name").is_in(sorted(focus_genes)))
        .get_column("uniprot_id")
        .to_list()
    )

    if not focus_ids:
        logger.warning("No focus UniProt IDs found; using direct candidate UniProt IDs")
        return load_candidate_uniprots(cfg)

    partners = pl.read_parquet(partners_path)
    partner_rows = partners.filter(
        (pl.col("type") == "post_translational")
        & (pl.col("n_sources") >= 5)
        & (pl.col("source").is_in(focus_ids) | pl.col("target").is_in(focus_ids))
    )

    focus_set = set(focus_ids) | configured_uniprots
    partner_ids: set[str] = set()

    for row in partner_rows.select(["source", "target"]).to_dicts():
        source = row["source"]
        target = row["target"]

        if source in focus_set:
            partner_ids.add(target)
        if target in focus_set:
            partner_ids.add(source)

    expanded = focus_set | partner_ids
    logger.info(
        "Loaded %d partner-aware UniProt IDs: %d focus + %d partners",
        len(expanded),
        len(focus_set),
        len(partner_ids),
    )
    return expanded


def load_pinder_index(cfg: PipelineConfig) -> pl.LazyFrame:
    """Download PINDER parquets from HuggingFace Hub and scan with polars."""
    local_dir = cfg.interim_dir / "pinder"
    local_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Resolving PINDER dataset from %s", cfg.pinder_dataset)
    local_paths: list[str] = []
    for filename in PINDER_PARQUET_FILES:
        path = hf_hub_download(
            repo_id=cfg.pinder_dataset,
            filename=filename,
            repo_type="dataset",
            local_dir=str(local_dir),
        )
        local_paths.append(path)

    return pl.scan_parquet(local_paths)


def parse_pinder_id(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Parse the PINDER system id into pdb / chain / uniprot columns.

    PINDER id format:  {pdb}__{chainR}_{uniprotR}--{pdb}__{chainL}_{uniprotL}
    e.g.  2wyy__C2_P03521--2wyy__H3_P03521
    """
    receptor = pl.col("id").str.split("--").list.get(0)
    ligand = pl.col("id").str.split("--").list.get(1)

    return lf.with_columns(
        receptor.str.split("__").list.get(0).alias("pdb_id"),
        receptor.str.split("__").list.get(1).str.split("_").list.get(0).alias("chain_R"),
        receptor.str.split("__").list.get(1).str.split("_").list.get(1).alias("uniprot_R"),
        ligand.str.split("__").list.get(1).str.split("_").list.get(0).alias("chain_L"),
        ligand.str.split("__").list.get(1).str.split("_").list.get(1).alias("uniprot_L"),
    )


def select_candidates(lf: pl.LazyFrame, cfg: PipelineConfig) -> pl.LazyFrame:
    """Apply quality filters and select diverse candidates for v1.

    Prefer complexes where at least one chain is a curated longevity candidate.
    If none survive the quality filters, fall back to the original unfiltered
    PINDER selection so the stage still produces a useful demo selection.
    """
    filtered = parse_pinder_id(lf)

    if not cfg.allow_predicted_structures:
        filtered = filtered.filter(
            (pl.col("predicted_R") == False) & (pl.col("predicted_L") == False)  # noqa: E712
        )

    # Enough interface contacts to have a meaningful interface.
    filtered = filtered.filter(pl.col("intermolecular_contacts") >= cfg.min_interface_contacts)

    # Both chains must resolve to a UniProt accession (needed for orthologs).
    filtered = filtered.filter(
        pl.col("uniprot_R").is_not_null() & pl.col("uniprot_L").is_not_null()
    )

    # Remove unresolved UniProt placeholders.
    filtered = filtered.filter(
        (pl.col("uniprot_R") != "UNDEFINED") & (pl.col("uniprot_L") != "UNDEFINED")
    )

    # Reasonable chain lengths for the GPU/API stage.
    filtered = filtered.filter(
        (pl.col("receptor_sequence").str.len_chars() <= cfg.max_chain_length)
        & (pl.col("ligand_sequence").str.len_chars() <= cfg.max_chain_length)
    )

    # Deduplicate by interacting UniProt pair (order-independent).
    filtered = filtered.with_columns(
        pl.concat_list(
            pl.min_horizontal("uniprot_R", "uniprot_L"),
            pl.max_horizontal("uniprot_R", "uniprot_L"),
        ).alias("_pair")
    )
    base_selection = (
        filtered.sort("intermolecular_contacts", descending=True)
        .unique(subset="_pair", keep="first", maintain_order=True)
        .drop("_pair")
    )

    candidate_uniprots = load_partner_aware_uniprots(cfg)
    if candidate_uniprots:
        candidate_selection = base_selection.filter(
            pl.col("uniprot_R").is_in(sorted(candidate_uniprots))
            | pl.col("uniprot_L").is_in(sorted(candidate_uniprots))
        )

        n_candidate_complexes = candidate_selection.select(pl.len()).collect().item()
        if n_candidate_complexes > 0:
            logger.info(
                "Candidate UniProt filter kept %d PINDER complexes",
                n_candidate_complexes,
            )
            return candidate_selection.head(cfg.selection_count)

        if not cfg.allow_unfiltered_fallback:
            logger.warning(
                "Candidate UniProt filter matched 0 PINDER complexes after quality filters; "
                "returning empty selection because allow_unfiltered_fallback=False"
            )
            return candidate_selection

        logger.warning(
            "Candidate UniProt filter matched 0 PINDER complexes after quality filters; "
            "falling back to unfiltered selection"
        )

    return base_selection.head(cfg.selection_count)


def write_selection(lf: pl.LazyFrame, cfg: PipelineConfig) -> Path:
    """Collect only at the final write — CSV for human audit."""
    output_path = cfg.output_dir / "selection.csv"
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    df = lf.collect()
    df.write_csv(output_path)
    logger.info("Wrote selection CSV: %d complexes -> %s", len(df), output_path)
    return output_path


def run_stage(cfg: PipelineConfig) -> pl.LazyFrame:
    """Run the full load_pinder stage."""
    lf = load_pinder_index(cfg)
    candidates = select_candidates(lf, cfg)
    write_selection(candidates, cfg)
    return candidates
