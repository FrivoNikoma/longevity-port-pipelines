from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_raw_metadata_response as raw_metadata,
)


def valid_raw_metadata_response_row() -> dict[str, str]:
    return {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2_elephant",
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "request_table": "data/input/ortholog_stronger_source_evidence_requests.csv",
        "request_source_row_index": "1",
        "gene_symbol": "MDM2",
        "source_species": "human",
        "target_species": "elephant",
        "target_species_taxid": "9785",
        "source_uniprot": "Q00987",
        "partner_uniprot": "P04637",
        "requested_evidence_source_database": "UniProtKB TrEMBL",
        "requested_evidence_source_accession": "G3SX30",
        "target_taxid": "9785",
        "target_species_name": "Loxodonta africana",
        "target_gene_symbol": "MDM2",
        "target_protein_accession": "G3SX30",
        "target_sequence_length": "492",
        "planned_lookup_source_type": "other_manual_source",
        "planned_lookup_source_name": "manual_source_placeholder",
        "planned_lookup_query_identifier": "G3SX30",
        "planned_lookup_query_taxid": "9785",
        "live_lookup_policy_decision": "authorized_still_blocked",
        "dry_run_status": "dry_run_raw_metadata_candidate_still_blocked",
        "dry_run_provider_mode": "injected_fake_or_noop_provider_only",
        "raw_metadata_status": "raw_metadata_dry_run_noop_unreviewed",
        "raw_metadata_response_status": "raw_metadata_received_unreviewed_still_blocked",
        "raw_metadata_review_status": "unreviewed_raw_metadata",
        "raw_metadata_source_type": "injected_fake_or_noop_provider",
        "raw_metadata_source_name": "noop_live_metadata_provider",
        "raw_metadata_source_identifier": "noop:G3SX30",
        "raw_metadata_payload_ref": "dry_run_noop_payload_not_persisted",
        "raw_metadata_summary": (
            "Synthetic raw metadata response validator test row only; "
            "raw metadata remains unreviewed and non-evidence."
        ),
        "sequence_fetched": "false",
        "source_evidence_created": "false",
        "reviewed_decision_created": "false",
        "gate4_gate5_policy_updated": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "downstream_block_status_after_raw_metadata": "blocked_gate4_gate5",
        "claim_policy_after_raw_metadata": "no_biological_claims_until_validation",
        "claim_status_after_raw_metadata": "repair_worklist",
        "biological_claim_status": "no_biological_claim",
        "forbidden_actions_after_raw_metadata": (
            "runtime persistence from live provider; source evidence creation; "
            "manual review row creation; reviewed decision creation; "
            "ortholog acceptance; ortholog validation; "
            "Gate 4 or Gate 5 policy update; sequence fetch; "
            "external database query; Biohub call; embedding generation; "
            "Boltz call; AF3 call; Chai call; enrichment rerun; contrast rerun; "
            "Gate 8 promotion; Gate 9 promotion; biological claim"
        ),
        "reviewer_note": (
            "Synthetic validator test row only; not source evidence, not reviewed, "
            "not downstream eligibility."
        ),
    }


def valid_raw_metadata_response_rows() -> pl.DataFrame:
    return pl.DataFrame([valid_raw_metadata_response_row()])


def test_raw_metadata_response_reader_loads_committed_header_only_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    assert rows.height == 0
    assert rows.columns == list(raw_metadata.REQUIRED_COLUMNS)


def test_default_path_points_to_committed_raw_metadata_response_table() -> None:
    assert (
        Path("data/input/ortholog_stronger_source_raw_metadata_responses.csv")
        == raw_metadata.DEFAULT_RAW_METADATA_RESPONSE_PATH
    )


def test_raw_metadata_candidate_helper_accepts_empty_committed_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()
    candidate_rows = raw_metadata.raw_metadata_candidate_rows(rows)

    assert candidate_rows.height == 0


def test_constants_preserve_blocker_first_policy() -> None:
    assert raw_metadata.BLOCKED_GATE4_GATE5 == "blocked_gate4_gate5"
    assert raw_metadata.NO_BIOLOGICAL_CLAIMS_POLICY == "no_biological_claims_until_validation"
    assert raw_metadata.REPAIR_WORKLIST_CLAIM_STATUS == "repair_worklist"
    assert raw_metadata.BIOLOGICAL_CLAIM_STATUS_NONE == "no_biological_claim"


def test_required_columns_are_present_in_committed_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    assert raw_metadata.missing_required_columns(rows) == []
    raw_metadata.validate_required_columns(rows)


def test_validate_required_columns_rejects_missing_column() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows().drop("biological_claim_status")

    with pytest.raises(ValueError, match="missing required columns"):
        raw_metadata.validate_required_columns(rows)


def test_validate_allowed_values_accepts_empty_committed_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    raw_metadata.validate_allowed_values(rows)


