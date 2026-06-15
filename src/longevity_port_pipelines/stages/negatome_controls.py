"""Load, embed, and apply curated NEGATOME-style negative-control partner inputs."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import polars as pl

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.models import EnrichmentResult
from longevity_port_pipelines.stages.embed import PerResidueEmbedding, embed_sequence
from longevity_port_pipelines.stages.negatome_analyze import compute_negatome_control_ratio
from longevity_port_pipelines.stages.negatome_inputs import (
    filter_nonempty_negative_control_pairs,
    validate_schema,
)

logger = logging.getLogger(__name__)

NegatomeLookupKey = tuple[str, str, str]
NegatomePairLookup = dict[NegatomeLookupKey, list[dict[str, object]]]


def negatome_lookup_key(complex_id: str, chain: str, target_species: str) -> NegatomeLookupKey:
    return complex_id, chain, target_species


def negative_partner_embedding_path(interim_dir: Path, model_name: str, uniprot: str) -> Path:
    safe_uniprot = uniprot.strip().replace("/", "_")
    return interim_dir / "negatome_embeddings" / model_name / f"{safe_uniprot}.npy"


def load_negatome_control_pairs(path: Path) -> pl.DataFrame | None:
    if not path.exists():
        return None

    pairs = pl.read_csv(path)
    validate_schema(pairs)
    return filter_nonempty_negative_control_pairs(pairs)


def build_negatome_pair_lookup(
    pairs: pl.DataFrame,
) -> NegatomePairLookup:
    lookup: NegatomePairLookup = {}

    for row in pairs.to_dicts():
        key = negatome_lookup_key(
            str(row["complex_id"]),
            str(row["chain"]),
            str(row["target_species"]),
        )
        lookup.setdefault(key, []).append(row)

    return lookup


def embed_negatome_control_partners(
    pairs: pl.DataFrame,
    cfg: PipelineConfig,
    token: str,
) -> int:
    """Embed curated negative-partner sequences; return count of newly written files."""
    validate_schema(pairs)
    embedded = 0

    unique_partners = (
        pairs.select(["negative_partner_uniprot", "negative_partner_sequence"])
        .unique()
        .sort("negative_partner_uniprot")
    )

    for row in unique_partners.iter_rows(named=True):
        uniprot = str(row["negative_partner_uniprot"])
        sequence = str(row["negative_partner_sequence"])
        output_path = negative_partner_embedding_path(cfg.interim_dir, cfg.esmc_model, uniprot)

        if output_path.exists():
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        embedding = embed_sequence(
            sequence=sequence,
            model=cfg.esmc_model,
            api_url=cfg.biohub_api_url,
            token=token,
        )
        np.save(output_path, embedding)
        embedded += 1
        logger.info("Embedded NEGATOME negative partner %s -> %s", uniprot, output_path)

    return embedded


def resolve_negatome_control_ratio(
    *,
    ref: PerResidueEmbedding,
    orth: PerResidueEmbedding,
    interface_residues: list[int],
    pair_rows: list[dict[str, object]],
    interim_dir: Path,
    model_name: str,
    source_uniprot: str | None = None,
) -> float | None:
    if not interface_residues or not pair_rows:
        return None

    ratios: list[float] = []

    for row in pair_rows:
        row_source = row.get("source_uniprot")
        if source_uniprot and row_source and str(row_source) != source_uniprot:
            continue

        uniprot = str(row["negative_partner_uniprot"])
        embedding_path = negative_partner_embedding_path(interim_dir, model_name, uniprot)
        if not embedding_path.exists():
            logger.warning(
                "Missing NEGATOME partner embedding for %s (%s)",
                uniprot,
                embedding_path,
            )
            continue

        negative_partner_embeddings = np.load(embedding_path)
        ratio = compute_negatome_control_ratio(
            ref=ref,
            orth=orth,
            interface_residues=interface_residues,
            negative_partner_embeddings=negative_partner_embeddings,
        )
        ratios.append(ratio)

    if not ratios:
        return None

    return float(np.median(ratios))


def apply_negatome_control_to_result(
    result: EnrichmentResult,
    *,
    ref: PerResidueEmbedding,
    orth: PerResidueEmbedding,
    interface_residues: list[int],
    pair_lookup: NegatomePairLookup,
    interim_dir: Path,
    source_uniprot: str | None = None,
) -> EnrichmentResult:
    key = negatome_lookup_key(result.complex_id, result.chain, result.target_species)
    pair_rows = pair_lookup.get(key, [])
    negatome_ratio = resolve_negatome_control_ratio(
        ref=ref,
        orth=orth,
        interface_residues=interface_residues,
        pair_rows=pair_rows,
        interim_dir=interim_dir,
        model_name=result.model_name,
        source_uniprot=source_uniprot,
    )
    if negatome_ratio is None:
        return result

    return result.model_copy(update={"negatome_control_ratio": negatome_ratio})
