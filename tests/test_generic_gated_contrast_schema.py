from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

GATED_CONTRAST_SCHEMA_PATH = ROOT / "data/config/generic_gated_contrast_schema.yaml"
LANE_REGISTRY_PATH = ROOT / "data/config/candidate_lanes.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_generic_gated_contrast_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)

    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "generic_gated_contrast_schema"
    assert schema["pipeline_gate"] == "longevity_contrast"


def test_generic_gated_contrast_schema_matches_lane_gate_sequence() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert schema["pipeline_gate"] in lane_registry["required_gate_sequence"]


def test_generic_gated_contrast_schema_uses_conservative_claim_policy() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert schema["claim_policy"] == lane_registry["claim_policy"]
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "technical_contrast_checkpoint"


def test_generic_gated_contrast_schema_lists_required_input_fields() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)

    required = set(schema["required_input_fields"])
    assert {
        "candidate_set",
        "lane_name",
        "candidate_id",
        "source_uniprot",
        "strict_panel_status",
        "contrast_dry_run_allowed",
        "controlled_claim_allowed",
        "target_species",
        "species_group",
        "enrichment_ratio",
        "effect_size",
        "p_two_sided",
        "claim_policy",
    } <= required


def test_generic_gated_contrast_schema_lists_required_output_fields() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)

    required = set(schema["required_output_fields"])
    assert {
        "candidate_set",
        "lane_name",
        "candidate_id",
        "source_uniprot",
        "long_lived_species",
        "short_lived_species",
        "short_lived_control_count",
        "long_enrichment_ratio",
        "short_enrichment_ratio",
        "enrichment_delta",
        "enrichment_log2_ratio",
        "contrast_class",
        "contrast_priority",
        "contrast_status",
        "recommended_next_action",
        "contrast_dry_run_allowed",
        "controlled_claim_allowed",
        "claim_policy",
        "claim_status",
        "contrast_note",
    } <= required


def test_generic_gated_contrast_schema_lists_status_groups() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)

    allowed = set(schema["allowed_contrast_statuses"])
    dry_run_outputs = set(schema["status_groups"]["dry_run_outputs"])
    blocked = set(schema["status_groups"]["blocked"])

    assert dry_run_outputs <= allowed
    assert blocked <= allowed
    assert dry_run_outputs.isdisjoint(blocked)
    assert dry_run_outputs | blocked == allowed


def test_generic_gated_contrast_schema_blocks_controlled_claims() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)
    dry_run_outputs = set(schema["status_groups"]["dry_run_outputs"])

    for status in schema["allowed_contrast_statuses"]:
        decision = schema["decision_rules"][status]
        assert decision["controlled_claim_allowed"] is False
        assert decision["contrast_dry_run_allowed"] is (status in dry_run_outputs)


def test_generic_gated_contrast_schema_requires_strict_panel_permission() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)

    requirements = schema["minimum_input_requirements"]
    assert requirements["requires_strict_panel_contrast_dry_run_allowed"] is True
    assert requirements["min_long_lived_ready_species"] >= 1
    assert requirements["min_short_lived_control_species"] >= 1
    assert requirements["required_group_contrast"] == "long_lived_vs_short_lived"

    blocked_rule = schema["decision_rules"]["blocked_strict_panel_not_ready"]
    assert blocked_rule["contrast_dry_run_allowed"] is False
    assert blocked_rule["recommended_next_action"] == "resolve_strict_panel_before_contrast"


def test_generic_gated_contrast_schema_records_allowed_contrast_classes() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)

    contrast_classes = set(schema["allowed_contrast_classes"])
    assert "long_lived_specific_interface_divergence" in contrast_classes
    assert "long_lived_specific_interface_constraint" in contrast_classes
    assert "short_lived_baseline_stronger_signal" in contrast_classes
    assert "weak_or_unresolved_contrast" in contrast_classes


def test_generic_gated_contrast_schema_blocks_overclaiming() -> None:
    text = GATED_CONTRAST_SCHEMA_PATH.read_text(encoding="utf-8")

    assert "technical contrast checkpoint" in text
    assert "validated longevity signal" in text
    assert "validated biological hit" in text
    assert "confirmed binding change" in text
    assert "confirmed functional effect" in text
    assert "safe to port" in text


def test_generic_gated_contrast_schema_records_no_live_action_guardrails() -> None:
    schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)

    guardrails = set(schema["required_guardrails"])
    assert "no Biohub calls from gated-contrast schema checks" in guardrails
    assert "no Boltz calls from gated-contrast schema checks" in guardrails
    assert "no live structural calls from gated-contrast schema checks" in guardrails
    assert "no embedding generation from gated-contrast schema checks" in guardrails
    assert "no cofolding input generation from gated-contrast schema checks" in guardrails
    assert "no biological claims from Gate 8 alone" in guardrails
    assert "strict panel dry-run permission is required before gated contrast" in guardrails
