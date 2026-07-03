from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import polars as pl

BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"
BIOLOGICAL_CLAIM_STATUS_NONE = "no_biological_claim"

DEFAULT_RAW_METADATA_RESPONSE_PATH = Path(
    "data/input/ortholog_stronger_source_raw_metadata_responses.csv"
)

REQUIRED_REQUEST_TRACE_COLUMNS = (
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
)

REQUIRED_LOOKUP_TRACE_COLUMNS = (
    "planned_lookup_source_type",
    "planned_lookup_source_name",
    "planned_lookup_query_identifier",
    "planned_lookup_query_taxid",
    "live_lookup_policy_decision",
    "dry_run_status",
    "dry_run_provider_mode",
    "raw_metadata_status",
)

REQUIRED_RAW_METADATA_RESPONSE_COLUMNS = (
    "raw_metadata_response_status",
    "raw_metadata_review_status",
    "raw_metadata_source_type",
    "raw_metadata_source_name",
    "raw_metadata_source_identifier",
    "raw_metadata_payload_ref",
    "raw_metadata_summary",
    "sequence_fetched",
    "source_evidence_created",
    "reviewed_decision_created",
    "gate4_gate5_policy_updated",
    "gate8_promoted",
    "gate9_promoted",
    "downstream_block_status_after_raw_metadata",
    "claim_policy_after_raw_metadata",
    "claim_status_after_raw_metadata",
    "biological_claim_status",
    "forbidden_actions_after_raw_metadata",
    "reviewer_note",
)

REQUIRED_COLUMNS = (
    *REQUIRED_REQUEST_TRACE_COLUMNS,
    *REQUIRED_LOOKUP_TRACE_COLUMNS,
    *REQUIRED_RAW_METADATA_RESPONSE_COLUMNS,
)


def read_raw_metadata_response_rows(
    path: Path = DEFAULT_RAW_METADATA_RESPONSE_PATH,
) -> pl.DataFrame:
    """Read the stronger-source raw metadata response table.

    This reader is table-only. It does not query external databases, fetch
    sequences, persist runtime output from a live provider, create source
    evidence, create manual review rows, create reviewed decisions, update
    Gate 4 / Gate 5 policy, promote Gate 8 or Gate 9, call Biohub, generate
    embeddings, call Boltz/AF3/Chai, rerun contrast, or make biological claims.
    """

    return pl.read_csv(path, infer_schema_length=0)


