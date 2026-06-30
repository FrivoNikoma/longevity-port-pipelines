from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import longevity_contrast as stage


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
            },
            {
                "complex_id": "candidate_a",
                "chain": "receptor",
                "target_species": "mouse",
                "interface_mean_delta": 0.02,
                "noninterface_mean_delta": 0.02,
                "enrichment_ratio": 1.0,
                "effect_size_cohens_d": 0.0,
            },
            {
                "complex_id": "blocked_candidate",
                "chain": "receptor",
                "target_species": "naked_mole_rat",
                "interface_mean_delta": 0.1,
                "noninterface_mean_delta": 0.05,
                "enrichment_ratio": 1.8,
                "effect_size_cohens_d": 0.9,
            },
            {
                "complex_id": "blocked_candidate",
                "chain": "receptor",
                "target_species": "mouse",
                "interface_mean_delta": 0.02,
                "noninterface_mean_delta": 0.02,
                "enrichment_ratio": 1.0,
                "effect_size_cohens_d": 0.0,
            },
        ]
    )


def gate_rows(
    *,
    eligible_status: str = stage.ELIGIBLE_GATE_STATUS,
    blocked_status: str = "blocked_negatome_repair_policy",
) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "strict_contrast_gate_status": eligible_status,
                "recommended_next_action": "prepare_contrast_dry_run",
                "gate_note": "Candidate passes dry-run gate checks.",
            },
            {
                "candidate_id": "blocked_candidate",
                "pdb_id": "8bhv",
                "chain": "receptor",
                "source_uniprot": "P12956",
                "priority": "2",
                "strict_contrast_gate_status": blocked_status,
                "recommended_next_action": "complete_negatome_repair_before_controlled_claim",
                "gate_note": "NEGATOME repair decision remains deferred_no_claim.",
            },
        ]
    )


def test_build_gated_longevity_contrast_filters_to_eligible_gate_rows() -> None:
    contrast = stage.build_gated_longevity_contrast(
        enrichment=enrichment_rows(),
        candidate_gate=gate_rows(),
        short_lived_species=["mouse"],
        long_lived_species=["naked_mole_rat"],
    )

    assert contrast.height == 1
    row = contrast.row(0, named=True)
    assert row["candidate_id"] == "candidate_a"
    assert row["complex_id"] == "candidate_a"
    assert row["chain"] == "receptor"
    assert row["strict_contrast_gate_status"] == stage.ELIGIBLE_GATE_STATUS
    assert row["gate_recommended_next_action"] == "prepare_contrast_dry_run"
    assert row["contrast_class"] == "long_lived_specific_interface_divergence"
    assert row["contrast_checkpoint_policy"] == "technical_checkpoint_no_claim"
    assert "not a validated biological signal" in row["contrast_checkpoint_note"]


def test_build_gated_longevity_contrast_returns_empty_when_no_gate_rows_are_eligible() -> None:
    all_blocked = gate_rows(
        eligible_status="blocked_strict_panel",
        blocked_status="blocked_negatome_repair_policy",
    )

    contrast = stage.build_gated_longevity_contrast(
        enrichment=enrichment_rows(),
        candidate_gate=all_blocked,
        short_lived_species=["mouse"],
        long_lived_species=["naked_mole_rat"],
    )

    assert contrast.is_empty()
    assert contrast.columns == list(stage.GATED_CONTRAST_SCHEMA)


def test_blocked_contrast_gate_rows_records_noneligible_rows() -> None:
    blocked = stage.blocked_contrast_gate_rows(gate_rows())

    assert blocked.height == 1
    row = blocked.row(0, named=True)
    assert row["candidate_id"] == "blocked_candidate"
    assert row["strict_contrast_gate_status"] == "blocked_negatome_repair_policy"
    assert row["recommended_next_action"] == "complete_negatome_repair_before_controlled_claim"


def test_eligible_gate_rows_validates_required_columns() -> None:
    with pytest.raises(ValueError, match="candidate_gate is missing required columns"):
        stage.eligible_gate_rows(gate_rows().drop("gate_note"))


def test_build_gated_longevity_contrast_returns_empty_when_enrichment_has_no_matching_candidate() -> (
    None
):
    missing_enrichment = enrichment_rows().with_columns(
        pl.lit("other_candidate").alias("complex_id")
    )

    contrast = stage.build_gated_longevity_contrast(
        enrichment=missing_enrichment,
        candidate_gate=gate_rows(),
        short_lived_species=["mouse"],
        long_lived_species=["naked_mole_rat"],
    )

    assert contrast.is_empty()
