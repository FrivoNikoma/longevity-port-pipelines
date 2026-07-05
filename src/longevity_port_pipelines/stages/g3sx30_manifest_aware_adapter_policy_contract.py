from __future__ import annotations

from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.g3sx30_manifest_aware_dry_run_preflight_adapter import (
    ADAPTER_SCHEMA,
    ALLOWED_OUTPUT_LOCATION,
    CURRENT_CLI_COMPATIBILITY,
    EXPECTED_CANDIDATE_ID,
    EXPECTED_GENE_SYMBOL,
    EXPECTED_TARGET_ACCESSION,
    EXPECTED_TARGET_ACCESSION_DB,
    EXPECTED_TARGET_SPECIES,
    EXPECTED_TARGET_TAXID,
    OUTPUT_PATH_POLICY,
    REQUIRED_NEXT_ACTION,
    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_rows,
)

DEFAULT_SOURCE_ADAPTER_SCAFFOLD = Path(
    "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
)
DEFAULT_SOURCE_ADAPTER_SCAFFOLD_ROW_INDEX = 1

ADAPTER_STATUS = "manifest_understood_runtime_blocked"
ADAPTER_DECISION = "do_not_execute_current_cli_directly"

POLICY_STATUS = "adapter_policy_runtime_blocked"
POLICY_DECISION = "require_manifest_aware_wrapper_before_execution"
CURRENT_CLI_DIRECT_EXECUTION_DECISION = "reject_current_cli_direct_execution"
WRAPPER_SCAFFOLD_DECISION = "allow_wrapper_scaffold_only"
NOT_AUTHORIZED = "not_authorized"
ALLOWED_NEXT_ACTION_AFTER_POLICY = "prepare_manifest_aware_wrapper_scaffold_pr"
CLAIM_STATUS = "technical_checkpoint"

ALLOWED_ADAPTER_POLICY_STATUSES = {POLICY_STATUS}
ALLOWED_ADAPTER_POLICY_DECISIONS = {POLICY_DECISION}
ALLOWED_CURRENT_CLI_COMPATIBILITY_VALUES = {CURRENT_CLI_COMPATIBILITY}
ALLOWED_CURRENT_CLI_DIRECT_EXECUTION_DECISIONS = {CURRENT_CLI_DIRECT_EXECUTION_DECISION}
ALLOWED_WRAPPER_SCAFFOLD_DECISIONS = {WRAPPER_SCAFFOLD_DECISION}
ALLOWED_EXECUTION_DECISIONS = {NOT_AUTHORIZED}
ALLOWED_NEXT_ACTIONS_AFTER_ADAPTER_POLICY = {
    "prepare_manifest_aware_wrapper_scaffold_pr",
    "add_source_level_manifest_guardrail_before_execution",
    "keep_runtime_blocked",
}

BLOCKED_NEXT_ACTION_VOCABULARY = (
    "prepare_manifest_aware_wrapper_scaffold_pr; "
    "add_source_level_manifest_guardrail_before_execution; keep_runtime_blocked"
)

FORBIDDEN_EXECUTION_VOCABULARY = (
    "allow_dry_run_execution; run_curated_embedding_preflight; "
    "run_curated_embedding_single; execute_manifest; ready_for_preflight; "
    "allow_biohub_call; allow_esmc_call; allow_embedding_generation; "
    "allow_npy_artifact; allow_data_output_artifact; promote_gate8; promote_gate9"
)

