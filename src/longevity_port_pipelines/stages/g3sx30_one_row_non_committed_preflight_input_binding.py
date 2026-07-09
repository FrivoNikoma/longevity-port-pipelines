"""Validate the G3SX30 non-committed preflight input binding.

This helper validates table semantics only. It does not read the generated .npy,
call Biohub / ESMC, generate embeddings, run preflight, promote gates, or make
biological claims.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import cast

DEFAULT_DECISION_TABLE = Path(
    "data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv"
)
DEFAULT_BINDING_TABLE = Path("data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv")

EXPECTED_LOCAL_EMBEDDING_PATH = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_NEXT_CHECK = "run_record_g3sx30_one_row_local_embedding_preflight_check"
EXPECTED_FORBIDDEN_ACTIONS = (
    "Biohub call",
    "ESMC call",
    "live embedding rerun",
    "embedding generation",
    ".npy commit",
    "data/output commit",
    "external FASTA commit",
    "external live log commit",
    "external validation JSON commit",
    "ready_for_preflight promotion",
    "Gate 8 promotion",
    "Gate 9 promotion",
    "Boltz call",
    "AF3 call",
    "Chai call",
    "enrichment rerun",
    "contrast rerun",
    "biological claim",
)

DECISION_EXPECTED = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "local_embedding_path": EXPECTED_LOCAL_EMBEDDING_PATH,
    "artifact_location": "local_runtime_data_output_ignored_by_git",
    "local_runtime_embedding_exists": "true",
    "local_runtime_embedding_tracked": "false",
    "local_runtime_embedding_committed": "false",
    "embedding_shape": "492x960",
    "embedding_dtype": "float32",
    "embedding_finite": "true",
    "sequence_length_matches": "true",
    "approved_for_one_row_readiness_preflight_input": "true",
    "readiness_preflight_input_record_status": "approved_local_runtime_artifact_as_one_row_readiness_preflight_input",
    "ready_for_preflight": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "allowed_next_action": "prepare_one_row_non_committed_preflight_input_consumer_or_manifest_binding_pr",
}

BINDING_EXPECTED = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "target_accession": "G3SX30",
    "target_accession_db": "UniProtKB TrEMBL",
    "target_species": "Loxodonta africana",
    "target_taxid": "9785",
    "gene_symbol": "MDM2",
    "source_decision_table": str(DEFAULT_DECISION_TABLE).replace("\\", "/"),
    "source_decision_row_index": "1",
    "source_decision_status": "approved_local_runtime_artifact_as_one_row_readiness_preflight_input",
    "local_embedding_path": EXPECTED_LOCAL_EMBEDDING_PATH,
    "artifact_location": "local_runtime_data_output_ignored_by_git",
    "local_runtime_embedding_exists": "true",
    "local_runtime_embedding_tracked": "false",
    "local_runtime_embedding_committed": "false",
    "embedding_shape": "492x960",
    "embedding_dtype": "float32",
    "embedding_finite": "true",
    "sequence_length_matches": "true",
    "approved_for_one_row_readiness_preflight_input": "true",
    "non_committed_preflight_input_reference_created": "true",
    "ready_for_preflight": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "next_concrete_check": EXPECTED_NEXT_CHECK,
    "next_check_scope": "local_artifact_shape_dtype_finiteness_sequence_length_path_policy_only",
    "next_check_input": "data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv#1",
    "next_check_output_policy": "external_non_committed_observation_only",
    "next_check_output_example": "D:/biohub_projects/_chatgpt_observations/g3sx30_one_row_local_embedding_preflight_check.json",
    "allowed_next_action_after_binding": EXPECTED_NEXT_CHECK,
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [cast(dict[str, str], row) for row in csv.DictReader(handle)]


def read_one_row(path: Path) -> dict[str, str]:
    rows = read_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def _require_expected(row: dict[str, str], expected: dict[str, str]) -> None:
    missing = [field for field in expected if field not in row]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    for field, expected_value in expected.items():
        value = row[field]
        if value != expected_value:
            raise ValueError(f"Expected {field}={expected_value!r}, got {value!r}")


def validate_decision_row(row: dict[str, str]) -> None:
    _require_expected(row, DECISION_EXPECTED)


def build_binding_row(decision_row: dict[str, str]) -> dict[str, str]:
    validate_decision_row(decision_row)

    return {
        **BINDING_EXPECTED,
        "forbidden_actions": "; ".join(EXPECTED_FORBIDDEN_ACTIONS),
        "reviewer_id": "manual_gate_review",
        "review_date": "2026-07-09",
        "binding_note": (
            "Creates a repo-visible non-committed preflight input binding for the "
            "already-generated local runtime G3SX30 / elephant MDM2 ESMC embedding "
            "artifact. This binding identifies the biological target and local "
            "artifact, confirms the approved one-row readiness/preflight input "
            "decision, and names the next concrete local artifact preflight check. "
            "It does not consume the artifact for analysis and does not promote "
            "ready_for_preflight, Gate 8, Gate 9, or any biological claim."
        ),
    }


def validate_binding_row(row: dict[str, str]) -> None:
    _require_expected(row, BINDING_EXPECTED)

    forbidden_actions = row.get("forbidden_actions", "")
    missing = [
        forbidden for forbidden in EXPECTED_FORBIDDEN_ACTIONS if forbidden not in forbidden_actions
    ]
    if missing:
        raise ValueError(f"Missing forbidden action tokens: {missing}")


def load_decision_and_build_binding(
    decision_table: Path = DEFAULT_DECISION_TABLE,
) -> dict[str, str]:
    return build_binding_row(read_one_row(decision_table))


def load_and_validate_binding(
    binding_table: Path = DEFAULT_BINDING_TABLE,
) -> dict[str, str]:
    row = read_one_row(binding_table)
    validate_binding_row(row)
    return row
