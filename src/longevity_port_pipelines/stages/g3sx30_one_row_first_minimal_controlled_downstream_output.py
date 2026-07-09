"""G3SX30 one-row first minimal controlled downstream output helpers.

This module validates the committed output record created from the passed
controlled downstream read/check result for the one-row ready G3SX30 elephant
MDM2 local runtime artifact.

The output is a one-row artifact identity and embedding health summary. It does
not call Biohub / ESMC, generate a new embedding, commit the generated .npy
artifact, promote Gate 8 or Gate 9, rerun enrichment/contrast, or make a
biological claim.
"""

from __future__ import annotations

import csv
from pathlib import Path

DEFAULT_SOURCE_READ_CHECK_RESULT_TABLE = Path(
    "data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv"
)
DEFAULT_OUTPUT_TABLE = Path(
    "data/input/g3sx30_one_row_first_minimal_controlled_downstream_outputs.csv"
)

EXPECTED_CANDIDATE_SET = "tp53_mdm2_elephant"
EXPECTED_LANE_NAME = "tp53_mdm2_elephant"
EXPECTED_CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
EXPECTED_TARGET_ACCESSION = "G3SX30"
EXPECTED_TARGET_ACCESSION_DB = "UniProtKB TrEMBL"
EXPECTED_TARGET_SPECIES = "Loxodonta africana"
EXPECTED_TARGET_TAXID = "9785"
EXPECTED_GENE_SYMBOL = "MDM2"
EXPECTED_SOURCE_READ_CHECK_ACTION = (
    "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact"
)
EXPECTED_SOURCE_READ_CHECK_STATUS = "controlled_downstream_read_check_passed"
EXPECTED_CONTROLLED_HANDLE_ID = (
    "g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle"
)
EXPECTED_CONTROLLED_INPUT_STATUS = "one_row_ready_artifact_available_for_controlled_downstream_use"
EXPECTED_READY_ARTIFACT_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_EMBEDDING_SHAPE = "492x960"
EXPECTED_EMBEDDING_DTYPE = "float32"
EXPECTED_SEQUENCE_LENGTH = "492"
EXPECTED_READY_SCOPE = "one_row_g3sx30_elephant_mdm2_only"
EXPECTED_OUTPUT_RECORD_ID = (
    "g3sx30_elephant_mdm2_one_row_artifact_identity_embedding_health_summary"
)
EXPECTED_OUTPUT_ACTION = (
    "add_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact"
)
EXPECTED_OUTPUT_STATUS = "first_minimal_controlled_downstream_output_created"
EXPECTED_OUTPUT_TYPE = "one_row_artifact_identity_and_embedding_health_summary"
EXPECTED_OUTPUT_SCOPE = "identity_and_embedding_health_only_no_biological_claim"
EXPECTED_NEXT_STEP = (
    "move_toward_first_analysis_adjacent_controlled_output_or_next_concrete_"
    "biological_data_bearing_step_for_one_row_ready_g3sx30_artifact"
)

SOURCE_READ_CHECK_REQUIRED_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "source_downstream_use_path_table",
    "source_downstream_use_path_row_index",
    "read_check_action",
    "read_check_status",
    "controlled_handle_id",
    "controlled_input_status",
    "source_ready_artifact_reference",
    "local_runtime_embedding_exists",
    "local_runtime_embedding_tracked",
    "local_runtime_embedding_committed",
    "git_ignore_rule_status",
    "embedding_shape",
    "embedding_dtype",
    "embedding_finite",
    "sequence_length",
    "sequence_length_matches",
    "one_row_only",
    "ready_scope",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "data_output_artifact_committed",
    "biohub_esmc_called_by_read_check",
    "live_embedding_rerun_by_read_check",
    "embedding_generation_performed_by_read_check",
    "npy_artifact_created_by_read_check",
    "boltz_called",
    "af3_called",
    "chai_called",
    "enrichment_rerun",
    "contrast_rerun",
    "next_step",
    "next_pr_should_move_toward_first_minimal_controlled_downstream_output",
    "no_additional_read_check_approval_before_output",
)

