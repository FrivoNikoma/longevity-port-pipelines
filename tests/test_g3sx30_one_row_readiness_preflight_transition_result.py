from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_one_row_readiness_preflight_transition_result as transition,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DECISION_TABLE = ROOT / transition.DEFAULT_SOURCE_DECISION_TABLE
TRANSITION_RESULT_TABLE = ROOT / transition.DEFAULT_TRANSITION_RESULT_TABLE


def test_transition_result_table_has_one_valid_row() -> None:
    row = transition.load_and_validate_transition_result(TRANSITION_RESULT_TABLE)

    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["ready_for_preflight"] == "true"
    assert row["ready_scope"] == "one_row_g3sx30_elephant_mdm2_only"


def test_transition_result_can_be_rebuilt_from_source_decision() -> None:
    expected = transition.load_source_decision_and_build_transition_result(SOURCE_DECISION_TABLE)
    actual = transition.load_and_validate_transition_result(TRANSITION_RESULT_TABLE)

    assert actual == expected


def test_transition_result_consumes_final_decision_not_new_approval() -> None:
    row = transition.load_and_validate_transition_result(TRANSITION_RESULT_TABLE)

    assert row["source_decision"] == "approve_one_row_readiness_preflight_transition_path"
    assert row["source_approved_for_next_transition_step"] == "true"
    assert row["source_allowed_next_action"] == (
        "run_one_row_g3sx30_readiness_preflight_transition"
    )
    assert row["source_next_pr_must_be_actual_transition_check"] == "true"
    assert row["source_no_additional_decision_before_transition"] == "true"


def test_transition_result_records_actual_transition_and_one_row_ready() -> None:
    row = transition.load_and_validate_transition_result(TRANSITION_RESULT_TABLE)

    assert row["transition_action"] == "run_one_row_g3sx30_readiness_preflight_transition"
    assert row["transition_status"] == "one_row_readiness_preflight_transition_passed"
    assert row["one_row_only"] == "true"
    assert row["ready_for_preflight"] == "true"


def test_transition_result_keeps_boundaries_false() -> None:
    row = transition.load_and_validate_transition_result(TRANSITION_RESULT_TABLE)

    for field in [
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
        "data_output_artifact_committed",
        "local_runtime_embedding_tracked",
        "local_runtime_embedding_committed",
        "biohub_esmc_called_by_transition",
        "live_embedding_rerun_by_transition",
        "embedding_generation_performed_by_transition",
        "npy_artifact_created_by_transition",
        "boltz_called",
        "af3_called",
        "chai_called",
        "enrichment_rerun",
        "contrast_rerun",
    ]:
        assert row[field] == "false"


def test_transition_result_rejects_unapproved_source_decision() -> None:
    source = transition.require_single_row(SOURCE_DECISION_TABLE)
    bad = dict(source)
    bad["approved_for_next_transition_step"] = "false"

    with pytest.raises(ValueError, match="approved_for_next_transition_step"):
        transition.build_transition_result_row_from_source_decision(bad)


def test_transition_result_rejects_wrong_next_action() -> None:
    source = transition.require_single_row(SOURCE_DECISION_TABLE)
    bad = dict(source)
    bad["allowed_next_action"] = "prepare_another_transition_approval"

    with pytest.raises(ValueError, match="allowed_next_action"):
        transition.build_transition_result_row_from_source_decision(bad)


def test_transition_result_rejects_gate_or_claim_promotion() -> None:
    row = transition.require_single_row(TRANSITION_RESULT_TABLE)

    for field in ["gate8_promoted", "gate9_promoted", "biological_claim_made"]:
        bad = dict(row)
        bad[field] = "true"

        with pytest.raises(ValueError, match=field):
            transition.validate_transition_result_row(bad)
