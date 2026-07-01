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
