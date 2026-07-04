from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import polars as pl

DEFAULT_REVIEW_DECISIONS_PATH = Path("data/input/ortholog_evidence_review_decisions.csv")

REVIEWED_FOR_PLANNING_STILL_POLICY_BLOCKED = "reviewed_for_planning_still_policy_blocked"
BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"

REQUIRED_COLUMNS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "review_source_table",
    "review_source_row_index",
    "intake_table",
    "intake_source_table",
    "intake_source_row_index",
    "gene_symbol",
    "source_species",
    "target_species",
    "target_species_taxid",
    "source_uniprot",
    "partner_uniprot",
    "evidence_source_type",
    "evidence_source_database",
    "evidence_source_accession",
    "target_taxid",
    "target_species_name",
    "target_gene_symbol",
    "target_protein_accession",
    "target_sequence_length",
    "review_source_status_before_review",
    "review_source_decision_before_review",
    "review_decision",
    "reviewed_target_uniprot",
    "reviewed_source_database",
    "reviewed_source_accession",
    "reviewed_sequence_length",
    "reviewed_taxid",
    "review_evidence_uri_or_note",
    "reviewer_note",
    "downstream_block_status_after_review",
    "allowed_next_action_after_review",
    "claim_policy_after_review",
    "claim_status_after_review",
    "forbidden_actions_after_review",
)

REVIEW_DECISION_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "review_source_table",
    "review_source_row_index",
    "evidence_source_database",
    "evidence_source_accession",
)

ALLOWED_REVIEW_SOURCE_STATUSES_BEFORE_REVIEW = {
    "evidence_ready_for_review_decision",
    "second_review_complete_still_blocked",
}

ALLOWED_REVIEW_SOURCE_DECISIONS_BEFORE_REVIEW = {
    "evidence_ready_for_review_decision",
    "ready_for_later_reviewed_decision_pr",
}

ALLOWED_REVIEW_DECISIONS = {
    "accepted_for_planning_after_review",
    "rejected_after_review",
    "needs_additional_source_evidence",
    "conflict_or_exclude",
    "keep_blocked_until_manual_review",
}

ALLOWED_DOWNSTREAM_BLOCK_STATUSES_AFTER_REVIEW = {
    REVIEWED_FOR_PLANNING_STILL_POLICY_BLOCKED,
    BLOCKED_GATE4_GATE5,
}

