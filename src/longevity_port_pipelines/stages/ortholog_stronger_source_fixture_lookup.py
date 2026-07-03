"""Fixture-backed stronger-source lookup helpers.

This module is intentionally fixture-only. It can read committed synthetic
lookup-result fixtures and join them to fixture-backed lookup plan rows, but it
must not perform live external lookup, fetch sequences, collect source evidence,
create reviewed decisions, update Gate 4 / Gate 5 policy, promote downstream
gates, or make biological claims.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import polars as pl

from longevity_port_pipelines.stages import ortholog_stronger_source_lookup_plan as lookup_plan

DEFAULT_FIXTURE_LOOKUP_RESULTS_PATH: Final[Path] = Path(
    "tests/fixtures/ortholog_stronger_source_fixture_lookup_results.csv"
)

BLOCKED_GATE4_GATE5: Final[str] = lookup_plan.BLOCKED_GATE4_GATE5
REPAIR_WORKLIST_CLAIM_STATUS: Final[str] = lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "fixture_lookup_result_id",
    "candidate_set",
    "candidate_id",
    "requested_evidence_source_database",
    "requested_evidence_source_accession",
    "target_taxid",
    "target_species_name",
    "target_gene_symbol",
    "planned_lookup_source_type",
    "planned_lookup_source_name",
    "planned_lookup_query_identifier",
    "planned_lookup_query_taxid",
    "fixture_lookup_status",
    "fixture_payload_accession",
    "fixture_payload_source_name",
    "fixture_payload_review_status",
    "fixture_payload_taxid",
    "fixture_payload_gene_symbol",
    "fixture_payload_sequence_length",
    "fixture_result_block_status",
    "fixture_result_claim_status",
    "fixture_result_is_evidence",
    "fixture_result_note",
)

LOOKUP_JOIN_COLUMNS: Final[tuple[str, ...]] = (
    "candidate_set",
    "candidate_id",
    "requested_evidence_source_database",
    "requested_evidence_source_accession",
    "target_taxid",
    "target_gene_symbol",
    "planned_lookup_source_type",
    "planned_lookup_query_identifier",
    "planned_lookup_query_taxid",
)

ALLOWED_FIXTURE_LOOKUP_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "fixture_hit_still_blocked",
        "fixture_miss_still_blocked",
        "fixture_error_still_blocked",
        "fixture_deferred_still_blocked",
    }
)

ALLOWED_FIXTURE_PAYLOAD_REVIEW_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "reviewed",
        "unreviewed",
        "unresolved",
        "not_applicable",
    }
)

DISALLOWED_FIXTURE_TEXT_VALUES: Final[frozenset[str]] = frozenset(
    {
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
        "reviewed decision created",
        "Gate 4 policy updated",
        "Gate 5 policy updated",
    }
)


def read_fixture_lookup_result_rows(
    path: Path = DEFAULT_FIXTURE_LOOKUP_RESULTS_PATH,
) -> pl.DataFrame:
    """Read committed synthetic fixture lookup rows.

    This reader is intentionally local-file-only. It does not perform live
    external lookup, does not fetch sequences, and does not create source
    evidence rows.
    """
    return pl.read_csv(path, infer_schema_length=0)


def empty_fixture_lookup_result_rows() -> pl.DataFrame:
    """Return an empty fixture result frame with the committed fixture schema."""
    return pl.DataFrame(schema={column: pl.String for column in REQUIRED_COLUMNS})


def missing_required_columns(rows: pl.DataFrame) -> list[str]:
    """Return required fixture columns missing from a DataFrame."""
    present = set(rows.columns)
    return [column for column in REQUIRED_COLUMNS if column not in present]


def validate_required_columns(rows: pl.DataFrame) -> None:
    """Require fixture lookup rows to use the committed fixture schema."""
    missing = missing_required_columns(rows)
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def invalid_values(
    rows: pl.DataFrame,
    column: str,
    allowed_values: frozenset[str],
) -> list[str]:
    """Return sorted non-empty values outside an allowed set."""
    if column not in rows.columns or rows.is_empty():
        return []

    values = (
        rows.select(pl.col(column).cast(pl.String).str.strip_chars().alias(column))
        .filter(pl.col(column) != "")
        .get_column(column)
        .to_list()
    )
    return sorted({str(value) for value in values if str(value) not in allowed_values})


def validate_allowed_values(rows: pl.DataFrame) -> None:
    """Validate fixture result rows remain blocked, local, and non-evidence."""
    validate_required_columns(rows)

    checks: tuple[tuple[str, frozenset[str]], ...] = (
        ("planned_lookup_source_type", frozenset(lookup_plan.ALLOWED_PLANNED_LOOKUP_SOURCE_TYPES)),
        ("fixture_lookup_status", ALLOWED_FIXTURE_LOOKUP_STATUSES),
        ("fixture_payload_review_status", ALLOWED_FIXTURE_PAYLOAD_REVIEW_STATUSES),
        ("fixture_result_block_status", frozenset({BLOCKED_GATE4_GATE5})),
        ("fixture_result_claim_status", frozenset({REPAIR_WORKLIST_CLAIM_STATUS})),
        ("fixture_result_is_evidence", frozenset({"false"})),
    )

    errors: list[str] = []
    for column, allowed_values in checks:
        invalid = invalid_values(rows, column, allowed_values)
        if invalid:
            errors.append(f"{column}: {invalid}")

    if errors:
        raise ValueError(f"invalid fixture lookup values: {'; '.join(errors)}")


def duplicate_fixture_result_ids(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate fixture result IDs, if any."""
    validate_required_columns(rows)
    if rows.is_empty():
        return pl.DataFrame(schema={"fixture_lookup_result_id": pl.String, "count": pl.UInt32})

    return (
        rows.group_by("fixture_lookup_result_id")
        .len(name="count")
        .filter(pl.col("count") > 1)
        .sort("fixture_lookup_result_id")
    )


