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
    WRAPPER_DECISION,
    WRAPPER_STATUS,
    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows,
)

DEFAULT_SOURCE_WRAPPER_SCAFFOLD = Path(
    "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
)
DEFAULT_SOURCE_WRAPPER_SCAFFOLD_ROW_INDEX = 1
DEFAULT_SOURCE_POLICY_CONTRACT = Path(
    "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
)
DEFAULT_SOURCE_POLICY_CONTRACT_ROW_INDEX = 1
DEFAULT_SOURCE_MANIFEST = Path("data/input/g3sx30_dry_run_preflight_manifest.csv")
DEFAULT_SOURCE_MANIFEST_ROW_INDEX = 1

COMMAND_CONTRACT_STATUS = "command_contract_scaffold_runtime_blocked"
COMMAND_CONTRACT_DECISION = "define_future_command_contract_only"
EXPECTED_COMMAND_FAMILY = "curated_embedding_preflight_dry_run_wrapper"
OUTPUT_PATH_POLICY = "do_not_write_committed_data_output"
ALLOWED_OUTPUT_LOCATION_POLICY = "future_temp_or_manual_reviews_path_only"
EXPECTED_FUTURE_COMMAND_CONTRACT = "expected_future_command_contract"
REQUIRED_FUTURE_ARGS = "required_future_args"
FORBIDDEN_FUTURE_ARGS = "forbidden_future_args"
ALLOWED_NEXT_ACTION_AFTER_COMMAND_CONTRACT = "add_wrapper_source_guardrail_pr"
CLAIM_STATUS = "technical_checkpoint"

ALLOWED_COMMAND_CONTRACT_STATUSES = {COMMAND_CONTRACT_STATUS}
ALLOWED_COMMAND_CONTRACT_DECISIONS = {COMMAND_CONTRACT_DECISION}
ALLOWED_NEXT_ACTIONS_AFTER_COMMAND_CONTRACT = {
    "add_wrapper_source_guardrail_pr",
    "add_wrapper_help_observation_note_pr",
    "keep_runtime_blocked",
}

REQUIRED_FUTURE_GUARDRAILS = (
    "must be manifest-aware; must read only G3SX30 manifest row #1; "
    "must keep max_live_batch_size=0; must reject Biohub / ESMC calls; "
    "must reject embedding generation; must reject .npy artifacts; "
    "must reject committed data/output artifacts; "
    "must require explicit non-committed output path before any later dry-run; "
    "must keep ready_for_preflight false"
)
FORBIDDEN_VOCABULARY = (
    "run_curated_embedding_preflight; run_curated_embedding_single; execute_wrapper; "
    "execute_manifest; select_actual_command; select_committed_data_output; "
    "ready_for_preflight; allow_biohub_call; allow_esmc_call; allow_embedding_generation; "
    "allow_npy_artifact; allow_data_output_artifact; promote_gate8; promote_gate9; biological_claim"
)
FORBIDDEN_ACTIONS = (
    "pyproject script entry point; Typer executable wrapper; wrapper execution; "
    "dry-run execution; live execution; actual command run; --help run; observed-help claims; "
    "actual CLI flag verification claims; Biohub call; ESMC call; embedding generation; "
    ".npy artifact; data/output artifact commit; ready_for_preflight; manifest runtime unlock; "
    "Gate 8 promotion; Gate 9 promotion; Boltz call; AF3 call; Chai call; enrichment rerun; "
    "contrast rerun; biological claim"
)

