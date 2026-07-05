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
SOURCE_PROVENANCE_PATH = ROOT / "data/input/reviewed_target_sequence_provenance.csv"

REVIEWED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_table() -> pl.DataFrame:
    return pl.read_csv(TABLE_PATH)


def deferred_row() -> dict[str, object]:
    return load_table().row(0, named=True)


def approval_row() -> dict[str, object]:
    return load_table().row(1, named=True)


def test_target_sequence_review_decision_schema_records_g3sx30_approval_row() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "target_sequence_review_decision_schema"
    assert schema["pipeline_gate"] == "target_sequence_review_decision"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "technical_checkpoint"
    assert schema["scaffold_scope"]["source_layer"] == "reviewed_target_sequence_provenance"
    assert schema["scaffold_scope"]["source_table"] == (
        "data/input/reviewed_target_sequence_provenance.csv"
    )
    assert (
        schema["scaffold_scope"]["scaffold_status"]
        == "one_g3sx30_deferred_decision_row_plus_one_reviewed_approval_decision_row"
    )
    assert schema["scaffold_scope"]["current_g3sx30_source_sequence_provenance_row_index"] == 2
    assert (
        schema["scaffold_scope"]["current_g3sx30_sequence_review_decision"]
        == "approve_reviewed_sequence_provenance_for_planning"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_decision_status"]
        == "reviewed_for_planning_still_preflight_blocked"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_downstream_block_status_after_decision"]
        == "sequence_reviewed_still_preflight_decision_blocked"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_allowed_next_action_after_decision"]
        == "consider_later_dry_run_preflight_decision_pr"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_sequence_review_status"]
        == "reviewed_sequence_provenance"
    )
    assert schema["scaffold_scope"]["current_g3sx30_sequence_length_status"] == "matches"
    assert schema["scaffold_scope"]["current_g3sx30_provenance_review_status"] == "reviewed"
    assert schema["scaffold_scope"]["current_g3sx30_reviewed_sequence_length"] == 492
    assert schema["scaffold_scope"]["current_g3sx30_reviewed_sequence_sha256"] == (
        REVIEWED_SEQUENCE_SHA256
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_runtime_status_after_decision"]
        == "still_not_ready_for_preflight"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_controlled_worklist_allowed_next_action"]
        == "keep_blocked"
    )


def test_target_sequence_review_decision_schema_required_columns_match_helper() -> None:
    schema = load_schema()

    assert schema["required_columns"] == REQUIRED_COLUMNS
    assert list(TARGET_SEQUENCE_REVIEW_DECISION_SCHEMA) == REQUIRED_COLUMNS


def test_target_sequence_review_decision_table_has_deferred_and_approval_rows() -> None:
    table = load_table()

    assert table.columns == REQUIRED_COLUMNS
    assert table.height == 2
    validate_target_sequence_review_decision_schema(table)
    validate_target_sequence_review_decision_rows(table)


def test_g3sx30_deferred_decision_row_is_preserved() -> None:
    row = deferred_row()

    assert row["target_accession"] == "G3SX30"
    assert row["source_sequence_provenance_row_index"] == 1
    assert row["sequence_review_decision"] == "defer_pending_sequence_review"
    assert row["sequence_length_status_after_decision"] == "not_fetched"
    assert row["provenance_review_status_after_decision"] == "deferred"
    assert row["reviewed_sequence_sha256"] == "not_applicable_not_fetched"
    assert row["reviewed_sequence_length"] == 0
    assert row["decision_status"] == "deferred_pending_review"
    assert row["downstream_block_status_after_decision"] == "sequence_review_deferred_still_blocked"
    assert row["allowed_next_action_after_decision"] == "defer_pending_sequence_review"
    assert row["claim_status"] == "repair_worklist"


