from pathlib import Path

DOC_PATH = Path("docs/sirt6_contrast_gated_cofolding_run_plan.md")


def test_sirt6_contrast_gated_cofolding_run_plan_doc_exists() -> None:
    assert DOC_PATH.exists()


def test_sirt6_contrast_gated_cofolding_run_plan_records_gated_inputs() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "data/output/sirt6_gated_longevity_contrast.csv" in text
    assert "data/output/sirt6_gated_longevity_contrast_blocked.csv" in text
    assert "uv run longevity-contrast" in text


def test_sirt6_contrast_gated_cofolding_run_plan_records_inclusion_policy() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "eligible_for_contrast_dry_run" in text
    assert "technical_checkpoint_no_claim" in text
    assert "eligible_for_cofolding_dry_run" in text
    assert "It does not mean the row is biologically validated" in text


def test_sirt6_contrast_gated_cofolding_run_plan_records_blocked_row_policy() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "blocked table are excluded from live cofolding planning by default" in text
    assert "blocked_by_contrast_gate" in text
    assert "blocked_pending_manual_review" in text
    assert "blocked_pending_negatome_repair" in text
    assert "blocked_pending_species_coverage_repair" in text


def test_sirt6_contrast_gated_cofolding_run_plan_records_manifest_fields() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "candidate_id" in text
    assert "pdb_id" in text
    assert "chain" in text
    assert "source_uniprot" in text
    assert "target_species" in text
    assert "contrast_class" in text
    assert "cofolding_plan_status" in text


def test_sirt6_contrast_gated_cofolding_run_plan_blocks_overclaiming() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "This candidate should be submitted to Boltz immediately" in text
    assert "This proves a SIRT6 longevity mechanism" in text
    assert "This proves a functional species-specific interaction" in text
    assert "This is a validated biological result" in text


def test_sirt6_contrast_gated_cofolding_run_plan_records_no_live_actions() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "call the Biohub API" in text
    assert "call the Boltz API" in text
    assert "generate embeddings" in text
    assert "compute new enrichment statistics" in text
    assert "submit cofolding jobs" in text
    assert "spend Boltz credits" in text
    assert "make wet-lab or biological validation claims" in text