REVIEW_DECISION_EXPECTED_VALUES = {
    "accepted_for_planning_after_review": {
        "downstream_block_status_after_review": REVIEWED_FOR_PLANNING_STILL_POLICY_BLOCKED,
        "allowed_next_action_after_review": ("consider_later_explicit_gate4_gate5_policy_update"),
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "rejected_after_review": {
        "downstream_block_status_after_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_review": "keep_row_excluded_from_downstream_planning",
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "needs_additional_source_evidence": {
        "downstream_block_status_after_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_review": "defer_until_stronger_source_evidence_exists",
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "conflict_or_exclude": {
        "downstream_block_status_after_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_review": "prepare_later_rejection_or_exclusion_review",
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "keep_blocked_until_manual_review": {
        "downstream_block_status_after_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_review": "perform_manual_ortholog_evidence_review",
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
}

RUNTIME_SIDE_EFFECTS = frozenset(
    {
        "automatic Gate 4 or Gate 5 policy update",
        "sequence fetch",
        "Biohub call",
        "embedding generation",
        "Boltz call",
        "AF3 call",
        "Chai call",
        "enrichment rerun",
        "contrast rerun",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "biological claim",
    }
)

DISALLOWED_CLAIM_VALUES = {
    "accepted_ortholog",
    "validated_ortholog",
    "validated_biological_signal",
    "validated_longevity_signal",
    "validated_biological_hit",
    "confirmed_binding_change",
    "confirmed_functional_effect",
    "Gate 8 eligible",
    "Gate 9 eligible",
    "embedding ready",
    "Biohub ready",
    "Boltz ready",
    "AF3 ready",
    "Chai ready",
    "safe_to_port",
    "safe to port",
    "proven_pro_longevity_variant",
}


def read_review_decision_rows(
    path: Path = DEFAULT_REVIEW_DECISIONS_PATH,
) -> pl.DataFrame:
    """Read ortholog evidence reviewed-decision rows.

    This reader is table-only. It does not fetch sequences, query databases, call
    Biohub, generate embeddings, call Boltz/AF3/Chai, rerun contrast, promote
    downstream gates, update Gate 4 / Gate 5 policy, or make biological claims.
    """

    return pl.read_csv(path, infer_schema_length=0)


def _text(row: Mapping[str, object], key: str) -> str:
    value = row.get(key, "")
    if value is None:
        return ""
    return str(value).strip()


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
        str(value).strip()
        for value in rows.get_column(column).unique().to_list()
        if str(value).strip() not in allowed_values
    )


def find_duplicate_review_decision_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate ortholog evidence reviewed-decision keys."""

    return (
        rows.group_by(list(REVIEW_DECISION_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(REVIEW_DECISION_KEY_COLUMNS))
    )


def reviewed_for_planning_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return reviewed-for-planning rows that remain policy-blocked."""

    return rows.filter(
        pl.col("downstream_block_status_after_review") == REVIEWED_FOR_PLANNING_STILL_POLICY_BLOCKED
    )


def blocked_review_decision_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return reviewed-decision rows that remain Gate 4 / Gate 5 blocked."""

    return rows.filter(pl.col("downstream_block_status_after_review") == BLOCKED_GATE4_GATE5)


def forbidden_actions_present(row: Mapping[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row, "forbidden_actions_after_review")
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def _validate_target_sequence_lengths(rows: pl.DataFrame) -> None:
    bad_values: list[str] = []
    for column in ("target_sequence_length", "reviewed_sequence_length"):
        for value in rows.get_column(column).to_list():
            text = str(value).strip()
            if text == "unresolved":
                continue
            if not text.isdigit() or int(text) <= 0:
                bad_values.append(f"{column}={text}")

    if bad_values:
        raise ValueError(
            "Ortholog evidence reviewed-decision table has invalid sequence lengths: "
            + ", ".join(sorted(set(bad_values)))
        )


def _validate_review_decision_rules(rows: pl.DataFrame) -> None:
    mismatches: list[str] = []
    for row in rows.iter_rows(named=True):
        decision = _text(row, "review_decision")
        expected_values = REVIEW_DECISION_EXPECTED_VALUES[decision]
        for column, expected_value in expected_values.items():
            if _text(row, column) != expected_value:
                mismatches.append(f"{_text(row, 'candidate_id')}:{column}")

    if mismatches:
        raise ValueError(
            "Ortholog evidence reviewed-decision table has decision-rule mismatches: "
            + ", ".join(sorted(mismatches))
        )


def _validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    missing: list[str] = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row, "candidate_id"))

    if missing:
        raise ValueError(
            "Ortholog evidence reviewed-decision table has rows missing required "
            "forbidden actions: " + ", ".join(sorted(missing))
        )


def _validate_no_disallowed_claim_values(rows: pl.DataFrame) -> None:
    observed_values: set[str] = set()
    for column in rows.columns:
        observed_values.update(str(value).strip() for value in rows.get_column(column).to_list())

    disallowed_observed = sorted(observed_values & DISALLOWED_CLAIM_VALUES)
    if disallowed_observed:
        raise ValueError(
            "Ortholog evidence reviewed-decision table contains disallowed claim values: "
            + ", ".join(disallowed_observed)
        )


def validate_review_decision_rows(rows: pl.DataFrame) -> None:
    """Validate reviewed-decision rows without creating downstream permission."""

    missing = _missing_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog evidence reviewed-decision table is missing required columns: "
            + ", ".join(missing)
        )

    duplicate_keys = find_duplicate_review_decision_keys(rows)
    if duplicate_keys.height:
        raise ValueError("Ortholog evidence reviewed-decision table has duplicate keys.")

    checks = {
        "review_source_status_before_review": (ALLOWED_REVIEW_SOURCE_STATUSES_BEFORE_REVIEW),
        "review_source_decision_before_review": (ALLOWED_REVIEW_SOURCE_DECISIONS_BEFORE_REVIEW),
        "review_decision": ALLOWED_REVIEW_DECISIONS,
        "downstream_block_status_after_review": (ALLOWED_DOWNSTREAM_BLOCK_STATUSES_AFTER_REVIEW),
        "claim_policy_after_review": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_review": {REPAIR_WORKLIST_CLAIM_STATUS},
    }
    for column, allowed_values in checks.items():
        invalid = _invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                "Ortholog evidence reviewed-decision table has invalid values in "
                f"{column}: " + ", ".join(invalid)
            )

    blank_required: list[str] = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog evidence reviewed-decision table has blank required fields: "
            + ", ".join(blank_required)
        )

    _validate_target_sequence_lengths(rows)
    _validate_review_decision_rules(rows)
    _validate_required_forbidden_actions(rows)
    _validate_no_disallowed_claim_values(rows)
