from __future__ import annotations

from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.g3sx30_dry_run_preflight_manifest import (
    G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA,
    validate_g3sx30_dry_run_preflight_manifest_rows,
)

DEFAULT_SOURCE_MANIFEST = Path("data/input/g3sx30_dry_run_preflight_manifest.csv")
DEFAULT_SOURCE_MANIFEST_ROW_INDEX = 1

EXPECTED_TARGET_ACCESSION = "G3SX30"
EXPECTED_TARGET_ACCESSION_DB = "UniProtKB TrEMBL"
EXPECTED_TARGET_SPECIES = "Loxodonta africana"
EXPECTED_TARGET_TAXID = 9785
EXPECTED_GENE_SYMBOL = "MDM2"
EXPECTED_CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
EXPECTED_SEQUENCE_LENGTH = 492
EXPECTED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"

ADAPTER_STATUS = "manifest_understood_runtime_blocked"
ADAPTER_DECISION = "do_not_execute_current_cli_directly"
CURRENT_CLI_COMPATIBILITY = "not_directly_executable_manifest_mismatch_output_path_issue"
REQUIRED_NEXT_ACTION = "add_manifest_aware_wrapper_or_guardrail_before_execution"
OUTPUT_PATH_POLICY = "do_not_write_committed_data_output"
ALLOWED_OUTPUT_LOCATION = "not_selected_scaffold_only"
CLAIM_STATUS = "technical_checkpoint"

FORBIDDEN_ACTIONS = (
    "curated-embedding-preflight run; curated_embedding_preflight run; "
    "curated-embedding-single run; curated_embedding_single run; help run; "
    "Biohub call; ESMC call; embedding generation; .npy artifact; "
    "data/output artifact commit; ready_for_preflight; manifest runtime unlock; "
    "Gate 8 promotion; Gate 9 promotion; Boltz call; AF3 call; Chai call; "
    "enrichment rerun; contrast rerun; biological claim"
)

ADAPTER_SCHEMA = {
    "source_manifest_table": pl.Utf8,
    "source_manifest_row_index": pl.Int64,
    "candidate_id": pl.Utf8,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_species": pl.Utf8,
    "target_taxid": pl.Int64,
    "gene_symbol": pl.Utf8,
    "reviewed_sequence_sha256": pl.Utf8,
    "reviewed_sequence_length": pl.Int64,
    "manifest_entry_status": pl.Utf8,
    "dry_run_only": pl.Boolean,
    "max_live_batch_size": pl.Int64,
    "ready_for_preflight_after_manifest": pl.Utf8,
    "sequence_fetch_allowed": pl.Boolean,
    "biohub_call_allowed": pl.Boolean,
    "esmc_call_allowed": pl.Boolean,
    "embedding_generation_allowed": pl.Boolean,
    "curated_embedding_preflight_allowed": pl.Boolean,
    "curated_embedding_single_allowed": pl.Boolean,
    "adapter_status": pl.Utf8,
    "adapter_decision": pl.Utf8,
    "current_cli_compatibility": pl.Utf8,
    "required_next_action": pl.Utf8,
    "curated_embedding_preflight_runtime_allowed": pl.Boolean,
    "curated_embedding_single_runtime_allowed": pl.Boolean,
    "output_path_policy": pl.Utf8,
    "allowed_output_location": pl.Utf8,
    "claim_status": pl.Utf8,
    "forbidden_actions": pl.Utf8,
    "review_note": pl.Utf8,
}

REQUIRED_COLUMNS = list(ADAPTER_SCHEMA)


def empty_g3sx30_manifest_aware_dry_run_preflight_adapter_table() -> pl.DataFrame:
    return pl.DataFrame(schema=ADAPTER_SCHEMA)


def read_g3sx30_dry_run_preflight_manifest(path: Path = DEFAULT_SOURCE_MANIFEST) -> pl.DataFrame:
    return pl.read_csv(path, schema_overrides=G3SX30_DRY_RUN_PREFLIGHT_MANIFEST_SCHEMA)


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


def _select_manifest_row(manifest: pl.DataFrame, row_index: int) -> dict[str, object]:
    if row_index < 1:
        raise ValueError("source_manifest_row_index is 1-based and must be positive")
    if row_index > manifest.height:
        raise ValueError(
            f"Missing manifest row index {row_index}; manifest has {manifest.height} rows"
        )
    return manifest.row(row_index - 1, named=True)


def _require_manifest_identity(row: dict[str, object]) -> None:
    expected_strings = {
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "reviewed_sequence_sha256": EXPECTED_SEQUENCE_SHA256,
        "manifest_entry_status": "manifest_scaffold_ready_runtime_blocked",
        "ready_for_preflight_after_manifest": "false",
        "claim_status": CLAIM_STATUS,
    }
    for column, expected_text in expected_strings.items():
        observed_text = _row_str(row, column)
        if observed_text != expected_text:
            raise ValueError(f"Expected {column}={expected_text!r}, observed {observed_text!r}")

    expected_ints = {
        "target_taxid": EXPECTED_TARGET_TAXID,
        "reviewed_sequence_length": EXPECTED_SEQUENCE_LENGTH,
        "max_live_batch_size": 0,
    }
    for column, expected_int in expected_ints.items():
        observed_int = _row_int(row, column)
        if observed_int != expected_int:
            raise ValueError(f"Expected {column}={expected_int}, observed {observed_int}")

    if not _row_bool(row, "dry_run_only"):
        raise ValueError("Expected dry_run_only=true")

    for column in [
        "sequence_fetch_allowed",
        "biohub_call_allowed",
        "esmc_call_allowed",
        "embedding_generation_allowed",
        "curated_embedding_preflight_allowed",
        "curated_embedding_single_allowed",
    ]:
        if _row_bool(row, column):
            raise ValueError(f"Expected {column}=false")


