"""Tests for NEGATOME control loading and application."""

from pathlib import Path

import numpy as np
import polars as pl

from longevity_port_pipelines.models import EnrichmentResult
from longevity_port_pipelines.stages.embed import PerResidueEmbedding
from longevity_port_pipelines.stages.negatome_controls import (
    apply_negatome_control_to_result,
    build_negatome_pair_lookup,
    load_negatome_control_pairs,
    negative_partner_embedding_path,
    resolve_negatome_control_ratio,
)


def pair_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["c1"],
            "chain": ["receptor"],
            "target_species": ["naked_mole_rat"],
            "source_uniprot": ["P12345"],
            "negative_partner_uniprot": ["Q99999"],
            "negative_partner_source": ["curated_manual"],
            "negative_partner_sequence": ["ACDEFGHIK"],
            "control_type": ["curated_negative"],
        }
    )


def embeddings(sequence: str) -> PerResidueEmbedding:
    length = len(sequence)
    dim = 4
    values = np.arange(length * dim, dtype=np.float32).reshape(length, dim)
    return PerResidueEmbedding(
        complex_id="c1",
        chain="receptor",
        species_taxid=9606,
        model_name="test-model",
        sequence=sequence,
        embeddings=values,
    )


def test_build_negatome_pair_lookup() -> None:
    lookup = build_negatome_pair_lookup(pair_rows())
    assert ("c1", "receptor", "naked_mole_rat") in lookup
    assert lookup[("c1", "receptor", "naked_mole_rat")][0]["negative_partner_uniprot"] == "Q99999"


def test_load_negatome_control_pairs_from_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "negatome_control_pairs.csv"
    pair_rows().write_csv(csv_path)

    loaded = load_negatome_control_pairs(csv_path)
    assert loaded is not None
    assert loaded.height == 1


def test_resolve_negatome_control_ratio_uses_cached_partner_embedding(tmp_path: Path) -> None:
    interim_dir = tmp_path / "interim"
    model_name = "test-model"
    partner_path = negative_partner_embedding_path(interim_dir, model_name, "Q99999")
    partner_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(partner_path, np.ones((5, 4), dtype=np.float32))

    ratio = resolve_negatome_control_ratio(
        ref=embeddings("ACDEFGHIK"),
        orth=embeddings("ACDEFGHIK"),
        interface_residues=[1, 2],
        pair_rows=build_negatome_pair_lookup(pair_rows())[("c1", "receptor", "naked_mole_rat")],
        interim_dir=interim_dir,
        model_name=model_name,
        source_uniprot="P12345",
    )

    assert ratio is not None
    assert ratio > 0.0


def test_apply_negatome_control_to_result_populates_field(tmp_path: Path) -> None:
    interim_dir = tmp_path / "interim"
    model_name = "test-model"
    partner_path = negative_partner_embedding_path(interim_dir, model_name, "Q99999")
    partner_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(partner_path, np.ones((5, 4), dtype=np.float32))

    result = EnrichmentResult(
        complex_id="c1",
        model_name=model_name,
        source_species="human",
        target_species="naked_mole_rat",
        chain="receptor",
        interface_mean_delta=1.0,
        noninterface_mean_delta=0.5,
        enrichment_ratio=2.0,
        shuffled_control_ratio=1.0,
        mann_whitney_p=0.01,
        effect_size_cohens_d=1.2,
    )

    updated = apply_negatome_control_to_result(
        result,
        ref=embeddings("ACDEFGHIK"),
        orth=embeddings("ACDEFGHIK"),
        interface_residues=[1, 2],
        pair_lookup=build_negatome_pair_lookup(pair_rows()),
        interim_dir=interim_dir,
        source_uniprot="P12345",
    )

    assert updated.negatome_control_ratio is not None


def test_resolve_negatome_control_ratio_returns_none_without_embedding(tmp_path: Path) -> None:
    ratio = resolve_negatome_control_ratio(
        ref=embeddings("ACDEFGHIK"),
        orth=embeddings("ACDEFGHIK"),
        interface_residues=[1, 2],
        pair_rows=build_negatome_pair_lookup(pair_rows())[("c1", "receptor", "naked_mole_rat")],
        interim_dir=tmp_path / "interim",
        model_name="test-model",
    )

    assert ratio is None


def test_resolve_negatome_control_ratio_filters_source_uniprot(tmp_path: Path) -> None:
    interim_dir = tmp_path / "interim"
    model_name = "test-model"
    partner_path = negative_partner_embedding_path(interim_dir, model_name, "Q99999")
    partner_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(partner_path, np.ones((5, 4), dtype=np.float32))

    ratio = resolve_negatome_control_ratio(
        ref=embeddings("ACDEFGHIK"),
        orth=embeddings("ACDEFGHIK"),
        interface_residues=[1, 2],
        pair_rows=build_negatome_pair_lookup(pair_rows())[("c1", "receptor", "naked_mole_rat")],
        interim_dir=interim_dir,
        model_name=model_name,
        source_uniprot="WRONG",
    )

    assert ratio is None
