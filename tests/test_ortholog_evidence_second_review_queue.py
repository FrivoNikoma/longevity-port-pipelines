from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/input/ortholog_evidence_second_review_queue.csv"
SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_second_review_schema.yaml"
INTAKE_TABLE_PATH = ROOT / "data/input/ortholog_evidence_intake.csv"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def second_review_rows() -> list[dict[str, str]]:
    rows = read_csv_rows(QUEUE_PATH)
    assert len(rows) == 1
    return rows


def test_second_review_queue_has_pending_g3sx30_mdm2_row() -> None:
    row = second_review_rows()[0]

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["gene_symbol"] == "MDM2"
    assert row["evidence_source_database"] == "UniProtKB TrEMBL"
    assert row["evidence_source_accession"] == "G3SX30"
    assert row["target_species_name"] == "Loxodonta africana"
    assert row["target_protein_accession"] == "G3SX30"
    assert row["target_sequence_length"] == "492"
    assert row["second_review_status"] == "pending_second_review"
    assert row["second_review_decision"] == "pending"


def test_second_review_queue_uses_schema_required_fields() -> None:
    schema = load_schema()
    required_fields = set(schema["required_row_identity_fields"]) | set(
        schema["required_second_review_fields"]
    )

    for row in second_review_rows():
        assert required_fields <= set(row)
        assert all(row[field] for field in required_fields)


def test_second_review_queue_uses_allowed_values() -> None:
    schema = load_schema()
    row = second_review_rows()[0]

    assert row["intake_outcome_before_second_review"] in set(
        schema["allowed_intake_outcomes_before_second_review"]
    )
    assert row["second_review_status"] in set(schema["allowed_second_review_statuses"])
    assert row["second_review_decision"] in set(schema["allowed_second_review_decisions"])
    assert row["downstream_block_status_after_second_review"] in set(
        schema["allowed_downstream_block_statuses_after_second_review"]
    )
    assert row["claim_policy_after_second_review"] in set(
        schema["allowed_claim_policies_after_second_review"]
    )
    assert row["claim_status_after_second_review"] in set(
        schema["allowed_claim_statuses_after_second_review"]
    )


def test_second_review_queue_traces_ambiguous_intake_row() -> None:
    row = second_review_rows()[0]
    intake_rows = read_csv_rows(INTAKE_TABLE_PATH)
    matching = [
        intake_row
        for intake_row in intake_rows
        if intake_row["candidate_id"] == row["candidate_id"]
        and intake_row["source_table"] == row["intake_source_table"]
        and intake_row["source_row_index"] == row["intake_source_row_index"]
        and intake_row["evidence_source_accession"] == row["evidence_source_accession"]
    ]

    assert len(matching) == 1
    intake_row = matching[0]

    assert intake_row["intake_outcome"] == "evidence_ambiguous_needs_second_reviewer"
    assert row["intake_outcome_before_second_review"] == intake_row["intake_outcome"]
    assert row["target_protein_accession"] == intake_row["target_protein_accession"]
    assert row["target_sequence_length"] == intake_row["target_sequence_length"]
    assert row["target_taxid"] == intake_row["target_taxid"]


def test_second_review_queue_keeps_row_blocked_by_schema_rule() -> None:
    schema = load_schema()
    row = second_review_rows()[0]
    rule = schema["second_review_decision_rules"][row["second_review_decision"]]

    assert rule["gate4_gate5_policy_update_allowed"] is False
    assert rule["gate8_eligible"] is False
    assert rule["gate9_eligible"] is False
    assert rule["embedding_ready"] is False
    assert rule["biohub_ready"] is False
    assert rule["boltz_ready"] is False
    assert rule["af3_ready"] is False
    assert rule["chai_ready"] is False
    assert rule["accepted_ortholog_claim_allowed"] is False
    assert rule["validated_ortholog_claim_allowed"] is False
    assert rule["biological_claim_allowed"] is False
    assert (
        row["downstream_block_status_after_second_review"]
        == (rule["downstream_block_status_after_second_review"])
    )
    assert (
        row["allowed_next_action_after_second_review"]
        == (rule["allowed_next_action_after_second_review"])
    )
    assert row["claim_status_after_second_review"] == rule["claim_status_after_second_review"]


def test_second_review_queue_records_guardrails_and_no_claims() -> None:
    row = second_review_rows()[0]
    forbidden_actions = row["forbidden_actions_after_second_review"]

    assert row["claim_policy_after_second_review"] == "no_biological_claims_until_validation"
    assert row["claim_status_after_second_review"] == "repair_worklist"
    assert row["reviewed_target_uniprot_after_second_review"] == "unresolved"
    assert "ortholog acceptance" in forbidden_actions
    assert "reviewed decision creation" in forbidden_actions
    assert "Gate 4 or Gate 5 policy update" in forbidden_actions
    assert "sequence fetch" in forbidden_actions
    assert "Biohub call" in forbidden_actions
    assert "embedding generation" in forbidden_actions
    assert "Boltz call" in forbidden_actions
    assert "Gate 8 promotion" in forbidden_actions
    assert "Gate 9 promotion" in forbidden_actions
    assert "biological claim" in forbidden_actions


def test_second_review_queue_does_not_accept_or_validate_orthologs() -> None:
    forbidden_values = {
        "accepted_for_planning_after_review",
        "accepted_ortholog",
        "validated_ortholog",
        "validated_biological_signal",
        "validated_longevity_signal",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "embedding ready",
        "Biohub ready",
        "Boltz ready",
        "safe_to_port",
    }

    observed_values: set[str] = set()
    for row in second_review_rows():
        observed_values.update(row.values())

    assert observed_values.isdisjoint(forbidden_values)
