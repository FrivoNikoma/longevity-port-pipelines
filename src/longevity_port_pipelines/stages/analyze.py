"""Stage 6: Enrichment analysis — interface vs non-interface embedding deltas."""

from __future__ import annotations

import logging

import biotite.sequence as seq
import biotite.sequence.align as align
import numpy as np
from scipy import stats

from longevity_port_pipelines.models import EnrichmentResult
from longevity_port_pipelines.stages.embed import PerResidueEmbedding

logger = logging.getLogger(__name__)


def _to_protein_sequence(s: str) -> seq.ProteinSequence:
    """Build a biotite ProteinSequence, mapping unparseable symbols to 'X'."""
    try:
        return seq.ProteinSequence(s)
    except Exception:
        valid = set(seq.ProteinSequence.alphabet.get_symbols())
        return seq.ProteinSequence("".join(c if c in valid else "X" for c in s))


def align_and_compute_deltas(
    ref: PerResidueEmbedding,
    orth: PerResidueEmbedding,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute per-residue L2 embedding deltas between aligned positions.

    Uses biotite global pairwise alignment (BLOSUM62) to map residues between
    reference and ortholog, then computes L2 distance at each aligned position.

    Returns (deltas, aligned_ref_positions) — both shape (n_aligned,).
    """
    s_ref = _to_protein_sequence(ref.sequence)
    s_orth = _to_protein_sequence(orth.sequence)

    matrix = align.SubstitutionMatrix.std_protein_matrix()
    alignments = align.align_optimal(
        s_ref, s_orth, matrix, gap_penalty=(-10, -1), terminal_penalty=False
    )
    trace = alignments[0].trace  # shape (aln_len, 2); -1 marks gaps

    deltas = []
    aligned_ref_positions = []
    for r_idx, o_idx in trace:
        if r_idx == -1 or o_idx == -1:
            continue
        if r_idx >= ref.embeddings.shape[0] or o_idx >= orth.embeddings.shape[0]:
            continue

        delta = np.linalg.norm(ref.embeddings[r_idx] - orth.embeddings[o_idx])
        deltas.append(float(delta))
        aligned_ref_positions.append(int(r_idx))

    return np.array(deltas), np.array(aligned_ref_positions)


def compute_enrichment(
    deltas: np.ndarray,
    aligned_positions: np.ndarray,
    interface_residues: list[int],
) -> tuple[float, float, float]:
    """Compute enrichment ratio of embedding shift at interface vs non-interface.

    Returns (interface_mean, noninterface_mean, enrichment_ratio).
    """
    interface_set = set(interface_residues)
    is_interface = np.array([pos in interface_set for pos in aligned_positions])

    if not np.any(is_interface) or not np.any(~is_interface):
        logger.warning("Cannot compute enrichment: empty interface or non-interface set")
        return 0.0, 0.0, 1.0

    interface_deltas = deltas[is_interface]
    noninterface_deltas = deltas[~is_interface]

    interface_mean = float(np.mean(interface_deltas))
    noninterface_mean = float(np.mean(noninterface_deltas))
    enrichment = interface_mean / noninterface_mean if noninterface_mean > 0 else float("inf")

    return interface_mean, noninterface_mean, enrichment


def shuffled_control(
    deltas: np.ndarray,
    n_interface: int,
    n_permutations: int = 1000,
) -> float:
    """Shuffled random mask control.

    Randomly assign n_interface positions as "interface" and compute the
    mean enrichment ratio across permutations.
    """
    rng = np.random.default_rng(seed=42)
    ratios = []

    for _ in range(n_permutations):
        perm = rng.permutation(len(deltas))
        fake_interface = deltas[perm[:n_interface]]
        fake_noninterface = deltas[perm[n_interface:]]

        if len(fake_noninterface) == 0:
            continue

        mean_iface = float(np.mean(fake_interface))
        mean_noniface = float(np.mean(fake_noninterface))
        if mean_noniface > 0:
            ratios.append(mean_iface / mean_noniface)

    return float(np.mean(ratios)) if ratios else 1.0


def mann_whitney_test(
    deltas: np.ndarray,
    aligned_positions: np.ndarray,
    interface_residues: list[int],
) -> tuple[float, float]:
    """Mann-Whitney U test + Cohen's d for interface vs non-interface deltas.

    Returns (p_value, cohens_d).
    """
    interface_set = set(interface_residues)
    is_interface = np.array([pos in interface_set for pos in aligned_positions])

    interface_deltas = deltas[is_interface]
    noninterface_deltas = deltas[~is_interface]

    if len(interface_deltas) < 2 or len(noninterface_deltas) < 2:
        return 1.0, 0.0

    stat_result = stats.mannwhitneyu(
        interface_deltas, noninterface_deltas, alternative="greater"
    )
    p_value = float(stat_result.pvalue)

    pooled_std = float(np.sqrt(
        (np.var(interface_deltas) * (len(interface_deltas) - 1)
         + np.var(noninterface_deltas) * (len(noninterface_deltas) - 1))
        / (len(interface_deltas) + len(noninterface_deltas) - 2)
    ))
    cohens_d = (
        (float(np.mean(interface_deltas)) - float(np.mean(noninterface_deltas))) / pooled_std
        if pooled_std > 0 else 0.0
    )

    return p_value, cohens_d


def analyze_pair(
    ref: PerResidueEmbedding,
    orth: PerResidueEmbedding,
    interface_residues: list[int],
    source_species_name: str,
    target_species_name: str,
    n_permutations: int = 1000,
    negatome_enrichment: float | None = None,
) -> EnrichmentResult:
    """Full analysis for one reference-ortholog pair."""
    deltas, aligned_positions = align_and_compute_deltas(ref, orth)
    interface_mean, noninterface_mean, enrichment = compute_enrichment(
        deltas, aligned_positions, interface_residues
    )
    shuffled = shuffled_control(deltas, len(interface_residues), n_permutations)
    p_value, cohens_d = mann_whitney_test(deltas, aligned_positions, interface_residues)

    return EnrichmentResult(
        complex_id=ref.complex_id,
        model_name=ref.model_name,
        source_species=source_species_name,
        target_species=target_species_name,
        chain=ref.chain,
        interface_mean_delta=interface_mean,
        noninterface_mean_delta=noninterface_mean,
        enrichment_ratio=enrichment,
        shuffled_control_ratio=shuffled,
        negatome_control_ratio=negatome_enrichment,
        mann_whitney_p=p_value,
        effect_size_cohens_d=cohens_d,
        is_predicted_structure=orth.is_predicted_structure,
    )