def build_g3sx30_manifest_aware_dry_run_preflight_adapter_table(
    manifest: pl.DataFrame,
    *,
    source_manifest_table: str = "data/input/g3sx30_dry_run_preflight_manifest.csv",
    source_manifest_row_index: int = DEFAULT_SOURCE_MANIFEST_ROW_INDEX,
) -> pl.DataFrame:
    validate_g3sx30_dry_run_preflight_manifest_rows(manifest)
    row = _select_manifest_row(manifest, source_manifest_row_index)
    _require_manifest_identity(row)

    review_note = (
        "Manifest-aware dry-run preflight adapter scaffold only. The manifest row is "
        "understood and remains runtime-blocked. Current curated embedding CLI behavior "
        "must not be executed directly against G3SX30 until a manifest-aware wrapper or "
        "source-level guardrail resolves the manifest mismatch and data/output default."
    )

    return pl.DataFrame(
        [
            {
                "source_manifest_table": source_manifest_table,
                "source_manifest_row_index": source_manifest_row_index,
                "candidate_id": _row_str(row, "candidate_id"),
                "target_accession": _row_str(row, "target_accession"),
                "target_accession_db": _row_str(row, "target_accession_db"),
                "target_species": _row_str(row, "target_species"),
                "target_taxid": _row_int(row, "target_taxid"),
                "gene_symbol": _row_str(row, "gene_symbol"),
                "reviewed_sequence_sha256": _row_str(row, "reviewed_sequence_sha256"),
                "reviewed_sequence_length": _row_int(row, "reviewed_sequence_length"),
                "manifest_entry_status": _row_str(row, "manifest_entry_status"),
                "dry_run_only": _row_bool(row, "dry_run_only"),
                "max_live_batch_size": _row_int(row, "max_live_batch_size"),
                "ready_for_preflight_after_manifest": _row_str(
                    row, "ready_for_preflight_after_manifest"
                ),
                "sequence_fetch_allowed": _row_bool(row, "sequence_fetch_allowed"),
                "biohub_call_allowed": _row_bool(row, "biohub_call_allowed"),
                "esmc_call_allowed": _row_bool(row, "esmc_call_allowed"),
                "embedding_generation_allowed": _row_bool(row, "embedding_generation_allowed"),
                "curated_embedding_preflight_allowed": _row_bool(
                    row, "curated_embedding_preflight_allowed"
                ),
                "curated_embedding_single_allowed": _row_bool(
                    row, "curated_embedding_single_allowed"
                ),
                "adapter_status": ADAPTER_STATUS,
                "adapter_decision": ADAPTER_DECISION,
                "current_cli_compatibility": CURRENT_CLI_COMPATIBILITY,
                "required_next_action": REQUIRED_NEXT_ACTION,
                "curated_embedding_preflight_runtime_allowed": False,
                "curated_embedding_single_runtime_allowed": False,
                "output_path_policy": OUTPUT_PATH_POLICY,
                "allowed_output_location": ALLOWED_OUTPUT_LOCATION,
                "claim_status": CLAIM_STATUS,
                "forbidden_actions": FORBIDDEN_ACTIONS,
                "review_note": review_note,
            }
        ],
        schema=ADAPTER_SCHEMA,
    ).select(REQUIRED_COLUMNS)


def validate_g3sx30_manifest_aware_dry_run_preflight_adapter_schema(table: pl.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in table.columns]
    if missing:
        raise ValueError(f"Missing required adapter columns: {missing}")


def validate_g3sx30_manifest_aware_dry_run_preflight_adapter_rows(table: pl.DataFrame) -> None:
    validate_g3sx30_manifest_aware_dry_run_preflight_adapter_schema(table)

    for row in table.iter_rows(named=True):
        _require_manifest_identity(row)

        expected_strings = {
            "source_manifest_table": "data/input/g3sx30_dry_run_preflight_manifest.csv",
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
                raise ValueError(f"Expected {column}={expected_text!r}, observed {observed_text!r}")

        if _row_int(row, "source_manifest_row_index") != 1:
            raise ValueError("Adapter scaffold must reference source manifest row index 1")

        for column in [
            "curated_embedding_preflight_runtime_allowed",
            "curated_embedding_single_runtime_allowed",
        ]:
            if _row_bool(row, column):
                raise ValueError(f"Adapter scaffold must keep {column}=false")

        forbidden_actions = _row_str(row, "forbidden_actions")
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
            if required not in forbidden_actions:
                raise ValueError(f"Missing forbidden action guardrail: {required}")
