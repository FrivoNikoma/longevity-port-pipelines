"""Dry-run runtime boundary for stronger-source live metadata lookup.

This module wires lookup plan rows through the explicit live lookup policy
boundary and then through the scaffold-only live metadata client. It is
operator/runtime dry-run only: provider calls are fake/injected/noop only, and
results remain raw metadata dry-run summary rows.

It does not implement a real API client, import network libraries, fetch
sequences, persist raw metadata, collect source evidence, create reviewed
decisions, update Gate 4 / Gate 5 policy, promote Gate 8 or Gate 9, or make
biological claims.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final

import polars as pl

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_lookup_policy as live_policy,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_metadata_client as live_client,
)

DRY_RUN_STATUS_SKIPPED_POLICY_DENIED: Final[str] = "dry_run_skipped_policy_denied_still_blocked"
DRY_RUN_STATUS_RAW_METADATA_CANDIDATE: Final[str] = "dry_run_raw_metadata_candidate_still_blocked"

PROVIDER_MODE_INJECTED_FAKE_OR_NOOP_ONLY: Final[str] = "injected_fake_or_noop_provider_only"

RAW_METADATA_STATUS_DRY_RUN_NOOP_UNREVIEWED: Final[str] = "raw_metadata_dry_run_noop_unreviewed"

BIOLOGICAL_CLAIM_STATUS_NONE: Final[str] = "no_biological_claim"

DRY_RUN_SUMMARY_COLUMNS: Final[tuple[str, ...]] = (
    "candidate_set",
    "candidate_id",
    "planned_lookup_source_type",
    "planned_lookup_query_identifier",
    "planned_lookup_mode",
    "runtime_explicit_live_opt_in",
    "runtime_operator_acknowledged_blockers",
    "runtime_running_in_ci",
    "runtime_sequence_fetch_requested",
    "runtime_output_target",
    "live_lookup_policy_decision",
    "live_lookup_authorized",
    "sequence_fetch_authorized",
    "live_metadata_lookup_status",
    "live_metadata_provider_called",
    "raw_metadata_status",
    "dry_run_status",
    "dry_run_provider_mode",
    "sequence_included",
    "persistence_written",
    "source_evidence_created",
    "evidence_row_created",
    "reviewed_decision_created",
    "gate4_gate5_policy_updated",
    "gate8_promoted",
    "gate9_promoted",
    "downstream_block_status",
    "claim_status",
    "biological_claim_status",
    "dry_run_note",
)


def empty_live_metadata_dry_run_summary() -> pl.DataFrame:
    """Return an empty typed dry-run summary frame."""

    return pl.DataFrame(schema={column: pl.String for column in DRY_RUN_SUMMARY_COLUMNS})


def text(row: Mapping[str, object], column: str) -> str:
    """Return a stripped string value from a row mapping."""

    return str(row.get(column, "")).strip()


def bool_text(value: bool) -> str:
    """Return lower-case string form for runtime boolean flags."""

    return str(value).lower()


def noop_live_metadata_provider(
    request: live_client.LiveMetadataLookupRequest,
) -> Mapping[str, object]:
    """Return a raw, unreviewed noop metadata candidate for dry-run tests.

    The request is accepted only so the scaffold can prove provider wiring.
    This function does not call external services, fetch sequences, persist
    metadata, create source evidence, create reviewed decisions, update gates,
    or make biological claims.
    """

    return {
        "raw_metadata_status": RAW_METADATA_STATUS_DRY_RUN_NOOP_UNREVIEWED,
        "provider_request_candidate_set": request.candidate_set,
        "provider_request_candidate_id": request.candidate_id,
        "provider_request_source_type": request.planned_lookup_source_type,
        "provider_request_query_identifier": request.planned_lookup_query_identifier,
    }


def dry_run_status_for_client_row(row: Mapping[str, object]) -> str:
    """Return the dry-run status implied by the scaffold result row."""

    if text(row, "provider_called") == "true":
        return DRY_RUN_STATUS_RAW_METADATA_CANDIDATE

    return DRY_RUN_STATUS_SKIPPED_POLICY_DENIED


def dry_run_note(
    *,
    policy_row: Mapping[str, object],
    client_row: Mapping[str, object],
) -> str:
    """Build a conservative runtime dry-run note."""

    return (
        "Dry-run runtime boundary evaluated the lookup plan through the live "
        "lookup opt-in policy and scaffold-only metadata client. "
        f"policy_decision={text(policy_row, 'live_lookup_policy_decision')}; "
        f"metadata_lookup_status={text(client_row, 'live_metadata_lookup_status')}. "
        "This summary is raw metadata dry-run output only: it is not persisted "
        "metadata, not source evidence, not a reviewed decision, not a Gate 4 / "
        "Gate 5 policy update, not Gate 8 or Gate 9 promotion, and not a "
        "biological claim."
    )


def dry_run_summary_row(
    *,
    plan_row: Mapping[str, object],
    policy_row: Mapping[str, object],
    client_row: Mapping[str, object],
    context: live_policy.LiveLookupOptInContext,
    provider_mode: str,
) -> dict[str, str]:
    """Build one typed dry-run summary row from plan, policy, and scaffold rows."""

    return {
        "candidate_set": text(policy_row, "candidate_set"),
        "candidate_id": text(policy_row, "candidate_id"),
        "planned_lookup_source_type": text(policy_row, "planned_lookup_source_type"),
        "planned_lookup_query_identifier": text(
            policy_row,
            "planned_lookup_query_identifier",
        ),
        "planned_lookup_mode": text(plan_row, "planned_lookup_mode"),
        "runtime_explicit_live_opt_in": bool_text(context.explicit_live_opt_in),
        "runtime_operator_acknowledged_blockers": bool_text(context.operator_acknowledged_blockers),
        "runtime_running_in_ci": bool_text(context.running_in_ci),
        "runtime_sequence_fetch_requested": bool_text(context.sequence_fetch_requested),
        "runtime_output_target": context.output_target,
        "live_lookup_policy_decision": text(policy_row, "live_lookup_policy_decision"),
        "live_lookup_authorized": text(policy_row, "live_lookup_authorized"),
        "sequence_fetch_authorized": text(policy_row, "sequence_fetch_authorized"),
        "live_metadata_lookup_status": text(client_row, "live_metadata_lookup_status"),
        "live_metadata_provider_called": text(client_row, "provider_called"),
        "raw_metadata_status": text(client_row, "raw_metadata_status"),
        "dry_run_status": dry_run_status_for_client_row(client_row),
        "dry_run_provider_mode": provider_mode,
        "sequence_included": text(client_row, "sequence_included"),
        "persistence_written": "false",
        "source_evidence_created": "false",
        "evidence_row_created": text(client_row, "evidence_row_created"),
        "reviewed_decision_created": text(client_row, "reviewed_decision_created"),
        "gate4_gate5_policy_updated": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "downstream_block_status": text(client_row, "downstream_block_status"),
        "claim_status": text(client_row, "claim_status"),
        "biological_claim_status": BIOLOGICAL_CLAIM_STATUS_NONE,
        "dry_run_note": dry_run_note(policy_row=policy_row, client_row=client_row),
    }


def _summary_from_rows(rows: list[dict[str, str]]) -> pl.DataFrame:
    """Build a typed dry-run summary frame from row dictionaries."""

    if not rows:
        return empty_live_metadata_dry_run_summary()

    return pl.DataFrame(rows).select(list(DRY_RUN_SUMMARY_COLUMNS))


def build_live_metadata_dry_run_summary(
    lookup_plan_rows: pl.DataFrame,
    *,
    context: live_policy.LiveLookupOptInContext | None = None,
    provider: live_client.MetadataProvider = noop_live_metadata_provider,
    provider_mode: str = PROVIDER_MODE_INJECTED_FAKE_OR_NOOP_ONLY,
) -> pl.DataFrame:
    """Build a dry-run runtime/operator summary for live metadata lookup attempts.

    The wrapper connects three already-separated layers:

    1. lookup plan row;
    2. explicit live lookup policy decision;
    3. scaffold-only metadata client with injected fake/noop provider.

    The returned rows are a typed summary contract for tests and operators.
    They are not persisted raw metadata, not source evidence, not reviewed
    decisions, not Gate 4 / Gate 5 policy updates, not downstream eligibility,
    and not biological claims.
    """

    if context is None:
        context = live_policy.LiveLookupOptInContext()

    policy_rows = live_policy.evaluate_live_lookup_opt_in_for_plan_rows(
        lookup_plan_rows,
        context,
    )
    client_rows = live_client.run_live_metadata_lookup_for_policy_rows(
        policy_rows,
        provider,
    )

    if policy_rows.is_empty():
        return empty_live_metadata_dry_run_summary()

    summary_rows = [
        dry_run_summary_row(
            plan_row=plan_row,
            policy_row=policy_row,
            client_row=client_row,
            context=context,
            provider_mode=provider_mode,
        )
        for plan_row, policy_row, client_row in zip(
            lookup_plan_rows.iter_rows(named=True),
            policy_rows.iter_rows(named=True),
            client_rows.iter_rows(named=True),
            strict=True,
        )
    ]

    return _summary_from_rows(summary_rows).sort(
        [
            "dry_run_status",
            "candidate_id",
            "planned_lookup_source_type",
            "planned_lookup_query_identifier",
        ]
    )


def dry_run_status_counts(summary: pl.DataFrame) -> dict[str, int]:
    """Return dry-run status counts for operator/runtime reporting."""

    if summary.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in summary.group_by("dry_run_status").len().iter_rows(named=True):
        counts[str(row["dry_run_status"])] = int(row["len"])

    return counts
