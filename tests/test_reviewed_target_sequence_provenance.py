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
POLICY_TABLE_PATH = ROOT / "data/input/ortholog_evidence_gate45_policy_updates.csv"
TARGET_SEQUENCE_DECISIONS_PATH = ROOT / "data/input/target_sequence_review_decisions.csv"

OFFICIAL_SOURCE_REFERENCE = "https://rest.uniprot.org/uniprotkb/G3SX30.fasta"
METADATA_SOURCE_REFERENCE = "https://rest.uniprot.org/uniprotkb/search?query=accession:G3SX30&fields=accession,id,reviewed,protein_name,gene_names,organism_name,organism_id,length,protein_existence&format=tsv"
REVIEWED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_table() -> pl.DataFrame:
    return pl.read_csv(TABLE_PATH)


def deferred_row() -> dict[str, object]:
    return load_table().row(0, named=True)


def reviewed_row() -> dict[str, object]:
    return load_table().row(1, named=True)


def test_reviewed_target_sequence_provenance_schema_records_reviewed_g3sx30_row_status() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "reviewed_target_sequence_provenance_schema"
    assert schema["pipeline_gate"] == "reviewed_target_sequence_provenance"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "technical_checkpoint"
    assert (
        schema["scaffold_scope"]["scaffold_status"]
        == "one_g3sx30_deferred_row_plus_one_reviewed_official_uniprot_row"
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_worklist_status"]
        == "planning_policy_updated_runtime_blocked"
    )
    assert schema["scaffold_scope"]["current_g3sx30_allowed_next_action"] == "keep_blocked"
    assert (
        schema["scaffold_scope"]["current_g3sx30_sequence_review_status"]
        == "reviewed_sequence_provenance"
    )
    assert schema["scaffold_scope"]["current_g3sx30_sequence_length_status"] == "matches"
    assert schema["scaffold_scope"]["current_g3sx30_provenance_review_status"] == "reviewed"
    assert (
        schema["scaffold_scope"]["current_g3sx30_allowed_sequence_next_action"]
        == "consider_later_dry_run_preflight_decision_pr"
    )
    assert schema["scaffold_scope"]["current_g3sx30_official_source_reference"] == (
        OFFICIAL_SOURCE_REFERENCE
    )
    assert schema["scaffold_scope"]["current_g3sx30_metadata_source_reference"] == (
        METADATA_SOURCE_REFERENCE
    )
    assert schema["scaffold_scope"]["current_g3sx30_reviewed_sequence_length"] == 492
    assert schema["scaffold_scope"]["current_g3sx30_reviewed_sequence_sha256"] == (
        REVIEWED_SEQUENCE_SHA256
    )
    assert (
        schema["scaffold_scope"]["current_g3sx30_runtime_status_after_review"]
        == "still_not_ready_for_preflight"
    )


def test_reviewed_target_sequence_provenance_schema_required_columns_match_helper() -> None:
    schema = load_schema()

    assert schema["required_columns"] == REQUIRED_COLUMNS
    assert list(REVIEWED_TARGET_SEQUENCE_PROVENANCE_SCHEMA) == REQUIRED_COLUMNS


def test_reviewed_target_sequence_provenance_table_has_deferred_and_reviewed_g3sx30_rows() -> None:
    table = load_table()

    assert table.columns == REQUIRED_COLUMNS
    assert table.height == 2
    validate_reviewed_target_sequence_provenance_schema(table)
    validate_reviewed_target_sequence_provenance_rows(table)


def test_g3sx30_deferred_sequence_row_is_preserved() -> None:
    row = deferred_row()

    assert row["target_accession"] == "G3SX30"
    assert row["sequence_source_type"] == "deferred_pending_review"
    assert row["sequence_source_reference"] == "not_applicable_deferred_pending_review"
    assert row["reviewed_sequence_sha256"] == "not_applicable_not_fetched"
    assert row["reviewed_sequence_length"] == 0
    assert row["sequence_length_status"] == "not_fetched"
    assert row["sequence_review_status"] == "deferred_pending_review"
    assert row["provenance_review_status"] == "deferred"
    assert row["allowed_next_action_after_sequence_review"] == "defer_pending_sequence_review"
    assert row["claim_status"] == "repair_worklist"


def test_g3sx30_reviewed_sequence_row_records_official_uniprot_source_review() -> None:
    row = reviewed_row()

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["lane_name"] == "tp53_mdm2_elephant"
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["source_policy_table"] == "data/input/ortholog_evidence_gate45_policy_updates.csv"
    assert row["source_policy_row_index"] == 1
    assert row["target_accession"] == "G3SX30"
    assert row["target_accession_db"] == "UniProtKB TrEMBL"
    assert row["target_species"] == "Loxodonta africana"
    assert row["target_taxid"] == 9785
    assert row["gene_symbol"] == "MDM2"
    assert row["sequence_source_type"] == "reviewed_external_database_record"
    assert row["sequence_source_reference"] == OFFICIAL_SOURCE_REFERENCE
    assert row["reviewed_sequence_sha256"] == REVIEWED_SEQUENCE_SHA256
    assert row["reviewed_sequence_length"] == 492
    assert row["sequence_length_status"] == "matches"
    assert row["sequence_review_status"] == "reviewed_sequence_provenance"
    assert row["provenance_review_status"] == "reviewed"
    assert row["allowed_next_action_after_sequence_review"] == (
        "consider_later_dry_run_preflight_decision_pr"
    )
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "technical_checkpoint"