OUTPUT_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "source_read_check_result_table",
    "source_read_check_result_row_index",
    "source_read_check_action",
    "source_read_check_status",
    "source_controlled_handle_id",
    "source_controlled_input_status",
    "source_ready_artifact_reference",
    "source_local_runtime_embedding_exists",
    "source_local_runtime_embedding_tracked",
    "source_local_runtime_embedding_committed",
    "source_git_ignore_rule_status",
    "source_embedding_shape",
    "source_embedding_dtype",
    "source_embedding_finite",
    "source_sequence_length",
    "source_sequence_length_matches",
    "source_one_row_only",
    "source_ready_scope",
    "output_record_id",
    "output_action",
    "output_status",
    "output_type",
    "output_scope",
    "artifact_identity_summary",
    "embedding_health_summary",
    "candidate_identity_confirmed",
    "artifact_reference_confirmed",
    "embedding_health_confirmed",
    "one_row_only",
    "ready_scope",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "data_output_artifact_committed",
    "biohub_esmc_called_by_output",
    "live_embedding_rerun_by_output",
    "embedding_generation_performed_by_output",
    "npy_artifact_created_by_output",
    "boltz_called",
    "af3_called",
    "chai_called",
    "enrichment_rerun",
    "contrast_rerun",
    "next_step",
    "next_pr_should_be_concrete_analysis_adjacent_or_biological_data_bearing_step",
    "no_additional_non_result_layer_before_next_concrete_step",
    "forbidden_actions",
    "recorder_id",
    "output_date",
    "output_note",
)

