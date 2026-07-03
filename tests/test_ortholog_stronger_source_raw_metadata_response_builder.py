from __future__ import annotations

from collections.abc import Mapping

import polars as pl
import pytest

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_lookup_policy as live_policy,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_metadata_dry_run as dry_run,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_lookup_plan as lookup_plan,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_raw_metadata_response as raw_metadata,
)


def lookup_plan_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2",
        "candidate_id": "mdm2_elephant_G3SX30",
        "request_table": "data/input/ortholog_stronger_source_evidence_requests.csv",
        "request_source_row_index": "0",
        "gene_symbol": "MDM2",
        "source_species": "human",
        "target_species": "elephant",
        "target_species_taxid": "9785",
        "source_uniprot": "Q00987",
        "partner_uniprot": "P04637",
        "requested_evidence_source_database": "UniProt",
        "requested_evidence_source_accession": "G3SX30",
        "target_taxid": "9785",
        "target_species_name": "Loxodonta africana",
        "target_gene_symbol": "MDM2",
        "target_protein_accession": "G3SX30",
        "target_sequence_length": "491",
        "planned_lookup_source_type": "reviewed_uniprot",
        "planned_lookup_source_name": "UniProt reviewed record",
        "planned_lookup_query_identifier": "G3SX30",
        "planned_lookup_query_taxid": "9785",
        "planned_lookup_mode": live_policy.EXPLICIT_LIVE_LOOKUP_MODE,
        "live_lookup_allowed": "false",
        "sequence_fetch_allowed": "false",
        "planned_output_target": lookup_plan.DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET,
        "lookup_plan_status": "lookup_planned_still_blocked",
        "downstream_block_status_after_lookup_plan": lookup_plan.BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_lookup_plan": "add_manual_source_evidence_row_later",
        "claim_policy_after_lookup_plan": lookup_plan.NO_BIOLOGICAL_CLAIMS_POLICY,
        "claim_status_after_lookup_plan": lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS,
        "forbidden_actions_after_lookup_plan": "; ".join(sorted(lookup_plan.RUNTIME_SIDE_EFFECTS)),
        "reviewer_note": "Raw metadata response builder test row; remains blocked.",
    }
    row.update(overrides)
    return row


def lookup_plan_rows(*rows: dict[str, object]) -> pl.DataFrame:
    if not rows:
        return pl.DataFrame(schema={column: pl.String for column in lookup_plan.REQUIRED_COLUMNS})

    return pl.DataFrame(list(rows)).select(list(lookup_plan.REQUIRED_COLUMNS))


def authorized_dry_run_summary(plan_rows: pl.DataFrame) -> pl.DataFrame:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        running_in_ci=False,
        sequence_fetch_requested=False,
        operator_acknowledged_blockers=True,
    )

    return dry_run.build_live_metadata_dry_run_summary(
        plan_rows,
        context=context,
    )


def row0(frame: pl.DataFrame) -> dict[str, object]:
    return frame.row(0, named=True)


def assert_raw_metadata_guardrails(row: Mapping[str, object]) -> None:
    assert row["sequence_fetched"] == "false"
    assert row["source_evidence_created"] == "false"
    assert row["reviewed_decision_created"] == "false"
    assert row["gate4_gate5_policy_updated"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"
    assert row["downstream_block_status_after_raw_metadata"] == raw_metadata.BLOCKED_GATE4_GATE5
    assert row["claim_policy_after_raw_metadata"] == raw_metadata.NO_BIOLOGICAL_CLAIMS_POLICY
    assert row["claim_status_after_raw_metadata"] == raw_metadata.REPAIR_WORKLIST_CLAIM_STATUS
    assert row["biological_claim_status"] == raw_metadata.BIOLOGICAL_CLAIM_STATUS_NONE
    assert raw_metadata.forbidden_actions_present(dict(row))


def test_empty_raw_metadata_response_rows_preserves_schema() -> None:
    rows = raw_metadata.empty_raw_metadata_response_rows()

    assert rows.is_empty()
    assert rows.columns == list(raw_metadata.REQUIRED_COLUMNS)


def test_empty_dry_run_summary_returns_empty_response_frame() -> None:
    rows = raw_metadata.build_raw_metadata_response_rows_from_dry_run_summary(
        lookup_plan_rows=lookup_plan_rows(),
        dry_run_summary_rows=dry_run.empty_live_metadata_dry_run_summary(),
    )

    assert rows.is_empty()
    assert rows.columns == list(raw_metadata.REQUIRED_COLUMNS)
    raw_metadata.validate_stronger_source_raw_metadata_response_rows(rows)


def test_policy_denied_dry_run_summary_is_skipped() -> None:
    plan_rows = lookup_plan_rows(lookup_plan_row())
    summary = dry_run.build_live_metadata_dry_run_summary(plan_rows)

    rows = raw_metadata.build_raw_metadata_response_rows_from_dry_run_summary(
        lookup_plan_rows=plan_rows,
        dry_run_summary_rows=summary,
    )

    assert rows.is_empty()
    assert rows.columns == list(raw_metadata.REQUIRED_COLUMNS)
    raw_metadata.validate_stronger_source_raw_metadata_response_rows(rows)


def test_candidate_dry_run_summary_maps_to_valid_raw_metadata_response_row() -> None:
    plan_rows = lookup_plan_rows(lookup_plan_row())
    summary = authorized_dry_run_summary(plan_rows)

    rows = raw_metadata.build_raw_metadata_response_rows_from_dry_run_summary(
        lookup_plan_rows=plan_rows,
        dry_run_summary_rows=summary,
    )

    assert rows.height == 1
    assert rows.columns == list(raw_metadata.REQUIRED_COLUMNS)

    result = row0(rows)
    assert result["candidate_set"] == "tp53_mdm2_elephant"
    assert result["candidate_id"] == "mdm2_elephant_G3SX30"
    assert result["request_table"] == "data/input/ortholog_stronger_source_evidence_requests.csv"
    assert result["planned_lookup_source_type"] == "reviewed_uniprot"
    assert result["planned_lookup_query_identifier"] == "G3SX30"
    assert result["live_lookup_policy_decision"] == live_policy.DECISION_AUTHORIZED_STILL_BLOCKED
    assert result["dry_run_status"] == dry_run.DRY_RUN_STATUS_RAW_METADATA_CANDIDATE
    assert result["raw_metadata_status"] == dry_run.RAW_METADATA_STATUS_DRY_RUN_NOOP_UNREVIEWED
    assert (
        result["raw_metadata_response_status"] == "raw_metadata_received_unreviewed_still_blocked"
    )
    assert result["raw_metadata_review_status"] == "unreviewed_raw_metadata"
    assert result["raw_metadata_source_type"] == "injected_fake_or_noop_provider"

    assert_raw_metadata_guardrails(result)
    raw_metadata.validate_stronger_source_raw_metadata_response_rows(rows)


def test_builder_rejects_unmatched_candidate_dry_run_summary_row() -> None:
    plan_rows = lookup_plan_rows(lookup_plan_row())
    summary = authorized_dry_run_summary(plan_rows).with_columns(
        pl.lit("different_candidate").alias("candidate_id")
    )

    with pytest.raises(ValueError, match="Could not match every raw metadata candidate"):
        raw_metadata.build_raw_metadata_response_rows_from_dry_run_summary(
            lookup_plan_rows=plan_rows,
            dry_run_summary_rows=summary,
        )
