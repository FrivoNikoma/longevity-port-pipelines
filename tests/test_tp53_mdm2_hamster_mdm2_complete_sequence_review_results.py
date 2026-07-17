import polars as pl

from longevity_port_pipelines.stages import (
    tp53_mdm2_hamster_mdm2_complete_sequence_review_results as review,
)


def row_for_accession(
    rows: pl.DataFrame,
    accession: str,
) -> dict[str, object]:
    selected = rows.filter(pl.col("candidate_accession") == accession)
    assert selected.height == 1
    return selected.row(0, named=True)


def test_hamster_review_results_validate() -> None:
    rows = review.read_results()
    review.validate_results(rows)
    assert rows.height == 20


def test_complete_sequence_group_is_single_and_corroborated() -> None:
    rows = review.read_results()
    selected = rows.filter(pl.col("sequence_group_accepted") == "true")
    assert set(selected["candidate_accession"].to_list()) == {"A0ABM2YB85", "XP_040610761.1"}
    assert selected["sequence_sha256"].n_unique() == 1
    assert selected["sequence_length"].to_list() == [
        "510",
        "510",
    ]
    assert set(selected["source_gene_id"].to_list()) == {"101833011"}


def test_a0abm2yb85_is_primary_project_accession() -> None:
    row = row_for_accession(
        review.read_results(),
        "A0ABM2YB85",
    )
    assert row["candidate_disposition"] == (
        "selected_complete_sequence_group_primary_project_accession"
    )
    assert row["project_accession_accepted"] == "true"
    assert row["sequence_group_accepted"] == "true"
    assert row["strict_panel_row_allowed_after_decision"] == "true"
    assert row["canonical_biological_isoform_claimed"] == "false"


def test_refseq_corroborates_selected_sequence_group() -> None:
    row = row_for_accession(
        review.read_results(),
        "XP_040610761.1",
    )
    assert row["candidate_disposition"] == ("selected_complete_sequence_group_corroborating_refseq")
    assert row["sequence_group_accepted"] == "true"
    assert row["project_accession_accepted"] == "false"


def test_q60524_remains_distinct_fragment_anchor() -> None:
    rows = review.read_results()
    q60524 = row_for_accession(rows, "Q60524")
    primary = row_for_accession(
        rows,
        "A0ABM2YB85",
    )
    assert q60524["sequence_length"] == "466"
    assert q60524["sequence_status"] == ("fragment_non_terminal_positions_1,466")
    assert q60524["candidate_disposition"] == ("reviewed_fragment_evidence_anchor_not_selected")
    assert primary["exact_match_to_q60524"] == "false"
    assert primary["q60524_exact_subsequence_of_candidate"] == "false"


def test_identity_failures_are_not_admitted() -> None:
    rows = review.read_results()
    excluded = rows.filter(pl.col("identity_status") == "fail")
    assert excluded.height == 16
    assert set(excluded["strict_panel_row_allowed_after_decision"].to_list()) == {"false"}
    assert set(excluded["sequence_group_accepted"].to_list()) == {"false"}


def test_review_boundaries_remain_closed() -> None:
    for row in review.read_results().iter_rows(named=True):
        for field in review.FALSE_BOUNDARY_FIELDS:
            assert row[field] == "false"
