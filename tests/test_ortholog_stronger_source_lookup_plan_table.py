from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOOKUP_PLAN_TABLE_PATH = ROOT / "data/input/ortholog_stronger_source_lookup_plan.csv"
LOOKUP_PLAN_SCHEMA_PATH = ROOT / "data/config/ortholog_stronger_source_lookup_plan_schema.yaml"


def read_csv_header_and_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return list(reader.fieldnames or []), list(reader)


def load_schema() -> dict:
    return yaml.safe_load(LOOKUP_PLAN_SCHEMA_PATH.read_text(encoding="utf-8"))


def test_lookup_plan_table_scaffold_exists_and_is_header_only() -> None:
    assert LOOKUP_PLAN_TABLE_PATH.exists()

    columns, rows = read_csv_header_and_rows(LOOKUP_PLAN_TABLE_PATH)

    assert columns
    assert rows == []


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


def test_lookup_plan_table_scaffold_has_no_lookup_rows_yet() -> None:
    _columns, rows = read_csv_header_and_rows(LOOKUP_PLAN_TABLE_PATH)

    assert rows == []


def test_lookup_plan_table_scaffold_has_no_source_evidence_rows_yet() -> None:
    _columns, rows = read_csv_header_and_rows(LOOKUP_PLAN_TABLE_PATH)

    assert rows == []
