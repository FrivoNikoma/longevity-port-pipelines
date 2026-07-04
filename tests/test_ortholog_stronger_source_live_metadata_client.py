from __future__ import annotations

from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_lookup_policy as live_policy,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_metadata_client as live_client,
)


def explicit_live_plan_row() -> dict[str, str]:
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
        "planned_output_target": "data/input/ortholog_stronger_source_raw_metadata_responses.csv",
        "lookup_plan_status": "lookup_planned_still_blocked",
        "downstream_block_status_after_lookup_plan": "blocked_gate4_gate5",
        "allowed_next_action_after_lookup_plan": "keep_blocked",
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
        "reviewer_note": "Synthetic live metadata client test row; still blocked.",
    }


def policy_row(
    context: live_policy.LiveLookupOptInContext | None = None,
) -> dict[str, str]:
    return live_policy.evaluate_live_lookup_opt_in_for_plan_row(
        explicit_live_plan_row(),
        context,
    )


def authorized_policy_row() -> dict[str, str]:
    return policy_row(
        live_policy.LiveLookupOptInContext(
            explicit_live_opt_in=True,
            operator_acknowledged_blockers=True,
        )
    )


def denied_policy_row() -> dict[str, str]:
    return policy_row()


def provider_must_not_be_called(
    request: live_client.LiveMetadataLookupRequest,
) -> dict[str, str]:
    raise AssertionError(f"provider should not have been called: {request}")


def test_empty_live_metadata_lookup_rows_preserves_schema() -> None:
    rows = live_client.empty_live_metadata_lookup_rows()

    assert rows.height == 0
    assert rows.columns == list(live_client.RESULT_COLUMNS)


def test_request_from_policy_row_preserves_request_identity() -> None:
    request = live_client.request_from_policy_row(authorized_policy_row())

    assert request.candidate_set == "tp53_mdm2_elephant"
    assert request.candidate_id == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert request.planned_lookup_source_type == "uniprot_entry_metadata"
    assert request.planned_lookup_query_identifier == "G3SX30"
    assert request.live_lookup_policy_decision == (live_policy.DECISION_AUTHORIZED_STILL_BLOCKED)


def test_denied_policy_row_does_not_call_provider() -> None:
    result = live_client.run_live_metadata_lookup_for_policy_row(
        denied_policy_row(),
        provider_must_not_be_called,
    )

    assert result["live_metadata_lookup_status"] == (
        live_client.LOOKUP_STATUS_SKIPPED_POLICY_DENIED
    )
    assert result["provider_called"] == "false"
    assert result["raw_metadata_status"] == live_client.RAW_METADATA_STATUS_NOT_REQUESTED
    assert result["sequence_included"] == "false"
    assert result["evidence_row_created"] == "false"
    assert result["reviewed_decision_created"] == "false"
    assert result["downstream_block_status"] == "blocked_gate4_gate5"
    assert result["claim_status"] == "repair_worklist"


def test_ci_denied_policy_row_does_not_call_provider() -> None:
    row = policy_row(
        live_policy.LiveLookupOptInContext(
            explicit_live_opt_in=True,
            running_in_ci=True,
            operator_acknowledged_blockers=True,
        )
    )

    result = live_client.run_live_metadata_lookup_for_policy_row(
        row,
        provider_must_not_be_called,
    )

    assert result["provider_called"] == "false"
    assert result["live_metadata_lookup_status"] == (
        live_client.LOOKUP_STATUS_SKIPPED_POLICY_DENIED
    )
    assert result["raw_metadata_status"] == live_client.RAW_METADATA_STATUS_NOT_REQUESTED


def test_sequence_fetch_denied_policy_row_does_not_call_provider() -> None:
    row = policy_row(
        live_policy.LiveLookupOptInContext(
            explicit_live_opt_in=True,
            sequence_fetch_requested=True,
            operator_acknowledged_blockers=True,
        )
    )

    result = live_client.run_live_metadata_lookup_for_policy_row(
        row,
        provider_must_not_be_called,
    )

    assert result["provider_called"] == "false"
    assert result["sequence_included"] == "false"
    assert result["evidence_row_created"] == "false"
    assert result["reviewed_decision_created"] == "false"


