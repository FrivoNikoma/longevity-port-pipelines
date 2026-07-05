from __future__ import annotations

from typing import Literal, cast

import polars as pl

FORBIDDEN_ACTIONS = (
    "sequence fetch; Biohub call; ESMC call; embedding generation; "
    "curated_embedding_preflight run; curated_embedding_single run; data/output commit; "
    ".npy artifact; ready_for_preflight; Gate 8 promotion; Gate 9 promotion; "
    "Boltz call; AF3 call; Chai call; enrichment rerun; contrast rerun; biological claim"
)

DryRunPreflightDecision = Literal[
    "approve_dry_run_preflight_for_planning",
    "defer_pending_dry_run_preflight_decision",
    "keep_blocked",
]
SourceSequenceReviewDecision = Literal[
    "approve_reviewed_sequence_provenance_for_planning",
    "defer_pending_sequence_review",
    "reject_sequence_provenance",
    "keep_blocked_after_mismatch",
]

REQUIRED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "source_target_sequence_review_decision_table",
    "source_target_sequence_review_decision_row_index",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "source_sequence_review_decision",
    "source_sequence_length_status_after_decision",
    "source_provenance_review_status_after_decision",
    "source_decision_status",
    "source_downstream_block_status_after_decision",
    "reviewed_sequence_sha256",
    "reviewed_sequence_length",
    "dry_run_preflight_decision",
    "dry_run_preflight_status_after_decision",
    "allowed_next_action_after_decision",
    "max_live_batch_size_after_decision",
    "ready_for_preflight_after_decision",
    "claim_policy",
    "claim_status",
    "review_note",
    "reviewer_id",
    "review_date",
    "forbidden_actions",
]

G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "source_target_sequence_review_decision_table": pl.Utf8,
    "source_target_sequence_review_decision_row_index": pl.Int64,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "source_sequence_review_decision": pl.Utf8,
    "source_sequence_length_status_after_decision": pl.Utf8,
    "source_provenance_review_status_after_decision": pl.Utf8,
    "source_decision_status": pl.Utf8,
    "source_downstream_block_status_after_decision": pl.Utf8,
    "reviewed_sequence_sha256": pl.Utf8,
    "reviewed_sequence_length": pl.Int64,
    "dry_run_preflight_decision": pl.Utf8,
    "dry_run_preflight_status_after_decision": pl.Utf8,
    "allowed_next_action_after_decision": pl.Utf8,
    "max_live_batch_size_after_decision": pl.Int64,
    "ready_for_preflight_after_decision": pl.Utf8,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "review_note": pl.Utf8,
    "reviewer_id": pl.Utf8,
    "review_date": pl.Utf8,
    "forbidden_actions": pl.Utf8,
}

ALLOWED_SOURCE_TABLES = {"data/input/target_sequence_review_decisions.csv"}
ALLOWED_SOURCE_SEQUENCE_REVIEW_DECISIONS = {
    "approve_reviewed_sequence_provenance_for_planning",
    "defer_pending_sequence_review",
    "reject_sequence_provenance",
    "keep_blocked_after_mismatch",
}
ALLOWED_SOURCE_LENGTH_STATUSES = {"matches", "mismatch", "not_checked", "not_fetched"}
ALLOWED_SOURCE_PROVENANCE_REVIEW_STATUSES = {
    "reviewed",
    "rejected",
    "needs_review",
    "deferred",
}
ALLOWED_SOURCE_DECISION_STATUSES = {
    "reviewed_for_planning_still_preflight_blocked",
    "deferred_pending_review",
    "rejected_sequence_provenance",
    "keep_blocked_after_mismatch",
}
ALLOWED_SOURCE_DOWNSTREAM_BLOCK_STATUSES = {
    "sequence_reviewed_still_preflight_decision_blocked",
    "sequence_review_deferred_still_blocked",
    "sequence_review_rejected_or_excluded",
    "sequence_review_mismatch_still_blocked",
}
ALLOWED_DRY_RUN_PREFLIGHT_DECISIONS = {
    "approve_dry_run_preflight_for_planning",
    "defer_pending_dry_run_preflight_decision",
    "keep_blocked",
}
ALLOWED_DRY_RUN_PREFLIGHT_STATUSES = {
    "dry_run_preflight_planning_approved_runtime_blocked",
    "dry_run_preflight_decision_deferred_still_blocked",
    "dry_run_preflight_still_blocked",
}
ALLOWED_NEXT_ACTIONS_AFTER_DECISION = {
    "prepare_later_dry_run_preflight_manifest_pr",
    "defer_pending_dry_run_preflight_decision",
    "keep_blocked",
}
ALLOWED_CLAIM_POLICIES = {"no_biological_claims_until_validation"}
ALLOWED_CLAIM_STATUSES = {"technical_checkpoint", "repair_worklist"}


def empty_g3sx30_dry_run_preflight_decisions_table() -> pl.DataFrame:
    return pl.DataFrame(schema=G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA)


def validate_g3sx30_dry_run_preflight_decision_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required dry-run preflight decision columns: {missing}")


