from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages.target_sequence_review_decisions import (
    FORBIDDEN_ACTIONS,
    REQUIRED_COLUMNS,
    TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA,
    empty_target_sequence_review_decisions_table,
    validate_target_sequence_review_decision_rows,
    validate_target_sequence_review_decision_schema,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/target_sequence_review_decision_schema.yaml"
TABLE_PATH = ROOT / "data/input/target_sequence_review_decisions.csv"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_target_sequence_review_decision_schema_is_header_only_scaffold() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "target_sequence_review_decision_schema"
    assert schema["pipeline_gate"] == "target_sequence_review_decision"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "technical_checkpoint"
    assert schema["scaffold_scope"]["source_layer"] == "reviewed_target_sequence_provenance"
    assert schema["scaffold_scope"]["source_table"] == (
        "data/input/reviewed_target_sequence_provenance.csv"
    )
    assert schema["scaffold_scope"]["checklist_source"] == (
        "docs/g3sx30_target_sequence_review_checklist.md"
    )
    assert schema["scaffold_scope"]["scaffold_status"] == "header_only_no_rows"
    assert (
        schema["scaffold_scope"]["current_g3sx30_sequence_review_status"]
        == "deferred_pending_review"
    )
    assert schema["scaffold_scope"]["current_g3sx30_sequence_length_status"] == "not_fetched"
    assert schema["scaffold_scope"]["current_g3sx30_provenance_review_status"] == "deferred"
    assert (
        schema["scaffold_scope"]["current_g3sx30_controlled_worklist_allowed_next_action"]
        == "keep_blocked"
    )


def test_target_sequence_review_decision_schema_required_columns_match_helper() -> None:
    schema = load_schema()

    assert schema["required_columns"] == REQUIRED_COLUMNS
    assert list(TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA) == REQUIRED_COLUMNS


def test_target_sequence_review_decision_table_is_header_only() -> None:
    table = pl.read_csv(TABLE_PATH)

    assert table.columns == REQUIRED_COLUMNS
    assert table.height == 0
    validate_target_sequence_review_decision_schema(table)
    validate_target_sequence_review_decision_rows(table)


def test_empty_target_sequence_review_decisions_table_matches_schema() -> None:
    table = empty_target_sequence_review_decisions_table()

    assert table.columns == REQUIRED_COLUMNS
    assert table.schema == TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA
    assert table.height == 0


def test_target_sequence_review_decision_schema_never_authorizes_runtime() -> None:
    schema = load_schema()
    forbidden = set(schema["scaffold_scope"]["does_not_authorize"])

    for required in [
        "sequence fetch",
        "source provenance row mutation",
        "Biohub calls",
        "ESMC calls",
        "embedding generation",
        "curated_embedding_preflight",
        "curated_embedding_single",
        "ready_for_preflight",
        "data/output commits",
        ".npy artifacts",
        "Gate 8 eligibility",
        "Gate 9 eligibility",
        "Boltz calls",
        "AF3 calls",
        "Chai calls",
        "enrichment rerun",
        "contrast rerun",
        "biological claims",
    ]:
        assert required in forbidden

    for rule in schema["decision_rules"].values():
        assert rule["mutates_source_sequence_provenance_row"] is False
        assert rule["ready_for_preflight"] is False
        assert rule["embedding_ready"] is False
        assert rule["biohub_ready"] is False
        assert rule["live_call_ready"] is False
        assert rule["gate8_eligible"] is False
        assert rule["gate9_eligible"] is False
        assert rule["boltz_ready"] is False
        assert rule["af3_ready"] is False
        assert rule["chai_ready"] is False
        assert rule["biological_claim_allowed"] is False


def synthetic_base_row() -> dict[str, object]:
    return {
        "candidate_set": "fixture_candidate_set",
        "lane_name": "fixture_lane",
        "candidate_id": "fixture_candidate",
        "source_sequence_provenance_table": ("data/input/reviewed_target_sequence_provenance.csv"),
        "source_sequence_provenance_row_index": 1,
        "target_accession": "FIXTURE_ACCESSION",
        "target_accession_db": "UniProtKB TrEMBL",
        "target_species": "fixture_species",
        "target_taxid": 1,
        "gene_symbol": "FIXTURE",
        "sequence_review_decision": "defer_pending_sequence_review",
        "sequence_length_status_after_decision": "not_fetched",
        "provenance_review_status_after_decision": "deferred",
        "reviewed_sequence_sha256": "not_applicable_not_fetched",
        "reviewed_sequence_length": 0,
        "decision_status": "deferred_pending_review",
        "downstream_block_status_after_decision": "sequence_review_deferred_still_blocked",
        "allowed_next_action_after_decision": "defer_pending_sequence_review",
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "repair_worklist",
        "review_note": "Synthetic fixture only; not a committed G3SX30 row.",
        "reviewer_id": "synthetic_fixture_reviewer",
        "review_date": "not_applicable_fixture",
        "forbidden_actions": FORBIDDEN_ACTIONS,
    }


def test_target_sequence_review_decision_validator_accepts_synthetic_defer_row() -> None:
    table = pl.DataFrame(
        [synthetic_base_row()],
        schema=TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA,
    )

    validate_target_sequence_review_decision_rows(table)


def test_target_sequence_review_decision_validator_accepts_synthetic_approval_row() -> None:
    row = synthetic_base_row()
    row.update(
        {
            "sequence_review_decision": "approve_reviewed_sequence_provenance_for_planning",
            "sequence_length_status_after_decision": "matches",
            "provenance_review_status_after_decision": "reviewed",
            "reviewed_sequence_sha256": "0" * 64,
            "reviewed_sequence_length": 1,
            "decision_status": "reviewed_for_planning_still_preflight_blocked",
            "downstream_block_status_after_decision": (
                "sequence_reviewed_still_preflight_decision_blocked"
            ),
            "allowed_next_action_after_decision": ("consider_later_dry_run_preflight_decision_pr"),
            "claim_status": "technical_checkpoint",
        }
    )
    table = pl.DataFrame([row], schema=TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA)

    validate_target_sequence_review_decision_rows(table)


def test_target_sequence_review_decision_validator_blocks_approval_without_matches() -> None:
    row = synthetic_base_row()
    row.update(
        {
            "sequence_review_decision": "approve_reviewed_sequence_provenance_for_planning",
            "sequence_length_status_after_decision": "mismatch",
            "provenance_review_status_after_decision": "reviewed",
            "decision_status": "keep_blocked_after_mismatch",
            "downstream_block_status_after_decision": "sequence_review_mismatch_still_blocked",
            "allowed_next_action_after_decision": "keep_blocked",
        }
    )
    table = pl.DataFrame([row], schema=TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA)

    with pytest.raises(
        ValueError,
        match="approve_reviewed_sequence_provenance_for_planning requires",
    ):
        validate_target_sequence_review_decision_rows(table)


def test_target_sequence_review_decision_validator_accepts_mismatch_blocker_row() -> None:
    row = synthetic_base_row()
    row.update(
        {
            "sequence_review_decision": "keep_blocked_after_mismatch",
            "sequence_length_status_after_decision": "mismatch",
            "provenance_review_status_after_decision": "needs_review",
            "decision_status": "keep_blocked_after_mismatch",
            "downstream_block_status_after_decision": "sequence_review_mismatch_still_blocked",
            "allowed_next_action_after_decision": "keep_blocked",
        }
    )
    table = pl.DataFrame([row], schema=TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA)

    validate_target_sequence_review_decision_rows(table)


def test_target_sequence_review_decision_validator_rejects_missing_columns() -> None:
    table = pl.DataFrame({"candidate_set": ["fixture"]})

    with pytest.raises(ValueError, match="Missing required"):
        validate_target_sequence_review_decision_schema(table)
