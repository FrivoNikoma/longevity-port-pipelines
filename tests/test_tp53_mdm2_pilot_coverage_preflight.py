from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import tp53_mdm2_ortholog_repair_decisions as repair
from longevity_port_pipelines.stages.tp53_mdm2_pilot_coverage_preflight import (
    build_tp53_mdm2_pilot_coverage_preflight,
    coverage_preflight_status,
    recommended_next_action,
    status_counts,
)

MANIFEST_PATH = Path("data/input/tp53_mdm2_pilot_manifest.csv")


def load_manifest() -> pl.DataFrame:
    return pl.read_csv(MANIFEST_PATH)


def load_repair_decisions() -> pl.DataFrame:
    return repair.read_repair_decisions()


def test_build_tp53_mdm2_pilot_coverage_preflight_uses_committed_manifest() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(load_manifest())

    assert preflight.height == 2
    assert set(preflight.get_column("candidate_id").to_list()) == {
        "tp53_mdm2_elephant_seed_tp53_chain",
        "tp53_mdm2_elephant_seed_mdm2_chain",
    }


def test_build_tp53_mdm2_pilot_coverage_preflight_keeps_rows_blocked() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(load_manifest())

    assert set(preflight.get_column("coverage_preflight_status").to_list()) == {
        "blocked_pending_coverage_repair"
    }
    assert set(preflight.get_column("recommended_next_action").to_list()) == {
        "curate_or_fetch_tp53_mdm2_source_ortholog_coverage"
    }


def test_build_tp53_mdm2_pilot_coverage_preflight_records_unchecked_coverage() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(load_manifest())

    assert set(preflight.get_column("source_ortholog_status").to_list()) == {"not_checked"}
    assert set(preflight.get_column("local_candidate_row_status").to_list()) == {"not_checked"}


def test_build_tp53_mdm2_pilot_coverage_preflight_preserves_no_claim_policy() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(load_manifest())

    assert set(preflight.get_column("claim_policy").to_list()) == {"technical_checkpoint_no_claim"}


def test_build_tp53_mdm2_pilot_coverage_preflight_leaves_repair_fields_blank_without_table() -> (
    None
):
    preflight = build_tp53_mdm2_pilot_coverage_preflight(load_manifest())

    assert set(preflight.get_column("repair_decision").to_list()) == {""}
    assert set(preflight.get_column("repair_priority").to_list()) == {""}
    assert set(preflight.get_column("repair_claim_policy").to_list()) == {""}
    assert set(preflight.get_column("repair_note").to_list()) == {""}


def test_build_tp53_mdm2_pilot_coverage_preflight_applies_repair_decisions() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
    )

    assert set(preflight.get_column("repair_decision").to_list()) == {
        "fetch_or_curate_source_ortholog"
    }
    assert set(preflight.get_column("repair_priority").to_list()) == {"high"}
    assert set(preflight.get_column("repair_claim_policy").to_list()) == {"ortholog_repair_only"}
    assert all(
        "remains blocked until source ortholog provenance" in note
        for note in preflight.get_column("repair_note").to_list()
    )


def test_build_tp53_mdm2_pilot_coverage_preflight_rejects_invalid_repair_decisions() -> None:
    repair_decisions = load_repair_decisions().with_columns(
        pl.lit("biological_claim").alias("claim_policy")
    )

    with pytest.raises(ValueError, match="invalid values in claim_policy"):
        build_tp53_mdm2_pilot_coverage_preflight(
            load_manifest(),
            repair_decisions=repair_decisions,
        )


def test_build_tp53_mdm2_pilot_coverage_preflight_notes_no_live_actions() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
    )

    note_text = " ".join(preflight.get_column("coverage_preflight_note").to_list())
    assert "No Biohub" not in note_text
    assert "no Biohub" in note_text
    assert "Boltz" in note_text
    assert "biological claims" in note_text
    assert "repair-decision rows" in note_text


def test_build_tp53_mdm2_pilot_coverage_preflight_rejects_invalid_manifest() -> None:
    manifest = load_manifest().with_columns(pl.lit("biological_claim").alias("claim_policy"))

    with pytest.raises(ValueError, match="Invalid claim_policy"):
        build_tp53_mdm2_pilot_coverage_preflight(manifest)


@pytest.mark.parametrize(
    ("gate_status", "expected_status"),
    [
        ("blocked_contrast_coverage", "blocked_pending_coverage_repair"),
        ("eligible_for_contrast_dry_run", "coverage_marked_ready_in_manifest"),
        ("blocked_negatome_controls", "blocked_by_noncoverage_gate"),
    ],
)
def test_coverage_preflight_status_maps_gate_statuses(
    gate_status: str,
    expected_status: str,
) -> None:
    assert coverage_preflight_status(gate_status) == expected_status


@pytest.mark.parametrize(
    ("coverage_status", "expected_action"),
    [
        (
            "blocked_pending_coverage_repair",
            "curate_or_fetch_tp53_mdm2_source_ortholog_coverage",
        ),
        ("coverage_marked_ready_in_manifest", "run_contrast_gate_before_cofolding"),
        (
            "blocked_by_noncoverage_gate",
            "resolve_manifest_gate_blocker_before_coverage_preflight",
        ),
    ],
)
def test_recommended_next_action_maps_coverage_status(
    coverage_status: str,
    expected_action: str,
) -> None:
    assert recommended_next_action(coverage_status) == expected_action


def test_status_counts_summarizes_preflight_rows() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(load_manifest())

    assert status_counts(preflight) == {"blocked_pending_coverage_repair": 2}


def test_build_tp53_mdm2_pilot_coverage_preflight_does_not_make_claims() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
    )

    forbidden_values = {
        "biological_claim",
        "validated_biological_signal",
        "eligible_for_cofolding_live_run",
        "submit_live_boltz_now",
    }

    observed_values = set()
    for column in preflight.columns:
        observed_values.update(str(value) for value in preflight.get_column(column).to_list())

    assert observed_values.isdisjoint(forbidden_values)
