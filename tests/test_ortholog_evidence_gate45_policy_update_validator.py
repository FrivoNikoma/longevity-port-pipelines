from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import ortholog_evidence_gate45_policy_update as policy


def committed_rows() -> pl.DataFrame:
    rows = policy.read_policy_update_rows()
    assert rows.height == 1
    return rows


def committed_row() -> dict[str, str]:
    rows = committed_rows().to_dicts()
    assert len(rows) == 1
    return {key: str(value) for key, value in rows[0].items()}


def valid_policy_update_row() -> dict[str, str]:
    return committed_row()


def test_read_policy_update_rows_loads_committed_row() -> None:
    rows = committed_rows()
    assert tuple(rows.columns) == policy.REQUIRED_COLUMNS


def test_validate_policy_update_rows_accepts_committed_row() -> None:
    rows = committed_rows()
    policy.validate_policy_update_rows(rows)


def test_policy_update_helpers_find_committed_runtime_blocked_row() -> None:
    rows = committed_rows()
    assert policy.find_duplicate_policy_update_keys(rows).height == 0
    assert policy.approved_policy_update_rows(rows).height == 1
    assert policy.blocked_policy_update_rows(rows).height == 0


def test_committed_policy_update_row_remains_runtime_blocked() -> None:
    row = committed_row()

    assert row["policy_update_decision"] == "approve_gate45_policy_update_for_planning"
    assert row["gate4_status_after_policy"] == "gate4_policy_updated_for_planning"
    assert row["gate5_status_after_policy"] == "gate5_policy_updated_for_planning"
    assert (
        row["downstream_block_status_after_policy"] == "gate45_policy_updated_still_runtime_blocked"
    )
    assert row["allowed_next_action_after_policy"] == (
        "prepare_later_gate_aware_embedding_fill_plan_pr"
    )
    assert row["claim_status_after_policy"] == "repair_worklist"
    assert policy.forbidden_actions_present(row)


def test_validate_policy_update_rows_accepts_valid_future_row_shape() -> None:
    rows = pl.DataFrame([valid_policy_update_row()])
    policy.validate_policy_update_rows(rows)


def test_validate_policy_update_rows_rejects_missing_required_column() -> None:
    rows = committed_rows().drop("candidate_id")

    with pytest.raises(ValueError, match="missing required columns"):
        policy.validate_policy_update_rows(rows)


def test_validate_policy_update_rows_rejects_duplicate_keys() -> None:
    row = valid_policy_update_row()
    rows = pl.DataFrame([row, row])

    with pytest.raises(ValueError, match="duplicate keys"):
        policy.validate_policy_update_rows(rows)


def test_validate_policy_update_rows_rejects_decision_rule_mismatch() -> None:
    row = valid_policy_update_row()
    row["downstream_block_status_after_policy"] = "blocked_gate4_gate5"
    rows = pl.DataFrame([row])

    with pytest.raises(ValueError, match="decision-rule mismatches"):
        policy.validate_policy_update_rows(rows)


def test_validate_policy_update_rows_rejects_missing_forbidden_actions() -> None:
    row = valid_policy_update_row()
    row["forbidden_actions_after_policy"] = "sequence fetch"
    rows = pl.DataFrame([row])

    with pytest.raises(ValueError, match="missing required forbidden actions"):
        policy.validate_policy_update_rows(rows)


def test_validate_policy_update_rows_rejects_disallowed_claim_values() -> None:
    row = valid_policy_update_row()
    row["policy_update_note"] = "validated_ortholog"
    rows = pl.DataFrame([row])

    with pytest.raises(ValueError, match="disallowed claim values"):
        policy.validate_policy_update_rows(rows)
