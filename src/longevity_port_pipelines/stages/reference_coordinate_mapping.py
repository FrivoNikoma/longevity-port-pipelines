"""Reusable full-length reference-to-target residue coordinate mapping."""

from __future__ import annotations

from dataclasses import dataclass

import biotite.sequence as seq
import biotite.sequence.align as align


@dataclass(frozen=True)
class AlignedResiduePair:
    """One ungapped residue pair from a reference-to-target alignment."""

    reference_index: int
    target_index: int
    reference_residue: str
    target_residue: str

    @property
    def residue_identity_consistent(self) -> bool:
        """Return whether the aligned residues have the same one-letter code."""
        return self.reference_residue == self.target_residue


@dataclass(frozen=True)
class ReferenceTargetAlignment:
    """Auditable result of one deterministic reference-to-target alignment."""

    aligned_pairs: tuple[AlignedResiduePair, ...]
    trace_length: int
    optimal_alignment_count: int


def to_protein_sequence(sequence: str) -> seq.ProteinSequence:
    """Build a Biotite protein sequence, mapping unsupported symbols to ``X``."""
    try:
        return seq.ProteinSequence(sequence)
    except Exception:
        valid = set(seq.ProteinSequence.alphabet.get_symbols())
        return seq.ProteinSequence(
            "".join(residue if residue in valid else "X" for residue in sequence)
        )


def align_reference_to_target(
    reference_sequence: str,
    target_sequence: str,
) -> ReferenceTargetAlignment:
    """Map full-length reference indices to target indices with the generic policy.

    The policy intentionally matches the historical enrichment implementation:
    global BLOSUM62 alignment, affine gap penalties ``(-10, -1)``, free terminal
    gaps, and the first alignment returned when several optima exist.
    """
    reference = to_protein_sequence(reference_sequence)
    target = to_protein_sequence(target_sequence)
    matrix = align.SubstitutionMatrix.std_protein_matrix()
    alignments = align.align_optimal(
        reference,
        target,
        matrix,
        gap_penalty=(-10, -1),
        terminal_penalty=False,
    )
    if not alignments:
        raise ValueError("Biotite returned no reference-to-target alignment")

    trace = alignments[0].trace
    pairs: list[AlignedResiduePair] = []
    for reference_index, target_index in trace:
        if reference_index == -1 or target_index == -1:
            continue
        ref_index = int(reference_index)
        tgt_index = int(target_index)
        pairs.append(
            AlignedResiduePair(
                reference_index=ref_index,
                target_index=tgt_index,
                reference_residue=reference_sequence[ref_index],
                target_residue=target_sequence[tgt_index],
            )
        )

    return ReferenceTargetAlignment(
        aligned_pairs=tuple(pairs),
        trace_length=int(trace.shape[0]),
        optimal_alignment_count=len(alignments),
    )
