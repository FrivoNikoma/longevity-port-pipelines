from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from longevity_port_pipelines.stages import (
    g3sx30_first_controlled_human_elephant_mdm2_pairwise_embedding_robustness_check as robustness,
)

ROOT = Path(__file__).resolve().parents[1]
RESULT_TABLE = ROOT / robustness.DEFAULT_ROBUSTNESS_CHECK_TABLE


def read_one_row(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    return rows[0]


def test_robustness_table_has_one_valid_result_row() -> None:
    item = robustness.load_and_validate_robustness_check(RESULT_TABLE)
    assert item["robustness_check_status"] == (
        "first_controlled_pairwise_embedding_robustness_check_created"
    )
    assert item["control_result_created"] == "true"


def test_robustness_result_records_exact_control_design() -> None:
    item = robustness.load_and_validate_robustness_check(RESULT_TABLE)
    assert item["robustness_check_type"] == ("deterministic_residue_block_jackknife_mean_pooling")
    assert item["block_count"] == "10"
    assert item["block_count_per_species"] == "10"
    assert item["control_comparison_count"] == "20"
    assert item["human_block_deletion_control_count"] == "10"
    assert item["elephant_block_deletion_control_count"] == "10"
    assert item["deletion_design"] == "one_species_one_block_deleted_at_a_time"
    assert item["paired_cross_species_block_deletion_performed"] == "false"
    assert item["residue_alignment_performed"] == "false"


def test_robustness_result_records_exact_metrics() -> None:
    item = robustness.load_and_validate_robustness_check(RESULT_TABLE)
    assert item["baseline_cosine_similarity"] == "0.9973314302339468"
    assert item["min_control_cosine_similarity"] == "0.9896092392687877"
    assert item["max_control_cosine_similarity"] == "0.9974979683829747"
    assert item["mean_control_cosine_similarity"] == "0.9949019040387004"
    assert item["std_control_cosine_similarity"] == "0.0023610146368762"
    assert item["max_abs_delta_from_baseline"] == "0.0077221909651590"
    assert item["baseline_within_control_range"] == "true"


def test_robustness_result_validates_source_pairwise_summary() -> None:
    item = robustness.load_and_validate_robustness_check(RESULT_TABLE)
    robustness.validate_source_pairwise_summary(item)
    assert item["source_pairwise_summary_status"] == (
        "first_human_elephant_mdm2_mean_pooled_embedding_summary_created"
    )


def test_robustness_result_keeps_forbidden_side_effects_false() -> None:
    item = robustness.load_and_validate_robustness_check(RESULT_TABLE)
    for field in robustness.FALSE_ONLY_FIELDS:
        assert item[field] == "false"


def test_contiguous_blocks_cover_human_and_elephant_lengths() -> None:
    human_blocks = robustness.contiguous_blocks(491, 10)
    elephant_blocks = robustness.contiguous_blocks(492, 10)

    assert [block.size for block in human_blocks] == [50] + [49] * 9
    assert [block.size for block in elephant_blocks] == [50, 50] + [49] * 8
    assert sum(block.size for block in human_blocks) == 491
    assert sum(block.size for block in elephant_blocks) == 492


def test_block_jackknife_creates_twenty_controls_without_alignment() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)

    baseline, values = robustness.compute_block_jackknife_control_values(
        human,
        elephant,
        block_count=10,
    )
    summary = robustness.summarize_control_values(baseline, values)

    assert baseline == pytest.approx(1.0)
    assert len(values) == 20
    assert all(value == pytest.approx(1.0) for value in values)
    assert summary.min_control_cosine_similarity == pytest.approx(1.0)
    assert summary.max_control_cosine_similarity == pytest.approx(1.0)
    assert summary.max_abs_delta_from_baseline == pytest.approx(0.0)
    assert summary.baseline_within_control_range is True


def test_block_jackknife_rejects_wrong_original_shape() -> None:
    human = np.ones((490, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)

    with pytest.raises(ValueError, match="row count"):
        robustness.compute_block_jackknife_control_values(human, elephant)


def test_block_jackknife_rejects_non_finite_values() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)
    elephant[0, 0] = np.nan

    with pytest.raises(ValueError, match="non-finite"):
        robustness.compute_block_jackknife_control_values(human, elephant)


def test_validator_rejects_biological_claim() -> None:
    item = read_one_row(RESULT_TABLE)
    item["biological_claim_made"] = "true"

    with pytest.raises(ValueError, match="biological_claim_made"):
        robustness.validate_robustness_check_row(item)


def test_validator_rejects_metric_drift() -> None:
    item = read_one_row(RESULT_TABLE)
    item["min_control_cosine_similarity"] = "0.9000000000000000"

    with pytest.raises(ValueError, match="min_control_cosine_similarity"):
        robustness.validate_robustness_check_row(item)
