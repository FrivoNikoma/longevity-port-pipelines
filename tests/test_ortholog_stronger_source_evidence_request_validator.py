from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_evidence_request as request,
)


def test_stronger_source_request_reader_loads_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    assert rows.height == 1

    row = rows.row(0, named=True)
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["evidence_source_accession"] == "G3SX30"


def test_pending_source_collection_helper_finds_committed_row() -> None:
    rows = request.read_stronger_source_request_rows()
    pending_rows = request.pending_source_collection_rows(rows)

    assert pending_rows.height == 1

    row = pending_rows.row(0, named=True)
    assert row["request_status"] == "pending_source_collection"
    assert row["request_decision"] == "needs_manual_source_collection"


def test_default_path_points_to_committed_request_table() -> None:
    assert (
        Path("data/input/ortholog_stronger_source_evidence_requests.csv")
        == request.DEFAULT_STRONGER_SOURCE_REQUEST_PATH
    )


def test_constants_preserve_blocker_first_policy() -> None:
    assert request.BLOCKED_GATE4_GATE5 == "blocked_gate4_gate5"
    assert request.NO_BIOLOGICAL_CLAIMS_POLICY == "no_biological_claims_until_validation"
    assert request.REPAIR_WORKLIST_CLAIM_STATUS == "repair_worklist"


def test_required_columns_are_present_in_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    assert request.missing_required_columns(rows) == []
    request.validate_required_columns(rows)


def test_validate_required_columns_rejects_missing_column() -> None:
    rows = request.read_stronger_source_request_rows().drop("claim_status_after_request")

    with pytest.raises(ValueError, match="missing required columns"):
        request.validate_required_columns(rows)


def test_validate_allowed_values_accepts_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    request.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_invalid_request_status() -> None:
    rows = request.read_stronger_source_request_rows().with_columns(
        pl.lit("accepted_ortholog").alias("request_status")
    )

    with pytest.raises(ValueError, match="invalid values in request_status"):
        request.validate_allowed_values(rows)


def test_forbidden_actions_present_accepts_committed_row() -> None:
    rows = request.read_stronger_source_request_rows()
    row = rows.row(0, named=True)

    assert request.forbidden_actions_present(row)


def test_validate_required_forbidden_actions_accepts_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    request.validate_required_forbidden_actions(rows)


def test_validate_required_forbidden_actions_rejects_missing_actions() -> None:
    rows = request.read_stronger_source_request_rows().with_columns(
        pl.lit("ortholog acceptance").alias("forbidden_actions_after_request")
    )

    with pytest.raises(ValueError, match="missing required forbidden actions"):
        request.validate_required_forbidden_actions(rows)


def test_validate_no_duplicate_request_keys_accepts_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    request.validate_no_duplicate_request_keys(rows)


def test_validate_no_duplicate_request_keys_rejects_duplicate_row() -> None:
    rows = request.read_stronger_source_request_rows()
    duplicate_rows = pl.concat([rows, rows])

    with pytest.raises(ValueError, match="duplicate request keys"):
        request.validate_no_duplicate_request_keys(duplicate_rows)


def test_validate_no_blank_required_fields_accepts_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    request.validate_no_blank_required_fields(rows)


def test_validate_no_blank_required_fields_rejects_blank_required_value() -> None:
    rows = request.read_stronger_source_request_rows().with_columns(
        pl.lit("").alias("request_reason")
    )

    with pytest.raises(ValueError, match="blank required fields"):
        request.validate_no_blank_required_fields(rows)


def test_validate_target_sequence_length_accepts_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    request.validate_target_sequence_length(rows)


def test_validate_target_sequence_length_accepts_unresolved() -> None:
    rows = request.read_stronger_source_request_rows().with_columns(
        pl.lit("unresolved").alias("target_sequence_length")
    )

    request.validate_target_sequence_length(rows)


def test_validate_target_sequence_length_rejects_non_positive_length() -> None:
    rows = request.read_stronger_source_request_rows().with_columns(
        pl.lit("0").alias("target_sequence_length")
    )

    with pytest.raises(ValueError, match="invalid target_sequence_length"):
        request.validate_target_sequence_length(rows)


def test_validate_no_disallowed_claim_values_accepts_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    request.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_gate8_claim() -> None:
    rows = request.read_stronger_source_request_rows().with_columns(
        pl.lit("Gate 8 eligible").alias("claim_status_after_request")
    )

    with pytest.raises(ValueError, match="disallowed claim values"):
        request.validate_no_disallowed_claim_values(rows)


def test_validate_stronger_source_request_rows_accepts_committed_table() -> None:
    rows = request.read_stronger_source_request_rows()

    request.validate_stronger_source_request_rows(rows)


def test_validate_stronger_source_request_rows_rejects_downstream_claim() -> None:
    rows = request.read_stronger_source_request_rows().with_columns(
        pl.lit("validated_ortholog").alias("claim_status_after_request")
    )

    with pytest.raises(ValueError, match="invalid values|disallowed claim values"):
        request.validate_stronger_source_request_rows(rows)
