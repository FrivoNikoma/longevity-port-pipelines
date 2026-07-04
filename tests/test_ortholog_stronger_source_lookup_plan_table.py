from __future__ import annotations

import csv
from pathlib import Path

import yaml

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_lookup_plan as lookup_plan,
)

ROOT = Path(__file__).resolve().parents[1]
LOOKUP_PLAN_TABLE_PATH = ROOT / "data/input/ortholog_stronger_source_lookup_plan.csv"
LOOKUP_PLAN_SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_lookup_plan_schema.yaml"
EVIDENCE_REQUESTS_PATH = ROOT / "data/input/ortholog_stronger_source_evidence_requests.csv"


def read_csv_header_and_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return list(reader.fieldnames or []), list(reader)


def load_schema() -> dict:
    return yaml.safe_load(LOOKUP_PLAN_SCHEMA_PATH.read_text(encoding="utf-8"))


def committed_lookup_plan_row() -> dict[str, str]:
    _columns, rows = read_csv_header_and_rows(LOOKUP_PLAN_TABLE_PATH)
    assert len(rows) == 1
    return rows[0]


def committed_g3sx30_request_row() -> dict[str, str]:
    _columns, rows = read_csv_header_and_rows(EVIDENCE_REQUESTS_PATH)
    matching = [
        row
        for row in rows
        if row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
        and row["evidence_source_accession"] == "G3SX30"
    ]
    assert len(matching) == 1
    return matching[0]


def test_lookup_plan_table_exists_and_has_one_g3sx30_row() -> None:
    assert LOOKUP_PLAN_TABLE_PATH.exists()

    columns, rows = read_csv_header_and_rows(LOOKUP_PLAN_TABLE_PATH)

    assert columns
    assert len(rows) == 1
    assert rows[0]["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert rows[0]["planned_lookup_query_identifier"] == "G3SX30"


def test_lookup_plan_table_columns_match_schema_required_fields() -> None:
    schema = load_schema()
    expected_columns = (
        schema["required_request_trace_fields"] + schema["required_lookup_plan_fields"]
    )

    columns, _rows = read_csv_header_and_rows(LOOKUP_PLAN_TABLE_PATH)

    assert columns == expected_columns


def test_lookup_plan_table_keeps_request_trace_before_plan_fields() -> None:
    schema = load_schema()
    trace_fields = schema["required_request_trace_fields"]
    lookup_plan_fields = schema["required_lookup_plan_fields"]

    columns, _rows = read_csv_header_and_rows(LOOKUP_PLAN_TABLE_PATH)

    assert columns[: len(trace_fields)] == trace_fields
    assert columns[len(trace_fields) :] == lookup_plan_fields


def test_g3sx30_lookup_plan_row_traces_to_stronger_source_request() -> None:
    row = committed_lookup_plan_row()
    request = committed_g3sx30_request_row()

    assert row["request_table"] == ("data/input/ortholog_stronger_source_evidence_requests.csv")
    assert row["request_source_row_index"] == "1"
    assert row["candidate_set"] == request["candidate_set"]
    assert row["lane_name"] == request["lane_name"]
    assert row["candidate_id"] == request["candidate_id"]
    assert row["gene_symbol"] == request["gene_symbol"]
    assert row["source_uniprot"] == request["source_uniprot"]
    assert row["partner_uniprot"] == request["partner_uniprot"]
    assert row["requested_evidence_source_database"] == (request["evidence_source_database"])
    assert row["requested_evidence_source_accession"] == (request["evidence_source_accession"])


def test_g3sx30_lookup_plan_row_preserves_accession_identity() -> None:
    row = committed_lookup_plan_row()

    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["requested_evidence_source_accession"] == "G3SX30"
    assert row["target_protein_accession"] == "G3SX30"
    assert row["planned_lookup_query_identifier"] == "G3SX30"
    assert row["target_taxid"] == "9785"
    assert row["target_species_name"] == "Loxodonta africana"
    assert row["target_gene_symbol"] == "MDM2"
    assert row["target_sequence_length"] == "492"


def test_g3sx30_lookup_plan_row_is_metadata_planning_only() -> None:
    row = committed_lookup_plan_row()

    assert row["planned_lookup_source_type"] == "uniprot_entry_metadata"
    assert row["planned_lookup_source_name"] == "UniProtKB entry metadata lookup"
    assert row["planned_lookup_mode"] == "explicit_live_opt_in_required"
    assert row["live_lookup_allowed"] == "false"
    assert row["sequence_fetch_allowed"] == "false"
    assert row["planned_output_target"] == (
        "data/input/ortholog_stronger_source_raw_metadata_responses.csv"
    )
    assert row["lookup_plan_status"] == "lookup_planned_still_blocked"
    assert row["downstream_block_status_after_lookup_plan"] == "blocked_gate4_gate5"
    assert row["claim_policy_after_lookup_plan"] == ("no_biological_claims_until_validation")
    assert row["claim_status_after_lookup_plan"] == "repair_worklist"
    assert row["allowed_next_action_after_lookup_plan"] == (
        "add_raw_metadata_response_sandbox_row_later"
    )


def test_g3sx30_lookup_plan_row_does_not_claim_reviewed_uniprot() -> None:
    row = committed_lookup_plan_row()

    assert row["planned_lookup_source_type"] != "reviewed_uniprot"
    assert "does not confirm a reviewed UniProt source" in row["reviewer_note"]


def test_g3sx30_lookup_plan_row_does_not_shortcut_to_source_evidence() -> None:
    row = committed_lookup_plan_row()

    assert row["allowed_next_action_after_lookup_plan"] != ("add_manual_source_evidence_row_later")
    assert "source evidence collection" in row["forbidden_actions_after_lookup_plan"]
    assert "reviewed decision creation" in row["forbidden_actions_after_lookup_plan"]


def test_g3sx30_lookup_plan_row_forbids_downstream_side_effects() -> None:
    row = committed_lookup_plan_row()
    forbidden_actions = row["forbidden_actions_after_lookup_plan"]

    for action in lookup_plan.RUNTIME_SIDE_EFFECTS:
        assert action in forbidden_actions
