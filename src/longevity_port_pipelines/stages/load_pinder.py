"""Stage 1: Load PINDER PPI dataset from HuggingFace, select candidates."""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl
from huggingface_hub import hf_hub_download

from longevity_port_pipelines.config import PipelineConfig

logger = logging.getLogger(__name__)

PINDER_PARQUET_FILES = [
    "data/train-00000-of-00002.parquet",
    "data/train-00001-of-00002.parquet",
]


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

    All filtering stays lazy — no `.collect()` until final output.
    """
    filtered = parse_pinder_id(lf)

    # Experimental structures only.
    filtered = filtered.filter(
        (pl.col("predicted_R") == False) & (pl.col("predicted_L") == False)  # noqa: E712
    )

    # Enough interface contacts to have a meaningful interface.
    filtered = filtered.filter(pl.col("intermolecular_contacts") >= cfg.min_interface_contacts)

    # Both chains must resolve to a UniProt accession (needed for orthologs).
    filtered = filtered.filter(
        pl.col("uniprot_R").is_not_null() & pl.col("uniprot_L").is_not_null()
    )

    # Reasonable chain lengths for the GPU stage.
    filtered = filtered.filter(
        (pl.col("receptor_sequence").str.len_chars() <= cfg.max_chain_length)
        & (pl.col("ligand_sequence").str.len_chars() <= cfg.max_chain_length)
    )

    # Deduplicate by interacting UniProt pair (order-independent) so we get
    # DISTINCT complexes, not many copies of the same homo-oligomer interface.
    filtered = filtered.with_columns(
        pl.concat_list(
            pl.min_horizontal("uniprot_R", "uniprot_L"),
            pl.max_horizontal("uniprot_R", "uniprot_L"),
        ).alias("_pair")
    )
    filtered = (
        filtered.sort("intermolecular_contacts", descending=True)
        .unique(subset="_pair", keep="first", maintain_order=True)
        .drop("_pair")
    )

    return filtered.head(cfg.selection_count)


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
