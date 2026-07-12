"""Validate and reproduce the first matched elephant-MDM2 control result.

The elephant MDM2 G3SX30 embedding is compared with the exact comparator frozen
in the preceding independent-control result. This is a numerical embedding-space
control only, not a biological negative control.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from longevity_port_pipelines.stages import (
    g3sx30_first_independent_pairwise_embedding_control_result as source_control,
)

DEFAULT_SOURCE_CONTROL_TABLE = Path(
    "data/input/g3sx30_first_independent_pairwise_embedding_control_results.csv"
)
DEFAULT_MATCHED_CONTROL_TABLE = Path(
    "data/input/g3sx30_first_matched_elephant_mdm2_independent_control_results.csv"
)

EXPECTED_ELEPHANT_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_COMPARATOR_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/4xhu__A1_P09874--4xhu__B1_Q9UNS1_receptor_109478.npy"
)

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "source_independent_control_table": (
        "data/input/g3sx30_first_independent_pairwise_embedding_control_results.csv"
    ),
    "source_independent_control_row_index": "1",
    "source_independent_control_status": (
        "first_independent_pairwise_embedding_control_result_created"
    ),
    "matched_control_status": ("first_matched_elephant_mdm2_independent_control_result_created"),
    "matched_control_scope": (
        "numerical_embedding_space_matched_comparator_control_only_no_biological_claim"
    ),
    "selection_rule_frozen_before_similarity": "true",
    "inventory_similarity_computed": "false",
    "new_inventory_performed": "false",
    "comparator_reselected": "false",
    "comparator_remained_frozen": "true",
    "baseline_human_elephant_mdm2_cosine_similarity": "0.9973314302339468",
    "human_mdm2_to_frozen_comparator_cosine_similarity": "0.8316190559481323",
    "elephant_anchor_accession": "G3SX30",
    "elephant_anchor_species": "Loxodonta africana",
    "elephant_anchor_taxid": "9785",
    "elephant_anchor_gene_symbol": "MDM2",
    "elephant_anchor_artifact_reference": EXPECTED_ELEPHANT_REFERENCE,
    "elephant_anchor_shape": "492x960",
    "elephant_anchor_dtype": "float32",
    "elephant_anchor_finite": "true",
    "elephant_anchor_artifact_committed": "false",
    "elephant_anchor_mean_vector_l2_norm": "0.8347860929210978",
    "frozen_comparator_source_accession": "P09874",
    "frozen_comparator_target_accession": "EPQ16369.1",
    "frozen_comparator_target_accession_db": "NCBI Protein",
    "frozen_comparator_species": "brandts_bat",
    "frozen_comparator_taxid": "109478",
    "frozen_comparator_complex_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
    "frozen_comparator_chain": "receptor",
    "frozen_comparator_artifact_reference": EXPECTED_COMPARATOR_REFERENCE,
    "frozen_comparator_shape": "1024x960",
    "frozen_comparator_dtype": "float32",
    "frozen_comparator_finite": "true",
    "frozen_comparator_artifact_committed": "false",
    "frozen_comparator_mean_vector_l2_norm": "0.7998408962311685",
    "model": "esmc-300m-2024-12",
    "pooling": "independent_mean_pooling_over_residue_axis",
    "metric_calculation_dtype": "float64",
    "metric_decimal_places": "16",
    "elephant_mdm2_to_frozen_comparator_cosine_similarity": "0.8409825967886765",
    "baseline_minus_elephant_control_delta": "0.1563488334452703",
    "baseline_greater_than_elephant_control": "true",
    "human_control_minus_elephant_control_delta": "-0.0093635408405441",
    "absolute_human_elephant_control_similarity_difference": "0.0093635408405441",
    "external_matched_control_result_sha256": (
        "4fe3e2ec90e83eb82a4e6ac792845259fec47c03f151e0f979cd2b4d71d73301"
    ),
    "matched_control_result_created": "true",
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
        "add_first_additional_source_backed_independent_comparator_result_"
        "with_selection_frozen_in_same_step"
    ),
    "no_biological_interpretation_from_single_comparator": "true",
    "no_inventory_only_layer_before_next_result": "true",
    "no_control_plan_only_layer_before_next_result": "true",
    "no_additional_non_result_layer_before_next_concrete_step": "true",
    "result_date": "2026-07-12",
    "claim_note": (
        "Numerical matched embedding-space comparator only; not a biological "
        "negative control; not residue alignment; not interface analysis; not a "
        "binding result; not orthology proof; not functional-equivalence evidence; "
        "not longevity evidence."
    ),
}

FALSE_ONLY_FIELDS = (
    "inventory_similarity_computed",
    "new_inventory_performed",
    "comparator_reselected",
    "elephant_anchor_artifact_committed",
    "frozen_comparator_artifact_committed",
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
class MatchedControlMetrics:
    elephant_anchor_mean_vector_l2_norm: float
    frozen_comparator_mean_vector_l2_norm: float
    elephant_mdm2_to_frozen_comparator_cosine_similarity: float
    baseline_minus_elephant_control_delta: float
    baseline_greater_than_elephant_control: bool
    human_control_minus_elephant_control_delta: float
    absolute_human_elephant_control_similarity_difference: float


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


def compute_matched_control_metrics(
    elephant_anchor: np.ndarray,
    frozen_comparator: np.ndarray,
    *,
    baseline_human_elephant_mdm2_cosine_similarity: float,
    human_mdm2_to_frozen_comparator_cosine_similarity: float,
) -> MatchedControlMetrics:
    _validate_embedding(elephant_anchor, expected_rows=492)
    _validate_embedding(frozen_comparator, expected_rows=1024)

    elephant_mean = elephant_anchor.mean(axis=0, dtype=np.float64)
    comparator_mean = frozen_comparator.mean(axis=0, dtype=np.float64)

    elephant_norm = float(np.linalg.norm(elephant_mean))
    comparator_norm = float(np.linalg.norm(comparator_mean))
    if elephant_norm <= 0.0 or comparator_norm <= 0.0:
        raise ValueError("Mean-pooled embedding vectors must have positive norm")

    elephant_control = float(
        np.dot(elephant_mean, comparator_mean) / (elephant_norm * comparator_norm)
    )
    baseline_delta = float(baseline_human_elephant_mdm2_cosine_similarity - elephant_control)
    human_control_delta = float(
        human_mdm2_to_frozen_comparator_cosine_similarity - elephant_control
    )
    absolute_control_difference = abs(human_control_delta)

    values = (
        baseline_human_elephant_mdm2_cosine_similarity,
        human_mdm2_to_frozen_comparator_cosine_similarity,
        elephant_norm,
        comparator_norm,
        elephant_control,
        baseline_delta,
        human_control_delta,
        absolute_control_difference,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Matched control metrics must all be finite")
    for label, value in [
        (
            "baseline human-elephant MDM2 cosine similarity",
            baseline_human_elephant_mdm2_cosine_similarity,
        ),
        (
            "human MDM2 to frozen comparator cosine similarity",
            human_mdm2_to_frozen_comparator_cosine_similarity,
        ),
        (
            "elephant MDM2 to frozen comparator cosine similarity",
            elephant_control,
        ),
    ]:
        if not -1.0 <= value <= 1.0:
            raise ValueError(f"{label} must be in [-1, 1]")

    return MatchedControlMetrics(
        elephant_anchor_mean_vector_l2_norm=elephant_norm,
        frozen_comparator_mean_vector_l2_norm=comparator_norm,
        elephant_mdm2_to_frozen_comparator_cosine_similarity=elephant_control,
        baseline_minus_elephant_control_delta=baseline_delta,
        baseline_greater_than_elephant_control=(baseline_delta > COMPARISON_ABS_TOL),
        human_control_minus_elephant_control_delta=human_control_delta,
        absolute_human_elephant_control_similarity_difference=(absolute_control_difference),
    )


def reproduce_matched_control(
    elephant_anchor_path: Path,
    frozen_comparator_path: Path,
    *,
    baseline_human_elephant_mdm2_cosine_similarity: float,
    human_mdm2_to_frozen_comparator_cosine_similarity: float,
) -> MatchedControlMetrics:
    elephant_anchor = np.load(elephant_anchor_path, allow_pickle=False)
    frozen_comparator = np.load(frozen_comparator_path, allow_pickle=False)
    return compute_matched_control_metrics(
        elephant_anchor,
        frozen_comparator,
        baseline_human_elephant_mdm2_cosine_similarity=(
            baseline_human_elephant_mdm2_cosine_similarity
        ),
        human_mdm2_to_frozen_comparator_cosine_similarity=(
            human_mdm2_to_frozen_comparator_cosine_similarity
        ),
    )


def validate_source_control(item: dict[str, str]) -> None:
    source = source_control.load_and_validate_independent_control(DEFAULT_SOURCE_CONTROL_TABLE)
    expected = {
        "independent_control_status": item["source_independent_control_status"],
        "baseline_mdm2_cosine_similarity": (item["baseline_human_elephant_mdm2_cosine_similarity"]),
        "independent_control_cosine_similarity": (
            item["human_mdm2_to_frozen_comparator_cosine_similarity"]
        ),
        "selection_rule_frozen_before_similarity": "true",
        "inventory_similarity_computed": "false",
        "independent_comparator_source_accession": (item["frozen_comparator_source_accession"]),
        "independent_comparator_target_accession": (item["frozen_comparator_target_accession"]),
        "independent_comparator_species": item["frozen_comparator_species"],
        "independent_comparator_taxid": item["frozen_comparator_taxid"],
        "independent_comparator_artifact_reference": (item["frozen_comparator_artifact_reference"]),
        "comparator_must_remain_frozen": "true",
        "next_step": (
            "add_first_matched_elephant_mdm2_independent_control_result_before_interpretation"
        ),
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    for field, required in expected.items():
        actual = source.get(field)
        if actual != required:
            raise ValueError(
                f"Source independent control expected {field}={required!r}, got {actual!r}"
            )


def validate_matched_control_row(item: dict[str, str]) -> None:
    for field, expected in EXPECTED_VALUES.items():
        actual = item.get(field)
        if actual != expected:
            raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")

    for field in FALSE_ONLY_FIELDS:
        if item[field] != "false":
            raise ValueError(f"Expected {field}='false'")

    numeric_fields = (
        "baseline_human_elephant_mdm2_cosine_similarity",
        "human_mdm2_to_frozen_comparator_cosine_similarity",
        "elephant_anchor_mean_vector_l2_norm",
        "frozen_comparator_mean_vector_l2_norm",
        "elephant_mdm2_to_frozen_comparator_cosine_similarity",
        "baseline_minus_elephant_control_delta",
        "human_control_minus_elephant_control_delta",
        "absolute_human_elephant_control_similarity_difference",
    )
    for field in numeric_fields:
        if not math.isfinite(float(item[field])):
            raise ValueError(f"Expected finite metric {field}")

    baseline = float(item["baseline_human_elephant_mdm2_cosine_similarity"])
    human_control = float(item["human_mdm2_to_frozen_comparator_cosine_similarity"])
    elephant_control = float(item["elephant_mdm2_to_frozen_comparator_cosine_similarity"])
    baseline_delta = float(item["baseline_minus_elephant_control_delta"])
    human_control_delta = float(item["human_control_minus_elephant_control_delta"])
    absolute_control_difference = float(
        item["absolute_human_elephant_control_similarity_difference"]
    )

    for label, value in [
        ("baseline", baseline),
        ("human control", human_control),
        ("elephant control", elephant_control),
    ]:
        if not -1.0 <= value <= 1.0:
            raise ValueError(f"{label} cosine similarity must be in [-1, 1]")

    if not math.isclose(
        baseline_delta,
        baseline - elephant_control,
        abs_tol=COMPARISON_ABS_TOL,
    ):
        raise ValueError("baseline_minus_elephant_control_delta is inconsistent")
    if not math.isclose(
        human_control_delta,
        human_control - elephant_control,
        abs_tol=COMPARISON_ABS_TOL,
    ):
        raise ValueError("human_control_minus_elephant_control_delta is inconsistent")
    if not math.isclose(
        absolute_control_difference,
        abs(human_control_delta),
        abs_tol=COMPARISON_ABS_TOL,
    ):
        raise ValueError("absolute_human_elephant_control_similarity_difference is inconsistent")

    expected_baseline_greater = baseline_delta > COMPARISON_ABS_TOL
    if expected_baseline_greater != (item["baseline_greater_than_elephant_control"] == "true"):
        raise ValueError("Baseline/elephant-control ordering is inconsistent")

    if item["frozen_comparator_artifact_reference"] != EXPECTED_COMPARATOR_REFERENCE:
        raise ValueError("Frozen comparator path changed")
    if item["elephant_anchor_artifact_reference"] == item["frozen_comparator_artifact_reference"]:
        raise ValueError("Anchor and comparator paths must differ")

    claim_note = item.get("claim_note", "")
    for required in [
        "not a biological negative control",
        "not residue alignment",
        "not interface analysis",
        "not a binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
    ]:
        if required not in claim_note:
            raise ValueError(f"Missing claim boundary phrase: {required}")


def load_and_validate_matched_control(
    path: Path = DEFAULT_MATCHED_CONTROL_TABLE,
) -> dict[str, str]:
    item = require_single_row(path)
    validate_matched_control_row(item)
    validate_source_control(item)
    return item
