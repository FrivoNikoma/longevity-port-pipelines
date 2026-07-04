from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_MAP_PATH = ROOT / "docs/current_gate_map.md"


def read_gate_map() -> str:
    return GATE_MAP_PATH.read_text(encoding="utf-8")


def test_current_gate_map_records_raw_metadata_human_review_scaffold() -> None:
    text = read_gate_map()

    assert "ortholog_stronger_source_raw_metadata_review_schema.yaml" in text
    assert "ortholog_stronger_source_raw_metadata_reviews.csv" in text
    assert "ortholog_stronger_source_raw_metadata_review.py" in text
    assert "raw metadata human review schema status: `schema_only_no_rows`" in text
    assert "raw metadata human review table status: `header_only_scaffold`" in text
    assert "raw metadata human review rows: none" in text
    assert "no source evidence" in text
    assert "no reviewed decision" in text
    assert "no biological claim" in text
