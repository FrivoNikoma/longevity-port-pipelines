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
    ALLOWED_COMMAND_CONTRACT_DECISIONS,
    ALLOWED_COMMAND_CONTRACT_STATUSES,
    ALLOWED_NEXT_ACTION_AFTER_COMMAND_CONTRACT,
    ALLOWED_NEXT_ACTIONS_AFTER_COMMAND_CONTRACT,
    COMMAND_CONTRACT_DECISION,
    COMMAND_CONTRACT_SCHEMA,
    COMMAND_CONTRACT_STATUS,
    FORBIDDEN_ACTIONS,
    FORBIDDEN_VOCABULARY,
    REQUIRED_FUTURE_GUARDRAILS,
    build_g3sx30_wrapper_command_contract_scaffold_table,
    empty_g3sx30_wrapper_command_contract_scaffold_table,
    read_g3sx30_dry_run_preflight_manifest,
    read_g3sx30_wrapper_command_contract_scaffold,
    validate_g3sx30_wrapper_command_contract_scaffold_rows,
    validate_g3sx30_wrapper_command_contract_scaffold_schema,
)

ROOT = Path(__file__).resolve().parents[1]
WRAPPER_SCAFFOLD = ROOT / "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
POLICY_CONTRACT = ROOT / "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
MANIFEST = ROOT / "data/input/g3sx30_dry_run_preflight_manifest.csv"
COMMAND_CONTRACT = ROOT / "data/interim/g3sx30_wrapper_command_contract_scaffold.csv"
SCHEMA = ROOT / "data/config/g3sx30_wrapper_command_contract_scaffold_schema.yaml"


def _build_expected_command_contract() -> pl.DataFrame:
    return build_g3sx30_wrapper_command_contract_scaffold_table(
        read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD),
        read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT),
        read_g3sx30_dry_run_preflight_manifest(MANIFEST),
    )


def test_command_contract_schema_records_unverified_future_contract_boundary() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_wrapper_command_contract_scaffold",
        "future_command_contract_scaffold_only_runtime_blocked",
        "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1",
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "expected_future_command_contract",
        "required_future_args",
        "forbidden_future_args",
        "unverified_until_help_or_source_guardrail",
        "future_command_contract_scaffold_only",
        "actual_supported_args",
        "observed_help_flags",
        "verified_cli_contract",
        "command_contract_scaffold_runtime_blocked",
        "define_future_command_contract_only",
        "add_wrapper_source_guardrail_pr",
        "add_wrapper_help_observation_note_pr",
        "keep_runtime_blocked",
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
        "biological claim",
    ]:
        assert required in text


def test_command_contract_allowed_vocabularies_are_scaffold_only() -> None:
    assert {"command_contract_scaffold_runtime_blocked"} == ALLOWED_COMMAND_CONTRACT_STATUSES
    assert {"define_future_command_contract_only"} == ALLOWED_COMMAND_CONTRACT_DECISIONS
    assert {
        "add_wrapper_source_guardrail_pr",
        "add_wrapper_help_observation_note_pr",
        "keep_runtime_blocked",
    } == ALLOWED_NEXT_ACTIONS_AFTER_COMMAND_CONTRACT


def test_empty_command_contract_table_has_expected_schema() -> None:
    table = empty_g3sx30_wrapper_command_contract_scaffold_table()

    validate_g3sx30_wrapper_command_contract_scaffold_schema(table)
    assert table.is_empty()
    assert table.schema == COMMAND_CONTRACT_SCHEMA


def test_build_command_contract_from_wrapper_policy_and_manifest_rows() -> None:
    table = _build_expected_command_contract()

    validate_g3sx30_wrapper_command_contract_scaffold_rows(table)
    assert table.height == 1

    row = table.row(0, named=True)
    assert row["source_wrapper_scaffold_table"] == (
        "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv"
    )
    assert row["source_wrapper_scaffold_row_index"] == 1
    assert row["source_policy_contract_table"] == (
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv"
    )
    assert row["source_policy_contract_row_index"] == 1
    assert row["source_manifest_table"] == "data/input/g3sx30_dry_run_preflight_manifest.csv"
    assert row["source_manifest_row_index"] == 1
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["target_accession_db"] == "UniProtKB TrEMBL"
    assert row["target_species"] == "Loxodonta africana"
    assert row["target_taxid"] == 9785
    assert row["gene_symbol"] == "MDM2"
    assert row["source_wrapper_status"] == "wrapper_scaffold_runtime_blocked"
    assert row["source_wrapper_decision"] == "prepare_wrapper_plan_only"
    assert row["source_runtime_still_blocked"] is True
    assert row["command_contract_status"] == COMMAND_CONTRACT_STATUS
    assert row["command_contract_decision"] == COMMAND_CONTRACT_DECISION
    assert row["expected_command_family"] == "curated_embedding_preflight_dry_run_wrapper"
    assert row["output_path_policy"] == "do_not_write_committed_data_output"
    assert row["allowed_output_location_policy"] == "future_temp_or_manual_reviews_path_only"
    assert row["expected_future_command_contract"] == "expected_future_command_contract"
    assert row["required_future_args"] == "required_future_args"
    assert row["forbidden_future_args"] == "forbidden_future_args"
    assert row["required_future_guardrails"] == REQUIRED_FUTURE_GUARDRAILS
    assert row["forbidden_vocabulary"] == FORBIDDEN_VOCABULARY
    assert row["allowed_next_action_after_command_contract"] == (
        ALLOWED_NEXT_ACTION_AFTER_COMMAND_CONTRACT
    )
    assert row["claim_status"] == "technical_checkpoint"


