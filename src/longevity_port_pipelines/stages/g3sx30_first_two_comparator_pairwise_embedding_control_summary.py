"""Aggregate the first two committed MDM2 comparator result pairs.

The module reads and validates committed one-row CSV results only. It never
loads embedding arrays and never computes a new embedding cosine similarity.
The summary is numerical embedding-space bookkeeping, not a biological claim.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from longevity_port_pipelines.stages import (
    g3sx30_first_additional_source_backed_independent_comparator_result as second_source,
)
from longevity_port_pipelines.stages import (
    g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summary as baseline_source,
)
from longevity_port_pipelines.stages import (
    g3sx30_first_matched_elephant_mdm2_independent_control_result as first_source,
)

DEFAULT_BASELINE_TABLE = Path(
    "data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv"
)
DEFAULT_FIRST_COMPARATOR_TABLE = Path(
    "data/input/g3sx30_first_matched_elephant_mdm2_independent_control_results.csv"
)
DEFAULT_SECOND_COMPARATOR_TABLE = Path(
    "data/input/g3sx30_first_additional_source_backed_independent_comparator_results.csv"
)
DEFAULT_SUMMARY_TABLE = Path(
    "data/input/g3sx30_first_two_comparator_pairwise_embedding_control_summaries.csv"
)

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "source_baseline_table": (
        "data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv"
    ),
    "source_baseline_row_index": "1",
    "source_baseline_status": ("first_human_elephant_mdm2_mean_pooled_embedding_summary_created"),
    "source_first_comparator_table": (
        "data/input/g3sx30_first_matched_elephant_mdm2_independent_control_results.csv"
    ),
    "source_first_comparator_row_index": "1",
    "source_first_comparator_status": (
        "first_matched_elephant_mdm2_independent_control_result_created"
    ),
    "source_second_comparator_table": (
        "data/input/g3sx30_first_additional_source_backed_independent_comparator_results.csv"
    ),
    "source_second_comparator_row_index": "1",
    "source_second_comparator_status": (
        "first_additional_source_backed_independent_comparator_result_created"
    ),
    "source_second_comparator_required_next_step": (
        "add_first_two_comparator_pairwise_embedding_control_summary_before_interpretation"
    ),
    "summary_status": ("first_two_comparator_pairwise_embedding_control_summary_created"),
    "summary_scope": (
        "numerical_embedding_space_two_comparator_aggregation_only_no_biological_claim"
    ),
    "comparator_count": "2",
    "control_similarity_count": "4",
    "source_rows_validated": "true",
    "aggregation_recomputed_from_committed_rows": "true",
    "aggregation_method": "math_fsum_divided_by_count",
    "metric_calculation_dtype": "float64",
    "metric_decimal_places": "16",
    "baseline_human_elephant_mdm2_cosine_similarity": "0.9973314302339468",
    "first_human_control_cosine_similarity": "0.8316190559481323",
    "first_elephant_control_cosine_similarity": "0.8409825967886765",
    "first_absolute_human_elephant_control_difference": "0.0093635408405441",
    "second_human_control_cosine_similarity": "0.8095126148075514",
    "second_elephant_control_cosine_similarity": "0.8203721870665286",
    "second_absolute_human_elephant_control_difference": "0.0108595722589772",
    "human_control_mean_cosine_similarity": "0.8205658353778419",
    "elephant_control_mean_cosine_similarity": "0.8306773919276025",
    "all_control_mean_cosine_similarity": "0.8256216136527222",
    "minimum_control_cosine_similarity": "0.8095126148075514",
    "maximum_control_cosine_similarity": "0.8409825967886765",
    "control_cosine_similarity_range": "0.0314699819811251",
    "minimum_baseline_minus_control_delta": "0.1563488334452703",
    "maximum_baseline_minus_control_delta": "0.1878188154263953",
    "baseline_greater_than_all_four_controls": "true",
    "first_comparator_baseline_greater_than_both_anchors": "true",
    "second_comparator_baseline_greater_than_both_anchors": "true",
    "human_control_mean_minus_elephant_control_mean_delta": "-0.0101115565497606",
    "absolute_human_elephant_control_mean_difference": "0.0101115565497606",
    "mean_absolute_human_elephant_control_difference": "0.0101115565497607",
    "maximum_absolute_human_elephant_control_difference": "0.0108595722589772",
    "anchor_ordering_consistent_across_comparators": "true",
    "summary_result_created": "true",
    "new_similarity_computed": "false",
    "source_embedding_arrays_loaded": "false",
    "new_inventory_performed": "false",
    "comparator_selection_performed": "false",
    "biohub_esmc_called": "false",
    "new_embedding_generated": "false",
    "npy_artifact_read": "false",
    "npy_artifact_committed": "false",
    "raw_embedding_vectors_committed": "false",
    "data_output_artifact_committed": "false",
    "external_result_json_created": "false",
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
        "add_first_third_source_backed_independent_comparator_result_"
        "with_selection_frozen_in_same_step"
    ),
    "no_biological_interpretation_from_two_comparators": "true",
    "no_inventory_only_layer_before_next_result": "true",
    "no_control_plan_only_layer_before_next_result": "true",
    "no_additional_non_result_layer_before_next_concrete_step": "true",
    "result_date": "2026-07-13",
    "claim_note": (
        "Numerical aggregation of two committed embedding-space comparator "
        "pairs only; not a validated biological negative-control panel; not "
        "evidence of biological specificity; not residue alignment; not "
        "interface analysis; not a binding result; not orthology proof; not "
        "functional-equivalence evidence; not longevity evidence; not a "
        "biological claim."
    ),
}

FALSE_ONLY_FIELDS = (
    "new_similarity_computed",
    "source_embedding_arrays_loaded",
    "new_inventory_performed",
    "comparator_selection_performed",
    "biohub_esmc_called",
    "new_embedding_generated",
    "npy_artifact_read",
    "npy_artifact_committed",
    "raw_embedding_vectors_committed",
    "data_output_artifact_committed",
    "external_result_json_created",
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
    "source_rows_validated",
    "aggregation_recomputed_from_committed_rows",
    "baseline_greater_than_all_four_controls",
    "first_comparator_baseline_greater_than_both_anchors",
    "second_comparator_baseline_greater_than_both_anchors",
    "anchor_ordering_consistent_across_comparators",
    "summary_result_created",
    "no_biological_interpretation_from_two_comparators",
    "no_inventory_only_layer_before_next_result",
    "no_control_plan_only_layer_before_next_result",
    "no_additional_non_result_layer_before_next_concrete_step",
)

METRIC_FIELDS = (
    "baseline_human_elephant_mdm2_cosine_similarity",
    "first_human_control_cosine_similarity",
    "first_elephant_control_cosine_similarity",
    "first_absolute_human_elephant_control_difference",
    "second_human_control_cosine_similarity",
    "second_elephant_control_cosine_similarity",
    "second_absolute_human_elephant_control_difference",
    "human_control_mean_cosine_similarity",
    "elephant_control_mean_cosine_similarity",
    "all_control_mean_cosine_similarity",
    "minimum_control_cosine_similarity",
    "maximum_control_cosine_similarity",
    "control_cosine_similarity_range",
    "minimum_baseline_minus_control_delta",
    "maximum_baseline_minus_control_delta",
    "human_control_mean_minus_elephant_control_mean_delta",
    "absolute_human_elephant_control_mean_difference",
    "mean_absolute_human_elephant_control_difference",
    "maximum_absolute_human_elephant_control_difference",
)

COMPARISON_ABS_TOL = 5e-16


@dataclass(frozen=True)
class TwoComparatorSummaryMetrics:
    human_control_mean_cosine_similarity: float
    elephant_control_mean_cosine_similarity: float
    all_control_mean_cosine_similarity: float
    minimum_control_cosine_similarity: float
    maximum_control_cosine_similarity: float
    control_cosine_similarity_range: float
    minimum_baseline_minus_control_delta: float
    maximum_baseline_minus_control_delta: float
    baseline_greater_than_all_four_controls: bool
    first_comparator_baseline_greater_than_both_anchors: bool
    second_comparator_baseline_greater_than_both_anchors: bool
    human_control_mean_minus_elephant_control_mean_delta: float
    absolute_human_elephant_control_mean_difference: float
    mean_absolute_human_elephant_control_difference: float
    maximum_absolute_human_elephant_control_difference: float
    anchor_ordering_consistent_across_comparators: bool


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def format_metric(value: float) -> str:
    return f"{value:.16f}"


def _validate_cosine(label: str, value: float) -> None:
    if not math.isfinite(value) or not -1.0 <= value <= 1.0:
        raise ValueError(f"{label} must be finite and in [-1, 1]")


def compute_two_comparator_summary_metrics(
    *,
    baseline: float,
    first_human_control: float,
    first_elephant_control: float,
    second_human_control: float,
    second_elephant_control: float,
    first_absolute_anchor_difference: float,
    second_absolute_anchor_difference: float,
) -> TwoComparatorSummaryMetrics:
    for label, value in [
        ("baseline", baseline),
        ("first human control", first_human_control),
        ("first elephant control", first_elephant_control),
        ("second human control", second_human_control),
        ("second elephant control", second_elephant_control),
    ]:
        _validate_cosine(label, value)

    for label, value in [
        ("first absolute anchor difference", first_absolute_anchor_difference),
        ("second absolute anchor difference", second_absolute_anchor_difference),
    ]:
        if not math.isfinite(value) or not 0.0 <= value <= 2.0:
            raise ValueError(f"{label} must be finite and in [0, 2]")

    if not math.isclose(
        first_absolute_anchor_difference,
        abs(first_human_control - first_elephant_control),
        abs_tol=COMPARISON_ABS_TOL,
    ):
        raise ValueError("First committed absolute anchor difference is inconsistent")
    if not math.isclose(
        second_absolute_anchor_difference,
        abs(second_human_control - second_elephant_control),
        abs_tol=COMPARISON_ABS_TOL,
    ):
        raise ValueError("Second committed absolute anchor difference is inconsistent")

    human_controls = (first_human_control, second_human_control)
    elephant_controls = (first_elephant_control, second_elephant_control)
    all_controls = (
        first_human_control,
        first_elephant_control,
        second_human_control,
        second_elephant_control,
    )

    human_mean = math.fsum(human_controls) / len(human_controls)
    elephant_mean = math.fsum(elephant_controls) / len(elephant_controls)
    all_mean = math.fsum(all_controls) / len(all_controls)
    minimum_control = min(all_controls)
    maximum_control = max(all_controls)
    control_range = maximum_control - minimum_control
    minimum_baseline_delta = baseline - maximum_control
    maximum_baseline_delta = baseline - minimum_control

    mean_absolute_difference = (
        math.fsum(
            (
                first_absolute_anchor_difference,
                second_absolute_anchor_difference,
            )
        )
        / 2
    )
    maximum_absolute_difference = max(
        first_absolute_anchor_difference,
        second_absolute_anchor_difference,
    )
    mean_delta = human_mean - elephant_mean

    values = (
        human_mean,
        elephant_mean,
        all_mean,
        minimum_control,
        maximum_control,
        control_range,
        minimum_baseline_delta,
        maximum_baseline_delta,
        first_absolute_anchor_difference,
        second_absolute_anchor_difference,
        mean_absolute_difference,
        maximum_absolute_difference,
        mean_delta,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Two-comparator summary metrics must all be finite")

    return TwoComparatorSummaryMetrics(
        human_control_mean_cosine_similarity=human_mean,
        elephant_control_mean_cosine_similarity=elephant_mean,
        all_control_mean_cosine_similarity=all_mean,
        minimum_control_cosine_similarity=minimum_control,
        maximum_control_cosine_similarity=maximum_control,
        control_cosine_similarity_range=control_range,
        minimum_baseline_minus_control_delta=minimum_baseline_delta,
        maximum_baseline_minus_control_delta=maximum_baseline_delta,
        baseline_greater_than_all_four_controls=(minimum_baseline_delta > COMPARISON_ABS_TOL),
        first_comparator_baseline_greater_than_both_anchors=(
            baseline - max(first_human_control, first_elephant_control) > COMPARISON_ABS_TOL
        ),
        second_comparator_baseline_greater_than_both_anchors=(
            baseline - max(second_human_control, second_elephant_control) > COMPARISON_ABS_TOL
        ),
        human_control_mean_minus_elephant_control_mean_delta=mean_delta,
        absolute_human_elephant_control_mean_difference=abs(mean_delta),
        mean_absolute_human_elephant_control_difference=(mean_absolute_difference),
        maximum_absolute_human_elephant_control_difference=(maximum_absolute_difference),
        anchor_ordering_consistent_across_comparators=(
            (first_human_control < first_elephant_control)
            == (second_human_control < second_elephant_control)
        ),
    )


def validate_source_rows(item: dict[str, str]) -> None:
    baseline = baseline_source.load_and_validate_pairwise_summary(DEFAULT_BASELINE_TABLE)
    first = first_source.load_and_validate_matched_control(DEFAULT_FIRST_COMPARATOR_TABLE)
    second = second_source.load_and_validate_additional_comparator(DEFAULT_SECOND_COMPARATOR_TABLE)

    expected_baseline = {
        "pairwise_summary_status": item["source_baseline_status"],
        "mean_pooled_cosine_similarity": (item["baseline_human_elephant_mdm2_cosine_similarity"]),
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    expected_first = {
        "matched_control_status": item["source_first_comparator_status"],
        "baseline_human_elephant_mdm2_cosine_similarity": (
            item["baseline_human_elephant_mdm2_cosine_similarity"]
        ),
        "human_mdm2_to_frozen_comparator_cosine_similarity": (
            item["first_human_control_cosine_similarity"]
        ),
        "elephant_mdm2_to_frozen_comparator_cosine_similarity": (
            item["first_elephant_control_cosine_similarity"]
        ),
        "absolute_human_elephant_control_similarity_difference": (
            item["first_absolute_human_elephant_control_difference"]
        ),
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    expected_second = {
        "result_status": item["source_second_comparator_status"],
        "next_step": item["source_second_comparator_required_next_step"],
        "baseline_human_elephant_mdm2_cosine_similarity": (
            item["baseline_human_elephant_mdm2_cosine_similarity"]
        ),
        "previous_human_mdm2_to_comparator_cosine_similarity": (
            item["first_human_control_cosine_similarity"]
        ),
        "previous_elephant_mdm2_to_comparator_cosine_similarity": (
            item["first_elephant_control_cosine_similarity"]
        ),
        "human_mdm2_to_additional_comparator_cosine_similarity": (
            item["second_human_control_cosine_similarity"]
        ),
        "elephant_mdm2_to_additional_comparator_cosine_similarity": (
            item["second_elephant_control_cosine_similarity"]
        ),
        "absolute_human_elephant_additional_control_difference": (
            item["second_absolute_human_elephant_control_difference"]
        ),
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }

    for source_name, source, expected in [
        ("baseline", baseline, expected_baseline),
        ("first comparator", first, expected_first),
        ("second comparator", second, expected_second),
    ]:
        for field, required in expected.items():
            actual = source.get(field)
            if actual != required:
                raise ValueError(
                    f"{source_name} source expected {field}={required!r}, got {actual!r}"
                )

    if (
        first["frozen_comparator_artifact_reference"]
        == second["selected_comparator_artifact_reference"]
    ):
        raise ValueError("The two comparator artifact references must differ")


def validate_two_comparator_summary_row(item: dict[str, str]) -> None:
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

    for field in METRIC_FIELDS:
        if not math.isfinite(float(item[field])):
            raise ValueError(f"Expected finite metric {field}")

    metrics = compute_two_comparator_summary_metrics(
        baseline=float(item["baseline_human_elephant_mdm2_cosine_similarity"]),
        first_human_control=float(item["first_human_control_cosine_similarity"]),
        first_elephant_control=float(item["first_elephant_control_cosine_similarity"]),
        second_human_control=float(item["second_human_control_cosine_similarity"]),
        second_elephant_control=float(item["second_elephant_control_cosine_similarity"]),
        first_absolute_anchor_difference=float(
            item["first_absolute_human_elephant_control_difference"]
        ),
        second_absolute_anchor_difference=float(
            item["second_absolute_human_elephant_control_difference"]
        ),
    )
    computed = {
        "human_control_mean_cosine_similarity": (metrics.human_control_mean_cosine_similarity),
        "elephant_control_mean_cosine_similarity": (
            metrics.elephant_control_mean_cosine_similarity
        ),
        "all_control_mean_cosine_similarity": (metrics.all_control_mean_cosine_similarity),
        "minimum_control_cosine_similarity": (metrics.minimum_control_cosine_similarity),
        "maximum_control_cosine_similarity": (metrics.maximum_control_cosine_similarity),
        "control_cosine_similarity_range": (metrics.control_cosine_similarity_range),
        "minimum_baseline_minus_control_delta": (metrics.minimum_baseline_minus_control_delta),
        "maximum_baseline_minus_control_delta": (metrics.maximum_baseline_minus_control_delta),
        "human_control_mean_minus_elephant_control_mean_delta": (
            metrics.human_control_mean_minus_elephant_control_mean_delta
        ),
        "absolute_human_elephant_control_mean_difference": (
            metrics.absolute_human_elephant_control_mean_difference
        ),
        "mean_absolute_human_elephant_control_difference": (
            metrics.mean_absolute_human_elephant_control_difference
        ),
        "maximum_absolute_human_elephant_control_difference": (
            metrics.maximum_absolute_human_elephant_control_difference
        ),
    }
    for field, value in computed.items():
        if item[field] != format_metric(value):
            raise ValueError(f"Computed {field}={format_metric(value)!r}, got {item[field]!r}")

    boolean_computed = {
        "baseline_greater_than_all_four_controls": (
            metrics.baseline_greater_than_all_four_controls
        ),
        "first_comparator_baseline_greater_than_both_anchors": (
            metrics.first_comparator_baseline_greater_than_both_anchors
        ),
        "second_comparator_baseline_greater_than_both_anchors": (
            metrics.second_comparator_baseline_greater_than_both_anchors
        ),
        "anchor_ordering_consistent_across_comparators": (
            metrics.anchor_ordering_consistent_across_comparators
        ),
    }
    for field, value in boolean_computed.items():
        if item[field] != str(value).lower():
            raise ValueError(f"Computed boolean {field} is inconsistent")

    claim_note = item.get("claim_note", "")
    for required in [
        "not a validated biological negative-control panel",
        "not evidence of biological specificity",
        "not residue alignment",
        "not interface analysis",
        "not a binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
        "not a biological claim",
    ]:
        if required not in claim_note:
            raise ValueError(f"Missing claim boundary phrase: {required}")

    validate_source_rows(item)


def load_and_validate_two_comparator_summary(
    path: Path = DEFAULT_SUMMARY_TABLE,
) -> dict[str, str]:
    item = require_single_row(path)
    validate_two_comparator_summary_row(item)
    return item
