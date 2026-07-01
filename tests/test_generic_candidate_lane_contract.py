from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_contract() -> str:
    return (ROOT / "docs/generic_candidate_lane_contract.md").read_text(encoding="utf-8")


def test_generic_candidate_lane_contract_defines_shared_lane_architecture() -> None:
    text = read_contract()

    assert "candidate lane" in text
    assert "gated architecture" in text
    assert "candidate_set" in text
    assert "biological_mode" in text
    assert "claim policy" in text


def test_generic_candidate_lane_contract_lists_allowed_biological_modes() -> None:
    text = read_contract()

    for biological_mode in [
        "maintained_or_enhanced_repair",
        "beneficial_breakage",
        "transferable_function",
        "signaling_rewiring",
        "hub_risk_review",
    ]:
        assert biological_mode in text


def test_generic_candidate_lane_contract_records_core_lanes() -> None:
    text = read_contract()

    for lane_name in [
        "SIRT6",
        "TP53/MDM2",
        "HAS2/CD44",
        "IGF/RHEB/mTOR",
        "AMPK",
    ]:
        assert lane_name in text


def test_generic_candidate_lane_contract_keeps_cofolding_downstream() -> None:
    text = read_contract()

    assert "Cofolding is downstream compatibility planning" in text
    assert "discovery shortcut" in text
    assert "Live structural calls must remain opt-in" in text


def test_generic_candidate_lane_contract_blocks_overclaiming() -> None:
    text = read_contract()

    assert "validated longevity signal" in text
    assert "proven pro-longevity variant" in text
    assert "Disallowed language before validation" in text
