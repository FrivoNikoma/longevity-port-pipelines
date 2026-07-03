from __future__ import annotations

import inspect
from collections.abc import Mapping

import polars as pl

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_lookup_policy as live_policy,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_metadata_client as live_client,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_metadata_dry_run as dry_run,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_lookup_plan as lookup_plan,
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
        "reviewer_note": "Dry-run wrapper test row; remains blocked and non-reviewed.",
    }
    row.update(overrides)
    return row


def lookup_plan_rows(*rows: dict[str, object]) -> pl.DataFrame:
    return pl.DataFrame(list(rows)).select(list(lookup_plan.REQUIRED_COLUMNS))


def provider_should_not_be_called(
    request: live_client.LiveMetadataLookupRequest,
) -> Mapping[str, object]:
    raise AssertionError(f"provider should not be called: {request}")


def row0(frame: pl.DataFrame) -> dict[str, object]:
    return frame.row(0, named=True)


def assert_guardrails_remain_blocked(row: Mapping[str, object]) -> None:
    assert row["sequence_fetch_authorized"] == "false"
    assert row["sequence_included"] == "false"
    assert row["persistence_written"] == "false"
    assert row["source_evidence_created"] == "false"
    assert row["evidence_row_created"] == "false"
    assert row["reviewed_decision_created"] == "false"
    assert row["gate4_gate5_policy_updated"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"
    assert row["downstream_block_status"] == lookup_plan.BLOCKED_GATE4_GATE5
    assert row["claim_status"] == lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS
    assert row["biological_claim_status"] == dry_run.BIOLOGICAL_CLAIM_STATUS_NONE


def test_empty_live_metadata_dry_run_summary_preserves_schema() -> None:
    summary = dry_run.empty_live_metadata_dry_run_summary()

    assert summary.is_empty()
    assert summary.columns == list(dry_run.DRY_RUN_SUMMARY_COLUMNS)


def test_default_denied_does_not_call_provider() -> None:
    summary = dry_run.build_live_metadata_dry_run_summary(
        lookup_plan_rows(lookup_plan_row()),
        provider=provider_should_not_be_called,
    )

    assert summary.height == 1
    result = row0(summary)

    assert result["live_lookup_policy_decision"] == live_policy.DECISION_DENIED_DEFAULT_NO_OPT_IN
    assert result["live_lookup_authorized"] == "false"
    assert result["live_metadata_provider_called"] == "false"
    assert result["dry_run_status"] == dry_run.DRY_RUN_STATUS_SKIPPED_POLICY_DENIED
    assert_guardrails_remain_blocked(result)


def test_ci_denied_does_not_call_provider() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        running_in_ci=True,
        sequence_fetch_requested=False,
        operator_acknowledged_blockers=True,
    )

    summary = dry_run.build_live_metadata_dry_run_summary(
        lookup_plan_rows(lookup_plan_row()),
        context=context,
        provider=provider_should_not_be_called,
    )
    result = row0(summary)

    assert result["live_lookup_policy_decision"] == live_policy.DECISION_DENIED_CI
    assert result["runtime_running_in_ci"] == "true"
    assert result["live_metadata_provider_called"] == "false"
    assert_guardrails_remain_blocked(result)


def test_sequence_fetch_requested_does_not_call_provider() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        running_in_ci=False,
        sequence_fetch_requested=True,
        operator_acknowledged_blockers=True,
    )

    summary = dry_run.build_live_metadata_dry_run_summary(
        lookup_plan_rows(lookup_plan_row()),
        context=context,
        provider=provider_should_not_be_called,
    )
    result = row0(summary)

    assert result["live_lookup_policy_decision"] == live_policy.DECISION_DENIED_SEQUENCE_FETCH
    assert result["runtime_sequence_fetch_requested"] == "true"
    assert result["live_metadata_provider_called"] == "false"
    assert_guardrails_remain_blocked(result)


