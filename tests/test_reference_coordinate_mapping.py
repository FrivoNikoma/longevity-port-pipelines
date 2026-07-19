"""Synthetic ground-truth tests for reusable residue coordinate mapping."""

from longevity_port_pipelines.stages.reference_coordinate_mapping import (
    align_reference_to_target,
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
