"""Curated NEGATOME-style negative partner assignments for mini-pilot cases."""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl
import requests

from longevity_port_pipelines.stages.negatome_inputs import validate_schema
from longevity_port_pipelines.stages.ortholog_inputs import (
    filter_primary_curated_ortholog_candidates,
)

logger = logging.getLogger(__name__)

NEGATOME_PAIR_COLUMNS = [
    "complex_id",
    "chain",
    "target_species",
    "source_uniprot",
    "negative_partner_uniprot",
    "negative_partner_source",
    "negative_partner_sequence",
    "control_type",
]

CURATED_NEGATIVE_PARTNERS: dict[str, dict[str, str]] = {
    "P04908": {
        "negative_partner_uniprot": "P07437",
        "negative_partner_source": "negatome_database",
        "control_type": "curated_negative",
        "curation_note": (
            "Histone H2A tested against tubulin beta (TUBB). Cytoskeletal protein, not the "
            "nucleosome partner context."
        ),
    },
    "Q04206": {
        "negative_partner_uniprot": "P04637",
        "negative_partner_source": "curated_manual",
        "control_type": "curated_negative",
        "curation_note": (
            "NF-kB p65 tested against TP53. Regulatory protein outside the NF-kB/IkB complex."
        ),
    },
    "P09874": {
        "negative_partner_uniprot": "O60907",
        "negative_partner_source": "negatome_database",
        "control_type": "curated_negative",
        "curation_note": (
            "PARP1 tested against TBL1X from Negatome-style curation notes; not the PARP1 "
            "self-complex partner."
        ),
    },
    "Q8N6T7": {
        "negative_partner_uniprot": "P07437",
        "negative_partner_source": "curated_manual",
        "control_type": "curated_negative",
        "curation_note": ("SIRT6 tested against tubulin beta (TUBB), a non-chromatin interactor."),
    },
    "P12956": {
        "negative_partner_uniprot": "P49917",
        "negative_partner_source": "curated_manual",
        "control_type": "curated_negative",
        "curation_note": "Ku80 tested against LIG4, a DNA-repair protein outside the Ku70-Ku80 complex.",
    },
    "P13010": {
        "negative_partner_uniprot": "P49917",
        "negative_partner_source": "curated_manual",
        "control_type": "curated_negative",
        "curation_note": "Ku70 tested against LIG4, a DNA-repair protein outside the Ku70-Ku80 complex.",
    },
    "Q9H9Q4": {
        "negative_partner_uniprot": "P07437",
        "negative_partner_source": "curated_manual",
        "control_type": "curated_negative",
        "curation_note": (
            "8bhv ligand-side benchmark protein tested against tubulin beta, an unrelated "
            "cytoskeletal interactor."
        ),
    },
}


def parse_fasta_sequence(fasta_text: str) -> str:
    lines = [line.strip() for line in fasta_text.splitlines() if line.strip()]
    sequence_lines = [line for line in lines if not line.startswith(">")]
    if not sequence_lines:
        raise ValueError("FASTA payload did not contain a sequence")
    return "".join(sequence_lines)


def fetch_uniprot_sequence(uniprot: str, cache_dir: Path | None = None) -> str:
    uniprot_id = uniprot.strip().upper()
    cache_path = None
    if cache_dir is not None:
        cache_path = cache_dir / f"{uniprot_id}.fasta"
        if cache_path.exists():
            return parse_fasta_sequence(cache_path.read_text(encoding="utf-8"))

    response = requests.get(
        f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta",
        timeout=30,
    )
    response.raise_for_status()
    sequence = parse_fasta_sequence(response.text)

    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(response.text, encoding="utf-8")

    return sequence


def source_uniprot_for_chain(selection_row: dict[str, object], chain: str) -> str:
    if chain == "receptor":
        return str(selection_row["uniprot_R"])
    if chain == "ligand":
        return str(selection_row["uniprot_L"])
    raise ValueError(f"Unsupported chain role: {chain}")


