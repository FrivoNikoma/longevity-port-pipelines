"""Synthetic ground-truth tests for reusable residue coordinate mapping."""

from longevity_port_pipelines.stages.reference_coordinate_mapping import (
    AlignmentPolicy,
    align_reference_to_target,
    enumerate_reference_to_target_alignments,
)


def test_reference_coordinate_mapping_tracks_internal_deletion() -> None:
    alignment = align_reference_to_target(
        reference_sequence="ACDEFGHIK",
        target_sequence="ACDFGHIK",
    )
    by_reference = {pair.reference_index: pair.target_index for pair in alignment.aligned_pairs}

    assert by_reference[0] == 0
    assert 3 not in by_reference
    assert by_reference[4] == 3
    assert by_reference[8] == 7
    assert alignment.trace_length == 9


def test_reference_coordinate_mapping_records_substitution_identity() -> None:
    alignment = align_reference_to_target(
        reference_sequence="ACDEFG",
        target_sequence="ACNEFG",
    )
    pair = next(pair for pair in alignment.aligned_pairs if pair.reference_index == 2)

    assert pair.target_index == 2
    assert pair.reference_residue == "D"
    assert pair.target_residue == "N"
    assert pair.residue_identity_consistent is False


def test_alignment_enumeration_records_explicit_unique_traces() -> None:
    alignments = enumerate_reference_to_target_alignments(
        reference_sequence="AAAA",
        target_sequence="AAA",
    )

    assert len(alignments) > 1
    assert [alignment.optimal_alignment_index for alignment in alignments] == list(
        range(len(alignments))
    )
    assert {alignment.optimal_alignment_count for alignment in alignments} == {len(alignments)}
    assert len({alignment.trace_sha256 for alignment in alignments}) == len(alignments)
    assert all(alignment.trace for alignment in alignments)
    assert align_reference_to_target("AAAA", "AAA") == alignments[0]


def test_alignment_enumeration_rejects_unnamed_or_nonnegative_policy() -> None:
    for policy in (
        AlignmentPolicy("", -10, -1, False),
        AlignmentPolicy("invalid", 0, -1, False),
        AlignmentPolicy("invalid", -10, 0, False),
    ):
        try:
            enumerate_reference_to_target_alignments("ACD", "ACD", policy)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid alignment policy was accepted")
