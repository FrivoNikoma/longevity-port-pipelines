from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_raw_metadata_response_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_raw_metadata_response_schema_exists_and_is_blocker_first() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "generic_ortholog_stronger_source_raw_metadata_response_schema"
    assert schema["pipeline_gate"] == "ortholog_stronger_source_raw_metadata_response"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_raw_metadata_response_schema_starts_from_dry_run_candidate() -> None:
    schema = load_schema()

    assert schema["response_scope"]["from_dry_run_status"] == [
        "dry_run_raw_metadata_candidate_still_blocked"
    ]
    assert schema["response_scope"]["to_status"] == (
        "raw_metadata_received_unreviewed_still_blocked"
    )
    assert set(schema["response_scope"]["raw_metadata_is"]) == {
        "unreviewed",
        "non_evidence",
        "blocked_gate4_gate5",
        "repair_worklist",
    }


def test_raw_metadata_response_schema_does_not_authorize_downstream_work() -> None:
    schema = load_schema()
    blocked = set(schema["response_scope"]["does_not_authorize"])

    assert "Gate 4 / Gate 5 policy update" in blocked
    assert "Gate 8 eligibility" in blocked
    assert "Gate 9 eligibility" in blocked
    assert "sequence fetch" in blocked
    assert "source evidence creation" in blocked
    assert "manual review row creation" in blocked
    assert "reviewed decision creation" in blocked
    assert "accepted ortholog claims" in blocked
    assert "validated ortholog claims" in blocked
    assert "runtime persistence from live provider" in blocked
    assert "Biohub calls" in blocked
    assert "embedding generation" in blocked
    assert "Boltz readiness" in blocked
    assert "AF3 readiness" in blocked
    assert "Chai readiness" in blocked
    assert "biological claims" in blocked


def test_raw_metadata_response_schema_required_fields_are_distinct() -> None:
    schema = load_schema()

    request_trace_fields = set(schema["required_request_trace_fields"])
    lookup_trace_fields = set(schema["required_lookup_trace_fields"])
    response_fields = set(schema["required_raw_metadata_response_fields"])

    assert "candidate_id" in request_trace_fields
    assert "request_table" in request_trace_fields
    assert "planned_lookup_query_identifier" in lookup_trace_fields
    assert "dry_run_provider_mode" in lookup_trace_fields
    assert "raw_metadata_response_status" in response_fields
    assert "source_evidence_created" in response_fields
    assert "reviewed_decision_created" in response_fields
    assert "biological_claim_status" in response_fields
    assert "forbidden_actions_after_raw_metadata" in response_fields

    assert not (request_trace_fields & lookup_trace_fields)
    assert not (request_trace_fields & response_fields)
    assert not (lookup_trace_fields & response_fields)


def test_raw_metadata_response_schema_allowed_values_are_conservative() -> None:
    schema = load_schema()

    assert set(schema["allowed_dry_run_statuses"]) == {
        "dry_run_raw_metadata_candidate_still_blocked",
        "dry_run_skipped_policy_denied_still_blocked",
    }
    assert schema["allowed_dry_run_provider_modes"] == ["injected_fake_or_noop_provider_only"]
    assert set(schema["allowed_raw_metadata_response_statuses"]) == {
        "raw_metadata_received_unreviewed_still_blocked",
        "raw_metadata_not_requested_policy_denied",
        "raw_metadata_deferred_keep_blocked",
        "raw_metadata_conflict_keep_blocked",
    }
    assert set(schema["allowed_raw_metadata_review_statuses"]) == {
        "unreviewed_raw_metadata",
        "raw_metadata_requires_manual_review",
    }
    assert schema["allowed_downstream_block_statuses_after_raw_metadata"] == ["blocked_gate4_gate5"]
    assert schema["allowed_claim_statuses_after_raw_metadata"] == ["repair_worklist"]
    assert schema["allowed_claim_policies_after_raw_metadata"] == [
        "no_biological_claims_until_validation"
    ]
    assert schema["allowed_biological_claim_statuses"] == ["no_biological_claim"]


def test_raw_metadata_response_schema_false_flags_cover_side_effects() -> None:
    schema = load_schema()

    assert set(schema["allowed_false_flags"]) == {
        "sequence_fetched",
        "source_evidence_created",
        "reviewed_decision_created",
        "gate4_gate5_policy_updated",
        "gate8_promoted",
        "gate9_promoted",
    }


def test_raw_metadata_response_schema_guardrails_block_runtime_side_effects() -> None:
    schema = load_schema()
    guardrails = set(schema["required_guardrails"])

    assert "raw metadata response rows remain unreviewed" in guardrails
    assert "raw metadata response rows are not source evidence" in guardrails
    assert "raw metadata response rows do not create manual review rows" in guardrails
    assert "raw metadata response rows do not create reviewed decisions" in guardrails
    assert "raw metadata response rows do not accept orthologs" in guardrails
    assert "raw metadata response rows do not validate orthologs" in guardrails
    assert "raw metadata response rows do not update Gate 4 / Gate 5 policy" in guardrails
    assert "raw metadata response rows do not fetch sequences" in guardrails
    assert (
        "raw metadata response rows do not write runtime persistence from live providers"
        in guardrails
    )
    assert "raw metadata response rows do not call Biohub" in guardrails
    assert "raw metadata response rows do not generate embeddings" in guardrails
    assert "raw metadata response rows do not call Boltz" in guardrails
    assert "raw metadata response rows do not promote Gate 8" in guardrails
    assert "raw metadata response rows do not promote Gate 9" in guardrails
    assert "raw metadata response rows do not make biological claims" in guardrails