def test_authorized_policy_row_calls_injected_provider_once() -> None:
    calls: list[live_client.LiveMetadataLookupRequest] = []

    def fake_provider(
        request: live_client.LiveMetadataLookupRequest,
    ) -> dict[str, str]:
        calls.append(request)
        return {"raw_metadata_status": "synthetic_raw_metadata_hit_unreviewed"}

    result = live_client.run_live_metadata_lookup_for_policy_row(
        authorized_policy_row(),
        fake_provider,
    )

    assert len(calls) == 1
    assert calls[0].candidate_id == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert calls[0].planned_lookup_query_identifier == "G3SX30"
    assert result["provider_called"] == "true"
    assert result["live_metadata_lookup_status"] == (
        live_client.LOOKUP_STATUS_RAW_METADATA_CANDIDATE
    )
    assert result["raw_metadata_status"] == "synthetic_raw_metadata_hit_unreviewed"


def test_authorized_result_remains_raw_metadata_only() -> None:
    def fake_provider(
        request: live_client.LiveMetadataLookupRequest,
    ) -> dict[str, str]:
        return {"raw_metadata_status": "synthetic_raw_metadata_hit_unreviewed"}

    result = live_client.run_live_metadata_lookup_for_policy_row(
        authorized_policy_row(),
        fake_provider,
    )

    assert result["sequence_included"] == "false"
    assert result["evidence_row_created"] == "false"
    assert result["reviewed_decision_created"] == "false"
    assert result["downstream_block_status"] == "blocked_gate4_gate5"
    assert result["claim_status"] == "repair_worklist"
    assert "not evidence" in result["live_metadata_lookup_note"]
    assert "not a reviewed decision" in result["live_metadata_lookup_note"]
    assert "not downstream eligibility" in result["live_metadata_lookup_note"]


def test_authorized_blank_provider_status_defaults_to_unreviewed_raw_metadata() -> None:
    def fake_provider(
        request: live_client.LiveMetadataLookupRequest,
    ) -> dict[str, str]:
        return {"raw_metadata_status": ""}

    result = live_client.run_live_metadata_lookup_for_policy_row(
        authorized_policy_row(),
        fake_provider,
    )

    assert result["raw_metadata_status"] == (live_client.RAW_METADATA_STATUS_RECEIVED_UNREVIEWED)


def test_run_live_metadata_lookup_for_policy_rows_returns_typed_frame() -> None:
    calls: list[live_client.LiveMetadataLookupRequest] = []

    def fake_provider(
        request: live_client.LiveMetadataLookupRequest,
    ) -> dict[str, str]:
        calls.append(request)
        return {"raw_metadata_status": "synthetic_raw_metadata_hit_unreviewed"}

    rows = pl.DataFrame([authorized_policy_row(), denied_policy_row()])

    results = live_client.run_live_metadata_lookup_for_policy_rows(
        rows,
        fake_provider,
    )

    assert results.height == 2
    assert results.columns == list(live_client.RESULT_COLUMNS)
    assert len(calls) == 1
    assert set(results.get_column("evidence_row_created").to_list()) == {"false"}
    assert set(results.get_column("reviewed_decision_created").to_list()) == {"false"}
    assert set(results.get_column("sequence_included").to_list()) == {"false"}
    assert set(results.get_column("downstream_block_status").to_list()) == {"blocked_gate4_gate5"}
    assert set(results.get_column("claim_status").to_list()) == {"repair_worklist"}


def test_run_live_metadata_lookup_for_empty_policy_rows_returns_empty_result() -> None:
    results = live_client.run_live_metadata_lookup_for_policy_rows(
        live_policy.empty_policy_rows(),
        provider_must_not_be_called,
    )

    assert results.height == 0
    assert results.columns == list(live_client.RESULT_COLUMNS)


def test_live_metadata_client_module_does_not_import_network_libraries() -> None:
    source = Path(
        "src/longevity_port_pipelines/stages/ortholog_stronger_source_live_metadata_client.py"
    ).read_text(encoding="utf-8")

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
        "urlopen",
        "socket.",
    )

    for term in forbidden_terms:
        assert term not in source


def test_live_metadata_client_module_does_not_encode_persistence_or_downstream_actions() -> None:
    source = Path(
        "src/longevity_port_pipelines/stages/ortholog_stronger_source_live_metadata_client.py"
    ).read_text(encoding="utf-8")

    forbidden_terms = (
        "write_csv",
        "read_csv",
        "read_database",
        "source evidence row created",
        "reviewed ortholog decision",
        "accepted_ortholog",
        "validated_ortholog",
        "Gate 8",
        "Gate 9",
        "Biohub",
        "embedding generation",
        "Boltz",
        "AF3",
        "Chai",
    )

    for term in forbidden_terms:
        assert term not in source
