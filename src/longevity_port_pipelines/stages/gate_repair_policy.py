from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

GATE4_GATE5_BLOCKED = "blocked_gate4_gate5"
REVIEWED_FOR_PLANNING_STILL_POLICY_BLOCKED = "reviewed_for_planning_still_policy_blocked"
ACCEPTED_FOR_PLANNING_AFTER_REVIEW = "accepted_for_planning_after_review"
CONSIDER_LATER_POLICY_UPDATE = "consider_later_explicit_gate4_gate5_policy_update"

REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"

RUNTIME_SIDE_EFFECTS = frozenset(
    {
        "sequence fetch",
        "manual ortholog curation",
        "Biohub call",
        "embedding generation",
        "Boltz call",
        "enrichment rerun",
        "contrast rerun",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "biological claim",
    }
)

BLOCKED_REVIEW_DECISIONS = frozenset(
    {
        "rejected_after_review",
        "deferred_pending_source",
        "needs_second_reviewer",
    }
)


@dataclass(frozen=True)
class GateRepairPolicyDecision:
    """Conservative Gate 4 / Gate 5 repair policy decision for one row."""

    repair_queue_status: str
    downstream_block_status: str
    allowed_next_action: str
    claim_status: str
    gate4_gate5_policy_update_allowed: bool
    explicit_policy_update_required: bool
    can_leave_gate4_gate5_now: bool
    gate8_eligible: bool
    gate9_eligible: bool
    embedding_ready: bool
    boltz_ready: bool
    biological_claim_allowed: bool
    reason: str


def _text(row: Mapping[str, object], key: str) -> str:
    value = row.get(key, "")
    if value is None:
        return ""
    return str(value).strip()


def forbidden_actions_present(row: Mapping[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row, "forbidden_actions")
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def classify_gate_repair_policy(
    row: Mapping[str, object],
) -> GateRepairPolicyDecision:
    """Classify one repair-summary row using conservative Gate 4 / Gate 5 policy.

    This helper is pure and table-only. It does not fetch sequences, curate
    orthologs, call Biohub, generate embeddings, call Boltz, rerun enrichment or
    contrast, promote Gate 8 / Gate 9, or make biological claims.
    """

    repair_decision = _text(row, "repair_decision")
    repair_queue_status = _text(row, "repair_queue_status")
    downstream_block_status = _text(row, "downstream_block_status")
    allowed_next_action = _text(row, "allowed_next_action")
    claim_status = _text(row, "claim_status")

    is_accepted_for_planning = repair_decision == ACCEPTED_FOR_PLANNING_AFTER_REVIEW
    still_policy_blocked = downstream_block_status == REVIEWED_FOR_PLANNING_STILL_POLICY_BLOCKED
    asks_for_later_policy_update = allowed_next_action == CONSIDER_LATER_POLICY_UPDATE

    policy_update_allowed = (
        is_accepted_for_planning or still_policy_blocked or asks_for_later_policy_update
    )

    if policy_update_allowed:
        reason = (
            "reviewed for planning; a later explicit Gate 4 / Gate 5 policy "
            "update may be considered, but this row cannot leave Gate 4 / Gate 5 now"
        )
    elif repair_decision in BLOCKED_REVIEW_DECISIONS:
        reason = f"{repair_decision} remains a Gate 4 / Gate 5 blocker"
    elif downstream_block_status == GATE4_GATE5_BLOCKED:
        reason = "row remains blocked at Gate 4 / Gate 5"
    else:
        reason = "row is conservatively blocked because no explicit policy helper permission exists"

    return GateRepairPolicyDecision(
        repair_queue_status=repair_queue_status,
        downstream_block_status=downstream_block_status,
        allowed_next_action=allowed_next_action,
        claim_status=claim_status,
        gate4_gate5_policy_update_allowed=policy_update_allowed,
        explicit_policy_update_required=policy_update_allowed,
        can_leave_gate4_gate5_now=False,
        gate8_eligible=False,
        gate9_eligible=False,
        embedding_ready=False,
        boltz_ready=False,
        biological_claim_allowed=False,
        reason=reason,
    )


def can_leave_gate4_gate5_now(row: Mapping[str, object]) -> bool:
    """Return whether the row can leave Gate 4 / Gate 5 without another PR."""

    return classify_gate_repair_policy(row).can_leave_gate4_gate5_now
