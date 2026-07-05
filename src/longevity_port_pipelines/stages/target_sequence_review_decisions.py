from __future__ import annotations

from typing import Literal, cast

import polars as pl

FORBIDDEN_ACTIONS = (
    "sequence fetch; source provenance row mutation; Biohub call; ESMC call; "
    "embedding generation; curated_embedding_preflight; curated_embedding_single; "
    "data/output commit; .npy artifact; ready_for_preflight; Gate 8 promotion; "
    "Gate 9 promotion; Boltz call; AF3 call; Chai call; enrichment rerun; "
    "contrast rerun; biological claim"
)

SequenceReviewDecision = Literal[
    "approve_reviewed_sequence_provenance_for_planning",
    "defer_pending_sequence_review",
    "reject_sequence_provenance",
    "keep_blocked_after_mismatch",
]
SequenceLengthStatusAfterDecision = Literal[
    "matches",
    "mismatch",
    "not_checked",
    "not_fetched",
]

REQUIRED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "source_sequence_provenance_table",
    "source_sequence_provenance_row_index",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "sequence_review_decision",
    "sequence_length_status_after_decision",
    "provenance_review_status_after_decision",
    "reviewed_sequence_sha256",
    "reviewed_sequence_length",
    "decision_status",
    "downstream_block_status_after_decision",
    "allowed_next_action_after_decision",
    "claim_policy",
    "claim_status",
    "review_note",
    "reviewer_id",
    "review_date",
    "forbidden_actions",
]

TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "source_sequence_provenance_table": pl.Utf8,
    "source_sequence_provenance_row_index": pl.Int64,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "sequence_review_decision": pl.Utf8,
    "sequence_length_status_after_decision": pl.Utf8,
    "provenance_review_status_after_decision": pl.Utf8,
    "reviewed_sequence_sha256": pl.Utf8,
    "reviewed_sequence_length": pl.Int64,
    "decision_status": pl.Utf8,
    "downstream_block_status_after_decision": pl.Utf8,
    "allowed_next_action_after_decision": pl.Utf8,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "review_note": pl.Utf8,
    "reviewer_id": pl.Utf8,
    "review_date": pl.Utf8,
    "forbidden_actions": pl.Utf8,
}

ALLOWED_SOURCE_SEQUENCE_PROVENANCE_TABLES = {
    "data/input/reviewed_target_sequence_provenance.csv",
}
ALLOWED_SEQUENCE_REVIEW_DECISIONS = {
    "approve_reviewed_sequence_provenance_for_planning",
    "defer_pending_sequence_review",
    "reject_sequence_provenance",
    "keep_blocked_after_mismatch",
}
ALLOWED_SEQUENCE_LENGTH_STATUSES_AFTER_DECISION = {
    "matches",
    "mismatch",
    "not_checked",
    "not_fetched",
}
ALLOWED_PROVENANCE_REVIEW_STATUSES_AFTER_DECISION = {
    "reviewed",
    "rejected",
    "needs_review",
    "deferred",
}
ALLOWED_DECISION_STATUSES = {
    "reviewed_for_planning_still_preflight_blocked",
    "deferred_pending_review",
    "rejected_sequence_provenance",
    "keep_blocked_after_mismatch",
}
ALLOWED_DOWNSTREAM_BLOCK_STATUSES_AFTER_DECISION = {
    "sequence_reviewed_still_preflight_decision_blocked",
    "sequence_review_deferred_still_blocked",
    "sequence_review_rejected_or_excluded",
    "sequence_review_mismatch_still_blocked",
}
ALLOWED_NEXT_ACTIONS_AFTER_DECISION = {
    "consider_later_dry_run_preflight_decision_pr",
    "defer_pending_sequence_review",
    "reject_or_exclude_sequence_source",
    "keep_blocked",
}
ALLOWED_CLAIM_POLICIES = {"no_biological_claims_until_validation"}
ALLOWED_CLAIM_STATUSES = {"technical_checkpoint", "repair_worklist"}


def empty_target_sequence_review_decisions_table() -> pl.DataFrame:
    return pl.DataFrame(schema=TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA)


def validate_target_sequence_review_decision_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required target sequence review decision columns: {missing}")


