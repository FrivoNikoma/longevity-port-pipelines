from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path

DEFAULT_TABLE = Path("data/interim/g3sx30_wrapper_dry_run_execution_plan_review.csv")

SOURCE_EXECUTION_PLAN_SCAFFOLD_TABLE = (
    "data/interim/g3sx30_wrapper_dry_run_execution_plan_scaffold.csv"
)
SOURCE_EXECUTION_PLAN_SCAFFOLD_ROW_INDEX = "1"
SOURCE_ENTRYPOINT_BOUNDARY_MODULE = (
    "src/longevity_port_pipelines/stages/g3sx30_wrapper_source_entrypoint_boundary.py"
)
SOURCE_MANIFEST_TABLE = "data/input/g3sx30_dry_run_preflight_manifest.csv"
SOURCE_MANIFEST_ROW_INDEX = "1"

CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
TARGET_ACCESSION = "G3SX30"
TARGET_ACCESSION_DB = "UniProtKB TrEMBL"
TARGET_SPECIES = "Loxodonta africana"
TARGET_TAXID = "9785"
GENE_SYMBOL = "MDM2"
REVIEWED_SEQUENCE_LENGTH = "492"
REVIEWED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"

SCRIPT_ENTRY_POINT = "g3sx30-wrapper-dry-run"
SELECTED_FUTURE_MANIFEST_PATH = "data/input/g3sx30_dry_run_preflight_manifest.csv"
SELECTED_FUTURE_MANIFEST_ROW_INDEX = "1"
SELECTED_EXTERNAL_OUTPUT_PATH = (
    "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
)
SELECTED_FUTURE_COMMAND_FORM = (
    "uv run g3sx30-wrapper-dry-run "
    "--manifest data/input/g3sx30_dry_run_preflight_manifest.csv "
    "--manifest-row-index 1 "
    "--output-path D:/biohub_projects/_chatgpt_observations/"
    "g3sx30_wrapper_dry_run_execution_plan.json"
)

REVIEW_STATUS = "dry_run_execution_plan_scaffold_reviewed"
REVIEW_DECISION = "approve_selected_external_output_dry_run_for_next_pr"
REVIEW_SCOPE = "final_non_execution_review_before_actual_dry_run_pr"
OUTPUT_PATH_REVIEW_DECISION = "approve_external_non_committed_output_path"
COMMAND_FORM_REVIEW_DECISION = "approve_selected_wrapper_dry_run_command_form"
CLAIM_STATUS = "technical_checkpoint"
ALLOWED_NEXT_ACTION_AFTER_REVIEW = "execute_g3sx30_wrapper_dry_run_with_external_output_path"

FORBIDDEN_ACTIONS_THIS_PR = (
    "run_dry_run; run_live; execute_manifest_in_this_pr; call_biohub; "
    "call_esmc; generate_embeddings; create_npy_artifact; create_output_file; "
    "create_output_directory; commit_data_output_artifact; ready_for_preflight; "
    "promote_gate8; promote_gate9; call_boltz; call_af3; call_chai; biological_claim"
)

REVIEW_NOTE = (
    "Final non-execution review layer for the selected G3SX30 wrapper dry-run "
    "execution plan scaffold. The selected command form and external "
    "non-committed output path are reviewed and approved for the next PR only. "
    "This PR does not run the dry-run, does not execute the manifest, does not "
    "create the external output file or directory, does not call Biohub / ESMC, "
    "does not generate embeddings, and does not promote ready_for_preflight, "
    "Gate 8, Gate 9, or biological claims. After this review, the next "
    "practical PR should execute the G3SX30 wrapper dry-run with the reviewed "
    "external output path, still with no Biohub / ESMC, no embeddings, and no "
    "Gate 8 / Gate 9."
)

COLUMN_ORDER = [
    "source_execution_plan_scaffold_table",
    "source_execution_plan_scaffold_row_index",
    "source_entrypoint_boundary_module",
    "source_manifest_table",
    "source_manifest_row_index",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "reviewed_sequence_length",
    "reviewed_sequence_sha256",
    "review_status",
    "review_scope",
    "review_decision",
    "script_entry_point",
    "selected_future_command_form",
    "selected_future_manifest_path",
    "selected_future_manifest_row_index",
    "selected_external_output_path",
    "selected_command_form_reviewed",
    "selected_external_output_path_reviewed",
    "selected_manifest_row_reviewed",
    "command_form_review_decision",
    "external_output_path_review_decision",
    "dry_run_execution_authorized_for_next_pr",
    "dry_run_execution_authorized_in_this_pr",
    "dry_run_executed",
    "live_execution_authorized",
    "manifest_execution_authorized_in_this_pr",
    "biohub_esmc_authorized",
    "embedding_generation_authorized",
    "npy_artifact_authorized",
    "output_file_created",
    "output_directory_created",
    "data_output_artifact_commit_authorized",
    "ready_for_preflight_authorized",
    "gate8_promotion_authorized",
    "gate9_promotion_authorized",
    "biological_claim_authorized",
    "runtime_still_blocked_in_this_pr",
    "next_pr_must_use_reviewed_command_form",
    "next_pr_must_use_reviewed_external_output_path",
    "allowed_next_action_after_review",
    "claim_status",
    "forbidden_actions_this_pr",
    "review_note",
]


