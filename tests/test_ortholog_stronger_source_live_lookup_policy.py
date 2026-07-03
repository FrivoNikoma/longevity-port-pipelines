from __future__ import annotations

from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_lookup_policy as live_policy,
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
        "planned_lookup_source_type": "reviewed_uniprot",
        "planned_lookup_source_name": "UniProt reviewed entry lookup",
        "planned_lookup_query_identifier": "G3SX30",
        "planned_lookup_query_taxid": "9785",
        "planned_lookup_mode": "explicit_live_opt_in_required",
        "live_lookup_allowed": "false",
        "sequence_fetch_allowed": "false",
        "planned_output_target": ("data/input/ortholog_stronger_source_evidence_collection.csv"),
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
        "reviewer_note": "Synthetic live opt-in policy test row; still blocked.",
    }


def explicit_live_plan_rows() -> pl.DataFrame:
    return pl.DataFrame([explicit_live_plan_row()])


def decision_for(
    row: dict[str, str],
    context: live_policy.LiveLookupOptInContext | None = None,
) -> dict[str, str]:
    return live_policy.evaluate_live_lookup_opt_in_for_plan_row(row, context)


def test_empty_policy_rows_preserves_schema() -> None:
    rows = live_policy.empty_policy_rows()

    assert rows.height == 0
    assert rows.columns == list(live_policy.POLICY_COLUMNS)


def test_default_context_denies_explicit_live_plan() -> None:
    decision = decision_for(explicit_live_plan_row())

    assert decision["live_lookup_policy_decision"] == (
        live_policy.DECISION_DENIED_DEFAULT_NO_OPT_IN
    )
    assert decision["live_lookup_authorized"] == "false"
    assert decision["sequence_fetch_authorized"] == "false"
    assert decision["live_lookup_policy_block_status"] == "blocked_gate4_gate5"
    assert decision["live_lookup_policy_claim_status"] == "repair_worklist"


def test_non_explicit_plan_mode_is_denied() -> None:
    row = explicit_live_plan_row() | {"planned_lookup_mode": "fixture_backed_only"}

    decision = decision_for(row)

    assert decision["live_lookup_policy_decision"] == (
        live_policy.DECISION_DENIED_NOT_EXPLICIT_PLAN
    )
    assert decision["live_lookup_authorized"] == "false"


def test_plan_live_lookup_flag_must_remain_false() -> None:
    row = explicit_live_plan_row() | {"live_lookup_allowed": "true"}

    decision = decision_for(row)

    assert decision["live_lookup_policy_decision"] == (live_policy.DECISION_DENIED_PLAN_LIVE_FLAG)
    assert decision["live_lookup_authorized"] == "false"


def test_plan_sequence_fetch_flag_must_remain_false() -> None:
    row = explicit_live_plan_row() | {"sequence_fetch_allowed": "true"}

    decision = decision_for(row)

    assert decision["live_lookup_policy_decision"] == (
        live_policy.DECISION_DENIED_PLAN_SEQUENCE_FLAG
    )
    assert decision["live_lookup_authorized"] == "false"


def test_wrong_plan_output_target_is_denied() -> None:
    row = explicit_live_plan_row() | {"planned_output_target": "data/output/live.csv"}

    decision = decision_for(row)

    assert decision["live_lookup_policy_decision"] == (
        live_policy.DECISION_DENIED_WRONG_OUTPUT_TARGET
    )
    assert decision["live_lookup_authorized"] == "false"


def test_wrong_runtime_output_target_is_denied() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        operator_acknowledged_blockers=True,
        output_target="data/output/live.csv",
    )

    decision = decision_for(explicit_live_plan_row(), context)

    assert decision["live_lookup_policy_decision"] == (
        live_policy.DECISION_DENIED_WRONG_OUTPUT_TARGET
    )
    assert decision["live_lookup_authorized"] == "false"


def test_unblocked_plan_status_is_denied() -> None:
    row = explicit_live_plan_row() | {
        "downstream_block_status_after_lookup_plan": "Gate 8 eligible"
    }

    decision = decision_for(row)

    assert decision["live_lookup_policy_decision"] == (live_policy.DECISION_DENIED_PLAN_NOT_BLOCKED)
    assert decision["live_lookup_authorized"] == "false"