COMMAND_CONTRACT_SCHEMA = {
    "source_wrapper_scaffold_table": pl.Utf8,
    "source_wrapper_scaffold_row_index": pl.Int64,
    "source_policy_contract_table": pl.Utf8,
    "source_policy_contract_row_index": pl.Int64,
    "source_manifest_table": pl.Utf8,
    "source_manifest_row_index": pl.Int64,
    "candidate_id": pl.Utf8,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "source_wrapper_status": pl.Utf8,
    "source_wrapper_decision": pl.Utf8,
    "source_runtime_still_blocked": pl.Boolean,
    "command_contract_status": pl.Utf8,
    "command_contract_decision": pl.Utf8,
    "expected_command_family": pl.Utf8,
    "actual_cli_help_observed": pl.Boolean,
    "actual_command_verified": pl.Boolean,
    "command_selected": pl.Boolean,
    "output_path_selected": pl.Boolean,
    "execution_plan_materialized": pl.Boolean,
    "execution_authorized": pl.Boolean,
    "wrapper_execution_authorized": pl.Boolean,
    "dry_run_execution_authorized": pl.Boolean,
    "live_execution_authorized": pl.Boolean,
    "ready_for_preflight_authorized": pl.Boolean,
    "biohub_esmc_authorized": pl.Boolean,
    "embedding_generation_authorized": pl.Boolean,
    "npy_artifact_authorized": pl.Boolean,
    "data_output_artifact_commit_authorized": pl.Boolean,
    "output_path_policy": pl.Utf8,
    "allowed_output_location_policy": pl.Utf8,
    "expected_future_command_contract": pl.Utf8,
    "required_future_args": pl.Utf8,
    "forbidden_future_args": pl.Utf8,
    "required_future_guardrails": pl.Utf8,
    "forbidden_vocabulary": pl.Utf8,
    "unverified_until_help_or_source_guardrail": pl.Boolean,
    "future_command_contract_scaffold_only": pl.Boolean,
    "runtime_still_blocked": pl.Boolean,
    "allowed_next_action_after_command_contract": pl.Utf8,
    "claim_status": pl.Utf8,
    "forbidden_actions": pl.Utf8,
    "contract_note": pl.Utf8,
}

REQUIRED_COLUMNS = list(COMMAND_CONTRACT_SCHEMA)


def empty_g3sx30_wrapper_command_contract_scaffold_table() -> pl.DataFrame:
    return pl.DataFrame(schema=COMMAND_CONTRACT_SCHEMA)


def read_g3sx30_dry_run_preflight_manifest(
    path: Path = DEFAULT_SOURCE_MANIFEST,
) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)


def read_g3sx30_wrapper_command_contract_scaffold(path: Path) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=COMMAND_CONTRACT_SCHEMA)


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