def _row_value(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        raise ValueError(f"Missing value for {column}")
    return str(value).strip()


def _expected_decision_values(
    *,
    dry_run_preflight_decision: DryRunPreflightDecision,
) -> tuple[str, str, str]:
    if dry_run_preflight_decision == "approve_dry_run_preflight_for_planning":
        return (
            "dry_run_preflight_planning_approved_runtime_blocked",
            "prepare_later_dry_run_preflight_manifest_pr",
            "technical_checkpoint",
        )
    if dry_run_preflight_decision == "defer_pending_dry_run_preflight_decision":
        return (
            "dry_run_preflight_decision_deferred_still_blocked",
            "defer_pending_dry_run_preflight_decision",
            "repair_worklist",
        )
    return (
        "dry_run_preflight_still_blocked",
        "keep_blocked",
        "repair_worklist",
    )


def validate_g3sx30_dry_run_preflight_decision_rows(table: pl.DataFrame) -> None:
    validate_g3sx30_dry_run_preflight_decision_schema(table)

    for row in table.iter_rows(named=True):
        source_table = _row_value(row, "source_target_sequence_review_decision_table")
        source_sequence_review_decision = _row_value(row, "source_sequence_review_decision")
        source_length_status = _row_value(row, "source_sequence_length_status_after_decision")
        source_provenance_status = _row_value(
            row,
            "source_provenance_review_status_after_decision",
        )
        source_decision_status = _row_value(row, "source_decision_status")
        source_downstream_block_status = _row_value(
            row,
            "source_downstream_block_status_after_decision",
        )
        dry_run_preflight_decision = _row_value(row, "dry_run_preflight_decision")
        dry_run_preflight_status = _row_value(
            row,
            "dry_run_preflight_status_after_decision",
        )
        allowed_next_action = _row_value(row, "allowed_next_action_after_decision")
        ready_for_preflight = _row_value(row, "ready_for_preflight_after_decision")
        claim_policy = _row_value(row, "claim_policy")
        claim_status = _row_value(row, "claim_status")

        if source_table not in ALLOWED_SOURCE_TABLES:
            raise ValueError(
                f"Invalid source_target_sequence_review_decision_table: {source_table}"
            )
        if source_sequence_review_decision not in ALLOWED_SOURCE_SEQUENCE_REVIEW_DECISIONS:
            raise ValueError(
                f"Invalid source_sequence_review_decision: {source_sequence_review_decision}"
            )
        if source_length_status not in ALLOWED_SOURCE_LENGTH_STATUSES:
            raise ValueError(
                f"Invalid source_sequence_length_status_after_decision: {source_length_status}"
            )
        if source_provenance_status not in ALLOWED_SOURCE_PROVENANCE_REVIEW_STATUSES:
            raise ValueError(
                "Invalid source_provenance_review_status_after_decision: "
                f"{source_provenance_status}"
            )
        if source_decision_status not in ALLOWED_SOURCE_DECISION_STATUSES:
            raise ValueError(f"Invalid source_decision_status: {source_decision_status}")
        if source_downstream_block_status not in ALLOWED_SOURCE_DOWNSTREAM_BLOCK_STATUSES:
            raise ValueError(
                "Invalid source_downstream_block_status_after_decision: "
                f"{source_downstream_block_status}"
            )
        if dry_run_preflight_decision not in ALLOWED_DRY_RUN_PREFLIGHT_DECISIONS:
            raise ValueError(f"Invalid dry_run_preflight_decision: {dry_run_preflight_decision}")
        if dry_run_preflight_status not in ALLOWED_DRY_RUN_PREFLIGHT_STATUSES:
            raise ValueError(
                f"Invalid dry_run_preflight_status_after_decision: {dry_run_preflight_status}"
            )
        if allowed_next_action not in ALLOWED_NEXT_ACTIONS_AFTER_DECISION:
            raise ValueError(f"Invalid allowed_next_action_after_decision: {allowed_next_action}")
        if claim_policy not in ALLOWED_CLAIM_POLICIES:
            raise ValueError(f"Invalid claim_policy: {claim_policy}")
        if claim_status not in ALLOWED_CLAIM_STATUSES:
            raise ValueError(f"Invalid claim_status: {claim_status}")

        expected_status, expected_next_action, expected_claim_status = _expected_decision_values(
            dry_run_preflight_decision=cast(
                DryRunPreflightDecision,
                dry_run_preflight_decision,
            )
        )
        if dry_run_preflight_status != expected_status:
            raise ValueError(
                "dry_run_preflight_status_after_decision does not match decision rule: "
                f"expected {expected_status}, got {dry_run_preflight_status}"
            )
        if allowed_next_action != expected_next_action:
            raise ValueError(
                "allowed_next_action_after_decision does not match decision rule: "
                f"expected {expected_next_action}, got {allowed_next_action}"
            )
        if claim_status != expected_claim_status:
            raise ValueError(
                "claim_status does not match decision rule: "
                f"expected {expected_claim_status}, got {claim_status}"
            )

        if dry_run_preflight_decision == "approve_dry_run_preflight_for_planning":
            if (
                source_sequence_review_decision
                != "approve_reviewed_sequence_provenance_for_planning"
            ):
                raise ValueError(
                    "approve_dry_run_preflight_for_planning requires approved "
                    "reviewed sequence provenance"
                )
            if source_length_status != "matches":
                raise ValueError(
                    "approve_dry_run_preflight_for_planning requires "
                    "source_sequence_length_status_after_decision=matches"
                )
            if source_provenance_status != "reviewed":
                raise ValueError(
                    "approve_dry_run_preflight_for_planning requires reviewed provenance"
                )
            if source_decision_status != "reviewed_for_planning_still_preflight_blocked":
                raise ValueError(
                    "approve_dry_run_preflight_for_planning requires "
                    "reviewed_for_planning_still_preflight_blocked source decision"
                )

        if ready_for_preflight.lower() != "false":
            raise ValueError("dry-run preflight decisions must not mark ready_for_preflight")

        max_live_batch_size = int(row["max_live_batch_size_after_decision"])
        if max_live_batch_size != 0:
            raise ValueError("dry-run preflight decisions require max_live_batch_size=0")

        forbidden_actions = _row_value(row, "forbidden_actions")
        for required in [
            "sequence fetch",
            "Biohub call",
            "ESMC call",
            "embedding generation",
            "curated_embedding_preflight run",
            "curated_embedding_single run",
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
