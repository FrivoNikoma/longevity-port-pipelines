from __future__ import annotations

from pathlib import Path

import polars as pl

DEFAULT_REPAIR_DECISIONS_PATH = Path("data/input/tp53_mdm2_ortholog_repair_decisions.csv")

EXPECTED_CANDIDATE_SET = "tp53_mdm2_elephant"

REQUIRED_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "partner_uniprot",
    "target_species",
    "coverage_preflight_status",
    "source_ortholog_status",
    "local_candidate_row_status",
    "recommended_next_action",
    "repair_decision",
    "repair_priority",
    "claim_policy",
    "repair_note",
)

DECISION_KEY_COLUMNS = (
    "candidate_id",
    "source_uniprot",
    "target_species",
    "chain",
)

ALLOWED_REPAIR_DECISIONS = {
    "fetch_or_curate_source_ortholog",
    "review_local_rows_without_source_ortholog",
    "defer_until_manual_review",
    "coverage_ready",
}

ALLOWED_REPAIR_PRIORITIES = {
    "high",
    "medium",
    "low",
}

ALLOWED_CLAIM_POLICIES = {
    "ortholog_repair_only",
    "deferred_no_claim",
    "technical_checkpoint_no_claim",
}

ALLOWED_COVERAGE_PREFLIGHT_STATUSES = {
    "blocked_pending_coverage_repair",
    "coverage_marked_ready_in_manifest",
    "blocked_by_noncoverage_gate",
}

ALLOWED_SOURCE_ORTHOLOG_STATUSES = {
    "not_checked",
    "missing_source_ortholog",
    "present_source_ortholog",
    "manual_review_required",
}

ALLOWED_LOCAL_CANDIDATE_ROW_STATUSES = {
    "not_checked",
    "missing_local_candidate_row",
    "present_local_candidate_row",
    "manual_review_required",
}


def read_repair_decisions(
    path: Path = DEFAULT_REPAIR_DECISIONS_PATH,
) -> pl.DataFrame:
    """Read the TP53/MDM2 ortholog repair decision table."""
    return pl.read_csv(path, infer_schema_length=0)


def _missing_columns(rows: pl.DataFrame) -> list[str]:
    return [column for column in REQUIRED_COLUMNS if column not in rows.columns]


def _invalid_values(
    rows: pl.DataFrame,
    *,
    column: str,
    allowed_values: set[str],
) -> list[str]:
    if column not in rows.columns:
        return []

    return sorted(
        value for value in rows.get_column(column).unique().to_list() if value not in allowed_values
    )


def find_duplicate_decision_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate TP53/MDM2 repair decision keys."""
    return (
        rows.group_by(list(DECISION_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(DECISION_KEY_COLUMNS))
    )


def validate_repair_decisions(rows: pl.DataFrame) -> None:
    """Validate TP53/MDM2 ortholog repair decisions without making claims."""

    missing = _missing_columns(rows)
    if missing:
        raise ValueError(
            "TP53/MDM2 repair decision table is missing required columns: " + ", ".join(missing)
        )

    duplicate_keys = find_duplicate_decision_keys(rows)
    if duplicate_keys.height:
        raise ValueError(
            "TP53/MDM2 repair decision table has duplicate candidate/source/species/chain keys."
        )

    checks = {
        "candidate_set": {EXPECTED_CANDIDATE_SET},
        "coverage_preflight_status": ALLOWED_COVERAGE_PREFLIGHT_STATUSES,
        "source_ortholog_status": ALLOWED_SOURCE_ORTHOLOG_STATUSES,
        "local_candidate_row_status": ALLOWED_LOCAL_CANDIDATE_ROW_STATUSES,
        "repair_decision": ALLOWED_REPAIR_DECISIONS,
        "repair_priority": ALLOWED_REPAIR_PRIORITIES,
        "claim_policy": ALLOWED_CLAIM_POLICIES,
    }
    for column, allowed_values in checks.items():
        invalid = _invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"TP53/MDM2 repair decision table has invalid values in {column}: "
                + ", ".join(invalid)
            )

    blank_required = []
    for column in (
        "candidate_set",
        "candidate_id",
        "source_uniprot",
        "partner_uniprot",
        "target_species",
        "repair_decision",
        "repair_priority",
        "claim_policy",
        "repair_note",
    ):
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "TP53/MDM2 repair decision table has blank required decision fields: "
            + ", ".join(blank_required)
        )
