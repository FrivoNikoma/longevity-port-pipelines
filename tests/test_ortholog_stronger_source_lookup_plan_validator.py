from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_lookup_plan as lookup_plan,
)


def valid_lookup_plan_row() -> dict[str, str]:
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
        "planned_lookup_source_type": "uniprot_entry_metadata",
        "planned_lookup_source_name": "UniProtKB entry metadata lookup",
        "planned_lookup_query_identifier": "G3SX30",
        "planned_lookup_query_taxid": "9785",
        "planned_lookup_mode": "explicit_live_opt_in_required",
        "live_lookup_allowed": "false",
        "sequence_fetch_allowed": "false",
        "planned_output_target": ("data/input/ortholog_stronger_source_raw_metadata_responses.csv"),
        "lookup_plan_status": "lookup_planned_still_blocked",
        "downstream_block_status_after_lookup_plan": "blocked_gate4_gate5",
        "allowed_next_action_after_lookup_plan": "add_raw_metadata_response_sandbox_row_later",
        "claim_policy_after_lookup_plan": "no_biological_claims_until_validation",
        "claim_status_after_lookup_plan": "repair_worklist",
        "forbidden_actions_after_lookup_plan": (
            "live external database lookup; source evidence collection; "
            "ortholog acceptance; curated ortholog candidate creation; "
            "standard ortholog coverage population; reviewed decision creation; "
            "Gate 4 or Gate 5 policy update; sequence fetch; Biohub call; "
            "embedding generation; Boltz call; AF3 call; Chai call; "
            "enrichment rerun; contrast rerun; Gate 8 promotion; "
            "Gate 9 promotion; biological claim"
        ),
        "reviewer_note": "Synthetic validator test row only; no lookup or evidence committed.",
    }


def valid_lookup_plan_rows() -> pl.DataFrame:
    return pl.DataFrame([valid_lookup_plan_row()])


def test_lookup_plan_reader_loads_committed_g3sx30_lookup_plan_row() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    assert rows.height == 1
    assert rows.columns == list(lookup_plan.REQUIRED_COLUMNS)
    assert rows.item(0, "candidate_id") == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert rows.item(0, "planned_lookup_query_identifier") == "G3SX30"


def test_default_path_points_to_committed_lookup_plan_table() -> None:
    assert (
        Path("data/input/ortholog_stronger_source_lookup_plan.csv")
        == lookup_plan.DEFAULT_STRONGER_SOURCE_LOOKUP_PLAN_PATH
    )


def test_default_output_target_points_to_raw_metadata_response_table() -> None:
    assert lookup_plan.DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET == (
        "data/input/ortholog_stronger_source_raw_metadata_responses.csv"
    )


def test_planned_lookup_helper_returns_committed_g3sx30_row() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()
    planned_rows = lookup_plan.planned_lookup_rows(rows)

    assert planned_rows.height == 1
    assert planned_rows.item(0, "planned_lookup_query_identifier") == "G3SX30"


def test_constants_preserve_blocker_first_policy() -> None:
    assert lookup_plan.BLOCKED_GATE4_GATE5 == "blocked_gate4_gate5"
    assert lookup_plan.NO_BIOLOGICAL_CLAIMS_POLICY == ("no_biological_claims_until_validation")
    assert lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS == "repair_worklist"


def test_required_columns_are_present_in_committed_table() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    assert lookup_plan.missing_required_columns(rows) == []
    lookup_plan.validate_required_columns(rows)


def test_validate_required_columns_rejects_missing_column() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows().drop(
        "claim_status_after_lookup_plan"
    )

    with pytest.raises(ValueError, match="missing required columns"):
        lookup_plan.validate_required_columns(rows)


def test_validate_allowed_values_accepts_empty_committed_table() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    lookup_plan.validate_allowed_values(rows)


def test_validate_allowed_values_accepts_valid_future_lookup_plan_row() -> None:
    rows = valid_lookup_plan_rows()

    lookup_plan.validate_allowed_values(rows)


def test_validate_allowed_values_accepts_raw_metadata_sandbox_next_action() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("add_raw_metadata_response_sandbox_row_later").alias(
            "allowed_next_action_after_lookup_plan"
        )
    )

    lookup_plan.validate_allowed_values(rows)


def test_validate_allowed_values_still_accepts_reviewed_uniprot_future_source_type() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("reviewed_uniprot").alias("planned_lookup_source_type")
    )

    lookup_plan.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_live_lookup_true() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("true").alias("live_lookup_allowed"))

    with pytest.raises(ValueError, match="invalid values in live_lookup_allowed"):
        lookup_plan.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_sequence_fetch_true() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("true").alias("sequence_fetch_allowed"))

    with pytest.raises(ValueError, match="invalid values in sequence_fetch_allowed"):
        lookup_plan.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_wrong_output_target() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("data/output/unsafe.csv").alias("planned_output_target")
    )

    with pytest.raises(ValueError, match="invalid values in planned_output_target"):
        lookup_plan.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_gate8_status() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("Gate 8 eligible").alias("downstream_block_status_after_lookup_plan")
    )

    with pytest.raises(
        ValueError,
        match="invalid values in downstream_block_status_after_lookup_plan",
    ):
        lookup_plan.validate_allowed_values(rows)


