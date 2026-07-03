from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_TABLE_PATH = ROOT / "data/input/ortholog_stronger_source_evidence_collection.csv"
COLLECTION_SCHEMA_PATH = (
    ROOT / "data/config/ortholog_stronger_source_evidence_collection_schema.yaml"
)


def read_csv_header_and_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return list(reader.fieldnames or []), list(reader)


def load_schema() -> dict:
    return yaml.safe_load(COLLECTION_SCHEMA_PATH.read_text(encoding="utf-8"))


def test_collection_table_scaffold_exists_and_is_header_only() -> None:
    assert COLLECTION_TABLE_PATH.exists()

    columns, rows = read_csv_header_and_rows(COLLECTION_TABLE_PATH)

    assert columns
    assert rows == []


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


def test_collection_table_scaffold_has_no_manual_source_evidence_yet() -> None:
    _columns, rows = read_csv_header_and_rows(COLLECTION_TABLE_PATH)

    assert rows == []
