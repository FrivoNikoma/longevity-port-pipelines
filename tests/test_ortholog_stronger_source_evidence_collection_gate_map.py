from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_MAP_PATH = ROOT / "docs/current_gate_map.md"


def read_gate_map() -> str:
    return GATE_MAP_PATH.read_text(encoding="utf-8")


def test_current_gate_map_records_g3sx30_stronger_source_collection_row() -> None:
    text = read_gate_map()

    assert "stronger-source collection table status: `one_g3sx30_row_still_blocked`" in text
    assert (
        "manually collected stronger-source evidence rows: one G3SX30 metadata-only "
        "UniProtKB TrEMBL row"
    ) in text
    assert "collection_decision=`evidence_recorded_for_later_intake_pr`" in text
    assert "blocked_gate4_gate5" in text
    assert "repair_worklist" in text
    assert "no sequence fetch" in text
    assert "no reviewed decision" in text
    assert "no biological claim" in text
