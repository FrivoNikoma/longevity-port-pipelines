from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages.g3sx30_manifest_aware_adapter_policy_contract import (
    read_g3sx30_manifest_aware_adapter_policy_contract,
    read_g3sx30_manifest_aware_adapter_scaffold,
)
from longevity_port_pipelines.stages.g3sx30_manifest_aware_dry_run_wrapper_scaffold import (
    ALLOWED_NEXT_ACTION_AFTER_WRAPPER_SCAFFOLD,
    ALLOWED_NEXT_ACTIONS_AFTER_WRAPPER_SCAFFOLD,
    ALLOWED_WRAPPER_DECISIONS,
    ALLOWED_WRAPPER_STATUSES,
    FORBIDDEN_ACTIONS,
    WRAPPER_DECISION,
    WRAPPER_SCAFFOLD_SCHEMA,
    WRAPPER_STATUS,
    build_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table,
    empty_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table,
    read_g3sx30_dry_run_preflight_manifest,
    read_g3sx30_manifest_aware_dry_run_wrapper_scaffold,
    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows,
    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_schema,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY_CONTRACT = ROOT / "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
ADAPTER_SCAFFOLD = (
    ROOT / "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
)
MANIFEST = ROOT / "data/input/g3sx30_dry_run_preflight_manifest.csv"
WRAPPER_SCAFFOLD = ROOT / "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
SCHEMA = ROOT / "data/config/g3sx30_manifest_aware_dry_run_wrapper_scaffold_schema.yaml"


def _build_expected_wrapper_scaffold() -> pl.DataFrame:
    return build_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table(
        read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT),
        read_g3sx30_manifest_aware_adapter_scaffold(ADAPTER_SCAFFOLD),
        read_g3sx30_dry_run_preflight_manifest(MANIFEST),
    )


def test_wrapper_scaffold_schema_records_non_executable_boundary() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_manifest_aware_dry_run_wrapper_scaffold",
        "wrapper_scaffold_runtime_blocked_table_only_no_runtime_side_effects",
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1",
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "wrapper_scaffold: non-executable representation of a future wrapper boundary",
        "wrapper_command_contract: future command/argument/output-path contract, not this scaffold",
        "wrapper_execution: not authorized by this scaffold",
        "dry_run_execution: still later, not this scaffold",
        "live_embedding_fill: much later, not this scaffold",
        "wrapper_scaffold_runtime_blocked",
        "prepare_wrapper_plan_only",
        "add_wrapper_command_contract_pr",
        "add_source_level_wrapper_guardrail_pr",
        "keep_runtime_blocked",
        "pyproject script entry point",
        "Typer executable wrapper",
        "manifest-aware wrapper implementation",
        "wrapper execution",
        "dry-run execution",
        "live execution",
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
        "biological claim",
    ]:
        assert required in text


def test_wrapper_scaffold_allowed_vocabularies_are_scaffold_only() -> None:
    assert {"wrapper_scaffold_runtime_blocked"} == ALLOWED_WRAPPER_STATUSES
    assert {"prepare_wrapper_plan_only"} == ALLOWED_WRAPPER_DECISIONS
    assert {
        "add_wrapper_command_contract_pr",
        "add_source_level_wrapper_guardrail_pr",
        "keep_runtime_blocked",
    } == ALLOWED_NEXT_ACTIONS_AFTER_WRAPPER_SCAFFOLD


def test_empty_wrapper_scaffold_table_has_expected_schema() -> None:
    table = empty_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table()

    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_schema(table)
    assert table.is_empty()
    assert table.schema == WRAPPER_SCAFFOLD_SCHEMA