def test_g3sx30_reviewed_sequence_row_records_identity_review_details_without_raw_sequence() -> (
    None
):
    row = reviewed_row()
    note = str(row["review_note"])

    for required in [
        "Official UniProt REST review PASS",
        "G3SX30_LOXAF",
        "E3 ubiquitin-protein ligase Mdm2",
        "Loxodonta africana",
        "taxid 9785",
        "gene MDM2",
        "protein existence inferred from homology",
        METADATA_SOURCE_REFERENCE,
        "raw FASTA sequence artifact is not committed",
    ]:
        assert required in note

    assert row["sequence_source_reference"] == OFFICIAL_SOURCE_REFERENCE
    assert "MEEPQ" not in note


def test_g3sx30_reviewed_sequence_row_matches_gate45_policy_source() -> None:
    row = reviewed_row()
    policy_table = pl.read_csv(POLICY_TABLE_PATH)
    source_row = policy_table.row(row["source_policy_row_index"] - 1, named=True)

    assert row["source_policy_table"] == "data/input/ortholog_evidence_gate45_policy_updates.csv"
    assert source_row["candidate_set"] == row["candidate_set"]
    assert source_row["lane_name"] == row["lane_name"]
    assert source_row["candidate_id"] == row["candidate_id"]
    assert source_row["reviewed_target_uniprot"] == row["target_accession"]
    assert source_row["reviewed_source_database"] == row["target_accession_db"]
    assert source_row["reviewed_taxid"] == row["target_taxid"]
    assert source_row["reviewed_sequence_length"] == row["reviewed_sequence_length"] == 492
    assert source_row["downstream_block_status_after_policy"] == (
        "gate45_policy_updated_still_runtime_blocked"
    )


def test_g3sx30_reviewed_sequence_row_has_matching_target_sequence_decision_rows() -> None:
    decision_table = pl.read_csv(TARGET_SEQUENCE_DECISIONS_PATH)

    assert decision_table.height == 2

    deferred = decision_table.row(0, named=True)
    assert deferred["target_accession"] == "G3SX30"
    assert deferred["source_sequence_provenance_row_index"] == 1
    assert deferred["sequence_review_decision"] == "defer_pending_sequence_review"
    assert deferred["sequence_length_status_after_decision"] == "not_fetched"
    assert deferred["provenance_review_status_after_decision"] == "deferred"
    assert deferred["decision_status"] == "deferred_pending_review"
    assert deferred["downstream_block_status_after_decision"] == (
        "sequence_review_deferred_still_blocked"
    )
    assert deferred["allowed_next_action_after_decision"] == "defer_pending_sequence_review"

    approval = decision_table.row(1, named=True)
    assert approval["target_accession"] == "G3SX30"
    assert approval["source_sequence_provenance_row_index"] == 2
    assert approval["sequence_review_decision"] == (
        "approve_reviewed_sequence_provenance_for_planning"
    )
    assert approval["sequence_length_status_after_decision"] == "matches"
    assert approval["provenance_review_status_after_decision"] == "reviewed"
    assert approval["reviewed_sequence_sha256"] == REVIEWED_SEQUENCE_SHA256
    assert approval["reviewed_sequence_length"] == 492
    assert approval["decision_status"] == "reviewed_for_planning_still_preflight_blocked"
    assert approval["downstream_block_status_after_decision"] == (
        "sequence_reviewed_still_preflight_decision_blocked"
    )
    assert approval["allowed_next_action_after_decision"] == (
        "consider_later_dry_run_preflight_decision_pr"
    )
    assert approval["claim_status"] == "technical_checkpoint"

    forbidden_actions = approval["forbidden_actions"]
    for required in [
        "source provenance row mutation",
        "ready_for_preflight",
        "Biohub call",
        "ESMC call",
        "embedding generation",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "biological claim",
    ]:
        assert required in forbidden_actions


def test_g3sx30_deferred_sequence_row_does_not_record_reviewed_sequence() -> None:
    row = deferred_row()

    assert row["sequence_length_status"] != "matches"
    assert row["sequence_review_status"] != "reviewed_sequence_provenance"
    assert row["provenance_review_status"] != "reviewed"
    assert row["allowed_next_action_after_sequence_review"] != (
        "consider_later_dry_run_preflight_decision_pr"
    )
    assert row["reviewed_sequence_length"] == 0
    assert row["reviewed_sequence_sha256"] == "not_applicable_not_fetched"
    assert row["claim_status"] == "repair_worklist"


def test_g3sx30_reviewed_sequence_row_forbids_runtime_side_effects() -> None:
    row = reviewed_row()
    forbidden_actions = row["forbidden_actions"]

    for required in [
        "sequence fetch",
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
