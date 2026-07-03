from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_second_review_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_second_review_schema_exists_and_is_blocker_first() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "generic_ortholog_evidence_second_review_schema"
    assert schema["pipeline_gate"] == "ortholog_evidence_second_review"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_second_review_schema_only_starts_from_ambiguous_intake_rows() -> None:
    schema = load_schema()

    assert schema["second_review_scope"]["from_intake_outcome"] == [
        "evidence_ambiguous_needs_second_reviewer"
    ]
    assert schema["second_review_scope"]["to_status"] == "second_review_worklist_item"
    assert "accepted ortholog claims" in schema["second_review_scope"]["does_not_authorize"]
    assert "Gate 8 eligibility" in schema["second_review_scope"]["does_not_authorize"]
    assert "Gate 9 eligibility" in schema["second_review_scope"]["does_not_authorize"]


def test_second_review_schema_required_fields_are_distinct_and_present() -> None:
    schema = load_schema()

    identity_fields = schema["required_row_identity_fields"]
    review_fields = schema["required_second_review_fields"]

    assert "evidence_source_accession" in identity_fields
    assert "intake_outcome_before_second_review" in review_fields
    assert "second_review_decision" in review_fields
    assert "forbidden_actions_after_second_review" in review_fields
    assert not (set(identity_fields) & set(review_fields))


def test_second_review_schema_allowed_statuses_and_decisions_are_conservative() -> None:
    schema = load_schema()

    assert set(schema["allowed_second_review_statuses"]) == {
        "pending_second_review",
        "second_review_in_progress",
        "second_review_complete_still_blocked",
    }
    assert set(schema["allowed_second_review_decisions"]) == {
        "pending",
        "ready_for_later_reviewed_decision_pr",
        "needs_additional_source_evidence",
        "conflict_or_exclude",
        "keep_blocked_until_manual_review",
    }


def test_second_review_decision_rules_do_not_authorize_downstream_work() -> None:
    schema = load_schema()

    for rule in schema["second_review_decision_rules"].values():
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
        assert rule["downstream_block_status_after_second_review"] == "blocked_gate4_gate5"
        assert rule["claim_status_after_second_review"] == "repair_worklist"


def test_second_review_schema_required_guardrails_block_runtime_side_effects() -> None:
    schema = load_schema()
    guardrails = set(schema["required_guardrails"])

    assert "second-review rows do not accept orthologs automatically" in guardrails
    assert "second-review rows do not create reviewed decisions automatically" in guardrails
    assert "second-review rows do not update Gate 4 / Gate 5 policy automatically" in guardrails
    assert "second-review rows do not fetch sequences" in guardrails
    assert "second-review rows do not call Biohub" in guardrails
    assert "second-review rows do not generate embeddings" in guardrails
    assert "second-review rows do not call Boltz" in guardrails
    assert "second-review rows do not promote Gate 8" in guardrails
    assert "second-review rows do not promote Gate 9" in guardrails
    assert "second-review rows do not make biological claims" in guardrails
