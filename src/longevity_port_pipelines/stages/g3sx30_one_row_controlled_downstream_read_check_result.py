"""G3SX30 one-row controlled downstream read/check result helpers.

This module validates the committed result record for the actual controlled
downstream read/check of the one-row ready G3SX30 elephant MDM2 local runtime
embedding artifact.

It records a read/check result; it does not call Biohub / ESMC, generate a new
embedding, commit the generated .npy artifact, promote Gate 8 or Gate 9, rerun
enrichment/contrast, or make a biological claim.
"""

from __future__ import annotations

import csv
from pathlib import Path

DEFAULT_SOURCE_DOWNSTREAM_USE_PATH_TABLE = Path(
    "data/input/g3sx30_one_row_controlled_downstream_use_paths.csv"
)
DEFAULT_READ_CHECK_RESULT_TABLE = Path(
    "data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv"
)

EXPECTED_CANDIDATE_SET = "tp53_mdm2_elephant"
EXPECTED_LANE_NAME = "tp53_mdm2_elephant"
EXPECTED_CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
EXPECTED_TARGET_ACCESSION = "G3SX30"
EXPECTED_TARGET_ACCESSION_DB = "UniProtKB TrEMBL"
EXPECTED_TARGET_SPECIES = "Loxodonta africana"
EXPECTED_TARGET_TAXID = "9785"
EXPECTED_GENE_SYMBOL = "MDM2"
EXPECTED_CONTROLLED_DOWNSTREAM_USE_PATH = (
    "first_controlled_downstream_use_path_for_one_row_ready_artifact"
)
EXPECTED_CONTROLLED_HANDLE_ID = (
    "g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle"
)
EXPECTED_CONTROLLED_INPUT_STATUS = "one_row_ready_artifact_available_for_controlled_downstream_use"
EXPECTED_READY_ARTIFACT_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_READY_ARTIFACT_LOCATION = "local_runtime_data_output_ignored_by_git"
EXPECTED_READ_CHECK_ACTION = (
    "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact"
)
EXPECTED_READ_CHECK_STATUS = "controlled_downstream_read_check_passed"
EXPECTED_EMBEDDING_SHAPE = "492x960"
EXPECTED_EMBEDDING_DTYPE = "float32"
EXPECTED_SEQUENCE_LENGTH = "492"
EXPECTED_READY_SCOPE = "one_row_g3sx30_elephant_mdm2_only"
EXPECTED_CONTROLLED_READ_CHECK_SCOPE = (
    "local_artifact_read_shape_dtype_finiteness_sequence_length_path_policy_only"
)
EXPECTED_NEXT_STEP = (
    "move_toward_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact"
)

SOURCE_DOWNSTREAM_USE_PATH_REQUIRED_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "controlled_downstream_use_path",
    "controlled_handle_id",
    "controlled_input_status",
    "one_row_only",
    "ready_scope",
    "ready_artifact_reference",
    "ready_artifact_location",
    "controlled_read_check_next_action",
    "next_pr_must_be_actual_controlled_downstream_read_check",
    "no_additional_downstream_approval_before_read_check",
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
    "next_step",
)

READ_CHECK_RESULT_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "source_downstream_use_path_table",
    "source_downstream_use_path_row_index",
    "source_controlled_downstream_use_path",
    "source_controlled_handle_id",
    "source_controlled_input_status",
    "source_ready_artifact_reference",
    "source_ready_artifact_location",
    "source_next_pr_must_be_actual_controlled_downstream_read_check",
    "source_no_additional_downstream_approval_before_read_check",
    "source_next_step",
    "read_check_action",
    "read_check_status",
    "controlled_handle_id",
    "controlled_input_status",
    "local_runtime_embedding_exists",
    "local_runtime_embedding_tracked",
    "local_runtime_embedding_committed",
    "git_ignore_rule_status",
    "embedding_shape",
    "embedding_dtype",
    "embedding_finite",
    "sequence_length",
    "sequence_length_matches",
    "controlled_read_check_scope",
    "one_row_only",
    "ready_scope",
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
    "next_step",
    "next_pr_should_move_toward_first_minimal_controlled_downstream_output",
    "no_additional_read_check_approval_before_output",
    "forbidden_actions",
    "reviewer_id",
    "check_date",
    "result_note",
)