def _require_source_wrapper_scaffold_runtime_blocked(row: dict[str, object]) -> None:
    expected_strings = {
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "wrapper_status": WRAPPER_STATUS,
        "wrapper_decision": WRAPPER_DECISION,
        "allowed_next_action_after_wrapper_scaffold": "add_wrapper_command_contract_pr",
        "claim_status": CLAIM_STATUS,
    }
    for column, expected_text in expected_strings.items():
        observed_text = _row_str(row, column)
        if observed_text != expected_text:
            raise ValueError(
                f"Expected wrapper scaffold {column}={expected_text!r}, observed {observed_text!r}"
            )

    if _row_int(row, "target_taxid") != EXPECTED_TARGET_TAXID:
        raise ValueError(f"Expected wrapper scaffold target_taxid={EXPECTED_TARGET_TAXID}")

    for column in [
        "command_selected",
        "output_path_selected",
        "execution_plan_materialized",
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
            raise ValueError(f"Wrapper scaffold must keep {column}=false")

    if not _row_bool(row, "runtime_still_blocked"):
        raise ValueError("Wrapper scaffold must keep runtime_still_blocked=true")


def _require_manifest_runtime_blocked(row: dict[str, object]) -> None:
    expected_strings = {
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "manifest_entry_status": "manifest_scaffold_ready_runtime_blocked",
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


def _require_source_identity_matches(
    wrapper_row: dict[str, object],
    policy_row: dict[str, object],
    manifest_row: dict[str, object],
) -> None:
    for column in [
        "candidate_id",
        "target_accession",
        "target_accession_db",
        "target_species",
        "gene_symbol",
    ]:
        values = {
            _row_str(wrapper_row, column),
            _row_str(policy_row, column),
            _row_str(manifest_row, column),
        }
        if len(values) != 1:
            raise ValueError(f"Source rows disagree on {column}: {sorted(values)}")

    taxids = {
        _row_int(wrapper_row, "target_taxid"),
        _row_int(policy_row, "target_taxid"),
        _row_int(manifest_row, "target_taxid"),
    }
    if taxids != {EXPECTED_TARGET_TAXID}:
        raise ValueError(f"Source rows disagree on target_taxid: {sorted(taxids)}")


def build_g3sx30_wrapper_command_contract_scaffold_table(
    wrapper_scaffold: pl.DataFrame,
    policy_contract: pl.DataFrame,
    manifest: pl.DataFrame,
    *,
    source_wrapper_scaffold_table: str = (
        "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
    ),
    source_wrapper_scaffold_row_index: int = DEFAULT_SOURCE_WRAPPER_SCAFFOLD_ROW_INDEX,
    source_policy_contract_table: str = "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv",
    source_policy_contract_row_index: int = DEFAULT_SOURCE_POLICY_CONTRACT_ROW_INDEX,
    source_manifest_table: str = "data/input/g3sx30_dry_run_preflight_manifest.csv",
    source_manifest_row_index: int = DEFAULT_SOURCE_MANIFEST_ROW_INDEX,
    allowed_next_action_after_command_contract: str = ALLOWED_NEXT_ACTION_AFTER_COMMAND_CONTRACT,
) -> pl.DataFrame:
    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows(wrapper_scaffold)
    validate_g3sx30_manifest_aware_adapter_policy_contract_rows(policy_contract)
    validate_g3sx30_dry_run_preflight_manifest_rows(manifest)

    if (
        allowed_next_action_after_command_contract
        not in ALLOWED_NEXT_ACTIONS_AFTER_COMMAND_CONTRACT
    ):
        raise ValueError(
            "Invalid allowed_next_action_after_command_contract: "
            f"{allowed_next_action_after_command_contract}"
        )

    wrapper_row = _select_row(
        wrapper_scaffold,
        source_wrapper_scaffold_row_index,
        "wrapper scaffold",
    )
    policy_row = _select_row(policy_contract, source_policy_contract_row_index, "policy contract")
    manifest_row = _select_row(manifest, source_manifest_row_index, "manifest")

    _require_source_wrapper_scaffold_runtime_blocked(wrapper_row)
    _require_manifest_runtime_blocked(manifest_row)
    _require_source_identity_matches(wrapper_row, policy_row, manifest_row)

    contract_note = (
        "Command contract scaffold row only. This row defines an expected future command contract, "
        "required future args, forbidden future args, and required future guardrails. It does not "
        "claim actual CLI help was observed, does not claim actual CLI flags were verified, selects "
        "no command, selects no output path, materializes no execution plan, and keeps runtime blocked."
    )

    return pl.DataFrame(
        [
            {
                "source_wrapper_scaffold_table": source_wrapper_scaffold_table,
                "source_wrapper_scaffold_row_index": source_wrapper_scaffold_row_index,
                "source_policy_contract_table": source_policy_contract_table,
                "source_policy_contract_row_index": source_policy_contract_row_index,
                "source_manifest_table": source_manifest_table,
                "source_manifest_row_index": source_manifest_row_index,
                "candidate_id": _row_str(wrapper_row, "candidate_id"),
                "target_accession": _row_str(wrapper_row, "target_accession"),
                "target_accession_db": _row_str(wrapper_row, "target_accession_db"),
                "target_species": _row_str(wrapper_row, "target_species"),
                "target_taxid": _row_int(wrapper_row, "target_taxid"),
                "gene_symbol": _row_str(wrapper_row, "gene_symbol"),
                "source_wrapper_status": _row_str(wrapper_row, "wrapper_status"),
                "source_wrapper_decision": _row_str(wrapper_row, "wrapper_decision"),
                "source_runtime_still_blocked": _row_bool(wrapper_row, "runtime_still_blocked"),
                "command_contract_status": COMMAND_CONTRACT_STATUS,
                "command_contract_decision": COMMAND_CONTRACT_DECISION,
                "expected_command_family": EXPECTED_COMMAND_FAMILY,
                "actual_cli_help_observed": False,
                "actual_command_verified": False,
                "command_selected": False,
                "output_path_selected": False,
                "execution_plan_materialized": False,
                "execution_authorized": False,
                "wrapper_execution_authorized": False,
                "dry_run_execution_authorized": False,
                "live_execution_authorized": False,
                "ready_for_preflight_authorized": False,
                "biohub_esmc_authorized": False,
                "embedding_generation_authorized": False,
                "npy_artifact_authorized": False,
                "data_output_artifact_commit_authorized": False,
                "output_path_policy": OUTPUT_PATH_POLICY,
                "allowed_output_location_policy": ALLOWED_OUTPUT_LOCATION_POLICY,
                "expected_future_command_contract": EXPECTED_FUTURE_COMMAND_CONTRACT,
                "required_future_args": REQUIRED_FUTURE_ARGS,
                "forbidden_future_args": FORBIDDEN_FUTURE_ARGS,
                "required_future_guardrails": REQUIRED_FUTURE_GUARDRAILS,
                "forbidden_vocabulary": FORBIDDEN_VOCABULARY,
                "unverified_until_help_or_source_guardrail": True,
                "future_command_contract_scaffold_only": True,
                "runtime_still_blocked": True,
                "allowed_next_action_after_command_contract": allowed_next_action_after_command_contract,
                "claim_status": CLAIM_STATUS,
                "forbidden_actions": FORBIDDEN_ACTIONS,
                "contract_note": contract_note,
            }
        ],
        schema=COMMAND_CONTRACT_SCHEMA,
    ).select(REQUIRED_COLUMNS)


def validate_g3sx30_wrapper_command_contract_scaffold_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required wrapper command contract scaffold columns: {missing}")


def _reject_forbidden_value(value: str) -> None:
    for forbidden in [
        "run_preflight",
        "execute_wrapper",
        "execute_manifest",
        "actual_supported_args",
        "observed_help_flags",
        "verified_cli_contract",
    ]:
        if value == forbidden:
            raise ValueError(f"Forbidden command-contract value: {forbidden}")


def validate_g3sx30_wrapper_command_contract_scaffold_rows(table: pl.DataFrame) -> None:
    validate_g3sx30_wrapper_command_contract_scaffold_schema(table)

    for row in table.iter_rows(named=True):
        expected_strings = {
            "source_wrapper_scaffold_table": (
                "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
            ),
            "source_policy_contract_table": "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv",
            "source_manifest_table": "data/input/g3sx30_dry_run_preflight_manifest.csv",
            "candidate_id": EXPECTED_CANDIDATE_ID,
            "target_accession": EXPECTED_TARGET_ACCESSION,
            "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
            "target_species": EXPECTED_TARGET_SPECIES,
            "gene_symbol": EXPECTED_GENE_SYMBOL,
            "source_wrapper_status": WRAPPER_STATUS,
            "source_wrapper_decision": WRAPPER_DECISION,
            "command_contract_status": COMMAND_CONTRACT_STATUS,
            "command_contract_decision": COMMAND_CONTRACT_DECISION,
            "expected_command_family": EXPECTED_COMMAND_FAMILY,
            "output_path_policy": OUTPUT_PATH_POLICY,
            "allowed_output_location_policy": ALLOWED_OUTPUT_LOCATION_POLICY,
            "expected_future_command_contract": EXPECTED_FUTURE_COMMAND_CONTRACT,
            "required_future_args": REQUIRED_FUTURE_ARGS,
            "forbidden_future_args": FORBIDDEN_FUTURE_ARGS,
            "required_future_guardrails": REQUIRED_FUTURE_GUARDRAILS,
            "forbidden_vocabulary": FORBIDDEN_VOCABULARY,
            "allowed_next_action_after_command_contract": ALLOWED_NEXT_ACTION_AFTER_COMMAND_CONTRACT,
            "claim_status": CLAIM_STATUS,
            "forbidden_actions": FORBIDDEN_ACTIONS,
        }
        for column, expected_text in expected_strings.items():
            observed_text = _row_str(row, column)
            if observed_text != expected_text:
                raise ValueError(f"Expected {column}={expected_text!r}, observed {observed_text!r}")
            _reject_forbidden_value(observed_text)

        expected_ints = {
            "source_wrapper_scaffold_row_index": 1,
            "source_policy_contract_row_index": 1,
            "source_manifest_row_index": 1,
            "target_taxid": EXPECTED_TARGET_TAXID,
        }
        for column, expected_int in expected_ints.items():
            observed_int = _row_int(row, column)
            if observed_int != expected_int:
                raise ValueError(f"Expected {column}={expected_int}, observed {observed_int}")

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
                raise ValueError(f"Command contract scaffold must keep {column}=false")

        for column in [
            "source_runtime_still_blocked",
            "unverified_until_help_or_source_guardrail",
            "future_command_contract_scaffold_only",
            "runtime_still_blocked",
        ]:
            if not _row_bool(row, column):
                raise ValueError(f"Command contract scaffold must keep {column}=true")

        contract_note = _row_str(row, "contract_note")
        for required in [
            "expected future command contract",
            "required future args",
            "forbidden future args",
            "required future guardrails",
            "does not claim actual CLI help was observed",
            "does not claim actual CLI flags were verified",
            "selects no command",
            "selects no output path",
            "materializes no execution plan",
            "keeps runtime blocked",
        ]:
            if required not in contract_note:
                raise ValueError(f"Missing command contract note: {required}")

        forbidden_actions = _row_str(row, "forbidden_actions")
        for required in [
            "pyproject script entry point",
            "Typer executable wrapper",
            "wrapper execution",
            "dry-run execution",
            "live execution",
            "actual command run",
            "--help run",
            "observed-help claims",
            "actual CLI flag verification claims",
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
