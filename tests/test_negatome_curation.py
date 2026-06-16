from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import polars as pl

from longevity_port_pipelines.stages.negatome_curation import (
    build_core3_negatome_control_pairs,
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
