from __future__ import annotations

from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.g3sx30_dry_run_preflight_manifest import (
    G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA,
    validate_g3sx30_dry_run_preflight_manifest_rows,
)
from longevity_port_pipelines.stages.g3sx30_manifest_aware_adapter_policy_contract import (
    validate_g3sx30_manifest_aware_adapter_policy_contract_rows,
)
from longevity_port_pipelines.stages.g3sx30_manifest_aware_dry_run_preflight_adapter import (
    EXPECTED_CANDIDATE_ID,
    EXPECTED_GENE_SYMBOL,
    EXPECTED_TARGET_ACCESSION,
    EXPECTED_TARGET_ACCESSION_DB,
    EXPECTED_TARGET_SPECIES,
    EXPECTED_TARGET_TAXID,
)
from longevity_port_pipelines.stages.g3sx30_manifest_aware_dry_run_wrapper_scaffold import (
    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows,
)
from longevity_port_pipelines.stages.g3sx30_wrapper_command_contract_scaffold import (
    ALLOWED_NEXT_ACTION_AFTER_COMMAND_CONTRACT,
    COMMAND_CONTRACT_DECISION,
    COMMAND_CONTRACT_STATUS,
    EXPECTED_COMMAND_FAMILY,
    validate_g3sx30_wrapper_command_contract_scaffold_rows,
)

DEFAULT_SOURCE_COMMAND_CONTRACT = Path("data/interim/g3sx30_wrapper_command_contract_scaffold.csv")
DEFAULT_SOURCE_WRAPPER_SCAFFOLD = Path(
    "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
)
DEFAULT_SOURCE_MANIFEST = Path("data/input/g3sx30_dry_run_preflight_manifest.csv")
DEFAULT_SOURCE_POLICY_CONTRACT = Path(
    "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
)

EXPECTED_REVIEWED_SEQUENCE_LENGTH = 492
EXPECTED_REVIEWED_SEQUENCE_SHA256 = (
    "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
)

SOURCE_GUARDRAIL_STATUS = "source_guardrail_scaffold_runtime_blocked"
SOURCE_GUARDRAIL_DECISION = "define_source_level_guardrails_only"
GUARDRAIL_SCOPE = "future_wrapper_source_checks_only"
GUARDRAIL_RUNTIME_EFFECT = "no_runtime_effect"
ALLOWED_NEXT_ACTION_AFTER_SOURCE_GUARDRAIL = "add_wrapper_help_observation_note_pr"
CLAIM_STATUS = "technical_checkpoint"
FORBIDDEN_NEXT_ACTIONS = "run_preflight; execute_wrapper; ready_for_preflight"

ALLOWED_SOURCE_GUARDRAIL_STATUSES = {SOURCE_GUARDRAIL_STATUS}
ALLOWED_SOURCE_GUARDRAIL_DECISIONS = {SOURCE_GUARDRAIL_DECISION}
ALLOWED_NEXT_ACTIONS_AFTER_SOURCE_GUARDRAIL = {
    "add_wrapper_help_observation_note_pr",
    "add_wrapper_guardrail_implementation_plan_pr",
    "keep_runtime_blocked",
}

FALSE_COLUMNS = [
    "source_actual_cli_help_observed",
    "source_actual_command_verified",
    "source_command_selected",
    "source_output_path_selected",
    "source_execution_plan_materialized",
    "source_guardrail_verification_observed",
    "source_guardrail_implemented",
    "actual_source_code_modified",
    "actual_cli_help_observed",
    "actual_command_verified",
    "wrapper_implementation_authorized",
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
]

TRUE_COLUMNS = [
    "source_runtime_still_blocked",
    "manifest_row_required",
    "accession_guardrail_required",
    "species_guardrail_required",
    "taxid_guardrail_required",
    "gene_symbol_guardrail_required",
    "reviewed_length_guardrail_required",
    "reviewed_sha256_guardrail_required",
    "max_live_batch_size_zero_required",
    "all_runtime_permissions_false_required",
    "non_committed_output_path_required_before_future_dry_run",
    "committed_data_output_rejected",
    "runtime_still_blocked",
]

