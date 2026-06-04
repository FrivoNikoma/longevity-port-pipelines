"""Stage 3: Load STRING interaction data, annotate hub status."""

from __future__ import annotations

import gzip
import logging
from pathlib import Path

import polars as pl
import requests

from longevity_port_pipelines.config import REFERENCE_SPECIES, PipelineConfig

logger = logging.getLogger(__name__)

STRING_LINKS_URL_TEMPLATE = (
    "https://stringdb-downloads.org/download/"
    "protein.links.v12.5/{taxid}.protein.links.v12.5.txt.gz"
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


def load_string_links(taxid: int, cfg: PipelineConfig) -> pl.LazyFrame:
    """Load STRING links as a polars LazyFrame, filtering by score threshold."""
    url = STRING_LINKS_URL_TEMPLATE.format(taxid=taxid)
    gz_path = cfg.interim_dir / "string" / f"{taxid}.protein.links.v12.5.txt.gz"
    _download_if_missing(url, gz_path)

    tsv_path = gz_path.with_suffix("")
    if not tsv_path.exists():
        logger.info("Decompressing %s", gz_path)
        with gzip.open(gz_path, "rb") as f_in, open(tsv_path, "wb") as f_out:
            f_out.write(f_in.read())

    lf = pl.scan_csv(tsv_path, separator=" ", infer_schema_length=10000)
    return lf.filter(pl.col("combined_score") >= cfg.string_score_threshold)


def count_partners(links_lf: pl.LazyFrame) -> pl.LazyFrame:
    """Count interaction partners per protein from STRING links."""
    left_counts = (
        links_lf
        .group_by("protein1")
        .agg(pl.col("protein2").n_unique().alias("n_partners"))
        .rename({"protein1": "string_id"})
    )
    right_counts = (
        links_lf
        .group_by("protein2")
        .agg(pl.col("protein1").n_unique().alias("n_partners"))
        .rename({"protein2": "string_id"})
    )
    return (
        pl.concat([left_counts, right_counts])
        .group_by("string_id")
        .agg(pl.col("n_partners").sum())
    )


def annotate_hub_status(
    candidates_lf: pl.LazyFrame,
    cfg: PipelineConfig,
) -> pl.LazyFrame:
    """Annotate candidates with STRING partner counts and hub flags.

    Proteins with > hub_partner_threshold partners are flagged as hubs
    and deprioritized (sorted to bottom, not removed).
    """
    taxid = REFERENCE_SPECIES.taxid

    try:
        links_lf = load_string_links(taxid, cfg)
    except Exception:
        logger.warning("Could not load STRING data for taxid %d — skipping hub annotation", taxid)
        return candidates_lf

    partner_counts = count_partners(links_lf)

    candidate_cols = candidates_lf.collect_schema().names()
    uniprot_r = "uniprot_R" if "uniprot_R" in candidate_cols else None
    uniprot_l = "uniprot_L" if "uniprot_L" in candidate_cols else None

    result = candidates_lf

    if uniprot_r:
        result = result.join(
            partner_counts.rename({"string_id": "string_r", "n_partners": "partners_R"}),
            left_on=uniprot_r,
            right_on="string_r",
            how="left",
        )
    if uniprot_l:
        result = result.join(
            partner_counts.rename({"string_id": "string_l", "n_partners": "partners_L"}),
            left_on=uniprot_l,
            right_on="string_l",
            how="left",
        )

    hub_expr_parts: list[pl.Expr] = []
    if uniprot_r:
        hub_expr_parts.append(
            pl.col("partners_R").fill_null(0) > cfg.hub_partner_threshold
        )
    if uniprot_l:
        hub_expr_parts.append(
            pl.col("partners_L").fill_null(0) > cfg.hub_partner_threshold
        )

    if hub_expr_parts:
        hub_expr = hub_expr_parts[0]
        for part in hub_expr_parts[1:]:
            hub_expr = hub_expr | part
        result = result.with_columns(hub_expr.alias("is_hub"))
        result = result.sort("is_hub")

    return result


def run_stage(candidates_lf: pl.LazyFrame, cfg: PipelineConfig) -> pl.LazyFrame:
    """Run the full STRING hub annotation stage."""
    return annotate_hub_status(candidates_lf, cfg)
