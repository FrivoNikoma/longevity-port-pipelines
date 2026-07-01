from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import gated_contrast
from longevity_port_pipelines.stages import sirt6_generic_gated_contrast_input as stage


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
            {
                "complex_id": "ungated_candidate",
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


def test_build_sirt6_generic_gated_contrast_input_matches_generic_required_columns() -> None:
    generic_input = stage.build_sirt6_generic_gated_contrast_input(
        enrichment=enrichment_rows(),
        candidate_gate=gate_rows(),
    )

    assert generic_input.columns == list(stage.GENERIC_GATED_CONTRAST_INPUT_SCHEMA)
    assert set(generic_input.columns) >= gated_contrast.REQUIRED_COLUMNS


def test_build_sirt6_generic_gated_contrast_input_maps_eligible_rows() -> None:
    generic_input = stage.build_sirt6_generic_gated_contrast_input(
        enrichment=enrichment_rows(),
        candidate_gate=gate_rows(),
    )

    candidate_rows = generic_input.filter(pl.col("candidate_id") == "candidate_a")
    assert candidate_rows.height == 2

    long_row = candidate_rows.filter(pl.col("target_species") == "naked_mole_rat").row(
        0,
        named=True,
    )
    short_row = candidate_rows.filter(pl.col("target_species") == "mouse").row(
        0,
        named=True,
    )

    assert long_row["candidate_set"] == "sirt6_dna_repair"
    assert long_row["lane_name"] == "sirt6_dna_repair"
    assert long_row["pdb_id"] == "4xhu"
    assert long_row["source_uniprot"] == "P09874"
    assert long_row["strict_panel_status"] == "strict_panel_ready"
    assert long_row["contrast_dry_run_allowed"] is True
    assert long_row["controlled_claim_allowed"] is False
    assert long_row["target_species_taxid"] == 10181
    assert long_row["species_group"] == "long_lived_small_body"
    assert long_row["effect_size"] == pytest.approx(0.9)
    assert long_row["claim_policy"] == "no_biological_claims_until_validation"

    assert short_row["target_species_taxid"] == 10090
    assert short_row["species_group"] == "short_lived_control"


def test_build_sirt6_generic_gated_contrast_input_preserves_blocked_gate_rows() -> None:
    generic_input = stage.build_sirt6_generic_gated_contrast_input(
        enrichment=enrichment_rows(),
        candidate_gate=gate_rows(),
    )

    blocked_rows = generic_input.filter(pl.col("candidate_id") == "blocked_candidate")
    assert blocked_rows.height == 2

    row = blocked_rows.row(0, named=True)
    assert row["strict_panel_status"] == "blocked_negatome_repair_policy"
    assert row["contrast_dry_run_allowed"] is False
    assert row["controlled_claim_allowed"] is False


def test_sirt6_generic_input_can_feed_generic_gated_contrast_runtime() -> None:
    generic_input = stage.build_sirt6_generic_gated_contrast_input(
        enrichment=enrichment_rows(),
        candidate_gate=gate_rows(),
    )

    contrast = gated_contrast.build_generic_gated_contrast(generic_input)

    assert contrast.height == 2

    ready_row = contrast.filter(pl.col("candidate_id") == "candidate_a").row(
        0,
        named=True,
    )
    blocked_row = contrast.filter(pl.col("candidate_id") == "blocked_candidate").row(
        0,
        named=True,
    )

    assert ready_row["contrast_status"] == "technical_contrast_ready"
    assert ready_row["contrast_class"] == "long_lived_specific_interface_divergence"
    assert ready_row["robustness_status"] == "technical_single_baseline_review"

    assert blocked_row["contrast_status"] == "blocked_strict_panel_not_ready"
    assert blocked_row["robustness_status"] == "blocked_before_robustness_review"
    assert blocked_row["contrast_dry_run_allowed"] is False


def test_build_sirt6_generic_gated_contrast_input_drops_ungated_enrichment_rows() -> None:
    generic_input = stage.build_sirt6_generic_gated_contrast_input(
        enrichment=enrichment_rows().filter(pl.col("complex_id") == "ungated_candidate"),
        candidate_gate=gate_rows(),
    )

    assert generic_input.is_empty()
    assert generic_input.schema == stage.GENERIC_GATED_CONTRAST_INPUT_SCHEMA


def test_build_sirt6_generic_gated_contrast_input_validates_enrichment_columns() -> None:
    with pytest.raises(ValueError, match="enrichment is missing required columns"):
        stage.build_sirt6_generic_gated_contrast_input(
            enrichment=enrichment_rows().drop("p_two_sided"),
            candidate_gate=gate_rows(),
        )


def test_build_sirt6_generic_gated_contrast_input_validates_gate_columns() -> None:
    with pytest.raises(ValueError, match="candidate_gate is missing required columns"):
        stage.build_sirt6_generic_gated_contrast_input(
            enrichment=enrichment_rows(),
            candidate_gate=gate_rows().drop("strict_contrast_gate_status"),
        )


def test_build_sirt6_generic_gated_contrast_input_rejects_unknown_species() -> None:
    bad_enrichment = enrichment_rows().with_columns(
        pl.when(pl.col("target_species") == "mouse")
        .then(pl.lit("unknown_species"))
        .otherwise(pl.col("target_species"))
        .alias("target_species")
    )

    with pytest.raises(ValueError, match="Unknown SIRT6 target species"):
        stage.build_sirt6_generic_gated_contrast_input(
            enrichment=bad_enrichment,
            candidate_gate=gate_rows(),
        )
