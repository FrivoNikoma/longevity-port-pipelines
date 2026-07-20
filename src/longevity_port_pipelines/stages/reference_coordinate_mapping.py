"""Reusable full-length reference-to-target residue coordinate mapping."""

from __future__ import annotations

import hashlib
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
    trace: tuple[tuple[int, int], ...] = ()
    policy_id: str = "canonical_free_terminal"
    optimal_alignment_index: int = 0
    trace_sha256: str = ""


@dataclass(frozen=True)
class AlignmentPolicy:
    """Named Biotite alignment policy used by coordinate sensitivity audits."""

    policy_id: str
    gap_open: int
    gap_extend: int
    terminal_penalty: bool

    @property
    def gap_penalty(self) -> tuple[int, int]:
        """Return the affine gap penalty in Biotite's expected form."""
        return self.gap_open, self.gap_extend


DEFAULT_ALIGNMENT_POLICY = AlignmentPolicy(
    policy_id="canonical_free_terminal",
    gap_open=-10,
    gap_extend=-1,
    terminal_penalty=False,
)


def to_protein_sequence(sequence: str) -> seq.ProteinSequence:
    """Build a Biotite protein sequence, mapping unsupported symbols to ``X``."""
    try:
        return seq.ProteinSequence(sequence)
    except Exception:
        valid = set(seq.ProteinSequence.alphabet.get_symbols())
        return seq.ProteinSequence(
            "".join(residue if residue in valid else "X" for residue in sequence)
        )


def _trace_sha256(trace: tuple[tuple[int, int], ...]) -> str:
    """Return a platform-independent identity for one complete alignment trace."""
    canonical = "".join(
        f"{reference_index},{target_index}\n" for reference_index, target_index in trace
    )
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def enumerate_reference_to_target_alignments(
    reference_sequence: str,
    target_sequence: str,
    policy: AlignmentPolicy = DEFAULT_ALIGNMENT_POLICY,
) -> tuple[ReferenceTargetAlignment, ...]:
    """Enumerate every optimal trace for one explicit alignment policy.

    Returning the complete trace set lets a sensitivity runner compute a metric
    from the exact alignment it audited.  Callers that need historical behavior
    should continue to use :func:`align_reference_to_target`, which selects the
    first canonical trace.
    """
    if not policy.policy_id.strip():
        raise ValueError("Alignment policy_id must be non-empty")
    if policy.gap_open >= 0 or policy.gap_extend >= 0:
        raise ValueError("Alignment gap penalties must be negative")

    reference = to_protein_sequence(reference_sequence)
    target = to_protein_sequence(target_sequence)
    matrix = align.SubstitutionMatrix.std_protein_matrix()
    optimal = align.align_optimal(
        reference,
        target,
        matrix,
        gap_penalty=policy.gap_penalty,
        terminal_penalty=policy.terminal_penalty,
    )
    if not optimal:
        raise ValueError("Biotite returned no reference-to-target alignment")

    results: list[ReferenceTargetAlignment] = []
    for optimal_index, alignment_result in enumerate(optimal):
        raw_trace = tuple(
            (int(reference_index), int(target_index))
            for reference_index, target_index in alignment_result.trace
        )
        pairs: list[AlignedResiduePair] = []
        for reference_index, target_index in raw_trace:
            if reference_index == -1 or target_index == -1:
                continue
            pairs.append(
                AlignedResiduePair(
                    reference_index=reference_index,
                    target_index=target_index,
                    reference_residue=reference_sequence[reference_index],
                    target_residue=target_sequence[target_index],
                )
            )

        results.append(
            ReferenceTargetAlignment(
                aligned_pairs=tuple(pairs),
                trace_length=len(raw_trace),
                optimal_alignment_count=len(optimal),
                trace=raw_trace,
                policy_id=policy.policy_id,
                optimal_alignment_index=optimal_index,
                trace_sha256=_trace_sha256(raw_trace),
            )
        )

    hashes = [result.trace_sha256 for result in results]
    if len(set(hashes)) != len(hashes):
        raise ValueError("Biotite returned duplicate optimal alignment traces")
    return tuple(results)


def align_reference_to_target(
    reference_sequence: str,
    target_sequence: str,
) -> ReferenceTargetAlignment:
    """Map full-length reference indices to target indices with the generic policy.

    The policy intentionally matches the historical enrichment implementation:
    global BLOSUM62 alignment, affine gap penalties ``(-10, -1)``, free terminal
    gaps, and the first alignment returned when several optima exist.
    """
    return enumerate_reference_to_target_alignments(
        reference_sequence,
        target_sequence,
        DEFAULT_ALIGNMENT_POLICY,
    )[0]