SOURCE_GUARDRAIL_SCHEMA = {
    "source_command_contract_table": pl.Utf8,
    "source_command_contract_row_index": pl.Int64,
    "source_wrapper_scaffold_table": pl.Utf8,
    "source_wrapper_scaffold_row_index": pl.Int64,
    "source_manifest_table": pl.Utf8,
    "source_manifest_row_index": pl.Int64,
    "source_policy_contract_table": pl.Utf8,
    "source_policy_contract_row_index": pl.Int64,
    "candidate_id": pl.Utf8,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "reviewed_sequence_length": pl.Int64,
    "reviewed_sequence_sha256": pl.Utf8,
    "source_command_contract_status": pl.Utf8,
    "source_command_contract_decision": pl.Utf8,
    "source_expected_command_family": pl.Utf8,
    "source_actual_cli_help_observed": pl.Boolean,
    "source_actual_command_verified": pl.Boolean,
    "source_command_selected": pl.Boolean,
    "source_output_path_selected": pl.Boolean,
    "source_execution_plan_materialized": pl.Boolean,
    "source_runtime_still_blocked": pl.Boolean,
    "source_guardrail_status": pl.Utf8,
    "source_guardrail_decision": pl.Utf8,
    "guardrail_scope": pl.Utf8,
    "guardrail_runtime_effect": pl.Utf8,
    "manifest_row_required": pl.Boolean,
    "manifest_row_index_required": pl.Int64,
    "accession_guardrail_required": pl.Boolean,
    "species_guardrail_required": pl.Boolean,
    "taxid_guardrail_required": pl.Boolean,
    "gene_symbol_guardrail_required": pl.Boolean,
    "reviewed_length_guardrail_required": pl.Boolean,
    "reviewed_sha256_guardrail_required": pl.Boolean,
    "max_live_batch_size_zero_required": pl.Boolean,
    "all_runtime_permissions_false_required": pl.Boolean,
    "non_committed_output_path_required_before_future_dry_run": pl.Boolean,
    "committed_data_output_rejected": pl.Boolean,
    "source_guardrail_verification_observed": pl.Boolean,
    "source_guardrail_implemented": pl.Boolean,
    "actual_source_code_modified": pl.Boolean,
    "actual_cli_help_observed": pl.Boolean,
    "actual_command_verified": pl.Boolean,
    "wrapper_implementation_authorized": pl.Boolean,
    "wrapper_execution_authorized": pl.Boolean,
    "dry_run_execution_authorized": pl.Boolean,
    "live_execution_authorized": pl.Boolean,
    "ready_for_preflight_authorized": pl.Boolean,
    "biohub_esmc_authorized": pl.Boolean,
    "embedding_generation_authorized": pl.Boolean,
    "npy_artifact_authorized": pl.Boolean,
    "data_output_artifact_commit_authorized": pl.Boolean,
    "gate8_promotion_authorized": pl.Boolean,
    "gate9_promotion_authorized": pl.Boolean,
    "biological_claim_authorized": pl.Boolean,
    "allowed_next_action_after_source_guardrail": pl.Utf8,
    "claim_status": pl.Utf8,
    "runtime_still_blocked": pl.Boolean,
    "forbidden_next_actions": pl.Utf8,
    "guardrail_note": pl.Utf8,
}
REQUIRED_COLUMNS = list(SOURCE_GUARDRAIL_SCHEMA)


def empty_g3sx30_wrapper_source_guardrail_scaffold_table() -> pl.DataFrame:
    return pl.DataFrame(schema=SOURCE_GUARDRAIL_SCHEMA)


def read_g3sx30_dry_run_preflight_manifest(
    path: Path = DEFAULT_SOURCE_MANIFEST,
) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)


def read_g3sx30_wrapper_source_guardrail_scaffold(path: Path) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=SOURCE_GUARDRAIL_SCHEMA)


