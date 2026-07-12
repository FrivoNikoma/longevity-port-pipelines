from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from longevity_port_pipelines.stages import (
    g3sx30_first_independent_pairwise_embedding_control_result as control,
)

ROOT = Path(__file__).resolve().parents[1]
CONTROL_TABLE = ROOT / control.DEFAULT_INDEPENDENT_CONTROL_TABLE


def read_one_row(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    return rows[0]


def test_independent_control_table_has_one_valid_result_row() -> None:
    item = control.load_and_validate_independent_control(CONTROL_TABLE)
    assert item["independent_control_status"] == (
        "first_independent_pairwise_embedding_control_result_created"
    )
    assert item["control_result_created"] == "true"


def test_independent_control_records_frozen_pre_similarity_selection() -> None:
    item = control.load_and_validate_independent_control(CONTROL_TABLE)
    assert item["selection_rule_frozen_before_similarity"] == "true"
    assert item["inventory_similarity_computed"] == "false"
    assert item["inventory_embedding_file_count"] == "216"
    assert item["inventory_technical_candidate_count"] == "1"
    assert "pre_similarity_ranked_comparator" in item["control_selection_rule"]


def test_independent_control_records_exact_comparator_provenance() -> None:
    item = control.load_and_validate_independent_control(CONTROL_TABLE)
    assert item["independent_comparator_source_accession"] == "P09874"
    assert item["independent_comparator_target_accession"] == "EPQ16369.1"
    assert item["independent_comparator_species"] == "brandts_bat"
    assert item["independent_comparator_taxid"] == "109478"
    assert item["independent_comparator_shape"] == "1024x960"
    assert item["independent_comparator_dtype"] == "float32"
    assert item["independent_comparator_finite"] == "true"
    control.validate_provenance_docs(item)


def test_independent_control_records_exact_metrics() -> None:
    item = control.load_and_validate_independent_control(CONTROL_TABLE)
    assert item["baseline_mdm2_cosine_similarity"] == "0.9973314302339468"
    assert item["independent_control_cosine_similarity"] == "0.8316190559481323"
    assert item["baseline_minus_control_delta"] == "0.1657123742858144"
    assert item["baseline_greater_than_independent_control"] == "true"


def test_independent_control_keeps_forbidden_side_effects_false() -> None:
    item = control.load_and_validate_independent_control(CONTROL_TABLE)
    for field in control.FALSE_ONLY_FIELDS:
        assert item[field] == "false"


def test_independent_control_validates_source_results() -> None:
    item = control.load_and_validate_independent_control(CONTROL_TABLE)
    control.validate_source_rows(item)


def test_compute_independent_control_metrics_supports_different_lengths() -> None:
    anchor = np.ones((491, 960), dtype=np.float32)
    comparator = np.ones((1024, 960), dtype=np.float32)

    metrics = control.compute_independent_control_metrics(
        anchor,
        comparator,
        baseline_mdm2_cosine_similarity=1.0,
    )

    assert metrics.independent_control_cosine_similarity == pytest.approx(1.0)
    assert metrics.baseline_minus_control_delta == pytest.approx(0.0)
    assert metrics.baseline_greater_than_independent_control is False


def test_compute_independent_control_metrics_rejects_wrong_comparator_shape() -> None:
    anchor = np.ones((491, 960), dtype=np.float32)
    comparator = np.ones((1023, 960), dtype=np.float32)

    with pytest.raises(ValueError, match="Expected embedding shape"):
        control.compute_independent_control_metrics(
            anchor,
            comparator,
            baseline_mdm2_cosine_similarity=0.9,
        )


def test_compute_independent_control_metrics_rejects_non_finite_values() -> None:
    anchor = np.ones((491, 960), dtype=np.float32)
    comparator = np.ones((1024, 960), dtype=np.float32)
    comparator[0, 0] = np.nan

    with pytest.raises(ValueError, match="non-finite"):
        control.compute_independent_control_metrics(
            anchor,
            comparator,
            baseline_mdm2_cosine_similarity=0.9,
        )


def test_validator_rejects_biological_claim() -> None:
    item = read_one_row(CONTROL_TABLE)
    item["biological_claim_made"] = "true"

    with pytest.raises(ValueError, match="biological_claim_made"):
        control.validate_independent_control_row(item)


def test_validator_rejects_metric_drift() -> None:
    item = read_one_row(CONTROL_TABLE)
    item["independent_control_cosine_similarity"] = "0.9000000000000000"

    with pytest.raises(ValueError, match="independent_control_cosine_similarity"):
        control.validate_independent_control_row(item)


def test_validator_rejects_mdm2_comparator_path() -> None:
    item = read_one_row(CONTROL_TABLE)
    item["independent_comparator_artifact_reference"] = (
        "data/output/embeddings/esmc-300m-2024-12/mdm2_control.npy"
    )

    with pytest.raises(ValueError, match="independent_comparator_artifact_reference"):
        control.validate_independent_control_row(item)
