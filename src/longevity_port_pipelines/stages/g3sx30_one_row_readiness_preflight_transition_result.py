"""G3SX30 one-row readiness/preflight transition result helper."""

from __future__ import annotations

import csv
from pathlib import Path

DEFAULT_SOURCE_DECISION_TABLE = Path(
    "data/input/g3sx30_one_row_readiness_preflight_transition_decisions.csv"
)
DEFAULT_TRANSITION_RESULT_TABLE = Path(
    "data/input/g3sx30_one_row_readiness_preflight_transition_results.csv"
)

EXPECTED = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "target_accession": "G3SX30",
    "target_accession_db": "UniProtKB TrEMBL",
    "target_species": "Loxodonta africana",
    "target_taxid": "9785",
    "gene_symbol": "MDM2",
    "source_decision_table": "data/input/g3sx30_one_row_readiness_preflight_transition_decisions.csv",
    "source_decision_row_index": "1",
    "source_decision": "approve_one_row_readiness_preflight_transition_path",
    "source_approved_for_next_transition_step": "true",
    "source_allowed_next_action": "run_one_row_g3sx30_readiness_preflight_transition",
    "source_next_pr_must_be_actual_transition_check": "true",
    "source_no_additional_decision_before_transition": "true",
    "transition_action": "run_one_row_g3sx30_readiness_preflight_transition",
    "transition_status": "one_row_readiness_preflight_transition_passed",
    "one_row_only": "true",
    "ready_for_preflight": "true",
    "ready_scope": "one_row_g3sx30_elephant_mdm2_only",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "data_output_artifact_committed": "false",
    "local_embedding_path": (
        "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
    ),
    "local_runtime_embedding_tracked": "false",
    "local_runtime_embedding_committed": "false",
    "biohub_esmc_called_by_transition": "false",
    "live_embedding_rerun_by_transition": "false",
    "embedding_generation_performed_by_transition": "false",
    "npy_artifact_created_by_transition": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "enrichment_rerun": "false",
    "contrast_rerun": "false",
    "allowed_downstream_use_path": (
        "first_controlled_downstream_use_path_for_one_row_ready_artifact"
    ),
    "next_step": "add_first_controlled_downstream_use_path_for_one_row_ready_artifact",
}

SOURCE_DECISION_EXPECTED = {
    "decision": "approve_one_row_readiness_preflight_transition_path",
    "approved_for_next_transition_step": "true",
    "ready_for_preflight": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "allowed_next_action": "run_one_row_g3sx30_readiness_preflight_transition",
    "next_pr_must_be_actual_transition_check": "true",
    "no_additional_decision_before_transition": "true",
}

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
    "additional transition approval before downstream use",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def _repo_relative_text(path: Path) -> str:
    if path.is_absolute():
        try:
            return path.relative_to(Path.cwd()).as_posix()
        except ValueError:
            return path.as_posix()
    return str(path).replace("\\", "/")


def _require(row: dict[str, str], field: str, expected: str) -> None:
    value = row.get(field)
    if value != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {value!r}")


def validate_source_decision_row(row: dict[str, str]) -> None:
    for field, expected in SOURCE_DECISION_EXPECTED.items():
        _require(row, field, expected)


def build_transition_result_row_from_source_decision(
    source_decision_row: dict[str, str],
    *,
    source_decision_table: Path = DEFAULT_SOURCE_DECISION_TABLE,
) -> dict[str, str]:
    validate_source_decision_row(source_decision_row)
    row = dict(EXPECTED)
    row["source_decision_table"] = _repo_relative_text(source_decision_table)
    row["candidate_set"] = source_decision_row["candidate_set"]
    row["lane_name"] = source_decision_row["lane_name"]
    row["candidate_id"] = source_decision_row["candidate_id"]
    row["target_accession"] = source_decision_row["target_accession"]
    row["target_accession_db"] = source_decision_row["target_accession_db"]
    row["target_species"] = source_decision_row["target_species"]
    row["target_taxid"] = source_decision_row["target_taxid"]
    row["gene_symbol"] = source_decision_row["gene_symbol"]
    row["source_decision"] = source_decision_row["decision"]
    row["source_approved_for_next_transition_step"] = source_decision_row[
        "approved_for_next_transition_step"
    ]
    row["source_allowed_next_action"] = source_decision_row["allowed_next_action"]
    row["source_next_pr_must_be_actual_transition_check"] = source_decision_row[
        "next_pr_must_be_actual_transition_check"
    ]
    row["source_no_additional_decision_before_transition"] = source_decision_row[
        "no_additional_decision_before_transition"
    ]
    row["forbidden_actions"] = "; ".join(FORBIDDEN_ACTIONS)
    row["reviewer_id"] = "manual_gate_review"
    row["transition_date"] = "2026-07-09"
    row["transition_note"] = (
        "Actual one-row G3SX30 readiness/preflight transition/check result. "
        "This consumes the final transition decision row and marks only this "
        "single G3SX30 elephant MDM2 row ready_for_preflight=true. It does not "
        "promote Gate 8, Gate 9, or any biological claim. It does not call "
        "Biohub/ESMC, rerun live embedding, generate an embedding, or commit the "
        "local .npy/data-output artifact. After this PR, the next step should be "
        "the first controlled downstream use path for the one-row ready artifact, "
        "not another transition approval."
    )
    return row


def validate_transition_result_row(row: dict[str, str]) -> None:
    for field, expected in EXPECTED.items():
        _require(row, field, expected)
    for forbidden in FORBIDDEN_ACTIONS:
        if forbidden not in row.get("forbidden_actions", ""):
            raise ValueError(f"Missing forbidden action token: {forbidden!r}")


def load_and_validate_transition_result(
    table: Path = DEFAULT_TRANSITION_RESULT_TABLE,
) -> dict[str, str]:
    row = require_single_row(table)
    validate_transition_result_row(row)
    return row


def load_source_decision_and_build_transition_result(
    table: Path = DEFAULT_SOURCE_DECISION_TABLE,
) -> dict[str, str]:
    source = require_single_row(table)
    return build_transition_result_row_from_source_decision(
        source,
        source_decision_table=table,
    )
