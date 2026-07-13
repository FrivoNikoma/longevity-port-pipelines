import pytest

from longevity_port_pipelines.stages import (
    g3sx30_first_two_comparator_pairwise_embedding_control_summary as summary,
)


def test_two_comparator_summary_table_has_one_valid_row() -> None:
    row = summary.load_and_validate_two_comparator_summary()

    assert row["summary_result_created"] == "true"
    assert row["comparator_count"] == "2"
    assert row["control_similarity_count"] == "4"
    assert row["source_rows_validated"] == "true"


def test_two_comparator_summary_records_exact_source_values() -> None:
    row = summary.load_and_validate_two_comparator_summary()

    assert row["baseline_human_elephant_mdm2_cosine_similarity"] == ("0.9973314302339468")
    assert row["first_human_control_cosine_similarity"] == ("0.8316190559481323")
    assert row["first_elephant_control_cosine_similarity"] == ("0.8409825967886765")
    assert row["second_human_control_cosine_similarity"] == ("0.8095126148075514")
    assert row["second_elephant_control_cosine_similarity"] == ("0.8203721870665286")


def test_two_comparator_summary_records_exact_aggregates() -> None:
    row = summary.load_and_validate_two_comparator_summary()

    expected = {
        "human_control_mean_cosine_similarity": "0.8205658353778419",
        "elephant_control_mean_cosine_similarity": "0.8306773919276025",
        "all_control_mean_cosine_similarity": "0.8256216136527222",
        "minimum_control_cosine_similarity": "0.8095126148075514",
        "maximum_control_cosine_similarity": "0.8409825967886765",
        "control_cosine_similarity_range": "0.0314699819811251",
        "minimum_baseline_minus_control_delta": "0.1563488334452703",
        "maximum_baseline_minus_control_delta": "0.1878188154263953",
        "human_control_mean_minus_elephant_control_mean_delta": ("-0.0101115565497606"),
        "absolute_human_elephant_control_mean_difference": ("0.0101115565497606"),
        "mean_absolute_human_elephant_control_difference": ("0.0101115565497607"),
        "maximum_absolute_human_elephant_control_difference": ("0.0108595722589772"),
    }
    for field, value in expected.items():
        assert row[field] == value


def test_two_comparator_summary_records_exact_boolean_results() -> None:
    row = summary.load_and_validate_two_comparator_summary()

    for field in [
        "baseline_greater_than_all_four_controls",
        "first_comparator_baseline_greater_than_both_anchors",
        "second_comparator_baseline_greater_than_both_anchors",
        "anchor_ordering_consistent_across_comparators",
    ]:
        assert row[field] == "true"


def test_two_comparator_summary_forbidden_side_effects_are_false() -> None:
    row = summary.load_and_validate_two_comparator_summary()

    for field in summary.FALSE_ONLY_FIELDS:
        assert row[field] == "false"


def test_compute_two_comparator_summary_metrics() -> None:
    metrics = summary.compute_two_comparator_summary_metrics(
        baseline=0.9,
        first_human_control=0.4,
        first_elephant_control=0.5,
        second_human_control=0.6,
        second_elephant_control=0.7,
        first_absolute_anchor_difference=0.1,
        second_absolute_anchor_difference=0.1,
    )

    assert metrics.human_control_mean_cosine_similarity == pytest.approx(0.5)
    assert metrics.elephant_control_mean_cosine_similarity == pytest.approx(0.6)
    assert metrics.all_control_mean_cosine_similarity == pytest.approx(0.55)
    assert metrics.minimum_control_cosine_similarity == pytest.approx(0.4)
    assert metrics.maximum_control_cosine_similarity == pytest.approx(0.7)
    assert metrics.control_cosine_similarity_range == pytest.approx(0.3)
    assert metrics.minimum_baseline_minus_control_delta == pytest.approx(0.2)
    assert metrics.maximum_baseline_minus_control_delta == pytest.approx(0.5)
    assert metrics.baseline_greater_than_all_four_controls is True
    assert metrics.anchor_ordering_consistent_across_comparators is True


def test_compute_rejects_cosine_outside_range() -> None:
    with pytest.raises(ValueError, match=r"\[-1, 1\]"):
        summary.compute_two_comparator_summary_metrics(
            baseline=0.9,
            first_human_control=1.1,
            first_elephant_control=0.5,
            second_human_control=0.6,
            second_elephant_control=0.7,
            first_absolute_anchor_difference=0.1,
            second_absolute_anchor_difference=0.1,
        )


def test_validator_rejects_aggregate_drift() -> None:
    row = summary.load_and_validate_two_comparator_summary()
    row["all_control_mean_cosine_similarity"] = "0.8000000000000000"

    with pytest.raises(
        ValueError,
        match="all_control_mean_cosine_similarity",
    ):
        summary.validate_two_comparator_summary_row(row)


def test_validator_rejects_new_similarity_computation() -> None:
    row = summary.load_and_validate_two_comparator_summary()
    row["new_similarity_computed"] = "true"

    with pytest.raises(ValueError, match="new_similarity_computed"):
        summary.validate_two_comparator_summary_row(row)


def test_validator_rejects_biological_claim() -> None:
    row = summary.load_and_validate_two_comparator_summary()
    row["biological_claim_made"] = "true"

    with pytest.raises(ValueError, match="biological_claim_made"):
        summary.validate_two_comparator_summary_row(row)