def raw_metadata_candidate_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return raw metadata rows that remain unreviewed and still blocked."""

    return rows.filter(
        pl.col("raw_metadata_response_status") == "raw_metadata_received_unreviewed_still_blocked"
    )


def missing_required_columns(rows: pl.DataFrame) -> list[str]:
    """Return required columns missing from the raw metadata response table."""

    return [column for column in REQUIRED_COLUMNS if column not in rows.columns]


def validate_required_columns(rows: pl.DataFrame) -> None:
    """Validate that the raw metadata response table has all required columns."""

    missing = missing_required_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog stronger-source raw metadata response table is missing "
            "required columns: " + ", ".join(missing)
        )


ALLOWED_PLANNED_LOOKUP_SOURCE_TYPES = {
    "reviewed_uniprot",
    "ncbi_protein_or_gene_record",
    "ensembl_orthology",
    "oma_orthology",
    "orthodb_orthology",
    "primary_literature",
    "other_manual_source",
}

ALLOWED_DRY_RUN_STATUSES = {
    "dry_run_raw_metadata_candidate_still_blocked",
    "dry_run_skipped_policy_denied_still_blocked",
}

ALLOWED_DRY_RUN_PROVIDER_MODES = {
    "injected_fake_or_noop_provider_only",
}

ALLOWED_RAW_METADATA_STATUSES = {
    "raw_metadata_dry_run_noop_unreviewed",
    "raw_metadata_received_unreviewed",
    "raw_metadata_fake_provider_unreviewed",
    "not_requested_policy_denied",
}

ALLOWED_RAW_METADATA_RESPONSE_STATUSES = {
    "raw_metadata_received_unreviewed_still_blocked",
    "raw_metadata_not_requested_policy_denied",
    "raw_metadata_deferred_keep_blocked",
    "raw_metadata_conflict_keep_blocked",
}

ALLOWED_RAW_METADATA_REVIEW_STATUSES = {
    "unreviewed_raw_metadata",
    "raw_metadata_requires_manual_review",
}

ALLOWED_RAW_METADATA_SOURCE_TYPES = {
    "reviewed_uniprot",
    "ncbi_protein_or_gene_record",
    "ensembl_orthology",
    "oma_orthology",
    "orthodb_orthology",
    "primary_literature",
    "other_manual_source",
    "injected_fake_or_noop_provider",
}

FALSE_ONLY_COLUMNS = (
    "sequence_fetched",
    "source_evidence_created",
    "reviewed_decision_created",
    "gate4_gate5_policy_updated",
    "gate8_promoted",
    "gate9_promoted",
)


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
    """Validate conservative raw-metadata response vocabularies."""

    checks = {
        "planned_lookup_source_type": ALLOWED_PLANNED_LOOKUP_SOURCE_TYPES,
        "dry_run_status": ALLOWED_DRY_RUN_STATUSES,
        "dry_run_provider_mode": ALLOWED_DRY_RUN_PROVIDER_MODES,
        "raw_metadata_status": ALLOWED_RAW_METADATA_STATUSES,
        "raw_metadata_response_status": ALLOWED_RAW_METADATA_RESPONSE_STATUSES,
        "raw_metadata_review_status": ALLOWED_RAW_METADATA_REVIEW_STATUSES,
        "raw_metadata_source_type": ALLOWED_RAW_METADATA_SOURCE_TYPES,
        "downstream_block_status_after_raw_metadata": {BLOCKED_GATE4_GATE5},
        "claim_policy_after_raw_metadata": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_raw_metadata": {REPAIR_WORKLIST_CLAIM_STATUS},
        "biological_claim_status": {BIOLOGICAL_CLAIM_STATUS_NONE},
    }

    for column, allowed_values in checks.items():
        invalid = invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                f"Ortholog stronger-source raw metadata response table has "
                f"invalid values in {column}: " + ", ".join(invalid)
            )


def validate_false_only_columns(rows: pl.DataFrame) -> None:
    """Validate that side-effect flags remain false."""

    invalid_columns: list[str] = []
    for column in FALSE_ONLY_COLUMNS:
        invalid = invalid_values(rows, column=column, allowed_values={"false"})
        if invalid:
            invalid_columns.append(f"{column}: " + ", ".join(invalid))

    if invalid_columns:
        raise ValueError(
            "Ortholog stronger-source raw metadata response table has side-effect "
            "flags that must remain false: " + "; ".join(invalid_columns)
        )


RUNTIME_SIDE_EFFECTS = frozenset(
    {
        "runtime persistence from live provider",
        "source evidence creation",
        "manual review row creation",
        "reviewed decision creation",
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


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


DRY_RUN_LOOKUP_JOIN_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "planned_lookup_source_type",
    "planned_lookup_query_identifier",
)

DRY_RUN_DERIVED_RAW_METADATA_SOURCE_TYPE = "injected_fake_or_noop_provider"

DRY_RUN_DERIVED_PAYLOAD_REF_MARKERS = ("dry_run", "not_persisted")
DRY_RUN_DERIVED_SUMMARY_MARKERS = ("dry-run", "non-evidence")
DRY_RUN_DERIVED_REVIEWER_NOTE_MARKERS = ("dry-run-derived", "not source evidence")


def empty_raw_metadata_response_rows() -> pl.DataFrame:
    """Return an empty typed raw metadata response frame."""

    return pl.DataFrame(schema={column: pl.String for column in REQUIRED_COLUMNS})


def raw_metadata_response_status_for_dry_run_summary_row(
    dry_run_summary_row: Mapping[str, object],
) -> str | None:
    """Return raw metadata response status for a dry-run summary row.

    Only dry-run rows where the injected fake/noop provider was called are
    mapped into raw metadata response rows. Policy-denied dry-run rows are
    skipped because they did not request or receive raw metadata.
    """

    if (
        _text(dry_run_summary_row.get("dry_run_status"))
        == "dry_run_raw_metadata_candidate_still_blocked"
    ):
        return "raw_metadata_received_unreviewed_still_blocked"

    return None


def raw_metadata_response_row_from_dry_run_summary_row(
    *,
    lookup_plan_row: Mapping[str, object],
    dry_run_summary_row: Mapping[str, object],
) -> dict[str, str] | None:
    """Build one conservative raw metadata response row from dry-run output.

    The row is built in memory only. It preserves request/provenance trace from
    the lookup plan and runtime dry-run status from the dry-run summary. It does
    not write files, call providers, query external databases, fetch sequences,
    create source evidence, create review rows, create reviewed decisions,
    update Gate 4 / Gate 5 policy, promote Gate 8 or Gate 9, or make biological
    claims.
    """

    raw_metadata_response_status = raw_metadata_response_status_for_dry_run_summary_row(
        dry_run_summary_row
    )
    if raw_metadata_response_status is None:
        return None

    planned_lookup_query_identifier = _text(
        dry_run_summary_row.get("planned_lookup_query_identifier")
    )

    return {
        "candidate_set": _text(lookup_plan_row.get("candidate_set")),
        "lane_name": _text(lookup_plan_row.get("lane_name")),
        "candidate_id": _text(lookup_plan_row.get("candidate_id")),
        "request_table": _text(lookup_plan_row.get("request_table")),
        "request_source_row_index": _text(lookup_plan_row.get("request_source_row_index")),
        "gene_symbol": _text(lookup_plan_row.get("gene_symbol")),
        "source_species": _text(lookup_plan_row.get("source_species")),
        "target_species": _text(lookup_plan_row.get("target_species")),
        "target_species_taxid": _text(lookup_plan_row.get("target_species_taxid")),
        "source_uniprot": _text(lookup_plan_row.get("source_uniprot")),
        "partner_uniprot": _text(lookup_plan_row.get("partner_uniprot")),
        "requested_evidence_source_database": _text(
            lookup_plan_row.get("requested_evidence_source_database")
        ),
        "requested_evidence_source_accession": _text(
            lookup_plan_row.get("requested_evidence_source_accession")
        ),
        "target_taxid": _text(lookup_plan_row.get("target_taxid")),
        "target_species_name": _text(lookup_plan_row.get("target_species_name")),
        "target_gene_symbol": _text(lookup_plan_row.get("target_gene_symbol")),
        "target_protein_accession": _text(lookup_plan_row.get("target_protein_accession")),
        "target_sequence_length": _text(lookup_plan_row.get("target_sequence_length")),
        "planned_lookup_source_type": _text(dry_run_summary_row.get("planned_lookup_source_type")),
        "planned_lookup_source_name": _text(lookup_plan_row.get("planned_lookup_source_name")),
        "planned_lookup_query_identifier": planned_lookup_query_identifier,
        "planned_lookup_query_taxid": _text(lookup_plan_row.get("planned_lookup_query_taxid")),
        "live_lookup_policy_decision": _text(
            dry_run_summary_row.get("live_lookup_policy_decision")
        ),
        "dry_run_status": _text(dry_run_summary_row.get("dry_run_status")),
        "dry_run_provider_mode": _text(dry_run_summary_row.get("dry_run_provider_mode")),
        "raw_metadata_status": _text(dry_run_summary_row.get("raw_metadata_status")),
        "raw_metadata_response_status": raw_metadata_response_status,
        "raw_metadata_review_status": "unreviewed_raw_metadata",
        "raw_metadata_source_type": "injected_fake_or_noop_provider",
        "raw_metadata_source_name": _text(dry_run_summary_row.get("dry_run_provider_mode")),
        "raw_metadata_source_identifier": f"dry_run:{planned_lookup_query_identifier}",
        "raw_metadata_payload_ref": "dry_run_summary_payload_not_persisted",
        "raw_metadata_summary": (
            "Raw metadata response row built in memory from dry-run summary only; "
            "raw metadata remains unreviewed and non-evidence."
        ),
        "sequence_fetched": "false",
        "source_evidence_created": "false",
        "reviewed_decision_created": "false",
        "gate4_gate5_policy_updated": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "downstream_block_status_after_raw_metadata": BLOCKED_GATE4_GATE5,
        "claim_policy_after_raw_metadata": NO_BIOLOGICAL_CLAIMS_POLICY,
        "claim_status_after_raw_metadata": REPAIR_WORKLIST_CLAIM_STATUS,
        "biological_claim_status": BIOLOGICAL_CLAIM_STATUS_NONE,
        "forbidden_actions_after_raw_metadata": "; ".join(sorted(RUNTIME_SIDE_EFFECTS)),
        "reviewer_note": (
            "In-memory dry-run-derived raw metadata response only; not source "
            "evidence, not reviewed, not a Gate 4 / Gate 5 update, and not "
            "downstream eligibility."
        ),
    }


def build_raw_metadata_response_rows_from_dry_run_summary(
    *,
    lookup_plan_rows: pl.DataFrame,
    dry_run_summary_rows: pl.DataFrame,
) -> pl.DataFrame:
    """Build raw metadata response rows from dry-run summary rows in memory only."""

    if lookup_plan_rows.is_empty() or dry_run_summary_rows.is_empty():
        return empty_raw_metadata_response_rows()

    candidate_dry_run_rows = dry_run_summary_rows.filter(
        pl.col("dry_run_status") == "dry_run_raw_metadata_candidate_still_blocked"
    )
    if candidate_dry_run_rows.is_empty():
        return empty_raw_metadata_response_rows()

    joined_rows = lookup_plan_rows.join(
        candidate_dry_run_rows,
        on=list(DRY_RUN_LOOKUP_JOIN_COLUMNS),
        how="inner",
    )

    if joined_rows.height != candidate_dry_run_rows.height:
        raise ValueError(
            "Could not match every raw metadata candidate dry-run summary row "
            "to lookup plan provenance."
        )

    response_rows = [
        response_row
        for joined_row in joined_rows.iter_rows(named=True)
        if (
            response_row := raw_metadata_response_row_from_dry_run_summary_row(
                lookup_plan_row=joined_row,
                dry_run_summary_row=joined_row,
            )
        )
        is not None
    ]

    if not response_rows:
        return empty_raw_metadata_response_rows()

    rows = pl.DataFrame(response_rows).select(list(REQUIRED_COLUMNS))
    validate_stronger_source_raw_metadata_response_rows(rows)
    return rows.sort(list(RAW_METADATA_RESPONSE_KEY_COLUMNS))


def raw_metadata_row_is_dry_run_derived(row: Mapping[str, object]) -> bool:
    """Return true when a row is explicitly derived from fake/noop dry-run output."""

    return _text(row.get("raw_metadata_source_type")) == DRY_RUN_DERIVED_RAW_METADATA_SOURCE_TYPE


def _contains_all_markers(value: object, markers: tuple[str, ...]) -> bool:
    text = _text(value).lower()
    return all(marker in text for marker in markers)


def validate_dry_run_derived_rows_remain_explicit(rows: pl.DataFrame) -> None:
    """Validate that dry-run-derived rows cannot look like real metadata.

    Dry-run-derived raw metadata response rows may be exported as table rows, but
    they must remain explicit fake/noop dry-run artifacts. They are not real
    external database metadata, not source evidence, not reviewed decisions, not
    Gate 4 / Gate 5 policy updates, not downstream eligibility, and not
    biological claims.
    """

    validate_required_columns(rows)

    bad_rows: list[str] = []
    for row in rows.iter_rows(named=True):
        if not raw_metadata_row_is_dry_run_derived(row):
            continue

        if not (
            _contains_all_markers(
                row.get("raw_metadata_payload_ref"),
                DRY_RUN_DERIVED_PAYLOAD_REF_MARKERS,
            )
            and _contains_all_markers(
                row.get("raw_metadata_summary"),
                DRY_RUN_DERIVED_SUMMARY_MARKERS,
            )
            and _contains_all_markers(
                row.get("reviewer_note"),
                DRY_RUN_DERIVED_REVIEWER_NOTE_MARKERS,
            )
        ):
            bad_rows.append(_text(row.get("candidate_id", "")))

    if bad_rows:
        raise ValueError(
            "Dry-run-derived raw metadata response rows must remain explicit "
            "fake/noop non-evidence artifacts: " + ", ".join(sorted(bad_rows))
        )


def write_raw_metadata_response_rows(
    rows: pl.DataFrame,
    output_path: Path,
) -> Path:
    """Write already-built raw metadata response rows to an explicit table path.

    This is a table-only exporter. It writes only rows passed by the caller. It
    does not build rows, call providers, query external databases, fetch
    sequences, create source evidence, create manual review rows, create
    reviewed decisions, update Gate 4 / Gate 5 policy, promote Gate 8 or Gate 9,
    call Biohub, generate embeddings, call Boltz/AF3/Chai, rerun contrast, or
    make biological claims.
    """

    validate_stronger_source_raw_metadata_response_rows(rows)
    validate_dry_run_derived_rows_remain_explicit(rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows.select(list(REQUIRED_COLUMNS)).write_csv(output_path)
    return output_path


def forbidden_actions_present(row: dict[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row.get("forbidden_actions_after_raw_metadata", ""))
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    """Validate that every raw metadata row forbids runtime side effects."""

    missing: list[str] = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row.get("candidate_id", "")))

    if missing:
        raise ValueError(
            "Ortholog stronger-source raw metadata response table has rows "
            "missing required forbidden actions: " + ", ".join(sorted(missing))
        )


RAW_METADATA_RESPONSE_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "request_table",
    "request_source_row_index",
    "requested_evidence_source_database",
    "requested_evidence_source_accession",
    "planned_lookup_source_type",
    "planned_lookup_query_identifier",
    "raw_metadata_source_type",
    "raw_metadata_source_identifier",
)


def find_duplicate_raw_metadata_response_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate raw metadata response keys."""

    return (
        rows.group_by(list(RAW_METADATA_RESPONSE_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(RAW_METADATA_RESPONSE_KEY_COLUMNS))
    )


def validate_no_duplicate_raw_metadata_response_keys(rows: pl.DataFrame) -> None:
    """Validate that each raw metadata response key appears once."""

    duplicate_keys = find_duplicate_raw_metadata_response_keys(rows)
    if duplicate_keys.height:
        raise ValueError(
            "Ortholog stronger-source raw metadata response table has duplicate "
            "raw metadata response keys."
        )


def validate_no_blank_required_fields(rows: pl.DataFrame) -> None:
    """Validate that required fields are present and non-blank."""

    blank_required: list[str] = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog stronger-source raw metadata response table has blank "
            "required fields: " + ", ".join(blank_required)
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
            "Ortholog stronger-source raw metadata response table has invalid "
            "target_sequence_length values: " + ", ".join(sorted(set(bad_values)))
        )


