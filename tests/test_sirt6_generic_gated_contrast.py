from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import gated_contrast
from longevity_port_pipelines.stages import sirt6_generic_gated_contrast as stage
from longevity_port_pipelines.stages import (
    sirt6_generic_gated_contrast_input as input_stage,
)


def enrichment_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "complex_id": "candidate_a",
                "chain": "receptor",
                "target_species": "naked_mole_rat",
                "interface_mean_delta": 0.1,
                "noninterface_mean_delta": 0.05,
                "enrichment_ratio": 1.8,
                "effect_size_cohens_d": 0.9,
                "p_two_sided": 0.01,
                "is_predicted_structure": False,
            },
            {
                "complex_id": "candidate_a",
                "chain": "receptor",
                "target_species": "mouse",
                "interface_mean_delta": 0.02,
                "noninterface_mean_delta": 0.02,
                "enrichment_ratio": 1.0,
                "effect_size_cohens_d": 0.0,
                "p_two_sided": 0.9,
                "is_predicted_structure": False,
            },
            {
                "complex_id": "blocked_candidate",
                "chain": "receptor",
                "target_species": "naked_mole_rat",
                "interface_mean_delta": 0.1,
                "noninterface_mean_delta": 0.05,
                "enrichment_ratio": 1.8,
                "effect_size_cohens_d": 0.9,
                "p_two_sided": 0.01,
                "is_predicted_structure": False,
            },
            {
                "complex_id": "blocked_candidate",
                "chain": "receptor",
                "target_species": "mouse",
                "interface_mean_delta": 0.02,
                "noninterface_mean_delta": 0.02,
                "enrichment_ratio": 1.0,
                "effect_size_cohens_d": 0.0,
                "p_two_sided": 0.9,
                "is_predicted_structure": False,
            },
        ]
    )


def gate_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "strict_contrast_gate_status": "eligible_for_contrast_dry_run",
                "recommended_next_action": "prepare_contrast_dry_run",
                "gate_note": "Candidate passes dry-run gate checks.",
            },
            {
                "candidate_id": "blocked_candidate",
                "pdb_id": "8bhv",
                "chain": "receptor",
                "source_uniprot": "P12956",
                "priority": "2",
                "strict_contrast_gate_status": "blocked_negatome_repair_policy",
                "recommended_next_action": "complete_negatome_repair_before_controlled_claim",
                "gate_note": "NEGATOME repair decision remains deferred_no_claim.",
            },
        ]
    )


def test_build_sirt6_generic_gated_contrast_outputs_builds_input_and_summary() -> None:
    generic_input, summary = stage.build_sirt6_generic_gated_contrast_outputs(
        enrichment=enrichment_rows(),
        candidate_gate=gate_rows(),
    )

    assert generic_input.columns == list(input_stage.GENERIC_GATED_CONTRAST_INPUT_SCHEMA)
    assert summary.columns == list(gated_contrast.GATED_CONTRAST_SCHEMA)
    assert generic_input.height == 4
    assert summary.height == 2


def test_build_sirt6_generic_gated_contrast_outputs_runs_generic_runtime() -> None:
    _, summary = stage.build_sirt6_generic_gated_contrast_outputs(
        enrichment=enrichment_rows(),
        candidate_gate=gate_rows(),
    )

    ready_row = summary.filter(pl.col("candidate_id") == "candidate_a").row(
        0,
        named=True,
    )
    blocked_row = summary.filter(pl.col("candidate_id") == "blocked_candidate").row(
        0,
        named=True,
    )

    assert ready_row["candidate_set"] == "sirt6_dna_repair"
    assert ready_row["lane_name"] == "sirt6_dna_repair"
    assert ready_row["contrast_status"] == "technical_contrast_ready"
    assert ready_row["contrast_class"] == "long_lived_specific_interface_divergence"
    assert ready_row["robustness_status"] == "technical_single_baseline_review"
    assert ready_row["controlled_claim_allowed"] is False
    assert ready_row["claim_policy"] == "no_biological_claims_until_validation"

    assert blocked_row["contrast_status"] == "blocked_strict_panel_not_ready"
    assert blocked_row["contrast_class"] == "weak_or_unresolved_contrast"
    assert blocked_row["robustness_status"] == "blocked_before_robustness_review"
    assert blocked_row["contrast_dry_run_allowed"] is False
    assert blocked_row["controlled_claim_allowed"] is False


def test_write_sirt6_generic_gated_contrast_outputs_writes_both_csvs(tmp_path) -> None:
    generic_input_output = tmp_path / "sirt6_generic_gated_contrast_input.csv"
    output = tmp_path / "sirt6_generic_gated_contrast_summary.csv"

    generic_input, summary = stage.write_sirt6_generic_gated_contrast_outputs(
        enrichment=enrichment_rows(),
        candidate_gate=gate_rows(),
        generic_input_output=generic_input_output,
        output=output,
    )

    assert generic_input_output.exists()
    assert output.exists()

    written_input = pl.read_csv(generic_input_output)
    written_summary = pl.read_csv(output)

    assert written_input.height == generic_input.height
    assert written_summary.height == summary.height
    assert written_summary.columns == list(gated_contrast.GATED_CONTRAST_SCHEMA)


def test_build_sirt6_generic_gated_contrast_outputs_delegates_input_validation() -> None:
    with pytest.raises(ValueError, match="enrichment is missing required columns"):
        stage.build_sirt6_generic_gated_contrast_outputs(
            enrichment=enrichment_rows().drop("p_two_sided"),
            candidate_gate=gate_rows(),
        )
