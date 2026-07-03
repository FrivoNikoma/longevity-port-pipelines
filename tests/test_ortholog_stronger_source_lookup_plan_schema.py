from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_lookup_plan_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_lookup_plan_schema_exists_and_is_blocker_first() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "generic_ortholog_stronger_source_lookup_plan_schema"
    assert schema["pipeline_gate"] == "ortholog_stronger_source_lookup_plan"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"
    assert schema["maximum_claim_status"] == "repair_worklist"


def test_lookup_plan_schema_references_policy_document() -> None:
    schema = load_schema()

    assert schema["policy_document"] == ("docs/ortholog_stronger_source_lookup_api_policy.md")


def test_lookup_plan_schema_starts_from_source_collection_request() -> None:
    schema = load_schema()

    assert set(schema["plan_scope"]["from_request_status"]) == {
        "pending_source_collection",
        "source_collection_in_progress",
    }
    assert schema["plan_scope"]["from_request_decision"] == ["needs_manual_source_collection"]
    assert schema["plan_scope"]["lookup_plan_status"] == ["lookup_planned_still_blocked"]


def test_lookup_plan_schema_disables_live_lookup_and_sequence_fetch_by_default() -> None:
    schema = load_schema()
    plan_scope = schema["plan_scope"]

    assert plan_scope["default_live_lookup_allowed"] is False
    assert plan_scope["default_sequence_fetch_allowed"] is False
    assert plan_scope["ci_external_api_allowed"] is False
    assert plan_scope["allowed_output_target"] == [
        "data/input/ortholog_stronger_source_evidence_collection.csv"
    ]


def test_lookup_plan_schema_does_not_authorize_downstream_work() -> None:
    schema = load_schema()
    blocked = set(schema["plan_scope"]["does_not_authorize"])

    assert "live external database lookup by default" in blocked
    assert "sequence fetch" in blocked
    assert "curated ortholog candidate creation" in blocked
    assert "standard ortholog coverage population" in blocked
    assert "Gate 4 / Gate 5 policy update" in blocked
    assert "Gate 8 eligibility" in blocked
    assert "Gate 9 eligibility" in blocked
    assert "Biohub calls" in blocked
    assert "embedding generation" in blocked
    assert "accepted ortholog claims" in blocked
    assert "validated ortholog claims" in blocked
    assert "reviewed decision creation" in blocked
    assert "biological claims" in blocked


def test_lookup_plan_schema_required_fields_are_distinct() -> None:
    schema = load_schema()

    trace_fields = set(schema["required_request_trace_fields"])
    lookup_plan_fields = set(schema["required_lookup_plan_fields"])

    assert "candidate_id" in trace_fields
    assert "request_table" in trace_fields
    assert "requested_evidence_source_accession" in trace_fields
    assert "planned_lookup_source_type" in lookup_plan_fields
    assert "planned_lookup_mode" in lookup_plan_fields
    assert "forbidden_actions_after_lookup_plan" in lookup_plan_fields
    assert not (trace_fields & lookup_plan_fields)


def test_lookup_plan_schema_allowed_source_types_cover_requested_sources() -> None:
    schema = load_schema()

    assert set(schema["allowed_planned_lookup_source_types"]) == {
        "reviewed_uniprot",
        "ncbi_protein_or_gene_record",
        "ensembl_orthology",
        "oma_orthology",
        "orthodb_orthology",
        "primary_literature",
        "other_manual_source",
    }


def test_lookup_plan_schema_allowed_values_are_conservative() -> None:
    schema = load_schema()

    assert set(schema["allowed_planned_lookup_modes"]) == {
        "dry_run_plan_only",
        "fixture_backed_only",
        "explicit_live_opt_in_required",
    }
    assert schema["allowed_live_lookup_allowed_values"] == [False]
    assert schema["allowed_sequence_fetch_allowed_values"] == [False]
    assert set(schema["allowed_lookup_plan_statuses"]) == {
        "lookup_planned_still_blocked",
        "lookup_deferred_keep_blocked",
        "lookup_not_planned_keep_blocked",
    }
    assert schema["allowed_downstream_block_statuses_after_lookup_plan"] == ["blocked_gate4_gate5"]
    assert schema["allowed_claim_statuses_after_lookup_plan"] == ["repair_worklist"]
    assert schema["allowed_claim_policies_after_lookup_plan"] == [
        "no_biological_claims_until_validation"
    ]


def test_lookup_plan_schema_guardrails_block_runtime_side_effects() -> None:
    schema = load_schema()
    guardrails = set(schema["required_guardrails"])

    assert "lookup plan rows do not collect evidence by themselves" in guardrails
    assert "lookup plan rows do not accept orthologs automatically" in guardrails
    assert "lookup plan rows do not create curated ortholog candidates automatically" in guardrails
    assert "lookup plan rows do not populate standard ortholog coverage automatically" in guardrails
    assert "lookup plan rows do not permit live external database lookup by default" in guardrails
    assert "lookup plan rows do not fetch sequences" in guardrails
    assert "lookup plan rows do not call Biohub" in guardrails
    assert "lookup plan rows do not generate embeddings" in guardrails
    assert "lookup plan rows do not call Boltz" in guardrails
    assert "lookup plan rows do not promote Gate 8" in guardrails
    assert "lookup plan rows do not promote Gate 9" in guardrails
    assert "lookup plan rows do not make biological claims" in guardrails
