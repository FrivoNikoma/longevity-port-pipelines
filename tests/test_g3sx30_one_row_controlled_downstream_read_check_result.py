from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_one_row_controlled_downstream_read_check_result as read_check,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TABLE = ROOT / read_check.DEFAULT_SOURCE_DOWNSTREAM_USE_PATH_TABLE
RESULT_TABLE = ROOT / read_check.DEFAULT_READ_CHECK_RESULT_TABLE


def test_controlled_downstream_read_check_result_table_has_one_valid_row() -> None:
    row = read_check.load_and_validate_read_check_result(RESULT_TABLE)

    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["read_check_status"] == "controlled_downstream_read_check_passed"


def test_controlled_downstream_read_check_result_can_be_rebuilt_from_source() -> None:
    expected = read_check.load_source_and_build_read_check_result(SOURCE_TABLE)
    actual = read_check.load_and_validate_read_check_result(RESULT_TABLE)

    assert actual == expected


def test_controlled_downstream_read_check_consumes_existing_handle() -> None:
    row = read_check.load_and_validate_read_check_result(RESULT_TABLE)

    assert row["source_downstream_use_path_table"] == (
        "data/input/g3sx30_one_row_controlled_downstream_use_paths.csv"
    )
    assert row["source_downstream_use_path_row_index"] == "1"
    assert row["source_controlled_downstream_use_path"] == (
        "first_controlled_downstream_use_path_for_one_row_ready_artifact"
    )
    assert row["source_controlled_handle_id"] == (
        "g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle"
    )
    assert row["source_next_pr_must_be_actual_controlled_downstream_read_check"] == "true"
    assert row["source_no_additional_downstream_approval_before_read_check"] == "true"
    assert row["source_next_step"] == (
        "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact"
    )


def test_controlled_downstream_read_check_records_actual_local_artifact_check() -> None:
    row = read_check.load_and_validate_read_check_result(RESULT_TABLE)

    assert row["read_check_action"] == (
        "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact"
    )
    assert row["read_check_status"] == "controlled_downstream_read_check_passed"
    assert row["source_ready_artifact_reference"] == (
        "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
    )
    assert row["local_runtime_embedding_exists"] == "true"
    assert row["local_runtime_embedding_tracked"] == "false"
    assert row["local_runtime_embedding_committed"] == "false"
    assert row["git_ignore_rule_status"] == "data_output_ignored"
    assert row["embedding_shape"] == "492x960"
    assert row["embedding_dtype"] == "float32"
    assert row["embedding_finite"] == "true"
    assert row["sequence_length"] == "492"
    assert row["sequence_length_matches"] == "true"


def test_controlled_downstream_read_check_keeps_boundaries_false() -> None:
    row = read_check.load_and_validate_read_check_result(RESULT_TABLE)

    for field in [
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
        "data_output_artifact_committed",
        "biohub_esmc_called_by_read_check",
        "live_embedding_rerun_by_read_check",
        "embedding_generation_performed_by_read_check",
        "npy_artifact_created_by_read_check",
        "boltz_called",
        "af3_called",
        "chai_called",
        "enrichment_rerun",
        "contrast_rerun",
    ]:
        assert row[field] == "false"


def test_controlled_downstream_read_check_records_next_output_step() -> None:
    row = read_check.load_and_validate_read_check_result(RESULT_TABLE)

    assert row["next_step"] == (
        "move_toward_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact"
    )
    assert row["next_pr_should_move_toward_first_minimal_controlled_downstream_output"] == "true"
    assert row["no_additional_read_check_approval_before_output"] == "true"


def test_controlled_downstream_read_check_rejects_wrong_source_handle() -> None:
    source = read_check.require_single_row(SOURCE_TABLE)
    bad = dict(source)
    bad["controlled_handle_id"] = "wrong_handle"

    with pytest.raises(ValueError, match="controlled_handle_id"):
        read_check.build_read_check_result_row_from_source(
            bad,
            artifact_observation={
                "local_runtime_embedding_exists": "true",
                "local_runtime_embedding_tracked": "false",
                "local_runtime_embedding_committed": "false",
                "git_ignore_rule_status": "data_output_ignored",
                "embedding_shape": "492x960",
                "embedding_dtype": "float32",
                "embedding_finite": "true",
                "sequence_length": "492",
                "sequence_length_matches": "true",
            },
        )


def test_controlled_downstream_read_check_rejects_non_finite_observation() -> None:
    source = read_check.require_single_row(SOURCE_TABLE)

    with pytest.raises(ValueError, match="embedding_finite"):
        read_check.build_read_check_result_row_from_source(
            source,
            artifact_observation={
                "local_runtime_embedding_exists": "true",
                "local_runtime_embedding_tracked": "false",
                "local_runtime_embedding_committed": "false",
                "git_ignore_rule_status": "data_output_ignored",
                "embedding_shape": "492x960",
                "embedding_dtype": "float32",
                "embedding_finite": "false",
                "sequence_length": "492",
                "sequence_length_matches": "true",
            },
        )


def test_controlled_downstream_read_check_rejects_gate_or_claim_promotion() -> None:
    row = read_check.require_single_row(RESULT_TABLE)

    for field in ["gate8_promoted", "gate9_promoted", "biological_claim_made"]:
        bad = dict(row)
        bad[field] = "true"

        with pytest.raises(ValueError, match=field):
            read_check.validate_read_check_result_row(bad)