FORBIDDEN_ACTIONS = (
    "Biohub call",
    "ESMC call",
    "live embedding rerun",
    "embedding generation",
    ".npy commit",
    "data/output commit",
    "Gate 8 promotion",
    "Gate 9 promotion",
    "Boltz call",
    "AF3 call",
    "Chai call",
    "enrichment rerun",
    "contrast rerun",
    "biological claim",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries."""

    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    """Read exactly one CSV row."""

    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def _require_fields(row: dict[str, str], fields: tuple[str, ...]) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")


def _require_value(row: dict[str, str], field: str, expected: str) -> None:
    value = row.get(field)
    if value != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {value!r}")


def _repo_relative_text(path: Path) -> str:
    """Render a path as repo-relative text when possible."""

    if path.is_absolute():
        try:
            return path.relative_to(Path.cwd()).as_posix()
        except ValueError:
            return path.as_posix()
    return str(path).replace("\\", "/")


def validate_source_downstream_use_path_row(row: dict[str, str]) -> None:
    """Validate the controlled downstream handle consumed by this read/check."""

    _require_fields(row, SOURCE_DOWNSTREAM_USE_PATH_REQUIRED_FIELDS)

    expected_values = {
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "lane_name": EXPECTED_LANE_NAME,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "controlled_downstream_use_path": EXPECTED_CONTROLLED_DOWNSTREAM_USE_PATH,
        "controlled_handle_id": EXPECTED_CONTROLLED_HANDLE_ID,
        "controlled_input_status": EXPECTED_CONTROLLED_INPUT_STATUS,
        "one_row_only": "true",
        "ready_scope": EXPECTED_READY_SCOPE,
        "ready_artifact_reference": EXPECTED_READY_ARTIFACT_REFERENCE,
        "ready_artifact_location": EXPECTED_READY_ARTIFACT_LOCATION,
        "controlled_read_check_next_action": EXPECTED_READ_CHECK_ACTION,
        "next_pr_must_be_actual_controlled_downstream_read_check": "true",
        "no_additional_downstream_approval_before_read_check": "true",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "data_output_artifact_committed": "false",
        "biohub_esmc_called_by_path_creation": "false",
        "live_embedding_rerun_by_path_creation": "false",
        "embedding_generation_performed_by_path_creation": "false",
        "npy_artifact_created_by_path_creation": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "enrichment_rerun": "false",
        "contrast_rerun": "false",
        "next_step": EXPECTED_READ_CHECK_ACTION,
    }

    for field, expected in expected_values.items():
        _require_value(row, field, expected)


def build_read_check_result_row_from_source(
    source_row: dict[str, str],
    *,
    artifact_observation: dict[str, str],
    source_downstream_use_path_table: Path = DEFAULT_SOURCE_DOWNSTREAM_USE_PATH_TABLE,
    source_downstream_use_path_row_index: int = 1,
) -> dict[str, str]:
    """Build the expected controlled downstream read/check result row."""

    validate_source_downstream_use_path_row(source_row)

    required_observation = {
        "local_runtime_embedding_exists": "true",
        "local_runtime_embedding_tracked": "false",
        "local_runtime_embedding_committed": "false",
        "git_ignore_rule_status": "data_output_ignored",
        "embedding_shape": EXPECTED_EMBEDDING_SHAPE,
        "embedding_dtype": EXPECTED_EMBEDDING_DTYPE,
        "embedding_finite": "true",
        "sequence_length": EXPECTED_SEQUENCE_LENGTH,
        "sequence_length_matches": "true",
    }

    for field, expected in required_observation.items():
        _require_value(artifact_observation, field, expected)

    return {
        "candidate_set": source_row["candidate_set"],
        "lane_name": source_row["lane_name"],
        "candidate_id": source_row["candidate_id"],
        "target_accession": source_row["target_accession"],
        "target_accession_db": source_row["target_accession_db"],
        "target_species": source_row["target_species"],
        "target_taxid": source_row["target_taxid"],
        "gene_symbol": source_row["gene_symbol"],
        "source_downstream_use_path_table": _repo_relative_text(source_downstream_use_path_table),
        "source_downstream_use_path_row_index": str(source_downstream_use_path_row_index),
        "source_controlled_downstream_use_path": source_row["controlled_downstream_use_path"],
        "source_controlled_handle_id": source_row["controlled_handle_id"],
        "source_controlled_input_status": source_row["controlled_input_status"],
        "source_ready_artifact_reference": source_row["ready_artifact_reference"],
        "source_ready_artifact_location": source_row["ready_artifact_location"],
        "source_next_pr_must_be_actual_controlled_downstream_read_check": source_row[
            "next_pr_must_be_actual_controlled_downstream_read_check"
        ],
        "source_no_additional_downstream_approval_before_read_check": source_row[
            "no_additional_downstream_approval_before_read_check"
        ],
        "source_next_step": source_row["next_step"],
        "read_check_action": EXPECTED_READ_CHECK_ACTION,
        "read_check_status": EXPECTED_READ_CHECK_STATUS,
        "controlled_handle_id": source_row["controlled_handle_id"],
        "controlled_input_status": source_row["controlled_input_status"],
        "local_runtime_embedding_exists": artifact_observation["local_runtime_embedding_exists"],
        "local_runtime_embedding_tracked": artifact_observation["local_runtime_embedding_tracked"],
        "local_runtime_embedding_committed": artifact_observation[
            "local_runtime_embedding_committed"
        ],
        "git_ignore_rule_status": artifact_observation["git_ignore_rule_status"],
        "embedding_shape": artifact_observation["embedding_shape"],
        "embedding_dtype": artifact_observation["embedding_dtype"],
        "embedding_finite": artifact_observation["embedding_finite"],
        "sequence_length": artifact_observation["sequence_length"],
        "sequence_length_matches": artifact_observation["sequence_length_matches"],
        "controlled_read_check_scope": EXPECTED_CONTROLLED_READ_CHECK_SCOPE,
        "one_row_only": source_row["one_row_only"],
        "ready_scope": source_row["ready_scope"],
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "data_output_artifact_committed": "false",
        "biohub_esmc_called_by_read_check": "false",
        "live_embedding_rerun_by_read_check": "false",
        "embedding_generation_performed_by_read_check": "false",
        "npy_artifact_created_by_read_check": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "enrichment_rerun": "false",
        "contrast_rerun": "false",
        "next_step": EXPECTED_NEXT_STEP,
        "next_pr_should_move_toward_first_minimal_controlled_downstream_output": "true",
        "no_additional_read_check_approval_before_output": "true",
        "forbidden_actions": "; ".join(FORBIDDEN_ACTIONS),
        "reviewer_id": "manual_gate_review",
        "check_date": "2026-07-09",
        "result_note": (
            "Records the actual controlled downstream read/check result for the "
            "one-row ready G3SX30 elephant MDM2 local runtime artifact. The read/check "
            "validated the controlled handle, read the ignored local .npy artifact, "
            "and confirmed existence, untracked/uncommitted data-output policy, shape, "
            "dtype, finite values, and sequence-length match. It did not call Biohub/"
            "ESMC, rerun live embedding, generate a new embedding, commit the .npy or "
            "data/output artifact, promote Gate 8 or Gate 9, rerun enrichment/contrast, "
            "call Boltz/AF3/Chai, or make a biological claim. Next step moves toward "
            "the first minimal controlled downstream output, not another read/check "
            "approval."
        ),
    }


def validate_read_check_result_row(row: dict[str, str]) -> None:
    """Validate the committed controlled downstream read/check result row."""

    _require_fields(row, READ_CHECK_RESULT_FIELDS)

    expected_values = {
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "lane_name": EXPECTED_LANE_NAME,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "source_downstream_use_path_table": str(DEFAULT_SOURCE_DOWNSTREAM_USE_PATH_TABLE).replace(
            "\\", "/"
        ),
        "source_downstream_use_path_row_index": "1",
        "source_controlled_downstream_use_path": EXPECTED_CONTROLLED_DOWNSTREAM_USE_PATH,
        "source_controlled_handle_id": EXPECTED_CONTROLLED_HANDLE_ID,
        "source_controlled_input_status": EXPECTED_CONTROLLED_INPUT_STATUS,
        "source_ready_artifact_reference": EXPECTED_READY_ARTIFACT_REFERENCE,
        "source_ready_artifact_location": EXPECTED_READY_ARTIFACT_LOCATION,
        "source_next_pr_must_be_actual_controlled_downstream_read_check": "true",
        "source_no_additional_downstream_approval_before_read_check": "true",
        "source_next_step": EXPECTED_READ_CHECK_ACTION,
        "read_check_action": EXPECTED_READ_CHECK_ACTION,
        "read_check_status": EXPECTED_READ_CHECK_STATUS,
        "controlled_handle_id": EXPECTED_CONTROLLED_HANDLE_ID,
        "controlled_input_status": EXPECTED_CONTROLLED_INPUT_STATUS,
        "local_runtime_embedding_exists": "true",
        "local_runtime_embedding_tracked": "false",
        "local_runtime_embedding_committed": "false",
        "git_ignore_rule_status": "data_output_ignored",
        "embedding_shape": EXPECTED_EMBEDDING_SHAPE,
        "embedding_dtype": EXPECTED_EMBEDDING_DTYPE,
        "embedding_finite": "true",
        "sequence_length": EXPECTED_SEQUENCE_LENGTH,
        "sequence_length_matches": "true",
        "controlled_read_check_scope": EXPECTED_CONTROLLED_READ_CHECK_SCOPE,
        "one_row_only": "true",
        "ready_scope": EXPECTED_READY_SCOPE,
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "data_output_artifact_committed": "false",
        "biohub_esmc_called_by_read_check": "false",
        "live_embedding_rerun_by_read_check": "false",
        "embedding_generation_performed_by_read_check": "false",
        "npy_artifact_created_by_read_check": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "enrichment_rerun": "false",
        "contrast_rerun": "false",
        "next_step": EXPECTED_NEXT_STEP,
        "next_pr_should_move_toward_first_minimal_controlled_downstream_output": "true",
        "no_additional_read_check_approval_before_output": "true",
    }

    for field, expected in expected_values.items():
        _require_value(row, field, expected)

    forbidden_actions = row["forbidden_actions"]
    missing_forbidden = [
        forbidden for forbidden in FORBIDDEN_ACTIONS if forbidden not in forbidden_actions
    ]
    if missing_forbidden:
        raise ValueError(f"Missing forbidden action tokens: {missing_forbidden}")


def load_and_validate_read_check_result(
    result_table: Path = DEFAULT_READ_CHECK_RESULT_TABLE,
) -> dict[str, str]:
    """Load and validate the committed one-row read/check result table."""

    row = require_single_row(result_table)
    validate_read_check_result_row(row)
    return row


def load_source_and_build_read_check_result(
    source_table: Path = DEFAULT_SOURCE_DOWNSTREAM_USE_PATH_TABLE,
) -> dict[str, str]:
    """Build the expected result from the source row and expected observation."""

    source_row = require_single_row(source_table)
    observation = {
        "local_runtime_embedding_exists": "true",
        "local_runtime_embedding_tracked": "false",
        "local_runtime_embedding_committed": "false",
        "git_ignore_rule_status": "data_output_ignored",
        "embedding_shape": EXPECTED_EMBEDDING_SHAPE,
        "embedding_dtype": EXPECTED_EMBEDDING_DTYPE,
        "embedding_finite": "true",
        "sequence_length": EXPECTED_SEQUENCE_LENGTH,
        "sequence_length_matches": "true",
    }
    return build_read_check_result_row_from_source(
        source_row,
        artifact_observation=observation,
        source_downstream_use_path_table=source_table,
    )
