from __future__ import annotations

from pathlib import Path

import polars as pl

DEFAULT_REPAIR_DECISIONS_PATH = Path("data/input/sirt6_candidate_negatome_repair_decisions.csv")

REQUIRED_COLUMNS = (
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "priority",
    "negatome_status",
    "negative_partner_uniprot",
    "missing_negatome_species",
    "repair_decision",
    "repair_priority",
    "claim_policy",
    "repair_note",
)

DECISION_KEY_COLUMNS = (
    "candidate_id",
    "chain",
    "source_uniprot",
    "negative_partner_uniprot",
)

ALLOWED_NEGATOME_STATUSES = {
    "missing_curated_negative_partner",
    "missing_export_ready",
    "partial_existing",
    "not_audited",
}

ALLOWED_REPAIR_DECISIONS = {
    "curate_negative_partner",
    "export_curated_negatome_rows",
    "complete_missing_negatome_species",
    "exclude_from_controlled_claim",
    "defer_until_negatome_controls",
}

ALLOWED_REPAIR_PRIORITIES = {
    "high",
    "medium",
    "low",
}

ALLOWED_CLAIM_POLICIES = {
    "negatome_repair_only",
    "allowed_for_limited_dry_run_only",
    "excluded_from_controlled_claim",
    "deferred_no_claim",
}


def read_repair_decisions(path: Path = DEFAULT_REPAIR_DECISIONS_PATH) -> pl.DataFrame:
    """Read the curated candidate NEGATOME repair decision table."""
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
    """Return duplicate candidate/source/negative-partner repair decision keys."""
    return (
        rows.group_by(list(DECISION_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(DECISION_KEY_COLUMNS))
    )


def validate_repair_decisions(rows: pl.DataFrame) -> None:
    """Validate the curated NEGATOME repair decision table.

    The table records conservative repair policy for missing or partial
    NEGATOME-style controls. It must not create controlled enrichment claims by
    itself; it only says what must be repaired, excluded, or deferred before
    controlled contrast interpretation.
    """
    missing = _missing_columns(rows)
    if missing:
        raise ValueError(
            "NEGATOME repair decision table is missing required columns: " + ", ".join(missing)
        )

    duplicate_keys = find_duplicate_decision_keys(rows)
    if duplicate_keys.height:
        raise ValueError(
            "NEGATOME repair decision table has duplicate candidate/source/partner keys."
        )

    blank_required = []
    for column in (
        "negatome_status",
        "repair_decision",
        "repair_priority",
        "claim_policy",
        "repair_note",
    ):
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "NEGATOME repair decision table has blank required decision fields: "
            + ", ".join(blank_required)
        )

    checks = {
        "negatome_status": ALLOWED_NEGATOME_STATUSES,
        "repair_decision": ALLOWED_REPAIR_DECISIONS,
        "repair_priority": ALLOWED_REPAIR_PRIORITIES,
        "claim_policy": ALLOWED_CLAIM_POLICIES,
    }
    for column, allowed_values in checks.items():
        invalid = _invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"NEGATOME repair decision table has invalid values in {column}: "
                + ", ".join(invalid)
            )
