from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path

DEFAULT_TABLE = Path("data/interim/g3sx30_wrapper_dry_run_execution_plan_scaffold.csv")

CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
TARGET_ACCESSION = "G3SX30"
TARGET_ACCESSION_DB = "UniProtKB TrEMBL"
TARGET_SPECIES = "Loxodonta africana"
TARGET_TAXID = "9785"
GENE_SYMBOL = "MDM2"
REVIEWED_SEQUENCE_LENGTH = "492"
REVIEWED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"

SOURCE_ENTRYPOINT_MODULE = (
    "src/longevity_port_pipelines/stages/g3sx30_wrapper_source_entrypoint_boundary.py"
)
SOURCE_EXECUTION_PLAN_REVIEW_GATE_TABLE = (
    "data/interim/g3sx30_wrapper_execution_plan_review_gate.csv"
)
SOURCE_MANIFEST_TABLE = "data/input/g3sx30_dry_run_preflight_manifest.csv"
SOURCE_MANIFEST_ROW_INDEX = "1"

SCRIPT_ENTRY_POINT = "g3sx30-wrapper-dry-run"
FUTURE_MANIFEST_PATH = "data/input/g3sx30_dry_run_preflight_manifest.csv"
FUTURE_MANIFEST_ROW_INDEX = "1"
FUTURE_OUTPUT_PATH = (
    "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
)
FUTURE_COMMAND_FORM = (
    "uv run g3sx30-wrapper-dry-run "
    "--manifest data/input/g3sx30_dry_run_preflight_manifest.csv "
    "--manifest-row-index 1 "
    "--output-path D:/biohub_projects/_chatgpt_observations/"
    "g3sx30_wrapper_dry_run_execution_plan.json"
)

EXECUTION_PLAN_SCAFFOLD_STATUS = "dry_run_execution_plan_scaffold_non_executable"
EXECUTION_PLAN_SCAFFOLD_DECISION = "select_future_command_form_and_external_output_path_only"
OUTPUT_PATH_POLICY = "external_non_committed_observation_path_only"
ALLOWED_OUTPUT_LOCATION_POLICY = "D:/biohub_projects/_chatgpt_observations only"
CLAIM_STATUS = "technical_checkpoint"
ALLOWED_NEXT_ACTION = "review_dry_run_execution_plan_scaffold_before_any_execution"

FORBIDDEN_NEXT_ACTIONS = (
    "execute_wrapper; run_dry_run; run_live; execute_manifest; "
    "call_biohub; call_esmc; generate_embeddings; create_npy_artifact; "
    "write_output_file; create_output_directory; commit_data_output_artifact; "
    "ready_for_preflight; promote_gate8; promote_gate9; biological_claim"
)

SCAFFOLD_NOTE = (
    "Non-executable dry-run execution plan scaffold only. This row selects a "
    "future command form and a future non-committed output path outside the "
    "repository. It does not select a command for execution, does not select an "
    "output path for execution, does not materialize a runtime execution plan, "
    "does not execute the wrapper, does not read the manifest, does not write "
    "the output path, and keeps Biohub / ESMC, embedding generation, "
    "ready_for_preflight, Gate 8, Gate 9, and biological claims blocked."
)

COLUMN_ORDER = [
    "source_entrypoint_boundary_module",
    "source_execution_plan_review_gate_table",
    "source_execution_plan_review_gate_row_index",
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
    "execution_plan_scaffold_status",
    "execution_plan_scaffold_decision",
    "script_entry_point",
    "future_command_form_selected",
    "future_command_form",
    "future_manifest_path",
    "future_manifest_row_index",
    "future_non_committed_output_path_selected",
    "future_output_path",
    "output_path_policy",
    "allowed_output_location_policy",
    "committed_data_output_rejected",
    "output_file_created",
    "output_directory_created",
    "command_selected_for_execution",
    "output_path_selected_for_execution",
    "execution_plan_materialized",
    "wrapper_execution_authorized",
    "dry_run_execution_authorized",
    "live_execution_authorized",
    "manifest_execution_authorized",
    "ready_for_preflight_authorized",
    "biohub_esmc_authorized",
    "embedding_generation_authorized",
    "npy_artifact_authorized",
    "data_output_artifact_commit_authorized",
    "gate8_promotion_authorized",
    "gate9_promotion_authorized",
    "biological_claim_authorized",
    "runtime_still_blocked",
    "dry_run_execution_plan_scaffold_only",
    "claim_status",
    "allowed_next_action_after_execution_plan_scaffold",
    "forbidden_next_actions",
    "scaffold_note",
]