def test_build_wrapper_scaffold_from_policy_adapter_and_manifest_rows() -> None:
    table = _build_expected_wrapper_scaffold()

    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows(table)
    assert table.height == 1

    row = table.row(0, named=True)
    assert row["source_policy_contract_table"] == (
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
    )
    assert row["source_policy_contract_row_index"] == 1
    assert row["source_adapter_scaffold_table"] == (
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
    )
    assert row["source_adapter_scaffold_row_index"] == 1
    assert row["source_manifest_table"] == "data/input/g3sx30_dry_run_preflight_manifest.csv"
    assert row["source_manifest_row_index"] == 1
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["target_accession_db"] == "UniProtKB TrEMBL"
    assert row["target_species"] == "Loxodonta africana"
    assert row["target_taxid"] == 9785
    assert row["gene_symbol"] == "MDM2"
    assert row["manifest_entry_status"] == "manifest_scaffold_ready_runtime_blocked"
    assert row["adapter_status"] == "manifest_understood_runtime_blocked"
    assert row["adapter_decision"] == "do_not_execute_current_cli_directly"
    assert row["current_cli_compatibility"] == (
        "not_directly_executable_manifest_mismatch_output_path_issue"
    )
    assert row["policy_contract_status"] == "adapter_policy_runtime_blocked"
    assert row["policy_contract_decision"] == "require_manifest_aware_wrapper_before_execution"
    assert row["current_cli_direct_execution_decision"] == "reject_current_cli_direct_execution"
    assert row["wrapper_scaffold_decision"] == "allow_wrapper_scaffold_only"
    assert row["wrapper_status"] == WRAPPER_STATUS
    assert row["wrapper_decision"] == WRAPPER_DECISION
    assert row["allowed_next_action_after_wrapper_scaffold"] == (
        ALLOWED_NEXT_ACTION_AFTER_WRAPPER_SCAFFOLD
    )
    assert row["claim_status"] == "technical_checkpoint"


def test_checked_in_wrapper_scaffold_matches_source_derived_scaffold() -> None:
    expected = _build_expected_wrapper_scaffold()
    observed = read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD)

    validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows(observed)
    assert observed.to_dicts() == expected.to_dicts()


def test_wrapper_scaffold_keeps_all_runtime_permissions_false_and_runtime_blocked() -> None:
    table = _build_expected_wrapper_scaffold()
    row = table.row(0, named=True)

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
        assert row[column] is False

    assert row["runtime_still_blocked"] is True


def test_wrapper_scaffold_rejects_policy_contract_runtime_unlock() -> None:
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(ADAPTER_SCAFFOLD)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    broken = policy.with_columns(pl.lit(True).alias("wrapper_execution_allowed"))

    with pytest.raises(ValueError, match="wrapper_execution_allowed"):
        build_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table(broken, adapter, manifest)


def test_wrapper_scaffold_rejects_manifest_runtime_unlock() -> None:
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(ADAPTER_SCAFFOLD)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    broken = manifest.with_columns(pl.lit(True).alias("biohub_call_allowed"))

    with pytest.raises(ValueError, match="biohub_call_allowed"):
        build_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table(policy, adapter, broken)


def test_wrapper_scaffold_rejects_execution_next_action() -> None:
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)
    adapter = read_g3sx30_manifest_aware_adapter_scaffold(ADAPTER_SCAFFOLD)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)

    with pytest.raises(ValueError, match="allowed_next_action_after_wrapper_scaffold"):
        build_g3sx30_manifest_aware_dry_run_wrapper_scaffold_table(
            policy,
            adapter,
            manifest,
            allowed_next_action_after_wrapper_scaffold="run_preflight",
        )


def test_wrapper_scaffold_rejects_runtime_permission_in_scaffold_row() -> None:
    table = _build_expected_wrapper_scaffold()
    broken = table.with_columns(pl.lit(True).alias("command_selected"))

    with pytest.raises(ValueError, match="command_selected"):
        validate_g3sx30_manifest_aware_dry_run_wrapper_scaffold_rows(broken)


def test_wrapper_scaffold_note_and_forbidden_actions_are_non_executable() -> None:
    table = read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD)
    row = table.row(0, named=True)

    note = row["scaffold_note"]
    for required in [
        "this scaffold is not executable",
        "selects no command",
        "selects no output path",
        "does not materialize an execution plan",
        "keeps runtime blocked",
        "A later PR may define a wrapper command contract or source-level wrapper guardrail",
    ]:
        assert required in note

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
        assert required in FORBIDDEN_ACTIONS
        assert required in row["forbidden_actions"]