def build_dry_run_execution_plan_review_row() -> dict[str, str]:
    return {
        "source_execution_plan_scaffold_table": SOURCE_EXECUTION_PLAN_SCAFFOLD_TABLE,
        "source_execution_plan_scaffold_row_index": SOURCE_EXECUTION_PLAN_SCAFFOLD_ROW_INDEX,
        "source_entrypoint_boundary_module": SOURCE_ENTRYPOINT_BOUNDARY_MODULE,
        "source_manifest_table": SOURCE_MANIFEST_TABLE,
        "source_manifest_row_index": SOURCE_MANIFEST_ROW_INDEX,
        "candidate_id": CANDIDATE_ID,
        "target_accession": TARGET_ACCESSION,
        "target_accession_db": TARGET_ACCESSION_DB,
        "target_species": TARGET_SPECIES,
        "target_taxid": TARGET_TAXID,
        "gene_symbol": GENE_SYMBOL,
        "reviewed_sequence_length": REVIEWED_SEQUENCE_LENGTH,
        "reviewed_sequence_sha256": REVIEWED_SEQUENCE_SHA256,
        "review_status": REVIEW_STATUS,
        "review_scope": REVIEW_SCOPE,
        "review_decision": REVIEW_DECISION,
        "script_entry_point": SCRIPT_ENTRY_POINT,
        "selected_future_command_form": SELECTED_FUTURE_COMMAND_FORM,
        "selected_future_manifest_path": SELECTED_FUTURE_MANIFEST_PATH,
        "selected_future_manifest_row_index": SELECTED_FUTURE_MANIFEST_ROW_INDEX,
        "selected_external_output_path": SELECTED_EXTERNAL_OUTPUT_PATH,
        "selected_command_form_reviewed": "true",
        "selected_external_output_path_reviewed": "true",
        "selected_manifest_row_reviewed": "true",
        "command_form_review_decision": COMMAND_FORM_REVIEW_DECISION,
        "external_output_path_review_decision": OUTPUT_PATH_REVIEW_DECISION,
        "dry_run_execution_authorized_for_next_pr": "true",
        "dry_run_execution_authorized_in_this_pr": "false",
        "dry_run_executed": "false",
        "live_execution_authorized": "false",
        "manifest_execution_authorized_in_this_pr": "false",
        "biohub_esmc_authorized": "false",
        "embedding_generation_authorized": "false",
        "npy_artifact_authorized": "false",
        "output_file_created": "false",
        "output_directory_created": "false",
        "data_output_artifact_commit_authorized": "false",
        "ready_for_preflight_authorized": "false",
        "gate8_promotion_authorized": "false",
        "gate9_promotion_authorized": "false",
        "biological_claim_authorized": "false",
        "runtime_still_blocked_in_this_pr": "true",
        "next_pr_must_use_reviewed_command_form": "true",
        "next_pr_must_use_reviewed_external_output_path": "true",
        "allowed_next_action_after_review": ALLOWED_NEXT_ACTION_AFTER_REVIEW,
        "claim_status": CLAIM_STATUS,
        "forbidden_actions_this_pr": FORBIDDEN_ACTIONS_THIS_PR,
        "review_note": REVIEW_NOTE,
    }


def read_dry_run_execution_plan_review_rows(
    path: Path = DEFAULT_TABLE,
) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{column: value or "" for column, value in row.items()} for row in reader]


def validate_dry_run_execution_plan_review_row(row: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    expected = build_dry_run_execution_plan_review_row()

    if list(row) != COLUMN_ORDER:
        errors.append("column order does not match dry-run execution plan review schema")

    for column, expected_value in expected.items():
        observed_value = str(row.get(column, "")).strip()
        if observed_value != expected_value:
            errors.append(f"expected {column}={expected_value!r}, observed {observed_value!r}")

    if row.get("review_decision") != REVIEW_DECISION:
        errors.append("review decision must approve or reject the selected plan explicitly")

    if row.get("dry_run_execution_authorized_for_next_pr") == "true":
        if row.get("selected_command_form_reviewed") != "true":
            errors.append("next-PR authorization requires reviewed command form")
        if row.get("selected_external_output_path_reviewed") != "true":
            errors.append("next-PR authorization requires reviewed external output path")

    for column in [
        "dry_run_execution_authorized_in_this_pr",
        "dry_run_executed",
        "live_execution_authorized",
        "manifest_execution_authorized_in_this_pr",
        "biohub_esmc_authorized",
        "embedding_generation_authorized",
        "npy_artifact_authorized",
        "output_file_created",
        "output_directory_created",
        "data_output_artifact_commit_authorized",
        "ready_for_preflight_authorized",
        "gate8_promotion_authorized",
        "gate9_promotion_authorized",
        "biological_claim_authorized",
    ]:
        if row.get(column) != "false":
            errors.append(f"{column} must remain false in the review PR")

    selected_output_path = row.get("selected_external_output_path", "")
    if "data/output" in selected_output_path.replace("\\", "/"):
        errors.append("selected external output path must not be under data/output")

    if selected_output_path.endswith(".npy"):
        errors.append("selected external output path must not be an .npy artifact")

    if not selected_output_path.startswith("D:/biohub_projects/_chatgpt_observations/"):
        errors.append("selected external output path must use the reviewed observations directory")

    command_form = row.get("selected_future_command_form", "")
    for required in [
        "uv run g3sx30-wrapper-dry-run",
        "--manifest data/input/g3sx30_dry_run_preflight_manifest.csv",
        "--manifest-row-index 1",
        "--output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json",
    ]:
        if required not in command_form:
            errors.append(f"selected future command form is missing {required!r}")

    return errors
