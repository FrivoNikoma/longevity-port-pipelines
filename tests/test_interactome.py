"""Tests for interactome summarisation and UniProt annotation parsing."""

import polars as pl

from longevity_port_pipelines.stages.interactome import (
    parse_uniprot_annotations,
    summarise_interactome,
)


def test_summarise_interactome_partner_count() -> None:
    interactions = pl.DataFrame(
        {
            "source_genesymbol": ["SIRT1", "SIRT1", "FOXO3"],
            "target_genesymbol": ["FOXO3", "PPARG", "SIRT1"],
            "sources": ["STRING;BioGRID", "STRING", "STRING;BioGRID"],
            "is_directed": [1, 0, 1],
            "is_stimulation": [1, 0, 0],
            "is_inhibition": [0, 0, 0],
        }
    )

    summary = summarise_interactome(
        interactions.lazy(),
        candidate_genes=["SIRT1", "FOXO3"],
        hub_threshold=5,
    )

    sirt1 = summary.filter(pl.col("gene_name") == "SIRT1").row(0, named=True)
    assert sirt1["n_partners"] == 2  # FOXO3, PPARG
    assert sirt1["is_hub"] is False  # 2 < threshold 5

    foxo3 = summary.filter(pl.col("gene_name") == "FOXO3").row(0, named=True)
    assert foxo3["n_partners"] == 1  # SIRT1


def test_summarise_interactome_hub_detection() -> None:
    interactions = pl.DataFrame(
        {
            "source_genesymbol": ["MTOR"] * 20,
            "target_genesymbol": [f"PARTNER_{i}" for i in range(20)],
            "sources": ["STRING"] * 20,
            "is_directed": [0] * 20,
            "is_stimulation": [0] * 20,
            "is_inhibition": [0] * 20,
        }
    )

    summary = summarise_interactome(
        interactions.lazy(),
        candidate_genes=["MTOR"],
        hub_threshold=15,
    )

    mtor = summary.row(0, named=True)
    assert mtor["is_hub"] is True
    assert mtor["n_partners"] == 20


def test_parse_uniprot_annotations_membrane_protein() -> None:
    data = {
        "sequence": {"molWeight": 45000},
        "comments": [
            {
                "commentType": "SUBCELLULAR LOCATION",
                "subcellularLocations": [
                    {"location": {"value": "Cell membrane"}},
                ],
            }
        ],
        "features": [],
        "keywords": [{"name": "Kinase"}, {"name": "Transferase"}],
    }

    annots = parse_uniprot_annotations(data)
    assert annots["is_membrane"] is True
    assert annots["mass_da"] == 45000
    assert annots["size_kda"] == 45.0
    assert annots["has_glycosylation"] is False
    assert "Kinase" in annots["keywords"]


def test_parse_uniprot_annotations_glycoprotein() -> None:
    data = {
        "sequence": {"molWeight": 80000},
        "comments": [],
        "features": [{"type": "Glycosylation", "description": "N-linked"}],
        "keywords": [],
    }

    annots = parse_uniprot_annotations(data)
    assert annots["has_glycosylation"] is True
    assert annots["is_membrane"] is False
    assert annots["size_kda"] == 80.0


def test_parse_uniprot_annotations_empty() -> None:
    annots = parse_uniprot_annotations({})
    assert annots.get("is_membrane") is False
    assert annots.get("has_glycosylation") is False
    assert "mass_da" not in annots
