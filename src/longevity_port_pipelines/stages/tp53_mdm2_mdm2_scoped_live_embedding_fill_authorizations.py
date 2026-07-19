"""Scoped TP53/MDM2 live embedding fill authorization contract.

This is policy and metadata only. It performs no BioHub/ESMC call, embedding
creation, data/output write, contrast, gate promotion, or biological claim.
"""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

SOURCE_MANIFEST = Path("data/input/tp53_mdm2_mdm2_missing_embedding_fill_manifest.csv")
SOURCE_VALIDATION = Path(
    "data/input/tp53_mdm2_mdm2_missing_embedding_fill_manifest_validation_results.csv"
)
AUTH_TABLE = Path("data/input/tp53_mdm2_mdm2_scoped_live_embedding_fill_authorizations.csv")
AUTH_VALIDATION = Path(
    "data/input/tp53_mdm2_mdm2_scoped_live_embedding_fill_authorization_validation_results.csv"
)

ALLOWED_LIVE_ACCESSIONS = "P23804|A0ABM2YB85"
ALLOWED_MODEL = "esmc-300m-2024-12"
REQUIRED_RUNNER = "curated_embedding_single"
REQUIRED_LIVE_FLAG = "--yes-live"
ALLOWED_NEXT_ACTION = "execute_scoped_live_fill_with_immediate_post_fill_audit"

EXPECTED = {
    "P23804": {
        "species": "mouse",
        "taxid": "10090",
        "db": "UniProtKB Swiss-Prot",
        "length": "489",
        "sha": "0841e7c8ebd6a4a9e9e051538600d8f201c6682b3246dfb95ba301ab6233a3e3",
        "path": "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_10090.npy",
        "shape": "489x960",
    },
    "A0ABM2YB85": {
        "species": "hamster",
        "taxid": "10036",
        "db": "UniProtKB TrEMBL and NCBI RefSeq",
        "length": "510",
        "sha": "77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5",
        "path": "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_10036.npy",
        "shape": "510x960",
    },
}
AUTH_FIELDS = [
    "authorization_contract_version",
    "candidate_set",
    "lane_name",
    "candidate_id",
    "gene_symbol",
    "target_species",
    "target_taxid",
    "target_accession",
    "target_accession_db",
    "expected_sequence_length",
    "exact_normalized_sequence_sha256",
    "source_manifest_table",
    "source_manifest_file_sha256",
    "source_manifest_row_index",
    "source_validation_table",
    "source_validation_file_sha256",
    "source_validation_row_index",
    "source_manifest_row_validation_status",
    "source_manifest_status",
    "source_external_binding_status",
    "source_sequence_hash_binding_status",
    "source_local_prerequisite_status",
    "source_embedding_artifact_status",
    "source_authorization_status",
    "source_live_fill_allowed",
    "source_fill_execution_allowed",
    "expected_local_embedding_path",
    "allowed_live_accessions",
    "authorized_accession_count",
    "allowed_model",
    "required_runner",
    "required_live_flag",
    "explicit_human_opt_in_required",
    "human_opt_in_scope",
    "max_live_batch_size",
    "execution_order",
    "authorization_scope",
    "authorization_status",
    "authorization_effective",
    "live_fill_allowed",
    "fill_execution_allowed",
    "combined_live_fill_post_fill_audit_pr_allowed",
    "pre_live_single_dry_run_required",
    "required_pre_live_status",
    "required_sequence_length_status",
    "required_embedding_exists_before_live",
    "skip_existing_required",
    "overwrite_existing_allowed",
    "no_skip_existing_flag_allowed",
    "existing_target_behavior",
    "partial_failure_policy",
    "continue_after_live_failure",
    "continue_after_post_fill_audit_failure",
    "successful_prior_artifact_policy",
    "failed_or_invalid_artifact_policy",
    "automatic_rollback_of_valid_prior_row",
    "retry_requires_new_explicit_human_opt_in",
    "expected_post_fill_embedding_shape",
    "required_post_fill_dtype",
    "required_post_fill_numeric",
    "required_post_fill_finite",
    "required_post_fill_sequence_length_match",
    "required_follow_up_single_dry_run_status",
    "required_follow_up_preflight_status",
    "generated_artifact_must_remain_untracked",
    "generated_artifact_commit_allowed",
    "data_output_commit_allowed",
    "contrast_after_fill_automatic",
    "gate8_entry_after_fill_automatic",
    "gate8_promotion_after_fill_automatic",
    "gate9_promotion_after_fill_automatic",
    "biological_claim_after_fill_automatic",
    "allowed_next_action",
    "execution_performed_in_authorization_pr",
    "biohub_called",
    "esmc_called",
    "embedding_generated",
    "npy_artifact_created",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "contrast_run",
    "gate8_entry_allowed_in_authorization_pr",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "claim_policy",
    "claim_status",
    "authorization_note",
]
VALIDATION_FIELDS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "gene_symbol",
    "target_accession",
    "authorization_source_table",
    "authorization_row_index",
    "source_manifest_integrity_status",
    "source_validation_integrity_status",
    "accession_scope_validation_status",
    "identity_binding_validation_status",
    "path_binding_validation_status",
    "runner_policy_validation_status",
    "human_opt_in_policy_validation_status",
    "sequential_execution_policy_validation_status",
    "no_overwrite_policy_validation_status",
    "partial_failure_policy_validation_status",
    "post_fill_audit_policy_validation_status",
    "authorization_validation_status",
    "scoped_live_fill_authorization_status",
    "allowed_live_accessions",
    "max_live_batch_size",
    "authorization_effective",
    "live_fill_allowed",
    "fill_execution_allowed",
    "execution_performed",
    "allowed_next_action",
    "panel_runtime_blocker_code",
    "biohub_called",
    "esmc_called",
    "embedding_generated",
    "npy_artifact_created",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "contrast_run",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "claim_policy",
    "claim_status",
    "validation_note",
]

