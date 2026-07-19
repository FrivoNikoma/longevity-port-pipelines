"""Scoped TP53/MDM2 missing-embedding fill manifest contract.

This module builds and validates a metadata-only execution contract for the
missing P23804 and A0ABM2YB85 MDM2 embeddings.

It performs no BioHub or ESMC call, generates no embedding, creates no .npy
artifact, writes nothing under data/output, runs no contrast, promotes no gate,
and makes no biological claim.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

DEFAULT_EXTERNAL_BINDING_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_external_exact_sequence_binding_results.csv"
)
DEFAULT_LOCAL_PREREQUISITE_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_gate8_local_prerequisite_audit_results.csv"
)
DEFAULT_MANIFEST_TABLE = Path("data/input/tp53_mdm2_mdm2_missing_embedding_fill_manifest.csv")
DEFAULT_VALIDATION_RESULT_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_missing_embedding_fill_manifest_validation_results.csv"
)

BINDING_ROOT_ENV = "LONGEVITY_PORT_EXTERNAL_SEQUENCE_BINDING_ROOT"
MODEL_NAME = "esmc-300m-2024-12"
FILL_SCOPE = "scoped_mdm2_missing_embeddings_only"
EXECUTION_MODE = "table_only"
FILL_STATUS = "planning_policy_updated_runtime_blocked"
AUTHORIZATION_STATUS = "pending_explicit_scoped_live_fill_authorization"
ALLOWED_NEXT_ACTION = "request_explicit_scoped_live_fill_authorization"
CLAIM_POLICY = "no_biological_claims_until_validation"
CLAIM_STATUS = "technical_execution_contract"
FORBIDDEN_ACTIONS = (
    "BioHub call; ESMC call; embedding generation; .npy creation; "
    ".npy commit; data/output commit; raw FASTA commit; normalized "
    "amino-acid sequence commit; contrast run; Gate 8 entry; "
    "Gate 8 promotion; Gate 9 promotion; biological claim"
)

EXPECTED_ACCESSIONS = {
    "P23804": {
        "target_species": "mouse",
        "target_taxid": "10090",
        "target_accession_db": "UniProtKB Swiss-Prot",
        "expected_sequence_length": "489",
        "exact_normalized_sequence_sha256": (
            "0841e7c8ebd6a4a9e9e051538600d8f201c6682b3246dfb95ba301ab6233a3e3"
        ),
        "external_normalized_sequence_relative_path": "P23804.sequence.txt",
        "expected_local_embedding_path": (
            "data/output/embeddings/esmc-300m-2024-12/"
            "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_10090.npy"
        ),
    },
    "A0ABM2YB85": {
        "target_species": "hamster",
        "target_taxid": "10036",
        "target_accession_db": "UniProtKB TrEMBL and NCBI RefSeq",
        "expected_sequence_length": "510",
        "exact_normalized_sequence_sha256": (
            "77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5"
        ),
        "external_normalized_sequence_relative_path": "A0ABM2YB85.sequence.txt",
        "expected_local_embedding_path": (
            "data/output/embeddings/esmc-300m-2024-12/"
            "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_10036.npy"
        ),
    },
}

MANIFEST_FIELDS = (
    "manifest_contract_version",
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
    "external_binding_source_table",
    "external_binding_row_index",
    "external_binding_status",
    "external_binding_root_env",
    "external_binding_root_required_for_ci",
    "external_manifest_relative_path",
    "external_normalized_sequence_relative_path",
    "local_prerequisite_source_table",
    "local_prerequisite_row_index",
    "local_prerequisite_status",
    "embedding_model",
    "expected_local_embedding_path",
    "expected_local_embedding_path_policy_status",
    "embedding_path_declared_only",
    "existing_local_embedding_status",
    "existing_local_embedding_exists",
    "existing_local_embedding_tracked",
    "existing_local_embedding_committed",
    "fill_scope",
    "execution_mode",
    "fill_status",
    "table_only_validation_allowed",
    "live_opt_in_required",
    "max_live_batch_size",
    "authorization_status",
    "live_fill_allowed",
    "fill_execution_allowed",
    "allowed_next_action",
    "raw_fasta_committed",
    "normalized_sequence_committed",
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
    "forbidden_actions",
    "claim_policy",
    "claim_status",
    "manifest_note",
)

VALIDATION_RESULT_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "gene_symbol",
    "target_accession",
    "manifest_source_table",
    "manifest_row_index",
    "manifest_row_validation_status",
    "external_binding_validation_status",
    "sequence_hash_binding_status",
    "local_prerequisite_validation_status",
    "embedding_path_policy_status",
    "embedding_artifact_status",
    "manifest_validation_status",
    "scoped_missing_embedding_fill_manifest_status",
    "validated_manifest_accessions",
    "live_fill_allowed",
    "fill_execution_allowed",
    "authorization_status",
    "allowed_next_action",
    "panel_runtime_blocker_code",
    "external_binding_root_required_for_ci",
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
)

MANIFEST_FALSE_FIELDS = (
    "external_binding_root_required_for_ci",
    "live_fill_allowed",
    "fill_execution_allowed",
    "raw_fasta_committed",
    "normalized_sequence_committed",
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

VALIDATION_FALSE_FIELDS = (
    "live_fill_allowed",
    "fill_execution_allowed",
    "external_binding_root_required_for_ci",
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

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(
    path: Path,
    rows: list[dict[str, str]],
    fields: tuple[str, ...],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _require(row: dict[str, str], field: str, expected: str) -> None:
    actual = row.get(field, "").strip()
    if actual != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")


def _find_unique_row(rows: list[dict[str, str]], accession: str) -> tuple[int, dict[str, str]]:
    matches = [
        (index, row)
        for index, row in enumerate(rows, start=1)
        if row.get("target_accession", "").strip() == accession
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {accession}, found {len(matches)}")
    return matches[0]


def _validate_relative_filename(value: str, expected: str) -> None:
    path = Path(value)
    if (
        not value
        or path.is_absolute()
        or value != expected
        or len(path.parts) != 1
        or ".." in path.parts
        or "\\" in value
    ):
        raise ValueError(f"Expected safe relative filename {expected!r}, got {value!r}")


def _validate_embedding_path(value: str, expected: str) -> None:
    path = Path(value)
    required_prefix = "data/output/embeddings/esmc-300m-2024-12/"
    if (
        value != expected
        or path.is_absolute()
        or "\\" in value
        or ".." in path.parts
        or not value.startswith(required_prefix)
        or path.suffix != ".npy"
    ):
        raise ValueError(f"Invalid declared embedding path: {value!r}")


def build_manifest_rows(
    external_binding_rows: list[dict[str, str]],
    local_prerequisite_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for accession in ("P23804", "A0ABM2YB85"):
        expected = EXPECTED_ACCESSIONS[accession]
        binding_index, binding = _find_unique_row(external_binding_rows, accession)
        local_index, local = _find_unique_row(local_prerequisite_rows, accession)

        _require(
            binding,
            "external_binding_status",
            "passed_exact_external_non_committed_binding",
        )
        _require(
            binding,
            "later_missing_embedding_fill_manifest_allowed",
            "true",
        )
        _require(
            binding,
            "allowed_next_action",
            "prepare_scoped_missing_embedding_fill_manifest_dry_run",
        )
        for field in (
            "external_accession_verified",
            "external_taxid_verified",
            "external_length_verified",
            "external_sha256_verified",
        ):
            _require(binding, field, "true")
        _require(binding, "target_taxid", str(expected["target_taxid"]))
        _require(
            binding,
            "expected_sequence_length",
            str(expected["expected_sequence_length"]),
        )
        _require(
            binding,
            "external_normalized_sequence_sha256",
            str(expected["exact_normalized_sequence_sha256"]),
        )
        _require(binding, "external_binding_root_env", BINDING_ROOT_ENV)
        _validate_relative_filename(
            binding["external_normalized_sequence_relative_path"],
            str(expected["external_normalized_sequence_relative_path"]),
        )

        _require(local, "model_name", MODEL_NAME)
        _require(local, "target_species_taxid", str(expected["target_taxid"]))
        _require(
            local,
            "expected_sequence_length",
            str(expected["expected_sequence_length"]),
        )
        _require(local, "local_embedding_status", "missing")
        _require(local, "runtime_blocker_code", "missing_exact_local_embedding")
        _require(local, "git_ignore_rule_status", "data_output_ignored")
        _require(local, "local_runtime_embedding_exists", "false")
        _require(local, "local_runtime_embedding_tracked", "false")
        _require(local, "local_runtime_embedding_committed", "false")
        _validate_embedding_path(
            local["local_embedding_path"],
            str(expected["expected_local_embedding_path"]),
        )

        rows.append(
            {
                "manifest_contract_version": "1",
                "candidate_set": binding["candidate_set"],
                "lane_name": binding["lane_name"],
                "candidate_id": binding["candidate_id"],
                "gene_symbol": "MDM2",
                "target_species": str(expected["target_species"]),
                "target_taxid": str(expected["target_taxid"]),
                "target_accession": accession,
                "target_accession_db": str(expected["target_accession_db"]),
                "expected_sequence_length": str(expected["expected_sequence_length"]),
                "exact_normalized_sequence_sha256": str(
                    expected["exact_normalized_sequence_sha256"]
                ),
                "external_binding_source_table": (DEFAULT_EXTERNAL_BINDING_TABLE.as_posix()),
                "external_binding_row_index": str(binding_index),
                "external_binding_status": ("passed_exact_external_non_committed_binding"),
                "external_binding_root_env": BINDING_ROOT_ENV,
                "external_binding_root_required_for_ci": "false",
                "external_manifest_relative_path": binding[
                    "external_binding_manifest_relative_path"
                ],
                "external_normalized_sequence_relative_path": binding[
                    "external_normalized_sequence_relative_path"
                ],
                "local_prerequisite_source_table": (DEFAULT_LOCAL_PREREQUISITE_TABLE.as_posix()),
                "local_prerequisite_row_index": str(local_index),
                "local_prerequisite_status": "missing",
                "embedding_model": MODEL_NAME,
                "expected_local_embedding_path": local["local_embedding_path"],
                "expected_local_embedding_path_policy_status": ("data_output_ignored"),
                "embedding_path_declared_only": "true",
                "existing_local_embedding_status": "missing",
                "existing_local_embedding_exists": "false",
                "existing_local_embedding_tracked": "false",
                "existing_local_embedding_committed": "false",
                "fill_scope": FILL_SCOPE,
                "execution_mode": EXECUTION_MODE,
                "fill_status": FILL_STATUS,
                "table_only_validation_allowed": "true",
                "live_opt_in_required": "true",
                "max_live_batch_size": "0",
                "authorization_status": AUTHORIZATION_STATUS,
                "live_fill_allowed": "false",
                "fill_execution_allowed": "false",
                "allowed_next_action": ALLOWED_NEXT_ACTION,
                "raw_fasta_committed": "false",
                "normalized_sequence_committed": "false",
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
                "forbidden_actions": FORBIDDEN_ACTIONS,
                "claim_policy": CLAIM_POLICY,
                "claim_status": CLAIM_STATUS,
                "manifest_note": (
                    f"{accession} is a metadata-only scoped fill execution "
                    "contract. The exact external sequence binding is "
                    "verified and the canonical local embedding remains "
                    "missing. Live fill requires a separate explicit "
                    "authorization request."
                ),
            }
        )

    validate_manifest_rows(rows, external_binding_rows, local_prerequisite_rows)
    return rows


def validate_manifest_rows(
    rows: list[dict[str, str]],
    external_binding_rows: list[dict[str, str]],
    local_prerequisite_rows: list[dict[str, str]],
) -> None:
    if len(rows) != 2:
        raise ValueError(f"Expected exactly two manifest rows, got {len(rows)}")
    if [row.get("target_accession") for row in rows] != [
        "P23804",
        "A0ABM2YB85",
    ]:
        raise ValueError("Manifest accessions must be P23804 and A0ABM2YB85")

    for row in rows:
        if set(row) != set(MANIFEST_FIELDS):
            missing = sorted(set(MANIFEST_FIELDS) - set(row))
            extra = sorted(set(row) - set(MANIFEST_FIELDS))
            raise ValueError(f"Manifest fields differ; missing={missing}, extra={extra}")

        accession = row["target_accession"]
        expected = EXPECTED_ACCESSIONS[accession]
        binding_index, binding = _find_unique_row(external_binding_rows, accession)
        local_index, local = _find_unique_row(local_prerequisite_rows, accession)

        _require(row, "manifest_contract_version", "1")
        _require(row, "gene_symbol", "MDM2")
        _require(row, "target_species", str(expected["target_species"]))
        _require(row, "target_taxid", str(expected["target_taxid"]))
        _require(
            row,
            "expected_sequence_length",
            str(expected["expected_sequence_length"]),
        )
        _require(
            row,
            "exact_normalized_sequence_sha256",
            str(expected["exact_normalized_sequence_sha256"]),
        )
        if not SHA256_PATTERN.fullmatch(row["exact_normalized_sequence_sha256"]):
            raise ValueError(f"{accession}: invalid exact sequence SHA-256")

        _require(
            row,
            "external_binding_source_table",
            DEFAULT_EXTERNAL_BINDING_TABLE.as_posix(),
        )
        _require(row, "external_binding_row_index", str(binding_index))
        _require(
            row,
            "external_binding_status",
            "passed_exact_external_non_committed_binding",
        )
        _require(row, "external_binding_root_env", BINDING_ROOT_ENV)
        _require(row, "external_binding_root_required_for_ci", "false")
        _require(
            row,
            "external_manifest_relative_path",
            binding["external_binding_manifest_relative_path"],
        )
        _validate_relative_filename(
            row["external_normalized_sequence_relative_path"],
            str(expected["external_normalized_sequence_relative_path"]),
        )

        _require(
            row,
            "local_prerequisite_source_table",
            DEFAULT_LOCAL_PREREQUISITE_TABLE.as_posix(),
        )
        _require(row, "local_prerequisite_row_index", str(local_index))
        _require(row, "local_prerequisite_status", "missing")
        _require(local, "local_embedding_status", "missing")
        _require(row, "embedding_model", MODEL_NAME)
        _validate_embedding_path(
            row["expected_local_embedding_path"],
            str(expected["expected_local_embedding_path"]),
        )
        _require(
            row,
            "expected_local_embedding_path_policy_status",
            "data_output_ignored",
        )
        _require(row, "embedding_path_declared_only", "true")
        _require(row, "existing_local_embedding_status", "missing")
        _require(row, "existing_local_embedding_exists", "false")
        _require(row, "existing_local_embedding_tracked", "false")
        _require(row, "existing_local_embedding_committed", "false")
        _require(row, "fill_scope", FILL_SCOPE)
        _require(row, "execution_mode", EXECUTION_MODE)
        _require(row, "fill_status", FILL_STATUS)
        _require(row, "table_only_validation_allowed", "true")
        _require(row, "live_opt_in_required", "true")
        _require(row, "max_live_batch_size", "0")
        _require(row, "authorization_status", AUTHORIZATION_STATUS)
        _require(row, "allowed_next_action", ALLOWED_NEXT_ACTION)
        for field in MANIFEST_FALSE_FIELDS:
            _require(row, field, "false")
        _require(binding, "target_accession", accession)
        _require(
            binding,
            "external_normalized_sequence_sha256",
            row["exact_normalized_sequence_sha256"],
        )


def build_validation_result_rows(
    manifest_rows: list[dict[str, str]],
    external_binding_rows: list[dict[str, str]],
    local_prerequisite_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    validate_manifest_rows(manifest_rows, external_binding_rows, local_prerequisite_rows)
    rows: list[dict[str, str]] = []
    for index, manifest in enumerate(manifest_rows, start=1):
        accession = manifest["target_accession"]
        rows.append(
            {
                "candidate_set": manifest["candidate_set"],
                "lane_name": manifest["lane_name"],
                "candidate_id": manifest["candidate_id"],
                "gene_symbol": "MDM2",
                "target_accession": accession,
                "manifest_source_table": DEFAULT_MANIFEST_TABLE.as_posix(),
                "manifest_row_index": str(index),
                "manifest_row_validation_status": "passed",
                "external_binding_validation_status": (
                    "passed_exact_external_non_committed_binding"
                ),
                "sequence_hash_binding_status": "passed_exact_hash_bound",
                "local_prerequisite_validation_status": ("passed_missing_embedding"),
                "embedding_path_policy_status": ("passed_declared_ignored_output_path"),
                "embedding_artifact_status": "missing_not_created",
                "manifest_validation_status": "passed_table_only_validation",
                "scoped_missing_embedding_fill_manifest_status": (
                    "prepared_execution_contract_only"
                ),
                "validated_manifest_accessions": "P23804|A0ABM2YB85",
                "live_fill_allowed": "false",
                "fill_execution_allowed": "false",
                "authorization_status": AUTHORIZATION_STATUS,
                "allowed_next_action": ALLOWED_NEXT_ACTION,
                "panel_runtime_blocker_code": ("explicit_scoped_live_fill_authorization_required"),
                "external_binding_root_required_for_ci": "false",
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
                "claim_policy": CLAIM_POLICY,
                "claim_status": CLAIM_STATUS,
                "validation_note": (
                    f"{accession} passes committed table-only execution-"
                    "contract validation. No live fill or downstream "
                    "execution is authorized."
                ),
            }
        )
    validate_validation_result_rows(rows, manifest_rows)
    return rows


def validate_validation_result_rows(
    rows: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
) -> None:
    if len(rows) != 2:
        raise ValueError(f"Expected exactly two validation rows, got {len(rows)}")
    if [row.get("target_accession") for row in rows] != [
        "P23804",
        "A0ABM2YB85",
    ]:
        raise ValueError("Unexpected validation-result accessions")

    for index, row in enumerate(rows, start=1):
        if set(row) != set(VALIDATION_RESULT_FIELDS):
            missing = sorted(set(VALIDATION_RESULT_FIELDS) - set(row))
            extra = sorted(set(row) - set(VALIDATION_RESULT_FIELDS))
            raise ValueError(f"Validation fields differ; missing={missing}, extra={extra}")
        accession = row["target_accession"]
        _require(manifest_rows[index - 1], "target_accession", accession)
        _require(row, "manifest_source_table", DEFAULT_MANIFEST_TABLE.as_posix())
        _require(row, "manifest_row_index", str(index))
        _require(row, "manifest_row_validation_status", "passed")
        _require(
            row,
            "external_binding_validation_status",
            "passed_exact_external_non_committed_binding",
        )
        _require(row, "sequence_hash_binding_status", "passed_exact_hash_bound")
        _require(
            row,
            "local_prerequisite_validation_status",
            "passed_missing_embedding",
        )
        _require(
            row,
            "embedding_path_policy_status",
            "passed_declared_ignored_output_path",
        )
        _require(row, "embedding_artifact_status", "missing_not_created")
        _require(row, "manifest_validation_status", "passed_table_only_validation")
        _require(
            row,
            "scoped_missing_embedding_fill_manifest_status",
            "prepared_execution_contract_only",
        )
        _require(row, "validated_manifest_accessions", "P23804|A0ABM2YB85")
        _require(row, "authorization_status", AUTHORIZATION_STATUS)
        _require(row, "allowed_next_action", ALLOWED_NEXT_ACTION)
        _require(
            row,
            "panel_runtime_blocker_code",
            "explicit_scoped_live_fill_authorization_required",
        )
        for field in VALIDATION_FALSE_FIELDS:
            _require(row, field, "false")


def load_and_validate_committed_contract(
    manifest_path: Path = DEFAULT_MANIFEST_TABLE,
    validation_result_path: Path = DEFAULT_VALIDATION_RESULT_TABLE,
    external_binding_path: Path = DEFAULT_EXTERNAL_BINDING_TABLE,
    local_prerequisite_path: Path = DEFAULT_LOCAL_PREREQUISITE_TABLE,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    external_rows = read_csv_rows(external_binding_path)
    local_rows = read_csv_rows(local_prerequisite_path)
    manifest_rows = read_csv_rows(manifest_path)
    validation_rows = read_csv_rows(validation_result_path)
    validate_manifest_rows(manifest_rows, external_rows, local_rows)
    validate_validation_result_rows(validation_rows, manifest_rows)
    return manifest_rows, validation_rows
