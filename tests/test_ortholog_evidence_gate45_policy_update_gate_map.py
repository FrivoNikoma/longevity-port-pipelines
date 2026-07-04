from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_MAP_PATH = ROOT / "docs/current_gate_map.md"


def read_gate_map() -> str:
    return GATE_MAP_PATH.read_text(encoding="utf-8")


def test_current_gate_map_records_gate45_policy_update_row() -> None:
    text = read_gate_map()

    assert (
        "ortholog evidence Gate 4 / Gate 5 policy update schema status: `schema_active`"
    ) in text
    assert (
        "ortholog evidence Gate 4 / Gate 5 policy update table status: "
        "`one_g3sx30_row_runtime_blocked`"
    ) in text
    assert (
        "ortholog evidence Gate 4 / Gate 5 policy update rows: one G3SX30 "
        "planning-policy update row still runtime-blocked"
    ) in text
    assert ("policy_update_decision=`approve_gate45_policy_update_for_planning`") in text
    assert (
        "downstream_block_status_after_policy=`gate45_policy_updated_still_runtime_blocked`"
    ) in text
    assert (
        "allowed_next_action_after_policy=`prepare_later_gate_aware_embedding_fill_plan_pr`"
    ) in text
    assert (
        "ortholog evidence Gate 4 / Gate 5 policy update validator status: "
        "`table_only_no_runtime_side_effects`"
    ) in text


def test_current_gate_map_keeps_gate45_policy_update_runtime_boundary() -> None:
    text = read_gate_map()

    assert "does not fetch sequences" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not call AF3" in text
    assert "does not call Chai" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text
