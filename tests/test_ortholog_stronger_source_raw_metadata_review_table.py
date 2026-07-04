from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_raw_metadata_review_schema.yaml"
TABLE_PATH = ROOT / "data/input/ortholog_stronger_source_raw_metadata_reviews.csv"


def read_csv_header_and_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return list(reader.fieldnames or []), list(reader)


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_raw_metadata_review_table_exists_and_has_one_g3sx30_row() -> None:
    assert TABLE_PATH.exists()

    columns, rows = read_csv_header_and_rows(TABLE_PATH)

    assert columns
    assert len(rows) == 1
    assert rows[0]["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert rows[0]["raw_metadata_source_identifier"] == "UniProtKB:G3SX30"
    assert rows[0]["raw_metadata_human_review_decision"] == (
        "metadata_consistent_prepare_source_evidence_intake_later"
    )


def test_raw_metadata_review_table_columns_match_schema_required_fields() -> None:
    schema = load_schema()
    expected_columns = (
        schema["required_raw_metadata_response_trace_fields"] + schema["required_review_fields"]
    )

    columns, _rows = read_csv_header_and_rows(TABLE_PATH)

    assert columns == expected_columns


def test_g3sx30_raw_metadata_review_row_remains_blocked_and_metadata_only() -> None:
    _columns, rows = read_csv_header_and_rows(TABLE_PATH)
    row = rows[0]

    assert row["raw_metadata_human_review_status"] == (
        "raw_metadata_human_review_complete_still_blocked"
    )
    assert row["reviewed_metadata_source_type"] == "uniprot_entry_metadata"
    assert row["reviewed_accession"] == "G3SX30"
    assert row["reviewed_entry_name"] == "G3SX30_LOXAF"
    assert row["reviewed_reviewed_status"] == "unreviewed"
    assert row["reviewed_gene_symbol"] == "MDM2"
    assert row["reviewed_taxid"] == "9785"
    assert row["reviewed_sequence_length"] == "492"
    assert row["sequence_review_scope"] == "metadata_only_no_sequence_reviewed"

    assert row["sequence_fetched"] == "false"
    assert row["source_evidence_created"] == "false"
    assert row["reviewed_decision_created"] == "false"
    assert row["gate4_gate5_policy_updated"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"

    assert row["downstream_block_status_after_review"] == "blocked_gate4_gate5"
    assert row["allowed_next_action_after_review"] == ("prepare_later_source_evidence_intake_pr")
    assert row["claim_status_after_review"] == "repair_worklist"
    assert row["biological_claim_status"] == "no_biological_claim"
    assert "does not create source evidence" in row["reviewer_note"]
    assert "does not create" in row["reviewer_note"]
    assert "biological claim" in row["reviewer_note"]
