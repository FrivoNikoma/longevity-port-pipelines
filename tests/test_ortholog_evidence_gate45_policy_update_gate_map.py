from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_MAP_PATH = ROOT / "docs/current_gate_map.md"


def read_gate_map() -> str:
    return GATE_MAP_PATH.read_text(encoding="utf-8")


def test_current_gate_map_records_gate45_policy_update_scaffold() -> None:
    text = read_gate_map()

    assert (
        "ortholog evidence Gate 4 / Gate 5 policy update schema status: `schema_only_no_rows`"
    ) in text
    assert (
        "ortholog evidence Gate 4 / Gate 5 policy update table status: `header_only_no_rows`"
    ) in text
    assert (
        "ortholog evidence Gate 4 / Gate 5 policy update validator status: "
        "`table_only_no_runtime_side_effects`"
    ) in text


def test_current_gate_map_keeps_gate45_policy_update_scaffold_boundary() -> None:
    text = read_gate_map()

    assert "does not add a G3SX30 policy update row" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not call AF3" in text
    assert "does not call Chai" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text