def test_checked_in_command_contract_matches_source_derived_contract() -> None:
    expected = _build_expected_command_contract()
    observed = read_g3sx30_wrapper_command_contract_scaffold(COMMAND_CONTRACT)

    validate_g3sx30_wrapper_command_contract_scaffold_rows(observed)
    assert observed.to_dicts() == expected.to_dicts()


def test_command_contract_keeps_all_runtime_authorizations_false() -> None:
    row = _build_expected_command_contract().row(0, named=True)

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
        assert row[column] is False

    for column in [
        "source_runtime_still_blocked",
        "unverified_until_help_or_source_guardrail",
        "future_command_contract_scaffold_only",
        "runtime_still_blocked",
    ]:
        assert row[column] is True


def test_command_contract_rejects_source_wrapper_command_selection() -> None:
    wrapper = read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD)
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    broken = wrapper.with_columns(pl.lit(True).alias("command_selected"))

    with pytest.raises(ValueError, match="command_selected"):
        build_g3sx30_wrapper_command_contract_scaffold_table(broken, policy, manifest)


def test_command_contract_rejects_manifest_runtime_unlock() -> None:
    wrapper = read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD)
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    broken = manifest.with_columns(pl.lit(True).alias("embedding_generation_allowed"))

    with pytest.raises(ValueError, match="embedding_generation_allowed"):
        build_g3sx30_wrapper_command_contract_scaffold_table(wrapper, policy, broken)


def test_command_contract_rejects_direct_execution_next_action() -> None:
    wrapper = read_g3sx30_manifest_aware_dry_run_wrapper_scaffold(WRAPPER_SCAFFOLD)
    policy = read_g3sx30_manifest_aware_adapter_policy_contract(POLICY_CONTRACT)
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)

    with pytest.raises(ValueError, match="allowed_next_action_after_command_contract"):
        build_g3sx30_wrapper_command_contract_scaffold_table(
            wrapper,
            policy,
            manifest,
            allowed_next_action_after_command_contract="run_preflight",
        )


def test_command_contract_rejects_execution_authorization_in_scaffold_row() -> None:
    table = _build_expected_command_contract()
    broken = table.with_columns(pl.lit(True).alias("execution_authorized"))

    with pytest.raises(ValueError, match="execution_authorized"):
        validate_g3sx30_wrapper_command_contract_scaffold_rows(broken)


def test_command_contract_note_avoids_observed_help_or_verified_cli_claims() -> None:
    row = read_g3sx30_wrapper_command_contract_scaffold(COMMAND_CONTRACT).row(0, named=True)
    note = row["contract_note"]

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
        assert required in note

    for forbidden in [
        "actual_supported_args",
        "observed_help_flags",
        "verified_cli_contract",
    ]:
        assert forbidden not in note


def test_command_contract_forbidden_vocabularies_block_execution_language() -> None:
    row = read_g3sx30_wrapper_command_contract_scaffold(COMMAND_CONTRACT).row(0, named=True)

    for required in [
        "run_curated_embedding_preflight",
        "run_curated_embedding_single",
        "execute_wrapper",
        "execute_manifest",
        "select_actual_command",
        "select_committed_data_output",
        "ready_for_preflight",
        "allow_biohub_call",
        "allow_esmc_call",
        "allow_embedding_generation",
        "allow_npy_artifact",
        "allow_data_output_artifact",
        "promote_gate8",
        "promote_gate9",
        "biological_claim",
    ]:
        assert required in FORBIDDEN_VOCABULARY
        assert required in row["forbidden_vocabulary"]

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
        assert required in FORBIDDEN_ACTIONS
        assert required in row["forbidden_actions"]
