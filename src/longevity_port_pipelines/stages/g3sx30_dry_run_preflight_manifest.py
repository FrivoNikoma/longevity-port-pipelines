from __future__ import annotations

import polars as pl

FORBIDDEN_ACTIONS = (
    "sequence fetch; Biohub call; ESMC call; embedding generation; "
    "curated_embedding_preflight run; curated_embedding_single run; data/output commit; "
    ".npy artifact; ready_for_preflight; Gate 8 promotion; Gate 9 promotion; "
    "Boltz call; AF3 call; Chai call; enrichment rerun; contrast rerun; biological claim"
)

REQUIRED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "source_dry_run_preflight_decision_table",
    "source_dry_run_preflight_decision_row_index",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "source_dry_run_preflight_decision",
    "source_dry_run_preflight_status_after_decision",
    "source_allowed_next_action_after_decision",
    "source_max_live_batch_size_after_decision",
    "source_ready_for_preflight_after_decision",
    "reviewed_sequence_sha256",
    "reviewed_sequence_length",
    "manifest_entry_status",
    "dry_run_only",
    "max_live_batch_size",
    "ready_for_preflight_after_manifest",
    "sequence_fetch_allowed",
    "biohub_call_allowed",
    "esmc_call_allowed",
    "embedding_generation_allowed",
    "curated_embedding_preflight_allowed",
    "curated_embedding_single_allowed",
    "claim_policy",
    "claim_status",
    "review_note",
    "reviewer_id",
    "review_date",
    "forbidden_actions",
]

G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "source_dry_run_preflight_decision_table": pl.Utf8,
    "source_dry_run_preflight_decision_row_index": pl.Int64,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "source_dry_run_preflight_decision": pl.Utf8,
    "source_dry_run_preflight_status_after_decision": pl.Utf8,
    "source_allowed_next_action_after_decision": pl.Utf8,
    "source_max_live_batch_size_after_decision": pl.Int64,
    "source_ready_for_preflight_after_decision": pl.Utf8,
    "reviewed_sequence_sha256": pl.Utf8,
    "reviewed_sequence_length": pl.Int64,
    "manifest_entry_status": pl.Utf8,
    "dry_run_only": pl.Boolean,
    "max_live_batch_size": pl.Int64,
    "ready_for_preflight_after_manifest": pl.Utf8,
    "sequence_fetch_allowed": pl.Boolean,
    "biohub_call_allowed": pl.Boolean,
    "esmc_call_allowed": pl.Boolean,
    "embedding_generation_allowed": pl.Boolean,
    "curated_embedding_preflight_allowed": pl.Boolean,
    "curated_embedding_single_allowed": pl.Boolean,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "review_note": pl.Utf8,
    "reviewer_id": pl.Utf8,
    "review_date": pl.Utf8,
    "forbidden_actions": pl.Utf8,
}

ALLOWED_SOURCE_TABLES = {"data/input/g3sx30_dry_run_preflight_decisions.csv"}
ALLOWED_SOURCE_DRY_RUN_PREFLIGHT_DECISIONS = {"approve_dry_run_preflight_for_planning"}
ALLOWED_SOURCE_DRY_RUN_PREFLIGHT_STATUSES = {"dry_run_preflight_planning_approved_runtime_blocked"}
ALLOWED_SOURCE_NEXT_ACTIONS = {"prepare_later_dry_run_preflight_manifest_pr"}
ALLOWED_MANIFEST_ENTRY_STATUSES = {
    "manifest_scaffold_ready_runtime_blocked",
    "manifest_entry_deferred_still_blocked",
}
ALLOWED_CLAIM_POLICIES = {"no_biological_claims_until_validation"}
ALLOWED_CLAIM_STATUSES = {"technical_checkpoint", "repair_worklist"}


def empty_g3sx30_dry_run_preflight_manifest_table() -> pl.DataFrame:
    return pl.DataFrame(schema=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)


def validate_g3sx30_dry_run_preflight_manifest_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required dry-run preflight manifest columns: {missing}")


def _row_value(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        raise ValueError(f"Missing value for {column}")
    return str(value).strip()


def _row_bool(row: dict[str, object], column: str) -> bool:
    value = row[column]
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError(f"Invalid boolean value for {column}: {value}")


def validate_g3sx30_dry_run_preflight_manifest_rows(table: pl.DataFrame) -> None:
    validate_g3sx30_dry_run_preflight_manifest_schema(table)

    for row in table.iter_rows(named=True):
        source_table = _row_value(row, "source_dry_run_preflight_decision_table")
        source_decision = _row_value(row, "source_dry_run_preflight_decision")
        source_status = _row_value(
            row,
            "source_dry_run_preflight_status_after_decision",
        )
        source_next_action = _row_value(row, "source_allowed_next_action_after_decision")
        source_ready_for_preflight = _row_value(
            row,
            "source_ready_for_preflight_after_decision",
        )
        manifest_status = _row_value(row, "manifest_entry_status")
        ready_for_preflight_after_manifest = _row_value(
            row,
            "ready_for_preflight_after_manifest",
        )
        claim_policy = _row_value(row, "claim_policy")
        claim_status = _row_value(row, "claim_status")

        if source_table not in ALLOWED_SOURCE_TABLES:
            raise ValueError(f"Invalid source_dry_run_preflight_decision_table: {source_table}")
        if source_decision not in ALLOWED_SOURCE_DRY_RUN_PREFLIGHT_DECISIONS:
            raise ValueError(f"Invalid source_dry_run_preflight_decision: {source_decision}")
        if source_status not in ALLOWED_SOURCE_DRY_RUN_PREFLIGHT_STATUSES:
            raise ValueError(
                f"Invalid source_dry_run_preflight_status_after_decision: {source_status}"
            )
        if source_next_action not in ALLOWED_SOURCE_NEXT_ACTIONS:
            raise ValueError(
                f"Invalid source_allowed_next_action_after_decision: {source_next_action}"
            )
        if source_ready_for_preflight.lower() != "false":
            raise ValueError("source row must remain not ready_for_preflight")
        if manifest_status not in ALLOWED_MANIFEST_ENTRY_STATUSES:
            raise ValueError(f"Invalid manifest_entry_status: {manifest_status}")
        if claim_policy not in ALLOWED_CLAIM_POLICIES:
            raise ValueError(f"Invalid claim_policy: {claim_policy}")
        if claim_status not in ALLOWED_CLAIM_STATUSES:
            raise ValueError(f"Invalid claim_status: {claim_status}")

        if int(row["source_max_live_batch_size_after_decision"]) != 0:
            raise ValueError("source max live batch size must be 0")
        if int(row["max_live_batch_size"]) != 0:
            raise ValueError("dry-run preflight manifest requires max_live_batch_size=0")

        if not _row_bool(row, "dry_run_only"):
            raise ValueError("dry-run preflight manifest requires dry_run_only=true")
        if ready_for_preflight_after_manifest.lower() != "false":
            raise ValueError("dry-run preflight manifest must not mark ready_for_preflight")

        for column in [
            "sequence_fetch_allowed",
            "biohub_call_allowed",
            "esmc_call_allowed",
            "embedding_generation_allowed",
            "curated_embedding_preflight_allowed",
            "curated_embedding_single_allowed",
        ]:
            if _row_bool(row, column):
                raise ValueError(f"dry-run preflight manifest must not allow {column}")

        forbidden_actions = _row_value(row, "forbidden_actions")
        for required in [
            "sequence fetch",
            "Biohub call",
            "ESMC call",
            "embedding generation",
            "curated_embedding_preflight run",
            "curated_embedding_single run",
            "data/output commit",
            ".npy artifact",
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
