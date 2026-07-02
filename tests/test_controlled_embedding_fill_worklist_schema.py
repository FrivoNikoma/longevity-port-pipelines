from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/controlled_embedding_fill_worklist_schema.yaml"
CLAIM_POLICY_PATH = ROOT / "data/config/claim_policy_schema.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_controlled_embedding_fill_worklist_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(SCHEMA_PATH)

    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "controlled_embedding_fill_worklist_schema"
    assert schema["pipeline_gate"] == "controlled_embedding_fill_worklist"


def test_controlled_embedding_fill_worklist_schema_uses_claim_policy_schema() -> None:
    schema = load_yaml(SCHEMA_PATH)
    claim_policy = load_yaml(CLAIM_POLICY_PATH)

    assert schema["claim_policy"] in claim_policy["allowed_claim_policies"]
    assert schema["maximum_claim_status"] in claim_policy["allowed_claim_statuses"]
    assert schema["maximum_claim_status"] == "technical_checkpoint"


def test_controlled_embedding_fill_worklist_schema_references_protocol_and_precedent() -> None:
    schema = load_yaml(SCHEMA_PATH)

    assert schema["protocol_reference"] == "docs/controlled_embedding_fill_protocol.md"
    assert schema["planning_reference"] == "docs/gate_aware_embedding_fill_plan.md"
    assert schema["precedent_reference"] == "docs/brandts_bat_p09874_live_embedding_generation.md"


def test_controlled_embedding_fill_worklist_schema_lists_protocol_statuses() -> None:
    schema = load_yaml(SCHEMA_PATH)

    for status in [
        "ready_for_preflight",
        "needs_coverage_repair",
        "needs_source_provenance_review",
        "defer_until_gate8_ready",
        "reviewed_for_single_live_fill",
        "do_not_fill",
    ]:
        assert status in schema["allowed_fill_statuses"]

    for group in ["preflight_ready", "live_review_ready", "blocked"]:
        for status in schema["status_groups"][group]:
            assert status in schema["allowed_fill_statuses"]


def test_controlled_embedding_fill_worklist_schema_has_decision_rule_for_every_status() -> None:
    schema = load_yaml(SCHEMA_PATH)

    assert set(schema["decision_rules"]) == set(schema["allowed_fill_statuses"])

    for status, rule in schema["decision_rules"].items():
        assert "recommended_next_action" in rule
        assert rule["recommended_next_action"] in schema["allowed_next_actions"]
        assert isinstance(rule["dry_run_preflight_allowed"], bool)
        assert isinstance(rule["dry_run_single_allowed"], bool)
        assert isinstance(rule["live_call_allowed"], bool)
        assert rule["live_opt_in_required"] is True

        if status != "reviewed_for_single_live_fill":
            assert rule["live_call_allowed"] is False
            assert rule["max_live_batch_size"] == 0


def test_controlled_embedding_fill_worklist_schema_locks_single_live_fill_requirements() -> None:
    schema = load_yaml(SCHEMA_PATH)

    rule = schema["decision_rules"]["reviewed_for_single_live_fill"]

    assert rule["dry_run_preflight_allowed"] is True
    assert rule["dry_run_single_allowed"] is True
    assert rule["live_call_allowed"] is True
    assert rule["live_opt_in_required"] is True
    assert rule["max_live_batch_size"] == 1
    assert rule["required_live_flag"] == "--yes-live"
    assert rule["required_sequence_length_status"] == "matches"
    assert rule["required_embedding_exists_before_live"] is False


def test_controlled_embedding_fill_worklist_schema_records_required_output_fields() -> None:
    schema = load_yaml(SCHEMA_PATH)

    for field in [
        "candidate_set",
        "lane_name",
        "candidate_id",
        "complex_id",
        "chain",
        "source_uniprot",
        "target_species",
        "target_species_taxid",
        "target_accession",
        "target_accession_db",
        "target_sequence_length",
        "actual_sequence_length",
        "sequence_length_status",
        "embedding_path",
        "embedding_exists",
        "embedding_status",
        "fill_status",
        "fill_reason",
        "gate_dependency",
        "source_provenance_status",
        "coverage_repair_status",
        "dry_run_required",
        "live_opt_in_required",
        "max_live_batch_size",
        "allowed_next_action",
        "forbidden_actions",
        "claim_policy",
        "claim_status",
        "review_note",
    ]:
        assert field in schema["required_output_fields"]


def test_controlled_embedding_fill_worklist_schema_records_required_review_fields_before_live() -> (
    None
):
    schema = load_yaml(SCHEMA_PATH)

    for field in [
        "candidate_id",
        "target_species",
        "target_species_taxid",
        "source_uniprot",
        "target_accession",
        "reviewed_target_sequence",
        "reviewed_source_provenance",
        "no_unresolved_coverage_blocker",
        "fill_reason",
        "curated_embedding_preflight_output",
        "curated_embedding_single_dry_run_output",
        "human_approval_for_yes_live",
    ]:
        assert field in schema["required_review_fields_before_live"]


def test_controlled_embedding_fill_worklist_schema_blocks_overclaiming() -> None:
    schema = load_yaml(SCHEMA_PATH)

    for phrase in [
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert phrase in schema["disallowed_language"]


def test_controlled_embedding_fill_worklist_schema_records_no_live_action_guardrails() -> None:
    schema = load_yaml(SCHEMA_PATH)

    guardrails = schema["required_guardrails"]

    assert "no Biohub calls from worklist schema checks" in guardrails
    assert "no embeddings generated by worklist schema checks" in guardrails
    assert "no data/output artifacts committed from worklist schema checks" in guardrails
    assert "no Boltz calls from worklist schema checks" in guardrails
    assert "no enrichment or contrast rerun from worklist schema checks" in guardrails
    assert "no biological claims from embedding fill worklist status" in guardrails
    assert "TP53/MDM2 remains blocked while coverage/provenance is unresolved" in guardrails
