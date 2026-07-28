"""NEGATOME-style negative control enrichment for interface embedding analysis."""

from __future__ import annotations

import numpy as np

from longevity_port_pipelines.stages.analyze import compute_enrichment
from longevity_port_pipelines.stages.embed import PerResidueEmbedding
from longevity_port_pipelines.stages.reference_coordinate_mapping import (
    align_reference_to_target,
)


def _unit_vector(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm <= 0.0:
        return vector
    return vector / norm


def _mean_partner_pool(partner_embeddings: np.ndarray) -> np.ndarray:
    if partner_embeddings.ndim != 2:
        raise ValueError(
            f"Expected negative-partner embeddings of shape (L, D), got {partner_embeddings.shape}"
        )
    return _unit_vector(partner_embeddings.mean(axis=0))


def _coupling_scores(
    embeddings: np.ndarray,
    aligned_positions: np.ndarray,
    partner_pool: np.ndarray,
) -> np.ndarray:
    partner_unit = _unit_vector(partner_pool)
    scores: list[float] = []

    for position in aligned_positions:
        residue_embedding = embeddings[int(position)]
        scores.append(float(np.dot(_unit_vector(residue_embedding), partner_unit)))

    return np.asarray(scores, dtype=np.float64)


def compute_negatome_control_ratio(
    ref: PerResidueEmbedding,
    orth: PerResidueEmbedding,
    interface_residues: list[int],
    negative_partner_embeddings: np.ndarray,
) -> float:
    """Compute a NEGATOME-style control enrichment ratio.

    Uses the same structural interface mask as the primary enrichment analysis, but
    measures cross-species change in embedding coupling to a curated non-interacting
    partner rather than per-residue L2 self-shift.

    A true interface-specific ortholog signal should exceed this control when
    ``enrichment_ratio / negatome_control_ratio`` is meaningfully above 1.
    """
    if not interface_residues:
        return 1.0

    # Align reference to ortholog and keep BOTH coordinate frames: reference-frame
    # indices address the reference embedding, target-frame indices address the
    # ortholog embedding. Indexing the (possibly shorter) ortholog array with
    # reference positions previously raised an IndexError.
    alignment = align_reference_to_target(ref.sequence, orth.sequence)
    ref_positions_list: list[int] = []
    orth_positions_list: list[int] = []
    for pair in alignment.aligned_pairs:
        if (
            0 <= pair.reference_index < ref.embeddings.shape[0]
            and 0 <= pair.target_index < orth.embeddings.shape[0]
        ):
            ref_positions_list.append(pair.reference_index)
            orth_positions_list.append(pair.target_index)

    if not ref_positions_list:
        return 1.0

    ref_positions = np.asarray(ref_positions_list, dtype=np.int64)
    orth_positions = np.asarray(orth_positions_list, dtype=np.int64)

    partner_pool = _mean_partner_pool(negative_partner_embeddings)
    ref_coupling = _coupling_scores(ref.embeddings, ref_positions, partner_pool)
    orth_coupling = _coupling_scores(orth.embeddings, orth_positions, partner_pool)
    coupling_deltas = np.abs(ref_coupling - orth_coupling)

    # Interface membership is defined in reference coordinates.
    _, _, enrichment = compute_enrichment(
        coupling_deltas,
        ref_positions,
        interface_residues,
    )
    return enrichment
