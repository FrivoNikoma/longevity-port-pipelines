from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DECISIONS_PATH = ROOT / "data/input/generic_repair_queue_review_decisions.csv"
REVIEW_SCHEMA_PATH = ROOT / "data/config/generic_repair_queue_review_schema.yaml"
SIRT6_REPAIR_PATH = ROOT / "data/input/sirt6_candidate_coverage_repair_decisions.csv"
CHECKPOINT_DOC_PATH = ROOT / "docs/sirt6_manual_provenance_review_checkpoint.md"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def reviewed_row() -> dict[str, str]:
    rows = read_csv_rows(REVIEW_DECISIONS_PATH)
    assert len(rows) == 1
    return rows[0]


def test_review_decision_fixture_exists_and_has_one_sirt6_row() -> None:
    row = reviewed_row()
    assert row["candidate_set"] == "sirt6_dna_repair"
    assert row["lane_name"] == "SIRT6/core3"
    assert row["candidate_id"] == "4xhu__A1_P09874--4xhu__B1_Q9UNS1"
    assert row["source_table"] == "data/input/sirt6_candidate_coverage_repair_decisions.csv"
    assert row["source_row_index"] == "1"


def test_review_decision_fixture_uses_schema_required_fields() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    row = reviewed_row()
    required_fields = set(schema["required_pre_review_fields"]) | set(
        schema["required_review_fields"]
    )
    assert required_fields <= set(row)
    assert all(row[field] for field in required_fields)


def test_review_decision_fixture_traces_committed_sirt6_repair_row() -> None:
    row = reviewed_row()
    source_rows = read_csv_rows(SIRT6_REPAIR_PATH)
    source_row = source_rows[int(row["source_row_index"]) - 1]
    assert source_row["candidate_id"] == row["candidate_id"]
    assert source_row["source_uniprot"] == row["source_uniprot"]
    assert source_row["target_species"] == row["target_species"]
    assert source_row["target_species_taxid"] == row["target_species_taxid"]
    assert source_row["claim_policy"] == row["claim_policy_before_review"]
    assert source_row["repair_decision"] == "needs_external_manual_sequence_review"


def test_review_decision_defers_bowhead_taxid_mismatch() -> None:
    row = reviewed_row()
    assert row["review_decision"] == "deferred_pending_source"
    assert row["target_species"] == "bowhead_whale"
    assert row["target_species_taxid"] == "27622"
    assert row["reviewed_taxid"] == "27602"
    assert row["reviewed_target_uniprot"] == "unresolved"
    assert "NCBI Taxonomy" in row["reviewed_source_database"]
    assert "UniProt Taxonomy" in row["reviewed_source_database"]
    assert "taxid 27602" in row["review_evidence_uri_or_note"]
    assert "source repair row records 27622" in row["review_evidence_uri_or_note"]


def test_review_decision_keeps_downstream_blocked_by_schema_rule() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    row = reviewed_row()
    rule = schema["review_decision_rules"][row["review_decision"]]
    assert rule["gate8_eligible"] is False
    assert rule["gate9_eligible"] is False
    assert rule["embedding_ready"] is False
    assert rule["boltz_ready"] is False
    assert rule["validated_ortholog_claim_allowed"] is False
    assert rule["biological_claim_allowed"] is False
    assert (
        row["downstream_block_status_after_review"] == rule["downstream_block_status_after_review"]
    )
    assert row["allowed_next_action_after_review"] == rule["allowed_next_action_after_review"]
    assert row["claim_status_after_review"] == rule["claim_status_after_review"]


def test_review_decision_preserves_blocker_first_semantics() -> None:
    row = reviewed_row()
    assert row["repair_queue_status_before_review"] == "blocked_pending_manual_review"
    assert row["downstream_block_status_before_review"] == "blocked_gate4_gate5"
    assert row["downstream_block_status_after_review"] == "blocked_gate4_gate5"
    assert "valid Gate 4 / Gate 5 blocked worklist item" in row["reviewer_note"]
    assert "Gate 8 promotion" in row["forbidden_actions_after_review"]
    assert "Gate 9 promotion" in row["forbidden_actions_after_review"]
    assert "embedding generation" in row["forbidden_actions_after_review"]
    assert "Boltz call" in row["forbidden_actions_after_review"]
    assert "biological claim" in row["forbidden_actions_after_review"]


def test_review_checkpoint_doc_records_no_downstream_permission() -> None:
    text = CHECKPOINT_DOC_PATH.read_text(encoding="utf-8")
    assert "SIRT6 manual provenance review checkpoint" in text
    assert "data/input/generic_repair_queue_review_decisions.csv" in text
    assert "unreviewed Gate 4 / Gate 5 blocker" in text
    assert "reviewed-for-planning provenance evidence" in text
    assert "review_decision: deferred_pending_source" in text
    assert "downstream_block_status_after_review: blocked_gate4_gate5" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text