AUTH_FALSE_FIELDS = (
    "overwrite_existing_allowed",
    "no_skip_existing_flag_allowed",
    "continue_after_live_failure",
    "continue_after_post_fill_audit_failure",
    "automatic_rollback_of_valid_prior_row",
    "generated_artifact_commit_allowed",
    "data_output_commit_allowed",
    "contrast_after_fill_automatic",
    "gate8_entry_after_fill_automatic",
    "gate8_promotion_after_fill_automatic",
    "gate9_promotion_after_fill_automatic",
    "biological_claim_after_fill_automatic",
    "execution_performed_in_authorization_pr",
    "biohub_called",
    "esmc_called",
    "embedding_generated",
    "npy_artifact_created",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "contrast_run",
    "gate8_entry_allowed_in_authorization_pr",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
)
VALIDATION_FALSE_FIELDS = (
    "execution_performed",
    "biohub_called",
    "esmc_called",
    "embedding_generated",
    "npy_artifact_created",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "contrast_run",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
)
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path: Path) -> str:
    """Return a cross-platform canonical UTF-8/LF text SHA-256."""
    text = path.read_text(encoding="utf-8-sig")
    canonical_text = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()


def require(row: dict[str, str], field: str, expected: str) -> None:
    actual = row.get(field, "").strip()
    if actual != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")


