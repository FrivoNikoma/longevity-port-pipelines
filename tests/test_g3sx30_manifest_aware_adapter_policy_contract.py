from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages.g3sx30_manifest_aware_adapter_policy_contract import (
    ALLOWED_ADAPTER_POLICY_DECISIONS,
    ALLOWED_ADAPTER_POLICY_STATUSES,
    ALLOWED_CURRENT_CLI_COMPATIBILITY_VALUES,
    ALLOWED_CURRENT_CLI_DIRECT_EXECUTION_DECISIONS,
    ALLOWED_EXECUTION_DECISIONS,
    ALLOWED_NEXT_ACTION_AFTER_POLICY,
    ALLOWED_NEXT_ACTIONS_AFTER_ADAPTER_POLICY,
    ALLOWED_WRAPPER_SCAFFOLD_DECISIONS,
    CURRENT_CLI_DIRECT_EXECUTION_DECISION,
    NOT_AUTHORIZED,
    POLICY_CONTRACT_SCHEMA,
    POLICY_DECISION,
    POLICY_STATUS,
    WRAPPER_SCAFFOLD_DECISION,
    build_g3sx30_manifest_aware_adapter_policy_contract_table,
    empty_g3sx30_manifest_aware_adapter_policy_contract_table,
    read_g3sx30_manifest_aware_adapter_policy_contract,
    read_g3sx30_manifest_aware_adapter_scaffold,
    validate_g3sx30_manifest_aware_adapter_policy_contract_rows,
    validate_g3sx30_manifest_aware_adapter_policy_contract_schema,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ADAPTER = ROOT / "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
POLICY_TABLE = ROOT / "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
SCHEMA = ROOT / "data/config/g3sx30_manifest_aware_adapter_policy_contract_schema.yaml"


def test_policy_contract_schema_records_layer_separation_and_no_runtime_boundary() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_manifest_aware_adapter_policy_contract",
        "policy_contract_table_only_no_runtime_side_effects",
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1",
        "adapter_scaffold: instance-level understanding of manifest row #1",
        "adapter_policy_contract: machine-readable allowed transition contract after scaffold",
        "manifest_aware_wrapper: future implementation, not this policy contract",
        "dry_run_execution: still later, not this policy contract",
        "live_embedding_fill: much later, not this policy contract",
        "adapter_policy_runtime_blocked",
        "require_manifest_aware_wrapper_before_execution",
        "reject_current_cli_direct_execution",
        "allow_wrapper_scaffold_only",
        "not_authorized",
        "not_directly_executable_manifest_mismatch_output_path_issue",
        "prepare_manifest_aware_wrapper_scaffold_pr",
        "add_source_level_manifest_guardrail_before_execution",
        "keep_runtime_blocked",
        "pyproject script entry point",
        "manifest-aware wrapper implementation",
        "wrapper execution",
        "dry-run execution",
        "Biohub call",
        "ESMC call",
        "embedding generation",
        "ready_for_preflight",
        "manifest runtime unlock",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "biological claim",
    ]:
        assert required in text


def test_policy_contract_schema_forbids_execution_permitting_vocabulary() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

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
        assert forbidden in text


def test_policy_contract_allowed_vocabularies_are_blocked_only() -> None:
    assert {"adapter_policy_runtime_blocked"} == ALLOWED_ADAPTER_POLICY_STATUSES
    assert {"require_manifest_aware_wrapper_before_execution"} == ALLOWED_ADAPTER_POLICY_DECISIONS
    assert {"reject_current_cli_direct_execution"} == ALLOWED_CURRENT_CLI_DIRECT_EXECUTION_DECISIONS
    assert {"allow_wrapper_scaffold_only"} == ALLOWED_WRAPPER_SCAFFOLD_DECISIONS
    assert {"not_authorized"} == ALLOWED_EXECUTION_DECISIONS
    assert {
        "not_directly_executable_manifest_mismatch_output_path_issue"
    } == ALLOWED_CURRENT_CLI_COMPATIBILITY_VALUES
    assert {
        "prepare_manifest_aware_wrapper_scaffold_pr",
        "add_source_level_manifest_guardrail_before_execution",
        "keep_runtime_blocked",
    } == ALLOWED_NEXT_ACTIONS_AFTER_ADAPTER_POLICY


def test_empty_policy_contract_table_has_expected_schema() -> None:
    table = empty_g3sx30_manifest_aware_adapter_policy_contract_table()

    validate_g3sx30_manifest_aware_adapter_policy_contract_schema(table)
    assert table.is_empty()
    assert table.schema == POLICY_CONTRACT_SCHEMA


