"""Explicit opt-in boundary for future stronger-source live lookup.

This module is a policy helper only. It does not implement a real source
client, does not call external services, does not fetch sequences, does not
collect source evidence, does not create reviewed decisions, and does not
promote downstream gates.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

import polars as pl

from longevity_port_pipelines.stages import ortholog_stronger_source_lookup_plan as lookup_plan

EXPLICIT_LIVE_LOOKUP_MODE: Final[str] = "explicit_live_opt_in_required"

DECISION_DENIED_NOT_EXPLICIT_PLAN: Final[str] = "denied_not_explicit_live_plan"
DECISION_DENIED_DEFAULT_NO_OPT_IN: Final[str] = "denied_default_no_opt_in"
DECISION_DENIED_CI: Final[str] = "denied_ci_external_api_disabled"
DECISION_DENIED_SEQUENCE_FETCH: Final[str] = "denied_sequence_fetch_requested"
DECISION_DENIED_WRONG_OUTPUT_TARGET: Final[str] = "denied_wrong_output_target"
DECISION_DENIED_PLAN_NOT_BLOCKED: Final[str] = "denied_plan_not_blocked"
DECISION_DENIED_CLAIM_NOT_REPAIR_WORKLIST: Final[str] = "denied_claim_not_repair_worklist"
DECISION_DENIED_PLAN_LIVE_FLAG: Final[str] = "denied_plan_live_flag_not_false"
DECISION_DENIED_PLAN_SEQUENCE_FLAG: Final[str] = "denied_plan_sequence_flag_not_false"
DECISION_DENIED_MISSING_BLOCKER_ACK: Final[str] = "denied_missing_blocker_ack"
DECISION_AUTHORIZED_STILL_BLOCKED: Final[str] = "authorized_explicit_opt_in_still_blocked"

POLICY_COLUMNS: Final[tuple[str, ...]] = (
    "candidate_set",
    "candidate_id",
    "planned_lookup_source_type",
    "planned_lookup_query_identifier",
    "planned_lookup_mode",
    "live_lookup_policy_decision",
    "live_lookup_authorized",
    "sequence_fetch_authorized",
    "live_lookup_policy_block_status",
    "live_lookup_policy_claim_status",
    "live_lookup_policy_output_target",
    "live_lookup_policy_note",
)


@dataclass(frozen=True)
class LiveLookupOptInContext:
    """Runtime-only context required before any future live lookup is allowed."""

    explicit_live_opt_in: bool = False
    running_in_ci: bool = False
    sequence_fetch_requested: bool = False
    operator_acknowledged_blockers: bool = False
    output_target: str = lookup_plan.DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET


def empty_policy_rows() -> pl.DataFrame:
    """Return an empty live-lookup policy decision frame."""

    return pl.DataFrame(schema={column: pl.String for column in POLICY_COLUMNS})


def text(row: Mapping[str, object], column: str) -> str:
    """Return a stripped string value from a plan row mapping."""

    return str(row.get(column, "")).strip()


def decision_row(
    row: Mapping[str, object],
    *,
    decision: str,
    authorized: bool,
    note: str,
) -> dict[str, str]:
    """Build one live-lookup policy decision row."""

    return {
        "candidate_set": text(row, "candidate_set"),
        "candidate_id": text(row, "candidate_id"),
        "planned_lookup_source_type": text(row, "planned_lookup_source_type"),
        "planned_lookup_query_identifier": text(
            row,
            "planned_lookup_query_identifier",
        ),
        "planned_lookup_mode": text(row, "planned_lookup_mode"),
        "live_lookup_policy_decision": decision,
        "live_lookup_authorized": str(authorized).lower(),
        "sequence_fetch_authorized": "false",
        "live_lookup_policy_block_status": lookup_plan.BLOCKED_GATE4_GATE5,
        "live_lookup_policy_claim_status": lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS,
        "live_lookup_policy_output_target": lookup_plan.DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET,
        "live_lookup_policy_note": note,
    }


def evaluate_live_lookup_opt_in_for_plan_row(
    row: Mapping[str, object],
    context: LiveLookupOptInContext | None = None,
) -> dict[str, str]:
    """Evaluate whether one plan row may enter a future live-lookup path.

    Authorization here is boundary metadata only. It does not run a live lookup,
    fetch sequences, write source evidence, create reviewed decisions, update
    Gate 4 / Gate 5 policy, promote downstream gates, or make biological claims.
    """

    if context is None:
        context = LiveLookupOptInContext()

    if text(row, "planned_lookup_mode") != EXPLICIT_LIVE_LOOKUP_MODE:
        return decision_row(
            row,
            decision=DECISION_DENIED_NOT_EXPLICIT_PLAN,
            authorized=False,
            note="Plan row is not marked explicit_live_opt_in_required.",
        )

    if text(row, "live_lookup_allowed") != "false":
        return decision_row(
            row,
            decision=DECISION_DENIED_PLAN_LIVE_FLAG,
            authorized=False,
            note="Plan rows must keep live_lookup_allowed=false by default.",
        )

    if text(row, "sequence_fetch_allowed") != "false":
        return decision_row(
            row,
            decision=DECISION_DENIED_PLAN_SEQUENCE_FLAG,
            authorized=False,
            note="Plan rows must keep sequence_fetch_allowed=false.",
        )

    if text(row, "planned_output_target") != lookup_plan.DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET:
        return decision_row(
            row,
            decision=DECISION_DENIED_WRONG_OUTPUT_TARGET,
            authorized=False,
            note="Plan row output target is outside the stronger-source collection table.",
        )

    if context.output_target != lookup_plan.DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET:
        return decision_row(
            row,
            decision=DECISION_DENIED_WRONG_OUTPUT_TARGET,
            authorized=False,
            note="Runtime output target is outside the stronger-source collection table.",
        )

    if text(row, "downstream_block_status_after_lookup_plan") != (lookup_plan.BLOCKED_GATE4_GATE5):
        return decision_row(
            row,
            decision=DECISION_DENIED_PLAN_NOT_BLOCKED,
            authorized=False,
            note="Plan row does not preserve blocked Gate 4 / Gate 5 status.",
        )

    if text(row, "claim_status_after_lookup_plan") != (lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS):
        return decision_row(
            row,
            decision=DECISION_DENIED_CLAIM_NOT_REPAIR_WORKLIST,
            authorized=False,
            note="Plan row does not preserve repair_worklist claim status.",
        )

    if context.running_in_ci:
        return decision_row(
            row,
            decision=DECISION_DENIED_CI,
            authorized=False,
            note="Live external lookup remains disabled in CI.",
        )

    if not context.explicit_live_opt_in:
        return decision_row(
            row,
            decision=DECISION_DENIED_DEFAULT_NO_OPT_IN,
            authorized=False,
            note="Runtime context did not provide explicit live lookup opt-in.",
        )

    if context.sequence_fetch_requested:
        return decision_row(
            row,
            decision=DECISION_DENIED_SEQUENCE_FETCH,
            authorized=False,
            note="Sequence fetch is a separate policy layer and is not authorized here.",
        )

    if not context.operator_acknowledged_blockers:
        return decision_row(
            row,
            decision=DECISION_DENIED_MISSING_BLOCKER_ACK,
            authorized=False,
            note="Operator did not acknowledge that results remain blocked and non-reviewed.",
        )

    return decision_row(
        row,
        decision=DECISION_AUTHORIZED_STILL_BLOCKED,
        authorized=True,
        note=(
            "Explicit runtime opt-in boundary passed. This authorizes only a "
            "future live metadata lookup path; it does not authorize sequence "
            "fetch, source evidence collection, reviewed decisions, Gate 4 / "
            "Gate 5 policy update, downstream promotion, or biological claims."
        ),
    )


def evaluate_live_lookup_opt_in_for_plan_rows(
    rows: pl.DataFrame,
    context: LiveLookupOptInContext | None = None,
) -> pl.DataFrame:
    """Evaluate live-lookup policy decisions for lookup plan rows."""

    if context is None:
        context = LiveLookupOptInContext()

    lookup_plan.validate_stronger_source_lookup_plan_rows(rows)
    if rows.is_empty():
        return empty_policy_rows()

    decisions = [
        evaluate_live_lookup_opt_in_for_plan_row(row, context) for row in rows.iter_rows(named=True)
    ]
    return pl.DataFrame(decisions).select(list(POLICY_COLUMNS))


def authorized_policy_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return rows that passed the explicit live-lookup opt-in boundary."""

    if rows.is_empty():
        return empty_policy_rows()

    return rows.filter(pl.col("live_lookup_authorized") == "true")
