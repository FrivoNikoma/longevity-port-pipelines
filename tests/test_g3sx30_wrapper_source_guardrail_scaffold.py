from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages.g3sx30_manifest_aware_adapter_policy_contract import (
    read_g3sx30_manifest_aware_adapter_policy_contract,
)
from longevity_port_pipelines.stages.g3sx30_manifest_aware_dry_run_wrapper_scaffold import (
    read_g3sx30_manifest_aware_dry_run_wrapper_scaffold,
)
from longevity_port_pipelines.stages.g3sx30_wrapper_command_contract_scaffold import (
    read_g3sx30_wrapper_command_contract_scaffold,
)
from longevity_port_pipelines.stages.g3sx30_wrapper_source_guardrail_scaffold import (
    ALLOWED_NEXT_ACTIONS_AFTER_SOURCE_GUARDRAIL,
    FORBIDDEN_NEXT_ACTIONS,
    SOURCE_GUARDRAIL_SCHEMA,
    build_g3sx30_wrapper_source_guardrail_scaffold_table,
    empty_g3sx30_wrapper_source_guardrail_scaffold_table,
    read_g3sx30_dry_run_preflight_manifest,
    read_g3sx30_wrapper_source_guardrail_scaffold,
    validate_g3sx30_wrapper_source_guardrail_scaffold_rows,
    validate_g3sx30_wrapper_source_guardrail_scaffold_schema,
)

ROOT = Path(__file__).resolve().parents[1]
COMMAND_CONTRACT = ROOT / "data/interim/g3sx30_wrapper_command_contract_scaffold.csv"
WRAPPER_SCAFFOLD = ROOT / "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
MANIFEST = ROOT / "data/input/g3sx30_dry_run_preflight_manifest.csv"
POLICY_CONTRACT = ROOT / "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
SOURCE_GUARDRAIL = ROOT / "data/interim/g3sx30_wrapper_source_guardrail_scaffold.csv"
SCHEMA = ROOT / "data/config/g3sx30_wrapper_source_guardrail_scaffold_schema.yaml"


def _build_expected_source_guardrail() -> pl.DataFrame:
    return build_g3sx30_wrapper_source_guardrail_scaffold_table(
        read_g3sx30_wrapper_command_contract_scaffold(COMMAND_CONTRACT),
        read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD),
        read_g3sx30_dry_run_preflight_manifest(MANIFEST),
        read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT),
    )


def test_source_guardrail_schema_records_non_executable_boundary() -> None:
    text = SCHEMA.read_text(encoding="utf-8")
    for required in [
        "g3sx30_wrapper_source_guardrail_scaffold",
        "source_guardrail_scaffold_runtime_blocked",
        "data/interim/g3sx30_wrapper_command_contract_scaffold.csv#1",
        "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1",
        "future_wrapper_source_checks_only",
        "no_runtime_effect",
        "add_wrapper_help_observation_note_pr",
        "add_wrapper_guardrail_implementation_plan_pr",
        "keep_runtime_blocked",
        "run_preflight",
        "execute_wrapper",
        "ready_for_preflight",
        "wrapper implementation",
        "wrapper execution",
        "dry-run execution",
        "live execution",
        "--help run",
        "Biohub call",
        "ESMC call",
        "embedding generation",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "biological claim",
    ]:
        assert required in text


def test_source_guardrail_allowed_next_actions_are_blocked_future_steps() -> None:
    assert {
        "add_wrapper_help_observation_note_pr",
        "add_wrapper_guardrail_implementation_plan_pr",
        "keep_runtime_blocked",
    } == ALLOWED_NEXT_ACTIONS_AFTER_SOURCE_GUARDRAIL


def test_empty_source_guardrail_table_has_expected_schema() -> None:
    table = empty_g3sx30_wrapper_source_guardrail_scaffold_table()
    validate_g3sx30_wrapper_source_guardrail_scaffold_schema(table)
    assert table.is_empty()
    assert table.schema == SOURCE_GUARDRAIL_SCHEMA


