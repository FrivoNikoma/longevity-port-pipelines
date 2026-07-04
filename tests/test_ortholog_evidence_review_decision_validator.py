from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import ortholog_evidence_review_decision as review


def committed_rows() -> pl.DataFrame:
    rows = review.read_review_decision_rows()
    assert rows.height == 0
    return rows


def valid_review_row() -> dict[str, str]:
    row = {column: "value" for column in review.REQUIRED_COLUMNS}
    row.update(
        {
            "candidate_set": "tp53_mdm2_elephant",
            "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
            "review_source_table": "data/input/ortholog_evidence_intake.csv",
            "review_source_row_index": "5",
            "evidence_source_database": "UniProtKB TrEMBL",
            "evidence_source_accession": "G3SX30",
            "target_sequence_length": "492",
            "reviewed_sequence_length": "492",
            "review_source_status_before_review": "evidence_ready_for_review_decision",
            "review_source_decision_before_review": "evidence_ready_for_review_decision",
            "review_decision": "accepted_for_planning_after_review",
            "downstream_block_status_after_review": ("reviewed_for_planning_still_policy_blocked"),
            "allowed_next_action_after_review": (
                "consider_later_explicit_gate4_gate5_policy_update"
            ),
            "claim_policy_after_review": "no_biological_claims_until_validation",
            "claim_status_after_review": "repair_worklist",
            "forbidden_actions_after_review": "; ".join(sorted(review.RUNTIME_SIDE_EFFECTS)),
        }
    )
    return row


def test_read_review_decision_rows_loads_header_only_scaffold() -> None:
    rows = committed_rows()
    assert tuple(rows.columns) == review.REQUIRED_COLUMNS


def test_validate_review_decision_rows_accepts_header_only_scaffold() -> None:
    rows = committed_rows()
    review.validate_review_decision_rows(rows)


def test_review_decision_helpers_return_empty_frames_for_scaffold() -> None:
    rows = committed_rows()
    assert review.find_duplicate_review_decision_keys(rows).height == 0
    assert review.reviewed_for_planning_rows(rows).height == 0
    assert review.blocked_review_decision_rows(rows).height == 0


def test_validate_review_decision_rows_accepts_valid_future_row_shape() -> None:
    rows = pl.DataFrame([valid_review_row()])
    review.validate_review_decision_rows(rows)


def test_validate_review_decision_rows_rejects_missing_required_column() -> None:
    rows = committed_rows().drop("candidate_id")

    with pytest.raises(ValueError, match="missing required columns"):
        review.validate_review_decision_rows(rows)


def test_validate_review_decision_rows_rejects_duplicate_keys() -> None:
    row = valid_review_row()
    rows = pl.DataFrame([row, row])

    with pytest.raises(ValueError, match="duplicate keys"):
        review.validate_review_decision_rows(rows)


def test_validate_review_decision_rows_rejects_review_rule_mismatch() -> None:
    row = valid_review_row()
    row["downstream_block_status_after_review"] = "blocked_gate4_gate5"
    rows = pl.DataFrame([row])

    with pytest.raises(ValueError, match="decision-rule mismatches"):
        review.validate_review_decision_rows(rows)


def test_validate_review_decision_rows_rejects_missing_forbidden_actions() -> None:
    row = valid_review_row()
    row["forbidden_actions_after_review"] = "sequence fetch"
    rows = pl.DataFrame([row])

    with pytest.raises(ValueError, match="missing required forbidden actions"):
        review.validate_review_decision_rows(rows)


def test_validate_review_decision_rows_rejects_disallowed_claim_values() -> None:
    row = valid_review_row()
    row["reviewer_note"] = "validated_ortholog"
    rows = pl.DataFrame([row])

    with pytest.raises(ValueError, match="disallowed claim values"):
        review.validate_review_decision_rows(rows)
