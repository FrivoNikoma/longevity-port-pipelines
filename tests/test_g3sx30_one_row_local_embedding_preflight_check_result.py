from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_one_row_local_embedding_preflight_check_result as result,
)

ROOT = Path(__file__).resolve().parents[1]
BINDING_TABLE = ROOT / result.DEFAULT_BINDING_TABLE
RESULT_TABLE = ROOT / result.DEFAULT_RESULT_TABLE


def test_g3sx30_preflight_result_table_has_one_valid_row() -> None:
    row = result.load_and_validate_result(RESULT_TABLE)

    assert row["candidate_id"] == result.EXPECTED_CANDIDATE_ID
    assert row["target_accession"] == "G3SX30"
    assert row["target_species"] == "Loxodonta africana"
    assert row["target_taxid"] == "9785"
    assert row["gene_symbol"] == "MDM2"


def test_g3sx30_preflight_result_can_be_rebuilt_from_binding_row() -> None:
    expected = result.load_binding_and_build_result(BINDING_TABLE)
    actual = result.load_and_validate_result(RESULT_TABLE)

    assert actual == expected


def test_g3sx30_preflight_result_records_local_artifact_pass() -> None:
    row = result.load_and_validate_result(RESULT_TABLE)

    assert row["check_name"] == "g3sx30_one_row_local_embedding_preflight_check"
    assert row["check_status"] == "local_preflight_pass"
    assert row["local_embedding_path"] == result.EXPECTED_LOCAL_EMBEDDING_PATH
    assert row["artifact_location"] == "local_runtime_data_output_ignored_by_git"
    assert row["local_runtime_embedding_exists"] == "true"
    assert row["local_runtime_embedding_tracked"] == "false"
    assert row["local_runtime_embedding_committed"] == "false"
    assert row["git_ignore_rule_status"] == "data_output_ignored"
    assert row["embedding_shape"] == "492x960"
    assert row["embedding_dtype"] == "float32"
    assert row["embedding_finite"] == "true"
    assert row["sequence_length"] == "492"
    assert row["sequence_length_matches"] == "true"


def test_g3sx30_preflight_result_records_no_side_effects() -> None:
    row = result.load_and_validate_result(RESULT_TABLE)

    for field in [
        "biohub_esmc_called_by_check",
        "live_embedding_rerun_by_check",
        "embedding_generation_performed_by_check",
        "npy_artifact_created_by_check",
        "data_output_artifact_committed",
        "external_validation_json_committed",
        "ready_for_preflight_promoted",
        "gate8_promoted",
        "gate9_promoted",
        "boltz_called",
        "af3_called",
        "chai_called",
        "enrichment_rerun",
        "contrast_rerun",
        "biological_claim_made",
        "downstream_gate_unlocked",
    ]:
        assert row[field] == "false"


def test_g3sx30_preflight_result_records_next_practical_decision() -> None:
    row = result.load_and_validate_result(RESULT_TABLE)

    assert (
        row["next_practical_decision"]
        == "approve_one_row_readiness_preflight_transition_path_or_repair_concrete_blocker"
    )
    assert row["pass_decision_path"] == "approve_one_row_readiness_preflight_transition_path"
    assert row["fail_decision_path"] == "repair_concrete_local_preflight_blocker"


def test_g3sx30_preflight_result_rejects_failed_status() -> None:
    row = result.require_single_row(RESULT_TABLE)
    bad_row = dict(row)
    bad_row["check_status"] = "local_preflight_fail"

    with pytest.raises(ValueError, match="check_status"):
        result.validate_result_row(bad_row)


def test_g3sx30_preflight_result_rejects_ready_or_gate_promotion() -> None:
    row = result.require_single_row(RESULT_TABLE)

    for field in [
        "ready_for_preflight_promoted",
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
        "downstream_gate_unlocked",
    ]:
        bad_row = dict(row)
        bad_row[field] = "true"

        with pytest.raises(ValueError, match=field):
            result.validate_result_row(bad_row)


def test_g3sx30_preflight_result_rejects_runtime_side_effects() -> None:
    row = result.require_single_row(RESULT_TABLE)

    for field in [
        "biohub_esmc_called_by_check",
        "live_embedding_rerun_by_check",
        "embedding_generation_performed_by_check",
        "npy_artifact_created_by_check",
        "data_output_artifact_committed",
        "external_validation_json_committed",
        "boltz_called",
        "af3_called",
        "chai_called",
        "enrichment_rerun",
        "contrast_rerun",
    ]:
        bad_row = dict(row)
        bad_row[field] = "true"

        with pytest.raises(ValueError, match=field):
            result.validate_result_row(bad_row)


def test_g3sx30_preflight_result_forbidden_actions_cover_boundaries() -> None:
    row = result.load_and_validate_result(RESULT_TABLE)

    for forbidden in result.FORBIDDEN_ACTIONS:
        assert forbidden in row["forbidden_actions"]
