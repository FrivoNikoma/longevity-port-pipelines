from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages.controlled_embedding_fill_worklist import (
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


def schema_required_fields() -> list[str]:
    schema_text = Path("data/config/controlled_embedding_fill_worklist_schema.yaml").read_text(
        encoding="utf-8"
    )
    schema = yaml.safe_load(schema_text)
    return list(schema["required_output_fields"])


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
    assert "Biohub call" in row["forbidden_actions"]
    assert "Boltz call" in row["forbidden_actions"]
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
