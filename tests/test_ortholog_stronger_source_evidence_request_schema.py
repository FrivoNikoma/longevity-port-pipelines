from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_evidence_request_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_stronger_source_request_schema_exists_and_is_blocker_first() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "generic_ortholog_stronger_source_evidence_request_schema"
    assert schema["pipeline_gate"] == "ortholog_stronger_source_evidence_request"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_stronger_source_request_schema_starts_from_completed_still_blocked_review() -> None:
    schema = load_schema()

    assert schema["request_scope"]["from_second_review_status"] == [
        "second_review_complete_still_blocked"
    ]
    assert schema["request_scope"]["from_second_review_decision"] == [
        "needs_additional_source_evidence"
    ]
    assert schema["request_scope"]["to_status"] == "stronger_source_evidence_request"


def test_stronger_source_request_schema_does_not_authorize_downstream_work() -> None:
    schema = load_schema()
    blocked = set(schema["request_scope"]["does_not_authorize"])

    assert "Gate 4 / Gate 5 policy update" in blocked
    assert "Gate 8 eligibility" in blocked
    assert "Gate 9 eligibility" in blocked
    assert "sequence fetch" in blocked
    assert "external database query" in blocked
    assert "Biohub calls" in blocked
    assert "embedding generation" in blocked
    assert "accepted ortholog claims" in blocked
    assert "validated ortholog claims" in blocked
    assert "reviewed decision creation" in blocked
    assert "biological claims" in blocked


def test_stronger_source_request_schema_required_fields_are_distinct() -> None:
    schema = load_schema()

    identity_fields = set(schema["required_row_identity_fields"])
    request_fields = set(schema["required_request_fields"])

    assert "evidence_source_accession" in identity_fields
    assert "second_review_decision_before_request" in request_fields
    assert "requested_source_types" in request_fields
    assert "forbidden_actions_after_request" in request_fields
    assert not (identity_fields & request_fields)


def test_stronger_source_request_schema_allowed_values_are_conservative() -> None:
    schema = load_schema()

    assert schema["allowed_second_review_statuses_before_request"] == [
        "second_review_complete_still_blocked"
    ]
    assert schema["allowed_second_review_decisions_before_request"] == [
        "needs_additional_source_evidence"
    ]
    assert set(schema["allowed_request_statuses"]) == {
        "pending_source_collection",
        "source_collection_in_progress",
        "source_collection_complete_still_blocked",
    }
    assert set(schema["allowed_request_decisions"]) == {
        "pending",
        "needs_manual_source_collection",
        "ready_for_later_evidence_intake_pr",
        "conflict_or_exclude",
        "keep_blocked_until_manual_review",
    }
    assert schema["allowed_downstream_block_statuses_after_request"] == ["blocked_gate4_gate5"]
    assert schema["allowed_claim_statuses_after_request"] == ["repair_worklist"]


def test_stronger_source_request_schema_guardrails_block_runtime_side_effects() -> None:
    schema = load_schema()
    guardrails = set(schema["required_guardrails"])

    assert "stronger-source request rows do not accept orthologs automatically" in guardrails
    assert (
        "stronger-source request rows do not create reviewed decisions automatically" in guardrails
    )
    assert "stronger-source request rows do not fetch sequences" in guardrails
    assert "stronger-source request rows do not query external databases" in guardrails
    assert "stronger-source request rows do not call Biohub" in guardrails
    assert "stronger-source request rows do not generate embeddings" in guardrails
    assert "stronger-source request rows do not call Boltz" in guardrails
    assert "stronger-source request rows do not promote Gate 8" in guardrails
    assert "stronger-source request rows do not promote Gate 9" in guardrails
    assert "stronger-source request rows do not make biological claims" in guardrails
