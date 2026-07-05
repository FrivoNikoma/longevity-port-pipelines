from __future__ import annotations

from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.g3sx30_dry_run_preflight_manifest import (
    G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA,
    validate_g3sx30_dry_run_preflight_manifest_rows,
)
from longevity_port_pipelines.stages.g3sx30_manifest_aware_adapter_policy_contract import (
    ALLOWED_NEXT_ACTION_AFTER_POLICY,
    CURRENT_CLI_DIRECT_EXECUTION_DECISION,
    NOT_AUTHORIZED,
    POLICY_DECISION,
    POLICY_STATUS,
    WRAPPER_SCAFFOLD_DECISION,
    validate_g3sx30_manifest_aware_adapter_policy_contract_rows,
)
from longevity_port_pipelines.stages.g3sx30_manifest_aware_dry_run_preflight_adapter import (
    ADAPTER_DECISION,
    ADAPTER_STATUS,
    CURRENT_CLI_COMPATIBILITY,
    EXPECTED_CANDIDATE_ID,
    EXPECTED_GENE_SYMBOL,
    EXPECTED_TARGET_ACCESSION,
    EXPECTED_TARGET_ACCESSION_DB,
    EXPECTED_TARGET_SPECIES,
    EXPECTED_TARGET_TAXID,
    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_rows,
)

DEFAULT_SOURCE_POLICY_CONTRACT = Path(
    "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
)
DEFAULT_SOURCE_POLICY_CONTRACT_ROW_INDEX = 1
DEFAULT_SOURCE_ADAPTER_SCAFFOLD = Path(
    "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
)
DEFAULT_SOURCE_ADAPTER_SCAFFOLD_ROW_INDEX = 1
DEFAULT_SOURCE_MANIFEST = Path("data/input/g3sx30_dry_run_preflight_manifest.csv")
DEFAULT_SOURCE_MANIFEST_ROW_INDEX = 1

MANIFEST_ENTRY_STATUS = "manifest_scaffold_ready_runtime_blocked"
WRAPPER_STATUS = "wrapper_scaffold_runtime_blocked"
WRAPPER_DECISION = "prepare_wrapper_plan_only"
ALLOWED_NEXT_ACTION_AFTER_WRAPPER_SCAFFOLD = "add_wrapper_command_contract_pr"
CLAIM_STATUS = "technical_checkpoint"

ALLOWED_WRAPPER_STATUSES = {WRAPPER_STATUS}
ALLOWED_WRAPPER_DECISIONS = {WRAPPER_DECISION}
ALLOWED_NEXT_ACTIONS_AFTER_WRAPPER_SCAFFOLD = {
    "add_wrapper_command_contract_pr",
    "add_source_level_wrapper_guardrail_pr",
    "keep_runtime_blocked",
}

FORBIDDEN_ACTIONS = (
    "pyproject script entry point; Typer executable wrapper; manifest-aware wrapper implementation; "
    "wrapper execution; dry-run execution; live execution; curated-embedding-preflight run; "
    "curated_embedding_preflight run; curated-embedding-single run; curated_embedding_single run; "
    "help run; command selection; output path selection; execution plan materialization; "
    "Biohub call; ESMC call; embedding generation; .npy artifact; data/output artifact commit; "
    "ready_for_preflight; manifest runtime unlock; Gate 8 promotion; Gate 9 promotion; "
    "Boltz call; AF3 call; Chai call; enrichment rerun; contrast rerun; biological claim"
)

WRAPPER_SCAFFOLD_SCHEMA = {
    "source_policy_contract_table": pl.Utf8,
    "source_policy_contract_row_index": pl.Int64,
    "source_adapter_scaffold_table": pl.Utf8,
    "source_adapter_scaffold_row_index": pl.Int64,
    "source_manifest_table": pl.Utf8,
    "source_manifest_row_index": pl.Int64,
    "candidate_id": pl.Utf8,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "manifest_entry_status": pl.Utf8,
    "adapter_status": pl.Utf8,
    "adapter_decision": pl.Utf8,
    "current_cli_compatibility": pl.Utf8,
    "policy_contract_status": pl.Utf8,
    "policy_contract_decision": pl.Utf8,
    "current_cli_direct_execution_decision": pl.Utf8,
    "wrapper_scaffold_decision": pl.Utf8,
    "wrapper_status": pl.Utf8,
    "wrapper_decision": pl.Utf8,
    "wrapper_execution_decision": pl.Utf8,
    "dry_run_execution_decision": pl.Utf8,
    "live_execution_decision": pl.Utf8,
    "ready_for_preflight_decision": pl.Utf8,
    "biohub_esmc_decision": pl.Utf8,
    "embedding_generation_decision": pl.Utf8,
    "artifact_decision": pl.Utf8,
    "pyproject_entry_point_allowed": pl.Boolean,
    "typer_executable_wrapper_allowed": pl.Boolean,
    "manifest_aware_wrapper_implementation_allowed": pl.Boolean,
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
    "command_selected": pl.Boolean,
    "output_path_selected": pl.Boolean,
    "execution_plan_materialized": pl.Boolean,
    "runtime_still_blocked": pl.Boolean,
    "allowed_next_action_after_wrapper_scaffold": pl.Utf8,
    "claim_status": pl.Utf8,
    "forbidden_actions": pl.Utf8,
    "scaffold_note": pl.Utf8,
}

