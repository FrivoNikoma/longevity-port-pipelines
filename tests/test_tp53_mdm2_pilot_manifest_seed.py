from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.tp53_mdm2_pilot_manifest_validator import (
    EXPECTED_BIOLOGICAL_MODE,
    EXPECTED_BREAKAGE_INTERPRETATION_POLICY,
    EXPECTED_CANDIDATE_SET,
    EXPECTED_CLAIM_POLICY,
    validate_tp53_mdm2_pilot_manifest,
)

MANIFEST_PATH = Path("data/input/tp53_mdm2_pilot_manifest.csv")


def load_manifest() -> pl.DataFrame:
    return pl.read_csv(MANIFEST_PATH)


def test_tp53_mdm2_pilot_manifest_seed_exists() -> None:
    assert MANIFEST_PATH.exists()


def test_tp53_mdm2_pilot_manifest_seed_passes_validator() -> None:
    validate_tp53_mdm2_pilot_manifest(load_manifest())


def test_tp53_mdm2_pilot_manifest_seed_records_expected_policy_values() -> None:
    frame = load_manifest()

    assert frame.get_column("candidate_set").unique().to_list() == [EXPECTED_CANDIDATE_SET]
    assert frame.get_column("biological_mode").unique().to_list() == [EXPECTED_BIOLOGICAL_MODE]
    assert frame.get_column("breakage_interpretation_policy").unique().to_list() == [
        EXPECTED_BREAKAGE_INTERPRETATION_POLICY
    ]
    assert frame.get_column("claim_policy").unique().to_list() == [EXPECTED_CLAIM_POLICY]


def test_tp53_mdm2_pilot_manifest_seed_records_tp53_mdm2_pair() -> None:
    frame = load_manifest()

    assert set(frame.get_column("source_uniprot").to_list()) == {"P04637", "Q00987"}
    assert set(frame.get_column("partner_uniprot").to_list()) == {"P04637", "Q00987"}
    assert set(frame.get_column("target_species").to_list()) == {"elephant"}
    assert set(frame.get_column("pdb_id").to_list()) == {"1ycr"}


def test_tp53_mdm2_pilot_manifest_seed_is_blocked_by_default() -> None:
    frame = load_manifest()

    assert set(frame.get_column("strict_contrast_gate_status").to_list()) == {
        "blocked_contrast_coverage"
    }
    assert set(frame.get_column("cofolding_plan_status").to_list()) == {"blocked_by_contrast_gate"}


def test_tp53_mdm2_pilot_manifest_seed_does_not_make_claims() -> None:
    frame = load_manifest()

    forbidden_values = {
        "biological_claim",
        "validated_biological_signal",
        "submit_live_boltz_now",
        "eligible_for_cofolding_live_run",
    }

    observed_values = set()
    for column in frame.columns:
        observed_values.update(str(value) for value in frame.get_column(column).to_list())

    assert observed_values.isdisjoint(forbidden_values)
