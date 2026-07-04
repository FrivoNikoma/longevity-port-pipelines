from __future__ import annotations

from typing import Literal, cast

import polars as pl

FORBIDDEN_ACTIONS = (
    "sequence fetch; Biohub call; ESMC call; embedding generation; "
    "curated_embedding_preflight; curated_embedding_single; data/output commit; "
    ".npy artifact; Gate 8 promotion; Gate 9 promotion; Boltz call; AF3 call; Chai call; "
    "enrichment rerun; contrast rerun; biological claim"
)

SequenceLengthStatus = Literal["matches", "mismatch", "not_checked", "not_fetched"]
SequenceReviewStatus = Literal[
    "reviewed_sequence_provenance",
    "rejected_sequence_provenance",
    "deferred_pending_review",
]

REQUIRED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "source_policy_table",
    "source_policy_row_index",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "sequence_source_type",
    "sequence_source_reference",
    "reviewed_sequence_sha256",
    "reviewed_sequence_length",
    "sequence_length_status",
    "sequence_review_status",
    "provenance_review_status",
    "allowed_next_action_after_sequence_review",
    "claim_policy",
    "claim_status",
    "review_note",
    "forbidden_actions",
]

REVIEWED_TARGET_SEQUENCE_PROVENANCE_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "source_policy_table": pl.Utf8,
    "source_policy_row_index": pl.Int64,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "sequence_source_type": pl.Utf8,
    "sequence_source_reference": pl.Utf8,
    "reviewed_sequence_sha256": pl.Utf8,
    "reviewed_sequence_length": pl.Int64,
    "sequence_length_status": pl.Utf8,
    "sequence_review_status": pl.Utf8,
    "provenance_review_status": pl.Utf8,
    "allowed_next_action_after_sequence_review": pl.Utf8,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "review_note": pl.Utf8,
    "forbidden_actions": pl.Utf8,
}

ALLOWED_SEQUENCE_LENGTH_STATUSES = {"matches", "mismatch", "not_checked", "not_fetched"}
ALLOWED_SEQUENCE_REVIEW_STATUSES = {
    "reviewed_sequence_provenance",
    "rejected_sequence_provenance",
    "deferred_pending_review",
}
ALLOWED_PROVENANCE_REVIEW_STATUSES = {"reviewed", "rejected", "needs_review", "deferred"}
ALLOWED_NEXT_ACTIONS_AFTER_SEQUENCE_REVIEW = {
    "consider_later_dry_run_preflight_decision_pr",
    "keep_blocked",
    "defer_pending_sequence_review",
    "reject_or_exclude_sequence_source",
}
ALLOWED_CLAIM_POLICIES = {"no_biological_claims_until_validation"}
ALLOWED_CLAIM_STATUSES = {"technical_checkpoint", "repair_worklist"}


def empty_reviewed_target_sequence_provenance_table() -> pl.DataFrame:
    return pl.DataFrame(schema=REVIEWED_TARGET_SEQUENCE_PROVENANCE_SCHEMA)


def validate_reviewed_target_sequence_provenance_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required reviewed target sequence provenance columns: {missing}")


def _row_value(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        raise ValueError(f"Missing value for {column}")
    return str(value).strip()


def _allowed_next_action(
    *,
    sequence_review_status: SequenceReviewStatus,
    sequence_length_status: SequenceLengthStatus,
) -> str:
    if sequence_review_status == "reviewed_sequence_provenance":
        if sequence_length_status != "matches":
            return "keep_blocked"
        return "consider_later_dry_run_preflight_decision_pr"
    if sequence_review_status == "rejected_sequence_provenance":
        return "reject_or_exclude_sequence_source"
    return "defer_pending_sequence_review"


def validate_reviewed_target_sequence_provenance_rows(table: pl.DataFrame) -> None:
    validate_reviewed_target_sequence_provenance_schema(table)

    for row in table.iter_rows(named=True):
        sequence_length_status = _row_value(row, "sequence_length_status")
        sequence_review_status = _row_value(row, "sequence_review_status")
        provenance_review_status = _row_value(row, "provenance_review_status")
        allowed_next_action = _row_value(row, "allowed_next_action_after_sequence_review")
        claim_policy = _row_value(row, "claim_policy")
        claim_status = _row_value(row, "claim_status")

        if sequence_length_status not in ALLOWED_SEQUENCE_LENGTH_STATUSES:
            raise ValueError(f"Invalid sequence_length_status: {sequence_length_status}")
        if sequence_review_status not in ALLOWED_SEQUENCE_REVIEW_STATUSES:
            raise ValueError(f"Invalid sequence_review_status: {sequence_review_status}")
        if provenance_review_status not in ALLOWED_PROVENANCE_REVIEW_STATUSES:
            raise ValueError(f"Invalid provenance_review_status: {provenance_review_status}")
        if allowed_next_action not in ALLOWED_NEXT_ACTIONS_AFTER_SEQUENCE_REVIEW:
            raise ValueError(
                f"Invalid allowed_next_action_after_sequence_review: {allowed_next_action}"
            )
        if claim_policy not in ALLOWED_CLAIM_POLICIES:
            raise ValueError(f"Invalid claim_policy: {claim_policy}")
        if claim_status not in ALLOWED_CLAIM_STATUSES:
            raise ValueError(f"Invalid claim_status: {claim_status}")

        expected_next_action = _allowed_next_action(
            sequence_review_status=cast(SequenceReviewStatus, sequence_review_status),
            sequence_length_status=cast(SequenceLengthStatus, sequence_length_status),
        )
        if allowed_next_action != expected_next_action:
            raise ValueError(
                "allowed_next_action_after_sequence_review does not match "
                f"decision rule: expected {expected_next_action}, got {allowed_next_action}"
            )

        if sequence_review_status == "reviewed_sequence_provenance":
            if sequence_length_status != "matches":
                raise ValueError(
                    "reviewed_sequence_provenance requires sequence_length_status=matches"
                )
            if provenance_review_status != "reviewed":
                raise ValueError("reviewed_sequence_provenance requires reviewed provenance")

        forbidden_actions = _row_value(row, "forbidden_actions")
        for required in [
            "sequence fetch",
            "Biohub call",
            "ESMC call",
            "embedding generation",
            "Gate 8 promotion",
            "Gate 9 promotion",
            "Boltz call",
            "AF3 call",
            "Chai call",
            "biological claim",
        ]:
            if required not in forbidden_actions:
                raise ValueError(f"Missing forbidden action guardrail: {required}")
