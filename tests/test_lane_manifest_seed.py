from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages import lane_manifest

ROOT = Path(__file__).resolve().parents[1]

SEED_PATH = ROOT / "data/interim/generic_lane_manifest_seed.csv"
LANE_MANIFEST_SCHEMA_PATH = ROOT / "data/config/lane_manifest_schema.yaml"
CANDIDATE_LANES_PATH = ROOT / "data/config/candidate_lanes.yaml"


def load_seed() -> pl.DataFrame:
    return pl.read_csv(SEED_PATH)


def load_schema() -> dict:
    return lane_manifest.load_lane_manifest_schema(LANE_MANIFEST_SCHEMA_PATH)


def load_candidate_lanes() -> dict:
    return lane_manifest.load_candidate_lanes(CANDIDATE_LANES_PATH)


def test_generic_lane_manifest_seed_exists_and_has_one_row() -> None:
    seed = load_seed()

    assert seed.height == 1


def test_generic_lane_manifest_seed_has_required_schema_columns() -> None:
    schema = load_schema()
    seed = load_seed()

    assert set(schema["required_manifest_fields"]) <= set(seed.columns)


def test_generic_lane_manifest_seed_passes_generic_validator() -> None:
    lane_manifest.validate_lane_manifest(
        load_seed(),
        schema=load_schema(),
        candidate_lanes=load_candidate_lanes(),
    )


def test_generic_lane_manifest_seed_is_planning_only() -> None:
    seed = load_seed()
    row = seed.row(0, named=True)

    assert row["manifest_status"] == "planning_only"
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "planning_only"
    assert "no biological claim" in row["reviewer_note"].lower()


def test_generic_lane_manifest_seed_covers_required_gate_sequence() -> None:
    schema = load_schema()
    seed = load_seed()
    row = seed.row(0, named=True)

    recorded_gates = set(row["gate_sequence"].split(";"))
    required_gates = set(schema["required_gate_status_fields"])

    assert required_gates <= recorded_gates