def test_build_source_guardrail_from_command_contract_wrapper_manifest_and_policy() -> None:
    table = _build_expected_source_guardrail()
    validate_g3sx30_wrapper_source_guardrail_scaffold_rows(table)
    assert table.height == 1

    row = table.row(0, named=True)
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["target_species"] == "Loxodonta africana"
    assert row["target_taxid"] == 9785
    assert row["gene_symbol"] == "MDM2"
    assert row["reviewed_sequence_length"] == 492
    assert row["reviewed_sequence_sha256"] == (
        "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
    )
    assert row["source_command_contract_status"] == "command_contract_scaffold_runtime_blocked"
    assert row["source_actual_cli_help_observed"] is False
    assert row["source_actual_command_verified"] is False
    assert row["source_command_selected"] is False
    assert row["source_output_path_selected"] is False
    assert row["source_execution_plan_materialized"] is False
    assert row["source_guardrail_status"] == "source_guardrail_scaffold_runtime_blocked"
    assert row["source_guardrail_decision"] == "define_source_level_guardrails_only"
    assert row["guardrail_scope"] == "future_wrapper_source_checks_only"
    assert row["guardrail_runtime_effect"] == "no_runtime_effect"
    assert row["allowed_next_action_after_source_guardrail"] == (
        "add_wrapper_help_observation_note_pr"
    )
    assert row["claim_status"] == "technical_checkpoint"
    assert row["runtime_still_blocked"] is True


def test_checked_in_source_guardrail_matches_source_derived_guardrail() -> None:
    expected = _build_expected_source_guardrail()
    observed = read_g3sx30_wrapper_source_guardrail_scaffold(SOURCE_GUARDRAIL)
    validate_g3sx30_wrapper_source_guardrail_scaffold_rows(observed)
    assert observed.to_dicts() == expected.to_dicts()


def test_source_guardrail_keeps_all_runtime_authorizations_false() -> None:
    row = _build_expected_source_guardrail().row(0, named=True)
    for column in [
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
    ]:
        assert row[column] is False


def test_source_guardrail_rejects_command_contract_verification() -> None:
    command = read_g3sx30_wrapper_command_contract_scaffold(COMMAND_CONTRACT)
    wrapper = read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)
    broken = command.with_columns(pl.lit(True).alias("actual_command_verified"))

    with pytest.raises(ValueError, match="actual_command_verified"):
        build_g3sx30_wrapper_source_guardrail_scaffold_table(broken, wrapper, manifest, policy)


def test_source_guardrail_rejects_manifest_runtime_unlock() -> None:
    command = read_g3sx30_wrapper_command_contract_scaffold(COMMAND_CONTRACT)
    wrapper = read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)
    broken = manifest.with_columns(pl.lit(True).alias("biohub_call_allowed"))

    with pytest.raises(ValueError, match="biohub_call_allowed"):
        build_g3sx30_wrapper_source_guardrail_scaffold_table(command, wrapper, broken, policy)


def test_source_guardrail_rejects_direct_execution_next_action() -> None:
    command = read_g3sx30_wrapper_command_contract_scaffold(COMMAND_CONTRACT)
    wrapper = read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)

    with pytest.raises(ValueError, match="allowed_next_action_after_source_guardrail"):
        build_g3sx30_wrapper_source_guardrail_scaffold_table(
            command,
            wrapper,
            manifest,
            policy,
            allowed_next_action_after_source_guardrail="execute_wrapper",
        )


def test_source_guardrail_note_and_forbidden_next_actions_are_blocked_only() -> None:
    row = read_g3sx30_wrapper_source_guardrail_scaffold(SOURCE_GUARDRAIL).row(0, named=True)
    note = row["guardrail_note"]
    for required in [
        "future wrapper source checks only",
        "has no runtime effect",
        "does not implement the wrapper",
        "does not run --help",
        "does not execute anything",
        "keeps G3SX30 runtime blocked",
        "rejects Gate 8 / Gate 9 promotion",
        "makes no biological claim",
    ]:
        assert required in note

    for forbidden in ["run_preflight", "execute_wrapper", "ready_for_preflight"]:
        assert forbidden in FORBIDDEN_NEXT_ACTIONS
        assert forbidden in row["forbidden_next_actions"]
