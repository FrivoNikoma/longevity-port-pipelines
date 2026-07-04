from __future__ import annotations

from pathlib import Path

import yaml

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_raw_metadata_review as review,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_raw_metadata_review_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_raw_metadata_review_schema_exists_and_identifies_scope() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "ortholog_stronger_source_raw_metadata_review_schema"
    assert schema["pipeline_gate"] == "raw_metadata_response_human_review"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_raw_metadata_review_schema_columns_match_validator_contract() -> None:
    schema = load_schema()

    expected_columns = (
        schema["required_raw_metadata_response_trace_fields"] + schema["required_review_fields"]
    )

    assert expected_columns == list(review.REQUIRED_COLUMNS)


def test_raw_metadata_review_schema_allowed_decisions_are_blocker_first() -> None:
    schema = load_schema()

    assert set(schema["allowed_human_review_decisions"]) == {
        "pending",
        "metadata_consistent_prepare_source_evidence_intake_later",
        "metadata_conflict_keep_blocked",
        "metadata_insufficient_keep_blocked",
    }

    for rule in schema["review_decision_rules"].values():
        assert rule["downstream_block_status_after_review"] == "blocked_gate4_gate5"
        assert rule["claim_status_after_review"] == "repair_worklist"


def test_raw_metadata_review_schema_guardrails_forbid_downstream_side_effects() -> None:
    schema = load_schema()
    guardrails = set(schema["required_guardrails"])

    assert "raw metadata human review rows do not create source evidence" in guardrails
    assert "raw metadata human review rows do not create reviewed ortholog decisions" in guardrails
    assert "raw metadata human review rows do not update Gate 4 or Gate 5 policy" in guardrails
    assert "raw metadata human review rows do not promote Gate 8" in guardrails
    assert "raw metadata human review rows do not promote Gate 9" in guardrails
    assert "raw metadata human review rows do not fetch sequences" in guardrails
    assert "raw metadata human review rows do not make biological claims" in guardrails
