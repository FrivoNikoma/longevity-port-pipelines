from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_current_gate_map_lists_expected_gates() -> None:
    text = read_doc("docs/current_gate_map.md")

    for gate in [
        "Gate 0",
        "Gate 1",
        "Gate 2",
        "Gate 3",
        "Gate 4",
        "Gate 5",
        "Gate 6",
        "Gate 7",
        "Gate 8",
        "Gate 9",
        "Gate 10",
        "Gate 11",
        "Gate 12",
    ]:
        assert gate in text


def test_current_gate_map_distinguishes_current_calibration_lanes() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "SIRT6/core3" in text
    assert "first calibration lane" in text
    assert "TP53/MDM2 elephant" in text
    assert "second calibration lane" in text
    assert "beneficial_breakage" in text


def test_current_gate_map_contains_claim_policy_guardrails() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "technical checkpoint" in text
    assert "validated longevity signal" in text
    assert "proven pro-longevity variant" in text
    assert "Disallowed language" in text