def test_g3sx30_approval_decision_row_records_reviewed_sequence_approval_for_planning() -> None:
    row = approval_row()

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["lane_name"] == "tp53_mdm2_elephant"
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["source_sequence_provenance_table"] == (
        "data/input/reviewed_target_sequence_provenance.csv"
    )
    assert row["source_sequence_provenance_row_index"] == 2
    assert row["target_accession"] == "G3SX30"
    assert row["target_accession_db"] == "UniProtKB TrEMBL"
    assert row["target_species"] == "Loxodonta africana"
    assert row["target_taxid"] == 9785
    assert row["gene_symbol"] == "MDM2"
    assert row["sequence_review_decision"] == ("approve_reviewed_sequence_provenance_for_planning")
    assert row["sequence_length_status_after_decision"] == "matches"
    assert row["provenance_review_status_after_decision"] == "reviewed"
    assert row["reviewed_sequence_sha256"] == REVIEWED_SEQUENCE_SHA256
    assert row["reviewed_sequence_length"] == 492
    assert row["decision_status"] == "reviewed_for_planning_still_preflight_blocked"
    assert row["downstream_block_status_after_decision"] == (
        "sequence_reviewed_still_preflight_decision_blocked"
    )
    assert row["allowed_next_action_after_decision"] == (
        "consider_later_dry_run_preflight_decision_pr"
    )
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "technical_checkpoint"
    assert row["reviewer_id"] == "manual_official_source_review"
    assert row["review_date"] == "2026-07-05"


def test_g3sx30_approval_decision_row_matches_reviewed_source_sequence_provenance_row() -> None:
    row = approval_row()
    source_table = pl.read_csv(SOURCE_PROVENANCE_PATH)
    source_row = source_table.row(row["source_sequence_provenance_row_index"] - 1, named=True)

    assert source_row["candidate_set"] == row["candidate_set"]
    assert source_row["lane_name"] == row["lane_name"]
    assert source_row["candidate_id"] == row["candidate_id"]
    assert source_row["target_accession"] == row["target_accession"]
    assert source_row["target_accession_db"] == row["target_accession_db"]
    assert source_row["target_species"] == row["target_species"]
    assert source_row["target_taxid"] == row["target_taxid"]
    assert source_row["gene_symbol"] == row["gene_symbol"]
    assert source_row["sequence_source_type"] == "reviewed_external_database_record"
    assert source_row["sequence_length_status"] == "matches"
    assert source_row["sequence_review_status"] == "reviewed_sequence_provenance"
    assert source_row["provenance_review_status"] == "reviewed"
    assert source_row["allowed_next_action_after_sequence_review"] == (
        "consider_later_dry_run_preflight_decision_pr"
    )
    assert source_row["reviewed_sequence_length"] == row["reviewed_sequence_length"] == 492
    assert source_row["reviewed_sequence_sha256"] == row["reviewed_sequence_sha256"]


def test_g3sx30_deferred_decision_row_does_not_record_reviewed_sequence() -> None:
    row = deferred_row()

    assert row["sequence_review_decision"] != "approve_reviewed_sequence_provenance_for_planning"
    assert row["sequence_length_status_after_decision"] != "matches"
    assert row["provenance_review_status_after_decision"] != "reviewed"
    assert row["decision_status"] != "reviewed_for_planning_still_preflight_blocked"
    assert row["allowed_next_action_after_decision"] != (
        "consider_later_dry_run_preflight_decision_pr"
    )
    assert row["reviewed_sequence_length"] == 0
    assert row["reviewed_sequence_sha256"] == "not_applicable_not_fetched"
    assert row["claim_status"] == "repair_worklist"


def test_g3sx30_approval_decision_row_forbids_runtime_side_effects() -> None:
    row = approval_row()
    forbidden_actions = row["forbidden_actions"]

    for required in [
        "sequence fetch",
        "source provenance row mutation",
        "Biohub call",
        "ESMC call",
        "embedding generation",
        "curated_embedding_preflight",
        "curated_embedding_single",
        "data/output commit",
        ".npy artifact",
        "ready_for_preflight",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "Boltz call",
        "AF3 call",
        "Chai call",
        "enrichment rerun",
        "contrast rerun",
        "biological claim",
    ]:
        assert required in forbidden_actions


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
