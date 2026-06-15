"""Tests for NEGATOME-style control enrichment."""

import numpy as np

from longevity_port_pipelines.stages.embed import PerResidueEmbedding
from longevity_port_pipelines.stages.negatome_analyze import compute_negatome_control_ratio


def _embedding(
    sequence: str,
    pattern: np.ndarray,
    scale: float = 1.0,
) -> PerResidueEmbedding:
    length = len(sequence)
    dim = pattern.shape[0]
    embeddings = np.tile(pattern * scale, (length, 1)) + np.linspace(
        0.0, 0.01, length * dim, dtype=np.float64
    ).reshape(length, dim)
    return PerResidueEmbedding(
        complex_id="c1",
        chain="receptor",
        species_taxid=9606,
        model_name="test-model",
        sequence=sequence,
        embeddings=embeddings.astype(np.float32),
    )


def test_negatome_control_ratio_near_one_for_uniform_coupling_shift() -> None:
    sequence = "ACDEFGHIKLMNPQRSTVWY"
    ref = _embedding(sequence, np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    orth = _embedding(
        sequence,
        np.array([0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        scale=1.05,
    )
    negative_partner = np.tile(np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]), (12, 1))

    ratio = compute_negatome_control_ratio(
        ref=ref,
        orth=orth,
        interface_residues=[2, 3, 4],
        negative_partner_embeddings=negative_partner.astype(np.float32),
    )

    assert 0.7 < ratio < 1.3


def test_negatome_control_ratio_higher_when_interface_coupling_shifts() -> None:
    sequence = "ACDEFGHIKLMNPQRSTVWY"
    dim = 8
    partner_direction = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float64)

    ref_embeddings = np.zeros((len(sequence), dim), dtype=np.float32)
    orth_embeddings = np.zeros((len(sequence), dim), dtype=np.float32)
    for index in range(len(sequence)):
        base = np.random.default_rng(index).normal(size=dim)
        ref_embeddings[index] = base
        orth_embeddings[index] = base.copy()

    for index in [2, 3, 4]:
        ref_embeddings[index] += partner_direction
        orth_embeddings[index] += partner_direction * 3.0

    ref = PerResidueEmbedding(
        complex_id="c1",
        chain="receptor",
        species_taxid=9606,
        model_name="test-model",
        sequence=sequence,
        embeddings=ref_embeddings,
    )
    orth = PerResidueEmbedding(
        complex_id="c1",
        chain="receptor",
        species_taxid=10181,
        model_name="test-model",
        sequence=sequence,
        embeddings=orth_embeddings,
    )
    negative_partner = np.tile(partner_direction, (10, 1)).astype(np.float32)

    interface_ratio = compute_negatome_control_ratio(
        ref=ref,
        orth=orth,
        interface_residues=[2, 3, 4],
        negative_partner_embeddings=negative_partner,
    )
    background_ratio = compute_negatome_control_ratio(
        ref=ref,
        orth=orth,
        interface_residues=[10, 11, 12],
        negative_partner_embeddings=negative_partner,
    )

    assert interface_ratio > background_ratio
