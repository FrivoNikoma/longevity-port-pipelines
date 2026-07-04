from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_TABLE_PATH = ROOT / "data/input/ortholog_stronger_source_evidence_collection.csv"
COLLECTION_SCHEMA_PATH = (
    ROOT / "data/config/ortholog_stronger_source_evidence_collection_schema.yaml"
)
REQUEST_TABLE_PATH = ROOT / "data/input/ortholog_stronger_source_evidence_requests.csv"


def read_csv_header_and_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return list(reader.fieldnames or []), list(reader)


def load_schema() -> dict:
    return yaml.safe_load(COLLECTION_SCHEMA_PATH.read_text(encoding="utf-8"))


def committed_collection_row() -> dict[str, str]:
    _columns, rows = read_csv_header_and_rows(COLLECTION_TABLE_PATH)
    assert len(rows) == 1
    return rows[0]


def committed_request_row() -> dict[str, str]:
    _columns, rows = read_csv_header_and_rows(REQUEST_TABLE_PATH)
    matching = [
        row
        for row in rows
        if row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
        and row["evidence_source_accession"] == "G3SX30"
    ]
    assert len(matching) == 1
    return matching[0]


def test_collection_table_exists_and_has_one_g3sx30_row() -> None:
    assert COLLECTION_TABLE_PATH.exists()

    columns, rows = read_csv_header_and_rows(COLLECTION_TABLE_PATH)

    assert columns
    assert len(rows) == 1
    assert rows[0]["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert rows[0]["collected_source_type"] == "uniprot_unreviewed_entry_metadata"
    assert rows[0]["collected_source_identifier"] == "UniProtKB:G3SX30"


def test_collection_table_columns_match_schema_required_fields() -> None:
    schema = load_schema()
    expected_columns = (
        schema["required_request_trace_fields"] + schema["required_collection_fields"]
    )

    columns, _rows = read_csv_header_and_rows(COLLECTION_TABLE_PATH)

    assert columns == expected_columns


def test_collection_table_keeps_request_trace_before_collection_fields() -> None:
    schema = load_schema()
    trace_fields = schema["required_request_trace_fields"]
    collection_fields = schema["required_collection_fields"]

    columns, _rows = read_csv_header_and_rows(COLLECTION_TABLE_PATH)

    assert columns[: len(trace_fields)] == trace_fields
    assert columns[len(trace_fields) :] == collection_fields


def test_g3sx30_collection_row_traces_to_request_row() -> None:
    row = committed_collection_row()
    request_row = committed_request_row()

    assert row["candidate_set"] == request_row["candidate_set"]
    assert row["lane_name"] == request_row["lane_name"]
    assert row["candidate_id"] == request_row["candidate_id"]
    assert row["gene_symbol"] == request_row["gene_symbol"]
    assert row["source_species"] == request_row["source_species"]
    assert row["target_species"] == request_row["target_species"]
    assert row["target_species_taxid"] == request_row["target_species_taxid"]
    assert row["source_uniprot"] == request_row["source_uniprot"]
    assert row["partner_uniprot"] == request_row["partner_uniprot"]
    assert row["requested_evidence_source_database"] == request_row["evidence_source_database"]
    assert row["requested_evidence_source_accession"] == request_row["evidence_source_accession"]
    assert row["target_taxid"] == request_row["target_taxid"]
    assert row["target_species_name"] == request_row["target_species_name"]
    assert row["target_gene_symbol"] == request_row["target_gene_symbol"]
    assert row["target_protein_accession"] == request_row["target_protein_accession"]
    assert row["target_sequence_length"] == request_row["target_sequence_length"]
    assert row["request_table"] == "data/input/ortholog_stronger_source_evidence_requests.csv"


def test_g3sx30_collection_row_remains_blocked_and_non_decisional() -> None:
    row = committed_collection_row()

    assert row["collection_status"] == "manual_collection_complete_still_blocked"
    assert row["collection_decision"] == "evidence_recorded_for_later_intake_pr"
    assert row["downstream_block_status_after_collection"] == "blocked_gate4_gate5"
    assert row["allowed_next_action_after_collection"] == (
        "prepare_later_source_evidence_intake_pr"
    )
    assert row["claim_policy_after_collection"] == "no_biological_claims_until_validation"
    assert row["claim_status_after_collection"] == "repair_worklist"

    assert "No sequence was fetched or reviewed" in row["collected_evidence_summary"]
    assert "reviewed metadata-only UniProtKB sandbox row" in row["reviewer_note"]
    assert "does not fetch sequence" in row["reviewer_note"]
    assert "does not" in row["reviewer_note"]
    assert "biological claim" in row["reviewer_note"]