FORBIDDEN_ACTIONS = (
    "Biohub call",
    "ESMC call",
    "live embedding rerun",
    "embedding generation",
    ".npy commit",
    "data/output commit",
    "Gate 8 promotion",
    "Gate 9 promotion",
    "Boltz call",
    "AF3 call",
    "Chai call",
    "enrichment rerun",
    "contrast rerun",
    "biological claim",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries."""

    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    """Read exactly one CSV row."""

    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def _require_fields(row: dict[str, str], fields: tuple[str, ...]) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")


def _require_value(row: dict[str, str], field: str, expected: str) -> None:
    value = row.get(field)
    if value != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {value!r}")


def _repo_relative_text(path: Path) -> str:
    """Render a path as repo-relative text when possible."""

    if path.is_absolute():
        try:
            return path.relative_to(Path.cwd()).as_posix()
        except ValueError:
            return path.as_posix()
    return str(path).replace("\\", "/")


def validate_source_read_check_result_row(row: dict[str, str]) -> None:
    """Validate the passed read/check result consumed by this output."""

    _require_fields(row, SOURCE_READ_CHECK_REQUIRED_FIELDS)

    expected_values = {
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "lane_name": EXPECTED_LANE_NAME,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "read_check_action": EXPECTED_SOURCE_READ_CHECK_ACTION,
        "read_check_status": EXPECTED_SOURCE_READ_CHECK_STATUS,
        "controlled_handle_id": EXPECTED_CONTROLLED_HANDLE_ID,
        "controlled_input_status": EXPECTED_CONTROLLED_INPUT_STATUS,
        "source_ready_artifact_reference": EXPECTED_READY_ARTIFACT_REFERENCE,
        "local_runtime_embedding_exists": "true",
        "local_runtime_embedding_tracked": "false",
        "local_runtime_embedding_committed": "false",
        "git_ignore_rule_status": "data_output_ignored",
        "embedding_shape": EXPECTED_EMBEDDING_SHAPE,
        "embedding_dtype": EXPECTED_EMBEDDING_DTYPE,
        "embedding_finite": "true",
        "sequence_length": EXPECTED_SEQUENCE_LENGTH,
        "sequence_length_matches": "true",
        "one_row_only": "true",
        "ready_scope": EXPECTED_READY_SCOPE,
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "data_output_artifact_committed": "false",
        "biohub_esmc_called_by_read_check": "false",
        "live_embedding_rerun_by_read_check": "false",
        "embedding_generation_performed_by_read_check": "false",
        "npy_artifact_created_by_read_check": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "enrichment_rerun": "false",
        "contrast_rerun": "false",
        "next_step": (
            "move_toward_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact"
        ),
        "next_pr_should_move_toward_first_minimal_controlled_downstream_output": "true",
        "no_additional_read_check_approval_before_output": "true",
    }

    for field, expected in expected_values.items():
        _require_value(row, field, expected)


def build_output_row_from_source_read_check(
    source_row: dict[str, str],
    *,
    source_read_check_result_table: Path = DEFAULT_SOURCE_READ_CHECK_RESULT_TABLE,
    source_read_check_result_row_index: int = 1,
) -> dict[str, str]:
    """Build the first minimal controlled downstream output row."""

    validate_source_read_check_result_row(source_row)

    artifact_identity_summary = (
        "candidate=tp53_mdm2_elephant_seed_mdm2_chain; "
        "accession=G3SX30; species=Loxodonta africana; taxid=9785; gene=MDM2"
    )
    embedding_health_summary = (
        "local_runtime_embedding_exists=true; tracked=false; committed=false; "
        "ignored=data_output_ignored; shape=492x960; dtype=float32; finite=true; "
        "sequence_length_matches=true"
    )

    return {
        "candidate_set": source_row["candidate_set"],
        "lane_name": source_row["lane_name"],
        "candidate_id": source_row["candidate_id"],
        "target_accession": source_row["target_accession"],
        "target_accession_db": source_row["target_accession_db"],
        "target_species": source_row["target_species"],
        "target_taxid": source_row["target_taxid"],
        "gene_symbol": source_row["gene_symbol"],
        "source_read_check_result_table": _repo_relative_text(source_read_check_result_table),
        "source_read_check_result_row_index": str(source_read_check_result_row_index),
        "source_read_check_action": source_row["read_check_action"],
        "source_read_check_status": source_row["read_check_status"],
        "source_controlled_handle_id": source_row["controlled_handle_id"],
        "source_controlled_input_status": source_row["controlled_input_status"],
        "source_ready_artifact_reference": source_row["source_ready_artifact_reference"],
        "source_local_runtime_embedding_exists": source_row["local_runtime_embedding_exists"],
        "source_local_runtime_embedding_tracked": source_row["local_runtime_embedding_tracked"],
        "source_local_runtime_embedding_committed": source_row["local_runtime_embedding_committed"],
        "source_git_ignore_rule_status": source_row["git_ignore_rule_status"],
        "source_embedding_shape": source_row["embedding_shape"],
        "source_embedding_dtype": source_row["embedding_dtype"],
        "source_embedding_finite": source_row["embedding_finite"],
        "source_sequence_length": source_row["sequence_length"],
        "source_sequence_length_matches": source_row["sequence_length_matches"],
        "source_one_row_only": source_row["one_row_only"],
        "source_ready_scope": source_row["ready_scope"],
        "output_record_id": EXPECTED_OUTPUT_RECORD_ID,
        "output_action": EXPECTED_OUTPUT_ACTION,
        "output_status": EXPECTED_OUTPUT_STATUS,
        "output_type": EXPECTED_OUTPUT_TYPE,
        "output_scope": EXPECTED_OUTPUT_SCOPE,
        "artifact_identity_summary": artifact_identity_summary,
        "embedding_health_summary": embedding_health_summary,
        "candidate_identity_confirmed": "true",
        "artifact_reference_confirmed": "true",
        "embedding_health_confirmed": "true",
        "one_row_only": source_row["one_row_only"],
        "ready_scope": source_row["ready_scope"],
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "data_output_artifact_committed": "false",
        "biohub_esmc_called_by_output": "false",
        "live_embedding_rerun_by_output": "false",
        "embedding_generation_performed_by_output": "false",
        "npy_artifact_created_by_output": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "enrichment_rerun": "false",
        "contrast_rerun": "false",
        "next_step": EXPECTED_NEXT_STEP,
        "next_pr_should_be_concrete_analysis_adjacent_or_biological_data_bearing_step": "true",
        "no_additional_non_result_layer_before_next_concrete_step": "true",
        "forbidden_actions": "; ".join(FORBIDDEN_ACTIONS),
        "recorder_id": "manual_gate_record",
        "output_date": "2026-07-09",
        "output_note": (
            "Creates the first minimal controlled downstream output from the passed "
            "one-row G3SX30 controlled read/check result. The output is an artifact "
            "identity and embedding health summary only. It confirms candidate identity, "
            "artifact reference, ignored/untracked/uncommitted local runtime artifact "
            "status, shape, dtype, finite values, and sequence-length match. It does "
            "not call Biohub/ESMC, rerun live embedding, generate a new embedding, "
            "commit the .npy or data/output artifact, promote Gate 8 or Gate 9, "
            "rerun enrichment/contrast, call Boltz/AF3/Chai, or make a biological "
            "claim. Next step should be a concrete analysis-adjacent controlled output "
            "or another concrete biological-data-bearing step."
        ),
    }


def validate_output_row(row: dict[str, str]) -> None:
    """Validate the committed first minimal controlled downstream output row."""

    _require_fields(row, OUTPUT_FIELDS)

    expected_values = {
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "lane_name": EXPECTED_LANE_NAME,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "source_read_check_result_table": str(DEFAULT_SOURCE_READ_CHECK_RESULT_TABLE).replace(
            "\\", "/"
        ),
        "source_read_check_result_row_index": "1",
        "source_read_check_action": EXPECTED_SOURCE_READ_CHECK_ACTION,
        "source_read_check_status": EXPECTED_SOURCE_READ_CHECK_STATUS,
        "source_controlled_handle_id": EXPECTED_CONTROLLED_HANDLE_ID,
        "source_controlled_input_status": EXPECTED_CONTROLLED_INPUT_STATUS,
        "source_ready_artifact_reference": EXPECTED_READY_ARTIFACT_REFERENCE,
        "source_local_runtime_embedding_exists": "true",
        "source_local_runtime_embedding_tracked": "false",
        "source_local_runtime_embedding_committed": "false",
        "source_git_ignore_rule_status": "data_output_ignored",
        "source_embedding_shape": EXPECTED_EMBEDDING_SHAPE,
        "source_embedding_dtype": EXPECTED_EMBEDDING_DTYPE,
        "source_embedding_finite": "true",
        "source_sequence_length": EXPECTED_SEQUENCE_LENGTH,
        "source_sequence_length_matches": "true",
        "source_one_row_only": "true",
        "source_ready_scope": EXPECTED_READY_SCOPE,
        "output_record_id": EXPECTED_OUTPUT_RECORD_ID,
        "output_action": EXPECTED_OUTPUT_ACTION,
        "output_status": EXPECTED_OUTPUT_STATUS,
        "output_type": EXPECTED_OUTPUT_TYPE,
        "output_scope": EXPECTED_OUTPUT_SCOPE,
        "candidate_identity_confirmed": "true",
        "artifact_reference_confirmed": "true",
        "embedding_health_confirmed": "true",
        "one_row_only": "true",
        "ready_scope": EXPECTED_READY_SCOPE,
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "data_output_artifact_committed": "false",
        "biohub_esmc_called_by_output": "false",
        "live_embedding_rerun_by_output": "false",
        "embedding_generation_performed_by_output": "false",
        "npy_artifact_created_by_output": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "enrichment_rerun": "false",
        "contrast_rerun": "false",
        "next_step": EXPECTED_NEXT_STEP,
        "next_pr_should_be_concrete_analysis_adjacent_or_biological_data_bearing_step": "true",
        "no_additional_non_result_layer_before_next_concrete_step": "true",
    }

    for field, expected in expected_values.items():
        _require_value(row, field, expected)

    for required in [
        "candidate=tp53_mdm2_elephant_seed_mdm2_chain",
        "accession=G3SX30",
        "species=Loxodonta africana",
        "gene=MDM2",
    ]:
        if required not in row["artifact_identity_summary"]:
            raise ValueError(f"Missing identity summary token: {required!r}")

    for required in [
        "shape=492x960",
        "dtype=float32",
        "finite=true",
        "sequence_length_matches=true",
    ]:
        if required not in row["embedding_health_summary"]:
            raise ValueError(f"Missing embedding health summary token: {required!r}")

    forbidden_actions = row["forbidden_actions"]
    missing_forbidden = [
        forbidden for forbidden in FORBIDDEN_ACTIONS if forbidden not in forbidden_actions
    ]
    if missing_forbidden:
        raise ValueError(f"Missing forbidden action tokens: {missing_forbidden}")


def load_and_validate_output(
    output_table: Path = DEFAULT_OUTPUT_TABLE,
) -> dict[str, str]:
    """Load and validate the committed first minimal output table."""

    row = require_single_row(output_table)
    validate_output_row(row)
    return row


def load_source_and_build_output(
    source_table: Path = DEFAULT_SOURCE_READ_CHECK_RESULT_TABLE,
) -> dict[str, str]:
    """Build the expected output from the source read/check row."""

    source_row = require_single_row(source_table)
    return build_output_row_from_source_read_check(
        source_row,
        source_read_check_result_table=source_table,
    )
