from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages.controlled_embedding_fill_worklist import (
    FORBIDDEN_ACTIONS,
    _dry_run_required,
    _max_live_batch_size,
    _next_action,
    build_controlled_embedding_fill_worklist,
    classify_fill_row,
    empty_controlled_embedding_fill_worklist,
    fill_status_counts,
    validate_preflight_schema,
)


def preflight_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "complex_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "chain": "receptor",
                "target_species": "brandts_bat",
                "source_uniprot": "P09874",
                "source_species_taxid": 9606,
                "target_species_taxid": 109478,
                "target_accession": "EPQ16369.1",
                "target_accession_db": "NCBI Protein",
                "target_sequence_length": 1024,
                "actual_sequence_length": 1024,
                "sequence_length_status": "matches",
                "model_name": "esmc-300m-2024-12",
                "embedding_path": "data/output/embeddings/model/missing.npy",
                "embedding_exists": False,
                "embedding_status": "missing",
            },
            {
                "complex_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "chain": "ligand",
                "target_species": "brandts_bat",
                "source_uniprot": "Q9UNS1",
                "source_species_taxid": 9606,
                "target_species_taxid": 109478,
                "target_accession": "XP_005878000.1",
                "target_accession_db": "NCBI Protein",
                "target_sequence_length": 300,
                "actual_sequence_length": 300,
                "sequence_length_status": "matches",
                "model_name": "esmc-300m-2024-12",
                "embedding_path": "data/output/embeddings/model/present.npy",
                "embedding_exists": True,
                "embedding_status": "present",
            },
            {
                "complex_id": "8bhv__N1_P49917--8bhv__M1_Q9H9Q4",
                "chain": "ligand",
                "target_species": "mouse",
                "source_uniprot": "Q9H9Q4",
                "source_species_taxid": 9606,
                "target_species_taxid": 10090,
                "target_accession": "NP_001000000.1",
                "target_accession_db": "NCBI Protein",
                "target_sequence_length": 290,
                "actual_sequence_length": 288,
                "sequence_length_status": "mismatch",
                "model_name": "esmc-300m-2024-12",
                "embedding_path": "data/output/embeddings/model/mismatch.npy",
                "embedding_exists": False,
                "embedding_status": "missing",
            },
        ]
    )


def schema_doc() -> dict:
    schema_text = Path("data/config/controlled_embedding_fill_worklist_schema.yaml").read_text(
        encoding="utf-8"
    )
    return yaml.safe_load(schema_text)


def schema_required_fields() -> list[str]:
    return list(schema_doc()["required_output_fields"])


def test_empty_controlled_embedding_fill_worklist_has_schema_columns() -> None:
    worklist = empty_controlled_embedding_fill_worklist()

    assert worklist.is_empty()
    assert worklist.columns == schema_required_fields()


def test_validate_preflight_schema_rejects_missing_required_column() -> None:
    with pytest.raises(ValueError, match="Missing required preflight columns"):
        validate_preflight_schema(preflight_rows().drop("embedding_status"))


def test_build_worklist_outputs_schema_required_fields() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows(),
        candidate_set="sirt6_dna_repair",
        lane_name="SIRT6/core3",
        source_provenance_status="reviewed",
        coverage_repair_status="not_needed",
    )

    assert worklist.columns == schema_required_fields()
    assert worklist.height == 3


def test_build_worklist_marks_missing_reviewed_matches_as_ready_for_preflight() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows(),
        candidate_set="sirt6_dna_repair",
        lane_name="SIRT6/core3",
        source_provenance_status="reviewed",
        coverage_repair_status="not_needed",
    )

    row = worklist.filter(pl.col("embedding_path").str.contains("missing.npy")).row(0, named=True)

    assert row["fill_status"] == "ready_for_preflight"
    assert row["allowed_next_action"] == "run_curated_embedding_preflight"
    assert row["dry_run_required"] is True
    assert row["live_opt_in_required"] is True
    assert row["max_live_batch_size"] == 0
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "technical_checkpoint"
    assert "sequence fetch" in row["forbidden_actions"]
    assert "Biohub call" in row["forbidden_actions"]
    assert "embedding generation" in row["forbidden_actions"]
    assert "Gate 8 promotion" in row["forbidden_actions"]
    assert "Gate 9 promotion" in row["forbidden_actions"]
    assert "Boltz call" in row["forbidden_actions"]
    assert "AF3 call" in row["forbidden_actions"]
    assert "Chai call" in row["forbidden_actions"]
    assert "biological claim" in row["forbidden_actions"]


def test_build_worklist_marks_present_embeddings_as_do_not_fill() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows(),
        candidate_set="sirt6_dna_repair",
        lane_name="SIRT6/core3",
        source_provenance_status="reviewed",
        coverage_repair_status="not_needed",
    )

    row = worklist.filter(pl.col("embedding_path").str.contains("present.npy")).row(0, named=True)

    assert row["fill_status"] == "do_not_fill"
    assert row["allowed_next_action"] == "do_not_fill"
    assert row["dry_run_required"] is False
    assert row["max_live_batch_size"] == 0


def test_build_worklist_marks_length_mismatch_as_source_review_needed() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows(),
        candidate_set="sirt6_dna_repair",
        lane_name="SIRT6/core3",
        source_provenance_status="reviewed",
        coverage_repair_status="not_needed",
    )

    row = worklist.filter(pl.col("sequence_length_status") == "mismatch").row(0, named=True)

    assert row["fill_status"] == "needs_source_provenance_review"
    assert row["allowed_next_action"] == "request_source_provenance_review"
    assert "sequence length" in row["fill_reason"]


