from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import ortholog_evidence_gate45_policy_update as policy


def committed_rows() -> pl.DataFrame:
    rows = policy.read_policy_update_rows()
    assert rows.height == 0
    return rows


def valid_policy_update_row() -> dict[str, str]:
    row = {column: "value" for column in policy.REQUIRED_COLUMNS}
    row.update(
        {
            "candidate_set": "tp53_mdm2_elephant",
            "lane_name": "tp53_mdm2_elephant",
            "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
            "policy_source_table": "data/input/ortholog_evidence_review_decisions.csv",
            "policy_source_row_index": "1",
            "reviewed_target_uniprot": "G3SX30",
            "reviewed_source_database": "UniProtKB TrEMBL",
            "reviewed_source_accession": "G3SX30",
            "reviewed_taxid": "9785",
            "reviewed_sequence_length": "492",
            "review_decision_before_policy": "accepted_for_planning_after_review",
            "downstream_block_status_before_policy": ("reviewed_for_planning_still_policy_blocked"),
            "allowed_next_action_before_policy": (
                "consider_later_explicit_gate4_gate5_policy_update"
            ),
            "claim_status_before_policy": "repair_worklist",
            "policy_update_decision": "approve_gate45_policy_update_for_planning",
            "gate4_status_after_policy": "gate4_policy_updated_for_planning",
            "gate5_status_after_policy": "gate5_policy_updated_for_planning",
            "downstream_block_status_after_policy": ("gate45_policy_updated_still_runtime_blocked"),
            "allowed_next_action_after_policy": ("prepare_later_gate_aware_embedding_fill_plan_pr"),
            "claim_policy_after_policy": "no_biological_claims_until_validation",
            "claim_status_after_policy": "repair_worklist",
            "policy_update_note": (
                "Planning-policy update only; no runtime side effects or biological claims."
            ),
            "forbidden_actions_after_policy": "; ".join(sorted(policy.RUNTIME_SIDE_EFFECTS)),
        }
    )
    return row


def test_read_policy_update_rows_loads_header_only_scaffold() -> None:
    rows = committed_rows()
    assert tuple(rows.columns) == policy.REQUIRED_COLUMNS


def test_validate_policy_update_rows_accepts_header_only_scaffold() -> None:
    rows = committed_rows()
    policy.validate_policy_update_rows(rows)


def test_policy_update_helpers_return_empty_frames_for_scaffold() -> None:
    rows = committed_rows()
    assert policy.find_duplicate_policy_update_keys(rows).height == 0
    assert policy.approved_policy_update_rows(rows).height == 0
    assert policy.blocked_policy_update_rows(rows).height == 0


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
