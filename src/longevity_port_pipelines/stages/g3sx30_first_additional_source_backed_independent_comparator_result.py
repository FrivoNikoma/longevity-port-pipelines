"""Validate and reproduce the first additional source-backed comparator result.

This result compares human MDM2 Q00987 and elephant MDM2 G3SX30 with one
additional comparator selected by a deterministic rule frozen before any
similarity calculation. It is a numerical embedding-space result only, not a
biological negative control.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from longevity_port_pipelines.stages import (
    g3sx30_first_matched_elephant_mdm2_independent_control_result as source_control,
)

DEFAULT_SOURCE_TABLE = Path(
    "data/input/g3sx30_first_matched_elephant_mdm2_independent_control_results.csv"
)
DEFAULT_RESULT_TABLE = Path(
    "data/input/g3sx30_first_additional_source_backed_independent_comparator_results.csv"
)

EXPECTED_HUMAN_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9606.npy"
)
EXPECTED_ELEPHANT_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_COMPARATOR_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/8bot__U1_P13010--8bot__T1_P12956_receptor_9606.npy"
)

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "source_matched_control_table": (
        "data/input/g3sx30_first_matched_elephant_mdm2_independent_control_results.csv"
    ),
    "source_matched_control_row_index": "1",
    "source_matched_control_status": (
        "first_matched_elephant_mdm2_independent_control_result_created"
    ),
    "result_status": ("first_additional_source_backed_independent_comparator_result_created"),
    "result_scope": ("numerical_embedding_space_additional_comparator_only_no_biological_claim"),
    "selection_rule_sha256": ("73199752734c03778885d063556804e2c3bcdef1f55f31b6aed52e8604d1c3a4"),
    "selection_rule_frozen_before_similarity": "true",
    "similarity_used_for_selection": "false",
    "selection_and_result_in_same_step": "true",
    "inventory_file_count": "216",
    "source_backed_eligible_candidate_count": "101",
    "selected_rank": "1",
    "selected_comparator_artifact_reference": EXPECTED_COMPARATOR_REFERENCE,
    "selected_comparator_shape": "642x960",
    "selected_comparator_dtype": "float32",
    "selected_comparator_finite": "true",
    "selected_comparator_artifact_committed": "false",
    "selected_comparator_reference_tier": "2",
    "selected_comparator_reference_files": ("tests/test_analyze_saved_embeddings_mapped.py"),
    "selected_comparator_accession_tokens": "P12956|P13010",
    "selected_comparator_pdb_token": "8bot",
    "selected_comparator_taxid": "9606",
    "selected_comparator_reuses_previous_comparator": "false",
    "supplemental_provenance_file": ("docs/sirt6_mini_pilot_v2_candidate_selection.md"),
    "supplemental_provenance_context_status": "v1_selected",
    "supplemental_provenance_source_accession": "P13010",
    "supplemental_provenance_partner_accession": "P12956",
    "supplemental_provenance_intermolecular_contacts": "732",
    "supplemental_provenance_used_for_selection_ranking": "false",
    "human_mdm2_artifact_reference": EXPECTED_HUMAN_REFERENCE,
    "human_mdm2_shape": "491x960",
    "human_mdm2_dtype": "float32",
    "human_mdm2_finite": "true",
    "human_mdm2_artifact_committed": "false",
    "elephant_mdm2_artifact_reference": EXPECTED_ELEPHANT_REFERENCE,
    "elephant_mdm2_shape": "492x960",
    "elephant_mdm2_dtype": "float32",
    "elephant_mdm2_finite": "true",
    "elephant_mdm2_artifact_committed": "false",
    "model": "esmc-300m-2024-12",
    "pooling": "independent_mean_pooling_over_residue_axis",
    "metric": "cosine_similarity",
    "metric_calculation_dtype": "float64",
    "metric_decimal_places": "16",
    "baseline_human_elephant_mdm2_cosine_similarity": "0.9973314302339468",
    "previous_human_mdm2_to_comparator_cosine_similarity": ("0.8316190559481323"),
    "previous_elephant_mdm2_to_comparator_cosine_similarity": ("0.8409825967886765"),
    "human_mdm2_mean_vector_l2_norm": "0.8317611517806081",
    "elephant_mdm2_mean_vector_l2_norm": "0.8347860929210978",
    "additional_comparator_mean_vector_l2_norm": "0.9081312113564025",
    "human_mdm2_to_additional_comparator_cosine_similarity": ("0.8095126148075514"),
    "elephant_mdm2_to_additional_comparator_cosine_similarity": ("0.8203721870665286"),
    "baseline_minus_human_additional_control_delta": "0.1878188154263953",
    "baseline_minus_elephant_additional_control_delta": "0.1769592431674182",
    "baseline_greater_than_human_additional_control": "true",
    "baseline_greater_than_elephant_additional_control": "true",
    "human_additional_control_minus_elephant_additional_control_delta": ("-0.0108595722589772"),
    "absolute_human_elephant_additional_control_difference": ("0.0108595722589772"),
    "external_additional_comparator_result_sha256": (
        "0180102edc74a4cee7f82a54d337bc30079e8d9f414bfb78589620a056d62a6b"
    ),
    "result_created": "true",
    "residue_alignment_performed": "false",
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
    "next_step": (
        "add_first_two_comparator_pairwise_embedding_control_summary_before_interpretation"
    ),
    "no_biological_interpretation_from_two_comparators": "true",
    "no_inventory_only_layer_before_next_result": "true",
    "no_control_plan_only_layer_before_next_result": "true",
    "no_additional_non_result_layer_before_next_concrete_step": "true",
    "result_date": "2026-07-12",
    "claim_note": (
        "Numerical embedding-space additional comparator only; not a validated "
        "biological negative control; not residue alignment; not interface "
        "analysis; not a binding result; not orthology proof; not "
        "functional-equivalence evidence; not longevity evidence."
    ),
}

FALSE_ONLY_FIELDS = (
    "similarity_used_for_selection",
    "selected_comparator_artifact_committed",
    "selected_comparator_reuses_previous_comparator",
    "supplemental_provenance_used_for_selection_ranking",
    "human_mdm2_artifact_committed",
    "elephant_mdm2_artifact_committed",
    "residue_alignment_performed",
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

COMPARISON_ABS_TOL = 5e-16


@dataclass(frozen=True)
class AdditionalComparatorMetrics:
    human_mdm2_mean_vector_l2_norm: float
    elephant_mdm2_mean_vector_l2_norm: float
    additional_comparator_mean_vector_l2_norm: float
    human_mdm2_to_additional_comparator_cosine_similarity: float
    elephant_mdm2_to_additional_comparator_cosine_similarity: float
    baseline_minus_human_additional_control_delta: float
    baseline_minus_elephant_additional_control_delta: float
    baseline_greater_than_human_additional_control: bool
    baseline_greater_than_elephant_additional_control: bool
    human_additional_control_minus_elephant_additional_control_delta: float
    absolute_human_elephant_additional_control_difference: float


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
    expected_rows: int,
    expected_columns: int = 960,
) -> None:
    if array.ndim != 2:
        raise ValueError(f"Expected a 2D embedding matrix, got {array.shape}")
    if array.shape != (expected_rows, expected_columns):
        raise ValueError(
            f"Expected embedding shape {(expected_rows, expected_columns)}, got {array.shape}"
        )
    if array.dtype != np.float32:
        raise ValueError(f"Expected embedding dtype float32, got {array.dtype}")
    if not np.isfinite(array).all():
        raise ValueError("Embedding contains non-finite values")


def _mean_and_norm(array: np.ndarray) -> tuple[np.ndarray, float]:
    vector = array.mean(axis=0, dtype=np.float64)
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("Mean-pooled embedding vector must have positive norm")
    return vector, norm


def _cosine(
    first: np.ndarray,
    first_norm: float,
    second: np.ndarray,
    second_norm: float,
) -> float:
    value = float(np.dot(first, second) / (first_norm * second_norm))
    if not math.isfinite(value) or not -1.0 <= value <= 1.0:
        raise ValueError("Cosine similarity must be finite and in [-1, 1]")
    return value


def compute_additional_comparator_metrics(
    human_mdm2: np.ndarray,
    elephant_mdm2: np.ndarray,
    additional_comparator: np.ndarray,
    *,
    baseline_human_elephant_mdm2_cosine_similarity: float,
) -> AdditionalComparatorMetrics:
    _validate_embedding(human_mdm2, expected_rows=491)
    _validate_embedding(elephant_mdm2, expected_rows=492)
    _validate_embedding(additional_comparator, expected_rows=642)

    human_mean, human_norm = _mean_and_norm(human_mdm2)
    elephant_mean, elephant_norm = _mean_and_norm(elephant_mdm2)
    comparator_mean, comparator_norm = _mean_and_norm(additional_comparator)

    human_similarity = _cosine(
        human_mean,
        human_norm,
        comparator_mean,
        comparator_norm,
    )
    elephant_similarity = _cosine(
        elephant_mean,
        elephant_norm,
        comparator_mean,
        comparator_norm,
    )

    baseline_minus_human = baseline_human_elephant_mdm2_cosine_similarity - human_similarity
    baseline_minus_elephant = baseline_human_elephant_mdm2_cosine_similarity - elephant_similarity
    human_minus_elephant = human_similarity - elephant_similarity
    absolute_difference = abs(human_minus_elephant)

    values = (
        baseline_human_elephant_mdm2_cosine_similarity,
        human_norm,
        elephant_norm,
        comparator_norm,
        human_similarity,
        elephant_similarity,
        baseline_minus_human,
        baseline_minus_elephant,
        human_minus_elephant,
        absolute_difference,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Additional comparator metrics must all be finite")

    return AdditionalComparatorMetrics(
        human_mdm2_mean_vector_l2_norm=human_norm,
        elephant_mdm2_mean_vector_l2_norm=elephant_norm,
        additional_comparator_mean_vector_l2_norm=comparator_norm,
        human_mdm2_to_additional_comparator_cosine_similarity=human_similarity,
        elephant_mdm2_to_additional_comparator_cosine_similarity=(elephant_similarity),
        baseline_minus_human_additional_control_delta=baseline_minus_human,
        baseline_minus_elephant_additional_control_delta=baseline_minus_elephant,
        baseline_greater_than_human_additional_control=(baseline_minus_human > COMPARISON_ABS_TOL),
        baseline_greater_than_elephant_additional_control=(
            baseline_minus_elephant > COMPARISON_ABS_TOL
        ),
        human_additional_control_minus_elephant_additional_control_delta=(human_minus_elephant),
        absolute_human_elephant_additional_control_difference=(absolute_difference),
    )


def reproduce_additional_comparator(
    human_mdm2_path: Path,
    elephant_mdm2_path: Path,
    additional_comparator_path: Path,
    *,
    baseline_human_elephant_mdm2_cosine_similarity: float,
) -> AdditionalComparatorMetrics:
    human = np.load(human_mdm2_path, allow_pickle=False)
    elephant = np.load(elephant_mdm2_path, allow_pickle=False)
    comparator = np.load(additional_comparator_path, allow_pickle=False)
    return compute_additional_comparator_metrics(
        human,
        elephant,
        comparator,
        baseline_human_elephant_mdm2_cosine_similarity=(
            baseline_human_elephant_mdm2_cosine_similarity
        ),
    )


def validate_source_matched_control(item: dict[str, str]) -> None:
    source = source_control.load_and_validate_matched_control(DEFAULT_SOURCE_TABLE)
    expected = {
        "matched_control_status": item["source_matched_control_status"],
        "baseline_human_elephant_mdm2_cosine_similarity": (
            item["baseline_human_elephant_mdm2_cosine_similarity"]
        ),
        "human_mdm2_to_frozen_comparator_cosine_similarity": (
            item["previous_human_mdm2_to_comparator_cosine_similarity"]
        ),
        "elephant_mdm2_to_frozen_comparator_cosine_similarity": (
            item["previous_elephant_mdm2_to_comparator_cosine_similarity"]
        ),
        "next_step": (
            "add_first_additional_source_backed_independent_comparator_result_"
            "with_selection_frozen_in_same_step"
        ),
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    for field, required in expected.items():
        actual = source.get(field)
        if actual != required:
            raise ValueError(
                f"Source matched control expected {field}={required!r}, got {actual!r}"
            )


def validate_additional_comparator_row(item: dict[str, str]) -> None:
    for field, expected in EXPECTED_VALUES.items():
        actual = item.get(field)
        if actual != expected:
            raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")

    for field in FALSE_ONLY_FIELDS:
        if item.get(field) != "false":
            raise ValueError(f"Expected {field}=false")

    for field in (
        "selection_rule_frozen_before_similarity",
        "selection_and_result_in_same_step",
        "selected_comparator_finite",
        "human_mdm2_finite",
        "elephant_mdm2_finite",
        "baseline_greater_than_human_additional_control",
        "baseline_greater_than_elephant_additional_control",
        "result_created",
        "no_biological_interpretation_from_two_comparators",
        "no_inventory_only_layer_before_next_result",
        "no_control_plan_only_layer_before_next_result",
        "no_additional_non_result_layer_before_next_concrete_step",
    ):
        if item.get(field) != "true":
            raise ValueError(f"Expected {field}=true")

    validate_source_matched_control(item)


def load_and_validate_additional_comparator(
    path: Path = DEFAULT_RESULT_TABLE,
) -> dict[str, str]:
    item = require_single_row(path)
    validate_additional_comparator_row(item)
    return item
