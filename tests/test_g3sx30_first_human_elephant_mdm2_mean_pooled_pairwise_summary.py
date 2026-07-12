from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from longevity_port_pipelines.stages import (
    g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summary as summary,
)

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_TABLE = ROOT / summary.DEFAULT_PAIRWISE_SUMMARY_TABLE


def read_one_row(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    return rows[0]


def test_pairwise_summary_table_has_one_valid_result_row() -> None:
    item = summary.load_and_validate_pairwise_summary(SUMMARY_TABLE)
    assert item["pairwise_summary_status"] == (
        "first_human_elephant_mdm2_mean_pooled_embedding_summary_created"
    )
    assert item["pairwise_summary_created"] == "true"


def test_pairwise_summary_records_exact_human_runtime_scope() -> None:
    item = summary.load_and_validate_pairwise_summary(SUMMARY_TABLE)
    assert item["human_accession"] == "Q00987"
    assert item["human_taxid"] == "9606"
    assert item["human_sequence_length"] == "491"
    assert item["human_sequence_sha256"] == (
        "77ed25650e717b3f610e42ef8e5c1c88d50e7485725032f8535448a0ca8b61b1"
    )
    assert item["human_runtime_input_csv_sha256"] == (
        "d86bf792c538a066d6085e69d3d0f0a1744e7dc5de2a7f179c3198d2e828b8fd"
    )
    assert item["biohub_esmc_live_execution_count"] == "1"
    assert item["live_scope_accession_count"] == "1"
    assert item["batch_run_performed"] == "false"


def test_pairwise_summary_records_both_embedding_health_results() -> None:
    item = summary.load_and_validate_pairwise_summary(SUMMARY_TABLE)
    assert item["human_embedding_generated"] == "true"
    assert item["human_embedding_shape"] == "491x960"
    assert item["human_embedding_dtype"] == "float32"
    assert item["human_embedding_finite"] == "true"
    assert item["elephant_embedding_reused"] == "true"
    assert item["elephant_embedding_shape"] == "492x960"
    assert item["elephant_embedding_dtype"] == "float32"
    assert item["elephant_embedding_finite"] == "true"


def test_pairwise_summary_records_exact_mean_pooled_metrics() -> None:
    item = summary.load_and_validate_pairwise_summary(SUMMARY_TABLE)
    assert item["human_mean_vector_l2_norm"] == "0.8317611517806080"
    assert item["elephant_mean_vector_l2_norm"] == "0.8347860929210978"
    assert item["mean_pooled_cosine_similarity"] == "0.9973314302339468"
    assert item["mean_pooled_cosine_distance"] == "0.0026685697660532"
    assert item["mean_pooled_euclidean_distance"] == "0.0609504211067301"


def test_pairwise_summary_closes_prior_blocker_without_mutating_source() -> None:
    item = summary.load_and_validate_pairwise_summary(SUMMARY_TABLE)
    assert item["source_comparator_blocker"] == ("source_backed_human_mdm2_embedding_not_available")
    assert item["pairwise_blocker"] == "none_first_pairwise_summary_created"
    summary.validate_source_comparator(item)


def test_pairwise_summary_keeps_forbidden_side_effects_false() -> None:
    item = summary.load_and_validate_pairwise_summary(SUMMARY_TABLE)
    for field in summary.FALSE_ONLY_FIELDS:
        assert item[field] == "false"


def test_compute_mean_pooled_metrics_supports_different_sequence_lengths() -> None:
    human_vector = np.ones((1, 960), dtype=np.float32)
    elephant_vector = np.ones((1, 960), dtype=np.float32)
    human = np.broadcast_to(human_vector, (491, 960))
    elephant = np.broadcast_to(elephant_vector, (492, 960))

    metrics = summary.compute_mean_pooled_metrics(human, elephant)

    assert metrics.mean_pooled_cosine_similarity == pytest.approx(1.0)
    assert metrics.mean_pooled_cosine_distance == pytest.approx(0.0)
    assert metrics.mean_pooled_euclidean_distance == pytest.approx(0.0)


def test_compute_mean_pooled_metrics_rejects_wrong_human_shape() -> None:
    human = np.ones((490, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)

    with pytest.raises(ValueError, match="Expected embedding shape"):
        summary.compute_mean_pooled_metrics(human, elephant)


def test_compute_mean_pooled_metrics_rejects_non_finite_values() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)
    human[0, 0] = np.nan

    with pytest.raises(ValueError, match="non-finite"):
        summary.compute_mean_pooled_metrics(human, elephant)


def test_validator_rejects_biological_claim() -> None:
    item = read_one_row(SUMMARY_TABLE)
    item["biological_claim_made"] = "true"

    with pytest.raises(ValueError, match="biological_claim_made"):
        summary.validate_pairwise_summary_row(item)


def test_validator_rejects_metric_drift() -> None:
    item = read_one_row(SUMMARY_TABLE)
    item["mean_pooled_cosine_similarity"] = "0.9000000000000000"

    with pytest.raises(ValueError, match="mean_pooled_cosine_similarity"):
        summary.validate_pairwise_summary_row(item)
