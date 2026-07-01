from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages import strict_contrast_panel as strict

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/generic_strict_contrast_panel_schema.yaml"


def load_schema() -> dict[str, object]:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def strict_input_rows(
    *,
    control_status: str = "controls_ready",
    candidate_id: str = "candidate_a",
) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_set": "sirt6_dna_repair",
                "lane_name": "sirt6_mini_pilot",
                "candidate_id": candidate_id,
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "mouse",
                "target_species_taxid": 10090,
                "species_group": "short_lived_control",
                "coverage_preflight_status": "coverage_preflight_ready",
                "control_readiness_status": control_status,
                "contrast_readiness_status": "contrast_ready",
                "claim_policy": "no_biological_claims_until_validation",
            },
            {
                "candidate_set": "sirt6_dna_repair",
                "lane_name": "sirt6_mini_pilot",
                "candidate_id": candidate_id,
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "naked_mole_rat",
                "target_species_taxid": 10181,
                "species_group": "long_lived_small_body",
                "coverage_preflight_status": "coverage_preflight_ready",
                "control_readiness_status": control_status,
                "contrast_readiness_status": "contrast_ready",
                "claim_policy": "no_biological_claims_until_validation",
            },
        ]
    )


def blocked_manual_review_rows() -> pl.DataFrame:
    blocked = pl.DataFrame(
        [
            {
                "candidate_set": "sirt6_dna_repair",
                "lane_name": "sirt6_mini_pilot",
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "bowhead_whale",
                "target_species_taxid": 27622,
                "species_group": "long_lived_large_body",
                "coverage_preflight_status": "blocked_needs_manual_review",
                "control_readiness_status": "controls_ready",
                "contrast_readiness_status": "contrast_ready",
                "claim_policy": "no_biological_claims_until_validation",
            }
        ]
    )
    return pl.concat([strict_input_rows(), blocked], how="vertical")


def test_generic_strict_panel_summary_schema_matches_yaml_required_outputs() -> None:
    schema = load_schema()

    assert list(strict.STRICT_PANEL_SUMMARY_SCHEMA) == schema["required_output_fields"]


def test_build_generic_strict_panel_summary_marks_ready_candidate() -> None:
    summary = strict.build_generic_strict_panel_summary(strict_input_rows())

    row = summary.row(0, named=True)
    assert row["candidate_set"] == "sirt6_dna_repair"
    assert row["lane_name"] == "sirt6_mini_pilot"
    assert row["strict_panel_status"] == "strict_panel_ready"
    assert row["recommended_next_action"] == (
        "run_strict_contrast_dry_run_without_biological_claims"
    )
    assert row["contrast_dry_run_allowed"] is True
    assert row["controlled_claim_allowed"] is False
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "strict_panel_readiness"
    assert row["n_strict_panel_ready_species"] == 2
    assert row["n_strict_panel_blocked_species"] == 0
    assert row["n_strict_long_lived_ready"] == 1
    assert row["n_strict_short_lived_ready"] == 1
    assert row["strict_long_lived_species"] == "naked_mole_rat"
    assert row["strict_short_lived_species"] == "mouse"
    assert row["blocked_target_species"] == ""
    assert row["coverage_preflight_statuses"] == "coverage_preflight_ready"
    assert row["control_readiness_statuses"] == "controls_ready"
    assert "not a biological claim" in row["strict_panel_note"]


def test_build_generic_strict_panel_summary_blocks_manual_review_rows() -> None:
    summary = strict.build_generic_strict_panel_summary(blocked_manual_review_rows())

    row = summary.row(0, named=True)
    assert row["strict_panel_status"] == "needs_manual_review"
    assert row["recommended_next_action"] == "perform_manual_strict_panel_review"
    assert row["contrast_dry_run_allowed"] is False
    assert row["controlled_claim_allowed"] is False
    assert row["n_strict_panel_ready_species"] == 2
    assert row["n_strict_panel_blocked_species"] == 1
    assert row["strict_long_lived_species"] == "naked_mole_rat"
    assert row["strict_short_lived_species"] == "mouse"
    assert row["blocked_target_species"] == "bowhead_whale"
    assert row["coverage_preflight_statuses"] == (
        "blocked_needs_manual_review,coverage_preflight_ready"
    )


def test_build_generic_strict_panel_summary_blocks_control_readiness() -> None:
    summary = strict.build_generic_strict_panel_summary(
        strict_input_rows(control_status="blocked_missing_negatome_control")
    )

    row = summary.row(0, named=True)
    assert row["strict_panel_status"] == "blocked_control_readiness"
    assert row["recommended_next_action"] == "resolve_control_readiness_before_strict_panel"
    assert row["contrast_dry_run_allowed"] is False
    assert row["control_readiness_statuses"] == "blocked_missing_negatome_control"


def test_build_generic_strict_panel_summary_allows_limited_control_dry_run() -> None:
    summary = strict.build_generic_strict_panel_summary(
        strict_input_rows(control_status="controls_accepted_for_limited_dry_run")
    )

    row = summary.row(0, named=True)
    assert row["strict_panel_status"] == "strict_panel_accepted_for_limited_dry_run"
    assert row["recommended_next_action"] == "run_limited_strict_contrast_dry_run_with_caveat"
    assert row["contrast_dry_run_allowed"] is True
    assert row["controlled_claim_allowed"] is False


def test_build_generic_strict_panel_summary_blocks_insufficient_short_lived_species() -> None:
    only_long_lived = strict_input_rows().filter(pl.col("target_species") != "mouse")

    summary = strict.build_generic_strict_panel_summary(only_long_lived)

    row = summary.row(0, named=True)
    assert row["strict_panel_status"] == "insufficient_strict_short_lived_species"
    assert row["recommended_next_action"] == "add_ready_short_lived_control_species"
    assert row["contrast_dry_run_allowed"] is False
    assert row["n_strict_long_lived_ready"] == 1
    assert row["n_strict_short_lived_ready"] == 0


def test_build_generic_strict_panel_summary_keeps_multiple_candidates_separate() -> None:
    inputs = pl.concat(
        [
            strict_input_rows(candidate_id="candidate_a"),
            strict_input_rows(candidate_id="candidate_b"),
        ],
        how="vertical",
    )

    summary = strict.build_generic_strict_panel_summary(inputs)

    assert summary.height == 2
    assert set(summary.get_column("candidate_id").to_list()) == {
        "candidate_a",
        "candidate_b",
    }


def test_build_generic_strict_panel_summary_validates_required_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        strict.build_generic_strict_panel_summary(pl.DataFrame({"candidate_id": ["candidate_a"]}))


def test_empty_generic_strict_panel_summary_has_schema() -> None:
    summary = strict.build_generic_strict_panel_summary(strict_input_rows().head(0))

    assert summary.is_empty()
    assert summary.columns == list(strict.STRICT_PANEL_SUMMARY_SCHEMA)


def test_strict_panel_status_counts_summarizes_rows() -> None:
    summary = strict.build_generic_strict_panel_summary(
        pl.concat(
            [
                strict_input_rows(candidate_id="candidate_a"),
                strict_input_rows(
                    candidate_id="candidate_b",
                    control_status="blocked_missing_negatome_control",
                ),
            ],
            how="vertical",
        )
    )

    assert strict.strict_panel_status_counts(summary) == {
        "blocked_control_readiness": 1,
        "strict_panel_ready": 1,
    }
