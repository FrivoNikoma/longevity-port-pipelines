"""Integration test for the full analysis pipeline with synthetic embeddings.

Constructs PerResidueEmbedding objects with a known ground truth: interface
residues get a large embedding shift, non-interface residues get a small one.
The enrichment analysis must detect this signal.
"""

import numpy as np

from longevity_port_pipelines.stages.analyze import (
    align_and_compute_deltas,
    analyze_pair,
    compute_enrichment,
)
from longevity_port_pipelines.stages.embed import PerResidueEmbedding


def _make_embedding(
    sequence: str,
    embeddings: np.ndarray,
    complex_id: str = "test_001",
    chain: str = "receptor",
    taxid: int = 9606,
) -> PerResidueEmbedding:
    return PerResidueEmbedding(
        complex_id=complex_id,
        chain=chain,
        species_taxid=taxid,
        model_name="esmc_600m",
        sequence=sequence,
        embeddings=embeddings,
    )


def test_align_and_compute_deltas_identical_sequences() -> None:
    rng = np.random.default_rng(42)
    seq = "MKTLVGAAQRS"
    ref_emb = rng.normal(size=(len(seq), 64)).astype(np.float32)
    orth_emb = ref_emb + rng.normal(scale=0.1, size=ref_emb.shape).astype(np.float32)

    ref = _make_embedding(seq, ref_emb, taxid=9606)
    orth = _make_embedding(seq, orth_emb, taxid=10181)

    deltas, positions = align_and_compute_deltas(ref, orth)
    assert len(deltas) == len(seq)
    assert np.all(positions == np.arange(len(seq)))
    assert np.all(deltas > 0)


def test_align_and_compute_deltas_with_insertion() -> None:
    rng = np.random.default_rng(42)
    ref_seq = "MKTLVGAA"
    orth_seq = "MKTXXLVGAA"  # 2-residue insertion
    ref_emb = rng.normal(size=(len(ref_seq), 32)).astype(np.float32)
    orth_emb = rng.normal(size=(len(orth_seq), 32)).astype(np.float32)

    ref = _make_embedding(ref_seq, ref_emb)
    orth = _make_embedding(orth_seq, orth_emb)

    deltas, positions = align_and_compute_deltas(ref, orth)
    assert len(deltas) <= len(ref_seq)
    assert len(deltas) == len(positions)


def test_analyze_pair_detects_interface_signal() -> None:
    """Core scientific assertion: when interface residues shift more than
    non-interface residues, analyze_pair must report enrichment > 1 and
    beat the shuffled control."""
    rng = np.random.default_rng(123)
    seq = "A" * 100
    dim = 64
    interface_residues = list(range(20))

    ref_emb = rng.normal(size=(100, dim)).astype(np.float32)
    orth_emb = ref_emb.copy()
    # large shift at interface positions
    orth_emb[interface_residues] += rng.normal(loc=3.0, scale=0.2, size=(20, dim)).astype(np.float32)
    # small shift everywhere else
    orth_emb[20:] += rng.normal(loc=0.1, scale=0.05, size=(80, dim)).astype(np.float32)

    ref = _make_embedding(seq, ref_emb, taxid=9606)
    orth = _make_embedding(seq, orth_emb, taxid=10181)

    result = analyze_pair(
        ref, orth, interface_residues,
        source_species_name="human",
        target_species_name="naked_mole_rat",
        n_permutations=500,
    )

    assert result.enrichment_ratio > 1.5
    assert result.enrichment_ratio > result.shuffled_control_ratio
    assert result.mann_whitney_p < 0.01
    assert result.effect_size_cohens_d > 1.0


def test_analyze_pair_no_signal_when_uniform_shift() -> None:
    """When the shift is uniform across all residues, enrichment should be ~1."""
    rng = np.random.default_rng(456)
    seq = "A" * 80
    dim = 64
    interface_residues = list(range(20))

    ref_emb = rng.normal(size=(80, dim)).astype(np.float32)
    orth_emb = ref_emb + rng.normal(loc=0.5, scale=0.05, size=(80, dim)).astype(np.float32)

    ref = _make_embedding(seq, ref_emb, taxid=9606)
    orth = _make_embedding(seq, orth_emb, taxid=10181)

    result = analyze_pair(
        ref, orth, interface_residues,
        source_species_name="human",
        target_species_name="naked_mole_rat",
        n_permutations=500,
    )

    assert 0.8 < result.enrichment_ratio < 1.2
    assert result.mann_whitney_p > 0.05


def test_compute_enrichment_interface_at_boundary() -> None:
    """Interface residues at the start and end of the sequence."""
    deltas = np.array([0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.8])
    positions = np.arange(8)
    interface = [0, 7]

    iface_mean, noniface_mean, ratio = compute_enrichment(deltas, positions, interface)
    assert iface_mean == (0.9 + 0.8) / 2
    assert ratio > 5.0
