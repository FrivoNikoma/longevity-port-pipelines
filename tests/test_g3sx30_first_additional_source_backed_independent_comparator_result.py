import numpy as np
import pytest

from longevity_port_pipelines.stages import (
    g3sx30_first_additional_source_backed_independent_comparator_result as result,
)


def test_additional_comparator_table_has_one_valid_row() -> None:
    row = result.load_and_validate_additional_comparator()

    assert row["result_created"] == "true"
    assert row["selection_rule_frozen_before_similarity"] == "true"
    assert row["similarity_used_for_selection"] == "false"
    assert row["selection_and_result_in_same_step"] == "true"


def test_additional_comparator_records_exact_selection() -> None:
    row = result.load_and_validate_additional_comparator()

    assert row["inventory_file_count"] == "216"
    assert row["source_backed_eligible_candidate_count"] == "101"
    assert row["selected_rank"] == "1"
    assert row["selected_comparator_reference_tier"] == "2"
    assert row["selected_comparator_taxid"] == "9606"
    assert row["selected_comparator_reuses_previous_comparator"] == "false"
    assert row["selected_comparator_artifact_reference"] == (result.EXPECTED_COMPARATOR_REFERENCE)


def test_additional_comparator_records_exact_provenance() -> None:
    row = result.load_and_validate_additional_comparator()

    assert row["selected_comparator_accession_tokens"] == "P12956|P13010"
    assert row["selected_comparator_pdb_token"] == "8bot"
    assert row["selected_comparator_reference_files"] == (
        "tests/test_analyze_saved_embeddings_mapped.py"
    )
    assert row["supplemental_provenance_file"] == (
        "docs/sirt6_mini_pilot_v2_candidate_selection.md"
    )
    assert row["supplemental_provenance_context_status"] == "v1_selected"
    assert row["supplemental_provenance_intermolecular_contacts"] == "732"
    assert row["supplemental_provenance_used_for_selection_ranking"] == "false"


def test_additional_comparator_records_exact_metrics() -> None:
    row = result.load_and_validate_additional_comparator()

    assert row["human_mdm2_to_additional_comparator_cosine_similarity"] == ("0.8095126148075514")
    assert row["elephant_mdm2_to_additional_comparator_cosine_similarity"] == ("0.8203721870665286")
    assert row["baseline_minus_human_additional_control_delta"] == ("0.1878188154263953")
    assert row["baseline_minus_elephant_additional_control_delta"] == ("0.1769592431674182")
    assert (
        row["human_additional_control_minus_elephant_additional_control_delta"]
        == "-0.0108595722589772"
    )
    assert row["absolute_human_elephant_additional_control_difference"] == "0.0108595722589772"


def test_additional_comparator_forbidden_side_effects_are_false() -> None:
    row = result.load_and_validate_additional_comparator()

    for field in result.FALSE_ONLY_FIELDS:
        assert row[field] == "false"


def test_compute_additional_comparator_supports_different_lengths() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)
    comparator = np.ones((642, 960), dtype=np.float32)

    metrics = result.compute_additional_comparator_metrics(
        human,
        elephant,
        comparator,
        baseline_human_elephant_mdm2_cosine_similarity=1.0,
    )

    assert metrics.human_mdm2_to_additional_comparator_cosine_similarity == (pytest.approx(1.0))
    assert metrics.elephant_mdm2_to_additional_comparator_cosine_similarity == (pytest.approx(1.0))
    assert metrics.baseline_minus_human_additional_control_delta == (pytest.approx(0.0))
    assert metrics.baseline_minus_elephant_additional_control_delta == (pytest.approx(0.0))
    assert metrics.baseline_greater_than_human_additional_control is False
    assert metrics.baseline_greater_than_elephant_additional_control is False
    assert metrics.absolute_human_elephant_additional_control_difference == (pytest.approx(0.0))


def test_compute_rejects_wrong_comparator_shape() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)
    comparator = np.ones((641, 960), dtype=np.float32)

    with pytest.raises(ValueError, match="Expected embedding shape"):
        result.compute_additional_comparator_metrics(
            human,
            elephant,
            comparator,
            baseline_human_elephant_mdm2_cosine_similarity=1.0,
        )


def test_compute_rejects_nonfinite_comparator() -> None:
    human = np.ones((491, 960), dtype=np.float32)
    elephant = np.ones((492, 960), dtype=np.float32)
    comparator = np.ones((642, 960), dtype=np.float32)
    comparator[0, 0] = np.nan

    with pytest.raises(ValueError, match="non-finite"):
        result.compute_additional_comparator_metrics(
            human,
            elephant,
            comparator,
            baseline_human_elephant_mdm2_cosine_similarity=1.0,
        )


def test_validator_rejects_selection_rule_drift() -> None:
    row = result.load_and_validate_additional_comparator()
    row["selection_rule_sha256"] = "0" * 64

    with pytest.raises(ValueError, match="selection_rule_sha256"):
        result.validate_additional_comparator_row(row)


def test_validator_rejects_biological_claim() -> None:
    row = result.load_and_validate_additional_comparator()
    row["biological_claim_made"] = "true"

    with pytest.raises(ValueError, match="biological_claim_made"):
        result.validate_additional_comparator_row(row)


def test_validator_rejects_metric_drift() -> None:
    row = result.load_and_validate_additional_comparator()
    row["baseline_minus_human_additional_control_delta"] = "0.1000000000000000"

    with pytest.raises(
        ValueError,
        match="baseline_minus_human_additional_control_delta",
    ):
        result.validate_additional_comparator_row(row)
