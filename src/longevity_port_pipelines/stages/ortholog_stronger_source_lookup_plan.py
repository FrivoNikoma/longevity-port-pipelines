from __future__ import annotations

from pathlib import Path

import polars as pl

BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"
DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET = "data/input/ortholog_stronger_source_raw_metadata_responses.csv"

DEFAULT_STRONGER_SOURCE_LOOKUP_PLAN_PATH = Path(
    "data/input/ortholog_stronger_source_lookup_plan.csv"
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
    "planned_lookup_source_type",
    "planned_lookup_source_name",
    "planned_lookup_query_identifier",
    "planned_lookup_query_taxid",
    "planned_lookup_mode",
    "live_lookup_allowed",
    "sequence_fetch_allowed",
    "planned_output_target",
    "lookup_plan_status",
    "downstream_block_status_after_lookup_plan",
    "allowed_next_action_after_lookup_plan",
    "claim_policy_after_lookup_plan",
    "claim_status_after_lookup_plan",
    "forbidden_actions_after_lookup_plan",
    "reviewer_note",
)


def read_stronger_source_lookup_plan_rows(
    path: Path = DEFAULT_STRONGER_SOURCE_LOOKUP_PLAN_PATH,
) -> pl.DataFrame:
    """Read the stronger-source lookup plan table.

    This reader is table-only. It does not query external databases, fetch
    sequences, call Biohub, generate embeddings, call Boltz/AF3/Chai, rerun
    contrast, collect source evidence, promote downstream gates, create reviewed
    decisions, or make biological claims.
    """

    return pl.read_csv(path, infer_schema_length=0)


def planned_lookup_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return rows that plan a still-blocked stronger-source lookup."""

    return rows.filter(pl.col("lookup_plan_status") == "lookup_planned_still_blocked")


def missing_required_columns(rows: pl.DataFrame) -> list[str]:
    """Return required columns missing from the lookup plan table."""

    return [column for column in REQUIRED_COLUMNS if column not in rows.columns]


def validate_required_columns(rows: pl.DataFrame) -> None:
    """Validate that the lookup plan table has all required columns."""

    missing = missing_required_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog stronger-source lookup plan table is missing required columns: "
            + ", ".join(missing)
        )


ALLOWED_PLANNED_LOOKUP_SOURCE_TYPES = {
    "uniprot_entry_metadata",
    "reviewed_uniprot",
    "ncbi_protein_or_gene_record",
    "ensembl_orthology",
    "oma_orthology",
    "orthodb_orthology",
    "primary_literature",
    "other_manual_source",
}

ALLOWED_PLANNED_LOOKUP_MODES = {
    "dry_run_plan_only",
    "fixture_backed_only",
    "explicit_live_opt_in_required",
}

ALLOWED_LOOKUP_PLAN_STATUSES = {
    "lookup_planned_still_blocked",
    "lookup_deferred_keep_blocked",
    "lookup_not_planned_keep_blocked",
}

ALLOWED_NEXT_ACTIONS_AFTER_LOOKUP_PLAN = {
    "add_lookup_plan_table_row",
    "add_lookup_plan_validator",
    "add_fixture_backed_lookup_client",
    "add_raw_metadata_response_sandbox_row_later",
    "add_manual_source_evidence_row_later",
    "keep_blocked",
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
    """Validate conservative lookup-plan vocabularies."""

    checks = {
        "planned_lookup_source_type": ALLOWED_PLANNED_LOOKUP_SOURCE_TYPES,
        "planned_lookup_mode": ALLOWED_PLANNED_LOOKUP_MODES,
        "live_lookup_allowed": {"false"},
        "sequence_fetch_allowed": {"false"},
        "planned_output_target": {DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET},
        "lookup_plan_status": ALLOWED_LOOKUP_PLAN_STATUSES,
        "downstream_block_status_after_lookup_plan": {BLOCKED_GATE4_GATE5},
        "allowed_next_action_after_lookup_plan": ALLOWED_NEXT_ACTIONS_AFTER_LOOKUP_PLAN,
        "claim_policy_after_lookup_plan": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_lookup_plan": {REPAIR_WORKLIST_CLAIM_STATUS},
    }

    for column, allowed_values in checks.items():
        invalid = invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"Ortholog stronger-source lookup plan table has invalid values "
                f"in {column}: " + ", ".join(invalid)
            )


RUNTIME_SIDE_EFFECTS = frozenset(
    {
        "live external database lookup",
        "source evidence collection",
        "ortholog acceptance",
        "curated ortholog candidate creation",
        "standard ortholog coverage population",
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


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def forbidden_actions_present(row: dict[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row.get("forbidden_actions_after_lookup_plan", ""))
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    """Validate that every lookup plan row forbids runtime side effects."""

    missing: list[str] = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row.get("candidate_id", "")))

    if missing:
        raise ValueError(
            "Ortholog stronger-source lookup plan table has rows missing "
            "required forbidden actions: " + ", ".join(sorted(missing))
        )


LOOKUP_PLAN_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "request_table",
    "request_source_row_index",
    "requested_evidence_source_database",
    "requested_evidence_source_accession",
    "planned_lookup_source_type",
    "planned_lookup_query_identifier",
    "planned_lookup_query_taxid",
)


def find_duplicate_stronger_source_lookup_plan_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate stronger-source lookup plan keys."""

    return (
        rows.group_by(list(LOOKUP_PLAN_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(LOOKUP_PLAN_KEY_COLUMNS))
    )


def validate_no_duplicate_lookup_plan_keys(rows: pl.DataFrame) -> None:
    """Validate that each stronger-source lookup plan key appears once."""

    duplicate_keys = find_duplicate_stronger_source_lookup_plan_keys(rows)
    if duplicate_keys.height:
        raise ValueError(
            "Ortholog stronger-source lookup plan table has duplicate lookup plan keys."
        )


def validate_no_blank_required_fields(rows: pl.DataFrame) -> None:
    """Validate that required fields are present and non-blank."""

    blank_required: list[str] = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog stronger-source lookup plan table has blank required fields: "
            + ", ".join(blank_required)
        )