POLICY_CONTRACT_SCHEMA = {
    "source_adapter_scaffold_table": pl.Utf8,
    "source_adapter_scaffold_row_index": pl.Int64,
    "candidate_id": pl.Utf8,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "adapter_status": pl.Utf8,
    "adapter_decision": pl.Utf8,
    "current_cli_compatibility": pl.Utf8,
    "source_required_next_action": pl.Utf8,
    "source_output_path_policy": pl.Utf8,
    "policy_status": pl.Utf8,
    "policy_decision": pl.Utf8,
    "current_cli_direct_execution_decision": pl.Utf8,
    "wrapper_scaffold_decision": pl.Utf8,
    "wrapper_execution_decision": pl.Utf8,
    "dry_run_execution_decision": pl.Utf8,
    "live_execution_decision": pl.Utf8,
    "ready_for_preflight_decision": pl.Utf8,
    "biohub_esmc_decision": pl.Utf8,
    "embedding_generation_decision": pl.Utf8,
    "artifact_decision": pl.Utf8,
    "pyproject_entry_point_allowed": pl.Boolean,
    "manifest_aware_wrapper_implementation_allowed": pl.Boolean,
    "current_cli_direct_execution_allowed": pl.Boolean,
    "wrapper_execution_allowed": pl.Boolean,
    "dry_run_execution_allowed": pl.Boolean,
    "live_execution_allowed": pl.Boolean,
    "ready_for_preflight_allowed": pl.Boolean,
    "biohub_call_allowed": pl.Boolean,
    "esmc_call_allowed": pl.Boolean,
    "embedding_generation_allowed": pl.Boolean,
    "npy_artifact_allowed": pl.Boolean,
    "data_output_artifact_commit_allowed": pl.Boolean,
    "gate8_promotion_allowed": pl.Boolean,
    "gate9_promotion_allowed": pl.Boolean,
    "biological_claim_allowed": pl.Boolean,
    "allowed_next_action_after_policy": pl.Utf8,
    "blocked_next_action_vocabulary": pl.Utf8,
    "claim_status": pl.Utf8,
    "forbidden_execution_vocabulary": pl.Utf8,
    "policy_note": pl.Utf8,
}

REQUIRED_COLUMNS = list(POLICY_CONTRACT_SCHEMA)


def empty_g3sx30_manifest_aware_adapter_policy_contract_table() -> pl.DataFrame:
    return pl.DataFrame(schema=POLICY_CONTRACT_SCHEMA)


def read_g3sx30_manifest_aware_adapter_scaffold(
    path: Path = DEFAULT_SOURCE_ADAPTER_SCAFFOLD,
) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=ADAPTER_SCHEMA)


def read_g3sx30_manifest_aware_adapter_policy_contract(path: Path) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=POLICY_CONTRACT_SCHEMA)


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


def _select_source_adapter_row(adapter_scaffold: pl.DataFrame, row_index: int) -> dict[str, object]:
    if row_index < 1:
        raise ValueError("source_adapter_scaffold_row_index is 1-based and must be positive")
    if row_index > adapter_scaffold.height:
        raise ValueError(
            f"Missing adapter scaffold row index {row_index}; "
            f"adapter scaffold has {adapter_scaffold.height} rows"
        )
    return adapter_scaffold.row(row_index - 1, named=True)


def _require_source_adapter_row_runtime_blocked(row: dict[str, object]) -> None:
    expected_strings = {
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "adapter_status": ADAPTER_STATUS,
        "adapter_decision": ADAPTER_DECISION,
        "current_cli_compatibility": CURRENT_CLI_COMPATIBILITY,
        "required_next_action": REQUIRED_NEXT_ACTION,
        "output_path_policy": OUTPUT_PATH_POLICY,
        "allowed_output_location": ALLOWED_OUTPUT_LOCATION,
        "claim_status": CLAIM_STATUS,
    }
    for column, expected_text in expected_strings.items():
        observed_text = _row_str(row, column)
        if observed_text != expected_text:
            raise ValueError(
                f"Expected source {column}={expected_text!r}, observed {observed_text!r}"
            )

    if _row_int(row, "target_taxid") != EXPECTED_TARGET_TAXID:
        raise ValueError(f"Expected source target_taxid={EXPECTED_TARGET_TAXID}")

    for column in [
        "curated_embedding_preflight_runtime_allowed",
        "curated_embedding_single_runtime_allowed",
    ]:
        if _row_bool(row, column):
            raise ValueError(f"Source adapter scaffold must keep {column}=false")


