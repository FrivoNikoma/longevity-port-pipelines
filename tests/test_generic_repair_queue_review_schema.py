from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEW_SCHEMA_PATH = ROOT / "data/config/generic_repair_queue_review_schema.yaml"
CLAIM_POLICY_PATH = ROOT / "data/config/claim_policy_schema.yaml"
LANE_REGISTRY_PATH = ROOT / "data/config/candidate_lanes.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_generic_repair_queue_review_schema_exists_and_is_versioned() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    assert schema["schema_version"] == 1
    assert schema["schema_id"] == "generic_repair_queue_review_schema"
    assert schema["pipeline_gate"] == "repair_decisions"


def test_generic_repair_queue_review_schema_matches_lane_gate_sequence() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    lane_registry = load_yaml(LANE_REGISTRY_PATH)
    assert schema["pipeline_gate"] in lane_registry["required_gate_sequence"]


def test_generic_repair_queue_review_schema_uses_claim_policy_schema() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    claim_policy = load_yaml(CLAIM_POLICY_PATH)
    assert schema["claim_policy"] in claim_policy["allowed_claim_policies"]
    assert schema["maximum_claim_status"] in claim_policy["allowed_claim_statuses"]
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_generic_repair_queue_review_schema_preserves_blocker_first_semantics() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    assert schema["review_scope"]["from_status"] == "unreviewed_gate4_gate5_blocker"
    assert schema["review_scope"]["to_status"] == "reviewed_for_planning_provenance_evidence"
    assert "unreviewed row is a valid" in schema["purpose"]
    guardrails = set(schema["required_guardrails"])
    assert "unreviewed rows remain valid blocked repair-queue worklist items" in guardrails


def test_generic_repair_queue_review_schema_lists_required_fields() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    pre_review = set(schema["required_pre_review_fields"])
    review = set(schema["required_review_fields"])

    assert {
        "candidate_set",
        "lane_name",
        "candidate_id",
        "source_table",
        "source_row_index",
        "source_uniprot",
        "target_species",
        "target_species_taxid",
        "target_uniprot_before_review",
        "repair_queue_status_before_review",
        "downstream_block_status_before_review",
    } <= pre_review

    assert {
        "review_decision",
        "reviewed_target_uniprot",
        "reviewed_source_database",
        "reviewed_source_accession",
        "reviewed_taxid",
        "review_evidence_uri_or_note",
        "downstream_block_status_after_review",
        "allowed_next_action_after_review",
        "claim_status_after_review",
        "forbidden_actions_after_review",
    } <= review


def test_generic_repair_queue_review_schema_lists_allowed_decisions() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    allowed = set(schema["allowed_review_decisions"])
    assert allowed == {
        "accepted_for_planning_after_review",
        "rejected_after_review",
        "deferred_pending_source",
        "needs_second_reviewer",
    }
    assert set(schema["status_groups"]["reviewed_for_planning"]) <= allowed
    assert set(schema["status_groups"]["blocked"]) <= allowed


def test_generic_repair_queue_review_schema_keeps_downstream_blocked() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    for decision in schema["allowed_review_decisions"]:
        rule = schema["review_decision_rules"][decision]
        assert rule["gate8_eligible"] is False
        assert rule["gate9_eligible"] is False
        assert rule["embedding_ready"] is False
        assert rule["boltz_ready"] is False
        assert rule["validated_ortholog_claim_allowed"] is False
        assert rule["biological_claim_allowed"] is False
        assert rule["claim_status_after_review"] == "repair_worklist"


def test_generic_repair_queue_review_schema_accepts_planning_only() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    rule = schema["review_decision_rules"]["accepted_for_planning_after_review"]
    assert rule["gate4_gate5_policy_update_allowed"] is True
    assert (
        rule["allowed_next_action_after_review"]
        == "consider_later_explicit_gate4_gate5_policy_update"
    )
    assert rule["downstream_block_status_after_review"] == (
        "reviewed_for_planning_still_policy_blocked"
    )


def test_generic_repair_queue_review_schema_records_evidence_source_policy() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    acceptable = set(schema["acceptable_evidence_source_types"])
    unacceptable = set(schema["unacceptable_evidence_source_types"])

    assert "reviewed_uniprot_entry" in acceptable
    assert "ncbi_protein_or_gene_record" in acceptable
    assert "ensembl_orthology_evidence" in acceptable
    assert "primary_literature_with_accession_level_evidence" in acceptable

    assert "embedding_similarity_alone" in unacceptable
    assert "downstream_enrichment_result" in unacceptable
    assert "boltz_af3_chai_or_cofolding_result" in unacceptable
    assert "biological_narrative_without_source_accession_evidence" in unacceptable


def test_generic_repair_queue_review_schema_blocks_overclaiming() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    for phrase in [
        "validated ortholog",
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "embedding ready",
        "Boltz ready",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert phrase in schema["disallowed_language"]


def test_generic_repair_queue_review_schema_records_no_live_action_guardrails() -> None:
    schema = load_yaml(REVIEW_SCHEMA_PATH)
    guardrails = set(schema["required_guardrails"])
    assert "reviewed decisions do not fetch sequences" in guardrails
    assert "reviewed decisions do not curate orthologs automatically" in guardrails
    assert "reviewed decisions do not call Biohub" in guardrails
    assert "reviewed decisions do not generate embeddings" in guardrails
    assert "reviewed decisions do not call Boltz" in guardrails
    assert "reviewed decisions do not promote Gate 8" in guardrails
    assert "reviewed decisions do not promote Gate 9" in guardrails
    assert "reviewed decisions do not make biological claims" in guardrails