def test_build_worklist_defaults_to_source_provenance_review_needed() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows().filter(pl.col("embedding_status") == "missing").head(1),
        candidate_set="sirt6_dna_repair",
        lane_name="SIRT6/core3",
    )

    row = worklist.row(0, named=True)

    assert row["fill_status"] == "needs_source_provenance_review"
    assert row["source_provenance_status"] == "needs_review"
    assert row["max_live_batch_size"] == 0


def test_build_worklist_marks_pending_coverage_as_needs_coverage_repair() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows().head(1),
        candidate_set="tp53_mdm2_elephant",
        lane_name="TP53/MDM2 elephant",
        source_provenance_status="reviewed",
        coverage_repair_status="pending",
    )

    row = worklist.row(0, named=True)

    assert row["fill_status"] == "needs_coverage_repair"
    assert row["allowed_next_action"] == "repair_coverage_before_fill"
    assert row["max_live_batch_size"] == 0


def test_build_worklist_can_defer_until_gate8_ready() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows().head(1),
        candidate_set="tp53_mdm2_elephant",
        lane_name="TP53/MDM2 elephant",
        source_provenance_status="reviewed",
        coverage_repair_status="not_needed",
        gate_dependency="gate8_long_lived_vs_short_lived_contrast",
        gate8_ready=False,
    )

    row = worklist.row(0, named=True)

    assert row["fill_status"] == "defer_until_gate8_ready"
    assert row["gate_dependency"] == "gate8_long_lived_vs_short_lived_contrast"
    assert row["allowed_next_action"] == "defer_until_gate8_ready"
    assert row["max_live_batch_size"] == 0


def test_builder_never_promotes_rows_to_live_fill_by_default() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows(),
        candidate_set="sirt6_dna_repair",
        lane_name="SIRT6/core3",
        source_provenance_status="reviewed",
        coverage_repair_status="not_needed",
    )

    assert "reviewed_for_single_live_fill" not in worklist["fill_status"].to_list()
    assert worklist["max_live_batch_size"].max() == 0


def test_classify_fill_row_locks_single_row_logic() -> None:
    status, reason = classify_fill_row(
        sequence_length_status="matches",
        embedding_exists=False,
        embedding_status="missing",
        source_provenance_status="reviewed",
        coverage_repair_status="not_needed",
        gate8_ready=True,
    )

    assert status == "ready_for_preflight"
    assert "dry-run preflight" in reason


def test_fill_status_counts_returns_counts_by_status() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows(),
        candidate_set="sirt6_dna_repair",
        lane_name="SIRT6/core3",
        source_provenance_status="reviewed",
        coverage_repair_status="not_needed",
    )

    counts = fill_status_counts(worklist)

    assert counts["ready_for_preflight"] == 1
    assert counts["do_not_fill"] == 1
    assert counts["needs_source_provenance_review"] == 1


def test_schema_records_planning_policy_updated_runtime_blocked_status() -> None:
    schema = schema_doc()
    rule = schema["decision_rules"]["planning_policy_updated_runtime_blocked"]

    assert "planning_policy_updated_runtime_blocked" in schema["allowed_fill_statuses"]
    assert "planning_policy_updated_runtime_blocked" in schema["status_groups"]["blocked"]
    assert (
        "planning_policy_updated_runtime_blocked" not in schema["status_groups"]["preflight_ready"]
    )
    assert (
        "planning_policy_updated_runtime_blocked"
        not in schema["status_groups"]["live_review_ready"]
    )
    assert rule["dry_run_preflight_allowed"] is False
    assert rule["dry_run_single_allowed"] is False
    assert rule["live_call_allowed"] is False
    assert rule["live_opt_in_required"] is True
    assert rule["max_live_batch_size"] == 0
    assert rule["recommended_next_action"] == "keep_blocked"


def test_planning_policy_updated_runtime_blocked_helper_behavior() -> None:
    fill_status = "planning_policy_updated_runtime_blocked"

    assert _next_action(fill_status) == "keep_blocked"
    assert _dry_run_required(fill_status) is False
    assert _max_live_batch_size(fill_status) == 0


def test_builder_does_not_infer_planning_policy_status_without_explicit_policy_context() -> None:
    worklist = build_controlled_embedding_fill_worklist(
        preflight_rows().head(1),
        candidate_set="tp53_mdm2_elephant",
        lane_name="TP53/MDM2 elephant",
        source_provenance_status="reviewed",
        coverage_repair_status="accepted_for_planning_after_review",
        gate_dependency="manual_review",
        gate8_ready=True,
    )

    row = worklist.row(0, named=True)

    assert row["fill_status"] == "ready_for_preflight"
    assert row["fill_status"] != "planning_policy_updated_runtime_blocked"
    assert row["allowed_next_action"] == "run_curated_embedding_preflight"


def test_worklist_forbidden_actions_include_planning_policy_runtime_boundaries() -> None:
    assert "sequence fetch" in FORBIDDEN_ACTIONS
    assert "Biohub call" in FORBIDDEN_ACTIONS
    assert "embedding generation" in FORBIDDEN_ACTIONS
    assert "data/output commit" in FORBIDDEN_ACTIONS
    assert "Gate 8 promotion" in FORBIDDEN_ACTIONS
    assert "Gate 9 promotion" in FORBIDDEN_ACTIONS
    assert "Boltz call" in FORBIDDEN_ACTIONS
    assert "AF3 call" in FORBIDDEN_ACTIONS
    assert "Chai call" in FORBIDDEN_ACTIONS
    assert "biological claim" in FORBIDDEN_ACTIONS