def build_g3sx30_manifest_aware_adapter_policy_contract_table(
    adapter_scaffold: pl.DataFrame,
    *,
    source_adapter_scaffold_table: str = (
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
    ),
    source_adapter_scaffold_row_index: int = DEFAULT_SOURCE_ADAPTER_SCAFFOLD_ROW_INDEX,
    allowed_next_action_after_policy: str = ALLOWED_NEXT_ACTION_AFTER_POLICY,
) -> pl.DataFrame:
    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_rows(adapter_scaffold)
    source_row = _select_source_adapter_row(adapter_scaffold, source_adapter_scaffold_row_index)
    _require_source_adapter_row_runtime_blocked(source_row)

    if allowed_next_action_after_policy not in ALLOWED_NEXT_ACTIONS_AFTER_ADAPTER_POLICY:
        raise ValueError(
            f"Invalid allowed_next_action_after_policy: {allowed_next_action_after_policy}"
        )

    policy_note = (
        "Policy contract row only. allow_wrapper_scaffold_only means only that a later PR may "
        "prepare a wrapper scaffold. It does not mean the wrapper exists, does not mean wrapper "
        "execution is allowed, and does not mean dry-run execution is allowed."
    )

    return pl.DataFrame(
        [
            {
                "source_adapter_scaffold_table": source_adapter_scaffold_table,
                "source_adapter_scaffold_row_index": source_adapter_scaffold_row_index,
                "candidate_id": _row_str(source_row, "candidate_id"),
                "target_accession": _row_str(source_row, "target_accession"),
                "target_accession_db": _row_str(source_row, "target_accession_db"),
                "target_species": _row_str(source_row, "target_species"),
                "target_taxid": _row_int(source_row, "target_taxid"),
                "gene_symbol": _row_str(source_row, "gene_symbol"),
                "adapter_status": _row_str(source_row, "adapter_status"),
                "adapter_decision": _row_str(source_row, "adapter_decision"),
                "current_cli_compatibility": _row_str(source_row, "current_cli_compatibility"),
                "source_required_next_action": _row_str(source_row, "required_next_action"),
                "source_output_path_policy": _row_str(source_row, "output_path_policy"),
                "policy_status": POLICY_STATUS,
                "policy_decision": POLICY_DECISION,
                "current_cli_direct_execution_decision": CURRENT_CLI_DIRECT_EXECUTION_DECISION,
                "wrapper_scaffold_decision": WRAPPER_SCAFFOLD_DECISION,
                "wrapper_execution_decision": NOT_AUTHORIZED,
                "dry_run_execution_decision": NOT_AUTHORIZED,
                "live_execution_decision": NOT_AUTHORIZED,
                "ready_for_preflight_decision": NOT_AUTHORIZED,
                "biohub_esmc_decision": NOT_AUTHORIZED,
                "embedding_generation_decision": NOT_AUTHORIZED,
                "artifact_decision": NOT_AUTHORIZED,
                "pyproject_entry_point_allowed": False,
                "manifest_aware_wrapper_implementation_allowed": False,
                "current_cli_direct_execution_allowed": False,
                "wrapper_execution_allowed": False,
                "dry_run_execution_allowed": False,
                "live_execution_allowed": False,
                "ready_for_preflight_allowed": False,
                "biohub_call_allowed": False,
                "esmc_call_allowed": False,
                "embedding_generation_allowed": False,
                "npy_artifact_allowed": False,
                "data_output_artifact_commit_allowed": False,
                "gate8_promotion_allowed": False,
                "gate9_promotion_allowed": False,
                "biological_claim_allowed": False,
                "allowed_next_action_after_policy": allowed_next_action_after_policy,
                "blocked_next_action_vocabulary": BLOCKED_NEXT_ACTION_VOCABULARY,
                "claim_status": CLAIM_STATUS,
                "forbidden_execution_vocabulary": FORBIDDEN_EXECUTION_VOCABULARY,
                "policy_note": policy_note,
            }
        ],
        schema=POLICY_CONTRACT_SCHEMA,
    ).select(REQUIRED_COLUMNS)


def validate_g3sx30_manifest_aware_adapter_policy_contract_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required adapter policy contract columns: {missing}")


