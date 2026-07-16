from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/tp53_mdm2_gate7_strict_panel_entry_decision_result.md"


def test_gate7_decision_doc_records_terminal_outcome() -> None:
    text = DOC.read_text(encoding="utf-8")

    for fragment in [
        "Decision: Gate 7 entry is blocked",
        "`gate7_entry_allowed=false`",
        "`strict_panel_status=blocked_species_coverage_repair`",
        "`resolve_coverage_repair_decisions`",
        "two candidate rows",
        "zero strict-panel-ready species",
    ]:
        assert fragment in text


def test_gate7_decision_doc_preserves_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")

    for fragment in [
        "Gate 8 remains closed",
        "Gate 9 remains closed",
        "No Biohub or ESMC call",
        "No embedding was generated",
        "No biological claim",
        "ignored interim summary is not committed",
    ]:
        assert fragment in text
