from __future__ import annotations

import csv
from pathlib import Path

import yaml

from longevity_port_pipelines.stages import ortholog_evidence_gate45_policy_update as policy

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = ROOT / "data/input/ortholog_evidence_gate45_policy_updates.csv"
SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_gate45_policy_update_schema.yaml"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_gate45_policy_update_table_is_header_only_scaffold() -> None:
    rows = read_csv_rows(TABLE_PATH)
    assert rows == []


def test_gate45_policy_update_table_uses_module_columns() -> None:
    header = TABLE_PATH.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert tuple(header) == policy.REQUIRED_COLUMNS


def test_gate45_policy_update_table_uses_schema_required_fields() -> None:
    schema = load_yaml(SCHEMA_PATH)
    header = set(TABLE_PATH.read_text(encoding="utf-8").splitlines()[0].split(","))
    required = set(schema["required_source_fields"]) | set(schema["required_policy_fields"])
    assert required <= header


def test_gate45_policy_update_table_names_review_decision_source_layer() -> None:
    header = set(TABLE_PATH.read_text(encoding="utf-8").splitlines()[0].split(","))
    assert "policy_source_table" in header
    assert "policy_source_row_index" in header
    assert "review_decision_before_policy" in header
    assert "downstream_block_status_before_policy" in header
    assert "allowed_next_action_before_policy" in header
