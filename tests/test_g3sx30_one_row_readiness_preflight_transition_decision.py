from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_one_row_readiness_preflight_transition_decision as decision,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RESULT_TABLE = ROOT / decision.DEFAULT_SOURCE_RESULT_TABLE
DECISION_TABLE = ROOT / decision.DEFAULT_DECISION_TABLE


def test_g3sx30_transition_decision_table_has_one_valid_row() -> None:
    row = decision.load_and_validate_decision(DECISION_TABLE)

    assert row["candidate_id"] == decision.EXPECTED_CANDIDATE_ID
    assert row["target_accession"] == "G3SX30"
    assert row["target_species"] == "Loxodonta africana"
    assert row["target_taxid"] == "9785"
    assert row["gene_symbol"] == "MDM2"


def test_g3sx30_transition_decision_can_be_rebuilt_from_source_result() -> None:
    expected = decision.load_source_result_and_build_decision(SOURCE_RESULT_TABLE)
    actual = decision.load_and_validate_decision(DECISION_TABLE)

    assert actual == expected


def test_g3sx30_transition_decision_records_source_pass() -> None:
    row = decision.load_and_validate_decision(DECISION_TABLE)

    assert row["source_result_table"] == (
        "data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv"
    )
    assert row["source_result_row_index"] == "1"
    assert row["source_check_name"] == "g3sx30_one_row_local_embedding_preflight_check"
    assert row["source_check_status"] == "local_preflight_pass"
    assert row["source_preflight_artifact_status"] == "local_artifact_preflight_passed"
    assert row["source_embedding_shape"] == "492x960"
    assert row["source_embedding_dtype"] == "float32"
    assert row["source_embedding_finite"] == "true"
    assert row["source_sequence_length_matches"] == "true"
    assert row["source_local_runtime_embedding_tracked"] == "false"
    assert row["source_local_runtime_embedding_committed"] == "false"


def test_g3sx30_transition_decision_records_final_decision_without_gate_promotion() -> None:
    row = decision.load_and_validate_decision(DECISION_TABLE)

    assert row["decision"] == "approve_one_row_readiness_preflight_transition_path"
    assert row["approved_for_next_transition_step"] == "true"
    assert row["ready_for_preflight"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"
    assert row["biological_claim_made"] == "false"
    assert row["allowed_next_action"] == ("run_one_row_g3sx30_readiness_preflight_transition")


def test_g3sx30_transition_decision_records_anti_loop_fields() -> None:
    row = decision.load_and_validate_decision(DECISION_TABLE)

    assert row["next_pr_must_be_actual_transition_check"] == "true"
    assert row["no_additional_decision_before_transition"] == "true"
    assert row["next_required_pr_title"] == "Run one-row G3SX30 readiness/preflight transition"
    assert "no additional decision, review, scaffold, or binding layer" in row["decision_note"]


def test_g3sx30_transition_decision_rejects_non_pass_source_result() -> None:
    source_result = decision.require_single_row(SOURCE_RESULT_TABLE)
    bad_row = dict(source_result)
    bad_row["check_status"] = "local_preflight_fail"

    with pytest.raises(ValueError, match="check_status"):
        decision.build_decision_row_from_source_result(bad_row)


def test_g3sx30_transition_decision_rejects_abstract_next_action() -> None:
    row = decision.require_single_row(DECISION_TABLE)
    bad_row = dict(row)
    bad_row["allowed_next_action"] = "prepare_another_transition_decision"

    with pytest.raises(ValueError, match="allowed_next_action"):
        decision.validate_decision_row(bad_row)


def test_g3sx30_transition_decision_rejects_missing_anti_loop_flags() -> None:
    row = decision.require_single_row(DECISION_TABLE)

    for field in [
        "next_pr_must_be_actual_transition_check",
        "no_additional_decision_before_transition",
    ]:
        bad_row = dict(row)
        bad_row[field] = "false"

        with pytest.raises(ValueError, match=field):
            decision.validate_decision_row(bad_row)


def test_g3sx30_transition_decision_rejects_ready_or_gate_promotion() -> None:
    row = decision.require_single_row(DECISION_TABLE)

    for field in [
        "ready_for_preflight",
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
    ]:
        bad_row = dict(row)
        bad_row[field] = "true"

        with pytest.raises(ValueError, match=field):
            decision.validate_decision_row(bad_row)


def test_g3sx30_transition_decision_forbidden_actions_cover_boundaries() -> None:
    row = decision.load_and_validate_decision(DECISION_TABLE)

    for forbidden in decision.FORBIDDEN_ACTIONS:
        assert forbidden in row["forbidden_actions"]
