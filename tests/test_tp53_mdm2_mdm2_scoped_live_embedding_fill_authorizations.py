import copy
from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_scoped_live_embedding_fill_authorizations as authorization,
)

ROOT = Path(__file__).resolve().parents[1]


def load_authorization() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    return authorization.load_and_validate_committed_authorization(
        ROOT / authorization.AUTH_TABLE,
        ROOT / authorization.AUTH_VALIDATION,
        ROOT / authorization.SOURCE_MANIFEST,
        ROOT / authorization.SOURCE_VALIDATION,
    )


def source_rows() -> tuple[list[dict[str, str]], list[dict[str, str]], str, str]:
    manifest_path = ROOT / authorization.SOURCE_MANIFEST
    validation_path = ROOT / authorization.SOURCE_VALIDATION
    return (
        authorization.read_csv_rows(manifest_path),
        authorization.read_csv_rows(validation_path),
        authorization.file_sha256(manifest_path),
        authorization.file_sha256(validation_path),
    )


def test_exact_two_accessions_are_authorized() -> None:
    rows, _ = load_authorization()
    assert [row["target_accession"] for row in rows] == ["P23804", "A0ABM2YB85"]
    assert {row["allowed_live_accessions"] for row in rows} == {"P23804|A0ABM2YB85"}


def test_file_sha256_is_independent_of_line_endings(
    tmp_path: Path,
) -> None:
    lf_path = tmp_path / "lf.csv"
    crlf_path = tmp_path / "crlf.csv"

    lf_path.write_bytes(b"column_a,column_b\n1,2\n")
    crlf_path.write_bytes(b"column_a,column_b\r\n1,2\r\n")

    assert authorization.file_sha256(lf_path) == (authorization.file_sha256(crlf_path))


def test_source_contract_files_are_hash_bound() -> None:
    rows, _ = load_authorization()
    manifest_sha = authorization.file_sha256(ROOT / authorization.SOURCE_MANIFEST)
    validation_sha = authorization.file_sha256(ROOT / authorization.SOURCE_VALIDATION)
    assert {row["source_manifest_file_sha256"] for row in rows} == {manifest_sha}
    assert {row["source_validation_file_sha256"] for row in rows} == {validation_sha}


def test_identity_hash_length_and_paths_are_unchanged() -> None:
    rows, _ = load_authorization()
    for row in rows:
        expected = authorization.EXPECTED[row["target_accession"]]
        assert row["target_taxid"] == expected["taxid"]
        assert row["expected_sequence_length"] == expected["length"]
        assert row["exact_normalized_sequence_sha256"] == expected["sha"]
        assert row["expected_local_embedding_path"] == expected["path"]


def test_two_accessions_but_batch_size_one() -> None:
    rows, validation = load_authorization()
    for row in rows:
        assert row["authorized_accession_count"] == "2"
        assert row["max_live_batch_size"] == "1"
        assert row["required_runner"] == "curated_embedding_single"
        assert row["execution_order"] == "sequential_one_accession_at_a_time"
    assert {row["max_live_batch_size"] for row in validation} == {"1"}


def test_human_opt_in_and_pre_live_dry_run_are_required() -> None:
    rows, _ = load_authorization()
    for row in rows:
        assert row["explicit_human_opt_in_required"] == "true"
        assert row["human_opt_in_scope"] == "per_accession_per_invocation"
        assert row["pre_live_single_dry_run_required"] == "true"
        assert row["required_pre_live_status"] == "dry_run_missing"
        assert row["required_sequence_length_status"] == "matches"


def test_no_overwrite_policy_is_required() -> None:
    rows, _ = load_authorization()
    for row in rows:
        assert row["skip_existing_required"] == "true"
        assert row["overwrite_existing_allowed"] == "false"
        assert row["no_skip_existing_flag_allowed"] == "false"


def test_partial_failure_stops_execution() -> None:
    rows, _ = load_authorization()
    for row in rows:
        assert row["partial_failure_policy"] == "stop_after_first_failed_or_invalid_row"
        assert row["continue_after_live_failure"] == "false"
        assert row["continue_after_post_fill_audit_failure"] == "false"
        assert row["retry_requires_new_explicit_human_opt_in"] == "true"


def test_post_fill_audit_contract_is_exact() -> None:
    rows, _ = load_authorization()
    shapes = {"P23804": "489x960", "A0ABM2YB85": "510x960"}
    for row in rows:
        assert row["expected_post_fill_embedding_shape"] == shapes[row["target_accession"]]
        assert row["required_post_fill_dtype"] == "float32"
        assert row["required_post_fill_numeric"] == "true"
        assert row["required_post_fill_finite"] == "true"
        assert row["required_follow_up_single_dry_run_status"] == "dry_run_present"
        assert row["required_follow_up_preflight_status"] == "present_valid"


def test_authorization_is_effective_but_not_executed_here() -> None:
    rows, validation = load_authorization()
    for row in rows:
        assert row["authorization_effective"] == "true"
        assert row["live_fill_allowed"] == "true"
        assert row["fill_execution_allowed"] == "true"
        assert row["execution_performed_in_authorization_pr"] == "false"
    assert {row["execution_performed"] for row in validation} == {"false"}


def test_runtime_and_downstream_flags_remain_false() -> None:
    rows, validation = load_authorization()
    for row in rows:
        for field in authorization.AUTH_FALSE_FIELDS:
            assert row[field] == "false"
    for row in validation:
        for field in authorization.VALIDATION_FALSE_FIELDS:
            assert row[field] == "false"


def test_policy_only_validation_result() -> None:
    _, validation = load_authorization()
    for row in validation:
        assert row["authorization_validation_status"] == "passed_policy_only_validation"
        assert row["scoped_live_fill_authorization_status"] == "authorized_execution_contract_only"
        assert (
            row["allowed_next_action"] == "execute_scoped_live_fill_with_immediate_post_fill_audit"
        )


def test_batch_size_two_is_rejected() -> None:
    rows, _ = load_authorization()
    manifest, source_validation, manifest_sha, validation_sha = source_rows()
    bad = copy.deepcopy(rows)
    bad[0]["max_live_batch_size"] = "2"
    with pytest.raises(ValueError, match="max_live_batch_size"):
        authorization.validate_authorization_rows(
            bad, manifest, source_validation, manifest_sha, validation_sha
        )


def test_overwrite_permission_is_rejected() -> None:
    rows, _ = load_authorization()
    manifest, source_validation, manifest_sha, validation_sha = source_rows()
    bad = copy.deepcopy(rows)
    bad[0]["overwrite_existing_allowed"] = "true"
    with pytest.raises(ValueError, match="overwrite_existing_allowed"):
        authorization.validate_authorization_rows(
            bad, manifest, source_validation, manifest_sha, validation_sha
        )


def test_changed_source_hash_is_rejected() -> None:
    rows, _ = load_authorization()
    manifest, source_validation, _, validation_sha = source_rows()
    bad = copy.deepcopy(rows)
    bad[0]["source_manifest_file_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="source_manifest_file_sha256"):
        authorization.validate_authorization_rows(
            bad,
            manifest,
            source_validation,
            authorization.file_sha256(ROOT / authorization.SOURCE_MANIFEST),
            validation_sha,
        )


def test_protocol_records_narrow_mdm2_exception() -> None:
    text = (ROOT / "docs/controlled_embedding_fill_protocol.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Narrow MDM2-only technical authorization exception" in text
    assert "P23804" in text
    assert "A0ABM2YB85" in text
    assert "at most one live row at a time" in normalized
    assert "aggregate TP53/MDM2 lane remains closed" in normalized
