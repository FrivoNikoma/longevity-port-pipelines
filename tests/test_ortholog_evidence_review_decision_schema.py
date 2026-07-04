from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_review_decision_schema.yaml"
CLAIM_POLICY_PATH = ROOT / "data/config/claim_policy_schema.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ortholog_evidence_review_decision_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(SCHEMA_PATH)
    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "ortholog_evidence_review_decision_schema"
    assert schema["pipeline_gate"] == "ortholog_evidence_review_decision"


def test_ortholog_evidence_review_decision_schema_uses_claim_policy_schema() -> None:
    schema = load_yaml(SCHEMA_PATH)
    claim_policy = load_yaml(CLAIM_POLICY_PATH)
    assert schema["claim_policy"] in claim_policy["allowed_claim_policies"]
    assert schema["maximum_claim_status"] in claim_policy["allowed_claim_statuses"]
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_ortholog_evidence_review_decision_schema_is_separate_from_repair_overlay() -> None:
    schema = load_yaml(SCHEMA_PATH)
    scope = schema["review_decision_scope"]
    assert "ortholog_evidence_intake" in scope["allowed_review_sources"]
    assert "ortholog_evidence_second_review" in scope["allowed_review_sources"]
    assert "evidence_ready_for_review_decision" in scope["from_intake_outcome"]
    assert "ready_for_later_reviewed_decision_pr" in scope["from_second_review_decision"]


def test_ortholog_evidence_review_decision_schema_lists_required_fields() -> None:
    schema = load_yaml(SCHEMA_PATH)
    identity = set(schema["required_row_identity_fields"])
    review = set(schema["required_review_fields"])

    assert {
        "candidate_set",
        "candidate_id",
        "review_source_table",
        "review_source_row_index",
        "intake_table",
        "intake_source_table",
        "intake_source_row_index",
        "evidence_source_accession",
        "target_protein_accession",
    } <= identity

    assert {
        "review_source_status_before_review",
        "review_source_decision_before_review",
        "review_decision",
        "reviewed_target_uniprot",
        "reviewed_source_database",
        "reviewed_source_accession",
        "downstream_block_status_after_review",
        "allowed_next_action_after_review",
        "claim_status_after_review",
        "forbidden_actions_after_review",
    } <= review


def test_ortholog_evidence_review_decision_schema_lists_allowed_decisions() -> None:
    schema = load_yaml(SCHEMA_PATH)
    assert set(schema["allowed_review_decisions"]) == {
        "accepted_for_planning_after_review",
        "rejected_after_review",
        "needs_additional_source_evidence",
        "conflict_or_exclude",
        "keep_blocked_until_manual_review",
    }


def test_ortholog_evidence_review_decision_schema_keeps_downstream_blocked() -> None:
    schema = load_yaml(SCHEMA_PATH)
    for decision in schema["allowed_review_decisions"]:
        rule = schema["review_decision_rules"][decision]
        assert rule["automatic_gate4_gate5_policy_update_allowed"] is False
        assert rule["gate8_eligible"] is False
        assert rule["gate9_eligible"] is False
        assert rule["embedding_ready"] is False
        assert rule["biohub_ready"] is False
        assert rule["boltz_ready"] is False
        assert rule["af3_ready"] is False
        assert rule["chai_ready"] is False
        assert rule["validated_ortholog_claim_allowed"] is False
        assert rule["biological_claim_allowed"] is False
        assert rule["claim_status_after_review"] == "repair_worklist"


def test_ortholog_evidence_review_decision_schema_accepts_planning_only() -> None:
    schema = load_yaml(SCHEMA_PATH)
    rule = schema["review_decision_rules"]["accepted_for_planning_after_review"]
    assert rule["gate4_gate5_policy_update_allowed_later_explicit_pr_only"] is True
    assert rule["automatic_gate4_gate5_policy_update_allowed"] is False
    assert (
        rule["allowed_next_action_after_review"]
        == "consider_later_explicit_gate4_gate5_policy_update"
    )
    assert (
        rule["downstream_block_status_after_review"] == "reviewed_for_planning_still_policy_blocked"
    )


def test_ortholog_evidence_review_decision_schema_blocks_overclaiming() -> None:
    schema = load_yaml(SCHEMA_PATH)
    for phrase in [
        "validated ortholog",
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "embedding ready",
        "Biohub ready",
        "Boltz ready",
        "AF3 ready",
        "Chai ready",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert phrase in schema["disallowed_language"]


def test_ortholog_evidence_review_decision_schema_records_guardrails() -> None:
    schema = load_yaml(SCHEMA_PATH)
    guardrails = set(schema["required_guardrails"])
    assert "reviewed-decision rows do not automatically update Gate 4 / Gate 5 policy" in guardrails
    assert "reviewed-decision rows do not fetch sequences" in guardrails
    assert "reviewed-decision rows do not call Biohub" in guardrails
    assert "reviewed-decision rows do not generate embeddings" in guardrails
    assert "reviewed-decision rows do not call Boltz" in guardrails
    assert "reviewed-decision rows do not promote Gate 8" in guardrails
    assert "reviewed-decision rows do not promote Gate 9" in guardrails
    assert "reviewed-decision rows do not make biological claims" in guardrails
