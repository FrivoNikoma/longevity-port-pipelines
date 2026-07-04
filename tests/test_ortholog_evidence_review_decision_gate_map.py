from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_MAP_PATH = ROOT / "docs/current_gate_map.md"


def read_gate_map() -> str:
    return GATE_MAP_PATH.read_text(encoding="utf-8")


def test_current_gate_map_records_ortholog_evidence_review_decision_scaffold() -> None:
    text = read_gate_map()

    assert "ortholog evidence review decision schema status: `schema_active`" in text
    assert (
        "ortholog evidence review decision table status: `one_g3sx30_row_policy_blocked`"
    ) in text
    assert (
        "ortholog evidence review decision validator status: `table_only_no_runtime_side_effects`"
    ) in text


def test_current_gate_map_records_first_g3sx30_reviewed_decision_row() -> None:
    text = read_gate_map()

    assert (
        "ortholog evidence review decision rows: one G3SX30 "
        "reviewed-for-planning provenance row still policy-blocked"
    ) in text
    assert "review_decision=`accepted_for_planning_after_review`" in text
    assert (
        "downstream_block_status_after_review=`reviewed_for_planning_still_policy_blocked`"
    ) in text
    assert (
        "allowed_next_action_after_review=`consider_later_explicit_gate4_gate5_policy_update`"
    ) in text
    assert "collected-source intake row from `data/input/ortholog_evidence_intake.csv#5`" in text


def test_current_gate_map_keeps_reviewed_decision_boundary() -> None:
    text = read_gate_map()

    assert "does not automatically update Gate 4 / Gate 5 policy" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not call AF3" in text
    assert "does not call Chai" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text
