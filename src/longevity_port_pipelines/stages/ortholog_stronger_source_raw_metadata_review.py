from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import polars as pl

DEFAULT_RAW_METADATA_REVIEW_PATH = Path(
    "data/input/ortholog_stronger_source_raw_metadata_reviews.csv"
)

BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"
BIOLOGICAL_CLAIM_STATUS_NONE = "no_biological_claim"

REQUIRED_RAW_METADATA_RESPONSE_TRACE_COLUMNS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "raw_metadata_response_table",
    "raw_metadata_response_source_row_index",
    "gene_symbol",
    "source_species",
    "target_species",
    "target_species_taxid",
    "source_uniprot",
    "partner_uniprot",
    "requested_evidence_source_database",
    "requested_evidence_source_accession",
    "target_taxid",
    "target_species_name",
    "target_gene_symbol",
    "target_protein_accession",
    "target_sequence_length",
    "planned_lookup_source_type",
    "planned_lookup_query_identifier",
    "raw_metadata_source_type",
    "raw_metadata_source_name",
    "raw_metadata_source_identifier",
    "raw_metadata_status_before_review",
    "raw_metadata_response_status_before_review",
    "raw_metadata_review_status_before_review",
)

REQUIRED_REVIEW_COLUMNS = (
    "raw_metadata_human_review_status",
    "raw_metadata_human_review_decision",
    "reviewed_metadata_source_type",
    "reviewed_metadata_source_name",
    "reviewed_metadata_source_identifier",
    "reviewed_accession",
    "reviewed_entry_name",
    "reviewed_reviewed_status",
    "reviewed_gene_symbol",
    "reviewed_organism_name",
    "reviewed_taxid",
    "reviewed_sequence_length",
    "sequence_review_scope",
    "sequence_fetched",
    "source_evidence_created",
    "source_evidence_creation_status",
    "reviewed_decision_created",
    "reviewed_decision_creation_status",
    "gate4_gate5_policy_updated",
    "gate8_promoted",
    "gate9_promoted",
    "downstream_block_status_after_review",
    "allowed_next_action_after_review",
    "claim_policy_after_review",
    "claim_status_after_review",
    "biological_claim_status",
    "forbidden_actions_after_review",
    "reviewer_note",
)

REQUIRED_COLUMNS = (
    *REQUIRED_RAW_METADATA_RESPONSE_TRACE_COLUMNS,
    *REQUIRED_REVIEW_COLUMNS,
)

RAW_METADATA_REVIEW_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "raw_metadata_response_table",
    "raw_metadata_response_source_row_index",
    "raw_metadata_source_type",
    "raw_metadata_source_identifier",
)

FALSE_ONLY_COLUMNS = (
    "sequence_fetched",
    "source_evidence_created",
    "reviewed_decision_created",
    "gate4_gate5_policy_updated",
    "gate8_promoted",
    "gate9_promoted",
)

ALLOWED_RAW_METADATA_SOURCE_TYPES = {
    "uniprot_entry_metadata",
    "reviewed_uniprot",
    "ncbi_protein_or_gene_record",
    "ensembl_orthology",
    "oma_orthology",
    "orthodb_orthology",
    "primary_literature",
    "other_manual_source",
    "injected_fake_or_noop_provider",
}

ALLOWED_RAW_METADATA_STATUSES_BEFORE_REVIEW = {
    "raw_metadata_dry_run_noop_unreviewed",
    "raw_metadata_received_unreviewed",
    "raw_metadata_fake_provider_unreviewed",
    "not_requested_policy_denied",
}

ALLOWED_RAW_METADATA_RESPONSE_STATUSES_BEFORE_REVIEW = {
    "raw_metadata_received_unreviewed_still_blocked",
    "raw_metadata_not_requested_policy_denied",
    "raw_metadata_deferred_keep_blocked",
    "raw_metadata_conflict_keep_blocked",
}

ALLOWED_RAW_METADATA_REVIEW_STATUSES_BEFORE_REVIEW = {
    "unreviewed_raw_metadata",
    "raw_metadata_requires_manual_review",
}

ALLOWED_HUMAN_REVIEW_STATUSES = {
    "pending_raw_metadata_human_review",
    "raw_metadata_human_review_complete_still_blocked",
}

