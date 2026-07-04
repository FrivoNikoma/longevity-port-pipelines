from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_gate45_policy_update_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_gate45_policy_update_schema_is_scaffold_only() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "ortholog_evidence_gate45_policy_update_schema"
    assert schema["pipeline_gate"] == "ortholog_evidence_gate45_policy_update"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"
    assert schema["policy_update_scope"]["scaffold_status"] == "header_only_no_rows"


def test_gate45_policy_update_schema_sources_review_decisions() -> None:
    scope = load_schema()["policy_update_scope"]

    assert scope["allowed_policy_sources"] == ["ortholog_evidence_review_decisions"]
    assert scope["from_review_decision"] == ["accepted_for_planning_after_review"]
    assert scope["from_downstream_block_status"] == ["reviewed_for_planning_still_policy_blocked"]
    assert scope["from_allowed_next_action"] == [
        "consider_later_explicit_gate4_gate5_policy_update"
    ]


def test_gate45_policy_update_schema_never_authorizes_downstream_runtime() -> None:
    schema = load_schema()
    rules = schema["policy_update_decision_rules"]
    forbidden = set(schema["policy_update_scope"]["does_not_authorize"])

    for rule in rules.values():
        assert rule["gate8_eligible"] is False
        assert rule["gate9_eligible"] is False
        assert rule["embedding_ready"] is False
        assert rule["biohub_ready"] is False
        assert rule["boltz_ready"] is False
        assert rule["af3_ready"] is False
        assert rule["chai_ready"] is False
        assert rule["biological_claim_allowed"] is False

    assert "Gate 8 eligibility" in forbidden
    assert "Gate 9 eligibility" in forbidden
    assert "embedding generation" in forbidden
    assert "Boltz calls" in forbidden
    assert "biological claims" in forbidden
