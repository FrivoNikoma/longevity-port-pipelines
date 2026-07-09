from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_one_row_first_minimal_controlled_downstream_output as output,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TABLE = ROOT / output.DEFAULT_SOURCE_READ_CHECK_RESULT_TABLE
OUTPUT_TABLE = ROOT / output.DEFAULT_OUTPUT_TABLE


def test_first_minimal_controlled_downstream_output_table_has_one_valid_row() -> None:
    row = output.load_and_validate_output(OUTPUT_TABLE)

    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["output_status"] == "first_minimal_controlled_downstream_output_created"


def test_first_minimal_controlled_downstream_output_can_be_rebuilt_from_source() -> None:
    expected = output.load_source_and_build_output(SOURCE_TABLE)
    actual = output.load_and_validate_output(OUTPUT_TABLE)

    assert actual == expected


def test_first_minimal_controlled_downstream_output_consumes_passed_read_check() -> None:
    row = output.load_and_validate_output(OUTPUT_TABLE)

    assert row["source_read_check_result_table"] == (
        "data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv"
    )
    assert row["source_read_check_result_row_index"] == "1"
    assert row["source_read_check_action"] == (
        "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact"
    )
    assert row["source_read_check_status"] == "controlled_downstream_read_check_passed"
    assert row["source_controlled_handle_id"] == (
        "g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle"
    )
    assert row["source_controlled_input_status"] == (
        "one_row_ready_artifact_available_for_controlled_downstream_use"
    )


def test_first_minimal_controlled_downstream_output_records_identity_and_health() -> None:
    row = output.load_and_validate_output(OUTPUT_TABLE)

    assert row["output_action"] == (
        "add_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact"
    )
    assert row["output_type"] == "one_row_artifact_identity_and_embedding_health_summary"
    assert row["output_scope"] == "identity_and_embedding_health_only_no_biological_claim"
    assert row["candidate_identity_confirmed"] == "true"
    assert row["artifact_reference_confirmed"] == "true"
    assert row["embedding_health_confirmed"] == "true"
    assert row["source_embedding_shape"] == "492x960"
    assert row["source_embedding_dtype"] == "float32"
    assert row["source_embedding_finite"] == "true"
    assert row["source_sequence_length"] == "492"
    assert row["source_sequence_length_matches"] == "true"


def test_first_minimal_controlled_downstream_output_keeps_boundaries_false() -> None:
    row = output.load_and_validate_output(OUTPUT_TABLE)

    for field in [
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
        "data_output_artifact_committed",
        "biohub_esmc_called_by_output",
        "live_embedding_rerun_by_output",
        "embedding_generation_performed_by_output",
        "npy_artifact_created_by_output",
        "boltz_called",
        "af3_called",
        "chai_called",
        "enrichment_rerun",
        "contrast_rerun",
    ]:
        assert row[field] == "false"


def test_first_minimal_controlled_downstream_output_records_next_concrete_step() -> None:
    row = output.load_and_validate_output(OUTPUT_TABLE)

    assert row["next_step"] == (
        "move_toward_first_analysis_adjacent_controlled_output_or_next_concrete_"
        "biological_data_bearing_step_for_one_row_ready_g3sx30_artifact"
    )
    assert row["next_pr_should_be_concrete_analysis_adjacent_or_biological_data_bearing_step"] == (
        "true"
    )
    assert row["no_additional_non_result_layer_before_next_concrete_step"] == "true"


def test_first_minimal_controlled_downstream_output_rejects_failed_source_read_check() -> None:
    source = output.require_single_row(SOURCE_TABLE)
    bad = dict(source)
    bad["read_check_status"] = "controlled_downstream_read_check_failed"

    with pytest.raises(ValueError, match="read_check_status"):
        output.build_output_row_from_source_read_check(bad)


def test_first_minimal_controlled_downstream_output_rejects_unhealthy_source_embedding() -> None:
    source = output.require_single_row(SOURCE_TABLE)
    bad = dict(source)
    bad["embedding_finite"] = "false"

    with pytest.raises(ValueError, match="embedding_finite"):
        output.build_output_row_from_source_read_check(bad)


def test_first_minimal_controlled_downstream_output_rejects_gate_or_claim_promotion() -> None:
    row = output.require_single_row(OUTPUT_TABLE)

    for field in ["gate8_promoted", "gate9_promoted", "biological_claim_made"]:
        bad = dict(row)
        bad[field] = "true"

        with pytest.raises(ValueError, match=field):
            output.validate_output_row(bad)