ALLOWED_HUMAN_REVIEW_DECISIONS = {
    "pending",
    "metadata_consistent_prepare_source_evidence_intake_later",
    "metadata_conflict_keep_blocked",
    "metadata_insufficient_keep_blocked",
}

ALLOWED_REVIEWED_METADATA_SOURCE_TYPES = {
    "unresolved",
    *ALLOWED_RAW_METADATA_SOURCE_TYPES,
}

ALLOWED_REVIEWED_STATUSES = {
    "unresolved",
    "reviewed",
    "unreviewed",
    "unknown",
}

ALLOWED_SEQUENCE_REVIEW_SCOPES = {
    "not_reviewed_pending",
    "metadata_only_no_sequence_reviewed",
    "no_sequence_requested_or_reviewed",
}

RAW_METADATA_REVIEW_DECISION_EXPECTED_VALUES = {
    "pending": {
        "raw_metadata_human_review_status": "pending_raw_metadata_human_review",
        "downstream_block_status_after_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_review": "perform_raw_metadata_human_review",
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "metadata_consistent_prepare_source_evidence_intake_later": {
        "raw_metadata_human_review_status": "raw_metadata_human_review_complete_still_blocked",
        "downstream_block_status_after_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_review": "prepare_later_source_evidence_intake_pr",
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "metadata_conflict_keep_blocked": {
        "raw_metadata_human_review_status": "raw_metadata_human_review_complete_still_blocked",
        "downstream_block_status_after_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_review": "resolve_metadata_conflict_before_source_evidence",
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "metadata_insufficient_keep_blocked": {
        "raw_metadata_human_review_status": "raw_metadata_human_review_complete_still_blocked",
        "downstream_block_status_after_review": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_review": "keep_blocked_until_additional_metadata",
        "claim_status_after_review": REPAIR_WORKLIST_CLAIM_STATUS,
    },
}

RUNTIME_SIDE_EFFECTS = frozenset(
    {
        "source evidence creation",
        "reviewed ortholog decision creation",
        "ortholog acceptance",
        "ortholog validation",
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


def read_raw_metadata_review_rows(
    path: Path = DEFAULT_RAW_METADATA_REVIEW_PATH,
) -> pl.DataFrame:
    """Read raw metadata human-review rows.

    This reader is table-only. It does not fetch sequences, call external
    databases, create source evidence, create reviewed ortholog decisions,
    update Gate 4 / Gate 5 policy, promote downstream gates, call Biohub,
    generate embeddings, call Boltz/AF3/Chai, rerun contrast, or make
    biological claims.
    """

    return pl.read_csv(path, infer_schema_length=0)


def _text(row: Mapping[str, object], key: str) -> str:
    value = row.get(key, "")
    if value is None:
        return ""
    return str(value).strip()


def missing_required_columns(rows: pl.DataFrame) -> list[str]:
    """Return required columns missing from the raw metadata review table."""

    return [column for column in REQUIRED_COLUMNS if column not in rows.columns]


def find_duplicate_raw_metadata_review_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate raw metadata review keys."""

    return (
        rows.group_by(list(RAW_METADATA_REVIEW_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(RAW_METADATA_REVIEW_KEY_COLUMNS))
    )


def pending_raw_metadata_review_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return raw metadata rows still pending human review."""

    return rows.filter(
        pl.col("raw_metadata_human_review_status") == "pending_raw_metadata_human_review"
    )


def completed_still_blocked_raw_metadata_review_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return completed raw metadata reviews that remain blocked."""

    return rows.filter(
        pl.col("raw_metadata_human_review_status")
        == "raw_metadata_human_review_complete_still_blocked"
    )


def forbidden_actions_present(row: Mapping[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row, "forbidden_actions_after_review")
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


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


def _validate_target_sequence_length_column(rows: pl.DataFrame, column: str) -> None:
    bad_values: list[str] = []
    for value in rows.get_column(column).to_list():
        text = str(value).strip()
        if text == "unresolved":
            continue
        if not text.isdigit() or int(text) <= 0:
            bad_values.append(text)

    if bad_values:
        raise ValueError(
            f"Ortholog stronger-source raw metadata review table has invalid {column} values: "
            + ", ".join(sorted(set(bad_values)))
        )


def _validate_false_only_columns(rows: pl.DataFrame) -> None:
    invalid_columns: list[str] = []
    for column in FALSE_ONLY_COLUMNS:
        invalid = _invalid_values(rows, column=column, allowed_values={"false"})
        if invalid:
            invalid_columns.append(f"{column}: " + ", ".join(invalid))

    if invalid_columns:
        raise ValueError(
            "Ortholog stronger-source raw metadata review table has side-effect "
            "flags that must remain false: " + "; ".join(invalid_columns)
        )


def _validate_decision_rules(rows: pl.DataFrame) -> None:
    mismatches: list[str] = []
    for row in rows.iter_rows(named=True):
        decision = _text(row, "raw_metadata_human_review_decision")
        expected_values = RAW_METADATA_REVIEW_DECISION_EXPECTED_VALUES[decision]
        for column, expected_value in expected_values.items():
            if _text(row, column) != expected_value:
                mismatches.append(f"{_text(row, 'candidate_id')}:{column}")

    if mismatches:
        raise ValueError(
            "Ortholog stronger-source raw metadata review table has decision-rule "
            "mismatches: " + ", ".join(sorted(mismatches))
        )


def _validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    missing: list[str] = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row, "candidate_id"))

    if missing:
        raise ValueError(
            "Ortholog stronger-source raw metadata review table has rows missing "
            "required forbidden actions: " + ", ".join(sorted(missing))
        )


def _validate_no_disallowed_claim_values(rows: pl.DataFrame) -> None:
    observed_values: set[str] = set()
    for column in rows.columns:
        observed_values.update(str(value).strip() for value in rows.get_column(column).to_list())

    disallowed_observed = sorted(observed_values & DISALLOWED_CLAIM_VALUES)
    if disallowed_observed:
        raise ValueError(
            "Ortholog stronger-source raw metadata review table contains disallowed "
            "claim values: " + ", ".join(disallowed_observed)
        )


def validate_raw_metadata_review_rows(rows: pl.DataFrame) -> None:
    """Validate raw metadata human-review rows without downstream permission."""

    missing = missing_required_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog stronger-source raw metadata review table is missing required "
            "columns: " + ", ".join(missing)
        )

    duplicate_keys = find_duplicate_raw_metadata_review_keys(rows)
    if duplicate_keys.height:
        raise ValueError(
            "Ortholog stronger-source raw metadata review table has duplicate review keys."
        )

    checks = {
        "raw_metadata_source_type": ALLOWED_RAW_METADATA_SOURCE_TYPES,
        "raw_metadata_status_before_review": ALLOWED_RAW_METADATA_STATUSES_BEFORE_REVIEW,
        "raw_metadata_response_status_before_review": (
            ALLOWED_RAW_METADATA_RESPONSE_STATUSES_BEFORE_REVIEW
        ),
        "raw_metadata_review_status_before_review": (
            ALLOWED_RAW_METADATA_REVIEW_STATUSES_BEFORE_REVIEW
        ),
        "raw_metadata_human_review_status": ALLOWED_HUMAN_REVIEW_STATUSES,
        "raw_metadata_human_review_decision": ALLOWED_HUMAN_REVIEW_DECISIONS,
        "reviewed_metadata_source_type": ALLOWED_REVIEWED_METADATA_SOURCE_TYPES,
        "reviewed_reviewed_status": ALLOWED_REVIEWED_STATUSES,
        "sequence_review_scope": ALLOWED_SEQUENCE_REVIEW_SCOPES,
        "downstream_block_status_after_review": {BLOCKED_GATE4_GATE5},
        "claim_policy_after_review": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_review": {REPAIR_WORKLIST_CLAIM_STATUS},
        "biological_claim_status": {BIOLOGICAL_CLAIM_STATUS_NONE},
    }
    for column, allowed_values in checks.items():
        invalid = _invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"Ortholog stronger-source raw metadata review table has invalid values in "
                f"{column}: " + ", ".join(invalid)
            )

    blank_required: list[str] = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog stronger-source raw metadata review table has blank required "
            "fields: " + ", ".join(blank_required)
        )

    _validate_target_sequence_length_column(rows, "target_sequence_length")
    _validate_target_sequence_length_column(rows, "reviewed_sequence_length")
    _validate_false_only_columns(rows)
    _validate_decision_rules(rows)
    _validate_required_forbidden_actions(rows)
    _validate_no_disallowed_claim_values(rows)
