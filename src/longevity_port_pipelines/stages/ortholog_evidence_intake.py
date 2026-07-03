from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import polars as pl

DEFAULT_INTAKE_TABLE_PATH = Path("data/input/ortholog_evidence_intake.csv")

BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"

REQUIRED_COLUMNS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "source_table",
    "source_row_index",
    "gene_symbol",
    "source_species",
    "target_species",
    "target_species_taxid",
    "source_uniprot",
    "partner_uniprot",
    "target_uniprot_before_intake",
    "coverage_status_before_intake",
    "provenance_status_before_intake",
    "repair_queue_status_before_intake",
    "downstream_block_status_before_intake",
    "allowed_next_action_before_intake",
    "claim_policy_before_intake",
    "evidence_source_type",
    "evidence_source_database",
    "evidence_source_accession",
    "evidence_uri_or_reproducible_lookup_note",
    "target_taxid",
    "target_species_name",
    "target_gene_symbol",
    "target_protein_accession",
    "target_sequence_length",
    "reviewer_note",
    "ambiguity_flag",
    "second_reviewer_required",
    "intake_outcome",
    "downstream_block_status_after_intake",
    "allowed_next_action_after_intake",
    "claim_policy_after_intake",
    "claim_status_after_intake",
    "forbidden_actions_after_intake",
)

INTAKE_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "source_table",
    "source_row_index",
    "evidence_source_type",
    "evidence_source_database",
    "evidence_source_accession",
)

ALLOWED_EVIDENCE_SOURCE_TYPES = {
    "reviewed_uniprot_entry",
    "uniprot_ortholog_or_taxonomy_evidence",
    "ncbi_protein_or_gene_record",
    "ensembl_orthology_evidence",
    "oma_orthology_evidence",
    "orthodb_orthology_evidence",
    "primary_literature_with_accession_level_evidence",
    "project_curated_table_with_source_accession_and_reviewer_note",
}

ALLOWED_INTAKE_OUTCOMES = {
    "evidence_ready_for_review_decision",
    "evidence_insufficient_defer",
    "evidence_conflict_reject_or_exclude",
    "evidence_ambiguous_needs_second_reviewer",
}

BLOCKED_OR_UNRESOLVED_INTAKE_OUTCOMES = {
    "evidence_insufficient_defer",
    "evidence_conflict_reject_or_exclude",
    "evidence_ambiguous_needs_second_reviewer",
}

OUTCOME_EXPECTED_VALUES = {
    "evidence_ready_for_review_decision": {
        "downstream_block_status_after_intake": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_intake": "prepare_later_reviewed_decision_pr",
        "claim_status_after_intake": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "evidence_insufficient_defer": {
        "downstream_block_status_after_intake": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_intake": "defer_until_stronger_source_evidence_exists",
        "claim_status_after_intake": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "evidence_conflict_reject_or_exclude": {
        "downstream_block_status_after_intake": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_intake": "prepare_later_rejection_or_exclusion_review",
        "claim_status_after_intake": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "evidence_ambiguous_needs_second_reviewer": {
        "downstream_block_status_after_intake": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_intake": "perform_second_reviewer_evidence_intake_review",
        "claim_status_after_intake": REPAIR_WORKLIST_CLAIM_STATUS,
    },
}

BOOLEAN_TEXT_VALUES = {
    "true",
    "false",
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


def read_intake_rows(path: Path = DEFAULT_INTAKE_TABLE_PATH) -> pl.DataFrame:
    """Read the ortholog evidence intake table.

    This reader is table-only. It does not fetch sequences, query accession
    databases, call Biohub, generate embeddings, call Boltz/AF3/Chai, rerun
    contrast, promote downstream gates, or make biological claims.
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


def find_duplicate_intake_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate ortholog evidence intake keys."""

    return (
        rows.group_by(list(INTAKE_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(INTAKE_KEY_COLUMNS))
    )


def evidence_ready_for_review_decision_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return evidence rows that may support a later reviewed-decision PR."""

    return rows.filter(pl.col("intake_outcome") == "evidence_ready_for_review_decision")


def blocked_or_unresolved_intake_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return intake rows that remain blocked or unresolved after intake."""

    return rows.filter(pl.col("intake_outcome").is_in(BLOCKED_OR_UNRESOLVED_INTAKE_OUTCOMES))


def forbidden_actions_present(row: Mapping[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row, "forbidden_actions_after_intake")
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def _validate_target_sequence_length(rows: pl.DataFrame) -> None:
    bad_values = []
    for value in rows.get_column("target_sequence_length").to_list():
        text = str(value).strip()
        if text == "unresolved":
            continue
        if not text.isdigit() or int(text) <= 0:
            bad_values.append(text)

    if bad_values:
        raise ValueError(
            "Ortholog evidence intake table has invalid target_sequence_length values: "
            + ", ".join(sorted(set(bad_values)))
        )


def _validate_outcome_rules(rows: pl.DataFrame) -> None:
    mismatches = []
    for row in rows.iter_rows(named=True):
        outcome = _text(row, "intake_outcome")
        expected_values = OUTCOME_EXPECTED_VALUES[outcome]
        for column, expected_value in expected_values.items():
            if _text(row, column) != expected_value:
                mismatches.append(f"{_text(row, 'candidate_id')}:{column}")

    if mismatches:
        raise ValueError(
            "Ortholog evidence intake table has outcome-rule mismatches: "
            + ", ".join(sorted(mismatches))
        )


def _validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    missing = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row, "candidate_id"))

    if missing:
        raise ValueError(
            "Ortholog evidence intake table has rows missing required forbidden actions: "
            + ", ".join(sorted(missing))
        )


def _validate_no_disallowed_claim_values(rows: pl.DataFrame) -> None:
    observed_values: set[str] = set()
    for column in rows.columns:
        observed_values.update(str(value).strip() for value in rows.get_column(column).to_list())

    disallowed_observed = sorted(observed_values & DISALLOWED_CLAIM_VALUES)
    if disallowed_observed:
        raise ValueError(
            "Ortholog evidence intake table contains disallowed claim values: "
            + ", ".join(disallowed_observed)
        )


def validate_intake_rows(rows: pl.DataFrame) -> None:
    """Validate ortholog evidence intake rows without creating downstream permission."""

    missing = _missing_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog evidence intake table is missing required columns: " + ", ".join(missing)
        )

    duplicate_keys = find_duplicate_intake_keys(rows)
    if duplicate_keys.height:
        raise ValueError("Ortholog evidence intake table has duplicate intake keys.")

    checks = {
        "evidence_source_type": ALLOWED_EVIDENCE_SOURCE_TYPES,
        "intake_outcome": ALLOWED_INTAKE_OUTCOMES,
        "downstream_block_status_after_intake": {BLOCKED_GATE4_GATE5},
        "claim_policy_after_intake": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_intake": {REPAIR_WORKLIST_CLAIM_STATUS},
        "ambiguity_flag": BOOLEAN_TEXT_VALUES,
        "second_reviewer_required": BOOLEAN_TEXT_VALUES,
    }
    for column, allowed_values in checks.items():
        invalid = _invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"Ortholog evidence intake table has invalid values in {column}: "
                + ", ".join(invalid)
            )

    blank_required = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog evidence intake table has blank required fields: " + ", ".join(blank_required)
        )

    _validate_target_sequence_length(rows)
    _validate_outcome_rules(rows)
    _validate_required_forbidden_actions(rows)
    _validate_no_disallowed_claim_values(rows)
