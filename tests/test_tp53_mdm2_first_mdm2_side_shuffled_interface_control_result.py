# Tests for the first TP53/MDM2 MDM2-side shuffled control.

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_mdm2_side_shuffled_interface_control_result as result,
)

RESULT_TABLE = Path("data/input/tp53_mdm2_first_mdm2_side_shuffled_interface_control_results.csv")
SCHEMA_PATH = Path(
    "data/config/tp53_mdm2_first_mdm2_side_shuffled_interface_control_result_schema.yaml"
)


def _write_row(path: Path, row: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


def test_load_and_validate_mdm2_side_shuffled_control() -> None:
    row = result.load_and_validate_mdm2_side_shuffled_interface_control_result()

    assert row["structure_id"] == "1YCR"
    assert row["mdm2_chain_id"] == "A"
    assert row["mdm2_chain_residue_count"] == "85"
    assert row["true_interface_residue_count"] == "47"
    assert row["rng_seed"] == "42"
    assert row["n_permutations"] == "1000"
    assert row["unique_control_mask_count"] == "1000"
    assert row["control_mask_stream_sha256"] == (
        "6ebc3aea77388a9929d945acdb1962fe8eed148feecac7326fcbeceefbe2015c"
    )
    assert row["true_adjacent_pair_count"] == "38"
    assert row["true_contiguous_run_count"] == "9"
    assert row["true_longest_run_length"] == "16"
    assert row["next_step"] == ("add_first_tp53_mdm2_curated_negatome_interface_control_result")


def test_true_mask_compactness_metrics_are_exact() -> None:
    indices = [int(value) for value in result.EXPECTED_VALUES["true_interface_indices"].split("|")]
    metrics = result.compute_mask_compactness_metrics(indices)

    assert metrics.adjacent_pair_count == 38
    assert metrics.contiguous_run_count == 9
    assert metrics.longest_run_length == 16


def test_deterministic_control_recomputes_exact_metrics() -> None:
    recomputed = result.recompute_expected_values()

    for field in (
        "control_mask_stream_sha256",
        "unique_control_mask_count",
        "shuffled_adjacent_pair_count_mean",
        "shuffled_adjacent_pair_count_std_population",
        "shuffled_adjacent_pair_count_ge_true_count",
        "adjacent_pair_empirical_upper_p_add_one",
        "shuffled_contiguous_run_count_mean",
        "shuffled_contiguous_run_count_std_population",
        "shuffled_contiguous_run_count_le_true_count",
        "contiguous_run_empirical_lower_p_add_one",
        "shuffled_longest_run_length_mean",
        "shuffled_longest_run_length_std_population",
        "shuffled_longest_run_length_ge_true_count",
        "longest_run_empirical_upper_p_add_one",
    ):
        assert recomputed[field] == result.EXPECTED_VALUES[field]


def test_schema_matches_committed_result() -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    row = result.require_single_row(RESULT_TABLE)

    assert schema["name"] == ("tp53_mdm2_first_mdm2_side_shuffled_interface_control_result")
    assert schema["version"] == 1
    assert list(row) == schema["required_fields"]
    assert schema["control"]["rng_seed"] == 42
    assert schema["control"]["n_permutations"] == 1000
    assert schema["control"]["sample_size"] == 47
    assert schema["source"]["tp53"]["within_chain_shuffle_degenerate"] is True


def test_validator_rejects_changed_rng_seed(tmp_path: Path) -> None:
    row = result.require_single_row(RESULT_TABLE)
    row["rng_seed"] = "43"
    changed = tmp_path / "changed_seed.csv"
    _write_row(changed, row)

    with pytest.raises(ValueError, match="value mismatch"):
        result.load_and_validate_mdm2_side_shuffled_interface_control_result(changed)


def test_validator_rejects_changed_numerical_metric(
    tmp_path: Path,
) -> None:
    row = result.require_single_row(RESULT_TABLE)
    row["true_adjacent_pair_count"] = "37"
    changed = tmp_path / "changed_metric.csv"
    _write_row(changed, row)

    with pytest.raises(ValueError, match="value mismatch"):
        result.load_and_validate_mdm2_side_shuffled_interface_control_result(changed)


def test_control_boundaries_remain_false() -> None:
    row = result.load_and_validate_mdm2_side_shuffled_interface_control_result()

    for field in result.FALSE_ONLY_FIELDS:
        assert row[field] == "false"

    assert row["shuffled_interface_control_computed"] == "true"
    assert row["biological_claim_made"] == "false"
