"""Task B: Interactome layer — fetch known interactors per candidate protein.

Uses OmniPath (aggregates STRING, BioGRID, IntAct, Reactome, etc.) for PPI
queries in a single bulk call. UniProt REST for protein annotations (mass,
subcellular location, glycosylation).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import polars as pl
import requests
from omnipath.interactions import AllInteractions

from longevity_port_pipelines.config import PipelineConfig

logger = logging.getLogger(__name__)

UNIPROT_API = "https://rest.uniprot.org"


def _to_float(val: object, default: float = 0.0) -> float:
    try:
        return float(val)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# OmniPath: bulk PPI fetch
# ---------------------------------------------------------------------------

def fetch_all_interactions(gene_names: list[str]) -> pl.DataFrame:
    """Fetch interactions for all candidate genes in one OmniPath call.

    OmniPath aggregates STRING, BioGRID, IntAct, Signor, Reactome, etc.
    Returns a polars DataFrame with source/target gene symbols, directionality,
    and source databases.
    """
    logger.info("Querying OmniPath for %d genes...", len(gene_names))
    pdf = AllInteractions.get(
        genesymbols=True,
        organisms="human",
        partners=gene_names,
    )
    if pdf is None or pdf.empty:
        logger.warning("OmniPath returned no interactions")
        return pl.DataFrame()

    return pl.from_pandas(pdf)


def summarise_interactome(
    interactions_lf: pl.LazyFrame,
    candidate_genes: list[str],
    hub_threshold: int,
) -> pl.DataFrame:
    """Summarise per-candidate: partner count, hub flag, top partners, source DBs."""
    gene_set = set(candidate_genes)
    interactions = interactions_lf.collect()

    rows: list[dict[str, object]] = []

    for gene in candidate_genes:
        partners_as_source = interactions.filter(
            pl.col("source_genesymbol") == gene
        ).get_column("target_genesymbol").to_list() if "source_genesymbol" in interactions.columns else []

        partners_as_target = interactions.filter(
            pl.col("target_genesymbol") == gene
        ).get_column("source_genesymbol").to_list() if "target_genesymbol" in interactions.columns else []

        all_partners = sorted(set(partners_as_source + partners_as_target) - {gene})
        n_partners = len(all_partners)

        gene_ints = interactions.filter(
            (pl.col("source_genesymbol") == gene) | (pl.col("target_genesymbol") == gene)
        )

        sources_col = "sources" if "sources" in gene_ints.columns else None
        all_sources: set[str] = set()
        if sources_col:
            for val in gene_ints.get_column(sources_col).to_list():
                if isinstance(val, str):
                    all_sources.update(val.split(";"))

        n_directed = 0
        n_stimulation = 0
        n_inhibition = 0
        if "is_directed" in gene_ints.columns:
            n_directed = gene_ints.filter(pl.col("is_directed") == 1).height
        if "is_stimulation" in gene_ints.columns:
            n_stimulation = gene_ints.filter(pl.col("is_stimulation") == 1).height
        if "is_inhibition" in gene_ints.columns:
            n_inhibition = gene_ints.filter(pl.col("is_inhibition") == 1).height

        partner_in_candidates = [p for p in all_partners if p in gene_set]

        rows.append({
            "gene_name": gene,
            "n_partners": n_partners,
            "is_hub": n_partners > hub_threshold,
            "n_directed": n_directed,
            "n_stimulation": n_stimulation,
            "n_inhibition": n_inhibition,
            "top_partners": ", ".join(all_partners[:15]),
            "databases": ", ".join(sorted(all_sources)),
            "partners_in_candidates": ", ".join(partner_in_candidates),
        })

    return pl.DataFrame(rows)


# ---------------------------------------------------------------------------
# UniProt: protein annotations (mass, membrane, glycosylation)
# ---------------------------------------------------------------------------

def _uniprot_cache_path(cache_dir: Path, uniprot_id: str) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"uniprot_{uniprot_id}.json"


def fetch_uniprot_entry(uniprot_id: str, cache_dir: Path) -> dict[str, object]:
    """Fetch a UniProt entry JSON, cached to disk."""
    cache_file = _uniprot_cache_path(cache_dir, uniprot_id)
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)  # type: ignore[no-any-return]

    url = f"{UNIPROT_API}/uniprotkb/{uniprot_id}.json"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data: dict[str, object] = resp.json()
    except requests.RequestException:
        logger.warning("UniProt fetch failed for %s", uniprot_id)
        return {}

    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data


def parse_uniprot_annotations(data: dict[str, object]) -> dict[str, object]:
    """Extract mass, membrane flag, glycosylation flag, keywords."""
    result: dict[str, object] = {}

    seq = data.get("sequence", {})
    if isinstance(seq, dict):
        mass = seq.get("molWeight")
        if mass is not None:
            result["mass_da"] = mass
            result["size_kda"] = round(int(mass) / 1000, 1)

    is_membrane = False
    comments = data.get("comments", [])
    if isinstance(comments, list):
        for comment in comments:
            if not isinstance(comment, dict):
                continue
            if comment.get("commentType") == "SUBCELLULAR LOCATION":
                locs = comment.get("subcellularLocations", [])
                if isinstance(locs, list):
                    for loc in locs:
                        if isinstance(loc, dict):
                            loc_val = loc.get("location", {})
                            if isinstance(loc_val, dict) and "membrane" in str(loc_val.get("value", "")).lower():
                                is_membrane = True
    result["is_membrane"] = is_membrane

    has_glycosylation = False
    features = data.get("features", [])
    if isinstance(features, list):
        for feat in features:
            if isinstance(feat, dict) and feat.get("type") == "Glycosylation":
                has_glycosylation = True
                break
    result["has_glycosylation"] = has_glycosylation

    keywords: list[str] = []
    kw_list = data.get("keywords", [])
    if isinstance(kw_list, list):
        for kw in kw_list:
            if isinstance(kw, dict):
                name = kw.get("name")
                if isinstance(name, str):
                    keywords.append(name)
    result["keywords"] = ", ".join(keywords)

    return result


# ---------------------------------------------------------------------------
# Stage runner
# ---------------------------------------------------------------------------

def build_interactome(
    candidates_df: pl.DataFrame,
    cfg: PipelineConfig,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Build interactome for all candidates.

    Returns (summary_df, interactions_df).
    """
    gene_names: list[str] = candidates_df.get_column("gene_name").to_list()
    uniprot_ids: list[str] = candidates_df.get_column("uniprot_id").to_list()

    interactions = fetch_all_interactions(gene_names)

    summary = summarise_interactome(
        interactions.lazy(), gene_names, cfg.hub_partner_threshold,
    )

    uniprot_cache = cfg.interim_dir / "uniprot"
    annot_rows: list[dict[str, object]] = []
    for gene, uid in zip(gene_names, uniprot_ids, strict=True):
        entry = fetch_uniprot_entry(uid, uniprot_cache)
        annots = parse_uniprot_annotations(entry)
        annots["gene_name"] = gene
        annots["uniprot_id"] = uid
        annot_rows.append(annots)

    annot_df = pl.DataFrame(annot_rows) if annot_rows else pl.DataFrame()

    if annot_df.height > 0 and summary.height > 0:
        summary = summary.join(annot_df, on="gene_name", how="left")

    category_map = dict(zip(gene_names, candidates_df.get_column("category").to_list(), strict=True))
    summary = summary.with_columns(
        pl.col("gene_name").replace_strict(category_map, default="").alias("category")
    )

    return summary, interactions


def run_stage(
    candidates_df: pl.DataFrame,
    cfg: PipelineConfig,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Run interactome stage. Writes interactome.csv + interactome_partners.parquet."""
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    summary_df, interactions_df = build_interactome(candidates_df, cfg)

    summary_path = cfg.output_dir / "interactome.csv"
    summary_df.write_csv(summary_path)
    logger.info("Wrote interactome summary: %d proteins -> %s", len(summary_df), summary_path)

    if interactions_df.height > 0:
        partners_path = cfg.output_dir / "interactome_partners.parquet"
        interactions_df.write_parquet(partners_path)
        logger.info("Wrote interactions: %d rows -> %s", len(interactions_df), partners_path)

    n_hubs = summary_df.filter(pl.col("is_hub")).height if "is_hub" in summary_df.columns else 0
    logger.info(
        "Hub proteins (>%d partners): %d / %d",
        cfg.hub_partner_threshold, n_hubs, len(summary_df),
    )

    return summary_df, interactions_df