def build_core3_negatome_control_pairs(
    viewer_selections: pl.DataFrame,
    selection: pl.DataFrame,
    cache_dir: Path,
) -> pl.DataFrame:
    selection_by_id = {str(row["id"]): row for row in selection.to_dicts()}

    rows: list[dict[str, str]] = []
    for viewer_row in viewer_selections.to_dicts():
        complex_id = str(viewer_row["complex_id"])
        chain = str(viewer_row["chain"])
        target_species = str(viewer_row["target_species"])

        selection_row = selection_by_id.get(complex_id)
        if selection_row is None:
            raise ValueError(f"Missing selection row for complex_id={complex_id}")

        source_uniprot = source_uniprot_for_chain(selection_row, chain)
        partner_spec = CURATED_NEGATIVE_PARTNERS.get(source_uniprot)
        if partner_spec is None:
            raise ValueError(
                f"No curated negative partner configured for source_uniprot={source_uniprot} "
                f"({complex_id}/{chain})"
            )

        negative_uniprot = partner_spec["negative_partner_uniprot"]
        negative_sequence = fetch_uniprot_sequence(negative_uniprot, cache_dir=cache_dir)

        rows.append(
            {
                "complex_id": complex_id,
                "chain": chain,
                "target_species": target_species,
                "source_uniprot": source_uniprot,
                "negative_partner_uniprot": negative_uniprot,
                "negative_partner_source": partner_spec["negative_partner_source"],
                "negative_partner_sequence": negative_sequence,
                "control_type": partner_spec["control_type"],
            }
        )

    if not rows:
        return pl.DataFrame({column: [] for column in NEGATOME_PAIR_COLUMNS})

    return pl.DataFrame(rows).unique(
        subset=["complex_id", "chain", "target_species", "negative_partner_uniprot"]
    )


def build_curated_ortholog_negatome_control_pairs(
    curated_candidates: pl.DataFrame,
    cache_dir: Path,
) -> pl.DataFrame:
    """Build NEGATOME-style rows for primary curated ortholog candidates.

    This extends the same source-protein negative partner curation used by the
    core3 mini-pilot to curated ortholog species that were added later, such as
    Brandt's bat PARP1.
    """
    primary_candidates = filter_primary_curated_ortholog_candidates(curated_candidates)

    rows: list[dict[str, str]] = []
    for candidate_row in primary_candidates.to_dicts():
        complex_id = str(candidate_row["complex_id"])
        chain = str(candidate_row["chain"])
        target_species = str(candidate_row["target_species"])
        source_uniprot = str(candidate_row["source_uniprot"])

        partner_spec = CURATED_NEGATIVE_PARTNERS.get(source_uniprot)
        if partner_spec is None:
            raise ValueError(
                f"No curated negative partner configured for source_uniprot={source_uniprot} "
                f"({complex_id}/{chain}/{target_species})"
            )

        negative_uniprot = partner_spec["negative_partner_uniprot"]
        negative_sequence = fetch_uniprot_sequence(negative_uniprot, cache_dir=cache_dir)

        rows.append(
            {
                "complex_id": complex_id,
                "chain": chain,
                "target_species": target_species,
                "source_uniprot": source_uniprot,
                "negative_partner_uniprot": negative_uniprot,
                "negative_partner_source": partner_spec["negative_partner_source"],
                "negative_partner_sequence": negative_sequence,
                "control_type": partner_spec["control_type"],
            }
        )

    if not rows:
        return pl.DataFrame({column: [] for column in NEGATOME_PAIR_COLUMNS})

    return pl.DataFrame(rows).unique(
        subset=["complex_id", "chain", "target_species", "negative_partner_uniprot"]
    )


def validate_curated_sequences(pairs: pl.DataFrame) -> None:
    validate_schema(pairs)
    invalid = pairs.filter(
        pl.col("negative_partner_sequence").is_null()
        | (pl.col("negative_partner_sequence").str.len_chars() == 0)
    )
    if invalid.height > 0:
        raise ValueError(f"Curated NEGATOME rows failed sequence validation: {invalid}")
