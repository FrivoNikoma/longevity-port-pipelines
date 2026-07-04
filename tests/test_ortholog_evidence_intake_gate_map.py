from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_MAP_PATH = ROOT / "docs/current_gate_map.md"


def read_gate_map() -> str:
    return GATE_MAP_PATH.read_text(encoding="utf-8")


def test_current_gate_map_records_g3sx30_collected_source_intake_row() -> None:
    text = read_gate_map()

    assert (
        "collected source evidence intake rows: one G3SX30 collected-source intake row "
        "ready for later reviewed-decision PR"
    ) in text
    assert "intake_outcome=`evidence_ready_for_review_decision`" in text
    assert "allowed_next_action_after_intake=`prepare_later_reviewed_decision_pr`" in text
    assert "blocked_gate4_gate5" in text
    assert "repair_worklist" in text

    assert (
        "ortholog evidence review decision rows: one G3SX30 "
        "reviewed-for-planning provenance row still policy-blocked"
    ) in text
    assert "review_decision=`accepted_for_planning_after_review`" in text
    assert (
        "downstream_block_status_after_review=`reviewed_for_planning_still_policy_blocked`"
    ) in text

    assert "does not automatically update Gate 4 / Gate 5 policy" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text
