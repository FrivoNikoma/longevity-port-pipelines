from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import polars as pl

from longevity_port_pipelines.stages.negatome_curation import (
    build_core3_negatome_control_pairs,
    build_curated_ortholog_negatome_control_pairs,
    source_uniprot_for_chain,
)


def selection_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "id": ["8g57__A1_Q8N6T7--8g57__H1_P04908"],
            "uniprot_R": ["Q8N6T7"],
            "uniprot_L": ["P04908"],
        }
    )


def viewer_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["8g57__A1_Q8N6T7--8g57__H1_P04908"],
            "chain": ["ligand"],
            "target_species": ["naked_mole_rat"],
        }
    )


def curated_candidate_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["4xhu__A1_P09874--4xhu__B1_Q9UNS1"],
            "chain": ["receptor"],
            "target_species": ["brandts_bat"],
            "source_uniprot": ["P09874"],
            "source_species_taxid": [9606],
            "target_species_taxid": [109478],
            "target_accession": ["EPQ16369.1"],
            "target_accession_db": ["NCBI Protein"],
            "target_sequence": ["MFDGKVPHWY"],
            "target_sequence_length": [10],
            "curation_status": ["primary_candidate"],
            "evidence_source": ["manual_curated"],
            "curation_note": ["Brandt's bat PARP1 curated ortholog candidate."],
        }
    )


def test_source_uniprot_for_chain_maps_roles() -> None:
    row = selection_rows().to_dicts()[0]
    assert source_uniprot_for_chain(row, "receptor") == "Q8N6T7"
    assert source_uniprot_for_chain(row, "ligand") == "P04908"


@patch("longevity_port_pipelines.stages.negatome_curation.fetch_uniprot_sequence")
def test_build_core3_negatome_control_pairs_writes_curated_rows(
    fetch_sequence: object,
) -> None:
    fetch_sequence.return_value = "ACDEFGHIKLMNPQRSTVWY"  # type: ignore[attr-defined]

    pairs = build_core3_negatome_control_pairs(
        viewer_selections=viewer_rows(),
        selection=selection_rows(),
        cache_dir=Path("unused"),
    )

    assert pairs.height == 1
    row = pairs.row(0, named=True)
    assert row["source_uniprot"] == "P04908"
    assert row["negative_partner_uniprot"] == "P07437"
    assert row["negative_partner_sequence"] == "ACDEFGHIKLMNPQRSTVWY"


@patch("longevity_port_pipelines.stages.negatome_curation.fetch_uniprot_sequence")
def test_build_curated_ortholog_negatome_control_pairs_covers_primary_candidate(
    fetch_sequence: object,
) -> None:
    fetch_sequence.return_value = "MTELAGASSS"  # type: ignore[attr-defined]

    pairs = build_curated_ortholog_negatome_control_pairs(
        curated_candidates=curated_candidate_rows(),
        cache_dir=Path("unused"),
    )

    assert pairs.height == 1
    row = pairs.row(0, named=True)
    assert row["complex_id"] == "4xhu__A1_P09874--4xhu__B1_Q9UNS1"
    assert row["chain"] == "receptor"
    assert row["target_species"] == "brandts_bat"
    assert row["source_uniprot"] == "P09874"
    assert row["negative_partner_uniprot"] == "O60907"
    assert row["negative_partner_source"] == "negatome_database"
    assert row["control_type"] == "curated_negative"
    assert row["negative_partner_sequence"] == "MTELAGASSS"
