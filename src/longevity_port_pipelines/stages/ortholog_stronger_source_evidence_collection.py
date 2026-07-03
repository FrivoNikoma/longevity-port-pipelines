from __future__ import annotations

from pathlib import Path

import polars as pl

BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"

DEFAULT_STRONGER_SOURCE_COLLECTION_PATH = Path(
    "data/input/ortholog_stronger_source_evidence_collection.csv"
)

REQUIRED_COLUMNS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "request_table",
    "request_source_row_index",
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
    "collected_source_type",
    "collected_source_name",
    "collected_source_identifier",
    "collected_source_review_status",
    "collected_evidence_summary",
    "collection_status",
    "collection_decision",
    "downstream_block_status_after_collection",
    "allowed_next_action_after_collection",
    "claim_policy_after_collection",
    "claim_status_after_collection",
    "forbidden_actions_after_collection",
    "reviewer_note",
)


def read_stronger_source_collection_rows(
    path: Path = DEFAULT_STRONGER_SOURCE_COLLECTION_PATH,
) -> pl.DataFrame:
    """Read the stronger-source evidence collection table.

    This reader is table-only. It does not fetch sequences, query external
    databases, call Biohub, generate embeddings, call Boltz/AF3/Chai, rerun
    contrast, promote downstream gates, create reviewed decisions, or make
    biological claims.
    """

    return pl.read_csv(path, infer_schema_length=0)


def pending_manual_collection_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return collection rows that are pending manual source collection."""

    return rows.filter(pl.col("collection_status") == "pending_manual_collection")


def missing_required_columns(rows: pl.DataFrame) -> list[str]:
    """Return required columns missing from the collection table."""

    return [column for column in REQUIRED_COLUMNS if column not in rows.columns]


def validate_required_columns(rows: pl.DataFrame) -> None:
    """Validate that the collection table has all required columns."""

    missing = missing_required_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog stronger-source evidence collection table is missing required columns: "
            + ", ".join(missing)
        )


ALLOWED_COLLECTED_SOURCE_TYPES = {
    "reviewed_uniprot",
    "ncbi_protein_or_gene_record",
    "ensembl_orthology",
    "oma_orthology",
    "orthodb_orthology",
    "primary_literature",
    "other_manual_source",
}

ALLOWED_COLLECTION_STATUSES = {
    "pending_manual_collection",
    "manual_collection_in_progress",
    "manual_collection_complete_still_blocked",
}

ALLOWED_COLLECTION_DECISIONS = {
    "pending",
    "evidence_recorded_for_later_intake_pr",
    "evidence_insufficient_keep_blocked",
    "evidence_conflict_or_exclude",
    "needs_additional_manual_review",
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
    """Validate conservative collection-table vocabularies."""

    checks = {
        "collected_source_type": ALLOWED_COLLECTED_SOURCE_TYPES,
        "collection_status": ALLOWED_COLLECTION_STATUSES,
        "collection_decision": ALLOWED_COLLECTION_DECISIONS,
        "downstream_block_status_after_collection": {BLOCKED_GATE4_GATE5},
        "claim_policy_after_collection": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_collection": {REPAIR_WORKLIST_CLAIM_STATUS},
    }

    for column, allowed_values in checks.items():
        invalid = invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"Ortholog stronger-source evidence collection table has invalid values "
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

    forbidden_actions = _text(row.get("forbidden_actions_after_collection", ""))
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    """Validate that every collection row forbids runtime side effects."""

    missing: list[str] = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row.get("candidate_id", "")))

    if missing:
        raise ValueError(
            "Ortholog stronger-source evidence collection table has rows missing "
            "required forbidden actions: " + ", ".join(sorted(missing))
        )


COLLECTION_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "request_table",
    "request_source_row_index",
    "requested_evidence_source_database",
    "requested_evidence_source_accession",
    "collected_source_type",
    "collected_source_identifier",
)


def find_duplicate_stronger_source_collection_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate stronger-source evidence collection keys."""

    return (
        rows.group_by(list(COLLECTION_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(COLLECTION_KEY_COLUMNS))
    )


def validate_no_duplicate_collection_keys(rows: pl.DataFrame) -> None:
    """Validate that each stronger-source collection key appears once."""

    duplicate_keys = find_duplicate_stronger_source_collection_keys(rows)
    if duplicate_keys.height:
        raise ValueError(
            "Ortholog stronger-source evidence collection table has duplicate collection keys."
        )


def validate_no_blank_required_fields(rows: pl.DataFrame) -> None:
    """Validate that required fields are present and non-blank."""

    blank_required: list[str] = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog stronger-source evidence collection table has blank required fields: "
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
            "Ortholog stronger-source evidence collection table has invalid "
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
    """Validate that collection rows do not contain downstream claim values."""

    observed_values: set[str] = set()
    for column in rows.columns:
        observed_values.update(str(value).strip() for value in rows.get_column(column).to_list())

    disallowed_observed = sorted(observed_values & DISALLOWED_CLAIM_VALUES)
    if disallowed_observed:
        raise ValueError(
            "Ortholog stronger-source evidence collection table contains disallowed "
            "claim values: " + ", ".join(disallowed_observed)
        )


def validate_stronger_source_collection_rows(rows: pl.DataFrame) -> None:
    """Validate stronger-source collection rows without downstream promotion."""

    validate_required_columns(rows)
    validate_no_duplicate_collection_keys(rows)
    validate_allowed_values(rows)
    validate_no_blank_required_fields(rows)
    validate_target_sequence_length(rows)
    validate_required_forbidden_actions(rows)
    validate_no_disallowed_claim_values(rows)