def test_non_repair_worklist_claim_is_denied() -> None:
    row = explicit_live_plan_row() | {"claim_status_after_lookup_plan": "validated_ortholog"}

    decision = decision_for(row)

    assert decision["live_lookup_policy_decision"] == (
        live_policy.DECISION_DENIED_CLAIM_NOT_REPAIR_WORKLIST
    )
    assert decision["live_lookup_authorized"] == "false"


def test_ci_context_denies_even_with_explicit_opt_in() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        running_in_ci=True,
        operator_acknowledged_blockers=True,
    )

    decision = decision_for(explicit_live_plan_row(), context)

    assert decision["live_lookup_policy_decision"] == live_policy.DECISION_DENIED_CI
    assert decision["live_lookup_authorized"] == "false"


def test_sequence_fetch_request_is_denied_even_with_explicit_opt_in() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        sequence_fetch_requested=True,
        operator_acknowledged_blockers=True,
    )

    decision = decision_for(explicit_live_plan_row(), context)

    assert decision["live_lookup_policy_decision"] == (live_policy.DECISION_DENIED_SEQUENCE_FETCH)
    assert decision["live_lookup_authorized"] == "false"
    assert decision["sequence_fetch_authorized"] == "false"


def test_missing_blocker_acknowledgement_is_denied() -> None:
    context = live_policy.LiveLookupOptInContext(explicit_live_opt_in=True)

    decision = decision_for(explicit_live_plan_row(), context)

    assert decision["live_lookup_policy_decision"] == (
        live_policy.DECISION_DENIED_MISSING_BLOCKER_ACK
    )
    assert decision["live_lookup_authorized"] == "false"


def test_explicit_opt_in_with_blocker_acknowledgement_authorizes_boundary_only() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        operator_acknowledged_blockers=True,
    )

    decision = decision_for(explicit_live_plan_row(), context)

    assert decision["live_lookup_policy_decision"] == (
        live_policy.DECISION_AUTHORIZED_STILL_BLOCKED
    )
    assert decision["live_lookup_authorized"] == "true"
    assert decision["sequence_fetch_authorized"] == "false"
    assert decision["live_lookup_policy_block_status"] == "blocked_gate4_gate5"
    assert decision["live_lookup_policy_claim_status"] == "repair_worklist"
    assert "does not authorize sequence fetch" in decision["live_lookup_policy_note"]
    assert "source evidence collection" in decision["live_lookup_policy_note"]


def test_evaluate_live_lookup_opt_in_for_plan_rows_returns_policy_frame() -> None:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        operator_acknowledged_blockers=True,
    )

    rows = live_policy.evaluate_live_lookup_opt_in_for_plan_rows(
        explicit_live_plan_rows(),
        context,
    )

    assert rows.height == 1
    assert rows.columns == list(live_policy.POLICY_COLUMNS)
    assert rows.item(0, "live_lookup_policy_decision") == (
        live_policy.DECISION_AUTHORIZED_STILL_BLOCKED
    )
    assert rows.item(0, "live_lookup_authorized") == "true"


def test_authorized_policy_rows_filters_to_authorized_rows() -> None:
    authorized = decision_for(
        explicit_live_plan_row(),
        live_policy.LiveLookupOptInContext(
            explicit_live_opt_in=True,
            operator_acknowledged_blockers=True,
        ),
    )
    denied = decision_for(explicit_live_plan_row())
    rows = pl.DataFrame([authorized, denied])

    filtered = live_policy.authorized_policy_rows(rows)

    assert filtered.height == 1
    assert filtered.item(0, "live_lookup_authorized") == "true"


def test_policy_module_does_not_import_network_libraries() -> None:
    source = Path(
        "src/longevity_port_pipelines/stages/ortholog_stronger_source_live_lookup_policy.py"
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


def test_policy_module_does_not_encode_downstream_actions() -> None:
    source = Path(
        "src/longevity_port_pipelines/stages/ortholog_stronger_source_live_lookup_policy.py"
    ).read_text(encoding="utf-8")

    forbidden_terms = (
        "write_csv",
        "source evidence row",
        "reviewed ortholog decision",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "Biohub call",
        "Boltz call",
        "AF3 call",
        "Chai call",
    )

    for term in forbidden_terms:
        assert term not in source
