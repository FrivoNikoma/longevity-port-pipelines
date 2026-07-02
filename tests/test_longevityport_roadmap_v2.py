from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_roadmap_v2_defines_reusable_pipeline_compass() -> None:
    text = read_doc("docs/longevityport_roadmap_v2.md")

    assert "reusable gated decision pipeline" in text
    assert "Which gate are we closing?" in text
    assert "Boltz" in text
    assert "downstream compatibility classifier" in text


def test_roadmap_v2_lists_core_biological_lanes() -> None:
    text = read_doc("docs/longevityport_roadmap_v2.md")

    for lane in [
        "sirt6_dna_repair",
        "tp53_mdm2_elephant",
        "has2_cd44_nmr",
        "igf_rheb_mtor",
        "ampk_pilot",
    ]:
        assert lane in text


def test_roadmap_v2_keeps_architecture_before_live_structural_calls() -> None:
    text = read_doc("docs/longevityport_roadmap_v2.md")

    assert "Add generic candidate lane registry" in text
    assert "Add generic claim policy schema" in text
    assert "Add generic ortholog repair decision schema" in text
    assert "Add first generic Boltz campaign plan" in text


def test_roadmap_records_gate8_gate9_calibration_checkpoint() -> None:
    text = read_doc("docs/longevityport_roadmap_v2.md")

    assert "Checkpoint after Gate 8 and Gate 9 calibration lanes" in text
    assert "Generic Gate 8 input bridge exists" in text
    assert "Gate 9 dry-run path is recorded" in text
    assert "Generic Gate 8-compatible blocked summary exists" in text
    assert "blocked_gate8_not_ready" in text


def test_roadmap_records_remaining_blockers_after_checkpoint() -> None:
    text = read_doc("docs/longevityport_roadmap_v2.md")

    assert "TP53/MDM2 coverage repair" in text
    assert "gate-aware embedding fill plan" in text
    assert "live Boltz calls opt-in only" in text
    assert "validated longevity signal" in text
    assert "proven pro-longevity variant" in text