def validate_positive_integer_fields(rows: pl.DataFrame) -> None:
    """Validate taxid and sequence-length metadata without fetching sequences."""

    checked_columns = (
        "target_species_taxid",
        "target_taxid",
        "planned_lookup_query_taxid",
        "target_sequence_length",
    )
    bad_values: list[str] = []

    for column in checked_columns:
        for value in rows.get_column(column).to_list():
            text = str(value).strip()
            if column == "target_sequence_length" and text == "unresolved":
                continue
            if not text.isdigit() or int(text) <= 0:
                bad_values.append(f"{column}={text}")

    if bad_values:
        raise ValueError(
            "Ortholog stronger-source lookup plan table has invalid positive-integer "
            "metadata values: " + ", ".join(sorted(set(bad_values)))
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
    """Validate that lookup plan rows do not contain downstream claim values."""

    observed_values: set[str] = set()
    for column in rows.columns:
        observed_values.update(str(value).strip() for value in rows.get_column(column).to_list())

    disallowed_observed = sorted(observed_values & DISALLOWED_CLAIM_VALUES)
    if disallowed_observed:
        raise ValueError(
            "Ortholog stronger-source lookup plan table contains disallowed "
            "claim values: " + ", ".join(disallowed_observed)
        )


def validate_stronger_source_lookup_plan_rows(rows: pl.DataFrame) -> None:
    """Validate stronger-source lookup plan rows without downstream promotion."""

    validate_required_columns(rows)
    validate_no_duplicate_lookup_plan_keys(rows)
    validate_allowed_values(rows)
    validate_no_blank_required_fields(rows)
    validate_positive_integer_fields(rows)
    validate_required_forbidden_actions(rows)
    validate_no_disallowed_claim_values(rows)
