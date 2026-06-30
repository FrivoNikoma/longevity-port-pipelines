from pathlib import Path

DOC_PATH = Path("docs/tp53_mdm2_pilot_manifest_policy.md")


def test_tp53_mdm2_pilot_manifest_policy_doc_exists() -> None:
    assert DOC_PATH.exists()


def test_tp53_mdm2_pilot_manifest_policy_records_candidate_set() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "tp53_mdm2_elephant" in text
    assert "TP53 / MDM2" in text
    assert "beneficial_breakage" in text


def test_tp53_mdm2_pilot_manifest_policy_records_breakage_caution() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "interaction weakening may be the expected biological direction" in text
    assert "must not be automatically classified as incompatibility" in text
    assert "breakage can be beneficial, neutral, or harmful" in text
    assert "do_not_auto_classify_breakage_as_incompatibility" in text


def test_tp53_mdm2_pilot_manifest_policy_records_gate_stack_reuse() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "Candidate species coverage matrix" in text
    assert "Candidate coverage repair decision table" in text
    assert "NEGATOME readiness matrix" in text
    assert "NEGATOME repair decision table" in text
    assert "Strict contrast panel builder" in text
    assert "Candidate contrast gate" in text
    assert "Gated longevity contrast" in text
    assert "Contrast-gated cofolding manifest builder" in text


def test_tp53_mdm2_pilot_manifest_policy_records_required_status_language() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "eligible_for_contrast_dry_run" in text
    assert "technical_checkpoint_no_claim" in text
    assert "eligible_for_cofolding_dry_run" in text


def test_tp53_mdm2_pilot_manifest_policy_blocks_overclaiming() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "Elephant TP53 is validated as a longevity mechanism by this pipeline" in text
    assert "MDM2 escape is proven by this manifest policy" in text
    assert "Interface breakage is always beneficial" in text
    assert "Interface breakage is always incompatibility" in text
    assert "ready for wet-lab claims without additional controls" in text


def test_tp53_mdm2_pilot_manifest_policy_records_no_live_actions() -> None:
    text = DOC_PATH.read_text(encoding="utf8")

    assert "call the Biohub API" in text
    assert "call the Boltz API" in text
    assert "fetch orthologs" in text
    assert "generate embeddings" in text
    assert "compute enrichment statistics" in text
    assert "submit cofolding jobs" in text
    assert "spend Boltz credits" in text
    assert "create biological validation claims" in text
