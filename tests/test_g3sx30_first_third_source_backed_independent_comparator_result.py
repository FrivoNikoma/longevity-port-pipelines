import numpy as np
import pytest

from longevity_port_pipelines.stages import (
    g3sx30_first_third_source_backed_independent_comparator_result as result,
)


def test_third_comparator_table_has_one_valid_row() -> None:
    row = result.load_and_validate_third_comparator()

    assert row["result_created"] == "true"
    assert row["selection_rule_frozen_before_similarity"] == "true"
    assert row["similarity_used_for_selection"] == "false"
    assert row["selection_and_result_in_same_step"] == "true"


def test_third_comparator_records_inventory_and_selection() -> None:
    row = result.load_and_validate_third_comparator()

    assert row["historical_inventory_file_count"] == "216"
    assert row["current_inventory_file_count"] == "216"
    assert row["inventory_file_count_delta"] == "0"
    assert row["source_backed_eligible_candidate_count"] == "94"
    assert row["selected_rank"] == "1"
    assert row["selected_comparator_artifact_reference"] == (result.EXPECTED_COMPARATOR_REFERENCE)
    assert row["selected_comparator_reference_tier"] == "3"
    assert row["selected_comparator_taxid"] == "9606"
    assert row["selected_comparator_ignored"] == "true"
    assert row["selected_comparator_tracked"] == "false"
    assert row["selected_comparator_staged"] == "false"


def test_third_comparator_records_provenance_boundary() -> None:
    row = result.load_and_validate_third_comparator()

    assert row["selected_comparator_pdb_token"] == "7s68"
    assert row["selected_comparator_accession_tokens"] == "P09874"
    assert row["post_selection_exact_complex_match_count"] == "26"
    assert row["exact_artifact_path_reference_found"] == "false"
    assert row["exact_artifact_basename_reference_found"] == "false"
    assert row["complex_role_accession_taxid_context_confirmed"] == "true"
    assert row["exact_embedding_byte_provenance_confirmed"] == "false"
    assert row["exact_sequence_hash_provenance_confirmed"] == "false"
    assert row["supplemental_provenance_source_accession"] == "P09874"
    assert row["supplemental_provenance_partner_accession"] == "P09874"
    assert row["supplemental_provenance_intermolecular_contacts"] == "50"
    assert row["supplemental_provenance_used_for_selection_ranking"] == "false"


def test_third_comparator_records_exact_metrics() -> None:
    row = result.load_and_validate_third_comparator()

    assert row["human_mdm2_to_third_comparator_cosine_similarity"] == ("0.7472839682873271")
    assert row["elephant_mdm2_to_third_comparator_cosine_similarity"] == ("0.7516055327169140")
    assert row["baseline_minus_human_third_control_delta"] == ("0.2500474619466196")
    assert row["baseline_minus_elephant_third_control_delta"] == ("0.2457258975170328")
    assert row["absolute_human_elephant_third_control_difference"] == ("0.0043215644295869")


def test_third_comparator_forbidden_side_effects_are_false() -> None:
    row = result.load_and_validate_third_comparator()

    for field in result.FALSE_ONLY_FIELDS:
        assert row[field] == "false"


def test_compute_third_comparator_supports_different_lengths() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)
    comparator = np.ones((211, 960), dtype=np.float32)

    metrics = result.compute_third_comparator_metrics(
        human,
        elephant,
        comparator,
        baseline_human_elephant_mdm2_cosine_similarity=1.0,
    )

    assert metrics.human_mdm2_to_third_comparator_cosine_similarity == pytest.approx(1.0)
    assert metrics.elephant_mdm2_to_third_comparator_cosine_similarity == pytest.approx(1.0)
    assert metrics.baseline_minus_human_third_control_delta == pytest.approx(0.0)
    assert metrics.baseline_minus_elephant_third_control_delta == pytest.approx(0.0)
    assert metrics.baseline_greater_than_human_third_control is False
    assert metrics.baseline_greater_than_elephant_third_control is False
    assert metrics.absolute_human_elephant_third_control_difference == pytest.approx(0.0)


def test_compute_rejects_wrong_comparator_shape() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)
    comparator = np.ones((210, 960), dtype=np.float32)

    with pytest.raises(ValueError, match="Expected embedding shape"):
        result.compute_third_comparator_metrics(
            human,
            elephant,
            comparator,
            baseline_human_elephant_mdm2_cosine_similarity=1.0,
        )


def test_compute_rejects_nonfinite_comparator() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)
    comparator = np.ones((211, 960), dtype=np.float32)
    comparator[0, 0] = np.nan

    with pytest.raises(ValueError, match="non-finite"):
        result.compute_third_comparator_metrics(
            human,
            elephant,
            comparator,
            baseline_human_elephant_mdm2_cosine_similarity=1.0,
        )


def test_validator_rejects_selection_rule_drift() -> None:
    row = result.load_and_validate_third_comparator()
    row["selection_rule_sha256"] = "0" * 64

    with pytest.raises(ValueError, match="selection_rule_sha256"):
        result.validate_third_comparator_row(row)


def test_validator_rejects_provenance_overclaim() -> None:
    row = result.load_and_validate_third_comparator()
    row["exact_embedding_byte_provenance_confirmed"] = "true"

    with pytest.raises(ValueError, match="exact_embedding_byte_provenance_confirmed"):
        result.validate_third_comparator_row(row)


def test_validator_rejects_metric_drift() -> None:
    row = result.load_and_validate_third_comparator()
    row["baseline_minus_human_third_control_delta"] = "0.1000000000000000"

    with pytest.raises(
        ValueError,
        match="baseline_minus_human_third_control_delta",
    ):
        result.validate_third_comparator_row(row)