def unique_row(rows: list[dict[str, str]], accession: str) -> tuple[int, dict[str, str]]:
    matches = [
        (i, row) for i, row in enumerate(rows, start=1) if row.get("target_accession") == accession
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {accession}, found {len(matches)}")
    return matches[0]


def validate_path(value: str, expected: str) -> None:
    path = Path(value)
    if (
        value != expected
        or path.is_absolute()
        or WINDOWS_ABSOLUTE.match(value)
        or "\\" in value
        or ".." in path.parts
        or not value.startswith("data/output/embeddings/esmc-300m-2024-12/")
        or path.suffix != ".npy"
    ):
        raise ValueError(f"Invalid canonical embedding path: {value!r}")


def validate_sources(
    manifest_rows: list[dict[str, str]], validation_rows: list[dict[str, str]]
) -> None:
    expected_order = ["P23804", "A0ABM2YB85"]
    if [row.get("target_accession") for row in manifest_rows] != expected_order:
        raise ValueError("Source manifest scope changed")
    if [row.get("target_accession") for row in validation_rows] != expected_order:
        raise ValueError("Source validation scope changed")
    for accession in expected_order:
        expected = EXPECTED[accession]
        _, manifest = unique_row(manifest_rows, accession)
        _, validation = unique_row(validation_rows, accession)
        require(manifest, "gene_symbol", "MDM2")
        require(manifest, "target_species", expected["species"])
        require(manifest, "target_taxid", expected["taxid"])
        require(manifest, "target_accession_db", expected["db"])
        require(manifest, "expected_sequence_length", expected["length"])
        require(manifest, "exact_normalized_sequence_sha256", expected["sha"])
        require(manifest, "external_binding_status", "passed_exact_external_non_committed_binding")
        require(manifest, "local_prerequisite_status", "missing")
        require(manifest, "existing_local_embedding_status", "missing")
        require(manifest, "existing_local_embedding_exists", "false")
        require(manifest, "embedding_model", ALLOWED_MODEL)
        validate_path(manifest["expected_local_embedding_path"], expected["path"])
        require(manifest, "authorization_status", "pending_explicit_scoped_live_fill_authorization")
        require(manifest, "live_fill_allowed", "false")
        require(manifest, "fill_execution_allowed", "false")
        require(manifest, "allowed_next_action", "request_explicit_scoped_live_fill_authorization")
        require(validation, "manifest_row_validation_status", "passed")
        require(
            validation,
            "external_binding_validation_status",
            "passed_exact_external_non_committed_binding",
        )
        require(validation, "sequence_hash_binding_status", "passed_exact_hash_bound")
        require(validation, "local_prerequisite_validation_status", "passed_missing_embedding")
        require(validation, "embedding_artifact_status", "missing_not_created")
        require(validation, "manifest_validation_status", "passed_table_only_validation")
        require(
            validation,
            "scoped_missing_embedding_fill_manifest_status",
            "prepared_execution_contract_only",
        )
        require(validation, "validated_manifest_accessions", ALLOWED_LIVE_ACCESSIONS)


def build_authorization_rows(
    manifest_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    manifest_sha: str,
    validation_sha: str,
) -> list[dict[str, str]]:
    validate_sources(manifest_rows, validation_rows)
    rows: list[dict[str, str]] = []
    for accession in ("P23804", "A0ABM2YB85"):
        expected = EXPECTED[accession]
        manifest_index, manifest = unique_row(manifest_rows, accession)
        validation_index, validation = unique_row(validation_rows, accession)
        rows.append(
            {
                "authorization_contract_version": "1",
                "candidate_set": manifest["candidate_set"],
                "lane_name": manifest["lane_name"],
                "candidate_id": manifest["candidate_id"],
                "gene_symbol": "MDM2",
                "target_species": expected["species"],
                "target_taxid": expected["taxid"],
                "target_accession": accession,
                "target_accession_db": expected["db"],
                "expected_sequence_length": expected["length"],
                "exact_normalized_sequence_sha256": expected["sha"],
                "source_manifest_table": SOURCE_MANIFEST.as_posix(),
                "source_manifest_file_sha256": manifest_sha,
                "source_manifest_row_index": str(manifest_index),
                "source_validation_table": SOURCE_VALIDATION.as_posix(),
                "source_validation_file_sha256": validation_sha,
                "source_validation_row_index": str(validation_index),
                "source_manifest_row_validation_status": validation[
                    "manifest_row_validation_status"
                ],
                "source_manifest_status": validation[
                    "scoped_missing_embedding_fill_manifest_status"
                ],
                "source_external_binding_status": validation["external_binding_validation_status"],
                "source_sequence_hash_binding_status": validation["sequence_hash_binding_status"],
                "source_local_prerequisite_status": validation[
                    "local_prerequisite_validation_status"
                ],
                "source_embedding_artifact_status": validation["embedding_artifact_status"],
                "source_authorization_status": manifest["authorization_status"],
                "source_live_fill_allowed": manifest["live_fill_allowed"],
                "source_fill_execution_allowed": manifest["fill_execution_allowed"],
                "expected_local_embedding_path": manifest["expected_local_embedding_path"],
                "allowed_live_accessions": ALLOWED_LIVE_ACCESSIONS,
                "authorized_accession_count": "2",
                "allowed_model": ALLOWED_MODEL,
                "required_runner": REQUIRED_RUNNER,
                "required_live_flag": REQUIRED_LIVE_FLAG,
                "explicit_human_opt_in_required": "true",
                "human_opt_in_scope": "per_accession_per_invocation",
                "max_live_batch_size": "1",
                "execution_order": "sequential_one_accession_at_a_time",
                "authorization_scope": "scoped_mdm2_missing_embeddings_only",
                "authorization_status": "explicit_scoped_live_fill_authorized",
                "authorization_effective": "true",
                "live_fill_allowed": "true",
                "fill_execution_allowed": "true",
                "combined_live_fill_post_fill_audit_pr_allowed": "true",
                "pre_live_single_dry_run_required": "true",
                "required_pre_live_status": "dry_run_missing",
                "required_sequence_length_status": "matches",
                "required_embedding_exists_before_live": "false",
                "skip_existing_required": "true",
                "overwrite_existing_allowed": "false",
                "no_skip_existing_flag_allowed": "false",
                "existing_target_behavior": "skip_without_live_call",
                "partial_failure_policy": "stop_after_first_failed_or_invalid_row",
                "continue_after_live_failure": "false",
                "continue_after_post_fill_audit_failure": "false",
                "successful_prior_artifact_policy": "retain_only_if_post_fill_audit_passes",
                "failed_or_invalid_artifact_policy": "quarantine_or_remove_before_retry",
                "automatic_rollback_of_valid_prior_row": "false",
                "retry_requires_new_explicit_human_opt_in": "true",
                "expected_post_fill_embedding_shape": expected["shape"],
                "required_post_fill_dtype": "float32",
                "required_post_fill_numeric": "true",
                "required_post_fill_finite": "true",
                "required_post_fill_sequence_length_match": "true",
                "required_follow_up_single_dry_run_status": "dry_run_present",
                "required_follow_up_preflight_status": "present_valid",
                "generated_artifact_must_remain_untracked": "true",
                "generated_artifact_commit_allowed": "false",
                "data_output_commit_allowed": "false",
                "contrast_after_fill_automatic": "false",
                "gate8_entry_after_fill_automatic": "false",
                "gate8_promotion_after_fill_automatic": "false",
                "gate9_promotion_after_fill_automatic": "false",
                "biological_claim_after_fill_automatic": "false",
                "allowed_next_action": ALLOWED_NEXT_ACTION,
                "execution_performed_in_authorization_pr": "false",
                "biohub_called": "false",
                "esmc_called": "false",
                "embedding_generated": "false",
                "npy_artifact_created": "false",
                "npy_artifact_committed": "false",
                "data_output_artifact_committed": "false",
                "contrast_run": "false",
                "gate8_entry_allowed_in_authorization_pr": "false",
                "gate8_promoted": "false",
                "gate9_promoted": "false",
                "biological_claim_made": "false",
                "claim_policy": "no_biological_claims_until_validation",
                "claim_status": "technical_authorization_contract",
                "authorization_note": (
                    f"{accession} is authorized for one controlled live invocation only after a same-row dry-run, "
                    "explicit human opt-in, and unchanged source-contract validation. Immediate post-fill audit is "
                    "required before any next accession."
                ),
            }
        )
    validate_authorization_rows(rows, manifest_rows, validation_rows, manifest_sha, validation_sha)
    return rows


def validate_authorization_rows(
    rows: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    manifest_sha: str,
    validation_sha: str,
) -> None:
    validate_sources(manifest_rows, validation_rows)
    if len(rows) != 2 or [row.get("target_accession") for row in rows] != ["P23804", "A0ABM2YB85"]:
        raise ValueError("Authorization scope must be exactly P23804 and A0ABM2YB85")
    for row in rows:
        if list(row) != AUTH_FIELDS:
            raise ValueError("Authorization fields or field order changed")
        accession = row["target_accession"]
        expected = EXPECTED[accession]
        require(row, "source_manifest_file_sha256", manifest_sha)
        require(row, "source_validation_file_sha256", validation_sha)
        require(row, "target_taxid", expected["taxid"])
        require(row, "expected_sequence_length", expected["length"])
        require(row, "exact_normalized_sequence_sha256", expected["sha"])
        validate_path(row["expected_local_embedding_path"], expected["path"])
        require(row, "allowed_live_accessions", ALLOWED_LIVE_ACCESSIONS)
        require(row, "authorized_accession_count", "2")
        require(row, "allowed_model", ALLOWED_MODEL)
        require(row, "required_runner", REQUIRED_RUNNER)
        require(row, "required_live_flag", REQUIRED_LIVE_FLAG)
        require(row, "explicit_human_opt_in_required", "true")
        require(row, "human_opt_in_scope", "per_accession_per_invocation")
        require(row, "max_live_batch_size", "1")
        require(row, "execution_order", "sequential_one_accession_at_a_time")
        require(row, "authorization_status", "explicit_scoped_live_fill_authorized")
        require(row, "authorization_effective", "true")
        require(row, "live_fill_allowed", "true")
        require(row, "fill_execution_allowed", "true")
        require(row, "pre_live_single_dry_run_required", "true")
        require(row, "required_pre_live_status", "dry_run_missing")
        require(row, "required_sequence_length_status", "matches")
        require(row, "required_embedding_exists_before_live", "false")
        require(row, "skip_existing_required", "true")
        require(row, "partial_failure_policy", "stop_after_first_failed_or_invalid_row")
        require(row, "retry_requires_new_explicit_human_opt_in", "true")
        require(row, "expected_post_fill_embedding_shape", expected["shape"])
        require(row, "required_post_fill_dtype", "float32")
        require(row, "required_follow_up_single_dry_run_status", "dry_run_present")
        require(row, "required_follow_up_preflight_status", "present_valid")
        require(row, "allowed_next_action", ALLOWED_NEXT_ACTION)
        for field in AUTH_FALSE_FIELDS:
            require(row, field, "false")


def build_validation_rows(auth_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, auth in enumerate(auth_rows, start=1):
        rows.append(
            {
                "candidate_set": auth["candidate_set"],
                "lane_name": auth["lane_name"],
                "candidate_id": auth["candidate_id"],
                "gene_symbol": "MDM2",
                "target_accession": auth["target_accession"],
                "authorization_source_table": AUTH_TABLE.as_posix(),
                "authorization_row_index": str(index),
                "source_manifest_integrity_status": "passed_canonical_utf8_lf_sha256_binding",
                "source_validation_integrity_status": "passed_canonical_utf8_lf_sha256_binding",
                "accession_scope_validation_status": "passed_exact_two_accession_scope",
                "identity_binding_validation_status": "passed_accession_taxid_length_hash_binding",
                "path_binding_validation_status": "passed_canonical_ignored_embedding_path_binding",
                "runner_policy_validation_status": "passed_single_row_runner_policy",
                "human_opt_in_policy_validation_status": "passed_per_accession_explicit_opt_in_policy",
                "sequential_execution_policy_validation_status": "passed_max_live_batch_size_one",
                "no_overwrite_policy_validation_status": "passed_skip_existing_no_overwrite_policy",
                "partial_failure_policy_validation_status": "passed_stop_on_first_failure_policy",
                "post_fill_audit_policy_validation_status": "passed_immediate_post_fill_audit_policy",
                "authorization_validation_status": "passed_policy_only_validation",
                "scoped_live_fill_authorization_status": "authorized_execution_contract_only",
                "allowed_live_accessions": ALLOWED_LIVE_ACCESSIONS,
                "max_live_batch_size": "1",
                "authorization_effective": "true",
                "live_fill_allowed": "true",
                "fill_execution_allowed": "true",
                "execution_performed": "false",
                "allowed_next_action": ALLOWED_NEXT_ACTION,
                "panel_runtime_blocker_code": "none_for_scoped_authorized_accessions",
                "biohub_called": "false",
                "esmc_called": "false",
                "embedding_generated": "false",
                "npy_artifact_created": "false",
                "npy_artifact_committed": "false",
                "data_output_artifact_committed": "false",
                "contrast_run": "false",
                "gate8_entry_allowed": "false",
                "gate8_promoted": "false",
                "gate9_promoted": "false",
                "biological_claim_made": "false",
                "claim_policy": "no_biological_claims_until_validation",
                "claim_status": "technical_authorization_contract",
                "validation_note": (
                    f"{auth['target_accession']} passes policy-only authorization validation. No execution occurs in "
                    "this PR; the future invocation must be single-row, explicitly opted in, no-overwrite, and "
                    "followed immediately by post-fill audit."
                ),
            }
        )
    validate_validation_rows(rows, auth_rows)
    return rows


def validate_validation_rows(rows: list[dict[str, str]], auth_rows: list[dict[str, str]]) -> None:
    if len(rows) != 2 or [row.get("target_accession") for row in rows] != ["P23804", "A0ABM2YB85"]:
        raise ValueError("Authorization validation scope changed")
    for index, row in enumerate(rows, start=1):
        if list(row) != VALIDATION_FIELDS:
            raise ValueError("Authorization validation fields or field order changed")
        require(auth_rows[index - 1], "target_accession", row["target_accession"])
        require(row, "authorization_row_index", str(index))
        require(row, "authorization_validation_status", "passed_policy_only_validation")
        require(row, "scoped_live_fill_authorization_status", "authorized_execution_contract_only")
        require(row, "allowed_live_accessions", ALLOWED_LIVE_ACCESSIONS)
        require(row, "max_live_batch_size", "1")
        require(row, "authorization_effective", "true")
        require(row, "live_fill_allowed", "true")
        require(row, "fill_execution_allowed", "true")
        require(row, "allowed_next_action", ALLOWED_NEXT_ACTION)
        for field in VALIDATION_FALSE_FIELDS:
            require(row, field, "false")


def load_and_validate_committed_authorization(
    auth_path: Path = AUTH_TABLE,
    auth_validation_path: Path = AUTH_VALIDATION,
    source_manifest_path: Path = SOURCE_MANIFEST,
    source_validation_path: Path = SOURCE_VALIDATION,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    manifest_rows = read_csv_rows(source_manifest_path)
    source_validation_rows = read_csv_rows(source_validation_path)
    auth_rows = read_csv_rows(auth_path)
    validation_rows = read_csv_rows(auth_validation_path)
    validate_authorization_rows(
        auth_rows,
        manifest_rows,
        source_validation_rows,
        file_sha256(source_manifest_path),
        file_sha256(source_validation_path),
    )
    validate_validation_rows(validation_rows, auth_rows)
    return auth_rows, validation_rows
