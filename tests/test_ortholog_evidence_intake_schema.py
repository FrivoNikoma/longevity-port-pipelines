from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTAKE_SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_intake_schema.yaml"
REVIEW_SCHEMA_PATH = ROOT / "data/config/generic_repair_queue_review_schema.yaml"
CLAIM_POLICY_PATH = ROOT / "data/config/claim_policy_schema.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ortholog_evidence_intake_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)

    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "generic_ortholog_evidence_intake_schema"
    assert schema["pipeline_gate"] == "ortholog_evidence_intake"


def test_ortholog_evidence_intake_schema_uses_conservative_claim_policy() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    claim_policy = load_yaml(CLAIM_POLICY_PATH)

    assert schema["claim_policy"] in claim_policy["allowed_claim_policies"]
    assert schema["maximum_claim_status"] in claim_policy["allowed_claim_statuses"]
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_ortholog_evidence_intake_schema_preserves_blocker_first_semantics() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)

    assert schema["intake_scope"]["from_status"] == "gate4_gate5_repair_queue_worklist_item"
    assert (
        schema["intake_scope"]["to_status"]
        == "accession_level_evidence_candidate_for_later_review_decision"
    )
    assert "not an accepted ortholog" in schema["purpose"]

    guardrails = set(schema["required_guardrails"])
    assert "intake rows remain Gate 4 / Gate 5 repair-queue worklist items" in guardrails
    assert "intake rows do not accept orthologs automatically" in guardrails


def test_ortholog_evidence_intake_schema_lists_required_identity_fields() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    identity_fields = set(schema["required_row_identity_fields"])

    assert {
        "candidate_set",
        "lane_name",
        "candidate_id",
        "source_table",
        "source_row_index",
        "source_uniprot",
        "partner_uniprot",
        "target_species",
        "target_species_taxid",
        "target_uniprot_before_intake",
        "repair_queue_status_before_intake",
        "downstream_block_status_before_intake",
    } <= identity_fields


def test_ortholog_evidence_intake_schema_lists_required_evidence_fields() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    evidence_fields = set(schema["required_evidence_fields"])

    assert {
        "evidence_source_type",
        "evidence_source_database",
        "evidence_source_accession",
        "evidence_uri_or_reproducible_lookup_note",
        "target_taxid",
        "target_species_name",
        "target_gene_symbol",
        "target_protein_accession",
        "reviewer_note",
        "ambiguity_flag",
        "second_reviewer_required",
        "intake_outcome",
        "downstream_block_status_after_intake",
        "allowed_next_action_after_intake",
        "claim_status_after_intake",
        "forbidden_actions_after_intake",
    } <= evidence_fields


def test_ortholog_evidence_intake_schema_reuses_review_evidence_source_policy() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    review_schema = load_yaml(REVIEW_SCHEMA_PATH)

    assert set(schema["allowed_evidence_source_types"]) <= set(
        review_schema["acceptable_evidence_source_types"]
    )
    assert set(schema["unacceptable_evidence_source_types"]) <= set(
        review_schema["unacceptable_evidence_source_types"]
    )


def test_ortholog_evidence_intake_schema_lists_conservative_outcomes() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    review_schema = load_yaml(REVIEW_SCHEMA_PATH)

    allowed = set(schema["allowed_intake_outcomes"])
    assert allowed == {
        "evidence_ready_for_review_decision",
        "evidence_insufficient_defer",
        "evidence_conflict_reject_or_exclude",
        "evidence_ambiguous_needs_second_reviewer",
    }

    for outcome, review_decision in schema["mapping_to_review_decisions"].items():
        assert outcome in allowed
        assert review_decision in review_schema["allowed_review_decisions"]


def test_ortholog_evidence_intake_schema_keeps_downstream_blocked() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)

    for outcome in schema["allowed_intake_outcomes"]:
        rule = schema["intake_outcome_rules"][outcome]
        assert rule["gate4_gate5_policy_update_allowed"] is False
        assert rule["gate8_eligible"] is False
        assert rule["gate9_eligible"] is False
        assert rule["embedding_ready"] is False
        assert rule["biohub_ready"] is False
        assert rule["boltz_ready"] is False
        assert rule["af3_ready"] is False
        assert rule["chai_ready"] is False
        assert rule["accepted_ortholog_claim_allowed"] is False
        assert rule["validated_ortholog_claim_allowed"] is False
        assert rule["biological_claim_allowed"] is False
        assert rule["does_not_auto_accept_ortholog"] is True
        assert rule["downstream_block_status_after_intake"] == "blocked_gate4_gate5"
        assert rule["claim_status_after_intake"] == "repair_worklist"


def test_ortholog_evidence_intake_schema_ready_outcome_is_review_candidate_only() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    rule = schema["intake_outcome_rules"]["evidence_ready_for_review_decision"]

    assert rule["allowed_next_action_after_intake"] == "prepare_later_reviewed_decision_pr"
    assert rule["does_not_auto_accept_ortholog"] is True
    assert rule["gate4_gate5_policy_update_allowed"] is False
    assert rule["downstream_block_status_after_intake"] == "blocked_gate4_gate5"


def test_ortholog_evidence_intake_schema_blocks_overclaiming() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)

    for phrase in [
        "accepted ortholog",
        "validated ortholog",
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "embedding ready",
        "Biohub ready",
        "Boltz ready",
        "AF3 ready",
        "Chai ready",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert phrase in schema["disallowed_language"]


def test_ortholog_evidence_intake_schema_records_no_live_action_guardrails() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    guardrails = set(schema["required_guardrails"])

    assert "intake rows do not fetch sequences" in guardrails
    assert "intake rows do not call Biohub" in guardrails
    assert "intake rows do not generate embeddings" in guardrails
    assert "intake rows do not call Boltz" in guardrails
    assert "intake rows do not call AF3" in guardrails
    assert "intake rows do not call Chai" in guardrails
    assert "intake rows do not promote Gate 8" in guardrails
    assert "intake rows do not promote Gate 9" in guardrails
    assert "intake rows do not make biological claims" in guardrails