def build_dry_run_execution_plan_scaffold_row() -> dict[str, str]:
    return {
        "source_entrypoint_boundary_module": SOURCE_ENTRYPOINT_MODULE,
        "source_execution_plan_review_gate_table": SOURCE_EXECUTION_PLAN_REVIEW_GATE_TABLE,
        "source_execution_plan_review_gate_row_index": "1",
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
        "execution_plan_scaffold_status": EXECUTION_PLAN_SCAFFOLD_STATUS,
        "execution_plan_scaffold_decision": EXECUTION_PLAN_SCAFFOLD_DECISION,
        "script_entry_point": SCRIPT_ENTRY_POINT,
        "future_command_form_selected": "true",
        "future_command_form": FUTURE_COMMAND_FORM,
        "future_manifest_path": FUTURE_MANIFEST_PATH,
        "future_manifest_row_index": FUTURE_MANIFEST_ROW_INDEX,
        "future_non_committed_output_path_selected": "true",
        "future_output_path": FUTURE_OUTPUT_PATH,
        "output_path_policy": OUTPUT_PATH_POLICY,
        "allowed_output_location_policy": ALLOWED_OUTPUT_LOCATION_POLICY,
        "committed_data_output_rejected": "true",
        "output_file_created": "false",
        "output_directory_created": "false",
        "command_selected_for_execution": "false",
        "output_path_selected_for_execution": "false",
        "execution_plan_materialized": "false",
        "wrapper_execution_authorized": "false",
        "dry_run_execution_authorized": "false",
        "live_execution_authorized": "false",
        "manifest_execution_authorized": "false",
        "ready_for_preflight_authorized": "false",
        "biohub_esmc_authorized": "false",
        "embedding_generation_authorized": "false",
        "npy_artifact_authorized": "false",
        "data_output_artifact_commit_authorized": "false",
        "gate8_promotion_authorized": "false",
        "gate9_promotion_authorized": "false",
        "biological_claim_authorized": "false",
        "runtime_still_blocked": "true",
        "dry_run_execution_plan_scaffold_only": "true",
        "claim_status": CLAIM_STATUS,
        "allowed_next_action_after_execution_plan_scaffold": ALLOWED_NEXT_ACTION,
        "forbidden_next_actions": FORBIDDEN_NEXT_ACTIONS,
        "scaffold_note": SCAFFOLD_NOTE,
    }


def read_dry_run_execution_plan_scaffold_rows(
    path: Path = DEFAULT_TABLE,
) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [{column: value or "" for column, value in row.items()} for row in reader]


def validate_dry_run_execution_plan_scaffold_row(row: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    expected = build_dry_run_execution_plan_scaffold_row()

    if list(row) != COLUMN_ORDER:
        errors.append("column order does not match dry-run execution plan scaffold schema")

    for column, expected_value in expected.items():
        observed_value = str(row.get(column, "")).strip()
        if observed_value != expected_value:
            errors.append(f"expected {column}={expected_value!r}, observed {observed_value!r}")

    if "data/output" in row.get("future_output_path", "").replace("\\", "/"):
        errors.append("future output path must not be under data/output")

    if row.get("future_output_path", "").endswith(".npy"):
        errors.append("future output path must not be an .npy artifact")

    future_command_tokens = set(row.get("future_command_form", "").lower().split())
    forbidden_runtime_tokens = {
        "biohub",
        "biohub-esmc",
        "esmc",
        "curated-embedding-preflight",
        "curated_embedding_preflight",
        "curated-embedding-single",
        "curated_embedding_single",
    }
    observed_forbidden_tokens = future_command_tokens & forbidden_runtime_tokens
    if observed_forbidden_tokens:
        errors.append(
            "future command form must not call runtime clients directly: "
            + ", ".join(sorted(observed_forbidden_tokens))
        )

    return errors
