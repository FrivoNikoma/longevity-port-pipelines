from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_evidence_collection_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_collection_schema_exists_and_is_blocker_first() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "generic_ortholog_stronger_source_evidence_collection_schema"
    assert schema["pipeline_gate"] == "ortholog_stronger_source_evidence_collection"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_collection_schema_starts_from_manual_source_request() -> None:
    schema = load_schema()

    assert set(schema["collection_scope"]["from_request_status"]) == {
        "pending_source_collection",
        "source_collection_in_progress",
    }
    assert schema["collection_scope"]["from_request_decision"] == ["needs_manual_source_collection"]
    assert schema["collection_scope"]["to_status"] == (
        "stronger_source_evidence_collected_still_blocked"
    )


def test_collection_schema_does_not_authorize_downstream_work() -> None:
    schema = load_schema()
    blocked = set(schema["collection_scope"]["does_not_authorize"])

    assert "Gate 4 / Gate 5 policy update" in blocked
    assert "Gate 8 eligibility" in blocked
    assert "Gate 9 eligibility" in blocked
    assert "sequence fetch" in blocked
    assert "automated external database query" in blocked
    assert "Biohub calls" in blocked
    assert "embedding generation" in blocked
    assert "accepted ortholog claims" in blocked
    assert "validated ortholog claims" in blocked
    assert "reviewed decision creation" in blocked
    assert "biological claims" in blocked


def test_collection_schema_guardrails_block_runtime_side_effects() -> None:
    schema = load_schema()
    guardrails = set(schema["required_guardrails"])

    assert "collection rows do not accept orthologs automatically" in guardrails
    assert "collection rows do not create reviewed decisions automatically" in guardrails
    assert "collection rows do not fetch sequences" in guardrails
    assert "collection rows do not run automated external database queries" in guardrails
    assert "collection rows do not call Biohub" in guardrails
    assert "collection rows do not generate embeddings" in guardrails
    assert "collection rows do not call Boltz" in guardrails
    assert "collection rows do not promote Gate 8" in guardrails
    assert "collection rows do not promote Gate 9" in guardrails
    assert "collection rows do not make biological claims" in guardrails


def test_collection_schema_required_fields_are_distinct() -> None:
    schema = load_schema()

    trace_fields = set(schema["required_request_trace_fields"])
    collection_fields = set(schema["required_collection_fields"])

    assert "candidate_id" in trace_fields
    assert "request_table" in trace_fields
    assert "requested_evidence_source_accession" in trace_fields
    assert "collected_source_type" in collection_fields
    assert "collection_decision" in collection_fields
    assert "forbidden_actions_after_collection" in collection_fields
    assert not (trace_fields & collection_fields)


def test_collection_schema_allowed_source_types_cover_requested_sources() -> None:
    schema = load_schema()

    assert set(schema["allowed_collected_source_types"]) == {
        "uniprot_unreviewed_entry_metadata",
        "reviewed_uniprot",
        "ncbi_protein_or_gene_record",
        "ensembl_orthology",
        "oma_orthology",
        "orthodb_orthology",
        "primary_literature",
        "other_manual_source",
    }


def test_collection_schema_allowed_values_are_conservative() -> None:
    schema = load_schema()

    assert set(schema["allowed_collection_statuses"]) == {
        "pending_manual_collection",
        "manual_collection_in_progress",
        "manual_collection_complete_still_blocked",
    }
    assert set(schema["allowed_collection_decisions"]) == {
        "pending",
        "evidence_recorded_for_later_intake_pr",
        "evidence_insufficient_keep_blocked",
        "evidence_conflict_or_exclude",
        "needs_additional_manual_review",
    }
    assert schema["allowed_downstream_block_statuses_after_collection"] == ["blocked_gate4_gate5"]
    assert schema["allowed_claim_statuses_after_collection"] == ["repair_worklist"]
    assert schema["allowed_claim_policies_after_collection"] == [
        "no_biological_claims_until_validation"
    ]
