from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_sirt6_gate9_dry_run_path_records_expected_commands() -> None:
    text = read_doc("docs/sirt6_gated_technical_contrast_checkpoint.md")

    assert "## SIRT6 Gate 9 dry-run path" in text
    assert "uv run sirt6-cofolding-readiness-context" in text
    assert "uv run cofolding-readiness" in text
    assert "uv run cofolding-dry-run-manifest" in text


def test_sirt6_gate9_dry_run_path_records_expected_outputs() -> None:
    text = read_doc("docs/sirt6_gated_technical_contrast_checkpoint.md")

    assert "data/interim/sirt6_generic_cofolding_readiness_context.csv" in text
    assert "data/interim/sirt6_generic_cofolding_readiness_summary.csv" in text
    assert "data/interim/sirt6_generic_cofolding_dry_run_manifest.csv" in text
    assert "data/interim/sirt6_generic_cofolding_dry_run_blocked_manifest.csv" in text


def test_sirt6_gate9_dry_run_path_preserves_guardrails() -> None:
    text = read_doc("docs/sirt6_gated_technical_contrast_checkpoint.md")

    assert "cofolding_input_review_status = dry_run_inputs_unreviewed" in text
    assert "live_opt_in_status = live_not_requested" in text
    assert "It is not a Boltz input file and does not submit a Boltz job." in text
    assert "make wet-lab or biological validation claims" in text
    assert "bydefault" not in text