REQUIRED_COLUMNS = list(WRAPPER_SCAFFOLD_SCHEMA)


def empty_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table() -> pl.DataFrame:
    return pl.DataFrame(schema=WRAPPER_SCAFFOLD_SCHEMA)


def read_g3sx30_dry_run_preflight_manifest(
    path: Path = DEFAULT_SOURCE_MANIFEST,
) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)


def read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(path: Path) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=WRAPPER_SCAFFOLD_SCHEMA)


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


def _require_policy_contract_allows_scaffold_only(row: dict[str, object]) -> None:
    expected_strings = {
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "adapter_status": ADAPTER_STATUS,
        "adapter_decision": ADAPTER_DECISION,
        "current_cli_compatibility": CURRENT_CLI_COMPATIBILITY,
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
        "claim_status": CLAIM_STATUS,
    }
    for column, expected_text in expected_strings.items():
        observed_text = _row_str(row, column)
        if observed_text != expected_text:
            raise ValueError(
                f"Expected policy contract {column}={expected_text!r}, observed {observed_text!r}"
            )

    if _row_int(row, "target_taxid") != EXPECTED_TARGET_TAXID:
        raise ValueError(f"Expected policy contract target_taxid={EXPECTED_TARGET_TAXID}")

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
            raise ValueError(f"Policy contract must keep {column}=false")


def _require_manifest_runtime_blocked(row: dict[str, object]) -> None:
    expected_strings = {
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "manifest_entry_status": MANIFEST_ENTRY_STATUS,
        "ready_for_preflight_after_manifest": "false",
        "claim_status": CLAIM_STATUS,
    }
    for column, expected_text in expected_strings.items():
        observed_text = _row_str(row, column)
        if observed_text != expected_text:
            raise ValueError(
                f"Expected manifest {column}={expected_text!r}, observed {observed_text!r}"
            )

    if _row_int(row, "target_taxid") != EXPECTED_TARGET_TAXID:
        raise ValueError(f"Expected manifest target_taxid={EXPECTED_TARGET_TAXID}")
    if _row_int(row, "max_live_batch_size") != 0:
        raise ValueError("Manifest max_live_batch_size must remain 0")
    if not _row_bool(row, "dry_run_only"):
        raise ValueError("Manifest must keep dry_run_only=true")

    for column in [
        "sequence_fetch_allowed",
        "biohub_call_allowed",
        "esmc_call_allowed",
        "embedding_generation_allowed",
        "curated_embedding_preflight_allowed",
        "curated_embedding_single_allowed",
    ]:
        if _row_bool(row, column):
            raise ValueError(f"Manifest must keep {column}=false")


