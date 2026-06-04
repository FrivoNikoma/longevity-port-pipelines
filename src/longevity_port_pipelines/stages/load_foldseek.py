"""Stage 2: Filter candidates by AFDB Foldseek structural conservation."""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl
import requests

from longevity_port_pipelines.config import PipelineConfig

logger = logging.getLogger(__name__)

AFDB_CLUSTER_URL = (
    "https://afdb-cluster.steineggerlab.workers.dev/cluster_data.tsv"
)


def _download_if_missing(url: str, dest: Path, timeout: int = 300) -> Path:
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading %s -> %s", url, dest)
    resp = requests.get(url, timeout=timeout, stream=True)
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return dest


def load_foldseek_clusters(cfg: PipelineConfig) -> pl.LazyFrame:
    """Download and load AFDB Foldseek cluster assignments.

    The cluster table maps AlphaFold DB entries to structural cluster IDs.
    Clusters spanning many species indicate structural conservation.
    """
    dest = cfg.interim_dir / "foldseek" / "cluster_data.tsv"

    if not dest.exists():
        try:
            _download_if_missing(AFDB_CLUSTER_URL, dest)
        except Exception:
            logger.warning(
                "Could not download Foldseek cluster table from %s. "
                "Stage 2 will pass all candidates through unfiltered.",
                AFDB_CLUSTER_URL,
            )
            return pl.LazyFrame()

    return pl.scan_csv(dest, separator="\t", infer_schema_length=10000)


def count_species_per_cluster(clusters_lf: pl.LazyFrame) -> pl.LazyFrame:
    """Count distinct species (by taxid) per cluster."""
    schema_cols = clusters_lf.collect_schema().names()

    taxid_col = next(
        (c for c in schema_cols if c.lower() in ("taxid", "tax_id", "species_taxid", "organism")),
        None,
    )
    cluster_col = next(
        (c for c in schema_cols if c.lower() in ("cluster_id", "cluster", "rep_accession")),
        None,
    )

    if taxid_col is None or cluster_col is None:
        logger.warning(
            "Foldseek cluster table missing expected columns (found: %s). "
            "Skipping conservation filter.",
            schema_cols,
        )
        return pl.LazyFrame()

    return (
        clusters_lf
        .group_by(cluster_col)
        .agg(pl.col(taxid_col).n_unique().alias("n_species"))
    )


def filter_by_conservation(
    candidates_lf: pl.LazyFrame,
    clusters_lf: pl.LazyFrame,
    cfg: PipelineConfig,
) -> pl.LazyFrame:
    """Keep candidates whose proteins belong to structurally conserved clusters.

    If cluster data is unavailable, passes all candidates through with a warning.
    """
    if clusters_lf.collect_schema().len() == 0:
        logger.warning("No Foldseek cluster data available — passing all candidates through")
        return candidates_lf

    species_counts = count_species_per_cluster(clusters_lf)
    if species_counts.collect_schema().len() == 0:
        return candidates_lf

    conserved = species_counts.filter(pl.col("n_species") >= cfg.min_cluster_species)
    cluster_col = conserved.collect_schema().names()[0]

    candidate_cols = candidates_lf.collect_schema().names()
    join_col = next(
        (c for c in candidate_cols if "cluster" in c.lower()),
        None,
    )

    if join_col is None:
        logger.warning("No cluster column in candidates — skipping Foldseek filter")
        return candidates_lf

    n_before = candidates_lf.select(pl.len()).collect().item()
    result = candidates_lf.join(
        conserved.select(pl.col(cluster_col)),
        left_on=join_col,
        right_on=cluster_col,
        how="semi",
    )
    n_after = result.select(pl.len()).collect().item()
    logger.info("Foldseek conservation filter: %d -> %d candidates", n_before, n_after)

    return result


def run_stage(candidates_lf: pl.LazyFrame, cfg: PipelineConfig) -> pl.LazyFrame:
    """Run the full Foldseek filter stage."""
    clusters_lf = load_foldseek_clusters(cfg)
    return filter_by_conservation(candidates_lf, clusters_lf, cfg)
