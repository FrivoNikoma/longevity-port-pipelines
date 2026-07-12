"""Validate and reproduce the first controlled pairwise robustness result.

The committed row is a numerical embedding-space control only. Each species
is partitioned independently into contiguous residue-axis blocks. One block
from only one species is deleted at a time before independent mean pooling.
This does not perform residue alignment and does not support a biological
interpretation.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from longevity_port_pipelines.stages import (
    g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summary as pairwise,
)

DEFAULT_SOURCE_PAIRWISE_SUMMARY_TABLE = Path(
    "data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv"
)
DEFAULT_ROBUSTNESS_CHECK_TABLE = Path(
    "data/input/"
    "g3sx30_first_controlled_human_elephant_mdm2_pairwise_embedding_robustness_checks.csv"
)

EXPECTED_HUMAN_EMBEDDING_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9606.npy"
)
EXPECTED_ELEPHANT_EMBEDDING_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "source_pairwise_summary_table": "data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv",
    "source_pairwise_summary_row_index": "1",
    "source_pairwise_summary_status": "first_human_elephant_mdm2_mean_pooled_embedding_summary_created",
    "source_pairwise_summary_type": "human_elephant_mdm2_mean_pooled_embedding_space_comparison",
    "source_pairwise_summary_scope": "numerical_embedding_space_comparison_only_no_biological_claim",
    "baseline_cosine_similarity": "0.9973314302339468",
    "baseline_recomputed_matches_committed": "true",
    "robustness_check_status": "first_controlled_pairwise_embedding_robustness_check_created",
    "robustness_check_type": "deterministic_residue_block_jackknife_mean_pooling",
    "robustness_check_scope": "numerical_embedding_space_control_only_no_biological_claim",
    "control_result_created": "true",
    "block_count": "10",
    "block_count_per_species": "10",
    "control_comparison_count": "20",
    "human_block_deletion_control_count": "10",
    "elephant_block_deletion_control_count": "10",
    "block_partition_method": "independent_contiguous_numpy_array_split_over_residue_axis",
    "deletion_design": "one_species_one_block_deleted_at_a_time",
    "paired_cross_species_block_deletion_performed": "false",
    "residue_alignment_performed": "false",
    "mean_pooling_used": "true",
    "metric_calculation_dtype": "float64",
    "metric_decimal_places": "16",
    "min_control_cosine_similarity": "0.9896092392687877",
    "max_control_cosine_similarity": "0.9974979683829747",
    "mean_control_cosine_similarity": "0.9949019040387004",
    "std_control_cosine_similarity": "0.0023610146368762",
    "max_abs_delta_from_baseline": "0.0077221909651590",
    "baseline_within_control_range": "true",
    "human_embedding_artifact_reference": "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9606.npy",
    "human_embedding_shape": "491x960",
    "human_embedding_dtype": "float32",
    "human_embedding_finite": "true",
    "human_embedding_artifact_committed": "false",
    "elephant_embedding_artifact_reference": "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
    "elephant_embedding_shape": "492x960",
    "elephant_embedding_dtype": "float32",
    "elephant_embedding_finite": "true",
    "elephant_embedding_artifact_committed": "false",
    "external_robustness_result_sha256": "1ca19556000320bf4cb1842c5cd3723f7c2c107d889c496a3826ae59bc335399",
    "biohub_esmc_called": "false",
    "new_embedding_generated": "false",
    "npy_artifact_committed": "false",
    "raw_embedding_vectors_committed": "false",
    "data_output_artifact_committed": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "enrichment_rerun": "false",
    "contrast_rerun": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "next_step": "add_first_independent_pairwise_embedding_control_result_before_interpretation",
    "no_biological_interpretation_from_single_control": "true",
    "no_additional_control_plan_only_layer": "true",
    "no_additional_non_result_layer_before_next_concrete_step": "true",
    "result_date": "2026-07-12",
    "claim_note": "Numerical embedding-space control only; not residue alignment; not interface "
    "analysis; not binding result; not orthology proof; not functional-equivalence "
    "evidence; not longevity evidence.",
}

FALSE_ONLY_FIELDS = (
    "paired_cross_species_block_deletion_performed",
    "residue_alignment_performed",
    "human_embedding_artifact_committed",
    "elephant_embedding_artifact_committed",
    "biohub_esmc_called",
    "new_embedding_generated",
    "npy_artifact_committed",
    "raw_embedding_vectors_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "enrichment_rerun",
    "contrast_rerun",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
)

METRIC_FIELDS = (
    "baseline_cosine_similarity",
    "min_control_cosine_similarity",
    "max_control_cosine_similarity",
    "mean_control_cosine_similarity",
    "std_control_cosine_similarity",
    "max_abs_delta_from_baseline",
)


@dataclass(frozen=True)
class BlockJackknifeSummary:
    baseline_cosine_similarity: float
    min_control_cosine_similarity: float
    max_control_cosine_similarity: float
    mean_control_cosine_similarity: float
    std_control_cosine_similarity: float
    max_abs_delta_from_baseline: float
    baseline_within_control_range: bool
    control_values: tuple[float, ...]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def _validate_embedding(
    array: np.ndarray,
    *,
    expected_rows: int | None = None,
    expected_columns: int = 960,
) -> None:
    if array.ndim != 2:
        raise ValueError(f"Expected a 2D embedding matrix, got {array.shape}")
    if expected_rows is not None and array.shape[0] != expected_rows:
        raise ValueError(f"Expected embedding row count {expected_rows}, got {array.shape[0]}")
    if array.shape[1] != expected_columns:
        raise ValueError(f"Expected embedding dimension {expected_columns}, got {array.shape[1]}")
    if array.dtype != np.float32:
        raise ValueError(f"Expected embedding dtype float32, got {array.dtype}")
    if not np.isfinite(array).all():
        raise ValueError("Embedding contains non-finite values")


def cosine_similarity_from_mean_pools(
    human: np.ndarray,
    elephant: np.ndarray,
) -> float:
    _validate_embedding(human)
    _validate_embedding(elephant)

    human_mean = human.mean(axis=0, dtype=np.float64)
    elephant_mean = elephant.mean(axis=0, dtype=np.float64)
    human_norm = float(np.linalg.norm(human_mean))
    elephant_norm = float(np.linalg.norm(elephant_mean))
    if human_norm <= 0.0 or elephant_norm <= 0.0:
        raise ValueError("Mean-pooled embedding vectors must have positive norm")

    value = float(np.dot(human_mean, elephant_mean) / (human_norm * elephant_norm))
    if not math.isfinite(value):
        raise ValueError("Cosine similarity must be finite")
    if not -1.0 <= value <= 1.0:
        raise ValueError("Cosine similarity must be in [-1, 1]")
    return value


def contiguous_blocks(length: int, block_count: int) -> tuple[np.ndarray, ...]:
    if block_count < 2:
        raise ValueError("block_count must be at least 2")
    if block_count >= length:
        raise ValueError("block_count must be smaller than sequence length")

    blocks = tuple(
        block.astype(np.int64, copy=False)
        for block in np.array_split(
            np.arange(length, dtype=np.int64),
            block_count,
        )
    )
    if any(block.size == 0 for block in blocks):
        raise ValueError("All blocks must contain at least one residue")
    if sum(block.size for block in blocks) != length:
        raise ValueError("Blocks must cover the complete residue axis")
    return blocks


def _delete_block(array: np.ndarray, block: np.ndarray) -> np.ndarray:
    keep = np.ones(array.shape[0], dtype=bool)
    keep[block] = False
    reduced = array[keep]
    if reduced.shape[0] != array.shape[0] - block.size:
        raise ValueError("Unexpected reduced embedding length")
    return reduced


def compute_block_jackknife_control_values(
    human: np.ndarray,
    elephant: np.ndarray,
    *,
    block_count: int = 10,
) -> tuple[float, tuple[float, ...]]:
    _validate_embedding(human, expected_rows=491)
    _validate_embedding(elephant, expected_rows=492)

    baseline = cosine_similarity_from_mean_pools(human, elephant)
    values: list[float] = []

    for block in contiguous_blocks(human.shape[0], block_count):
        values.append(
            cosine_similarity_from_mean_pools(
                _delete_block(human, block),
                elephant,
            )
        )

    for block in contiguous_blocks(elephant.shape[0], block_count):
        values.append(
            cosine_similarity_from_mean_pools(
                human,
                _delete_block(elephant, block),
            )
        )

    if len(values) != 2 * block_count:
        raise ValueError("Unexpected control comparison count")
    return baseline, tuple(values)


def summarize_control_values(
    baseline: float,
    control_values: tuple[float, ...],
) -> BlockJackknifeSummary:
    if not control_values:
        raise ValueError("At least one control value is required")

    values = np.asarray(control_values, dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError("Control values must all be finite")

    minimum = float(values.min())
    maximum = float(values.max())
    mean = float(values.mean())
    standard_deviation = float(values.std(ddof=0))
    max_abs_delta = float(np.max(np.abs(values - baseline)))

    return BlockJackknifeSummary(
        baseline_cosine_similarity=baseline,
        min_control_cosine_similarity=minimum,
        max_control_cosine_similarity=maximum,
        mean_control_cosine_similarity=mean,
        std_control_cosine_similarity=standard_deviation,
        max_abs_delta_from_baseline=max_abs_delta,
        baseline_within_control_range=minimum <= baseline <= maximum,
        control_values=tuple(float(value) for value in values),
    )


def reproduce_robustness_check(
    human_path: Path,
    elephant_path: Path,
    *,
    block_count: int = 10,
) -> BlockJackknifeSummary:
    human = np.load(human_path, allow_pickle=False)
    elephant = np.load(elephant_path, allow_pickle=False)
    baseline, control_values = compute_block_jackknife_control_values(
        human,
        elephant,
        block_count=block_count,
    )
    return summarize_control_values(baseline, control_values)


def format_metric(value: float) -> str:
    return f"{value:.16f}"


def validate_source_pairwise_summary(item: dict[str, str]) -> None:
    source = pairwise.load_and_validate_pairwise_summary(DEFAULT_SOURCE_PAIRWISE_SUMMARY_TABLE)
    expected = {
        "pairwise_summary_status": item["source_pairwise_summary_status"],
        "pairwise_summary_type": item["source_pairwise_summary_type"],
        "pairwise_summary_scope": item["source_pairwise_summary_scope"],
        "mean_pooled_cosine_similarity": item["baseline_cosine_similarity"],
        "human_embedding_artifact_reference": item["human_embedding_artifact_reference"],
        "elephant_embedding_artifact_reference": item["elephant_embedding_artifact_reference"],
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    for field, expected_value in expected.items():
        actual = source.get(field)
        if actual != expected_value:
            raise ValueError(
                f"Source pairwise summary expected {field}={expected_value!r}, got {actual!r}"
            )


def validate_robustness_check_row(item: dict[str, str]) -> None:
    for field, expected in EXPECTED_VALUES.items():
        actual = item.get(field)
        if actual != expected:
            raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")

    for field in FALSE_ONLY_FIELDS:
        if item[field] != "false":
            raise ValueError(f"Expected {field}='false'")

    for field in METRIC_FIELDS:
        value = float(item[field])
        if not math.isfinite(value):
            raise ValueError(f"Expected finite metric {field}, got {item[field]!r}")

    baseline = float(item["baseline_cosine_similarity"])
    minimum = float(item["min_control_cosine_similarity"])
    maximum = float(item["max_control_cosine_similarity"])
    mean = float(item["mean_control_cosine_similarity"])
    standard_deviation = float(item["std_control_cosine_similarity"])
    max_abs_delta = float(item["max_abs_delta_from_baseline"])

    if not -1.0 <= minimum <= maximum <= 1.0:
        raise ValueError("Control cosine range must be ordered inside [-1, 1]")
    if not minimum <= mean <= maximum:
        raise ValueError("Mean control cosine similarity must be inside the range")
    if standard_deviation < 0.0:
        raise ValueError("Control cosine standard deviation must be non-negative")
    if max_abs_delta < 0.0:
        raise ValueError("Maximum absolute delta must be non-negative")

    expected_max_abs_delta = max(
        abs(minimum - baseline),
        abs(maximum - baseline),
    )
    if not math.isclose(
        max_abs_delta,
        expected_max_abs_delta,
        rel_tol=0.0,
        abs_tol=2e-15,
    ):
        raise ValueError(
            "Maximum absolute delta must match the most distant control range endpoint"
        )

    within_range = minimum <= baseline <= maximum
    if item["baseline_within_control_range"] != str(within_range).lower():
        raise ValueError("baseline_within_control_range does not match metrics")

    block_count = int(item["block_count"])
    if int(item["control_comparison_count"]) != 2 * block_count:
        raise ValueError("Control comparison count must equal two times block count")
    if int(item["human_block_deletion_control_count"]) != block_count:
        raise ValueError("Human control count must equal block count")
    if int(item["elephant_block_deletion_control_count"]) != block_count:
        raise ValueError("Elephant control count must equal block count")

    claim_note = item.get("claim_note", "")
    for required in [
        "not residue alignment",
        "not interface analysis",
        "not binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
    ]:
        if required not in claim_note:
            raise ValueError(f"Missing claim boundary phrase: {required}")


def load_and_validate_robustness_check(
    path: Path = DEFAULT_ROBUSTNESS_CHECK_TABLE,
) -> dict[str, str]:
    item = require_single_row(path)
    validate_robustness_check_row(item)
    validate_source_pairwise_summary(item)
    return item
