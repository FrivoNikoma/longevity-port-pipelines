from __future__ import annotations

import csv
from pathlib import Path

import yaml

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_raw_metadata_response as raw_metadata,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_METADATA_TABLE_PATH = ROOT / "data/input/ortholog_stronger_source_raw_metadata_responses.csv"
RAW_METADATA_SCHEMA_PATH = (
    ROOT / "data/config/ortholog_stronger_source_raw_metadata_response_schema.yaml"
)
LOOKUP_PLAN_TABLE_PATH = ROOT / "data/input/ortholog_stronger_source_lookup_plan.csv"


def read_csv_header_and_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return list(reader.fieldnames or []), list(reader)


def load_schema() -> dict:
    return yaml.safe_load(RAW_METADATA_SCHEMA_PATH.read_text(encoding="utf-8"))


def committed_raw_metadata_row() -> dict[str, str]:
    _columns, rows = read_csv_header_and_rows(RAW_METADATA_TABLE_PATH)
    assert len(rows) == 1
    return rows[0]


def committed_lookup_plan_row() -> dict[str, str]:
    _columns, rows = read_csv_header_and_rows(LOOKUP_PLAN_TABLE_PATH)
    matching = [
        row
        for row in rows
        if row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
        and row["planned_lookup_query_identifier"] == "G3SX30"
    ]
    assert len(matching) == 1
    return matching[0]


def test_raw_metadata_response_table_exists_and_has_one_g3sx30_dry_run_row() -> None:
    assert RAW_METADATA_TABLE_PATH.exists()

    columns, rows = read_csv_header_and_rows(RAW_METADATA_TABLE_PATH)

    assert columns
    assert len(rows) == 1
    assert rows[0]["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert rows[0]["planned_lookup_query_identifier"] == "G3SX30"


def test_raw_metadata_response_table_columns_match_schema_required_fields() -> None:
    schema = load_schema()
    expected_columns = (
        schema["required_request_trace_fields"]
        + schema["required_lookup_trace_fields"]
        + schema["required_raw_metadata_response_fields"]
    )

    columns, _rows = read_csv_header_and_rows(RAW_METADATA_TABLE_PATH)

    assert columns == expected_columns


def test_raw_metadata_response_row_traces_to_committed_lookup_plan() -> None:
    row = committed_raw_metadata_row()
    lookup_row = committed_lookup_plan_row()

    for column in [
        "candidate_set",
        "lane_name",
        "candidate_id",
        "request_table",
        "request_source_row_index",
        "gene_symbol",
        "source_species",
        "target_species",
        "target_species_taxid",
        "source_uniprot",
        "partner_uniprot",
        "requested_evidence_source_database",
        "requested_evidence_source_accession",
        "target_taxid",
        "target_species_name",
        "target_gene_symbol",
        "target_protein_accession",
        "target_sequence_length",
        "planned_lookup_source_type",
        "planned_lookup_source_name",
        "planned_lookup_query_identifier",
        "planned_lookup_query_taxid",
    ]:
        assert row[column] == lookup_row[column]


def test_g3sx30_raw_metadata_response_row_is_dry_run_derived_only() -> None:
    row = committed_raw_metadata_row()

    assert row["planned_lookup_source_type"] == "uniprot_entry_metadata"
    assert row["live_lookup_policy_decision"] == "authorized_explicit_opt_in_still_blocked"
    assert row["dry_run_status"] == "dry_run_raw_metadata_candidate_still_blocked"
    assert row["dry_run_provider_mode"] == "injected_fake_or_noop_provider_only"
    assert row["raw_metadata_source_type"] == "injected_fake_or_noop_provider"
    assert "dry_run" in row["raw_metadata_payload_ref"]
    assert "not_persisted" in row["raw_metadata_payload_ref"]
    assert "dry-run" in row["raw_metadata_summary"].lower()
    assert "non-evidence" in row["raw_metadata_summary"].lower()
    assert "dry-run-derived" in row["reviewer_note"].lower()
    assert "not source evidence" in row["reviewer_note"].lower()


def test_g3sx30_raw_metadata_response_row_preserves_blockers_and_false_flags() -> None:
    row = committed_raw_metadata_row()

    for column in raw_metadata.FALSE_ONLY_COLUMNS:
        assert row[column] == "false"

    assert row["raw_metadata_response_status"] == ("raw_metadata_received_unreviewed_still_blocked")
    assert row["raw_metadata_review_status"] == "unreviewed_raw_metadata"
    assert row["downstream_block_status_after_raw_metadata"] == "blocked_gate4_gate5"
    assert row["claim_policy_after_raw_metadata"] == ("no_biological_claims_until_validation")
    assert row["claim_status_after_raw_metadata"] == "repair_worklist"
    assert row["biological_claim_status"] == "no_biological_claim"


def test_g3sx30_raw_metadata_response_row_forbids_downstream_side_effects() -> None:
    row = committed_raw_metadata_row()

    assert raw_metadata.forbidden_actions_present(row)


def test_committed_raw_metadata_response_table_validates() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    assert rows.height == 1
    raw_metadata.validate_stronger_source_raw_metadata_response_rows(rows)
    raw_metadata.validate_dry_run_derived_rows_remain_explicit(rows)
