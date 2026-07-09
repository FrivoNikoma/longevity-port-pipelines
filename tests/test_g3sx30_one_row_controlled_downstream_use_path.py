from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_one_row_controlled_downstream_use_path as downstream,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TRANSITION_TABLE = ROOT / downstream.DEFAULT_SOURCE_TRANSITION_RESULT_TABLE
DOWNSTREAM_TABLE = ROOT / downstream.DEFAULT_DOWNSTREAM_USE_PATH_TABLE


def test_downstream_use_path_table_has_one_valid_row() -> None:
    row = downstream.load_and_validate_downstream_use_path(DOWNSTREAM_TABLE)

    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["controlled_input_status"] == (
        "one_row_ready_artifact_available_for_controlled_downstream_use"
    )


def test_downstream_use_path_can_be_rebuilt_from_source_transition() -> None:
    expected = downstream.load_source_transition_and_build_downstream_use_path(
        SOURCE_TRANSITION_TABLE
    )
    actual = downstream.load_and_validate_downstream_use_path(DOWNSTREAM_TABLE)

    assert actual == expected


def test_downstream_use_path_consumes_ready_transition_result() -> None:
    row = downstream.load_and_validate_downstream_use_path(DOWNSTREAM_TABLE)

    assert row["source_transition_result_table"] == (
        "data/input/g3sx30_one_row_readiness_preflight_transition_results.csv"
    )
    assert row["source_transition_result_row_index"] == "1"
    assert row["source_transition_status"] == ("one_row_readiness_preflight_transition_passed")
    assert row["source_ready_for_preflight"] == "true"
    assert row["source_allowed_downstream_use_path"] == (
        "first_controlled_downstream_use_path_for_one_row_ready_artifact"
    )


def test_downstream_use_path_records_concrete_controlled_handle() -> None:
    row = downstream.load_and_validate_downstream_use_path(DOWNSTREAM_TABLE)

    assert row["controlled_downstream_use_path"] == (
        "first_controlled_downstream_use_path_for_one_row_ready_artifact"
    )
    assert row["controlled_handle_id"] == (
        "g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle"
    )
    assert row["one_row_only"] == "true"
    assert row["ready_scope"] == "one_row_g3sx30_elephant_mdm2_only"
    assert row["controlled_read_check_next_action"] == (
        "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact"
    )


def test_downstream_use_path_keeps_boundaries_false() -> None:
    row = downstream.load_and_validate_downstream_use_path(DOWNSTREAM_TABLE)

    for field in [
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
        "data_output_artifact_committed",
        "biohub_esmc_called_by_path_creation",
        "live_embedding_rerun_by_path_creation",
        "embedding_generation_performed_by_path_creation",
        "npy_artifact_created_by_path_creation",
        "boltz_called",
        "af3_called",
        "chai_called",
        "enrichment_rerun",
        "contrast_rerun",
    ]:
        assert row[field] == "false"


def test_downstream_use_path_rejects_source_not_ready_for_preflight() -> None:
    source = downstream.require_single_row(SOURCE_TRANSITION_TABLE)
    bad = dict(source)
    bad["ready_for_preflight"] = "false"

    with pytest.raises(ValueError, match="ready_for_preflight"):
        downstream.build_downstream_use_path_row_from_source_transition(bad)


def test_downstream_use_path_rejects_wrong_source_use_path() -> None:
    source = downstream.require_single_row(SOURCE_TRANSITION_TABLE)
    bad = dict(source)
    bad["allowed_downstream_use_path"] = "uncontrolled_downstream_use"

    with pytest.raises(ValueError, match="allowed_downstream_use_path"):
        downstream.build_downstream_use_path_row_from_source_transition(bad)


def test_downstream_use_path_rejects_gate_or_claim_promotion() -> None:
    row = downstream.require_single_row(DOWNSTREAM_TABLE)

    for field in ["gate8_promoted", "gate9_promoted", "biological_claim_made"]:
        bad = dict(row)
        bad[field] = "true"

        with pytest.raises(ValueError, match=field):
            downstream.validate_downstream_use_path_row(bad)


def test_downstream_use_path_records_anti_loop_rule() -> None:
    row = downstream.load_and_validate_downstream_use_path(DOWNSTREAM_TABLE)

    assert row["next_pr_must_be_actual_controlled_downstream_read_check"] == "true"
    assert row["no_additional_downstream_approval_before_read_check"] == "true"
