from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

LANE_MANIFEST_SCHEMA_PATH = ROOT / "data/config/lane_manifest_schema.yaml"
CANDIDATE_LANES_PATH = ROOT / "data/config/candidate_lanes.yaml"
CLAIM_POLICY_SCHEMA_PATH = ROOT / "data/config/claim_policy_schema.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_lane_manifest_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(LANE_MANIFEST_SCHEMA_PATH)

    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "generic_lane_manifest_schema"


def test_lane_manifest_schema_uses_registry_claim_policy() -> None:
    schema = load_yaml(LANE_MANIFEST_SCHEMA_PATH)
    candidate_lanes = load_yaml(CANDIDATE_LANES_PATH)
    claim_policy_schema = load_yaml(CLAIM_POLICY_SCHEMA_PATH)

    assert schema["claim_policy"] == candidate_lanes["claim_policy"]
    assert schema["claim_policy"] == claim_policy_schema["policy_id"]
    assert schema["claim_policy"] == "no_biological_claims_until_validation"


def test_lane_manifest_schema_uses_registry_biological_modes() -> None:
    schema = load_yaml(LANE_MANIFEST_SCHEMA_PATH)
    candidate_lanes = load_yaml(CANDIDATE_LANES_PATH)

    assert set(schema["allowed_biological_modes"]) == set(
        candidate_lanes["allowed_biological_modes"]
    )

    for lane in candidate_lanes["lanes"].values():
        assert lane["biological_mode"] in schema["allowed_biological_modes"]


def test_lane_manifest_schema_covers_lane_lifecycle_statuses() -> None:
    schema = load_yaml(LANE_MANIFEST_SCHEMA_PATH)

    allowed_statuses = set(schema["allowed_lane_lifecycle_statuses"])

    assert {
        "calibration",
        "planned",
        "legacy_alignment",
    } <= allowed_statuses

    assert "lane_lifecycle_status" in schema["required_manifest_fields"]


def test_lane_manifest_schema_lists_required_identity_fields() -> None:
    schema = load_yaml(LANE_MANIFEST_SCHEMA_PATH)

    required_fields = set(schema["required_manifest_fields"])

    assert {
        "candidate_set",
        "candidate_id",
        "lane_name",
        "lane_lifecycle_status",
        "biological_mode",
        "source_species",
        "source_species_taxid",
        "target_species",
        "target_species_taxid",
        "gene_symbol",
        "source_uniprot",
        "target_uniprot",
        "claim_policy",
        "claim_status",
        "reviewer_note",
    } <= required_fields


def test_lane_manifest_schema_covers_required_gate_sequence() -> None:
    schema = load_yaml(LANE_MANIFEST_SCHEMA_PATH)
    candidate_lanes = load_yaml(CANDIDATE_LANES_PATH)

    required_gate_sequence = candidate_lanes["required_gate_sequence"]
    required_gate_status_fields = schema["required_gate_status_fields"]

    assert set(required_gate_sequence) == set(required_gate_status_fields)

    for gate_name in required_gate_sequence:
        assert required_gate_status_fields[gate_name].endswith("_status")


def test_lane_manifest_schema_reuses_claim_policy_statuses() -> None:
    schema = load_yaml(LANE_MANIFEST_SCHEMA_PATH)
    claim_policy_schema = load_yaml(CLAIM_POLICY_SCHEMA_PATH)

    assert set(schema["allowed_claim_statuses"]) <= set(
        claim_policy_schema["allowed_claim_statuses"]
    )

    assert schema["maximum_prevalidation_claim_status"] in schema["allowed_claim_statuses"]


def test_lane_manifest_schema_blocks_live_actions_and_overclaiming() -> None:
    schema = load_yaml(LANE_MANIFEST_SCHEMA_PATH)

    guardrails = " ".join(schema["required_manifest_guardrails"]).lower()
    disallowed = set(schema["disallowed_prevalidation_language"])

    assert "no live biohub calls" in guardrails
    assert "no live boltz calls" in guardrails
    assert "no embedding generation" in guardrails
    assert "no cofolding input generation" in guardrails
    assert "validated biological hit" in disallowed
    assert "therapeutic candidate" in disallowed
