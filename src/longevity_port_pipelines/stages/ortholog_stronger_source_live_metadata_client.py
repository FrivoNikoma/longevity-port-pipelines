"""Scaffold for future stronger-source live metadata lookup.

This module wires live metadata lookup attempts through the explicit opt-in
policy boundary. It is scaffold-only: it accepts an injected provider for tests
or future runtime integration, but it does not implement a network client, does
not fetch sequences, does not create evidence artifacts, does not create
reviewed decisions, does not update Gate 4 / Gate 5 policy, does not promote
downstream gates, and does not make biological claims.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Final

import polars as pl

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_lookup_policy as live_policy,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_lookup_plan as lookup_plan,
)

LOOKUP_STATUS_SKIPPED_POLICY_DENIED: Final[str] = "skipped_policy_denied_still_blocked"
LOOKUP_STATUS_RAW_METADATA_CANDIDATE: Final[str] = "raw_metadata_candidate_still_blocked"

RAW_METADATA_STATUS_NOT_REQUESTED: Final[str] = "not_requested_policy_denied"
RAW_METADATA_STATUS_RECEIVED_UNREVIEWED: Final[str] = "raw_metadata_received_unreviewed"

RESULT_COLUMNS: Final[tuple[str, ...]] = (
    "candidate_set",
    "candidate_id",
    "planned_lookup_source_type",
    "planned_lookup_query_identifier",
    "live_lookup_policy_decision",
    "live_metadata_lookup_status",
    "provider_called",
    "raw_metadata_status",
    "sequence_included",
    "evidence_row_created",
    "reviewed_decision_created",
    "downstream_block_status",
    "claim_status",
    "live_metadata_lookup_note",
)


@dataclass(frozen=True)
class LiveMetadataLookupRequest:
    """Minimal request passed to an injected metadata provider."""

    candidate_set: str
    candidate_id: str
    planned_lookup_source_type: str
    planned_lookup_query_identifier: str
    live_lookup_policy_decision: str


MetadataProvider = Callable[[LiveMetadataLookupRequest], Mapping[str, object]]


def empty_live_metadata_lookup_rows() -> pl.DataFrame:
    """Return an empty live metadata lookup scaffold result frame."""

    return pl.DataFrame(schema={column: pl.String for column in RESULT_COLUMNS})


def text(row: Mapping[str, object], column: str) -> str:
    """Return a stripped string value from a row mapping."""

    return str(row.get(column, "")).strip()


def request_from_policy_row(row: Mapping[str, object]) -> LiveMetadataLookupRequest:
    """Build the provider request identity from one policy decision row."""

    return LiveMetadataLookupRequest(
        candidate_set=text(row, "candidate_set"),
        candidate_id=text(row, "candidate_id"),
        planned_lookup_source_type=text(row, "planned_lookup_source_type"),
        planned_lookup_query_identifier=text(row, "planned_lookup_query_identifier"),
        live_lookup_policy_decision=text(row, "live_lookup_policy_decision"),
    )


def policy_row_is_authorized(row: Mapping[str, object]) -> bool:
    """Return true only for rows that passed the explicit opt-in boundary."""

    return (
        text(row, "live_lookup_authorized") == "true"
        and text(row, "live_lookup_policy_decision")
        == live_policy.DECISION_AUTHORIZED_STILL_BLOCKED
        and text(row, "sequence_fetch_authorized") == "false"
        and text(row, "live_lookup_policy_block_status") == lookup_plan.BLOCKED_GATE4_GATE5
        and text(row, "live_lookup_policy_claim_status") == lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS
    )


def result_row(
    row: Mapping[str, object],
    *,
    lookup_status: str,
    provider_called: bool,
    raw_metadata_status: str,
    note: str,
) -> dict[str, str]:
    """Build one scaffold result row that remains blocked and non-reviewed."""

    return {
        "candidate_set": text(row, "candidate_set"),
        "candidate_id": text(row, "candidate_id"),
        "planned_lookup_source_type": text(row, "planned_lookup_source_type"),
        "planned_lookup_query_identifier": text(row, "planned_lookup_query_identifier"),
        "live_lookup_policy_decision": text(row, "live_lookup_policy_decision"),
        "live_metadata_lookup_status": lookup_status,
        "provider_called": str(provider_called).lower(),
        "raw_metadata_status": raw_metadata_status,
        "sequence_included": "false",
        "evidence_row_created": "false",
        "reviewed_decision_created": "false",
        "downstream_block_status": lookup_plan.BLOCKED_GATE4_GATE5,
        "claim_status": lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS,
        "live_metadata_lookup_note": note,
    }


def run_live_metadata_lookup_for_policy_row(
    row: Mapping[str, object],
    provider: MetadataProvider,
) -> dict[str, str]:
    """Run scaffold lookup behavior for one policy row.

    Denied policy rows never call the injected provider. Authorized policy rows
    may call the injected provider, but the result remains raw, unreviewed,
    blocked at Gate 4 / Gate 5, and in repair_worklist claim status.
    """

    if not policy_row_is_authorized(row):
        return result_row(
            row,
            lookup_status=LOOKUP_STATUS_SKIPPED_POLICY_DENIED,
            provider_called=False,
            raw_metadata_status=RAW_METADATA_STATUS_NOT_REQUESTED,
            note=(
                "Policy boundary did not authorize a metadata provider call. "
                "The row remains blocked and non-reviewed."
            ),
        )

    request = request_from_policy_row(row)
    response = provider(request)
    raw_metadata_status = str(
        response.get("raw_metadata_status", RAW_METADATA_STATUS_RECEIVED_UNREVIEWED)
    ).strip()

    if raw_metadata_status == "":
        raw_metadata_status = RAW_METADATA_STATUS_RECEIVED_UNREVIEWED

    return result_row(
        row,
        lookup_status=LOOKUP_STATUS_RAW_METADATA_CANDIDATE,
        provider_called=True,
        raw_metadata_status=raw_metadata_status,
        note=(
            "Injected metadata provider returned a raw metadata candidate. "
            "This scaffold result is not evidence, not a reviewed decision, "
            "not a Gate 4 / Gate 5 policy update, and not downstream eligibility."
        ),
    )


def run_live_metadata_lookup_for_policy_rows(
    rows: pl.DataFrame,
    provider: MetadataProvider,
) -> pl.DataFrame:
    """Run scaffold lookup behavior for policy decision rows."""

    if rows.is_empty():
        return empty_live_metadata_lookup_rows()

    decisions = [
        run_live_metadata_lookup_for_policy_row(row, provider) for row in rows.iter_rows(named=True)
    ]
    return pl.DataFrame(decisions).select(list(RESULT_COLUMNS))