DISALLOWED_CLAIM_VALUES = {
    "accepted_ortholog",
    "validated_ortholog",
    "curated_ortholog_candidate",
    "Gate 8 eligible",
    "Gate 9 eligible",
    "safe_to_port",
    "biological_claim",
}


def validate_no_disallowed_claim_values(rows: pl.DataFrame) -> None:
    """Validate that raw metadata rows do not encode downstream claims."""

    claim_columns = (
        "claim_status_after_raw_metadata",
        "biological_claim_status",
        "reviewer_note",
        "raw_metadata_summary",
    )

    bad_values: list[str] = []
    for row in rows.iter_rows(named=True):
        for column in claim_columns:
            value = _text(row.get(column, ""))
            for disallowed in DISALLOWED_CLAIM_VALUES:
                if value == disallowed:
                    bad_values.append(f"{column}={value}")

    if bad_values:
        raise ValueError(
            "Ortholog stronger-source raw metadata response table has disallowed "
            "claim values: " + "; ".join(sorted(set(bad_values)))
        )


def validate_stronger_source_raw_metadata_response_rows(rows: pl.DataFrame) -> None:
    """Validate the raw metadata response table contract."""

    validate_required_columns(rows)
    validate_allowed_values(rows)
    validate_false_only_columns(rows)
    validate_required_forbidden_actions(rows)
    validate_no_duplicate_raw_metadata_response_keys(rows)
    validate_no_blank_required_fields(rows)
    validate_target_sequence_length(rows)
    validate_no_disallowed_claim_values(rows)
