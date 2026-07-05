from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages.g3sx30_dry_run_preflight_manifest import (
    FORBIDDEN_ACTIONS,
    G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA,
    REQUIRED_COLUMNS,
    empty_g3sx30_dry_run_preflight_manifest_table,
    validate_g3sx30_dry_run_preflight_manifest_rows,
    validate_g3sx30_dry_run_preflight_manifest_schema,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/g3sx30_dry_run_preflight_manifest_schema.yaml"
TABLE_PATH = ROOT / "data/input/g3sx30_dry_run_preflight_manifest.csv"
SOURCE_DECISIONS_PATH = ROOT / "data/input/g3sx30_dry_run_preflight_decisions.csv"

REVIEWED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_g3sx30_dry_run_preflight_manifest_schema_records_header_only_scaffold() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "g3sx30_dry_run_preflight_manifest_schema"
    assert schema["pipeline_gate"] == "g3sx30_dry_run_preflight_manifest"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"
    assert schema["scaffold_scope"]["source_layer"] == ("g3sx30_dry_run_preflight_decision")
    assert schema["scaffold_scope"]["source_table"] == (
        "data/input/g3sx30_dry_run_preflight_decisions.csv"
    )
    assert schema["scaffold_scope"]["source_row_index"] == 1
    assert (
        schema["scaffold_scope"]["scaffold_status"]
        == "header_only_no_committed_g3sx30_dry_run_preflight_manifest_entry"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_source_dry_run_preflight_decision"]
        == "approve_dry_run_preflight_for_planning"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_source_dry_run_preflight_status_after_decision"]
        == "dry_run_preflight_planning_approved_runtime_blocked"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_source_allowed_next_action_after_decision"]
        == "prepare_later_dry_run_preflight_manifest_pr"
    )
    assert schema["scaffold_scope"]["current_g3sx30_source_max_live_batch_size_after_decision"] == 0
    assert (
        schema["scaffold_scope"]["current_g3sx30_source_ready_for_preflight_after_decision"]
        == "false"
    )
    assert schema["scaffold_scope"]["current_g3sx30_reviewed_sequence_length"] == 492
    assert schema["scaffold_scope"]["current_g3sx30_reviewed_sequence_sha256"] == (
        REVIEWED_SEQUENCE_SHA256
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_manifest_entry_status"]
        == "no_committed_manifest_entry_yet"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_runtime_status_after_manifest_scaffold"]
        == "still_not_ready_for_preflight"
    )


def test_g3sx30_dry_run_preflight_manifest_required_columns_match_helper() -> None:
    schema = load_schema()

    assert schema["required_columns"] == REQUIRED_COLUMNS
    assert list(G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA) == REQUIRED_COLUMNS


def test_g3sx30_dry_run_preflight_manifest_table_is_header_only() -> None:
    table = pl.read_csv(TABLE_PATH)

    assert table.columns == REQUIRED_COLUMNS
    assert table.height == 0
    validate_g3sx30_dry_run_preflight_manifest_schema(table)
    validate_g3sx30_dry_run_preflight_manifest_rows(table)


def test_g3sx30_dry_run_preflight_manifest_source_decision_row_is_approved() -> None:
    source_table = pl.read_csv(SOURCE_DECISIONS_PATH)
    source_row = source_table.row(0, named=True)

    assert source_row["target_accession"] == "G3SX30"
    assert source_row["dry_run_preflight_decision"] == ("approve_dry_run_preflight_for_planning")
    assert source_row["dry_run_preflight_status_after_decision"] == (
        "dry_run_preflight_planning_approved_runtime_blocked"
    )
    assert source_row["allowed_next_action_after_decision"] == (
        "prepare_later_dry_run_preflight_manifest_pr"
    )
    assert source_row["max_live_batch_size_after_decision"] == 0
    assert str(source_row["ready_for_preflight_after_decision"]).lower() == "false"
    assert source_row["reviewed_sequence_length"] == 492
    assert source_row["reviewed_sequence_sha256"] == REVIEWED_SEQUENCE_SHA256


def synthetic_manifest_row() -> dict[str, object]:
    return {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2_elephant",
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "source_dry_run_preflight_decision_table": (
            "data/input/g3sx30_dry_run_preflight_decisions.csv"
        ),
        "source_dry_run_preflight_decision_row_index": 1,
        "target_accession": "G3SX30",
        "target_accession_db": "UniProtKB TrEMBL",
        "target_species": "Loxodonta africana",
        "target_taxid": 9785,
        "gene_symbol": "MDM2",
        "source_dry_run_preflight_decision": "approve_dry_run_preflight_for_planning",
        "source_dry_run_preflight_status_after_decision": (
            "dry_run_preflight_planning_approved_runtime_blocked"
        ),
        "source_allowed_next_action_after_decision": (
            "prepare_later_dry_run_preflight_manifest_pr"
        ),
        "source_max_live_batch_size_after_decision": 0,
        "source_ready_for_preflight_after_decision": "false",
        "reviewed_sequence_sha256": REVIEWED_SEQUENCE_SHA256,
        "reviewed_sequence_length": 492,
        "manifest_entry_status": "manifest_scaffold_ready_runtime_blocked",
        "dry_run_only": True,
        "max_live_batch_size": 0,
        "ready_for_preflight_after_manifest": "false",
        "sequence_fetch_allowed": False,
        "biohub_call_allowed": False,
        "esmc_call_allowed": False,
        "embedding_generation_allowed": False,
        "curated_embedding_preflight_allowed": False,
        "curated_embedding_single_allowed": False,
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "technical_checkpoint",
        "review_note": "Synthetic fixture only; not a committed manifest entry.",
        "reviewer_id": "synthetic_fixture_reviewer",
        "review_date": "not_applicable_fixture",
        "forbidden_actions": FORBIDDEN_ACTIONS,
    }


def test_g3sx30_dry_run_preflight_manifest_validator_accepts_synthetic_row() -> None:
    table = pl.DataFrame(
        [synthetic_manifest_row()],
        schema=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA,
    )

    validate_g3sx30_dry_run_preflight_manifest_rows(table)


def test_g3sx30_dry_run_preflight_manifest_validator_blocks_unapproved_source() -> None:
    row = synthetic_manifest_row()
    row["source_dry_run_preflight_decision"] = "keep_blocked"
    table = pl.DataFrame([row], schema=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)

    with pytest.raises(ValueError, match="Invalid source_dry_run_preflight_decision"):
        validate_g3sx30_dry_run_preflight_manifest_rows(table)


def test_g3sx30_dry_run_preflight_manifest_validator_blocks_non_dry_run_only() -> None:
    row = synthetic_manifest_row()
    row["dry_run_only"] = False
    table = pl.DataFrame([row], schema=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)

    with pytest.raises(ValueError, match="dry_run_only=true"):
        validate_g3sx30_dry_run_preflight_manifest_rows(table)


def test_g3sx30_dry_run_preflight_manifest_validator_blocks_live_batch_size() -> None:
    row = synthetic_manifest_row()
    row["max_live_batch_size"] = 1
    table = pl.DataFrame([row], schema=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)

    with pytest.raises(ValueError, match="max_live_batch_size=0"):
        validate_g3sx30_dry_run_preflight_manifest_rows(table)


def test_g3sx30_dry_run_preflight_manifest_validator_blocks_runtime_permissions() -> None:
    row = synthetic_manifest_row()
    row["embedding_generation_allowed"] = True
    table = pl.DataFrame([row], schema=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)

    with pytest.raises(ValueError, match="must not allow embedding_generation_allowed"):
        validate_g3sx30_dry_run_preflight_manifest_rows(table)


def test_empty_g3sx30_dry_run_preflight_manifest_table_matches_schema() -> None:
    table = empty_g3sx30_dry_run_preflight_manifest_table()

    assert table.columns == REQUIRED_COLUMNS
    assert table.schema == G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA
    assert table.height == 0


def test_g3sx30_dry_run_preflight_manifest_schema_never_authorizes_runtime() -> None:
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

    defaults = schema["required_manifest_defaults"]
    assert defaults["dry_run_only"] is True
    assert defaults["max_live_batch_size"] == 0
    assert defaults["ready_for_preflight_after_manifest"] == "false"
    assert defaults["sequence_fetch_allowed"] is False
    assert defaults["biohub_call_allowed"] is False
    assert defaults["esmc_call_allowed"] is False
    assert defaults["embedding_generation_allowed"] is False
    assert defaults["curated_embedding_preflight_allowed"] is False
    assert defaults["curated_embedding_single_allowed"] is False
    assert defaults["gate8_eligible"] is False
    assert defaults["gate9_eligible"] is False
    assert defaults["boltz_ready"] is False
    assert defaults["af3_ready"] is False
    assert defaults["chai_ready"] is False
    assert defaults["biological_claim_allowed"] is False
