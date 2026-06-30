from __future__ import annotations

from pathlib import Path

import polars as pl

DEFAULT_REPAIR_DECISIONS_PATH = Path("data/input/sirt6_candidate_coverage_repair_decisions.csv")

REQUIRED_COLUMNS = (
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "priority",
    "target_species",
    "target_species_taxid",
    "group",
    "coverage_gap_status",
    "recommended_coverage_action",
    "candidate_target_uniprots",
    "ortholog_source_dbs",
    "ortholog_source_files",
    "local_files",
    "repair_decision",
    "repair_priority",
    "claim_policy",
    "repair_note",
)

DECISION_KEY_COLUMNS = (
    "candidate_id",
    "source_uniprot",
    "target_species",
)

ALLOWED_REPAIR_DECISIONS = {
    "curate_source_ortholog",
    "accept_existing_local_row_after_provenance_review",
    "exclude_from_strict_panel",
    "needs_external_manual_sequence_review",
    "defer_until_stronger_source",
}

ALLOWED_REPAIR_PRIORITIES = {
    "high",
    "medium",
    "low",
}

ALLOWED_CLAIM_POLICIES = {
    "coverage_repair_only",
    "allowed_for_limited_dry_run_only",
    "excluded_from_strict_claim",
    "deferred_no_claim",
}


def read_repair_decisions(path: Path = DEFAULT_REPAIR_DECISIONS_PATH) -> pl.DataFrame:
    """Read the curated candidate coverage repair decision table."""
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
    """Return duplicate candidate/source/species repair decision keys."""
    return (
        rows.group_by(list(DECISION_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(DECISION_KEY_COLUMNS))
    )


def validate_repair_decisions(rows: pl.DataFrame) -> None:
    """Validate the curated repair decision table.

    The table is a conservative human-curated input. It should not create
    biological claims by itself; it only records how provenance blockers should
    be repaired, excluded, or deferred before strict contrast analysis.
    """
    missing = _missing_columns(rows)
    if missing:
        raise ValueError("Repair decision table is missing required columns: " + ", ".join(missing))

    duplicate_keys = find_duplicate_decision_keys(rows)
    if duplicate_keys.height:
        raise ValueError("Repair decision table has duplicate candidate/source/species keys.")

    checks = {
        "repair_decision": ALLOWED_REPAIR_DECISIONS,
        "repair_priority": ALLOWED_REPAIR_PRIORITIES,
        "claim_policy": ALLOWED_CLAIM_POLICIES,
    }
    for column, allowed_values in checks.items():
        invalid = _invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"Repair decision table has invalid values in {column}: " + ", ".join(invalid)
            )

    blank_required = []
    for column in ("repair_decision", "repair_priority", "claim_policy", "repair_note"):
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Repair decision table has blank required decision fields: " + ", ".join(blank_required)
        )