def test_missing_blocker_acknowledgement_does_not_call_provider() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        running_in_ci=False,
        sequence_fetch_requested=False,
        operator_acknowledged_blockers=False,
    )

    summary = dry_run.build_live_metadata_dry_run_summary(
        lookup_plan_rows(lookup_plan_row()),
        context=context,
        provider=provider_should_not_be_called,
    )
    result = row0(summary)

    assert result["live_lookup_policy_decision"] == live_policy.DECISION_DENIED_MISSING_BLOCKER_ACK
    assert result["runtime_operator_acknowledged_blockers"] == "false"
    assert result["live_metadata_provider_called"] == "false"
    assert_guardrails_remain_blocked(result)


def test_authorized_context_calls_only_injected_provider_once() -> None:
    calls: list[live_client.LiveMetadataLookupRequest] = []

    def fake_provider(
        request: live_client.LiveMetadataLookupRequest,
    ) -> Mapping[str, object]:
        calls.append(request)
        return {"raw_metadata_status": "raw_metadata_fake_provider_unreviewed"}

    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        running_in_ci=False,
        sequence_fetch_requested=False,
        operator_acknowledged_blockers=True,
    )

    summary = dry_run.build_live_metadata_dry_run_summary(
        lookup_plan_rows(lookup_plan_row()),
        context=context,
        provider=fake_provider,
    )
    result = row0(summary)

    assert len(calls) == 1
    assert calls[0].candidate_set == "tp53_mdm2_elephant"
    assert calls[0].candidate_id == "mdm2_elephant_G3SX30"
    assert calls[0].planned_lookup_query_identifier == "G3SX30"

    assert result["live_lookup_policy_decision"] == live_policy.DECISION_AUTHORIZED_STILL_BLOCKED
    assert result["live_lookup_authorized"] == "true"
    assert result["live_metadata_provider_called"] == "true"
    assert result["raw_metadata_status"] == "raw_metadata_fake_provider_unreviewed"
    assert result["dry_run_status"] == dry_run.DRY_RUN_STATUS_RAW_METADATA_CANDIDATE
    assert result["dry_run_provider_mode"] == dry_run.PROVIDER_MODE_INJECTED_FAKE_OR_NOOP_ONLY
    assert_guardrails_remain_blocked(result)


def test_authorized_result_remains_raw_metadata_dry_run_only() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        running_in_ci=False,
        sequence_fetch_requested=False,
        operator_acknowledged_blockers=True,
    )

    summary = dry_run.build_live_metadata_dry_run_summary(
        lookup_plan_rows(lookup_plan_row()),
        context=context,
    )
    result = row0(summary)

    assert result["live_metadata_provider_called"] == "true"
    assert result["raw_metadata_status"] == dry_run.RAW_METADATA_STATUS_DRY_RUN_NOOP_UNREVIEWED
    assert result["dry_run_status"] == dry_run.DRY_RUN_STATUS_RAW_METADATA_CANDIDATE
    assert "raw metadata dry-run output only" in str(result["dry_run_note"])
    assert_guardrails_remain_blocked(result)


def test_dry_run_status_counts() -> None:
    denied = dry_run.build_live_metadata_dry_run_summary(
        lookup_plan_rows(lookup_plan_row()),
        provider=provider_should_not_be_called,
    )

    counts = dry_run.dry_run_status_counts(denied)

    assert counts == {dry_run.DRY_RUN_STATUS_SKIPPED_POLICY_DENIED: 1}


def test_live_metadata_dry_run_module_does_not_import_network_libraries() -> None:
    source = inspect.getsource(dry_run)

    forbidden_terms = (
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import urllib",
        "from urllib",
        "import socket",
        "from socket",
        "requests.get",
        "httpx.get",
        "socket.",
    )

    for term in forbidden_terms:
        assert term not in source


def test_live_metadata_dry_run_module_does_not_encode_persistence_or_downstream_actions() -> None:
    source = inspect.getsource(dry_run)

    forbidden_terms = (
        "write_csv",
        "read_csv",
        "write_parquet",
        "read_parquet",
        "open(",
        "accepted_ortholog",
        "validated_ortholog",
        "safe_to_port",
        "eligible_for_gate8",
        "eligible_for_gate9",
        "source_evidence_row_created",
        "reviewed_ortholog_decision_created",
    )

    for term in forbidden_terms:
        assert term not in source
