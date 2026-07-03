from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = ROOT / "data/input/ortholog_stronger_source_evidence_requests.csv"
SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_evidence_request_schema.yaml"
SECOND_REVIEW_PATH = ROOT / "data/input/ortholog_evidence_second_review_queue.csv"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def request_rows() -> list[dict[str, str]]:
    rows = read_csv_rows(REQUEST_PATH)
    assert len(rows) == 1
    return rows


def test_stronger_source_request_has_g3sx30_mdm2_row() -> None:
    row = request_rows()[0]

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["gene_symbol"] == "MDM2"
    assert row["evidence_source_database"] == "UniProtKB TrEMBL"
    assert row["evidence_source_accession"] == "G3SX30"
    assert row["target_species_name"] == "Loxodonta africana"
    assert row["target_protein_accession"] == "G3SX30"
    assert row["target_sequence_length"] == "492"
    assert row["request_status"] == "pending_source_collection"
    assert row["request_decision"] == "needs_manual_source_collection"


def test_stronger_source_request_uses_schema_required_fields() -> None:
    schema = load_schema()
    required_fields = set(schema["required_row_identity_fields"]) | set(
        schema["required_request_fields"]
    )

    for row in request_rows():
        assert required_fields <= set(row)
        assert all(row[field] for field in required_fields)


def test_stronger_source_request_uses_allowed_values() -> None:
    schema = load_schema()
    row = request_rows()[0]

    assert row["second_review_status_before_request"] in set(
        schema["allowed_second_review_statuses_before_request"]
    )
    assert row["second_review_decision_before_request"] in set(
        schema["allowed_second_review_decisions_before_request"]
    )
    assert row["request_status"] in set(schema["allowed_request_statuses"])
    assert row["request_decision"] in set(schema["allowed_request_decisions"])
    assert row["downstream_block_status_after_request"] in set(
        schema["allowed_downstream_block_statuses_after_request"]
    )
    assert row["claim_policy_after_request"] in set(schema["allowed_claim_policies_after_request"])
    assert row["claim_status_after_request"] in set(schema["allowed_claim_statuses_after_request"])


def test_stronger_source_request_traces_second_review_row() -> None:
    row = request_rows()[0]
    second_review_rows = read_csv_rows(SECOND_REVIEW_PATH)

    matching = [
        second_review_row
        for second_review_row in second_review_rows
        if second_review_row["candidate_id"] == row["candidate_id"]
        and second_review_row["evidence_source_accession"] == row["evidence_source_accession"]
    ]

    assert len(matching) == 1
    second_review_row = matching[0]

    assert second_review_row["second_review_status"] == "second_review_complete_still_blocked"
    assert second_review_row["second_review_decision"] == "needs_additional_source_evidence"
    assert row["second_review_status_before_request"] == second_review_row["second_review_status"]
    assert (
        row["second_review_decision_before_request"]
        == (second_review_row["second_review_decision"])
    )
    assert (
        row["reviewed_target_uniprot_before_request"]
        == (second_review_row["reviewed_target_uniprot_after_second_review"])
    )


def test_stronger_source_request_records_manual_source_collection_without_querying() -> None:
    row = request_rows()[0]
    requested_sources = row["requested_source_types"]
    forbidden_actions = row["forbidden_actions_after_request"]

    assert "reviewed UniProt" in requested_sources
    assert "NCBI protein or gene record" in requested_sources
    assert "Ensembl orthology" in requested_sources
    assert "OMA orthology" in requested_sources
    assert "OrthoDB orthology" in requested_sources
    assert "primary literature" in requested_sources
    assert row["allowed_next_action_after_request"] == ("collect_stronger_source_evidence_manually")
    assert "external database query" in forbidden_actions


def test_stronger_source_request_records_guardrails_and_no_claims() -> None:
    row = request_rows()[0]
    forbidden_actions = row["forbidden_actions_after_request"]

    assert row["claim_policy_after_request"] == "no_biological_claims_until_validation"
    assert row["claim_status_after_request"] == "repair_worklist"
    assert row["reviewed_target_uniprot_before_request"] == "unresolved"
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


def test_stronger_source_request_does_not_accept_or_validate_orthologs() -> None:
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
    for row in request_rows():
        observed_values.update(row.values())

    assert observed_values.isdisjoint(forbidden_values)
