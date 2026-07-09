"""G3SX30 one-row local embedding preflight check result helpers.

This module validates the repo-visible result record for the externally executed
local preflight check of the already-generated local runtime G3SX30 / elephant
MDM2 ESMC embedding artifact.

It records a result; it does not read or commit the generated .npy artifact,
call Biohub / ESMC, generate embeddings, promote gates, or make biological
claims.
"""

from __future__ import annotations

import csv
from pathlib import Path

DEFAULT_BINDING_TABLE = Path("data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv")
DEFAULT_RESULT_TABLE = Path("data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv")

EXPECTED_CANDIDATE_SET = "tp53_mdm2_elephant"
EXPECTED_LANE_NAME = "tp53_mdm2_elephant"
EXPECTED_CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
EXPECTED_TARGET_ACCESSION = "G3SX30"
EXPECTED_TARGET_ACCESSION_DB = "UniProtKB TrEMBL"
EXPECTED_TARGET_SPECIES = "Loxodonta africana"
EXPECTED_TARGET_TAXID = "9785"
EXPECTED_GENE_SYMBOL = "MDM2"
EXPECTED_LOCAL_EMBEDDING_PATH = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_ARTIFACT_LOCATION = "local_runtime_data_output_ignored_by_git"
EXPECTED_EMBEDDING_SHAPE = "492x960"
EXPECTED_EMBEDDING_DTYPE = "float32"
EXPECTED_SEQUENCE_LENGTH = "492"
EXPECTED_EXTERNAL_OBSERVATION_JSON = (
    "D:/biohub_projects/_chatgpt_observations/g3sx30_one_row_local_embedding_preflight_check.json"
)
EXPECTED_CHECK_NAME = "g3sx30_one_row_local_embedding_preflight_check"
EXPECTED_CHECK_STATUS = "local_preflight_pass"
EXPECTED_NEXT_PRACTICAL_DECISION = (
    "approve_one_row_readiness_preflight_transition_path_or_repair_concrete_blocker"
)
EXPECTED_PASS_DECISION_PATH = "approve_one_row_readiness_preflight_transition_path"
EXPECTED_FAIL_DECISION_PATH = "repair_concrete_local_preflight_blocker"

BINDING_REQUIRED_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "source_decision_status",
    "local_embedding_path",
    "artifact_location",
    "local_runtime_embedding_exists",
    "local_runtime_embedding_tracked",
    "local_runtime_embedding_committed",
    "embedding_shape",
    "embedding_dtype",
    "embedding_finite",
    "sequence_length_matches",
    "approved_for_one_row_readiness_preflight_input",
    "non_committed_preflight_input_reference_created",
    "ready_for_preflight",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "next_concrete_check",
    "next_check_output_policy",
)

RESULT_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "source_binding_table",
    "source_binding_row_index",
    "source_binding_status",
    "check_name",
    "check_status",
    "external_observation_json",
    "local_embedding_path",
    "artifact_location",
    "local_runtime_embedding_exists",
    "local_runtime_embedding_tracked",
    "local_runtime_embedding_committed",
    "git_ignore_rule_status",
    "embedding_shape",
    "embedding_dtype",
    "embedding_finite",
    "sequence_length",
    "sequence_length_matches",
    "approved_for_one_row_readiness_preflight_input",
    "non_committed_preflight_input_reference_created",
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
    "next_practical_decision",
    "pass_decision_path",
    "fail_decision_path",
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
    "external FASTA commit",
    "external live log commit",
    "external validation JSON commit",
    "ready_for_preflight promotion",
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


def validate_binding_row(row: dict[str, str]) -> None:
    """Validate the source binding row that authorized the external local check."""

    _require_fields(row, BINDING_REQUIRED_FIELDS)

    expected_values = {
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "lane_name": EXPECTED_LANE_NAME,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "source_decision_status": (
            "approved_local_runtime_artifact_as_one_row_readiness_preflight_input"
        ),
        "local_embedding_path": EXPECTED_LOCAL_EMBEDDING_PATH,
        "artifact_location": EXPECTED_ARTIFACT_LOCATION,
        "local_runtime_embedding_exists": "true",
        "local_runtime_embedding_tracked": "false",
        "local_runtime_embedding_committed": "false",
        "embedding_shape": EXPECTED_EMBEDDING_SHAPE,
        "embedding_dtype": EXPECTED_EMBEDDING_DTYPE,
        "embedding_finite": "true",
        "sequence_length_matches": "true",
        "approved_for_one_row_readiness_preflight_input": "true",
        "non_committed_preflight_input_reference_created": "true",
        "ready_for_preflight": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "next_concrete_check": "run_record_g3sx30_one_row_local_embedding_preflight_check",
        "next_check_output_policy": "external_non_committed_observation_only",
    }

    for field, expected in expected_values.items():
        _require_value(row, field, expected)


