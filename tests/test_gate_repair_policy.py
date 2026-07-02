from __future__ import annotations

import csv
from pathlib import Path

from longevity_port_pipelines.stages import gate_repair_policy as policy

REVIEWED_OVERLAY_FIXTURE = Path("tests/fixtures/generic_repair_queue_summary_reviewed_overlay.csv")


def _fixture_rows() -> list[dict[str, str]]:
    with REVIEWED_OVERLAY_FIXTURE.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_reviewed_overlay_fixture_rows_remain_gate4_gate5_blocked() -> None:
    rows = _fixture_rows()

    decisions = [policy.classify_gate_repair_policy(row) for row in rows]

    assert len(decisions) == 13
    assert {decision.can_leave_gate4_gate5_now for decision in decisions} == {False}
    assert {decision.gate8_eligible for decision in decisions} == {False}
    assert {decision.gate9_eligible for decision in decisions} == {False}
    assert {decision.embedding_ready for decision in decisions} == {False}
    assert {decision.boltz_ready for decision in decisions} == {False}
    assert {decision.biological_claim_allowed for decision in decisions} == {False}


def test_deferred_reviewed_sirt6_row_does_not_allow_policy_update() -> None:
    deferred_row = _fixture_rows()[0]

    decision = policy.classify_gate_repair_policy(deferred_row)

    assert deferred_row["repair_decision"] == "deferred_pending_source"
    assert decision.gate4_gate5_policy_update_allowed is False
    assert decision.explicit_policy_update_required is False
    assert decision.can_leave_gate4_gate5_now is False
    assert decision.downstream_block_status == "blocked_gate4_gate5"
    assert decision.allowed_next_action == "defer_until_stronger_source_evidence_exists"
    assert decision.claim_status == "repair_worklist"
    assert "Gate 4 / Gate 5 blocker" in decision.reason


def test_accepted_review_still_requires_later_explicit_policy_update() -> None:
    accepted_row = {
        "repair_decision": "accepted_for_planning_after_review",
        "repair_queue_status": "reviewed_for_planning",
        "downstream_block_status": "reviewed_for_planning_still_policy_blocked",
        "allowed_next_action": "consider_later_explicit_gate4_gate5_policy_update",
        "claim_status": "repair_worklist",
        "forbidden_actions": "; ".join(sorted(policy.RUNTIME_SIDE_EFFECTS)),
    }

    decision = policy.classify_gate_repair_policy(accepted_row)

    assert decision.gate4_gate5_policy_update_allowed is True
    assert decision.explicit_policy_update_required is True
    assert decision.can_leave_gate4_gate5_now is False
    assert decision.gate8_eligible is False
    assert decision.gate9_eligible is False
    assert decision.embedding_ready is False
    assert decision.boltz_ready is False
    assert decision.biological_claim_allowed is False
    assert "later explicit Gate 4 / Gate 5 policy update" in decision.reason


def test_blocked_review_decisions_remain_blocked() -> None:
    for review_decision in [
        "rejected_after_review",
        "deferred_pending_source",
        "needs_second_reviewer",
    ]:
        row = {
            "repair_decision": review_decision,
            "repair_queue_status": f"blocked_{review_decision}",
            "downstream_block_status": "blocked_gate4_gate5",
            "allowed_next_action": "manual_sequence_provenance_review",
            "claim_status": "repair_worklist",
            "forbidden_actions": "; ".join(sorted(policy.RUNTIME_SIDE_EFFECTS)),
        }

        decision = policy.classify_gate_repair_policy(row)

        assert decision.gate4_gate5_policy_update_allowed is False
        assert decision.can_leave_gate4_gate5_now is False
        assert decision.gate8_eligible is False
        assert decision.gate9_eligible is False
        assert decision.biological_claim_allowed is False


def test_unknown_or_unrecognized_status_is_conservatively_blocked() -> None:
    row = {
        "repair_decision": "unexpected_future_status",
        "repair_queue_status": "unexpected_future_status",
        "downstream_block_status": "unexpected_future_status",
        "allowed_next_action": "unexpected_future_action",
        "claim_status": "repair_worklist",
        "forbidden_actions": "",
    }

    decision = policy.classify_gate_repair_policy(row)

    assert decision.gate4_gate5_policy_update_allowed is False
    assert decision.can_leave_gate4_gate5_now is False
    assert decision.gate8_eligible is False
    assert decision.gate9_eligible is False
    assert decision.embedding_ready is False
    assert decision.boltz_ready is False
    assert decision.biological_claim_allowed is False
    assert "conservatively blocked" in decision.reason


def test_fixture_rows_keep_runtime_side_effects_forbidden() -> None:
    assert all(policy.forbidden_actions_present(row) for row in _fixture_rows())