def build_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table(
    policy_contract: pl.DataFrame,
    adapter_scaffold: pl.DataFrame,
    manifest: pl.DataFrame,
    *,
    source_policy_contract_table: str = "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv",
    source_policy_contract_row_index: int = DEFAULT_SOURCE_POLICY_CONTRACT_ROW_INDEX,
    source_adapter_scaffold_table: str = (
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
    ),
    source_adapter_scaffold_row_index: int = DEFAULT_SOURCE_ADAPTER_SCAFFOLD_ROW_INDEX,
    source_manifest_table: str = "data/input/g3sx30_dry_run_preflight_manifest.csv",
    source_manifest_row_index: int = DEFAULT_SOURCE_MANIFEST_ROW_INDEX,
    allowed_next_action_after_wrapper_scaffold: str = ALLOWED_NEXT_ACTION_AFTER_WRAPPER_SCAFFOLD,
) -> pl.DataFrame:
    validate_g3sx30_manifest_aware_adapter_policy_contract_rows(policy_contract)
    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_rows(adapter_scaffold)
    validate_g3sx30_dry_run_preflight_manifest_rows(manifest)

    if (
        allowed_next_action_after_wrapper_scaffold
        not in ALLOWED_NEXT_ACTIONS_AFTER_WRAPPER_SCAFFOLD
    ):
        raise ValueError(
            "Invalid allowed_next_action_after_wrapper_scaffold: "
            f"{allowed_next_action_after_wrapper_scaffold}"
        )

    policy_row = _select_row(
        policy_contract,
        source_policy_contract_row_index,
        "policy contract",
    )
    adapter_row = _select_row(
        adapter_scaffold,
        source_adapter_scaffold_row_index,
        "adapter scaffold",
    )
    manifest_row = _select_row(manifest, source_manifest_row_index, "manifest")

    _require_policy_contract_allows_scaffold_only(policy_row)
    _require_manifest_runtime_blocked(manifest_row)

    # The adapter validator already enforces the adapter row semantics. This identity
    # check keeps the wrapper scaffold tied to the same concrete source rows.
    for column in [
        "candidate_id",
        "target_accession",
        "target_accession_db",
        "target_species",
        "gene_symbol",
    ]:
        values = {
            _row_str(policy_row, column),
            _row_str(adapter_row, column),
            _row_str(manifest_row, column),
        }
        if len(values) != 1:
            raise ValueError(f"Source rows disagree on {column}: {sorted(values)}")

    if _row_int(policy_row, "target_taxid") != _row_int(adapter_row, "target_taxid"):
        raise ValueError("Policy contract and adapter scaffold disagree on target_taxid")
    if _row_int(policy_row, "target_taxid") != _row_int(manifest_row, "target_taxid"):
        raise ValueError("Policy contract and manifest disagree on target_taxid")

    scaffold_note = (
        "Wrapper scaffold row only. The source policy contract, adapter scaffold, and manifest row are "
        "understood, but this scaffold is not executable. It selects no command, selects no output path, "
        "does not materialize an execution plan, and keeps runtime blocked. A later PR may define a "
        "wrapper command contract or source-level wrapper guardrail."
    )

    return pl.DataFrame(
        [
            {
                "source_policy_contract_table": source_policy_contract_table,
                "source_policy_contract_row_index": source_policy_contract_row_index,
                "source_adapter_scaffold_table": source_adapter_scaffold_table,
                "source_adapter_scaffold_row_index": source_adapter_scaffold_row_index,
                "source_manifest_table": source_manifest_table,
                "source_manifest_row_index": source_manifest_row_index,
                "candidate_id": _row_str(policy_row, "candidate_id"),
                "target_accession": _row_str(policy_row, "target_accession"),
                "target_accession_db": _row_str(policy_row, "target_accession_db"),
                "target_species": _row_str(policy_row, "target_species"),
                "target_taxid": _row_int(policy_row, "target_taxid"),
                "gene_symbol": _row_str(policy_row, "gene_symbol"),
                "manifest_entry_status": _row_str(manifest_row, "manifest_entry_status"),
                "adapter_status": _row_str(policy_row, "adapter_status"),
                "adapter_decision": _row_str(policy_row, "adapter_decision"),
                "current_cli_compatibility": _row_str(policy_row, "current_cli_compatibility"),
                "policy_contract_status": _row_str(policy_row, "policy_status"),
                "policy_contract_decision": _row_str(policy_row, "policy_decision"),
                "current_cli_direct_execution_decision": _row_str(
                    policy_row,
                    "current_cli_direct_execution_decision",
                ),
                "wrapper_scaffold_decision": _row_str(policy_row, "wrapper_scaffold_decision"),
                "wrapper_status": WRAPPER_STATUS,
                "wrapper_decision": WRAPPER_DECISION,
                "wrapper_execution_decision": NOT_AUTHORIZED,
                "dry_run_execution_decision": NOT_AUTHORIZED,
                "live_execution_decision": NOT_AUTHORIZED,
                "ready_for_preflight_decision": NOT_AUTHORIZED,
                "biohub_esmc_decision": NOT_AUTHORIZED,
                "embedding_generation_decision": NOT_AUTHORIZED,
                "artifact_decision": NOT_AUTHORIZED,
                "pyproject_entry_point_allowed": False,
                "typer_executable_wrapper_allowed": False,
                "manifest_aware_wrapper_implementation_allowed": False,
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
                "command_selected": False,
                "output_path_selected": False,
                "execution_plan_materialized": False,
                "runtime_still_blocked": True,
                "allowed_next_action_after_wrapper_scaffold": allowed_next_action_after_wrapper_scaffold,
                "claim_status": CLAIM_STATUS,
                "forbidden_actions": FORBIDDEN_ACTIONS,
                "scaffold_note": scaffold_note,
            }
        ],
        schema=WRAPPER_SCAFFOLD_SCHEMA,
    ).select(REQUIRED_COLUMNS)


def validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required wrapper scaffold columns: {missing}")


def validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows(table: pl.DataFrame) -> None:
    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_schema(table)

    for row in table.iter_rows(named=True):
        expected_strings = {
            "source_policy_contract_table": "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv",
            "source_adapter_scaffold_table": (
                "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
            ),
            "source_manifest_table": "data/input/g3sx30_dry_run_preflight_manifest.csv",
            "candidate_id": EXPECTED_CANDIDATE_ID,
            "target_accession": EXPECTED_TARGET_ACCESSION,
            "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
            "target_species": EXPECTED_TARGET_SPECIES,
            "gene_symbol": EXPECTED_GENE_SYMBOL,
            "manifest_entry_status": MANIFEST_ENTRY_STATUS,
            "adapter_status": ADAPTER_STATUS,
            "adapter_decision": ADAPTER_DECISION,
            "current_cli_compatibility": CURRENT_CLI_COMPATIBILITY,
            "policy_contract_status": POLICY_STATUS,
            "policy_contract_decision": POLICY_DECISION,
            "current_cli_direct_execution_decision": CURRENT_CLI_DIRECT_EXECUTION_DECISION,
            "wrapper_scaffold_decision": WRAPPER_SCAFFOLD_DECISION,
            "wrapper_status": WRAPPER_STATUS,
            "wrapper_decision": WRAPPER_DECISION,
            "wrapper_execution_decision": NOT_AUTHORIZED,
            "dry_run_execution_decision": NOT_AUTHORIZED,
            "live_execution_decision": NOT_AUTHORIZED,
            "ready_for_preflight_decision": NOT_AUTHORIZED,
            "biohub_esmc_decision": NOT_AUTHORIZED,
            "embedding_generation_decision": NOT_AUTHORIZED,
            "artifact_decision": NOT_AUTHORIZED,
            "allowed_next_action_after_wrapper_scaffold": ALLOWED_NEXT_ACTION_AFTER_WRAPPER_SCAFFOLD,
            "claim_status": CLAIM_STATUS,
            "forbidden_actions": FORBIDDEN_ACTIONS,
        }
        for column, expected_text in expected_strings.items():
            observed_text = _row_str(row, column)
            if observed_text != expected_text:
                raise ValueError(f"Expected {column}={expected_text!r}, observed {observed_text!r}")

        expected_ints = {
            "source_policy_contract_row_index": 1,
            "source_adapter_scaffold_row_index": 1,
            "source_manifest_row_index": 1,
            "target_taxid": EXPECTED_TARGET_TAXID,
        }
        for column, expected_int in expected_ints.items():
            observed_int = _row_int(row, column)
            if observed_int != expected_int:
                raise ValueError(f"Expected {column}={expected_int}, observed {observed_int}")

        for column in [
            "pyproject_entry_point_allowed",
            "typer_executable_wrapper_allowed",
            "manifest_aware_wrapper_implementation_allowed",
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
            "command_selected",
            "output_path_selected",
            "execution_plan_materialized",
        ]:
            if _row_bool(row, column):
                raise ValueError(f"Wrapper scaffold must keep {column}=false")

        if not _row_bool(row, "runtime_still_blocked"):
            raise ValueError("Wrapper scaffold must keep runtime_still_blocked=true")

        scaffold_note = _row_str(row, "scaffold_note")
        for required in [
            "this scaffold is not executable",
            "selects no command",
            "selects no output path",
            "does not materialize an execution plan",
            "keeps runtime blocked",
            "A later PR may define a wrapper command contract or source-level wrapper guardrail",
        ]:
            if required not in scaffold_note:
                raise ValueError(f"Missing wrapper scaffold note: {required}")

        forbidden_actions = _row_str(row, "forbidden_actions")
        for required in [
            "pyproject script entry point",
            "Typer executable wrapper",
            "manifest-aware wrapper implementation",
            "wrapper execution",
            "dry-run execution",
            "live execution",
            "curated-embedding-preflight run",
            "curated_embedding_preflight run",
            "curated-embedding-single run",
            "curated_embedding_single run",
            "help run",
            "command selection",
            "output path selection",
            "execution plan materialization",
            "Biohub call",
            "ESMC call",
            "embedding generation",
            ".npy artifact",
            "data/output artifact commit",
            "ready_for_preflight",
            "manifest runtime unlock",
            "Gate 8 promotion",
            "Gate 9 promotion",
            "Boltz call",
            "AF3 call",
            "Chai call",
            "biological claim",
        ]:
            if required not in forbidden_actions:
                raise ValueError(f"Missing forbidden action guardrail: {required}")