def validate_unique_fixture_result_ids(rows: pl.DataFrame) -> None:
    """Require stable unique fixture result IDs."""
    duplicates = duplicate_fixture_result_ids(rows)
    if not duplicates.is_empty():
        raise ValueError(f"duplicate fixture lookup result ids: {duplicates.to_dicts()}")


def validate_no_blank_required_fields(rows: pl.DataFrame) -> None:
    """Reject blank values in required fixture fields."""
    validate_required_columns(rows)
    if rows.is_empty():
        return

    blank_columns: list[str] = []
    for column in REQUIRED_COLUMNS:
        blank_count = rows.filter(pl.col(column).cast(pl.String).str.strip_chars() == "").height
        if blank_count:
            blank_columns.append(column)

    if blank_columns:
        raise ValueError(f"blank required fixture fields: {blank_columns}")


def validate_positive_integer_fields(rows: pl.DataFrame) -> None:
    """Validate taxids and sequence lengths without fetching sequences."""
    validate_required_columns(rows)
    if rows.is_empty():
        return

    errors: list[str] = []
    strict_columns = (
        "target_taxid",
        "planned_lookup_query_taxid",
        "fixture_payload_taxid",
    )
    for column in strict_columns:
        invalid = rows.filter(
            pl.col(column).cast(pl.String).str.strip_chars().str.contains(r"^[1-9][0-9]*$").not_()
        )
        if invalid.height:
            errors.append(f"{column}: {invalid.select(column).to_series().to_list()}")

    length_invalid = rows.filter(
        (
            pl.col("fixture_payload_sequence_length")
            .cast(pl.String)
            .str.strip_chars()
            .str.contains(r"^[1-9][0-9]*$")
            .not_()
        )
        & (pl.col("fixture_payload_sequence_length") != "unresolved")
    )
    if length_invalid.height:
        errors.append(
            "fixture_payload_sequence_length: "
            f"{length_invalid.select('fixture_payload_sequence_length').to_series().to_list()}"
        )

    if errors:
        raise ValueError(f"invalid positive-integer fixture metadata: {'; '.join(errors)}")


def validate_no_disallowed_fixture_text(rows: pl.DataFrame) -> None:
    """Reject fixture text that encodes downstream permission or claims."""
    validate_required_columns(rows)
    if rows.is_empty():
        return

    disallowed_hits: list[dict[str, str]] = []
    for row in rows.iter_rows(named=True):
        for column, value in row.items():
            text = str(value).strip()
            if text in DISALLOWED_FIXTURE_TEXT_VALUES:
                disallowed_hits.append(
                    {
                        "column": str(column),
                        "value": text,
                        "fixture_lookup_result_id": str(row["fixture_lookup_result_id"]),
                    }
                )

    if disallowed_hits:
        raise ValueError(f"disallowed fixture lookup text values: {disallowed_hits}")


def validate_fixture_lookup_result_rows(rows: pl.DataFrame) -> None:
    """Run all fixture lookup result validators."""
    validate_required_columns(rows)
    validate_allowed_values(rows)
    validate_unique_fixture_result_ids(rows)
    validate_no_blank_required_fields(rows)
    validate_positive_integer_fields(rows)
    validate_no_disallowed_fixture_text(rows)


def fixture_backed_lookup_plan_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return lookup plan rows explicitly marked as fixture-backed only."""
    lookup_plan.validate_stronger_source_lookup_plan_rows(rows)
    if rows.is_empty():
        return rows

    return rows.filter(pl.col("planned_lookup_mode") == "fixture_backed_only")


def lookup_fixture_results_for_plan_rows(
    plan_rows: pl.DataFrame,
    fixture_rows: pl.DataFrame,
) -> pl.DataFrame:
    """Join fixture-backed lookup plan rows to local synthetic fixture results.

    The returned rows are fixture lookup results only. They are not evidence
    rows, reviewed decisions, coverage rows, or downstream-gate permissions.
    """
    fixture_plan_rows = fixture_backed_lookup_plan_rows(plan_rows)
    validate_fixture_lookup_result_rows(fixture_rows)

    if fixture_plan_rows.is_empty() or fixture_rows.is_empty():
        return empty_fixture_lookup_result_rows()

    join_rows = fixture_plan_rows.select(list(LOOKUP_JOIN_COLUMNS))
    joined = join_rows.join(fixture_rows, on=list(LOOKUP_JOIN_COLUMNS), how="inner")
    if joined.is_empty():
        return empty_fixture_lookup_result_rows()

    return joined.select(list(REQUIRED_COLUMNS))


def lookup_fixture_results_from_default_fixture(
    plan_rows: pl.DataFrame,
    fixture_path: Path = DEFAULT_FIXTURE_LOOKUP_RESULTS_PATH,
) -> pl.DataFrame:
    """Read the default local fixture and join it to fixture-backed plan rows."""
    fixture_rows = read_fixture_lookup_result_rows(fixture_path)
    return lookup_fixture_results_for_plan_rows(plan_rows, fixture_rows)
