from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

CLAIM_POLICY_PATH = ROOT / "data/config/claim_policy_schema.yaml"
LANE_REGISTRY_PATH = ROOT / "data/config/candidate_lanes.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_claim_policy_schema_defines_policy_used_by_lane_registry() -> None:
    schema = load_yaml(CLAIM_POLICY_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert schema["policy_id"] == "no_biological_claims_until_validation"
    assert lane_registry["claim_policy"] in schema["allowed_claim_policies"]


def test_claim_policy_schema_lists_allowed_claim_statuses() -> None:
    schema = load_yaml(CLAIM_POLICY_PATH)

    for status in [
        "planning_only",
        "technical_checkpoint",
        "coverage_readiness",
        "repair_worklist",
        "control_readiness",
        "contrast_readiness",
        "cofolding_readiness",
        "structural_compatibility_checkpoint",
        "validation_required",
    ]:
        assert status in schema["allowed_claim_statuses"]


def test_claim_policy_schema_covers_required_gate_sequence() -> None:
    schema = load_yaml(CLAIM_POLICY_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    stage_policies = schema["pipeline_stage_policies"]

    for stage in lane_registry["required_gate_sequence"]:
        assert stage in stage_policies
        assert "maximum_claim_status" in stage_policies[stage]
        assert "allowed_summary" in stage_policies[stage]
        assert "disallowed_summary" in stage_policies[stage]


def test_claim_policy_schema_blocks_prevalidation_overclaiming() -> None:
    schema = load_yaml(CLAIM_POLICY_PATH)

    for phrase in [
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert phrase in schema["disallowed_prevalidation_language"]


def test_claim_policy_schema_keeps_structural_calls_as_checkpoints() -> None:
    schema = load_yaml(CLAIM_POLICY_PATH)

    structural_policy = schema["pipeline_stage_policies"]["live_structural_compatibility"]

    assert structural_policy["maximum_claim_status"] == "structural_compatibility_checkpoint"
    assert "functional benefit" in structural_policy["disallowed_summary"]


def test_claim_policy_schema_records_no_live_call_guardrails() -> None:
    schema = load_yaml(CLAIM_POLICY_PATH)

    guardrails = schema["required_guardrails"]

    assert "no live structural calls without explicit opt-in" in guardrails
    assert "no Biohub calls from claim-policy schema checks" in guardrails
    assert "no Boltz calls from claim-policy schema checks" in guardrails
