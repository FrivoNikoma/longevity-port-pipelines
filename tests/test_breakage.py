"""Tests for breakage taxonomy table logic."""

import polars as pl

from longevity_port_pipelines.stages.breakage_table import (
    _classify_partner,
    build_breakage_table,
)


def test_classify_partner_regulatory() -> None:
    assert _classify_partner("MAP2K1") == "functional"
    assert _classify_partner("UBE2D1") == "functional"


def test_classify_partner_functional() -> None:
    assert _classify_partner("TP53") == "functional"
    assert _classify_partner("FOXO3") == "functional"


def test_classify_partner_degradation_keywords() -> None:
    assert _classify_partner("ubiquitin") == "regulatory"
    assert _classify_partner("AUTOPHAGY_RELATED") == "regulatory"
    assert _classify_partner("caspase3") == "regulatory"


def test_build_breakage_table_structure() -> None:
    candidates = pl.DataFrame(
        {
            "gene_name": ["SIRT1", "TP53"],
            "uniprot_id": ["Q96EB6", "P04637"],
            "category": ["pro-longevity", "dna-repair"],
        }
    )
    interactome = pl.DataFrame(
        {
            "gene_name": ["SIRT1", "TP53"],
            "top_partners": ["FOXO3, PPARG, ubiquitin", "MDM2, BRCA1, caspase"],
        }
    )

    table = build_breakage_table(candidates, interactome)

    assert table.height > 0
    assert "desired_interaction_state" in table.columns
    assert "n_functional" in table.columns
    assert "n_regulatory" in table.columns

    sirt1_rows = table.filter(pl.col("protein") == "SIRT1")
    first = sirt1_rows.row(0, named=True)
    assert first["n_functional"] == 2  # FOXO3, PPARG
    assert first["n_regulatory"] == 1  # ubiquitin
    assert first["desired_interaction_state"] == ""


def test_build_breakage_table_covers_all_species() -> None:
    from longevity_port_pipelines.config import LONG_LIVED_SPECIES, SHORT_LIVED_SPECIES

    candidates = pl.DataFrame(
        {
            "gene_name": ["SIRT1"],
            "uniprot_id": ["Q96EB6"],
            "category": ["pro-longevity"],
        }
    )
    interactome = pl.DataFrame(
        {
            "gene_name": ["SIRT1"],
            "top_partners": ["FOXO3"],
        }
    )

    table = build_breakage_table(candidates, interactome)
    expected_species = len(LONG_LIVED_SPECIES) + len(SHORT_LIVED_SPECIES)
    assert table.height == expected_species