def _row_str(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        raise ValueError(f"Missing value for {column}")
    if isinstance(value, bool):
        return str(value).lower()
    return str(value).strip()


def _row_int(row: dict[str, object], column: str) -> int:
    value = row[column]
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        return int(value.strip())
    raise ValueError(f"Cannot interpret integer value for {column}: {value!r}")


def _row_bool(row: dict[str, object], column: str) -> bool:
    value = row[column]
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError(f"Invalid boolean value for {column}: {value}")


def _select_row(table: pl.DataFrame, row_index: int, label: str) -> dict[str, object]:
    if row_index < 1:
        raise ValueError(f"{label} row index is 1-based and must be positive")
    if row_index > table.height:
        raise ValueError(f"Missing {label} row index {row_index}; table has {table.height} rows")
    return table.row(row_index - 1, named=True)


def _require_identity(row: dict[str, object], label: str) -> None:
    expected = {
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
    }
    for column, expected_text in expected.items():
        if _row_str(row, column) != expected_text:
            raise ValueError(f"Expected {label} {column}={expected_text!r}")
    if _row_int(row, "target_taxid") != EXPECTED_TARGET_TAXID:
        raise ValueError(f"Expected {label} target_taxid={EXPECTED_TARGET_TAXID}")


def _require_command_contract(row: dict[str, object]) -> None:
    _require_identity(row, "command contract")
    expected = {
        "command_contract_status": COMMAND_CONTRACT_STATUS,
        "command_contract_decision": COMMAND_CONTRACT_DECISION,
        "expected_command_family": EXPECTED_COMMAND_FAMILY,
        "allowed_next_action_after_command_contract": ALLOWED_NEXT_ACTION_AFTER_COMMAND_CONTRACT,
        "claim_status": CLAIM_STATUS,
    }
    for column, expected_text in expected.items():
        if _row_str(row, column) != expected_text:
            raise ValueError(f"Expected command contract {column}={expected_text!r}")

    for column in [
        "actual_cli_help_observed",
        "actual_command_verified",
        "command_selected",
        "output_path_selected",
        "execution_plan_materialized",
        "execution_authorized",
        "wrapper_execution_authorized",
        "dry_run_execution_authorized",
        "live_execution_authorized",
        "ready_for_preflight_authorized",
        "biohub_esmc_authorized",
        "embedding_generation_authorized",
        "npy_artifact_authorized",
        "data_output_artifact_commit_authorized",
    ]:
        if _row_bool(row, column):
            raise ValueError(f"Command contract source must keep {column}=false")
    if not _row_bool(row, "runtime_still_blocked"):
        raise ValueError("Command contract source must keep runtime_still_blocked=true")


def _require_manifest(row: dict[str, object]) -> None:
    _require_identity(row, "manifest")
    if _row_int(row, "reviewed_sequence_length") != EXPECTED_REVIEWED_SEQUENCE_LENGTH:
        raise ValueError("Manifest reviewed_sequence_length must be 492")
    if _row_str(row, "reviewed_sequence_sha256") != EXPECTED_REVIEWED_SEQUENCE_SHA256:
        raise ValueError("Manifest reviewed_sequence_sha256 mismatch")
    if _row_int(row, "max_live_batch_size") != 0:
        raise ValueError("Manifest max_live_batch_size must remain 0")
    if _row_str(row, "ready_for_preflight_after_manifest") != "false":
        raise ValueError("Manifest ready_for_preflight_after_manifest must remain false")
    for column in [
        "sequence_fetch_allowed",
        "biohub_call_allowed",
        "esmc_call_allowed",
        "embedding_generation_allowed",
        "curated_embedding_preflight_allowed",
        "curated_embedding_single_allowed",
    ]:
        if _row_bool(row, column):
            raise ValueError(f"Manifest source must keep {column}=false")


def _require_policy(row: dict[str, object]) -> None:
    _require_identity(row, "policy contract")
    for column in [
        "wrapper_execution_decision",
        "dry_run_execution_decision",
        "live_execution_decision",
        "ready_for_preflight_decision",
        "biohub_esmc_decision",
        "embedding_generation_decision",
        "artifact_decision",
    ]:
        if _row_str(row, column) != "not_authorized":
            raise ValueError(f"Policy contract must keep {column}=not_authorized")


def build_g3sx30_wrapper_source_guardrail_scaffold_table(
    command_contract: pl.DataFrame,
    wrapper_scaffold: pl.DataFrame,
    manifest: pl.DataFrame,
    policy_contract: pl.DataFrame,
    *,
    allowed_next_action_after_source_guardrail: str = ALLOWED_NEXT_ACTION_AFTER_SOURCE_GUARDRAIL,
) -> pl.DataFrame:
    validate_g3sx30_wrapper_command_contract_scaffold_rows(command_contract)
    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows(wrapper_scaffold)
    validate_g3sx30_dry_run_preflight_manifest_rows(manifest)
    validate_g3sx30_manifest_aware_adapter_policy_contract_rows(policy_contract)

    if (
        allowed_next_action_after_source_guardrail
        not in ALLOWED_NEXT_ACTIONS_AFTER_SOURCE_GUARDRAIL
    ):
        raise ValueError(
            "Invalid allowed_next_action_after_source_guardrail: "
            f"{allowed_next_action_after_source_guardrail}"
        )

    command_row = _select_row(command_contract, 1, "command contract")
    wrapper_row = _select_row(wrapper_scaffold, 1, "wrapper scaffold")
    manifest_row = _select_row(manifest, 1, "manifest")
    policy_row = _select_row(policy_contract, 1, "policy contract")

    _require_command_contract(command_row)
    _require_identity(wrapper_row, "wrapper scaffold")
    _require_manifest(manifest_row)
    _require_policy(policy_row)

    row = {
        "source_command_contract_table": "data/interim/g3sx30_wrapper_command_contract_scaffold.csv",
        "source_command_contract_row_index": 1,
        "source_wrapper_scaffold_table": (
            "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
        ),
        "source_wrapper_scaffold_row_index": 1,
        "source_manifest_table": "data/input/g3sx30_dry_run_preflight_manifest.csv",
        "source_manifest_row_index": 1,
        "source_policy_contract_table": (
            "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
        ),
        "source_policy_contract_row_index": 1,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "reviewed_sequence_length": _row_int(manifest_row, "reviewed_sequence_length"),
        "reviewed_sequence_sha256": _row_str(manifest_row, "reviewed_sequence_sha256"),
        "source_command_contract_status": _row_str(command_row, "command_contract_status"),
        "source_command_contract_decision": _row_str(command_row, "command_contract_decision"),
        "source_expected_command_family": _row_str(command_row, "expected_command_family"),
        "source_actual_cli_help_observed": _row_bool(command_row, "actual_cli_help_observed"),
        "source_actual_command_verified": _row_bool(command_row, "actual_command_verified"),
        "source_command_selected": _row_bool(command_row, "command_selected"),
        "source_output_path_selected": _row_bool(command_row, "output_path_selected"),
        "source_execution_plan_materialized": _row_bool(command_row, "execution_plan_materialized"),
        "source_runtime_still_blocked": _row_bool(command_row, "runtime_still_blocked"),
        "source_guardrail_status": SOURCE_GUARDRAIL_STATUS,
        "source_guardrail_decision": SOURCE_GUARDRAIL_DECISION,
        "guardrail_scope": GUARDRAIL_SCOPE,
        "guardrail_runtime_effect": GUARDRAIL_RUNTIME_EFFECT,
        "manifest_row_required": True,
        "manifest_row_index_required": 1,
        "accession_guardrail_required": True,
        "species_guardrail_required": True,
        "taxid_guardrail_required": True,
        "gene_symbol_guardrail_required": True,
        "reviewed_length_guardrail_required": True,
        "reviewed_sha256_guardrail_required": True,
        "max_live_batch_size_zero_required": True,
        "all_runtime_permissions_false_required": True,
        "non_committed_output_path_required_before_future_dry_run": True,
        "committed_data_output_rejected": True,
        "source_guardrail_verification_observed": False,
        "source_guardrail_implemented": False,
        "actual_source_code_modified": False,
        "actual_cli_help_observed": False,
        "actual_command_verified": False,
        "wrapper_implementation_authorized": False,
        "wrapper_execution_authorized": False,
        "dry_run_execution_authorized": False,
        "live_execution_authorized": False,
        "ready_for_preflight_authorized": False,
        "biohub_esmc_authorized": False,
        "embedding_generation_authorized": False,
        "npy_artifact_authorized": False,
        "data_output_artifact_commit_authorized": False,
        "gate8_promotion_authorized": False,
        "gate9_promotion_authorized": False,
        "biological_claim_authorized": False,
        "allowed_next_action_after_source_guardrail": (allowed_next_action_after_source_guardrail),
        "claim_status": CLAIM_STATUS,
        "runtime_still_blocked": True,
        "forbidden_next_actions": FORBIDDEN_NEXT_ACTIONS,
        "guardrail_note": (
            "Source guardrail scaffold row only. This row defines future wrapper source "
            "checks only, has no runtime effect, does not implement the wrapper, does "
            "not run --help, does not observe CLI flags, does not select a command, "
            "does not select an output path, does not execute anything, keeps G3SX30 "
            "runtime blocked, rejects Gate 8 / Gate 9 promotion, and makes no "
            "biological claim."
        ),
    }
    return pl.DataFrame([row], schema=SOURCE_GUARDRAIL_SCHEMA).select(REQUIRED_COLUMNS)


def validate_g3sx30_wrapper_source_guardrail_scaffold_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required wrapper source guardrail scaffold columns: {missing}")


def validate_g3sx30_wrapper_source_guardrail_scaffold_rows(table: pl.DataFrame) -> None:
    validate_g3sx30_wrapper_source_guardrail_scaffold_schema(table)
    for row in table.iter_rows(named=True):
        expected = {
            "source_command_contract_table": (
                "data/interim/g3sx30_wrapper_command_contract_scaffold.csv"
            ),
            "source_wrapper_scaffold_table": (
                "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
            ),
            "source_manifest_table": "data/input/g3sx30_dry_run_preflight_manifest.csv",
            "source_policy_contract_table": (
                "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
            ),
            "candidate_id": EXPECTED_CANDIDATE_ID,
            "target_accession": EXPECTED_TARGET_ACCESSION,
            "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
            "target_species": EXPECTED_TARGET_SPECIES,
            "gene_symbol": EXPECTED_GENE_SYMBOL,
            "reviewed_sequence_sha256": EXPECTED_REVIEWED_SEQUENCE_SHA256,
            "source_command_contract_status": COMMAND_CONTRACT_STATUS,
            "source_command_contract_decision": COMMAND_CONTRACT_DECISION,
            "source_expected_command_family": EXPECTED_COMMAND_FAMILY,
            "source_guardrail_status": SOURCE_GUARDRAIL_STATUS,
            "source_guardrail_decision": SOURCE_GUARDRAIL_DECISION,
            "guardrail_scope": GUARDRAIL_SCOPE,
            "guardrail_runtime_effect": GUARDRAIL_RUNTIME_EFFECT,
            "allowed_next_action_after_source_guardrail": (
                ALLOWED_NEXT_ACTION_AFTER_SOURCE_GUARDRAIL
            ),
            "claim_status": CLAIM_STATUS,
            "forbidden_next_actions": FORBIDDEN_NEXT_ACTIONS,
        }
        for column, expected_text in expected.items():
            if _row_str(row, column) != expected_text:
                raise ValueError(f"Expected {column}={expected_text!r}")

        expected_ints = {
            "source_command_contract_row_index": 1,
            "source_wrapper_scaffold_row_index": 1,
            "source_manifest_row_index": 1,
            "source_policy_contract_row_index": 1,
            "target_taxid": EXPECTED_TARGET_TAXID,
            "reviewed_sequence_length": EXPECTED_REVIEWED_SEQUENCE_LENGTH,
            "manifest_row_index_required": 1,
        }
        for column, expected_int in expected_ints.items():
            if _row_int(row, column) != expected_int:
                raise ValueError(f"Expected {column}={expected_int}")

        for column in FALSE_COLUMNS:
            if _row_bool(row, column):
                raise ValueError(f"Source guardrail scaffold must keep {column}=false")
        for column in TRUE_COLUMNS:
            if not _row_bool(row, column):
                raise ValueError(f"Source guardrail scaffold must keep {column}=true")

        for forbidden in ["run_preflight", "execute_wrapper", "ready_for_preflight"]:
            if forbidden not in _row_str(row, "forbidden_next_actions"):
                raise ValueError(f"Missing forbidden next action: {forbidden}")

        note = _row_str(row, "guardrail_note")
        for required in [
            "future wrapper source checks only",
            "has no runtime effect",
            "does not implement the wrapper",
            "does not run --help",
            "does not observe CLI flags",
            "does not select a command",
            "does not select an output path",
            "does not execute anything",
            "keeps G3SX30 runtime blocked",
            "rejects Gate 8 / Gate 9 promotion",
            "makes no biological claim",
        ]:
            if required not in note:
                raise ValueError(f"Missing source guardrail note: {required}")
