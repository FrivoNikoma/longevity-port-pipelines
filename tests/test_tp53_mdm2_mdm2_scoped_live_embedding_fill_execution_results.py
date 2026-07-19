import copy
from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_scoped_live_embedding_fill_execution_results as execution,
)

ROOT = Path(__file__).resolve().parents[1]


def load_result() -> list[dict[str, str]]:
    return execution.load_and_validate_result(ROOT)


def source_context() -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    str,
    str,
]:
    auth_rows, validation_rows = execution.load_authorization(ROOT)
    auth_sha = execution.authorization.file_sha256(ROOT / execution.authorization.AUTH_TABLE)
    validation_sha = execution.authorization.file_sha256(
        ROOT / execution.authorization.AUTH_VALIDATION
    )
    return auth_rows, validation_rows, auth_sha, validation_sha


def validate_mutation(
    rows: list[dict[str, str]],
) -> None:
    auth_rows, validation_rows, auth_sha, validation_sha = source_context()
    execution.validate_result_rows(
        rows,
        auth_rows=auth_rows,
        auth_validation_rows=validation_rows,
        auth_sha256=auth_sha,
        auth_validation_sha256=validation_sha,
    )


def test_exact_two_accessions_completed_in_order() -> None:
    rows = load_result()
    assert [row["target_accession"] for row in rows] == ["P23804", "A0ABM2YB85"]
    assert [row["execution_order"] for row in rows] == ["1", "2"]


def test_results_are_bound_to_authorization_tables() -> None:
    rows = load_result()
    auth_sha = execution.authorization.file_sha256(ROOT / execution.authorization.AUTH_TABLE)
    validation_sha = execution.authorization.file_sha256(
        ROOT / execution.authorization.AUTH_VALIDATION
    )

    assert {row["source_authorization_file_sha256"] for row in rows} == {auth_sha}
    assert {row["source_authorization_validation_file_sha256"] for row in rows} == {validation_sha}


def test_execution_remained_single_row_and_sequential() -> None:
    rows = load_result()
    for row in rows:
        assert row["max_live_batch_size"] == "1"
        assert row["live_invocation_count"] == "1"
        assert row["execution_mode"] == "sequential_one_accession_at_a_time"
        assert row["explicit_human_opt_in_confirmed"] == "true"


def test_pre_live_and_live_statuses_are_exact() -> None:
    rows = load_result()
    for row in rows:
        assert row["pre_live_single_dry_run_status"] == "dry_run_missing"
        assert row["pre_live_sequence_length_status"] == "matches"
        assert row["pre_live_embedding_exists"] == "false"
        assert row["skip_existing_used"] == "true"
        assert row["live_status"] == "live_completed"
        assert row["biohub_called"] == "true"
        assert row["esmc_called"] == "true"
        assert row["embedding_generated"] == "true"


def test_immediate_and_follow_up_audits_passed() -> None:
    rows = load_result()
    expected_shapes = {
        "P23804": "489x960",
        "A0ABM2YB85": "510x960",
    }

    for row in rows:
        assert row["embedding_shape"] == expected_shapes[row["target_accession"]]
        assert row["embedding_dtype"] == "float32"
        assert row["embedding_numeric"] == "true"
        assert row["embedding_finite"] == "true"
        assert row["embedding_sequence_length_matches"] == "true"
        assert row["follow_up_single_dry_run_status"] == "dry_run_present"
        assert row["follow_up_preflight_status"] == "present_valid"
        assert row["local_embedding_status"] == "present_valid"


def test_embedding_hashes_are_fixed() -> None:
    rows = load_result()
    expected_hashes = {
        accession: values["embedding_sha256"] for accession, values in execution.EXPECTED.items()
    }
    assert {row["target_accession"]: row["embedding_sha256"] for row in rows} == expected_hashes


def test_runtime_artifacts_remain_outside_git() -> None:
    rows = load_result()
    for row in rows:
        assert row["npy_artifact_created"] == "true"
        assert row["embedding_ignored"] == "true"
        assert row["embedding_tracked"] == "false"
        assert row["npy_artifact_committed"] == "false"
        assert row["data_output_artifact_committed"] == "false"
        assert row["external_evidence_committed"] == "false"


def test_panel_is_ready_only_for_scoped_contrast_dry_run() -> None:
    rows = load_result()
    for row in rows:
        assert (
            row["panel_local_prerequisites_status"]
            == "ready_both_scoped_mdm2_embeddings_present_valid"
        )
        assert row["allowed_next_action"] == "prepare_and_execute_scoped_mdm2_contrast_dry_run"
        assert row["tp53_status"] == "deferred_pending_source"
        assert row["aggregate_tp53_mdm2_lane_status"] == "closed_tp53_deferred_pending_source"


def test_downstream_and_claim_flags_remain_false() -> None:
    rows = load_result()
    for row in rows:
        for field in execution.FALSE_FIELDS:
            assert row[field] == "false"


def test_changed_embedding_hash_is_rejected() -> None:
    rows = load_result()
    bad = copy.deepcopy(rows)
    bad[0]["embedding_sha256"] = "0" * 64

    with pytest.raises(
        ValueError,
        match="embedding_sha256",
    ):
        validate_mutation(bad)


def test_committed_embedding_permission_is_rejected() -> None:
    rows = load_result()
    bad = copy.deepcopy(rows)
    bad[1]["npy_artifact_committed"] = "true"

    with pytest.raises(
        ValueError,
        match="npy_artifact_committed",
    ):
        validate_mutation(bad)


def test_schema_docs_and_protocol_record_checkpoint() -> None:
    schema = (ROOT / execution.RESULT_SCHEMA).read_text(encoding="utf-8")
    documentation = (
        ROOT / "docs/tp53_mdm2_mdm2_scoped_live_embedding_fill_execution_result.md"
    ).read_text(encoding="utf-8")
    protocol = (ROOT / "docs/controlled_embedding_fill_protocol.md").read_text(encoding="utf-8")

    assert "P23804" in schema
    assert "A0ABM2YB85" in schema
    assert "prepare_and_execute_scoped_mdm2_contrast_dry_run" in schema
    assert "23c92fc3" in documentation
    assert "36387d8c" in documentation
    assert "Completed scoped MDM2 execution checkpoint" in protocol
