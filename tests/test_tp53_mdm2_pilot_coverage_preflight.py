from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import strict_contrast_panel as strict_panel
from longevity_port_pipelines.stages import (
    tp53_mdm2_gate7_coverage_repair_resolutions as resolutions,
)
from longevity_port_pipelines.stages import tp53_mdm2_ortholog_repair_decisions as repair
from longevity_port_pipelines.stages.tp53_mdm2_pilot_coverage_preflight import (
    build_tp53_mdm2_generic_strict_panel_input,
    build_tp53_mdm2_generic_strict_panel_summary,
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


def load_repair_resolutions() -> pl.DataFrame:
    return resolutions.read_resolutions()


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


def test_build_tp53_mdm2_pilot_coverage_preflight_records_generic_helper_trace() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
    )

    assert set(preflight.get_column("generic_coverage_status").to_list()) == {
        "missing_source_ortholog"
    }
    assert set(preflight.get_column("generic_provenance_status").to_list()) == {"unresolved"}
    assert set(preflight.get_column("generic_repair_status").to_list()) == {"pending"}
    assert set(preflight.get_column("generic_coverage_preflight_status").to_list()) == {
        "blocked_pending_repair_review"
    }
    assert set(preflight.get_column("generic_recommended_next_action").to_list()) == {
        "complete_ortholog_repair_decision_review"
    }
    assert set(preflight.get_column("strict_panel_allowed").to_list()) == {False}
    assert set(preflight.get_column("contrast_dry_run_allowed").to_list()) == {False}
    assert set(preflight.get_column("generic_claim_policy").to_list()) == {
        "no_biological_claims_until_validation"
    }
    assert set(preflight.get_column("generic_claim_status").to_list()) == {"repair_worklist"}


def test_build_tp53_mdm2_pilot_coverage_preflight_uses_generic_helper_without_repair_table() -> (
    None
):
    preflight = build_tp53_mdm2_pilot_coverage_preflight(load_manifest())

    assert set(preflight.get_column("generic_repair_status").to_list()) == {""}
    assert set(preflight.get_column("generic_coverage_preflight_status").to_list()) == {
        "blocked_pending_repair_review"
    }
    assert set(preflight.get_column("generic_recommended_next_action").to_list()) == {
        "complete_ortholog_repair_decision_review"
    }
    assert set(preflight.get_column("strict_panel_allowed").to_list()) == {False}
    assert set(preflight.get_column("contrast_dry_run_allowed").to_list()) == {False}


def test_build_tp53_mdm2_generic_strict_panel_input_uses_generic_schema_fields() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
    )

    strict_input = build_tp53_mdm2_generic_strict_panel_input(preflight)

    assert strict_input.height == preflight.height
    assert set(strict_panel.REQUIRED_COLUMNS).issubset(set(strict_input.columns))
    assert set(strict_input.get_column("lane_name").to_list()) == {"tp53_mdm2_elephant"}
    assert set(strict_input.get_column("target_species").to_list()) == {"elephant"}
    assert set(strict_input.get_column("target_species_taxid").to_list()) == {9785}
    assert set(strict_input.get_column("species_group").to_list()) == {"long_lived_large_body"}
    assert set(strict_input.get_column("coverage_preflight_status").to_list()) == {
        "blocked_pending_repair_review"
    }
    assert set(strict_input.get_column("control_readiness_status").to_list()) == {
        "controls_not_evaluated_coverage_blocked"
    }
    assert set(strict_input.get_column("claim_policy").to_list()) == {
        "no_biological_claims_until_validation"
    }


def test_build_tp53_mdm2_generic_strict_panel_summary_blocks_current_rows() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
    )

    summary = build_tp53_mdm2_generic_strict_panel_summary(preflight)

    assert summary.height == 2
    assert set(summary.get_column("candidate_id").to_list()) == {
        "tp53_mdm2_elephant_seed_tp53_chain",
        "tp53_mdm2_elephant_seed_mdm2_chain",
    }
    assert set(summary.get_column("strict_panel_status").to_list()) == {
        "blocked_species_coverage_repair"
    }
    assert set(summary.get_column("recommended_next_action").to_list()) == {
        "resolve_coverage_repair_decisions"
    }
    assert set(summary.get_column("contrast_dry_run_allowed").to_list()) == {False}
    assert set(summary.get_column("controlled_claim_allowed").to_list()) == {False}
    assert set(summary.get_column("n_strict_panel_ready_species").to_list()) == {0}
    assert set(summary.get_column("n_strict_panel_blocked_species").to_list()) == {1}
    assert set(summary.get_column("n_strict_long_lived_ready").to_list()) == {0}
    assert set(summary.get_column("n_strict_short_lived_ready").to_list()) == {0}
    assert set(summary.get_column("blocked_target_species").to_list()) == {"elephant"}


