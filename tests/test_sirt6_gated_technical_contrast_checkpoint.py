from __future__ import annotations

from pathlib import Path

DOC_PATH = Path("docs/sirt6_gated_technical_contrast_checkpoint.md")


def test_sirt6_gated_technical_contrast_checkpoint_doc_exists() -> None:
    assert DOC_PATH.exists()


def test_sirt6_gated_technical_contrast_checkpoint_records_command_and_outputs() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "uv run longevity-contrast" in text
    assert "data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet" in text
    assert "data/interim/sirt6_candidate_contrast_gate.csv" in text
    assert "data/output/sirt6_gated_longevity_contrast.csv" in text
    assert "data/output/sirt6_gated_longevity_contrast_blocked.csv" in text


def test_sirt6_gated_technical_contrast_checkpoint_records_gate_policy() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "eligible_for_contrast_dry_run" in text
    assert "technical_checkpoint_no_claim" in text
    assert "not a biological result" in text
    assert "not a validated longevity signal" in text
    assert "not a wet-lab claim" in text


def test_sirt6_gated_technical_contrast_checkpoint_blocks_overclaiming() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "SIRT6 longevity signal is validated" in text
    assert "This proves a long-lived species mechanism" in text
    assert "This proves functional protection or functional damage" in text
    assert "not by itself evidence for a validated SIRT6 longevity mechanism" in text


def test_sirt6_gated_technical_contrast_checkpoint_records_no_live_actions() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "call the Biohub API" in text
    assert "call the Boltz API" in text
    assert "generate embeddings" in text
    assert "compute new enrichment statistics" in text
    assert "submit cofolding jobs" in text
    assert "make wet-lab or biological validation claims" in text
