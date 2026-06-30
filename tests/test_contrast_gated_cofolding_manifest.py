from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import contrast_gated_cofolding_manifest as manifest


def gated_contrast_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "long_lived_species": "naked_mole_rat",
                "contrast_class": "long_lived_enhanced_interface_constraint",
                "strict_contrast_gate_status": "eligible_for_contrast_dry_run",
                "contrast_checkpoint_policy": "technical_checkpoint_no_claim",
                "gate_recommended_next_action": "prepare_contrast_dry_run",
                "gate_note": "Candidate passes dry-run gate checks.",
            },
            {
                "candidate_id": "blocked_candidate",
                "pdb_id": "8g57",
                "chain": "ligand",
                "long_lived_species": "bowhead_whale",
                "contrast_class": "weak_or_unresolved_contrast",
                "strict_contrast_gate_status": "blocked_negatome_controls",
                "contrast_checkpoint_policy": "technical_checkpoint_no_claim",
                "gate_recommended_next_action": "fix_negatome_controls",
                "gate_note": "Blocked row should not enter manifest.",
            },
            {
                "candidate_id": "wrong_policy_candidate",
                "pdb_id": "1nfi",
                "chain": "receptor",
                "long_lived_species": "elephant",
                "contrast_class": "weak_or_unresolved_contrast",
                "strict_contrast_gate_status": "eligible_for_contrast_dry_run",
                "contrast_checkpoint_policy": "uncontrolled_claim",
                "gate_recommended_next_action": "prepare_contrast_dry_run",
                "gate_note": "Wrong policy should not enter manifest.",
            },
        ]
    )


def candidate_gate_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "chain": "receptor",
                "source_uniprot": "P09874",
            }
        ]
    )


def blocked_contrast_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "negatome_blocked",
                "pdb_id": "8bhv",
                "chain": "ligand",
                "source_uniprot": "P12956",
                "priority": "2",
                "strict_contrast_gate_status": "blocked_negatome_controls",
                "recommended_next_action": "add_negatome_repair_decision",
                "gate_note": "NEGATOME controls incomplete.",
            },
            {
                "candidate_id": "coverage_blocked",
                "pdb_id": "8g57",
                "chain": "ligand",
                "source_uniprot": "Q8N6T7",
                "priority": "1",
                "strict_contrast_gate_status": "blocked_species_coverage",
                "recommended_next_action": "review_manual_coverage_repair_decisions",
                "gate_note": "Coverage repair required.",
            },
            {
                "candidate_id": "strict_blocked",
                "pdb_id": "1nfi",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "strict_contrast_gate_status": "blocked_strict_panel",
                "recommended_next_action": "resolve_strict_panel_status",
                "gate_note": "Strict panel not ready.",
            },
            {
                "candidate_id": "generic_blocked",
                "pdb_id": "7s68",
                "chain": "receptor",
                "source_uniprot": "Q8N6T7",
                "priority": "3",
                "strict_contrast_gate_status": "blocked_baseline_input",
                "recommended_next_action": "fix_baseline_input",
                "gate_note": "Baseline input missing.",
            },
        ]
    )


def test_build_contrast_gated_cofolding_manifest_keeps_only_eligible_rows() -> None:
    result = manifest.build_contrast_gated_cofolding_manifest(
        gated_contrast=gated_contrast_rows(),
        candidate_gate=candidate_gate_rows(),
    )

    assert result.height == 1
    row = result.row(0, named=True)
    assert row["candidate_id"] == "4xhu__A1_P09874--4xhu__B1_Q9UNS1"
    assert row["source_uniprot"] == "P09874"
    assert row["target_species"] == "naked_mole_rat"
    assert row["strict_contrast_gate_status"] == "eligible_for_contrast_dry_run"
    assert row["contrast_checkpoint_policy"] == "technical_checkpoint_no_claim"
    assert row["cofolding_plan_status"] == "eligible_for_cofolding_dry_run"
    assert "no live Boltz submission" in row["cofolding_plan_note"]


def test_build_contrast_gated_cofolding_manifest_returns_empty_schema_when_no_rows_pass() -> None:
    source = gated_contrast_rows().with_columns(
        pl.lit("blocked_negatome_controls").alias("strict_contrast_gate_status")
    )

    result = manifest.build_contrast_gated_cofolding_manifest(gated_contrast=source)

    assert result.is_empty()
    assert result.schema == manifest.empty_cofolding_manifest().schema


def test_build_blocked_contrast_gated_cofolding_manifest_maps_blocked_statuses() -> None:
    result = manifest.build_blocked_contrast_gated_cofolding_manifest(
        blocked_contrast=blocked_contrast_rows(),
    )

    by_id = {
        row["candidate_id"]: row["cofolding_plan_status"] for row in result.iter_rows(named=True)
    }
    assert by_id["negatome_blocked"] == "blocked_pending_negatome_repair"
    assert by_id["coverage_blocked"] == "blocked_pending_species_coverage_repair"
    assert by_id["strict_blocked"] == "blocked_pending_manual_review"
    assert by_id["generic_blocked"] == "blocked_by_contrast_gate"


def test_build_blocked_contrast_gated_cofolding_manifest_records_no_live_planning_note() -> None:
    result = manifest.build_blocked_contrast_gated_cofolding_manifest(
        blocked_contrast=blocked_contrast_rows(),
    )

    assert result.height == 4
    assert all(
        "excluded from live Boltz planning by default" in row["cofolding_plan_note"]
        for row in result.iter_rows(named=True)
    )


def test_build_contrast_gated_cofolding_manifest_validates_required_columns() -> None:
    source = gated_contrast_rows().drop("contrast_checkpoint_policy")

    with pytest.raises(ValueError, match="gated_contrast is missing required columns"):
        manifest.build_contrast_gated_cofolding_manifest(gated_contrast=source)


def test_build_blocked_contrast_gated_cofolding_manifest_validates_required_columns() -> None:
    source = blocked_contrast_rows().drop("recommended_next_action")

    with pytest.raises(ValueError, match="blocked_contrast is missing required columns"):
        manifest.build_blocked_contrast_gated_cofolding_manifest(blocked_contrast=source)