def test_build_tp53_mdm2_generic_strict_panel_summary_does_not_make_claims() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
    )

    summary = build_tp53_mdm2_generic_strict_panel_summary(preflight)

    assert set(summary.get_column("claim_policy").to_list()) == {
        "no_biological_claims_until_validation"
    }
    assert set(summary.get_column("claim_status").to_list()) == {"strict_panel_readiness"}
    assert set(summary.get_column("controlled_claim_allowed").to_list()) == {False}

    forbidden_values = {
        "biological_claim",
        "validated_biological_signal",
        "eligible_for_cofolding_live_run",
        "submit_live_boltz_now",
    }
    observed_values = set()
    for column in summary.columns:
        observed_values.update(str(value) for value in summary.get_column(column).to_list())

    assert observed_values.isdisjoint(forbidden_values)


def test_tp53_mdm2_coverage_resolutions_change_both_row_states() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
        repair_resolutions=load_repair_resolutions(),
    )
    by_candidate = {row["candidate_id"]: row for row in preflight.iter_rows(named=True)}

    mdm2 = by_candidate["tp53_mdm2_elephant_seed_mdm2_chain"]
    assert mdm2["coverage_repair_outcome"] == "coverage_repaired_and_ready"
    assert mdm2["coverage_preflight_status"] == "coverage_repaired_and_ready"
    assert mdm2["source_ortholog_status"] == "present_source_ortholog"
    assert mdm2["generic_repair_status"] == "accepted_for_planning_after_review"
    assert mdm2["generic_coverage_preflight_status"] == "coverage_preflight_ready"
    assert mdm2["strict_panel_allowed"] is True

    tp53 = by_candidate["tp53_mdm2_elephant_seed_tp53_chain"]
    assert tp53["coverage_repair_outcome"] == "deferred_pending_source"
    assert tp53["coverage_preflight_status"] == "deferred_pending_source"
    assert tp53["source_ortholog_status"] == "missing_source_ortholog"
    assert tp53["generic_repair_status"] == "deferred_pending_source"
    assert tp53["generic_coverage_preflight_status"] == ("blocked_deferred_pending_source")
    assert tp53["strict_panel_allowed"] is False
    assert tp53["resolution_blocker_code"] == (
        "no_accepted_accession_level_elephant_tp53_ortholog_evidence"
    )


def test_tp53_mdm2_coverage_resolutions_remove_pending_review_status() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
        repair_resolutions=load_repair_resolutions(),
    )

    assert "blocked_pending_repair_review" not in set(
        preflight.get_column("generic_coverage_preflight_status").to_list()
    )
    assert "pending" not in set(preflight.get_column("generic_repair_status").to_list())


def test_tp53_mdm2_resolved_strict_panel_records_downstream_states() -> None:
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=load_repair_decisions(),
        repair_resolutions=load_repair_resolutions(),
    )
    strict_input = build_tp53_mdm2_generic_strict_panel_input(preflight)
    input_by_candidate = {row["candidate_id"]: row for row in strict_input.iter_rows(named=True)}
    assert (
        input_by_candidate["tp53_mdm2_elephant_seed_mdm2_chain"]["control_readiness_status"]
        == "controls_ready"
    )
    assert (
        input_by_candidate["tp53_mdm2_elephant_seed_tp53_chain"]["control_readiness_status"]
        == "controls_not_evaluated_coverage_blocked"
    )

    summary = build_tp53_mdm2_generic_strict_panel_summary(preflight)
    by_candidate = {row["candidate_id"]: row for row in summary.iter_rows(named=True)}
    mdm2 = by_candidate["tp53_mdm2_elephant_seed_mdm2_chain"]
    assert mdm2["strict_panel_status"] == ("insufficient_strict_short_lived_species")
    assert mdm2["n_strict_long_lived_ready"] == 1
    assert mdm2["n_strict_short_lived_ready"] == 0
    assert mdm2["contrast_dry_run_allowed"] is False

    tp53 = by_candidate["tp53_mdm2_elephant_seed_tp53_chain"]
    assert tp53["strict_panel_status"] == "deferred_pending_source"
    assert tp53["contrast_dry_run_allowed"] is False
    assert set(summary.get_column("controlled_claim_allowed").to_list()) == {False}
