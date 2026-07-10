from __future__ import annotations

import csv
import math
from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summary as summary,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TABLE = ROOT / summary.DEFAULT_SOURCE_MINIMAL_OUTPUT_TABLE
SUMMARY_TABLE = ROOT / summary.DEFAULT_SUMMARY_TABLE


def read_one_row(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    return rows[0]


def test_summary_table_has_one_valid_row() -> None:
    row = summary.load_and_validate_summary(SUMMARY_TABLE)

    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["summary_status"] == ("first_analysis_adjacent_controlled_embedding_summary_created")
    assert row["summary_type"] == "one_row_embedding_scalar_summary_statistics"


def test_summary_consumes_exact_minimal_output_row() -> None:
    row = summary.load_and_validate_summary(SUMMARY_TABLE)

    assert row["source_minimal_output_table"] == (
        "data/input/g3sx30_one_row_first_minimal_controlled_downstream_outputs.csv"
    )
    assert row["source_minimal_output_row_index"] == "1"
    assert row["source_output_status"] == ("first_minimal_controlled_downstream_output_created")
    assert row["source_output_type"] == ("one_row_artifact_identity_and_embedding_health_summary")


def test_summary_records_expected_dimensions_and_finite_values() -> None:
    row = summary.load_and_validate_summary(SUMMARY_TABLE)

    assert row["token_count"] == "492"
    assert row["embedding_dim"] == "960"
    assert row["total_values"] == "472320"
    assert row["finite_value_count"] == "472320"
    assert row["finite_fraction"] == "1.0000000000"


def test_summary_scalar_statistics_are_finite() -> None:
    row = summary.load_and_validate_summary(SUMMARY_TABLE)

    for field in summary.REQUIRED_SCALAR_FIELDS:
        assert math.isfinite(float(row[field]))

    assert float(row["embedding_value_std"]) >= 0.0
    assert float(row["embedding_value_l2_norm"]) > 0.0
    assert float(row["token_l2_norm_mean"]) > 0.0
    assert float(row["token_l2_norm_std"]) >= 0.0


def test_summary_keeps_forbidden_side_effects_false() -> None:
    row = summary.load_and_validate_summary(SUMMARY_TABLE)

    for field in [
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
        "data_output_artifact_committed",
        "biohub_esmc_called_by_summary",
        "live_embedding_rerun_by_summary",
        "embedding_generation_performed_by_summary",
        "npy_artifact_created_by_summary",
        "raw_embedding_values_committed",
        "boltz_called",
        "af3_called",
        "chai_called",
        "enrichment_rerun",
        "contrast_rerun",
    ]:
        assert row[field] == "false"


def test_summary_points_directly_to_comparator_or_pairwise_result() -> None:
    row = summary.load_and_validate_summary(SUMMARY_TABLE)

    assert row["next_step"] == ("add_first_controlled_comparator_or_pairwise_embedding_summary")
    assert row["next_pr_should_add_controlled_comparator_or_pairwise_embedding_summary"] == "true"
    assert row["no_additional_scalar_summary_approval_before_comparator"] == "true"
    assert row["no_additional_non_result_layer_before_next_concrete_step"] == "true"


def test_validator_rejects_biological_claim_promotion() -> None:
    row = read_one_row(SUMMARY_TABLE)
    row["biological_claim_made"] = "true"

    with pytest.raises(ValueError, match="biological_claim_made"):
        summary.validate_summary_row(row)


def test_validator_rejects_scalar_summary_approval_loop() -> None:
    row = read_one_row(SUMMARY_TABLE)
    row["no_additional_scalar_summary_approval_before_comparator"] = "false"

    with pytest.raises(
        ValueError,
        match="no_additional_scalar_summary_approval_before_comparator",
    ):
        summary.validate_summary_row(row)


def test_source_table_still_contains_one_row() -> None:
    source = read_one_row(SOURCE_TABLE)

    assert source["output_status"] == ("first_minimal_controlled_downstream_output_created")
    assert source["source_ready_artifact_reference"] == (summary.EXPECTED_READY_ARTIFACT_REFERENCE)
