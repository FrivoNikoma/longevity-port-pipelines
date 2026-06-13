"""Stage 4: Fetch orthologs for long-lived species via OMA and UniProt REST."""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl
import requests

from longevity_port_pipelines.config import REFERENCE_SPECIES, TARGET_SPECIES, PipelineConfig
from longevity_port_pipelines.models import OrthologMapping, Species

logger = logging.getLogger(__name__)

OMA_API = "https://omabrowser.org/api"
UNIPROT_API = "https://rest.uniprot.org"


def query_oma_protein_sequence(entry_url: str) -> str:
    """Fetch a protein sequence from an OMA protein detail endpoint.

    The OMA ortholog list endpoint may provide only sequence metadata plus
    an entry_url. In that case, fetch the protein detail endpoint and read
    the full sequence field there.
    """
    if not entry_url:
        return ""

    try:
        resp = requests.get(entry_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        logger.warning("OMA protein detail query failed for %s", entry_url)
        return ""

    sequence = data.get("sequence", "")
    return str(sequence).strip() if sequence else ""


def query_oma_orthologs(uniprot_id: str, target_taxid: int) -> list[OrthologMapping]:
    """Query OMA API for orthologs of a given protein in a target species."""
    url = f"{OMA_API}/protein/{uniprot_id}/orthologs/"
    try:
        resp = requests.get(url, params={"format": "json"}, timeout=30)
        resp.raise_for_status()
        entries = resp.json()
    except (requests.RequestException, ValueError):
        logger.warning("OMA query failed for %s", uniprot_id)
        return []

    results: list[OrthologMapping] = []
    for entry in entries:
        species = entry.get("species", {})
        if species.get("taxon_id") != target_taxid:
            continue

        target_id = str(entry.get("canonicalid", "")).strip()
        sequence = str(entry.get("sequence", "") or "").strip()
        if not sequence:
            sequence = query_oma_protein_sequence(str(entry.get("entry_url", "")))

        if not target_id or not sequence:
            logger.debug(
                "Skipping OMA ortholog hit for %s taxid=%d because target_id or sequence is missing",
                uniprot_id,
                target_taxid,
            )
            continue

        results.append(
            OrthologMapping(
                source_uniprot=uniprot_id,
                source_species_taxid=REFERENCE_SPECIES.taxid,
                target_uniprot=target_id,
                target_species_taxid=target_taxid,
                target_sequence=sequence,
                is_reviewed=True,
                source_db="OMA",
            )
        )

    return results


def query_uniprot_orthologs(uniprot_id: str, target_taxid: int) -> list[OrthologMapping]:
    """Fallback: search UniProt for orthologs by gene name + taxid."""
    info_url = f"{UNIPROT_API}/uniprotkb/{uniprot_id}.json"
    try:
        resp = requests.get(info_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        logger.debug("UniProt info query failed for %s", uniprot_id)
        return []

    genes = data.get("genes", [])
    if not genes:
        return []
    gene_name = genes[0].get("geneName", {}).get("value", "")
    if not gene_name:
        return []

    search_url = f"{UNIPROT_API}/uniprotkb/search"
    params = {
        "query": f"gene:{gene_name} AND organism_id:{target_taxid}",
        "format": "json",
        "size": "5",
        "fields": "accession,sequence,reviewed",
    }
    try:
        resp = requests.get(search_url, params=params, timeout=30)
        resp.raise_for_status()
        hits = resp.json().get("results", [])
    except requests.RequestException:
        logger.debug("UniProt search failed for gene=%s taxid=%d", gene_name, target_taxid)
        return []

    results: list[OrthologMapping] = []
    for hit in hits:
        acc = hit.get("primaryAccession", "")
        seq_data = hit.get("sequence", {})
        seq = seq_data.get("value", "")
        reviewed = hit.get("entryType", "") == "UniProtKB reviewed (Swiss-Prot)"

        if not acc or not seq:
            continue

        results.append(
            OrthologMapping(
                source_uniprot=uniprot_id,
                source_species_taxid=REFERENCE_SPECIES.taxid,
                target_uniprot=acc,
                target_species_taxid=target_taxid,
                target_sequence=seq,
                is_reviewed=reviewed,
                source_db="UniProt",
            )
        )

    return results


def fetch_ortholog(uniprot_id: str, target: Species) -> OrthologMapping | None:
    """Fetch best ortholog: try OMA first, fall back to UniProt."""
    orthologs = query_oma_orthologs(uniprot_id, target.taxid)
    if not orthologs:
        orthologs = query_uniprot_orthologs(uniprot_id, target.taxid)
    if not orthologs:
        return None

    reviewed = [o for o in orthologs if o.is_reviewed]
    return reviewed[0] if reviewed else orthologs[0]


def fetch_orthologs_for_complexes(
    candidates_lf: pl.LazyFrame,
    cfg: PipelineConfig,
) -> tuple[pl.LazyFrame, list[OrthologMapping]]:
    """Fetch orthologs for all chains in selected complexes.

    Collects the LazyFrame here because we need row-by-row API calls.
    Returns the original LazyFrame (unchanged) plus collected ortholog mappings.
    """
    df = candidates_lf.collect()
    cols = df.columns

    id_col = next((c for c in cols if c.lower() in ("id", "pinder_id", "system_id")), cols[0])
    uniprot_r = "uniprot_R" if "uniprot_R" in cols else None
    uniprot_l = "uniprot_L" if "uniprot_L" in cols else None

    all_mappings: list[OrthologMapping] = []

    for row in df.iter_rows(named=True):
        complex_id = str(row[id_col])
        for chain_label, up_col in [("receptor", uniprot_r), ("ligand", uniprot_l)]:
            if up_col is None:
                continue
            uniprot_id = row.get(up_col)
            if not uniprot_id:
                continue

            for target in TARGET_SPECIES:
                mapping = fetch_ortholog(str(uniprot_id), target)
                if mapping:
                    all_mappings.append(mapping)
                    logger.info(
                        "%s/%s -> %s (%s, %s)",
                        complex_id,
                        chain_label,
                        target.name,
                        mapping.target_uniprot,
                        mapping.source_db,
                    )
                else:
                    logger.warning(
                        "%s/%s -> %s: no ortholog found",
                        complex_id,
                        chain_label,
                        target.name,
                    )

    return candidates_lf, all_mappings


def write_ortholog_coverage(
    mappings: list[OrthologMapping],
    cfg: PipelineConfig,
) -> Path:
    """Write ortholog coverage CSV for human audit."""
    output_path = cfg.output_dir / "ortholog_coverage.csv"
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    rows = [m.model_dump() for m in mappings]
    df = pl.DataFrame(rows) if rows else pl.DataFrame()
    df.write_csv(output_path)
    logger.info("Wrote ortholog coverage: %d mappings -> %s", len(rows), output_path)
    return output_path


def run_stage(
    candidates_lf: pl.LazyFrame, cfg: PipelineConfig
) -> tuple[pl.LazyFrame, list[OrthologMapping]]:
    """Run the full ortholog-fetching stage."""
    candidates_lf, mappings = fetch_orthologs_for_complexes(candidates_lf, cfg)
    write_ortholog_coverage(mappings, cfg)
    return candidates_lf, mappings