def _reject_forbidden_execution_vocabulary(value: str) -> None:
    for forbidden in [
        "allow_dry_run_execution",
        "run_curated_embedding_preflight",
        "run_curated_embedding_single",
        "execute_manifest",
        "ready_for_preflight",
        "allow_biohub_call",
        "allow_esmc_call",
        "allow_embedding_generation",
        "allow_npy_artifact",
        "allow_data_output_artifact",
        "promote_gate8",
        "promote_gate9",
    ]:
        if value == forbidden:
            raise ValueError(f"Forbidden execution-permitting vocabulary value: {forbidden}")


def validate_g3sx30_manifest_aware_adapter_policy_contract_rows(table: pl.DataFrame) -> None:
    validate_g3sx30_manifest_aware_adapter_policy_contract_schema(table)

    for row in table.iter_rows(named=True):
        expected_strings = {
            "source_adapter_scaffold_table": (
                "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
            ),
            "candidate_id": EXPECTED_CANDIDATE_ID,
            "target_accession": EXPECTED_TARGET_ACCESSION,
            "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
            "target_species": EXPECTED_TARGET_SPECIES,
            "gene_symbol": EXPECTED_GENE_SYMBOL,
            "adapter_status": ADAPTER_STATUS,
            "adapter_decision": ADAPTER_DECISION,
            "current_cli_compatibility": CURRENT_CLI_COMPATIBILITY,
            "source_required_next_action": REQUIRED_NEXT_ACTION,
            "source_output_path_policy": OUTPUT_PATH_POLICY,
            "policy_status": POLICY_STATUS,
            "policy_decision": POLICY_DECISION,
            "current_cli_direct_execution_decision": CURRENT_CLI_DIRECT_EXECUTION_DECISION,
            "wrapper_scaffold_decision": WRAPPER_SCAFFOLD_DECISION,
            "wrapper_execution_decision": NOT_AUTHORIZED,
            "dry_run_execution_decision": NOT_AUTHORIZED,
            "live_execution_decision": NOT_AUTHORIZED,
            "ready_for_preflight_decision": NOT_AUTHORIZED,
            "biohub_esmc_decision": NOT_AUTHORIZED,
            "embedding_generation_decision": NOT_AUTHORIZED,
            "artifact_decision": NOT_AUTHORIZED,
            "allowed_next_action_after_policy": ALLOWED_NEXT_ACTION_AFTER_POLICY,
            "blocked_next_action_vocabulary": BLOCKED_NEXT_ACTION_VOCABULARY,
            "claim_status": CLAIM_STATUS,
            "forbidden_execution_vocabulary": FORBIDDEN_EXECUTION_VOCABULARY,
        }
        for column, expected_text in expected_strings.items():
            observed_text = _row_str(row, column)
            if observed_text != expected_text:
                raise ValueError(f"Expected {column}={expected_text!r}, observed {observed_text!r}")
            _reject_forbidden_execution_vocabulary(observed_text)

        if _row_int(row, "source_adapter_scaffold_row_index") != 1:
            raise ValueError("Adapter policy contract must reference source adapter scaffold row 1")
        if _row_int(row, "target_taxid") != EXPECTED_TARGET_TAXID:
            raise ValueError(f"Expected target_taxid={EXPECTED_TARGET_TAXID}")

        for column in [
            "pyproject_entry_point_allowed",
            "manifest_aware_wrapper_implementation_allowed",
            "current_cli_direct_execution_allowed",
            "wrapper_execution_allowed",
            "dry_run_execution_allowed",
            "live_execution_allowed",
            "ready_for_preflight_allowed",
            "biohub_call_allowed",
            "esmc_call_allowed",
            "embedding_generation_allowed",
            "npy_artifact_allowed",
            "data_output_artifact_commit_allowed",
            "gate8_promotion_allowed",
            "gate9_promotion_allowed",
            "biological_claim_allowed",
        ]:
            if _row_bool(row, column):
                raise ValueError(f"Adapter policy contract must keep {column}=false")

        policy_note = _row_str(row, "policy_note")
        for required in [
            "allow_wrapper_scaffold_only means only that a later PR may prepare a wrapper scaffold",
            "does not mean the wrapper exists",
            "does not mean wrapper execution is allowed",
            "does not mean dry-run execution is allowed",
        ]:
            if required not in policy_note:
                raise ValueError(f"Missing wrapper scaffold only policy note: {required}")
