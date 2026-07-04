from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages.reviewed_target_sequence_provenance import (
    FORBIDDEN_ACTIONS,
    REQUIRED_COLUMNS,
    REVIEWED_TARGET_SEQUENCE_PROVENANCE_SCHEMA,
    empty_reviewed_target_sequence_provenance_table,
    validate_reviewed_target_sequence_provenance_rows,
    validate_reviewed_target_sequence_provenance_schema,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/reviewed_target_sequence_provenance_schema.yaml"
TABLE_PATH = ROOT / "data/input/reviewed_target_sequence_provenance.csv"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_reviewed_target_sequence_provenance_schema_is_scaffold_only() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "reviewed_target_sequence_provenance_schema"
    assert schema["pipeline_gate"] == "reviewed_target_sequence_provenance"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "technical_checkpoint"
    assert schema["scaffold_scope"]["scaffold_status"] == "header_only_no_rows"
    assert (
        schema["scaffold_scope"]["current_g3sx30_worklist_status"]
        == "planning_policy_updated_runtime_blocked"
    )
    assert schema["scaffold_scope"]["current_g3sx30_allowed_next_action"] == "keep_blocked"


def test_reviewed_target_sequence_provenance_schema_required_columns_match_helper() -> None:
    schema = load_schema()

    assert schema["required_columns"] == REQUIRED_COLUMNS
    assert list(REVIEWED_TARGET_SEQUENCE_PROVENANCE_SCHEMA) == REQUIRED_COLUMNS


def test_reviewed_target_sequence_provenance_header_table_has_no_rows() -> None:
    table = pl.read_csv(TABLE_PATH)

    assert table.columns == REQUIRED_COLUMNS
    assert table.height == 0
    validate_reviewed_target_sequence_provenance_schema(table)
    validate_reviewed_target_sequence_provenance_rows(table)


def test_empty_reviewed_target_sequence_provenance_table_matches_schema() -> None:
    table = empty_reviewed_target_sequence_provenance_table()

    assert table.columns == REQUIRED_COLUMNS
    assert table.schema == REVIEWED_TARGET_SEQUENCE_PROVENANCE_SCHEMA
    assert table.height == 0


def test_reviewed_target_sequence_provenance_schema_never_authorizes_runtime() -> None:
    schema = load_schema()
    forbidden = set(schema["scaffold_scope"]["does_not_authorize"])

    for required in [
        "sequence fetch",
        "Biohub calls",
        "ESMC calls",
        "embedding generation",
        "curated_embedding_preflight",
        "curated_embedding_single",
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

    for rule in schema["sequence_review_decision_rules"].values():
        assert rule["embedding_ready"] is False
        assert rule["biohub_ready"] is False
        assert rule["live_call_ready"] is False
        assert rule["gate8_eligible"] is False
        assert rule["gate9_eligible"] is False
        assert rule["boltz_ready"] is False
        assert rule["af3_ready"] is False
        assert rule["chai_ready"] is False
        assert rule["biological_claim_allowed"] is False


def test_reviewed_target_sequence_provenance_validator_accepts_synthetic_reviewed_row() -> None:
    row = {
        "candidate_set": "fixture_candidate_set",
        "lane_name": "fixture_lane",
        "candidate_id": "fixture_candidate",
        "source_policy_table": "data/input/ortholog_evidence_gate45_policy_updates.csv",
        "source_policy_row_index": 1,
        "target_accession": "FIXTURE_ACCESSION",
        "target_accession_db": "UniProtKB TrEMBL",
        "target_species": "fixture_species",
        "target_taxid": 1,
        "gene_symbol": "FIXTURE",
        "sequence_source_type": "reviewed_external_database_record",
        "sequence_source_reference": "fixture://reviewed-sequence",
        "reviewed_sequence_sha256": "0" * 64,
        "reviewed_sequence_length": 1,
        "sequence_length_status": "matches",
        "sequence_review_status": "reviewed_sequence_provenance",
        "provenance_review_status": "reviewed",
        "allowed_next_action_after_sequence_review": (
            "consider_later_dry_run_preflight_decision_pr"
        ),
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "technical_checkpoint",
        "review_note": "Synthetic fixture only; not a committed G3SX30 row.",
        "forbidden_actions": FORBIDDEN_ACTIONS,
    }
    table = pl.DataFrame([row], schema=REVIEWED_TARGET_SEQUENCE_PROVENANCE_SCHEMA)

    validate_reviewed_target_sequence_provenance_rows(table)


def test_reviewed_target_sequence_provenance_validator_blocks_reviewed_mismatch() -> None:
    row = {
        "candidate_set": "fixture_candidate_set",
        "lane_name": "fixture_lane",
        "candidate_id": "fixture_candidate",
        "source_policy_table": "data/input/ortholog_evidence_gate45_policy_updates.csv",
        "source_policy_row_index": 1,
        "target_accession": "FIXTURE_ACCESSION",
        "target_accession_db": "UniProtKB TrEMBL",
        "target_species": "fixture_species",
        "target_taxid": 1,
        "gene_symbol": "FIXTURE",
        "sequence_source_type": "reviewed_external_database_record",
        "sequence_source_reference": "fixture://reviewed-sequence",
        "reviewed_sequence_sha256": "0" * 64,
        "reviewed_sequence_length": 1,
        "sequence_length_status": "mismatch",
        "sequence_review_status": "reviewed_sequence_provenance",
        "provenance_review_status": "reviewed",
        "allowed_next_action_after_sequence_review": "keep_blocked",
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "technical_checkpoint",
        "review_note": "Synthetic fixture only; not a committed G3SX30 row.",
        "forbidden_actions": FORBIDDEN_ACTIONS,
    }
    table = pl.DataFrame([row], schema=REVIEWED_TARGET_SEQUENCE_PROVENANCE_SCHEMA)

    with pytest.raises(ValueError, match="requires sequence_length_status=matches"):
        validate_reviewed_target_sequence_provenance_rows(table)


def test_reviewed_target_sequence_provenance_validator_rejects_missing_columns() -> None:
    table = pl.DataFrame({"candidate_set": ["fixture"]})

    with pytest.raises(ValueError, match="Missing required"):
        validate_reviewed_target_sequence_provenance_schema(table)
