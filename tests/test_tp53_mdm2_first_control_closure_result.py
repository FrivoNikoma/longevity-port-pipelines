from __future__ import annotations

import ast
import csv
from pathlib import Path

import pytest
import yaml

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_control_closure_result as closure,
)

RESULT_PATH = Path("data/input/tp53_mdm2_first_control_closure_results.csv")
SCHEMA_PATH = Path("data/config/tp53_mdm2_first_control_closure_result_schema.yaml")
SOURCE_PATH = Path("src/longevity_port_pipelines/stages/tp53_mdm2_first_control_closure_result.py")


def test_control_closure_schema_and_row_contract() -> None:
    with RESULT_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    row = closure.load_and_validate_control_closure_result()
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert row == rows[0]
    assert list(row) == schema["required_fields"]
    assert schema["allowed_control_closure_statuses"] == [
        "closed_with_curated_negatome_interface_control_blocked"
    ]


def test_control_closure_aggregates_four_committed_results() -> None:
    row = closure.load_and_validate_control_closure_result()

    assert row["source_manifest_status"] == (
        "first_tp53_mdm2_interface_ready_manifest_result_created"
    )
    assert row["source_extraction_status"] == (
        "first_tp53_mdm2_human_reference_interface_residue_extraction_result_created"
    )
    assert row["source_shuffled_control_status"] == (
        "first_tp53_mdm2_mdm2_side_shuffled_interface_control_result_created"
    )
    assert row["source_curated_negatome_status"] == (
        "curated_negatome_record_reviewed_no_computable_interface_control"
    )
    assert row["interface_ready_manifest_created"] == "true"
    assert row["human_reference_interface_residues_extracted"] == "true"
    assert row["mdm2_shuffled_interface_control_computed"] == "true"
    assert row["curated_negative_record_found"] == "true"
    assert row["curated_negative_provenance_reviewed"] == "true"


def test_control_closure_preserves_numerical_shuffled_summary() -> None:
    row = closure.load_and_validate_control_closure_result()

    assert row["shuffled_control_n_permutations"] == "1000"
    assert row["true_adjacent_pair_count"] == "38"
    assert row["shuffled_adjacent_pair_count_mean"] == "25.4239999999999995"
    assert row["adjacent_pair_empirical_upper_p_add_one"] == "0.0009990009990010"
    assert row["true_contiguous_run_count"] == "9"
    assert row["shuffled_contiguous_run_count_mean"] == "21.5760000000000005"
    assert row["contiguous_run_empirical_lower_p_add_one"] == "0.0009990009990010"
    assert row["true_longest_run_length"] == "16"
    assert row["shuffled_longest_run_length_mean"] == "6.6260000000000003"
    assert row["longest_run_empirical_upper_p_add_one"] == "0.0019980019980020"


def test_control_closure_records_information_blocker_without_gate_promotion() -> None:
    row = closure.load_and_validate_control_closure_result()

    assert row["control_closure_status"] == (
        "closed_with_curated_negatome_interface_control_blocked"
    )
    assert row["control_package_aggregation_complete"] == "true"
    assert row["control_package_closed_with_blocker"] == "true"
    assert row["curated_negatome_blocker_information_not_technical"] == "true"
    assert row["control_blocker_class"] == "information_missing_not_runtime_failure"
    assert row["gate6_control_readiness_status"] == "blocked"
    assert row["gate6_control_readiness_resolved"] == "false"
    assert row["gate6_control_closure_blocked"] == "true"
    assert row["gate7_entry_allowed"] == "false"
    assert row["gate7_strict_panel_promoted"] == "false"
    assert row["gate8_entry_allowed"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"
    assert row["biological_approval_granted"] == "false"


def test_control_closure_keeps_runtime_and_claim_boundaries_false() -> None:
    row = closure.load_and_validate_control_closure_result()

    for field in (
        "mdm2_side_negative_residue_mask_available",
        "deterministic_no_embedding_mdm2_context_available",
        "curated_negatome_interface_control_metric_computed",
        "curated_negatome_control_computed",
        "curated_negatome_control_closed",
        "prohibited_surrogate_metrics_used",
        "existing_runtime_negatome_path_reused",
        "new_embeddings_generated",
        "embedding_control_ratio_computed",
        "biohub_esmc_called",
        "npy_artifact_read",
        "npy_artifact_written",
        "data_output_artifact_committed",
        "boltz_called",
        "af3_called",
        "chai_called",
        "comparative_elephant_interface_scoring_performed",
        "binding_claim_made",
        "non_binding_claim_made",
        "binding_strength_claim_made",
        "functional_significance_claim_made",
        "biological_specificity_claim_made",
        "adaptation_claim_made",
        "elephant_compatibility_claim_made",
        "beneficial_breakage_claim_made",
        "longevity_evidence_claim_made",
        "biological_claim_made",
    ):
        assert row[field] == "false"


def test_control_closure_evidence_digest_recomputes() -> None:
    row = closure.load_and_validate_control_closure_result()

    assert row["closure_evidence_canonical"] == closure.canonical_closure_evidence()
    assert row["closure_evidence_sha256"] == (
        "57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7"
    )
    assert closure.closure_evidence_sha256() == row["closure_evidence_sha256"]


def test_control_closure_rejects_gate7_entry_mutation() -> None:
    row = dict(closure.load_and_validate_control_closure_result())
    row["gate7_entry_allowed"] = "true"

    with pytest.raises(ValueError, match="gate7_entry_allowed"):
        closure.validate_result_row(row)


def test_control_closure_source_has_no_forbidden_runtime_imports() -> None:
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

    for forbidden in (
        "biohub",
        "torch",
        "numpy",
        "negatome_controls",
        "embed",
        "boltz",
        "chai",
    ):
        assert all(forbidden not in imported.lower() for imported in imports)
