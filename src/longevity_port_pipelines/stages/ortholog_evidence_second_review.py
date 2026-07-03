from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import polars as pl

DEFAULT_SECOND_REVIEW_QUEUE_PATH = Path("data/input/ortholog_evidence_second_review_queue.csv")

BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"
AMBIGUOUS_INTAKE_OUTCOME = "evidence_ambiguous_needs_second_reviewer"

REQUIRED_COLUMNS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
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
    "intake_outcome_before_second_review",
    "second_review_reason",
    "required_second_review_checks",
    "second_review_status",
    "second_review_decision",
    "reviewed_target_uniprot_after_second_review",
    "downstream_block_status_after_second_review",
    "allowed_next_action_after_second_review",
    "claim_policy_after_second_review",
    "claim_status_after_second_review",
    "forbidden_actions_after_second_review",
    "reviewer_note",
)

SECOND_REVIEW_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "intake_table",
    "intake_source_table",
    "intake_source_row_index",
    "evidence_source_database",
    "evidence_source_accession",
)

ALLOWED_INTAKE_OUTCOMES_BEFORE_SECOND_REVIEW = {
    AMBIGUOUS_INTAKE_OUTCOME,
}

ALLOWED_SECOND_REVIEW_STATUSES = {
    "pending_second_review",
    "second_review_in_progress",
    "second_review_complete_still_blocked",
}

ALLOWED_SECOND_REVIEW_DECISIONS = {
    "pending",
    "ready_for_later_reviewed_decision_pr",
    "needs_additional_source_evidence",
    "conflict_or_exclude",
    "keep_blocked_until_manual_review",
}

SECOND_REVIEW_DECISION_EXPECTED_VALUES = {
    "pending": {
        "downstream_block_status_after_second_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_second_review": "perform_second_reviewer_evidence_intake_review",
        "claim_status_after_second_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "ready_for_later_reviewed_decision_pr": {
        "downstream_block_status_after_second_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_second_review": "prepare_later_reviewed_decision_pr",
        "claim_status_after_second_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "needs_additional_source_evidence": {
        "downstream_block_status_after_second_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_second_review": "defer_until_stronger_source_evidence_exists",
        "claim_status_after_second_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "conflict_or_exclude": {
        "downstream_block_status_after_second_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_second_review": "prepare_later_rejection_or_exclusion_review",
        "claim_status_after_second_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "keep_blocked_until_manual_review": {
        "downstream_block_status_after_second_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_second_review": "perform_second_reviewer_evidence_intake_review",
        "claim_status_after_second_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
}

RUNTIME_SIDE_EFFECTS = frozenset(
    {
        "ortholog acceptance",
        "reviewed decision creation",
        "Gate 4 or Gate 5 policy update",
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
    "accepted_for_planning_after_review",
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


def read_second_review_rows(
    path: Path = DEFAULT_SECOND_REVIEW_QUEUE_PATH,
) -> pl.DataFrame:
    """Read the ortholog evidence second-review queue.

    This reader is table-only. It does not fetch sequences, query accession
    databases, call Biohub, generate embeddings, call Boltz/AF3/Chai, rerun
    contrast, promote downstream gates, create reviewed decisions, or make
    biological claims.
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


def find_duplicate_second_review_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate ortholog evidence second-review keys."""

    return (
        rows.group_by(list(SECOND_REVIEW_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(SECOND_REVIEW_KEY_COLUMNS))
    )


def pending_second_review_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return second-review rows that are still pending."""

    return rows.filter(pl.col("second_review_status") == "pending_second_review")


def completed_still_blocked_second_review_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return completed second-review rows that remain blocked."""

    return rows.filter(pl.col("second_review_status") == "second_review_complete_still_blocked")


def ready_for_later_reviewed_decision_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return rows that may support a later reviewed-decision PR."""

    return rows.filter(pl.col("second_review_decision") == "ready_for_later_reviewed_decision_pr")


def forbidden_actions_present(row: Mapping[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row, "forbidden_actions_after_second_review")
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def _validate_target_sequence_length(rows: pl.DataFrame) -> None:
    bad_values: list[str] = []
    for value in rows.get_column("target_sequence_length").to_list():
        text = str(value).strip()
        if text == "unresolved":
            continue
        if not text.isdigit() or int(text) <= 0:
            bad_values.append(text)

    if bad_values:
        raise ValueError(
            "Ortholog evidence second-review queue has invalid target_sequence_length values: "
            + ", ".join(sorted(set(bad_values)))
        )


def _validate_decision_rules(rows: pl.DataFrame) -> None:
    mismatches: list[str] = []
    for row in rows.iter_rows(named=True):
        decision = _text(row, "second_review_decision")
        expected_values = SECOND_REVIEW_DECISION_EXPECTED_VALUES[decision]
        for column, expected_value in expected_values.items():
            if _text(row, column) != expected_value:
                mismatches.append(f"{_text(row, 'candidate_id')}:{column}")

    if mismatches:
        raise ValueError(
            "Ortholog evidence second-review queue has decision-rule mismatches: "
            + ", ".join(sorted(mismatches))
        )


def _validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    missing: list[str] = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row, "candidate_id"))

    if missing:
        raise ValueError(
            "Ortholog evidence second-review queue has rows missing required forbidden actions: "
            + ", ".join(sorted(missing))
        )


def _validate_no_disallowed_claim_values(rows: pl.DataFrame) -> None:
    observed_values: set[str] = set()
    for column in rows.columns:
        observed_values.update(str(value).strip() for value in rows.get_column(column).to_list())

    disallowed_observed = sorted(observed_values & DISALLOWED_CLAIM_VALUES)
    if disallowed_observed:
        raise ValueError(
            "Ortholog evidence second-review queue contains disallowed claim values: "
            + ", ".join(disallowed_observed)
        )


def validate_second_review_rows(rows: pl.DataFrame) -> None:
    """Validate second-review rows without creating downstream permission."""

    missing = _missing_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog evidence second-review queue is missing required columns: "
            + ", ".join(missing)
        )

    duplicate_keys = find_duplicate_second_review_keys(rows)
    if duplicate_keys.height:
        raise ValueError("Ortholog evidence second-review queue has duplicate review keys.")

    checks = {
        "intake_outcome_before_second_review": ALLOWED_INTAKE_OUTCOMES_BEFORE_SECOND_REVIEW,
        "second_review_status": ALLOWED_SECOND_REVIEW_STATUSES,
        "second_review_decision": ALLOWED_SECOND_REVIEW_DECISIONS,
        "reviewed_target_uniprot_after_second_review": {"unresolved"},
        "downstream_block_status_after_second_review": {BLOCKED_GATE4_GATE5},
        "claim_policy_after_second_review": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_second_review": {REPAIR_WORKLIST_CLAIM_STATUS},
    }
    for column, allowed_values in checks.items():
        invalid = _invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"Ortholog evidence second-review queue has invalid values in {column}: "
                + ", ".join(invalid)
            )

    blank_required: list[str] = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog evidence second-review queue has blank required fields: "
            + ", ".join(blank_required)
        )

    _validate_target_sequence_length(rows)
    _validate_decision_rules(rows)
    _validate_required_forbidden_actions(rows)
    _validate_no_disallowed_claim_values(rows)
