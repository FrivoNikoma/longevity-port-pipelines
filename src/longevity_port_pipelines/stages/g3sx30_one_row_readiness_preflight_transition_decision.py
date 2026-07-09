"""G3SX30 one-row readiness/preflight transition decision helpers.

This module validates the final decision record that approves the one-row
G3SX30 readiness/preflight transition path from a passed local embedding
preflight result.

It records a decision only. It does not call Biohub / ESMC, generate
embeddings, read or commit the local .npy artifact, promote ready_for_preflight,
promote Gate 8 / Gate 9, or make biological claims.
"""

from __future__ import annotations

import csv
from pathlib import Path

DEFAULT_SOURCE_RESULT_TABLE = Path(
    "data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv"
)
DEFAULT_DECISION_TABLE = Path(
    "data/input/g3sx30_one_row_readiness_preflight_transition_decisions.csv"
)

EXPECTED_CANDIDATE_SET = "tp53_mdm2_elephant"
EXPECTED_LANE_NAME = "tp53_mdm2_elephant"
EXPECTED_CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
EXPECTED_TARGET_ACCESSION = "G3SX30"
EXPECTED_TARGET_ACCESSION_DB = "UniProtKB TrEMBL"
EXPECTED_TARGET_SPECIES = "Loxodonta africana"
EXPECTED_TARGET_TAXID = "9785"
EXPECTED_GENE_SYMBOL = "MDM2"
EXPECTED_SOURCE_CHECK_NAME = "g3sx30_one_row_local_embedding_preflight_check"
EXPECTED_SOURCE_CHECK_STATUS = "local_preflight_pass"
EXPECTED_SOURCE_PREFLIGHT_ARTIFACT_STATUS = "local_artifact_preflight_passed"
EXPECTED_SOURCE_EMBEDDING_SHAPE = "492x960"
EXPECTED_SOURCE_EMBEDDING_DTYPE = "float32"
EXPECTED_DECISION = "approve_one_row_readiness_preflight_transition_path"
EXPECTED_ALLOWED_NEXT_ACTION = "run_one_row_g3sx30_readiness_preflight_transition"
EXPECTED_NEXT_REQUIRED_PR_TITLE = "Run one-row G3SX30 readiness/preflight transition"

SOURCE_RESULT_REQUIRED_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "check_name",
    "check_status",
    "embedding_shape",
    "embedding_dtype",
    "embedding_finite",
    "sequence_length_matches",
    "local_runtime_embedding_tracked",
    "local_runtime_embedding_committed",
    "ready_for_preflight_promoted",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "next_practical_decision",
    "pass_decision_path",
)

DECISION_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "target_accession",
    "target_accession_db",
    "target_species",
    "target_taxid",
    "gene_symbol",
    "source_result_table",
    "source_result_row_index",
    "source_check_name",
    "source_check_status",
    "source_preflight_artifact_status",
    "source_embedding_shape",
    "source_embedding_dtype",
    "source_embedding_finite",
    "source_sequence_length_matches",
    "source_local_runtime_embedding_tracked",
    "source_local_runtime_embedding_committed",
    "decision",
    "approved_for_next_transition_step",
    "ready_for_preflight",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "allowed_next_action",
    "next_pr_must_be_actual_transition_check",
    "no_additional_decision_before_transition",
    "next_required_pr_title",
    "forbidden_actions",
    "reviewer_id",
    "decision_date",
    "decision_note",
)

