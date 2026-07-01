from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTROL_SCHEMA_PATH = ROOT / "data/config/generic_control_readiness_schema.yaml"
CLAIM_POLICY_PATH = ROOT / "data/config/claim_policy_schema.yaml"
LANE_REGISTRY_PATH = ROOT / "data/config/candidate_lanes.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_control_readiness_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)

    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "generic_control_readiness_schema"
    assert schema["pipeline_gate"] == "control_readiness"


def test_control_readiness_schema_matches_lane_gate_sequence() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert schema["pipeline_gate"] in lane_registry["required_gate_sequence"]


def test_control_readiness_schema_uses_claim_policy_schema() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)
    claim_policy = load_yaml(CLAIM_POLICY_PATH)

    assert schema["claim_policy"] in claim_policy["allowed_claim_policies"]
    assert schema["maximum_claim_status"] in claim_policy["allowed_claim_statuses"]
    assert schema["maximum_claim_status"] == "control_readiness"


def test_control_readiness_schema_lists_required_control_types() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)

    for control_type in [
        "shuffled_mask",
        "negatome",
        "curated_negative_partner",
    ]:
        assert control_type in schema["control_types"]
        assert "purpose" in schema["control_types"][control_type]
        assert "required_for" in schema["control_types"][control_type]


def test_control_readiness_schema_lists_status_groups() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)

    for status in [
        "controls_ready",
        "controls_accepted_for_limited_dry_run",
        "missing_controls",
        "blocked_missing_negatome",
        "blocked_missing_curated_negative_partner",
        "needs_manual_review",
    ]:
        assert status in schema["allowed_control_readiness_statuses"]

    for status in schema["status_groups"]["dry_run_ready"]:
        assert status in schema["allowed_control_readiness_statuses"]

    for status in schema["status_groups"]["blocked"]:
        assert status in schema["allowed_control_readiness_statuses"]


def test_control_readiness_schema_blocks_controlled_claims() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)

    for rule in schema["decision_rules"].values():
        assert rule["controlled_claim_allowed"] is False
        assert "recommended_next_action" in rule


def test_control_readiness_schema_records_required_output_fields() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)

    for field in [
        "candidate_set",
        "candidate_id",
        "source_uniprot",
        "shuffled_control_status",
        "negatome_control_status",
        "curated_negative_partner_status",
        "control_repair_status",
        "control_readiness_status",
        "recommended_next_action",
        "contrast_dry_run_allowed",
        "controlled_claim_allowed",
        "claim_policy",
        "claim_status",
        "notes",
    ]:
        assert field in schema["required_output_fields"]


def test_control_readiness_schema_blocks_overclaiming() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)

    for phrase in [
        "controls prove the biological signal",
        "NEGATOME validates the candidate",
        "validated longevity signal",
        "confirmed binding change",
        "confirmed functional effect",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert phrase in schema["disallowed_language"]


def test_control_readiness_schema_records_no_live_action_guardrails() -> None:
    schema = load_yaml(CONTROL_SCHEMA_PATH)

    guardrails = schema["required_guardrails"]
    assert "no Biohub calls from control-readiness schema checks" in guardrails
    assert "no Boltz calls from control-readiness schema checks" in guardrails
    assert "no live structural calls from control-readiness schema checks" in guardrails
    assert "no biological claims from control readiness alone" in guardrails