def _row_value(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        raise ValueError(f"Missing value for {column}")
    return str(value).strip()


def _expected_decision_values(
    *,
    sequence_review_decision: SequenceReviewDecision,
    sequence_length_status_after_decision: SequenceLengthStatusAfterDecision,
) -> tuple[str, str, str, str]:
    if sequence_review_decision == "approve_reviewed_sequence_provenance_for_planning":
        if sequence_length_status_after_decision != "matches":
            return (
                "keep_blocked_after_mismatch",
                "sequence_review_mismatch_still_blocked",
                "keep_blocked",
                "repair_worklist",
            )
        return (
            "reviewed_for_planning_still_preflight_blocked",
            "sequence_reviewed_still_preflight_decision_blocked",
            "consider_later_dry_run_preflight_decision_pr",
            "technical_checkpoint",
        )
    if sequence_review_decision == "reject_sequence_provenance":
        return (
            "rejected_sequence_provenance",
            "sequence_review_rejected_or_excluded",
            "reject_or_exclude_sequence_source",
            "repair_worklist",
        )
    if sequence_review_decision == "keep_blocked_after_mismatch":
        return (
            "keep_blocked_after_mismatch",
            "sequence_review_mismatch_still_blocked",
            "keep_blocked",
            "repair_worklist",
        )
    return (
        "deferred_pending_review",
        "sequence_review_deferred_still_blocked",
        "defer_pending_sequence_review",
        "repair_worklist",
    )


def validate_target_sequence_review_decision_rows(table: pl.DataFrame) -> None:
    validate_target_sequence_review_decision_schema(table)

    for row in table.iter_rows(named=True):
        source_table = _row_value(row, "source_sequence_provenance_table")
        sequence_review_decision = _row_value(row, "sequence_review_decision")
        sequence_length_status_after_decision = _row_value(
            row, "sequence_length_status_after_decision"
        )
        provenance_review_status_after_decision = _row_value(
            row, "provenance_review_status_after_decision"
        )
        decision_status = _row_value(row, "decision_status")
        downstream_block_status = _row_value(row, "downstream_block_status_after_decision")
        allowed_next_action = _row_value(row, "allowed_next_action_after_decision")
        claim_policy = _row_value(row, "claim_policy")
        claim_status = _row_value(row, "claim_status")

        if source_table not in ALLOWED_SOURCE_SEQUENCE_PROVENANCE_TABLES:
            raise ValueError(f"Invalid source_sequence_provenance_table: {source_table}")
        if sequence_review_decision not in ALLOWED_SEQUENCE_REVIEW_DECISIONS:
            raise ValueError(f"Invalid sequence_review_decision: {sequence_review_decision}")
        if (
            sequence_length_status_after_decision
            not in ALLOWED_SEQUENCE_LENGTH_STATUSES_AFTER_DECISION
        ):
            raise ValueError(
                "Invalid sequence_length_status_after_decision: "
                f"{sequence_length_status_after_decision}"
            )
        if (
            provenance_review_status_after_decision
            not in ALLOWED_PROVENANCE_REVIEW_STATUSES_AFTER_DECISION
        ):
            raise ValueError(
                "Invalid provenance_review_status_after_decision: "
                f"{provenance_review_status_after_decision}"
            )
        if decision_status not in ALLOWED_DECISION_STATUSES:
            raise ValueError(f"Invalid decision_status: {decision_status}")
        if downstream_block_status not in ALLOWED_DOWNSTREAM_BLOCK_STATUSES_AFTER_DECISION:
            raise ValueError(
                f"Invalid downstream_block_status_after_decision: {downstream_block_status}"
            )
        if allowed_next_action not in ALLOWED_NEXT_ACTIONS_AFTER_DECISION:
            raise ValueError(f"Invalid allowed_next_action_after_decision: {allowed_next_action}")
        if claim_policy not in ALLOWED_CLAIM_POLICIES:
            raise ValueError(f"Invalid claim_policy: {claim_policy}")
        if claim_status not in ALLOWED_CLAIM_STATUSES:
            raise ValueError(f"Invalid claim_status: {claim_status}")

        (
            expected_decision_status,
            expected_downstream_block_status,
            expected_next_action,
            expected_claim_status,
        ) = _expected_decision_values(
            sequence_review_decision=cast(
                SequenceReviewDecision,
                sequence_review_decision,
            ),
            sequence_length_status_after_decision=cast(
                SequenceLengthStatusAfterDecision,
                sequence_length_status_after_decision,
            ),
        )
        if decision_status != expected_decision_status:
            raise ValueError(
                f"decision_status does not match decision rule: expected "
                f"{expected_decision_status}, got {decision_status}"
            )
        if downstream_block_status != expected_downstream_block_status:
            raise ValueError(
                "downstream_block_status_after_decision does not match decision rule: "
                f"expected {expected_downstream_block_status}, got {downstream_block_status}"
            )
        if allowed_next_action != expected_next_action:
            raise ValueError(
                "allowed_next_action_after_decision does not match decision rule: "
                f"expected {expected_next_action}, got {allowed_next_action}"
            )
        if claim_status != expected_claim_status:
            raise ValueError(
                f"claim_status does not match decision rule: expected "
                f"{expected_claim_status}, got {claim_status}"
            )

        if sequence_review_decision == "approve_reviewed_sequence_provenance_for_planning":
            if sequence_length_status_after_decision != "matches":
                raise ValueError(
                    "approve_reviewed_sequence_provenance_for_planning requires "
                    "sequence_length_status_after_decision=matches"
                )
            if provenance_review_status_after_decision != "reviewed":
                raise ValueError(
                    "approve_reviewed_sequence_provenance_for_planning requires reviewed provenance"
                )

        if (
            sequence_review_decision == "keep_blocked_after_mismatch"
            and sequence_length_status_after_decision != "mismatch"
        ):
            raise ValueError(
                "keep_blocked_after_mismatch requires "
                "sequence_length_status_after_decision=mismatch"
            )

        forbidden_actions = _row_value(row, "forbidden_actions")
        for required in [
            "sequence fetch",
            "source provenance row mutation",
            "Biohub call",
            "ESMC call",
            "embedding generation",
            "curated_embedding_preflight",
            "curated_embedding_single",
            "ready_for_preflight",
            "Gate 8 promotion",
            "Gate 9 promotion",
            "Boltz call",
            "AF3 call",
            "Chai call",
            "biological claim",
        ]:
            if required not in forbidden_actions:
                raise ValueError(f"Missing forbidden action guardrail: {required}")
