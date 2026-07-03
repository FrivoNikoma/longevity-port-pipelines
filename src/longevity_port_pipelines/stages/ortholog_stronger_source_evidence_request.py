from __future__ import annotations

from pathlib import Path

import polars as pl

BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"

DEFAULT_STRONGER_SOURCE_REQUEST_PATH = Path(
    "data/input/ortholog_stronger_source_evidence_requests.csv"
)

REQUIRED_COLUMNS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "second_review_table",
    "second_review_source_row_index",
    "gene_symbol",
    "source_species",
    "target_species",
    "target_species_taxid",
    "source_uniprot",
    "partner_uniprot",
    "evidence_source_database",
    "evidence_source_accession",
    "target_taxid",
    "target_species_name",
    "target_gene_symbol",
    "target_protein_accession",
    "target_sequence_length",
    "second_review_status_before_request",
    "second_review_decision_before_request",
    "reviewed_target_uniprot_before_request",
    "request_reason",
    "requested_source_types",
    "requested_source_examples",
    "request_status",
    "request_decision",
    "downstream_block_status_after_request",
    "allowed_next_action_after_request",
    "claim_policy_after_request",
    "claim_status_after_request",
    "forbidden_actions_after_request",
    "reviewer_note",
)


def read_stronger_source_request_rows(
    path: Path = DEFAULT_STRONGER_SOURCE_REQUEST_PATH,
) -> pl.DataFrame:
    """Read the stronger-source evidence request table.

    This reader is table-only. It does not fetch sequences, query external
    databases, call Biohub, generate embeddings, call Boltz/AF3/Chai, rerun
    contrast, promote downstream gates, create reviewed decisions, or make
    biological claims.
    """

    return pl.read_csv(path, infer_schema_length=0)


def pending_source_collection_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return request rows that are pending manual source collection."""

    return rows.filter(pl.col("request_status") == "pending_source_collection")


def missing_required_columns(rows: pl.DataFrame) -> list[str]:
    """Return required columns missing from the request table."""

    return [column for column in REQUIRED_COLUMNS if column not in rows.columns]


def validate_required_columns(rows: pl.DataFrame) -> None:
    """Validate that the request table has all required columns."""

    missing = missing_required_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog stronger-source evidence request table is missing required columns: "
            + ", ".join(missing)
        )


ALLOWED_SECOND_REVIEW_STATUSES_BEFORE_REQUEST = {
    "second_review_complete_still_blocked",
}

ALLOWED_SECOND_REVIEW_DECISIONS_BEFORE_REQUEST = {
    "needs_additional_source_evidence",
}

ALLOWED_REQUEST_STATUSES = {
    "pending_source_collection",
    "source_collection_in_progress",
    "source_collection_complete_still_blocked",
}

ALLOWED_REQUEST_DECISIONS = {
    "pending",
    "needs_manual_source_collection",
    "ready_for_later_evidence_intake_pr",
    "conflict_or_exclude",
    "keep_blocked_until_manual_review",
}


def invalid_values(
    rows: pl.DataFrame,
    *,
    column: str,
    allowed_values: set[str],
) -> list[str]:
    """Return values outside the allowed vocabulary for one column."""

    return sorted(
        str(value).strip()
        for value in rows.get_column(column).unique().to_list()
        if str(value).strip() not in allowed_values
    )


def validate_allowed_values(rows: pl.DataFrame) -> None:
    """Validate conservative request-table vocabularies."""

    checks = {
        "second_review_status_before_request": ALLOWED_SECOND_REVIEW_STATUSES_BEFORE_REQUEST,
        "second_review_decision_before_request": ALLOWED_SECOND_REVIEW_DECISIONS_BEFORE_REQUEST,
        "reviewed_target_uniprot_before_request": {"unresolved"},
        "request_status": ALLOWED_REQUEST_STATUSES,
        "request_decision": ALLOWED_REQUEST_DECISIONS,
        "downstream_block_status_after_request": {BLOCKED_GATE4_GATE5},
        "claim_policy_after_request": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_request": {REPAIR_WORKLIST_CLAIM_STATUS},
    }

    for column, allowed_values in checks.items():
        invalid = invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"Ortholog stronger-source evidence request table has invalid values "
                f"in {column}: " + ", ".join(invalid)
            )


RUNTIME_SIDE_EFFECTS = frozenset(
    {
        "ortholog acceptance",
        "reviewed decision creation",
        "Gate 4 or Gate 5 policy update",
        "sequence fetch",
        "external database query",
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


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def forbidden_actions_present(row: dict[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row.get("forbidden_actions_after_request", ""))
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    """Validate that every request row forbids runtime side effects."""

    missing: list[str] = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row.get("candidate_id", "")))

    if missing:
        raise ValueError(
            "Ortholog stronger-source evidence request table has rows missing "
            "required forbidden actions: " + ", ".join(sorted(missing))
        )


REQUEST_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "second_review_table",
    "second_review_source_row_index",
    "evidence_source_database",
    "evidence_source_accession",
)


def find_duplicate_stronger_source_request_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate stronger-source evidence request keys."""

    return (
        rows.group_by(list(REQUEST_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(REQUEST_KEY_COLUMNS))
    )


def validate_no_duplicate_request_keys(rows: pl.DataFrame) -> None:
    """Validate that each stronger-source request key appears once."""

    duplicate_keys = find_duplicate_stronger_source_request_keys(rows)
    if duplicate_keys.height:
        raise ValueError(
            "Ortholog stronger-source evidence request table has duplicate request keys."
        )


def validate_no_blank_required_fields(rows: pl.DataFrame) -> None:
    """Validate that required fields are present and non-blank."""

    blank_required: list[str] = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog stronger-source evidence request table has blank required fields: "
            + ", ".join(blank_required)
        )


def validate_target_sequence_length(rows: pl.DataFrame) -> None:
    """Validate target sequence length values without fetching sequences."""

    bad_values: list[str] = []
    for value in rows.get_column("target_sequence_length").to_list():
        text = str(value).strip()
        if text == "unresolved":
            continue
        if not text.isdigit() or int(text) <= 0:
            bad_values.append(text)

    if bad_values:
        raise ValueError(
            "Ortholog stronger-source evidence request table has invalid "
            "target_sequence_length values: " + ", ".join(sorted(set(bad_values)))
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


def validate_no_disallowed_claim_values(rows: pl.DataFrame) -> None:
    """Validate that request rows do not contain downstream claim values."""

    observed_values: set[str] = set()
    for column in rows.columns:
        observed_values.update(str(value).strip() for value in rows.get_column(column).to_list())

    disallowed_observed = sorted(observed_values & DISALLOWED_CLAIM_VALUES)
    if disallowed_observed:
        raise ValueError(
            "Ortholog stronger-source evidence request table contains disallowed "
            "claim values: " + ", ".join(disallowed_observed)
        )


def validate_stronger_source_request_rows(rows: pl.DataFrame) -> None:
    """Validate stronger-source request rows without downstream promotion."""

    validate_required_columns(rows)
    validate_no_duplicate_request_keys(rows)
    validate_allowed_values(rows)
    validate_no_blank_required_fields(rows)
    validate_target_sequence_length(rows)
    validate_required_forbidden_actions(rows)
    validate_no_disallowed_claim_values(rows)