def test_forbidden_actions_present_accepts_valid_future_lookup_plan_row() -> None:
    row = valid_lookup_plan_row()

    assert lookup_plan.forbidden_actions_present(row)


def test_validate_required_forbidden_actions_accepts_empty_committed_table() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    lookup_plan.validate_required_forbidden_actions(rows)


def test_validate_required_forbidden_actions_rejects_missing_actions() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("ortholog acceptance").alias("forbidden_actions_after_lookup_plan")
    )

    with pytest.raises(ValueError, match="missing required forbidden actions"):
        lookup_plan.validate_required_forbidden_actions(rows)


def test_validate_no_duplicate_lookup_plan_keys_accepts_empty_committed_table() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    lookup_plan.validate_no_duplicate_lookup_plan_keys(rows)


def test_validate_no_duplicate_lookup_plan_keys_rejects_duplicate_row() -> None:
    rows = valid_lookup_plan_rows()
    duplicate_rows = pl.concat([rows, rows])

    with pytest.raises(ValueError, match="duplicate lookup plan keys"):
        lookup_plan.validate_no_duplicate_lookup_plan_keys(duplicate_rows)


def test_validate_no_blank_required_fields_accepts_empty_committed_table() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    lookup_plan.validate_no_blank_required_fields(rows)


def test_validate_no_blank_required_fields_rejects_blank_required_value() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("").alias("planned_lookup_source_name"))

    with pytest.raises(ValueError, match="blank required fields"):
        lookup_plan.validate_no_blank_required_fields(rows)


def test_validate_positive_integer_fields_accepts_empty_committed_table() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    lookup_plan.validate_positive_integer_fields(rows)


def test_validate_positive_integer_fields_accepts_unresolved_sequence_length() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("unresolved").alias("target_sequence_length")
    )

    lookup_plan.validate_positive_integer_fields(rows)


def test_validate_positive_integer_fields_rejects_bad_taxid() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("0").alias("planned_lookup_query_taxid"))

    with pytest.raises(ValueError, match="invalid positive-integer metadata"):
        lookup_plan.validate_positive_integer_fields(rows)


def test_validate_no_disallowed_claim_values_accepts_empty_committed_table() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    lookup_plan.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_accepted_ortholog() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("accepted_ortholog").alias("claim_status_after_lookup_plan")
    )

    with pytest.raises(ValueError, match="disallowed claim values|invalid values"):
        lookup_plan.validate_stronger_source_lookup_plan_rows(rows)


def test_validate_no_disallowed_claim_values_rejects_validated_ortholog() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("validated_ortholog").alias("reviewer_note")
    )

    with pytest.raises(ValueError, match="disallowed claim values"):
        lookup_plan.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_biohub_ready() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("Biohub ready").alias("reviewer_note"))

    with pytest.raises(ValueError, match="disallowed claim values"):
        lookup_plan.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_embedding_ready() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("embedding ready").alias("reviewer_note"))

    with pytest.raises(ValueError, match="disallowed claim values"):
        lookup_plan.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_boltz_ready() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("Boltz ready").alias("reviewer_note"))

    with pytest.raises(ValueError, match="disallowed claim values"):
        lookup_plan.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_af3_ready() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("AF3 ready").alias("reviewer_note"))

    with pytest.raises(ValueError, match="disallowed claim values"):
        lookup_plan.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_chai_ready() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("Chai ready").alias("reviewer_note"))

    with pytest.raises(ValueError, match="disallowed claim values"):
        lookup_plan.validate_no_disallowed_claim_values(rows)


def test_validate_no_disallowed_claim_values_rejects_safe_to_port() -> None:
    rows = valid_lookup_plan_rows().with_columns(pl.lit("safe_to_port").alias("reviewer_note"))

    with pytest.raises(ValueError, match="disallowed claim values"):
        lookup_plan.validate_no_disallowed_claim_values(rows)


def test_validate_stronger_source_lookup_plan_rows_accepts_empty_committed_table() -> None:
    rows = lookup_plan.read_stronger_source_lookup_plan_rows()

    lookup_plan.validate_stronger_source_lookup_plan_rows(rows)


def test_validate_stronger_source_lookup_plan_rows_accepts_valid_future_row() -> None:
    rows = valid_lookup_plan_rows()

    lookup_plan.validate_stronger_source_lookup_plan_rows(rows)


def test_validate_stronger_source_lookup_plan_rows_rejects_gate_policy_update() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("Gate 4 / Gate 5 policy update").alias("allowed_next_action_after_lookup_plan")
    )

    with pytest.raises(ValueError, match="invalid values|disallowed claim values"):
        lookup_plan.validate_stronger_source_lookup_plan_rows(rows)


def test_validate_stronger_source_lookup_plan_rows_rejects_reviewed_decision_creation() -> None:
    rows = valid_lookup_plan_rows().with_columns(
        pl.lit("reviewed decision creation").alias("allowed_next_action_after_lookup_plan")
    )

    with pytest.raises(ValueError, match="invalid values|disallowed claim values"):
        lookup_plan.validate_stronger_source_lookup_plan_rows(rows)