def test_validate_allowed_values_accepts_valid_future_raw_metadata_row() -> None:
    rows = valid_raw_metadata_response_rows()

    raw_metadata.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_accepted_ortholog_status() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("accepted_ortholog").alias("raw_metadata_response_status")
    )

    with pytest.raises(ValueError, match="invalid values in raw_metadata_response_status"):
        raw_metadata.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_downstream_block_status() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("gate8_ready").alias("downstream_block_status_after_raw_metadata")
    )

    with pytest.raises(
        ValueError,
        match="invalid values in downstream_block_status_after_raw_metadata",
    ):
        raw_metadata.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_biological_claim_status() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("biological_claim").alias("biological_claim_status")
    )

    with pytest.raises(ValueError, match="invalid values in biological_claim_status"):
        raw_metadata.validate_allowed_values(rows)


def test_validate_false_only_columns_accepts_empty_committed_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    raw_metadata.validate_false_only_columns(rows)


def test_validate_false_only_columns_accepts_valid_future_row() -> None:
    rows = valid_raw_metadata_response_rows()

    raw_metadata.validate_false_only_columns(rows)


def test_validate_false_only_columns_rejects_sequence_fetch() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(pl.lit("true").alias("sequence_fetched"))

    with pytest.raises(ValueError, match="must remain false"):
        raw_metadata.validate_false_only_columns(rows)


def test_validate_false_only_columns_rejects_source_evidence_creation() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("true").alias("source_evidence_created")
    )

    with pytest.raises(ValueError, match="must remain false"):
        raw_metadata.validate_false_only_columns(rows)


def test_validate_false_only_columns_rejects_gate8_promotion() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(pl.lit("true").alias("gate8_promoted"))

    with pytest.raises(ValueError, match="must remain false"):
        raw_metadata.validate_false_only_columns(rows)


def test_forbidden_actions_present_accepts_valid_future_raw_metadata_row() -> None:
    row = valid_raw_metadata_response_row()

    assert raw_metadata.forbidden_actions_present(row)


def test_validate_required_forbidden_actions_accepts_empty_committed_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    raw_metadata.validate_required_forbidden_actions(rows)


def test_validate_required_forbidden_actions_rejects_missing_actions() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("ortholog acceptance").alias("forbidden_actions_after_raw_metadata")
    )

    with pytest.raises(ValueError, match="missing required forbidden actions"):
        raw_metadata.validate_required_forbidden_actions(rows)


def test_validate_no_duplicate_raw_metadata_response_keys_accepts_empty_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    raw_metadata.validate_no_duplicate_raw_metadata_response_keys(rows)


def test_validate_no_duplicate_raw_metadata_response_keys_rejects_duplicate_row() -> None:
    rows = valid_raw_metadata_response_rows()
    duplicate_rows = pl.concat([rows, rows])

    with pytest.raises(ValueError, match="duplicate raw metadata response keys"):
        raw_metadata.validate_no_duplicate_raw_metadata_response_keys(duplicate_rows)


def test_validate_no_blank_required_fields_accepts_empty_committed_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    raw_metadata.validate_no_blank_required_fields(rows)


def test_validate_no_blank_required_fields_rejects_blank_required_value() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(pl.lit("").alias("raw_metadata_summary"))

    with pytest.raises(ValueError, match="blank required fields"):
        raw_metadata.validate_no_blank_required_fields(rows)


def test_validate_target_sequence_length_accepts_empty_committed_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    raw_metadata.validate_target_sequence_length(rows)


def test_validate_target_sequence_length_accepts_unresolved() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("unresolved").alias("target_sequence_length")
    )

    raw_metadata.validate_target_sequence_length(rows)


def test_validate_target_sequence_length_rejects_non_positive_length() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("0").alias("target_sequence_length")
    )

    with pytest.raises(ValueError, match="invalid target_sequence_length"):
        raw_metadata.validate_target_sequence_length(rows)


def test_validate_no_disallowed_claim_values_accepts_empty_committed_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    raw_metadata.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_gate8_claim() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("Gate 8 eligible").alias("claim_status_after_raw_metadata")
    )

    with pytest.raises(ValueError, match="disallowed claim values"):
        raw_metadata.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_validated_claim_in_summary() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("validated_ortholog").alias("raw_metadata_summary")
    )

    with pytest.raises(ValueError, match="disallowed claim values"):
        raw_metadata.validate_no_disallowed_claim_values(rows)


def test_validate_stronger_source_raw_metadata_response_rows_accepts_empty_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    raw_metadata.validate_stronger_source_raw_metadata_response_rows(rows)


def test_validate_stronger_source_raw_metadata_response_rows_accepts_valid_future_row() -> None:
    rows = valid_raw_metadata_response_rows()

    raw_metadata.validate_stronger_source_raw_metadata_response_rows(rows)


def test_validate_stronger_source_raw_metadata_response_rows_rejects_downstream_claim() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("validated_ortholog").alias("claim_status_after_raw_metadata")
    )

    with pytest.raises(ValueError, match="invalid values|disallowed claim values"):
        raw_metadata.validate_stronger_source_raw_metadata_response_rows(rows)


def test_validate_stronger_source_raw_metadata_response_rows_rejects_reviewed_decision() -> None:
    rows = valid_raw_metadata_response_rows().with_columns(
        pl.lit("true").alias("reviewed_decision_created")
    )

    with pytest.raises(ValueError, match="must remain false"):
        raw_metadata.validate_stronger_source_raw_metadata_response_rows(rows)