FORBIDDEN_ACTIONS = (
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
    "additional decision/review/scaffold/binding layer before transition",
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


def validate_source_result_row(row: dict[str, str]) -> None:
    """Validate the passed local preflight result that supports this decision."""

    _require_fields(row, SOURCE_RESULT_REQUIRED_FIELDS)

    expected_values = {
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "lane_name": EXPECTED_LANE_NAME,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "check_name": EXPECTED_SOURCE_CHECK_NAME,
        "check_status": EXPECTED_SOURCE_CHECK_STATUS,
        "embedding_shape": EXPECTED_SOURCE_EMBEDDING_SHAPE,
        "embedding_dtype": EXPECTED_SOURCE_EMBEDDING_DTYPE,
        "embedding_finite": "true",
        "sequence_length_matches": "true",
        "local_runtime_embedding_tracked": "false",
        "local_runtime_embedding_committed": "false",
        "ready_for_preflight_promoted": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "next_practical_decision": (
            "approve_one_row_readiness_preflight_transition_path_or_repair_concrete_blocker"
        ),
        "pass_decision_path": EXPECTED_DECISION,
    }

    for field, expected in expected_values.items():
        _require_value(row, field, expected)


def build_decision_row_from_source_result(
    source_result_row: dict[str, str],
    *,
    source_result_table: Path = DEFAULT_SOURCE_RESULT_TABLE,
    source_result_row_index: int = 1,
) -> dict[str, str]:
    """Build the expected final transition-path decision row."""

    validate_source_result_row(source_result_row)

    return {
        "candidate_set": source_result_row["candidate_set"],
        "lane_name": source_result_row["lane_name"],
        "candidate_id": source_result_row["candidate_id"],
        "target_accession": source_result_row["target_accession"],
        "target_accession_db": source_result_row["target_accession_db"],
        "target_species": source_result_row["target_species"],
        "target_taxid": source_result_row["target_taxid"],
        "gene_symbol": source_result_row["gene_symbol"],
        "source_result_table": _repo_relative_text(source_result_table),
        "source_result_row_index": str(source_result_row_index),
        "source_check_name": source_result_row["check_name"],
        "source_check_status": source_result_row["check_status"],
        "source_preflight_artifact_status": EXPECTED_SOURCE_PREFLIGHT_ARTIFACT_STATUS,
        "source_embedding_shape": source_result_row["embedding_shape"],
        "source_embedding_dtype": source_result_row["embedding_dtype"],
        "source_embedding_finite": source_result_row["embedding_finite"],
        "source_sequence_length_matches": source_result_row["sequence_length_matches"],
        "source_local_runtime_embedding_tracked": source_result_row[
            "local_runtime_embedding_tracked"
        ],
        "source_local_runtime_embedding_committed": source_result_row[
            "local_runtime_embedding_committed"
        ],
        "decision": EXPECTED_DECISION,
        "approved_for_next_transition_step": "true",
        "ready_for_preflight": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "allowed_next_action": EXPECTED_ALLOWED_NEXT_ACTION,
        "next_pr_must_be_actual_transition_check": "true",
        "no_additional_decision_before_transition": "true",
        "next_required_pr_title": EXPECTED_NEXT_REQUIRED_PR_TITLE,
        "forbidden_actions": "; ".join(FORBIDDEN_ACTIONS),
        "reviewer_id": "manual_gate_review",
        "decision_date": "2026-07-09",
        "decision_note": (
            "Final decision PR before the actual one-row G3SX30 readiness/"
            "preflight transition/check. The source local preflight result is "
            "local_preflight_pass, so this row approves only the one-row "
            "readiness/preflight transition path and the exact next action. It "
            "does not promote ready_for_preflight, Gate 8, Gate 9, or any "
            "biological claim. After this PR, the next PR must run the one-row "
            "G3SX30 readiness/preflight transition; no additional decision, "
            "review, scaffold, or binding layer is allowed before that."
        ),
    }


def validate_decision_row(row: dict[str, str]) -> None:
    """Validate the committed final transition-path decision row."""

    _require_fields(row, DECISION_FIELDS)

    expected_values = {
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "lane_name": EXPECTED_LANE_NAME,
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "target_accession": EXPECTED_TARGET_ACCESSION,
        "target_accession_db": EXPECTED_TARGET_ACCESSION_DB,
        "target_species": EXPECTED_TARGET_SPECIES,
        "target_taxid": EXPECTED_TARGET_TAXID,
        "gene_symbol": EXPECTED_GENE_SYMBOL,
        "source_result_table": str(DEFAULT_SOURCE_RESULT_TABLE).replace("\\", "/"),
        "source_result_row_index": "1",
        "source_check_name": EXPECTED_SOURCE_CHECK_NAME,
        "source_check_status": EXPECTED_SOURCE_CHECK_STATUS,
        "source_preflight_artifact_status": EXPECTED_SOURCE_PREFLIGHT_ARTIFACT_STATUS,
        "source_embedding_shape": EXPECTED_SOURCE_EMBEDDING_SHAPE,
        "source_embedding_dtype": EXPECTED_SOURCE_EMBEDDING_DTYPE,
        "source_embedding_finite": "true",
        "source_sequence_length_matches": "true",
        "source_local_runtime_embedding_tracked": "false",
        "source_local_runtime_embedding_committed": "false",
        "decision": EXPECTED_DECISION,
        "approved_for_next_transition_step": "true",
        "ready_for_preflight": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "allowed_next_action": EXPECTED_ALLOWED_NEXT_ACTION,
        "next_pr_must_be_actual_transition_check": "true",
        "no_additional_decision_before_transition": "true",
        "next_required_pr_title": EXPECTED_NEXT_REQUIRED_PR_TITLE,
    }

    for field, expected in expected_values.items():
        _require_value(row, field, expected)

    forbidden_actions = row["forbidden_actions"]
    missing_forbidden = [
        forbidden for forbidden in FORBIDDEN_ACTIONS if forbidden not in forbidden_actions
    ]
    if missing_forbidden:
        raise ValueError(f"Missing forbidden action tokens: {missing_forbidden}")


def load_and_validate_decision(
    decision_table: Path = DEFAULT_DECISION_TABLE,
) -> dict[str, str]:
    """Load and validate the committed one-row transition decision table."""

    row = require_single_row(decision_table)
    validate_decision_row(row)
    return row


def load_source_result_and_build_decision(
    source_result_table: Path = DEFAULT_SOURCE_RESULT_TABLE,
) -> dict[str, str]:
    """Load the source result row and build the expected decision row."""

    source_result_row = require_single_row(source_result_table)
    return build_decision_row_from_source_result(
        source_result_row,
        source_result_table=source_result_table,
    )
