from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

ORTHOLOG_REPAIR_SCHEMA_PATH = ROOT / "data/config/ortholog_repair_decision_schema.yaml"
CLAIM_POLICY_PATH = ROOT / "data/config/claim_policy_schema.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ortholog_repair_decision_schema_uses_conservative_claim_policy() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)
    claim_policy = load_yaml(CLAIM_POLICY_PATH)

    assert schema["claim_policy"] in claim_policy["allowed_claim_policies"]
    assert schema["maximum_claim_status"] == "repair_worklist"
    assert (
        schema["maximum_claim_status"]
        == claim_policy["pipeline_stage_policies"]["repair_decisions"]["maximum_claim_status"]
    )


def test_ortholog_repair_decision_schema_lists_required_fields() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)

    required_fields = set(schema["required_decision_fields"])

    for field in [
        "candidate_set",
        "candidate_id",
        "lane_name",
        "source_species",
        "target_species",
        "gene_symbol",
        "coverage_status",
        "provenance_status",
        "repair_decision",
        "repair_status",
        "claim_policy",
        "reviewer_note",
    ]:
        assert field in required_fields


def test_ortholog_repair_decision_schema_lists_allowed_repair_decisions() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)

    for decision in [
        "no_repair_needed",
        "curate_source_ortholog",
        "fetch_or_curate_source_ortholog",
        "generate_local_candidate_rows",
        "review_local_rows_without_source_ortholog",
        "accept_existing_local_row_after_provenance_review",
        "exclude_from_strict_panel",
        "defer_until_stronger_source",
        "needs_external_manual_sequence_review",
    ]:
        assert decision in schema["allowed_repair_decisions"]


def test_ortholog_repair_decision_schema_blocks_unresolved_rows_from_strict_panel() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)

    strict_panel_blockers = set(schema["strict_panel_effects"]["must_not_enter_strict_panel"])

    for status in [
        "pending",
        "in_review",
        "excluded_from_strict_panel",
        "deferred_pending_source",
        "needs_manual_review",
    ]:
        assert status in strict_panel_blockers


def test_ortholog_repair_decision_schema_allows_reviewed_rows_for_planning_only() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)

    allowed_statuses = set(schema["strict_panel_effects"]["may_enter_strict_panel"])
    contrast_ready_statuses = set(schema["contrast_gate_effects"]["may_enter_contrast_dry_run"])

    for status in [
        "not_needed",
        "repaired_for_planning",
        "accepted_for_planning_after_review",
    ]:
        assert status in allowed_statuses
        assert status in contrast_ready_statuses


def test_ortholog_repair_decision_schema_blocks_overclaiming() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)

    disallowed_language = schema["claim_guardrails"]["disallowed_language"]

    for phrase in [
        "validated ortholog",
        "confirmed conserved function",
        "validated biological hit",
        "validated longevity signal",
        "proven pro-longevity variant",
        "safe to port",
    ]:
        assert phrase in disallowed_language


def test_ortholog_repair_decision_schema_records_no_live_action_guardrails() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)

    guardrails = schema["no_live_action_guardrails"]

    assert "schema validation must not fetch orthologs" in guardrails
    assert "schema validation must not call Biohub" in guardrails
    assert "schema validation must not call Boltz" in guardrails
    assert "schema validation must not generate embeddings" in guardrails
