from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages.g3sx30_dry_run_preflight_decisions import (
    FORBIDDEN_ACTIONS,
    G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA,
    REQUIRED_COLUMNS,
    empty_g3sx30_dry_run_preflight_decisions_table,
    validate_g3sx30_dry_run_preflight_decision_rows,
    validate_g3sx30_dry_run_preflight_decision_schema,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/g3sx30_dry_run_preflight_decision_schema.yaml"
TABLE_PATH = ROOT / "data/input/g3sx30_dry_run_preflight_decisions.csv"
SOURCE_DECISIONS_PATH = ROOT / "data/input/target_sequence_review_decisions.csv"

REVIEWED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_g3sx30_dry_run_preflight_decision_schema_records_header_only_scaffold() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "g3sx30_dry_run_preflight_decision_schema"
    assert schema["pipeline_gate"] == "g3sx30_dry_run_preflight_decision"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"
    assert schema["scaffold_scope"]["source_layer"] == "target_sequence_review_decision"
    assert schema["scaffold_scope"]["source_table"] == (
        "data/input/target_sequence_review_decisions.csv"
    )
    assert schema["scaffold_scope"]["source_row_index"] == 2
    assert (
        schema["scaffold_scope"]["scaffold_status"]
        == "header_only_no_committed_g3sx30_dry_run_preflight_decision_row"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_source_sequence_review_decision"]
        == "approve_reviewed_sequence_provenance_for_planning"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_source_sequence_length_status_after_decision"]
        == "matches"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_source_decision_status"]
        == "reviewed_for_planning_still_preflight_blocked"
    )
    assert schema["scaffold_scope"]["current_g3sx30_reviewed_sequence_length"] == 492
    assert schema["scaffold_scope"]["current_g3sx30_reviewed_sequence_sha256"] == (
        REVIEWED_SEQUENCE_SHA256
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_dry_run_preflight_decision_status"]
        == "no_committed_decision_row_yet"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_runtime_status_after_scaffold"]
        == "still_not_ready_for_preflight"
    )


def test_g3sx30_dry_run_preflight_decision_schema_required_columns_match_helper() -> None:
    schema = load_schema()

    assert schema["required_columns"] == REQUIRED_COLUMNS
    assert list(G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA) == REQUIRED_COLUMNS


def test_g3sx30_dry_run_preflight_decision_table_is_header_only() -> None:
    table = pl.read_csv(TABLE_PATH)

    assert table.columns == REQUIRED_COLUMNS
    assert table.height == 0
    validate_g3sx30_dry_run_preflight_decision_schema(table)
    validate_g3sx30_dry_run_preflight_decision_rows(table)


def test_g3sx30_dry_run_preflight_source_decision_row_is_reviewed_and_still_blocked() -> None:
    source_table = pl.read_csv(SOURCE_DECISIONS_PATH)
    source_row = source_table.row(1, named=True)

    assert source_row["target_accession"] == "G3SX30"
    assert source_row["source_sequence_provenance_row_index"] == 2
    assert source_row["sequence_review_decision"] == (
        "approve_reviewed_sequence_provenance_for_planning"
    )
    assert source_row["sequence_length_status_after_decision"] == "matches"
    assert source_row["provenance_review_status_after_decision"] == "reviewed"
    assert source_row["reviewed_sequence_length"] == 492
    assert source_row["reviewed_sequence_sha256"] == REVIEWED_SEQUENCE_SHA256
    assert source_row["decision_status"] == "reviewed_for_planning_still_preflight_blocked"
    assert source_row["downstream_block_status_after_decision"] == (
        "sequence_reviewed_still_preflight_decision_blocked"
    )
    assert source_row["allowed_next_action_after_decision"] == (
        "consider_later_dry_run_preflight_decision_pr"
    )


def synthetic_approval_row() -> dict[str, object]:
    return {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2_elephant",
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "source_target_sequence_review_decision_table": (
            "data/input/target_sequence_review_decisions.csv"
        ),
        "source_target_sequence_review_decision_row_index": 2,
        "target_accession": "G3SX30",
        "target_accession_db": "UniProtKB TrEMBL",
        "target_species": "Loxodonta africana",
        "target_taxid": 9785,
        "gene_symbol": "MDM2",
        "source_sequence_review_decision": ("approve_reviewed_sequence_provenance_for_planning"),
        "source_sequence_length_status_after_decision": "matches",
        "source_provenance_review_status_after_decision": "reviewed",
        "source_decision_status": "reviewed_for_planning_still_preflight_blocked",
        "source_downstream_block_status_after_decision": (
            "sequence_reviewed_still_preflight_decision_blocked"
        ),
        "reviewed_sequence_sha256": REVIEWED_SEQUENCE_SHA256,
        "reviewed_sequence_length": 492,
        "dry_run_preflight_decision": "approve_dry_run_preflight_for_planning",
        "dry_run_preflight_status_after_decision": (
            "dry_run_preflight_planning_approved_runtime_blocked"
        ),
        "allowed_next_action_after_decision": "prepare_later_dry_run_preflight_manifest_pr",
        "max_live_batch_size_after_decision": 0,
        "ready_for_preflight_after_decision": "false",
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "technical_checkpoint",
        "review_note": "Synthetic fixture only; not a committed G3SX30 row.",
        "reviewer_id": "synthetic_fixture_reviewer",
        "review_date": "not_applicable_fixture",
        "forbidden_actions": FORBIDDEN_ACTIONS,
    }


def test_g3sx30_dry_run_preflight_validator_accepts_synthetic_approval_row() -> None:
    table = pl.DataFrame(
        [synthetic_approval_row()],
        schema=G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA,
    )

    validate_g3sx30_dry_run_preflight_decision_rows(table)


def test_g3sx30_dry_run_preflight_validator_blocks_approval_without_reviewed_source() -> None:
    row = synthetic_approval_row()
    row["source_sequence_review_decision"] = "defer_pending_sequence_review"
    table = pl.DataFrame([row], schema=G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA)

    with pytest.raises(ValueError, match="requires approved reviewed sequence provenance"):
        validate_g3sx30_dry_run_preflight_decision_rows(table)


def test_g3sx30_dry_run_preflight_validator_blocks_ready_for_preflight() -> None:
    row = synthetic_approval_row()
    row["ready_for_preflight_after_decision"] = "true"
    table = pl.DataFrame([row], schema=G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA)

    with pytest.raises(ValueError, match="must not mark ready_for_preflight"):
        validate_g3sx30_dry_run_preflight_decision_rows(table)


def test_g3sx30_dry_run_preflight_validator_blocks_live_batch_size() -> None:
    row = synthetic_approval_row()
    row["max_live_batch_size_after_decision"] = 1
    table = pl.DataFrame([row], schema=G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA)

    with pytest.raises(ValueError, match="max_live_batch_size=0"):
        validate_g3sx30_dry_run_preflight_decision_rows(table)


def test_empty_g3sx30_dry_run_preflight_decisions_table_matches_schema() -> None:
    table = empty_g3sx30_dry_run_preflight_decisions_table()

    assert table.columns == REQUIRED_COLUMNS
    assert table.schema == G3SX30_DRY_RUN_PREFLIGHT_DECISION_SCHEMA
    assert table.height == 0


def test_g3sx30_dry_run_preflight_schema_never_authorizes_runtime() -> None:
    schema = load_schema()
    forbidden = set(schema["scaffold_scope"]["does_not_authorize"])

    for required in [
        "sequence fetch",
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
        assert rule["ready_for_preflight_after_decision"] == "false"
        assert rule["max_live_batch_size_after_decision"] == 0
        assert rule["run_curated_embedding_preflight"] is False
        assert rule["run_curated_embedding_single"] is False
        assert rule["embedding_ready"] is False
        assert rule["biohub_ready"] is False
        assert rule["live_call_ready"] is False
        assert rule["gate8_eligible"] is False
        assert rule["gate9_eligible"] is False
        assert rule["boltz_ready"] is False
        assert rule["af3_ready"] is False
        assert rule["chai_ready"] is False
        assert rule["biological_claim_allowed"] is False
