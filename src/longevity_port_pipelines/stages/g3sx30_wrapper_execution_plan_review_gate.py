from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path

DEFAULT_TABLE = Path("data/interim/g3sx30_wrapper_execution_plan_review_gate.csv")

FIELDS = (
    "source_actual_help_observation_doc",
    "source_entrypoint_boundary_module",
    "source_command_contract_table",
    "source_source_guardrail_table",
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
    "help_observation_status",
    "help_exit_code",
    "observed_help_target",
    "observed_manifest_option",
    "observed_manifest_row_index_option",
    "observed_output_path_option",
    "observed_help_option",
    "execution_plan_review_status",
    "execution_plan_review_decision",
    "dry_run_plan_review_required_before_execution",
    "non_committed_output_path_review_required",
    "output_path_selected_for_execution",
    "output_path_policy",
    "committed_data_output_rejected",
    "command_selected_for_execution",
    "execution_plan_materialized",
    "wrapper_execution_authorized",
    "dry_run_execution_authorized",
    "live_execution_authorized",
    "ready_for_preflight_authorized",
    "biohub_esmc_authorized",
    "embedding_generation_authorized",
    "npy_artifact_authorized",
    "data_output_artifact_commit_authorized",
    "gate8_promotion_authorized",
    "gate9_promotion_authorized",
    "biological_claim_authorized",
    "runtime_still_blocked",
    "allowed_next_action_after_review_gate",
    "claim_status",
    "forbidden_next_actions",
    "review_gate_note",
)

EXPECTED_REVIEW_GATE_ROW = {
    "source_actual_help_observation_doc": "docs/g3sx30_wrapper_actual_help_observation.md",
    "source_entrypoint_boundary_module": "src/longevity_port_pipelines/stages/g3sx30_wrapper_source_entrypoint_boundary.py",
    "source_command_contract_table": "data/interim/g3sx30_wrapper_command_contract_scaffold.csv",
    "source_source_guardrail_table": "data/interim/g3sx30_wrapper_source_guardrail_scaffold.csv",
    "source_manifest_table": "data/input/g3sx30_dry_run_preflight_manifest.csv",
    "source_manifest_row_index": "1",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "target_accession": "G3SX30",
    "target_accession_db": "UniProtKB TrEMBL",
    "target_species": "Loxodonta africana",
    "target_taxid": "9785",
    "gene_symbol": "MDM2",
    "reviewed_sequence_length": "492",
    "reviewed_sequence_sha256": "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
    "help_observation_status": "observed_help_only",
    "help_exit_code": "0",
    "observed_help_target": "g3sx30-wrapper-dry-run",
    "observed_manifest_option": "true",
    "observed_manifest_row_index_option": "true",
    "observed_output_path_option": "true",
    "observed_help_option": "true",
    "execution_plan_review_status": "execution_plan_review_gate_runtime_blocked",
    "execution_plan_review_decision": "require_separate_review_before_any_execution",
    "dry_run_plan_review_required_before_execution": "true",
    "non_committed_output_path_review_required": "true",
    "output_path_selected_for_execution": "false",
    "output_path_policy": "non_committed_output_path_required_before_future_dry_run",
    "committed_data_output_rejected": "true",
    "command_selected_for_execution": "false",
    "execution_plan_materialized": "false",
    "wrapper_execution_authorized": "false",
    "dry_run_execution_authorized": "false",
    "live_execution_authorized": "false",
    "ready_for_preflight_authorized": "false",
    "biohub_esmc_authorized": "false",
    "embedding_generation_authorized": "false",
    "npy_artifact_authorized": "false",
    "data_output_artifact_commit_authorized": "false",
    "gate8_promotion_authorized": "false",
    "gate9_promotion_authorized": "false",
    "biological_claim_authorized": "false",
    "runtime_still_blocked": "true",
    "allowed_next_action_after_review_gate": "add_g3sx30_wrapper_execution_plan_runtime_blocker",
    "claim_status": "technical_checkpoint",
    "forbidden_next_actions": "execute_wrapper; run_dry_run; run_live; execute_manifest; select_actual_command_for_execution; select_output_path_for_execution; materialize_execution_plan; allow_biohub_call; allow_esmc_call; allow_embedding_generation; allow_npy_artifact; commit_data_output_artifact; ready_for_preflight; promote_gate8; promote_gate9; biological_claim",
    "review_gate_note": "Execution-plan review gate only. Help has been observed, but this row does not select a command for execution, does not select an output path, does not materialize an execution plan, and keeps wrapper execution, dry-run execution, Biohub / ESMC, embedding generation, ready_for_preflight, Gate 8, Gate 9, and biological claims blocked.",
}

FALSE_FLAG_FIELDS = (
    "output_path_selected_for_execution",
    "command_selected_for_execution",
    "execution_plan_materialized",
    "wrapper_execution_authorized",
    "dry_run_execution_authorized",
    "live_execution_authorized",
    "ready_for_preflight_authorized",
    "biohub_esmc_authorized",
    "embedding_generation_authorized",
    "npy_artifact_authorized",
    "data_output_artifact_commit_authorized",
    "gate8_promotion_authorized",
    "gate9_promotion_authorized",
    "biological_claim_authorized",
)

TRUE_GUARDRAIL_FIELDS = (
    "observed_manifest_option",
    "observed_manifest_row_index_option",
    "observed_output_path_option",
    "observed_help_option",
    "dry_run_plan_review_required_before_execution",
    "non_committed_output_path_review_required",
    "committed_data_output_rejected",
    "runtime_still_blocked",
)


def build_execution_plan_review_gate_row() -> dict[str, str]:
    return dict(EXPECTED_REVIEW_GATE_ROW)


def read_execution_plan_review_gate_rows(path: Path = DEFAULT_TABLE) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_execution_plan_review_gate_row(row: Mapping[str, str]) -> list[str]:
    errors: list[str] = []

    for field in FIELDS:
        if field not in row:
            errors.append(f"missing field: {field}")

    for field, expected in EXPECTED_REVIEW_GATE_ROW.items():
        observed = row.get(field)
        if observed != expected:
            errors.append(f"{field}={observed!r} expected {expected!r}")

    for field in FALSE_FLAG_FIELDS:
        if row.get(field) != "false":
            errors.append(f"{field} must remain false")

    for field in TRUE_GUARDRAIL_FIELDS:
        if row.get(field) != "true":
            errors.append(f"{field} must be true")

    return errors
