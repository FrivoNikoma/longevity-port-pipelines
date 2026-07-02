from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

COFOLDING_SCHEMA_PATH = ROOT / "data/config/generic_cofolding_readiness_schema.yaml"
CLAIM_POLICY_PATH = ROOT / "data/config/claim_policy_schema.yaml"
GATED_CONTRAST_SCHEMA_PATH = ROOT / "data/config/generic_gated_contrast_schema.yaml"
LANE_REGISTRY_PATH = ROOT / "data/config/candidate_lanes.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_generic_cofolding_readiness_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)

    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "generic_cofolding_readiness_schema"
    assert schema["pipeline_gate"] == "cofolding_readiness"


def test_generic_cofolding_readiness_schema_matches_lane_gate_sequence() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert schema["pipeline_gate"] in lane_registry["required_gate_sequence"]
    assert lane_registry["required_gate_sequence"].index("longevity_contrast") < lane_registry[
        "required_gate_sequence"
    ].index("cofolding_readiness")


def test_generic_cofolding_readiness_schema_uses_claim_policy_schema() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)
    claim_policy = load_yaml(CLAIM_POLICY_PATH)

    assert schema["claim_policy"] in claim_policy["allowed_claim_policies"]
    assert schema["maximum_claim_status"] in claim_policy["allowed_claim_statuses"]
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "cofolding_readiness"


def test_generic_cofolding_readiness_schema_consumes_gate8_output_fields() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)
    gated_contrast_schema = load_yaml(GATED_CONTRAST_SCHEMA_PATH)

    required_upstream = set(schema["required_upstream_fields"])
    gate8_outputs = set(gated_contrast_schema["required_output_fields"])

    assert required_upstream <= gate8_outputs
    assert {
        "candidate_set",
        "lane_name",
        "candidate_id",
        "source_uniprot",
        "long_lived_species",
        "contrast_class",
        "contrast_requires_review",
        "robustness_status",
        "contrast_status",
        "contrast_dry_run_allowed",
        "controlled_claim_allowed",
        "claim_policy",
        "claim_status",
    } <= required_upstream


def test_generic_cofolding_readiness_schema_lists_required_context_fields() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)

    required_context = set(schema["required_context_fields"])
    assert {
        "partner_uniprot",
        "partner_context_status",
        "source_provenance_status",
        "cofolding_input_review_status",
        "live_opt_in_status",
    } <= required_context
    assert required_context <= set(schema["required_input_fields"])


def test_generic_cofolding_readiness_schema_lists_required_output_fields() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)

    required = set(schema["required_output_fields"])
    assert {
        "candidate_set",
        "lane_name",
        "candidate_id",
        "pdb_id",
        "chain",
        "source_uniprot",
        "target_species",
        "partner_uniprot",
        "contrast_class",
        "contrast_status",
        "robustness_status",
        "cofolding_input_review_status",
        "cofolding_readiness_status",
        "recommended_next_action",
        "cofolding_dry_run_allowed",
        "live_cofolding_allowed",
        "controlled_claim_allowed",
        "claim_policy",
        "claim_status",
        "cofolding_readiness_note",
    } <= required


def test_generic_cofolding_readiness_schema_lists_status_groups() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)

    allowed = set(schema["allowed_cofolding_readiness_statuses"])
    dry_run_ready = set(schema["status_groups"]["dry_run_ready"])
    blocked = set(schema["status_groups"]["blocked"])

    assert dry_run_ready <= allowed
    assert blocked <= allowed
    assert dry_run_ready.isdisjoint(blocked)
    assert dry_run_ready | blocked == allowed


def test_generic_cofolding_readiness_schema_blocks_live_and_controlled_claims() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)
    dry_run_ready = set(schema["status_groups"]["dry_run_ready"])

    for status in schema["allowed_cofolding_readiness_statuses"]:
        decision = schema["decision_rules"][status]
        assert decision["cofolding_dry_run_allowed"] is (status in dry_run_ready)
        assert decision["live_cofolding_allowed"] is False
        assert decision["controlled_claim_allowed"] is False
        assert "recommended_next_action" in decision


def test_generic_cofolding_readiness_schema_records_minimum_requirements() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)

    requirements = schema["minimum_input_requirements"]
    assert requirements["requires_gate8_contrast_dry_run_allowed"] is True
    assert requirements["requires_conservative_claim_policy"] is True
    assert requirements["requires_controlled_claim_allowed_false"] is True
    assert requirements["requires_reviewed_dry_run_inputs_before_ready_status"] is True
    assert requirements["requires_live_not_requested_for_schema_checks"] is True
    assert "technical_contrast_ready" in requirements["allowed_gate8_contrast_statuses"]
    assert "technical_contrast_limited_dry_run" in requirements["allowed_gate8_contrast_statuses"]


def test_generic_cofolding_readiness_schema_records_context_statuses() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)
    context = schema["allowed_context_statuses"]

    assert "partner_context_ready" in context["partner_context"]
    assert "missing_partner_context" in context["partner_context"]
    assert "source_provenance_ready" in context["source_provenance"]
    assert "missing_source_provenance" in context["source_provenance"]
    assert "dry_run_inputs_reviewed" in context["cofolding_input_review"]
    assert "dry_run_inputs_unreviewed" in context["cofolding_input_review"]
    assert "live_not_requested" in context["live_opt_in"]
    assert "live_requested_requires_separate_review" in context["live_opt_in"]


def test_generic_cofolding_readiness_schema_covers_biological_modes() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)

    assert set(schema["biological_mode_interpretation"]) == set(
        lane_registry["allowed_biological_modes"]
    )


def test_generic_cofolding_readiness_schema_blocks_overclaiming() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)

    for phrase in [
        "cofolding validates the candidate",
        "Boltz validates the candidate",
        "validated structural compatibility",
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert phrase in schema["disallowed_language"]


def test_generic_cofolding_readiness_schema_records_no_live_action_guardrails() -> None:
    schema = load_yaml(COFOLDING_SCHEMA_PATH)

    guardrails = set(schema["required_guardrails"])
    assert "no Biohub calls from cofolding-readiness schema checks" in guardrails
    assert "no Boltz calls from cofolding-readiness schema checks" in guardrails
    assert "no live structural calls from cofolding-readiness schema checks" in guardrails
    assert "no embedding generation from cofolding-readiness schema checks" in guardrails
    assert "no cofolding input generation from cofolding-readiness schema checks" in guardrails
    assert "no cofolding job submission from cofolding-readiness schema checks" in guardrails
    assert "no Boltz credit spend from cofolding-readiness schema checks" in guardrails
    assert "no committed signed structure URLs from cofolding-readiness schema checks" in guardrails
    assert "no biological claims from cofolding readiness alone" in guardrails
    assert "live cofolding requires a separate explicit opt-in step" in guardrails