def test_build_policy_contract_from_adapter_scaffold_row() -> None:
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(SOURCE_ADAPTER)
    table = build_g3sx30_manifest_aware_adapter_policy_contract_table(adapter)

    validate_g3sx30_manifest_aware_adapter_policy_contract_rows(table)

    assert table.height == 1
    row = table.row(0, named=True)

    assert row["source_adapter_scaffold_table"] == (
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
    )
    assert row["source_adapter_scaffold_row_index"] == 1
    assert row["adapter_status"] == "manifest_understood_runtime_blocked"
    assert row["adapter_decision"] == "do_not_execute_current_cli_directly"
    assert row["current_cli_compatibility"] == (
        "not_directly_executable_manifest_mismatch_output_path_issue"
    )
    assert row["source_required_next_action"] == (
        "add_manifest_aware_wrapper_or_guardrail_before_execution"
    )
    assert row["source_output_path_policy"] == "do_not_write_committed_data_output"
    assert row["policy_status"] == POLICY_STATUS
    assert row["policy_decision"] == POLICY_DECISION
    assert row["current_cli_direct_execution_decision"] == CURRENT_CLI_DIRECT_EXECUTION_DECISION
    assert row["wrapper_scaffold_decision"] == WRAPPER_SCAFFOLD_DECISION
    assert row["wrapper_execution_decision"] == NOT_AUTHORIZED
    assert row["dry_run_execution_decision"] == NOT_AUTHORIZED
    assert row["live_execution_decision"] == NOT_AUTHORIZED
    assert row["ready_for_preflight_decision"] == NOT_AUTHORIZED
    assert row["biohub_esmc_decision"] == NOT_AUTHORIZED
    assert row["embedding_generation_decision"] == NOT_AUTHORIZED
    assert row["artifact_decision"] == NOT_AUTHORIZED
    assert row["allowed_next_action_after_policy"] == ALLOWED_NEXT_ACTION_AFTER_POLICY
    assert row["claim_status"] == "technical_checkpoint"


def test_checked_in_policy_contract_matches_adapter_derived_policy() -> None:
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(SOURCE_ADAPTER)
    expected = build_g3sx30_manifest_aware_adapter_policy_contract_table(adapter)
    observed = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_TABLE)

    validate_g3sx30_manifest_aware_adapter_policy_contract_rows(observed)
    assert observed.to_dicts() == expected.to_dicts()


def test_policy_contract_keeps_all_runtime_permissions_false() -> None:
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(SOURCE_ADAPTER)
    table = build_g3sx30_manifest_aware_adapter_policy_contract_table(adapter)
    row = table.row(0, named=True)

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
        assert row[column] is False


def test_policy_contract_rejects_source_adapter_runtime_unlock() -> None:
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(SOURCE_ADAPTER)
    broken = adapter.with_columns(pl.lit(True).alias("curated_embedding_preflight_runtime_allowed"))

    with pytest.raises(ValueError, match="curated_embedding_preflight_runtime_allowed"):
        build_g3sx30_manifest_aware_adapter_policy_contract_table(broken)


def test_policy_contract_rejects_execution_permitting_next_action() -> None:
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(SOURCE_ADAPTER)

    with pytest.raises(ValueError, match="allowed_next_action_after_policy"):
        build_g3sx30_manifest_aware_adapter_policy_contract_table(
            adapter,
            allowed_next_action_after_policy="run_curated_embedding_preflight",
        )


def test_policy_contract_rejects_execution_permission_in_policy_row() -> None:
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(SOURCE_ADAPTER)
    table = build_g3sx30_manifest_aware_adapter_policy_contract_table(adapter)
    broken = table.with_columns(pl.lit(True).alias("biohub_call_allowed"))

    with pytest.raises(ValueError, match="biohub_call_allowed"):
        validate_g3sx30_manifest_aware_adapter_policy_contract_rows(broken)


def test_wrapper_scaffold_only_wording_is_non_execution_authorization() -> None:
    table = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_TABLE)
    row = table.row(0, named=True)

    assert row["wrapper_scaffold_decision"] == "allow_wrapper_scaffold_only"
    assert row["wrapper_execution_decision"] == "not_authorized"
    assert row["dry_run_execution_decision"] == "not_authorized"
    assert row["live_execution_decision"] == "not_authorized"

    note = row["policy_note"]
    for required in [
        "allow_wrapper_scaffold_only means only that a later PR may prepare a wrapper scaffold",
        "does not mean the wrapper exists",
        "does not mean wrapper execution is allowed",
        "does not mean dry-run execution is allowed",
    ]:
        assert required in note
