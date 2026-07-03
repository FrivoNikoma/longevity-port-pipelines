from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_evidence_collection as collection,
)


def valid_collection_row() -> dict[str, str]:
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
        "collected_source_type": "other_manual_source",
        "collected_source_name": "manual_source_placeholder",
        "collected_source_identifier": "manual_source_placeholder",
        "collected_source_review_status": "unreviewed_manual_source_record",
        "collected_evidence_summary": "manual source evidence recorded for validator test only",
        "collection_status": "manual_collection_complete_still_blocked",
        "collection_decision": "evidence_recorded_for_later_intake_pr",
        "downstream_block_status_after_collection": "blocked_gate4_gate5",
        "allowed_next_action_after_collection": "review_collected_source_evidence",
        "claim_policy_after_collection": "no_biological_claims_until_validation",
        "claim_status_after_collection": "repair_worklist",
        "forbidden_actions_after_collection": (
            "ortholog acceptance; reviewed decision creation; "
            "Gate 4 or Gate 5 policy update; sequence fetch; "
            "external database query; Biohub call; embedding generation; "
            "Boltz call; AF3 call; Chai call; enrichment rerun; contrast rerun; "
            "Gate 8 promotion; Gate 9 promotion; biological claim"
        ),
        "reviewer_note": "Synthetic validator test row only; no source evidence committed.",
    }


def valid_collection_rows() -> pl.DataFrame:
    return pl.DataFrame([valid_collection_row()])


def test_collection_reader_loads_committed_header_only_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    assert rows.height == 0
    assert rows.columns == list(collection.REQUIRED_COLUMNS)


def test_default_path_points_to_committed_collection_table() -> None:
    assert (
        Path("data/input/ortholog_stronger_source_evidence_collection.csv")
        == collection.DEFAULT_STRONGER_SOURCE_COLLECTION_PATH
    )


def test_pending_manual_collection_helper_accepts_empty_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()
    pending_rows = collection.pending_manual_collection_rows(rows)

    assert pending_rows.height == 0


def test_constants_preserve_blocker_first_policy() -> None:
    assert collection.BLOCKED_GATE4_GATE5 == "blocked_gate4_gate5"
    assert collection.NO_BIOLOGICAL_CLAIMS_POLICY == "no_biological_claims_until_validation"
    assert collection.REPAIR_WORKLIST_CLAIM_STATUS == "repair_worklist"


def test_required_columns_are_present_in_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    assert collection.missing_required_columns(rows) == []
    collection.validate_required_columns(rows)


def test_validate_required_columns_rejects_missing_column() -> None:
    rows = collection.read_stronger_source_collection_rows().drop("claim_status_after_collection")

    with pytest.raises(ValueError, match="missing required columns"):
        collection.validate_required_columns(rows)


def test_validate_allowed_values_accepts_empty_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    collection.validate_allowed_values(rows)


def test_validate_allowed_values_accepts_valid_future_collection_row() -> None:
    rows = valid_collection_rows()

    collection.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_invalid_collection_status() -> None:
    rows = valid_collection_rows().with_columns(
        pl.lit("accepted_ortholog").alias("collection_status")
    )

    with pytest.raises(ValueError, match="invalid values in collection_status"):
        collection.validate_allowed_values(rows)


def test_forbidden_actions_present_accepts_valid_future_collection_row() -> None:
    row = valid_collection_row()

    assert collection.forbidden_actions_present(row)


def test_validate_required_forbidden_actions_accepts_empty_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    collection.validate_required_forbidden_actions(rows)


def test_validate_required_forbidden_actions_rejects_missing_actions() -> None:
    rows = valid_collection_rows().with_columns(
        pl.lit("ortholog acceptance").alias("forbidden_actions_after_collection")
    )

    with pytest.raises(ValueError, match="missing required forbidden actions"):
        collection.validate_required_forbidden_actions(rows)


def test_validate_no_duplicate_collection_keys_accepts_empty_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    collection.validate_no_duplicate_collection_keys(rows)


def test_validate_no_duplicate_collection_keys_rejects_duplicate_row() -> None:
    rows = valid_collection_rows()
    duplicate_rows = pl.concat([rows, rows])

    with pytest.raises(ValueError, match="duplicate collection keys"):
        collection.validate_no_duplicate_collection_keys(duplicate_rows)


def test_validate_no_blank_required_fields_accepts_empty_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    collection.validate_no_blank_required_fields(rows)


def test_validate_no_blank_required_fields_rejects_blank_required_value() -> None:
    rows = valid_collection_rows().with_columns(pl.lit("").alias("collected_evidence_summary"))

    with pytest.raises(ValueError, match="blank required fields"):
        collection.validate_no_blank_required_fields(rows)


def test_validate_target_sequence_length_accepts_empty_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    collection.validate_target_sequence_length(rows)


def test_validate_target_sequence_length_accepts_unresolved() -> None:
    rows = valid_collection_rows().with_columns(
        pl.lit("unresolved").alias("target_sequence_length")
    )

    collection.validate_target_sequence_length(rows)


def test_validate_target_sequence_length_rejects_non_positive_length() -> None:
    rows = valid_collection_rows().with_columns(pl.lit("0").alias("target_sequence_length"))

    with pytest.raises(ValueError, match="invalid target_sequence_length"):
        collection.validate_target_sequence_length(rows)


def test_validate_no_disallowed_claim_values_accepts_empty_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    collection.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_gate8_claim() -> None:
    rows = valid_collection_rows().with_columns(
        pl.lit("Gate 8 eligible").alias("claim_status_after_collection")
    )

    with pytest.raises(ValueError, match="disallowed claim values"):
        collection.validate_no_disallowed_claim_values(rows)


def test_validate_stronger_source_collection_rows_accepts_empty_committed_table() -> None:
    rows = collection.read_stronger_source_collection_rows()

    collection.validate_stronger_source_collection_rows(rows)


def test_validate_stronger_source_collection_rows_accepts_valid_future_row() -> None:
    rows = valid_collection_rows()

    collection.validate_stronger_source_collection_rows(rows)


def test_validate_stronger_source_collection_rows_rejects_downstream_claim() -> None:
    rows = valid_collection_rows().with_columns(
        pl.lit("validated_ortholog").alias("claim_status_after_collection")
    )

    with pytest.raises(ValueError, match="invalid values|disallowed claim values"):
        collection.validate_stronger_source_collection_rows(rows)
