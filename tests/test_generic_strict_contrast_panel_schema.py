from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

STRICT_PANEL_SCHEMA_PATH = ROOT / "data/config/generic_strict_contrast_panel_schema.yaml"
LANE_REGISTRY_PATH = ROOT / "data/config/candidate_lanes.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_generic_strict_contrast_panel_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)

    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "generic_strict_contrast_panel_schema"
    assert schema["pipeline_gate"] == "strict_panel_or_contrast_gate"


def test_generic_strict_contrast_panel_schema_matches_lane_gate_sequence() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert schema["pipeline_gate"] in lane_registry["required_gate_sequence"]


def test_generic_strict_contrast_panel_schema_uses_conservative_claim_policy() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert schema["claim_policy"] == lane_registry["claim_policy"]
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "strict_panel_readiness"


def test_generic_strict_contrast_panel_schema_lists_required_input_fields() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)

    required = set(schema["required_input_fields"])
    assert {
        "candidate_set",
        "lane_name",
        "candidate_id",
        "source_uniprot",
        "target_species",
        "species_group",
        "coverage_preflight_status",
        "control_readiness_status",
        "contrast_readiness_status",
        "claim_policy",
    } <= required


def test_generic_strict_contrast_panel_schema_lists_required_output_fields() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)

    required = set(schema["required_output_fields"])
    assert {
        "candidate_set",
        "lane_name",
        "candidate_id",
        "source_uniprot",
        "n_strict_panel_ready_species",
        "n_strict_panel_blocked_species",
        "n_strict_long_lived_ready",
        "n_strict_short_lived_ready",
        "strict_panel_status",
        "recommended_next_action",
        "contrast_dry_run_allowed",
        "controlled_claim_allowed",
        "claim_policy",
        "claim_status",
        "strict_panel_note",
    } <= required


def test_generic_strict_contrast_panel_schema_lists_status_groups() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)

    allowed = set(schema["allowed_strict_panel_statuses"])
    dry_run_ready = set(schema["status_groups"]["dry_run_ready"])
    blocked = set(schema["status_groups"]["blocked"])

    assert dry_run_ready <= allowed
    assert blocked <= allowed
    assert dry_run_ready.isdisjoint(blocked)
    assert dry_run_ready | blocked == allowed


def test_generic_strict_contrast_panel_schema_blocks_controlled_claims() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)
    dry_run_ready = set(schema["status_groups"]["dry_run_ready"])

    for status in schema["allowed_strict_panel_statuses"]:
        decision = schema["decision_rules"][status]
        assert decision["controlled_claim_allowed"] is False
        assert decision["contrast_dry_run_allowed"] is (status in dry_run_ready)


def test_generic_strict_contrast_panel_schema_records_minimum_panel_requirements() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)

    minimums = schema["minimum_panel_requirements"]
    assert minimums["min_long_lived_ready_species"] >= 1
    assert minimums["min_short_lived_ready_species"] >= 1
    assert minimums["min_total_ready_species"] >= 2
    assert minimums["required_group_contrast"] == "long_lived_vs_short_lived"


def test_generic_strict_contrast_panel_schema_covers_biological_modes() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert set(schema["biological_mode_interpretation"]) == set(
        lane_registry["allowed_biological_modes"]
    )


def test_generic_strict_contrast_panel_schema_blocks_overclaiming() -> None:
    text = STRICT_PANEL_SCHEMA_PATH.read_text(encoding="utf-8")

    assert "technical contrast dry-run" in text
    assert "validated longevity signal" in text
    assert "validated biological hit" in text
    assert "confirmed binding change" in text
    assert "confirmed functional effect" in text
    assert "safe to port" in text
    assert "proven pro-longevity variant" in text


def test_generic_strict_contrast_panel_schema_records_no_live_action_guardrails() -> None:
    schema = load_yaml(STRICT_PANEL_SCHEMA_PATH)

    guardrails = set(schema["required_guardrails"])
    assert "no Biohub calls from strict-panel schema checks" in guardrails
    assert "no Boltz calls from strict-panel schema checks" in guardrails
    assert "no live structural calls from strict-panel schema checks" in guardrails
    assert "no embedding generation from strict-panel schema checks" in guardrails
    assert "no cofolding input generation from strict-panel schema checks" in guardrails
    assert "no biological claims from strict-panel readiness alone" in guardrails
