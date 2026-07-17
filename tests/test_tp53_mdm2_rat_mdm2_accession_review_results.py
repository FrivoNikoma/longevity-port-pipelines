import polars as pl

from longevity_port_pipelines.stages import (
    tp53_mdm2_rat_mdm2_accession_review_results as rat_review,
)


def row_for(accession: str) -> dict[str, object]:
    rows = rat_review.read_results().filter(pl.col("candidate_accession") == accession)
    assert rows.height == 1
    return rows.row(0, named=True)


def test_rat_review_validates() -> None:
    rows = rat_review.read_results()
    rat_review.validate_results(rows)
    assert rows.height == 4


def test_refseq_is_anchor_not_canonical_accession() -> None:
    row = row_for("NP_001426446.1")
    assert row["source_record_status"] == "validated"
    assert row["sequence_length"] == "434"
    assert row["candidate_disposition"] == ("evidence_anchor_not_canonical_project_accession")
    assert row["canonical_project_accession_accepted"] == "false"


def test_a0_is_longer_nonexact_subsequence_container() -> None:
    row = row_for("A0A0G2JVC1")
    assert row["sequence_length"] == "483"
    assert row["length_delta_vs_reference"] == "49"
    assert row["exact_match_to_reference"] == "false"
    assert row["reference_exact_subsequence_of_candidate"] == "true"
    assert row["candidate_disposition"] == ("not_exact_accession_level_match")


def test_a6_is_excluded_inactive_accession() -> None:
    row = row_for("A6IGT1")
    assert row["source_record_status"] == "inactive"
    assert row["candidate_disposition"] == ("excluded_inactive_accession")


def test_d3_is_distinct_nonexact_sequence() -> None:
    row = row_for("D3ZVH5")
    assert row["sequence_length"] == "458"
    assert row["reference_exact_subsequence_of_candidate"] == "false"
    assert row["candidate_exact_subsequence_of_reference"] == "false"
    assert row["candidate_disposition"] == ("distinct_unreviewed_sequence_not_exact_match")


def test_no_candidate_is_accepted_and_boundaries_are_closed() -> None:
    rows = rat_review.read_results()
    assert set(rows["blocker_code"].to_list()) == {"no_unambiguous_canonical_rat_mdm2_sequence"}
    for row in rows.iter_rows(named=True):
        for field in rat_review.FALSE_FIELDS:
            assert str(row[field]).lower() == "false"
