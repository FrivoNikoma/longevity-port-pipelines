from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

REGISTRY_PATH = ROOT / "data/config/candidate_lanes.yaml"
CANDIDATE_SETS_PATH = ROOT / "data/config/candidate_sets.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_candidate_lane_registry_contains_core_lanes() -> None:
    registry = load_yaml(REGISTRY_PATH)

    assert set(registry["lanes"]) == {
        "sirt6_dna_repair",
        "tp53_mdm2_elephant",
        "has2_cd44_nmr",
        "igf_rheb_mtor",
        "ampk_pilot",
    }


def test_candidate_lane_registry_matches_candidate_sets() -> None:
    registry = load_yaml(REGISTRY_PATH)
    candidate_sets = load_yaml(CANDIDATE_SETS_PATH)

    candidate_set_names = set(candidate_sets["sets"])

    for lane_name, lane in registry["lanes"].items():
        assert lane["candidate_set"] == lane_name
        assert lane["candidate_set"] in candidate_set_names


def test_candidate_lane_registry_uses_allowed_biological_modes() -> None:
    registry = load_yaml(REGISTRY_PATH)
    allowed_modes = set(registry["allowed_biological_modes"])

    for lane in registry["lanes"].values():
        assert lane["biological_mode"] in allowed_modes


def test_candidate_lane_registry_records_required_lane_fields() -> None:
    registry = load_yaml(REGISTRY_PATH)

    required_fields = {
        "candidate_set",
        "display_name",
        "biological_mode",
        "focus_genes",
        "partner_genes",
        "lane_role",
        "current_gate_status",
        "interpretation_policy",
        "notes",
    }

    for lane in registry["lanes"].values():
        assert required_fields <= set(lane)
        assert lane["focus_genes"]
        assert lane["interpretation_policy"]


def test_candidate_lane_registry_keeps_claim_policy_conservative() -> None:
    registry = load_yaml(REGISTRY_PATH)

    assert registry["claim_policy"] == "no_biological_claims_until_validation"
    assert "cofolding_readiness" in registry["required_gate_sequence"]
    assert "decision_package" in registry["required_gate_sequence"]
