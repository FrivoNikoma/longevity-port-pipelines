from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages.g3sx30_manifest_aware_dry_run_preflight_adapter import (
    ADAPTER_DECISION,
    ADAPTER_STATUS,
    ALLOWED_OUTPUT_LOCATION,
    CLAIM_STATUS,
    CURRENT_CLI_COMPATIBILITY,
    EXPECTED_CANDIDATE_ID,
    EXPECTED_GENE_SYMBOL,
    EXPECTED_SEQUENCE_LENGTH,
    EXPECTED_SEQUENCE_SHA256,
    EXPECTED_TARGET_ACCESSION,
    EXPECTED_TARGET_ACCESSION_DB,
    EXPECTED_TARGET_SPECIES,
    EXPECTED_TARGET_TAXID,
    OUTPUT_PATH_POLICY,
    REQUIRED_NEXT_ACTION,
    build_g3sx30_manifest_aware_dry_run_preflight_adapter_table,
    empty_g3sx30_manifest_aware_dry_run_preflight_adapter_table,
    read_g3sx30_dry_run_preflight_manifest,
    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_rows,
    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_schema,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/input/g3sx30_dry_run_preflight_manifest.csv"
ADAPTER_TABLE = ROOT / "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv"
SCHEMA = ROOT / "data/config/g3sx30_manifest_aware_dry_run_preflight_adapter_schema.yaml"


def test_adapter_schema_file_records_no_runtime_boundary() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_manifest_aware_dry_run_preflight_adapter",
        "scaffold_only_no_runtime_side_effects",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "docs/g3sx30_dry_run_preflight_cli_compatibility_note.md",
        "curated-embedding-preflight run",
        "curated_embedding_preflight run",
        "curated-embedding-single run",
        "curated_embedding_single run",
        "help run",
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
        "enrichment rerun",
        "contrast rerun",
        "biological claim",
        "manifest_understood_runtime_blocked",
        "do_not_execute_current_cli_directly",
        "not_directly_executable_manifest_mismatch_output_path_issue",
        "add_manifest_aware_wrapper_or_guardrail_before_execution",
        "do_not_write_committed_data_output",
        "not_selected_scaffold_only",
        "technical_checkpoint",
    ]:
        assert required in text


def test_empty_adapter_table_has_expected_schema() -> None:
    table = empty_g3sx30_manifest_aware_dry_run_preflight_adapter_table()

    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_schema(table)
    assert table.is_empty()
    assert "adapter_status" in table.columns
    assert "curated_embedding_preflight_runtime_allowed" in table.columns
    assert "curated_embedding_single_runtime_allowed" in table.columns


def test_build_adapter_table_from_manifest_row_keeps_runtime_blocked() -> None:
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    table = build_g3sx30_manifest_aware_dry_run_preflight_adapter_table(manifest)

    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_rows(table)

    assert table.height == 1
    row = table.row(0, named=True)

    assert row["source_manifest_table"] == "data/input/g3sx30_dry_run_preflight_manifest.csv"
    assert row["source_manifest_row_index"] == 1
    assert row["candidate_id"] == EXPECTED_CANDIDATE_ID
    assert row["target_accession"] == EXPECTED_TARGET_ACCESSION
    assert row["target_accession_db"] == EXPECTED_TARGET_ACCESSION_DB
    assert row["target_species"] == EXPECTED_TARGET_SPECIES
    assert row["target_taxid"] == EXPECTED_TARGET_TAXID
    assert row["gene_symbol"] == EXPECTED_GENE_SYMBOL
    assert row["reviewed_sequence_sha256"] == EXPECTED_SEQUENCE_SHA256
    assert row["reviewed_sequence_length"] == EXPECTED_SEQUENCE_LENGTH
    assert row["manifest_entry_status"] == "manifest_scaffold_ready_runtime_blocked"
    assert row["dry_run_only"] is True
    assert row["max_live_batch_size"] == 0
    assert row["ready_for_preflight_after_manifest"] == "false"
    assert row["sequence_fetch_allowed"] is False
    assert row["biohub_call_allowed"] is False
    assert row["esmc_call_allowed"] is False
    assert row["embedding_generation_allowed"] is False
    assert row["curated_embedding_preflight_allowed"] is False
    assert row["curated_embedding_single_allowed"] is False
    assert row["adapter_status"] == ADAPTER_STATUS
    assert row["adapter_decision"] == ADAPTER_DECISION
    assert row["current_cli_compatibility"] == CURRENT_CLI_COMPATIBILITY
    assert row["required_next_action"] == REQUIRED_NEXT_ACTION
    assert row["curated_embedding_preflight_runtime_allowed"] is False
    assert row["curated_embedding_single_runtime_allowed"] is False
    assert row["output_path_policy"] == OUTPUT_PATH_POLICY
    assert row["allowed_output_location"] == ALLOWED_OUTPUT_LOCATION
    assert row["claim_status"] == CLAIM_STATUS


def test_checked_in_adapter_table_matches_manifest_derived_table() -> None:
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    expected = build_g3sx30_manifest_aware_dry_run_preflight_adapter_table(manifest)
    observed = pl.read_csv(
        ADAPTER_TABLE,
        schema_overrides=expected.schema,
    )

    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_rows(observed)
    assert observed.to_dicts() == expected.to_dicts()


def test_adapter_rejects_manifest_with_live_permission_enabled() -> None:
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    broken = manifest.with_columns(pl.lit(True).alias("biohub_call_allowed"))

    with pytest.raises(ValueError, match="biohub_call_allowed"):
        build_g3sx30_manifest_aware_dry_run_preflight_adapter_table(broken)


def test_adapter_rejects_manifest_with_nonzero_live_batch_size() -> None:
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    broken = manifest.with_columns(pl.lit(1).alias("max_live_batch_size"))

    with pytest.raises(ValueError, match="max_live_batch_size|batch size"):
        build_g3sx30_manifest_aware_dry_run_preflight_adapter_table(broken)


def test_adapter_rejects_runtime_unlock() -> None:
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    broken = manifest.with_columns(pl.lit("true").alias("ready_for_preflight_after_manifest"))

    with pytest.raises(ValueError, match="ready_for_preflight"):
        build_g3sx30_manifest_aware_dry_run_preflight_adapter_table(broken)


def test_adapter_forbidden_actions_cover_all_runtime_paths() -> None:
    manifest = read_g3sx30_dry_run_preflight_manifest(MANIFEST)
    table = build_g3sx30_manifest_aware_dry_run_preflight_adapter_table(manifest)
    row = table.row(0, named=True)
    forbidden = row["forbidden_actions"]

    for required in [
        "curated-embedding-preflight run",
        "curated_embedding_preflight run",
        "curated-embedding-single run",
        "curated_embedding_single run",
        "help run",
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
        "enrichment rerun",
        "contrast rerun",
        "biological claim",
    ]:
        assert required in forbidden
