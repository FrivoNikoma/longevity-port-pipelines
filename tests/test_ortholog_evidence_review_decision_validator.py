from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import ortholog_evidence_review_decision as review


def committed_rows() -> pl.DataFrame:
    rows = review.read_review_decision_rows()
    assert rows.height == 1
    return rows


def committed_row() -> dict[str, str]:
    rows = committed_rows().to_dicts()
    assert len(rows) == 1
    return {key: str(value) for key, value in rows[0].items()}


def valid_review_row() -> dict[str, str]:
    return committed_row()


def test_read_review_decision_rows_loads_committed_row() -> None:
    rows = committed_rows()
    assert tuple(rows.columns) == review.REQUIRED_COLUMNS


def test_validate_review_decision_rows_accepts_committed_row() -> None:
    rows = committed_rows()
    review.validate_review_decision_rows(rows)


def test_review_decision_helpers_find_committed_planning_row() -> None:
    rows = committed_rows()
    assert review.find_duplicate_review_decision_keys(rows).height == 0
    assert review.reviewed_for_planning_rows(rows).height == 1
    assert review.blocked_review_decision_rows(rows).height == 0


def test_committed_review_decision_row_is_policy_blocked() -> None:
    row = committed_row()

    assert row["review_decision"] == "accepted_for_planning_after_review"
    assert row["downstream_block_status_after_review"] == (
        "reviewed_for_planning_still_policy_blocked"
    )
    assert row["allowed_next_action_after_review"] == (
        "consider_later_explicit_gate4_gate5_policy_update"
    )
    assert row["claim_status_after_review"] == "repair_worklist"
    assert review.forbidden_actions_present(row)


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
