from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_tp53_mdm2_gate9_blocked_path_records_expected_commands() -> None:
    text = read_doc("docs/tp53_mdm2_pilot_manifest_policy.md")

    assert "## Generic Gate 9 blocked dry-run path" in text
    assert "uv run tp53-mdm2-cofolding-readiness-context" in text
    assert "uv run cofolding-readiness" in text
    assert "uv run cofolding-dry-run-manifest" in text


def test_tp53_mdm2_gate9_blocked_path_records_expected_outputs() -> None:
    text = read_doc("docs/tp53_mdm2_pilot_manifest_policy.md")

    assert "data/interim/tp53_mdm2_generic_cofolding_readiness_context.csv" in text
    assert "data/interim/tp53_mdm2_generic_cofolding_readiness_summary.csv" in text
    assert "data/interim/tp53_mdm2_generic_cofolding_dry_run_manifest.csv" in text
    assert "data/interim/tp53_mdm2_generic_cofolding_dry_run_blocked_manifest.csv" in text


def test_tp53_mdm2_gate9_blocked_path_records_blocked_expectation_and_guardrails() -> None:
    text = read_doc("docs/tp53_mdm2_pilot_manifest_policy.md")

    assert "eligible manifest: empty" in text
    assert "blocked manifest: blocked_gate8_not_ready" in text
    assert "coverage remains unresolved" in text
    assert "does not make TP53/MDM2 eligible for cofolding" in text
    assert "make biological claims" in text
