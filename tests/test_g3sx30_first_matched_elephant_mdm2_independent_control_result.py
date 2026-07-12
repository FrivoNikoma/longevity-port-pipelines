import numpy as np
import pytest

from longevity_port_pipelines.stages import (
    g3sx30_first_matched_elephant_mdm2_independent_control_result as control,
)


def test_matched_control_table_has_one_valid_row() -> None:
    row = control.load_and_validate_matched_control()

    assert row["matched_control_result_created"] == "true"
    assert row["comparator_reselected"] == "false"
    assert row["comparator_remained_frozen"] == "true"


def test_matched_control_records_exact_metrics() -> None:
    row = control.load_and_validate_matched_control()

    assert row["elephant_mdm2_to_frozen_comparator_cosine_similarity"] == ("0.8409825967886765")
    assert row["baseline_minus_elephant_control_delta"] == ("0.1563488334452703")
    assert row["human_control_minus_elephant_control_delta"] == ("-0.0093635408405441")
    assert row["absolute_human_elephant_control_similarity_difference"] == ("0.0093635408405441")


def test_matched_control_reuses_exact_frozen_comparator() -> None:
    row = control.load_and_validate_matched_control()

    assert row["frozen_comparator_source_accession"] == "P09874"
    assert row["frozen_comparator_target_accession"] == "EPQ16369.1"
    assert row["frozen_comparator_taxid"] == "109478"
    assert row["frozen_comparator_artifact_reference"] == (control.EXPECTED_COMPARATOR_REFERENCE)


def test_matched_control_forbidden_side_effects_are_false() -> None:
    row = control.load_and_validate_matched_control()

    for field in control.FALSE_ONLY_FIELDS:
        assert row[field] == "false"


def test_compute_matched_control_metrics_supports_different_lengths() -> None:
    elephant = np.ones((492, 960), dtype=np.float32)
    comparator = np.ones((1024, 960), dtype=np.float32)

    metrics = control.compute_matched_control_metrics(
        elephant,
        comparator,
        baseline_human_elephant_mdm2_cosine_similarity=1.0,
        human_mdm2_to_frozen_comparator_cosine_similarity=1.0,
    )

    assert metrics.elephant_mdm2_to_frozen_comparator_cosine_similarity == (pytest.approx(1.0))
    assert metrics.baseline_minus_elephant_control_delta == pytest.approx(0.0)
    assert metrics.baseline_greater_than_elephant_control is False
    assert metrics.human_control_minus_elephant_control_delta == (pytest.approx(0.0))
    assert metrics.absolute_human_elephant_control_similarity_difference == pytest.approx(0.0)


def test_compute_matched_control_rejects_wrong_elephant_shape() -> None:
    elephant = np.ones((491, 960), dtype=np.float32)
    comparator = np.ones((1024, 960), dtype=np.float32)

    with pytest.raises(ValueError, match="Expected embedding shape"):
        control.compute_matched_control_metrics(
            elephant,
            comparator,
            baseline_human_elephant_mdm2_cosine_similarity=1.0,
            human_mdm2_to_frozen_comparator_cosine_similarity=1.0,
        )


def test_compute_matched_control_rejects_nonfinite_comparator() -> None:
    elephant = np.ones((492, 960), dtype=np.float32)
    comparator = np.ones((1024, 960), dtype=np.float32)
    comparator[0, 0] = np.nan

    with pytest.raises(ValueError, match="non-finite"):
        control.compute_matched_control_metrics(
            elephant,
            comparator,
            baseline_human_elephant_mdm2_cosine_similarity=1.0,
            human_mdm2_to_frozen_comparator_cosine_similarity=1.0,
        )


def test_validator_rejects_comparator_path_drift() -> None:
    row = control.load_and_validate_matched_control()
    row["frozen_comparator_artifact_reference"] = "data/output/other.npy"

    with pytest.raises(ValueError, match="frozen_comparator_artifact_reference"):
        control.validate_matched_control_row(row)


def test_validator_rejects_biological_claim() -> None:
    row = control.load_and_validate_matched_control()
    row["biological_claim_made"] = "true"

    with pytest.raises(ValueError, match="biological_claim_made"):
        control.validate_matched_control_row(row)


def test_validator_rejects_metric_drift() -> None:
    row = control.load_and_validate_matched_control()
    row["baseline_minus_elephant_control_delta"] = "0.1000000000000000"

    with pytest.raises(ValueError, match="baseline_minus_elephant_control_delta"):
        control.validate_matched_control_row(row)