def build_result_row_from_binding(
    binding_row: dict[str, str],
    *,
    source_binding_table: Path = DEFAULT_BINDING_TABLE,
    source_binding_row_index: int = 1,
) -> dict[str, str]:
    """Build the expected local preflight check result row from a valid binding."""

    validate_binding_row(binding_row)

    return {
        "candidate_set": binding_row["candidate_set"],
        "lane_name": binding_row["lane_name"],
        "candidate_id": binding_row["candidate_id"],
        "target_accession": binding_row["target_accession"],
        "target_accession_db": binding_row["target_accession_db"],
        "target_species": binding_row["target_species"],
        "target_taxid": binding_row["target_taxid"],
        "gene_symbol": binding_row["gene_symbol"],
        "source_binding_table": _repo_relative_text(source_binding_table),
        "source_binding_row_index": str(source_binding_row_index),
        "source_binding_status": "non_committed_preflight_input_reference_created",
        "check_name": EXPECTED_CHECK_NAME,
        "check_status": EXPECTED_CHECK_STATUS,
        "external_observation_json": EXPECTED_EXTERNAL_OBSERVATION_JSON,
        "local_embedding_path": binding_row["local_embedding_path"],
        "artifact_location": binding_row["artifact_location"],
        "local_runtime_embedding_exists": binding_row["local_runtime_embedding_exists"],
        "local_runtime_embedding_tracked": binding_row["local_runtime_embedding_tracked"],
        "local_runtime_embedding_committed": binding_row["local_runtime_embedding_committed"],
        "git_ignore_rule_status": "data_output_ignored",
        "embedding_shape": binding_row["embedding_shape"],
        "embedding_dtype": binding_row["embedding_dtype"],
        "embedding_finite": binding_row["embedding_finite"],
        "sequence_length": EXPECTED_SEQUENCE_LENGTH,
        "sequence_length_matches": binding_row["sequence_length_matches"],
        "approved_for_one_row_readiness_preflight_input": binding_row[
            "approved_for_one_row_readiness_preflight_input"
        ],
        "non_committed_preflight_input_reference_created": binding_row[
            "non_committed_preflight_input_reference_created"
        ],
        "biohub_esmc_called_by_check": "false",
        "live_embedding_rerun_by_check": "false",
        "embedding_generation_performed_by_check": "false",
        "npy_artifact_created_by_check": "false",
        "data_output_artifact_committed": "false",
        "external_validation_json_committed": "false",
        "ready_for_preflight_promoted": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "enrichment_rerun": "false",
        "contrast_rerun": "false",
        "biological_claim_made": "false",
        "downstream_gate_unlocked": "false",
        "next_practical_decision": EXPECTED_NEXT_PRACTICAL_DECISION,
        "pass_decision_path": EXPECTED_PASS_DECISION_PATH,
        "fail_decision_path": EXPECTED_FAIL_DECISION_PATH,
        "forbidden_actions": "; ".join(FORBIDDEN_ACTIONS),
        "reviewer_id": "manual_gate_review",
        "check_date": "2026-07-09",
        "result_note": (
            "Records the external local preflight check result for the "
            "already-generated local runtime G3SX30 / elephant MDM2 ESMC "
            "embedding artifact. The check passed shape, dtype, finite, "
            "sequence-length, ignored/untracked/uncommitted artifact, and "
            "no-side-effect policy checks. This record does not commit the .npy "
            "artifact or external JSON, does not promote ready_for_preflight, "
            "does not promote Gate 8 or Gate 9, and makes no biological claim. "
            "Next practical decision: approve one-row readiness/preflight "
            "transition path or repair a concrete blocker."
        ),
    }


def validate_result_row(row: dict[str, str]) -> None:
    """Validate the committed local embedding preflight check result row."""

    _require_fields(row, RESULT_FIELDS)

    expected_values = {
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "lane_name": EXPECTED_LANE_NAME,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "source_binding_table": str(DEFAULT_BINDING_TABLE).replace("\\", "/"),
        "source_binding_row_index": "1",
        "source_binding_status": "non_committed_preflight_input_reference_created",
        "check_name": EXPECTED_CHECK_NAME,
        "check_status": EXPECTED_CHECK_STATUS,
        "external_observation_json": EXPECTED_EXTERNAL_OBSERVATION_JSON,
        "local_embedding_path": EXPECTED_LOCAL_EMBEDDING_PATH,
        "artifact_location": EXPECTED_ARTIFACT_LOCATION,
        "local_runtime_embedding_exists": "true",
        "local_runtime_embedding_tracked": "false",
        "local_runtime_embedding_committed": "false",
        "git_ignore_rule_status": "data_output_ignored",
        "embedding_shape": EXPECTED_EMBEDDING_SHAPE,
        "embedding_dtype": EXPECTED_EMBEDDING_DTYPE,
        "embedding_finite": "true",
        "sequence_length": EXPECTED_SEQUENCE_LENGTH,
        "sequence_length_matches": "true",
        "approved_for_one_row_readiness_preflight_input": "true",
        "non_committed_preflight_input_reference_created": "true",
        "biohub_esmc_called_by_check": "false",
        "live_embedding_rerun_by_check": "false",
        "embedding_generation_performed_by_check": "false",
        "npy_artifact_created_by_check": "false",
        "data_output_artifact_committed": "false",
        "external_validation_json_committed": "false",
        "ready_for_preflight_promoted": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "enrichment_rerun": "false",
        "contrast_rerun": "false",
        "biological_claim_made": "false",
        "downstream_gate_unlocked": "false",
        "next_practical_decision": EXPECTED_NEXT_PRACTICAL_DECISION,
        "pass_decision_path": EXPECTED_PASS_DECISION_PATH,
        "fail_decision_path": EXPECTED_FAIL_DECISION_PATH,
    }

    for field, expected in expected_values.items():
        _require_value(row, field, expected)

    forbidden_actions = row["forbidden_actions"]
    missing_forbidden = [
        forbidden for forbidden in FORBIDDEN_ACTIONS if forbidden not in forbidden_actions
    ]
    if missing_forbidden:
        raise ValueError(f"Missing forbidden action tokens: {missing_forbidden}")


def load_and_validate_result(
    result_table: Path = DEFAULT_RESULT_TABLE,
) -> dict[str, str]:
    """Load and validate the committed one-row result table."""

    row = require_single_row(result_table)
    validate_result_row(row)
    return row


def load_binding_and_build_result(
    binding_table: Path = DEFAULT_BINDING_TABLE,
) -> dict[str, str]:
    """Load the source binding row and build the expected result row."""

    binding_row = require_single_row(binding_table)
    return build_result_row_from_binding(binding_row, source_binding_table=binding_table)
