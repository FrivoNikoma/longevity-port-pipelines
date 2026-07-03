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


def read_csv_header_and_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return list(reader.fieldnames or []), list(reader)


def load_schema() -> dict:
    return yaml.safe_load(RAW_METADATA_SCHEMA_PATH.read_text(encoding="utf-8"))


def expected_columns_from_schema() -> list[str]:
    schema = load_schema()
    return (
        schema["required_request_trace_fields"]
        + schema["required_lookup_trace_fields"]
        + schema["required_raw_metadata_response_fields"]
    )


def test_raw_metadata_response_table_scaffold_exists_and_is_header_only() -> None:
    assert RAW_METADATA_TABLE_PATH.exists()

    columns, rows = read_csv_header_and_rows(RAW_METADATA_TABLE_PATH)

    assert columns
    assert rows == []


def test_raw_metadata_response_table_columns_match_schema_required_fields() -> None:
    columns, _rows = read_csv_header_and_rows(RAW_METADATA_TABLE_PATH)

    assert columns == expected_columns_from_schema()


def test_raw_metadata_response_table_columns_match_python_contract() -> None:
    columns, _rows = read_csv_header_and_rows(RAW_METADATA_TABLE_PATH)

    assert columns == list(raw_metadata.REQUIRED_COLUMNS)


def test_raw_metadata_response_table_keeps_trace_before_response_fields() -> None:
    schema = load_schema()
    request_trace_fields = schema["required_request_trace_fields"]
    lookup_trace_fields = schema["required_lookup_trace_fields"]
    response_fields = schema["required_raw_metadata_response_fields"]

    columns, _rows = read_csv_header_and_rows(RAW_METADATA_TABLE_PATH)

    request_end = len(request_trace_fields)
    lookup_end = request_end + len(lookup_trace_fields)

    assert columns[:request_end] == request_trace_fields
    assert columns[request_end:lookup_end] == lookup_trace_fields
    assert columns[lookup_end:] == response_fields


def test_raw_metadata_response_table_scaffold_has_no_raw_metadata_rows_yet() -> None:
    _columns, rows = read_csv_header_and_rows(RAW_METADATA_TABLE_PATH)

    assert rows == []


def test_raw_metadata_response_reader_loads_committed_header_only_table() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    assert rows.height == 0
    assert rows.columns == list(raw_metadata.REQUIRED_COLUMNS)


def test_default_path_points_to_committed_raw_metadata_response_table() -> None:
    assert (
        Path("data/input/ortholog_stronger_source_raw_metadata_responses.csv")
        == raw_metadata.DEFAULT_RAW_METADATA_RESPONSE_PATH
    )
