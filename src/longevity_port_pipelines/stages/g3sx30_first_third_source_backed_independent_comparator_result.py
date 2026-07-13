"""Validate the first third source-backed independent comparator result.

The committed row records one externally calculated whole-protein embedding-space
comparison. Selection was frozen before similarity calculation. This is not a
validated biological negative control and does not establish exact embedding-byte
or sequence-hash provenance.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from longevity_port_pipelines.stages import (
    g3sx30_first_additional_source_backed_independent_comparator_result as second_source,
)
from longevity_port_pipelines.stages import (
    g3sx30_first_matched_elephant_mdm2_independent_control_result as first_source,
)
from longevity_port_pipelines.stages import (
    g3sx30_first_two_comparator_pairwise_embedding_control_summary as source_summary,
)

DEFAULT_SOURCE_TABLE = Path(
    "data/input/g3sx30_first_two_comparator_pairwise_embedding_control_summaries.csv"
)
DEFAULT_RESULT_TABLE = Path(
    "data/input/g3sx30_first_third_source_backed_independent_comparator_results.csv"
)

EXPECTED_HUMAN_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9606.npy"
)
EXPECTED_ELEPHANT_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_COMPARATOR_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/7s68__D1_P09874--7s68__C1_P09874_ligand_9606.npy"
)

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "source_two_comparator_summary_table": (
        "data/input/g3sx30_first_two_comparator_pairwise_embedding_control_summaries.csv"
    ),
    "source_two_comparator_summary_row_index": "1",
    "source_two_comparator_summary_status": (
        "first_two_comparator_pairwise_embedding_control_summary_created"
    ),
    "result_status": "first_third_source_backed_independent_comparator_result_created",
    "result_scope": ("numerical_embedding_space_third_comparator_only_no_biological_claim"),
    "execution_helper_sha256": ("9c5ec6bab1b4b8681925e86d58a3790b60892ab403ce3c297a2330163cdec614"),
    "selection_freeze_json_sha256": (
        "d6b3ccb2f621dbac7d5723eef9fa126ac141815fea2ddb49f741869f06b36a8e"
    ),
    "selection_rule_sha256": ("aab50c4dcbd198f2ccd7525f29616071cd93b0ba2cbc6c735104e30990e59042"),
    "selection_rule_frozen_before_similarity": "true",
    "similarity_used_for_selection": "false",
    "selection_and_result_in_same_step": "true",
    "historical_inventory_file_count": "216",
    "current_inventory_file_count": "216",
    "inventory_file_count_delta": "0",
    "historical_inventory_universe_sha256": (
        "30ddb570feda2438c7c1864d466f43521ce8ab03ce1561f91f75f3cab78a8022"
    ),
    "inventory_universe_sha256": (
        "30ddb570feda2438c7c1864d466f43521ce8ab03ce1561f91f75f3cab78a8022"
    ),
    "added_inventory_path_count": "0",
    "removed_inventory_path_count": "0",
    "source_backed_eligible_candidate_count": "94",
    "selected_rank": "1",
    "selected_comparator_artifact_reference": EXPECTED_COMPARATOR_REFERENCE,
    "selected_comparator_shape": "211x960",
    "selected_comparator_dtype": "float32",
    "selected_comparator_finite": "true",
    "selected_comparator_artifact_committed": "false",
    "selected_comparator_ignored": "true",
    "selected_comparator_tracked": "false",
    "selected_comparator_staged": "false",
    "selected_comparator_reference_tier": "3",
    "selected_comparator_reference_files": (
        "data/config/g3sx30_first_independent_pairwise_embedding_control_result_schema.yaml"
        "|data/input/curated_ortholog_candidates.csv"
        "|data/input/g3sx30_first_independent_pairwise_embedding_control_results.csv"
    ),
    "selected_comparator_accession_tokens": "P09874",
    "selected_comparator_pdb_token": "7s68",
    "selected_comparator_taxid": "9606",
    "selected_comparator_reuses_previous_comparator": "false",
    "selected_comparator_reuses_previous_complex_context": "false",
    "post_selection_exact_complex_match_count": "26",
    "exact_artifact_path_reference_found": "false",
    "exact_artifact_basename_reference_found": "false",
    "complex_role_accession_taxid_context_confirmed": "true",
    "exact_embedding_byte_provenance_confirmed": "false",
    "exact_sequence_hash_provenance_confirmed": "false",
    "supplemental_provenance_files": (
        "docs/sirt6_mini_pilot_v2_candidate_selection.md|docs/parp1_negatome_evidence_notes.md"
    ),
    "supplemental_provenance_context_status": "v1_selected_parp1_homodimer_context",
    "supplemental_provenance_source_accession": "P09874",
    "supplemental_provenance_partner_accession": "P09874",
    "supplemental_provenance_intermolecular_contacts": "50",
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
    "first_human_control_cosine_similarity": "0.8316190559481323",
    "first_elephant_control_cosine_similarity": "0.8409825967886765",
    "second_human_control_cosine_similarity": "0.8095126148075514",
    "second_elephant_control_cosine_similarity": "0.8203721870665286",
    "human_mdm2_mean_vector_l2_norm": "0.8317611517806081",
    "elephant_mdm2_mean_vector_l2_norm": "0.8347860929210978",
    "third_comparator_mean_vector_l2_norm": "0.8067238204277115",
    "human_mdm2_to_third_comparator_cosine_similarity": "0.7472839682873271",
    "elephant_mdm2_to_third_comparator_cosine_similarity": "0.7516055327169140",
    "baseline_minus_human_third_control_delta": "0.2500474619466196",
    "baseline_minus_elephant_third_control_delta": "0.2457258975170328",
    "baseline_greater_than_human_third_control": "true",
    "baseline_greater_than_elephant_third_control": "true",
    "human_third_control_minus_elephant_third_control_delta": ("-0.0043215644295869"),
    "absolute_human_elephant_third_control_difference": "0.0043215644295869",
    "external_third_comparator_result_sha256": (
        "82fc8b408d815816dc5834e3d2e79de0d3f83699bb481d0b4a061b754873c043"
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
    "validated_biological_negative_control_panel": "false",
    "biological_specificity_claimed": "false",
    "biological_claim_made": "false",
    "next_step": (
        "add_first_three_comparator_pairwise_embedding_control_summary_before_interface_manifest"
    ),
    "no_biological_interpretation_from_three_comparators": "true",
    "no_inventory_only_layer_before_next_result": "true",
    "no_control_plan_only_layer_before_next_result": "true",
    "no_additional_non_result_layer_before_next_concrete_step": "true",
    "result_date": "2026-07-13",
    "claim_note": (
        "Numerical whole-protein embedding-space third comparator only; not a "
        "validated biological negative control; not evidence of biological "
        "specificity; not exact embedding-byte provenance; not exact sequence-hash "
        "provenance; not residue alignment; not interface analysis; not a binding "
        "result; not orthology proof; not functional-equivalence evidence; not "
        "longevity evidence; not a biological claim."
    ),
}

FALSE_ONLY_FIELDS = (
    "similarity_used_for_selection",
    "selected_comparator_artifact_committed",
    "selected_comparator_tracked",
    "selected_comparator_staged",
    "selected_comparator_reuses_previous_comparator",
    "selected_comparator_reuses_previous_complex_context",
    "exact_artifact_path_reference_found",
    "exact_artifact_basename_reference_found",
    "exact_embedding_byte_provenance_confirmed",
    "exact_sequence_hash_provenance_confirmed",
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
    "validated_biological_negative_control_panel",
    "biological_specificity_claimed",
    "biological_claim_made",
)

TRUE_ONLY_FIELDS = (
    "selection_rule_frozen_before_similarity",
    "selection_and_result_in_same_step",
    "selected_comparator_finite",
    "selected_comparator_ignored",
    "complex_role_accession_taxid_context_confirmed",
    "human_mdm2_finite",
    "elephant_mdm2_finite",
    "baseline_greater_than_human_third_control",
    "baseline_greater_than_elephant_third_control",
    "result_created",
    "no_biological_interpretation_from_three_comparators",
    "no_inventory_only_layer_before_next_result",
    "no_control_plan_only_layer_before_next_result",
    "no_additional_non_result_layer_before_next_concrete_step",
)

COMPARISON_ABS_TOL = 5e-16


@dataclass(frozen=True)
class ThirdComparatorMetrics:
    human_mdm2_mean_vector_l2_norm: float
    elephant_mdm2_mean_vector_l2_norm: float
    third_comparator_mean_vector_l2_norm: float
    human_mdm2_to_third_comparator_cosine_similarity: float
    elephant_mdm2_to_third_comparator_cosine_similarity: float
    baseline_minus_human_third_control_delta: float
    baseline_minus_elephant_third_control_delta: float
    baseline_greater_than_human_third_control: bool
    baseline_greater_than_elephant_third_control: bool
    human_third_control_minus_elephant_third_control_delta: float
    absolute_human_elephant_third_control_difference: float


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


def compute_third_comparator_metrics(
    human_mdm2: np.ndarray,
    elephant_mdm2: np.ndarray,
    third_comparator: np.ndarray,
    *,
    baseline_human_elephant_mdm2_cosine_similarity: float,
) -> ThirdComparatorMetrics:
    _validate_embedding(human_mdm2, expected_rows=491)
    _validate_embedding(elephant_mdm2, expected_rows=492)
    _validate_embedding(third_comparator, expected_rows=211)

    human_mean, human_norm = _mean_and_norm(human_mdm2)
    elephant_mean, elephant_norm = _mean_and_norm(elephant_mdm2)
    comparator_mean, comparator_norm = _mean_and_norm(third_comparator)

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
        raise ValueError("Third comparator metrics must all be finite")

    return ThirdComparatorMetrics(
        human_mdm2_mean_vector_l2_norm=human_norm,
        elephant_mdm2_mean_vector_l2_norm=elephant_norm,
        third_comparator_mean_vector_l2_norm=comparator_norm,
        human_mdm2_to_third_comparator_cosine_similarity=human_similarity,
        elephant_mdm2_to_third_comparator_cosine_similarity=elephant_similarity,
        baseline_minus_human_third_control_delta=baseline_minus_human,
        baseline_minus_elephant_third_control_delta=baseline_minus_elephant,
        baseline_greater_than_human_third_control=(baseline_minus_human > COMPARISON_ABS_TOL),
        baseline_greater_than_elephant_third_control=(baseline_minus_elephant > COMPARISON_ABS_TOL),
        human_third_control_minus_elephant_third_control_delta=human_minus_elephant,
        absolute_human_elephant_third_control_difference=absolute_difference,
    )


def reproduce_third_comparator(
    human_mdm2_path: Path,
    elephant_mdm2_path: Path,
    third_comparator_path: Path,
    *,
    baseline_human_elephant_mdm2_cosine_similarity: float,
) -> ThirdComparatorMetrics:
    human = np.load(human_mdm2_path, allow_pickle=False)
    elephant = np.load(elephant_mdm2_path, allow_pickle=False)
    comparator = np.load(third_comparator_path, allow_pickle=False)
    return compute_third_comparator_metrics(
        human,
        elephant,
        comparator,
        baseline_human_elephant_mdm2_cosine_similarity=(
            baseline_human_elephant_mdm2_cosine_similarity
        ),
    )


def validate_source_summary(item: dict[str, str]) -> None:
    source = source_summary.load_and_validate_two_comparator_summary(DEFAULT_SOURCE_TABLE)
    expected = {
        "summary_status": item["source_two_comparator_summary_status"],
        "baseline_human_elephant_mdm2_cosine_similarity": (
            item["baseline_human_elephant_mdm2_cosine_similarity"]
        ),
        "first_human_control_cosine_similarity": (item["first_human_control_cosine_similarity"]),
        "first_elephant_control_cosine_similarity": (
            item["first_elephant_control_cosine_similarity"]
        ),
        "second_human_control_cosine_similarity": (item["second_human_control_cosine_similarity"]),
        "second_elephant_control_cosine_similarity": (
            item["second_elephant_control_cosine_similarity"]
        ),
        "next_step": (
            "add_first_third_source_backed_independent_comparator_result_"
            "with_selection_frozen_in_same_step"
        ),
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    for field, required in expected.items():
        actual = source.get(field)
        if actual != required:
            raise ValueError(f"Source summary expected {field}={required!r}, got {actual!r}")


def validate_third_comparator_row(item: dict[str, str]) -> None:
    for field, expected in EXPECTED_VALUES.items():
        actual = item.get(field)
        if actual != expected:
            raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")

    for field in FALSE_ONLY_FIELDS:
        if item.get(field) != "false":
            raise ValueError(f"Expected {field}=false")

    for field in TRUE_ONLY_FIELDS:
        if item.get(field) != "true":
            raise ValueError(f"Expected {field}=true")

    if item["historical_inventory_universe_sha256"] != item["inventory_universe_sha256"]:
        raise ValueError("Inventory universe SHA256 changed despite zero inventory delta")

    if item["selected_comparator_artifact_reference"] in {
        first_source.EXPECTED_COMPARATOR_REFERENCE,
        second_source.EXPECTED_COMPARATOR_REFERENCE,
    }:
        raise ValueError("Third comparator must differ from the first two comparators")

    for field in (
        "baseline_human_elephant_mdm2_cosine_similarity",
        "first_human_control_cosine_similarity",
        "first_elephant_control_cosine_similarity",
        "second_human_control_cosine_similarity",
        "second_elephant_control_cosine_similarity",
        "human_mdm2_mean_vector_l2_norm",
        "elephant_mdm2_mean_vector_l2_norm",
        "third_comparator_mean_vector_l2_norm",
        "human_mdm2_to_third_comparator_cosine_similarity",
        "elephant_mdm2_to_third_comparator_cosine_similarity",
        "baseline_minus_human_third_control_delta",
        "baseline_minus_elephant_third_control_delta",
        "human_third_control_minus_elephant_third_control_delta",
        "absolute_human_elephant_third_control_difference",
    ):
        if not math.isfinite(float(item[field])):
            raise ValueError(f"Expected finite metric {field}")

    baseline = float(item["baseline_human_elephant_mdm2_cosine_similarity"])
    human = float(item["human_mdm2_to_third_comparator_cosine_similarity"])
    elephant = float(item["elephant_mdm2_to_third_comparator_cosine_similarity"])

    computed = {
        "baseline_minus_human_third_control_delta": baseline - human,
        "baseline_minus_elephant_third_control_delta": baseline - elephant,
        "human_third_control_minus_elephant_third_control_delta": human - elephant,
        "absolute_human_elephant_third_control_difference": abs(human - elephant),
    }
    for field, value in computed.items():
        if item[field] != f"{value:.16f}":
            raise ValueError(f"Computed {field}={f'{value:.16f}'!r}, got {item[field]!r}")

    if (baseline - human > COMPARISON_ABS_TOL) != (
        item["baseline_greater_than_human_third_control"] == "true"
    ):
        raise ValueError("Human third-control baseline ordering is inconsistent")
    if (baseline - elephant > COMPARISON_ABS_TOL) != (
        item["baseline_greater_than_elephant_third_control"] == "true"
    ):
        raise ValueError("Elephant third-control baseline ordering is inconsistent")

    claim_note = item.get("claim_note", "")
    for required in (
        "not a validated biological negative control",
        "not evidence of biological specificity",
        "not exact embedding-byte provenance",
        "not exact sequence-hash provenance",
        "not residue alignment",
        "not interface analysis",
        "not a binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
        "not a biological claim",
    ):
        if required not in claim_note:
            raise ValueError(f"Missing claim boundary phrase: {required}")

    validate_source_summary(item)


def load_and_validate_third_comparator(
    path: Path = DEFAULT_RESULT_TABLE,
) -> dict[str, str]:
    item = require_single_row(path)
    validate_third_comparator_row(item)
    return item
