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


def test_raw_metadata_review_table_exists_and_is_header_only() -> None:
    assert TABLE_PATH.exists()

    columns, rows = read_csv_header_and_rows(TABLE_PATH)

    assert columns
    assert rows == []


def test_raw_metadata_review_table_columns_match_schema_required_fields() -> None:
    schema = load_schema()
    expected_columns = (
        schema["required_raw_metadata_response_trace_fields"] + schema["required_review_fields"]
    )

    columns, _rows = read_csv_header_and_rows(TABLE_PATH)

    assert columns == expected_columns
