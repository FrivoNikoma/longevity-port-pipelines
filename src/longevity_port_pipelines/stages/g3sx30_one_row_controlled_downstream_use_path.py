"""G3SX30 one-row controlled downstream use path helpers."""

from __future__ import annotations

import csv
from pathlib import Path

DEFAULT_SOURCE_TRANSITION_RESULT_TABLE = Path(
    "data/input/g3sx30_one_row_readiness_preflight_transition_results.csv"
)
DEFAULT_DOWNSTREAM_USE_PATH_TABLE = Path(
    "data/input/g3sx30_one_row_controlled_downstream_use_paths.csv"
)

EXPECTED = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "target_accession": "G3SX30",
    "target_accession_db": "UniProtKB TrEMBL",
    "target_species": "Loxodonta africana",
    "target_taxid": "9785",
    "gene_symbol": "MDM2",
    "source_transition_result_table": (
        "data/input/g3sx30_one_row_readiness_preflight_transition_results.csv"
    ),
    "source_transition_result_row_index": "1",
    "source_transition_status": "one_row_readiness_preflight_transition_passed",
    "source_ready_for_preflight": "true",
    "source_allowed_downstream_use_path": (
        "first_controlled_downstream_use_path_for_one_row_ready_artifact"
    ),
    "controlled_downstream_use_path": (
        "first_controlled_downstream_use_path_for_one_row_ready_artifact"
    ),
    "controlled_handle_id": (
        "g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle"
    ),
    "controlled_input_status": ("one_row_ready_artifact_available_for_controlled_downstream_use"),
    "one_row_only": "true",
    "ready_scope": "one_row_g3sx30_elephant_mdm2_only",
    "ready_artifact_reference": (
        "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
    ),
    "ready_artifact_location": "local_runtime_data_output_ignored_by_git",
    "controlled_read_check_next_action": (
        "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact"
    ),
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
    "next_step": "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact",
}

SOURCE_TRANSITION_EXPECTED = {
    "transition_status": "one_row_readiness_preflight_transition_passed",
    "ready_for_preflight": "true",
    "ready_scope": "one_row_g3sx30_elephant_mdm2_only",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "allowed_downstream_use_path": (
        "first_controlled_downstream_use_path_for_one_row_ready_artifact"
    ),
    "next_step": "add_first_controlled_downstream_use_path_for_one_row_ready_artifact",
}

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
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def _repo_relative_text(path: Path) -> str:
    if path.is_absolute():
        try:
            return path.relative_to(Path.cwd()).as_posix()
        except ValueError:
            return path.as_posix()
    return str(path).replace("\\", "/")


def _require(row: dict[str, str], field: str, expected: str) -> None:
    value = row.get(field)
    if value != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {value!r}")


def validate_source_transition_result_row(row: dict[str, str]) -> None:
    for field, expected in SOURCE_TRANSITION_EXPECTED.items():
        _require(row, field, expected)


def build_downstream_use_path_row_from_source_transition(
    source_transition_row: dict[str, str],
    *,
    source_transition_result_table: Path = DEFAULT_SOURCE_TRANSITION_RESULT_TABLE,
) -> dict[str, str]:
    validate_source_transition_result_row(source_transition_row)
    row = dict(EXPECTED)
    row["source_transition_result_table"] = _repo_relative_text(source_transition_result_table)
    for field in [
        "candidate_set",
        "lane_name",
        "candidate_id",
        "target_accession",
        "target_accession_db",
        "target_species",
        "target_taxid",
        "gene_symbol",
    ]:
        row[field] = source_transition_row[field]
    row["source_transition_status"] = source_transition_row["transition_status"]
    row["source_ready_for_preflight"] = source_transition_row["ready_for_preflight"]
    row["source_allowed_downstream_use_path"] = source_transition_row["allowed_downstream_use_path"]
    row["ready_artifact_reference"] = source_transition_row["local_embedding_path"]
    row["forbidden_actions"] = "; ".join(FORBIDDEN_ACTIONS)
    row["reviewer_id"] = "manual_gate_review"
    row["path_creation_date"] = "2026-07-09"
    row["path_note"] = (
        "Creates the first controlled downstream use path for the one-row ready "
        "G3SX30 elephant MDM2 artifact. This is a concrete controlled handle for "
        "the single ready row, not a decision layer. It records that the one-row "
        "ready artifact is available for controlled downstream use. It does not "
        "call Biohub/ESMC, rerun live embedding, generate embeddings, commit the "
        "local .npy/data-output artifact, promote Gate 8 or Gate 9, rerun "
        "enrichment/contrast, call Boltz/AF3/Chai, or make a biological claim. "
        "After this PR, the next step should run an actual controlled downstream "
        "read/check for the one-row ready G3SX30 artifact."
    )
    return row


def validate_downstream_use_path_row(row: dict[str, str]) -> None:
    for field, expected in EXPECTED.items():
        _require(row, field, expected)
    for forbidden in FORBIDDEN_ACTIONS:
        if forbidden not in row.get("forbidden_actions", ""):
            raise ValueError(f"Missing forbidden action token: {forbidden!r}")


def load_and_validate_downstream_use_path(
    table: Path = DEFAULT_DOWNSTREAM_USE_PATH_TABLE,
) -> dict[str, str]:
    row = require_single_row(table)
    validate_downstream_use_path_row(row)
    return row


def load_source_transition_and_build_downstream_use_path(
    table: Path = DEFAULT_SOURCE_TRANSITION_RESULT_TABLE,
) -> dict[str, str]:
    source = require_single_row(table)
    return build_downstream_use_path_row_from_source_transition(
        source, source_transition_result_table=table
    )
