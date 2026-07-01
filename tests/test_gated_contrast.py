from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages.gated_contrast import (
    GATED_CONTRAST_SCHEMA,
    build_generic_gated_contrast,
    gated_contrast_status_counts,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/generic_gated_contrast_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def gated_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    return pl.DataFrame(
        rows,
        schema={
            "candidate_set": pl.Utf8,
            "lane_name": pl.Utf8,
            "candidate_id": pl.Utf8,
            "pdb_id": pl.Utf8,
            "chain": pl.Utf8,
            "source_uniprot": pl.Utf8,
            "priority": pl.Utf8,
            "strict_panel_status": pl.Utf8,
            "contrast_dry_run_allowed": pl.Boolean,
            "controlled_claim_allowed": pl.Boolean,
            "target_species": pl.Utf8,
            "target_species_taxid": pl.Int64,
            "species_group": pl.Utf8,
            "enrichment_ratio": pl.Float64,
            "effect_size": pl.Float64,
            "interface_mean_delta": pl.Float64,
            "noninterface_mean_delta": pl.Float64,
            "p_two_sided": pl.Float64,
            "is_predicted_structure": pl.Boolean,
            "claim_policy": pl.Utf8,
        },
    )


def _row(
    *,
    target_species: str,
    target_species_taxid: int,
    species_group: str,
    enrichment_ratio: float,
    effect_size: float,
    strict_panel_status: str = "strict_panel_ready",
    contrast_dry_run_allowed: bool = True,
    candidate_id: str = "candidate_a",
    priority: str = "1",
) -> dict[str, object]:
    return {
        "candidate_set": "demo_set",
        "lane_name": "demo_lane",
        "candidate_id": candidate_id,
        "pdb_id": "4xhu",
        "chain": "receptor",
        "source_uniprot": "P09874",
        "priority": priority,
        "strict_panel_status": strict_panel_status,
        "contrast_dry_run_allowed": contrast_dry_run_allowed,
        "controlled_claim_allowed": False,
        "target_species": target_species,
        "target_species_taxid": target_species_taxid,
        "species_group": species_group,
        "enrichment_ratio": enrichment_ratio,
        "effect_size": effect_size,
        "interface_mean_delta": 0.2,
        "noninterface_mean_delta": 0.05,
        "p_two_sided": 0.05,
        "is_predicted_structure": False,
        "claim_policy": "no_biological_claims_until_validation",
    }


def ready_input() -> pl.DataFrame:
    return gated_rows(
        [
            _row(
                target_species="naked_mole_rat",
                target_species_taxid=10181,
                species_group="long_lived_small_body",
                enrichment_ratio=1.8,
                effect_size=0.9,
            ),
            _row(
                target_species="mouse",
                target_species_taxid=10090,
                species_group="short_lived_control",
                enrichment_ratio=1.0,
                effect_size=0.0,
            ),
        ]
    )


def test_gated_contrast_schema_matches_yaml_required_outputs() -> None:
    schema = load_schema()

    assert list(GATED_CONTRAST_SCHEMA) == schema["required_output_fields"]


def test_build_generic_gated_contrast_marks_ready_candidate() -> None:
    contrast = build_generic_gated_contrast(ready_input())

    assert contrast.height == 1
    row = contrast.row(0, named=True)

    assert row["candidate_set"] == "demo_set"
    assert row["candidate_id"] == "candidate_a"
    assert row["long_lived_species"] == "naked_mole_rat"
    assert row["short_lived_species"] == "mouse"
    assert row["short_lived_control_count"] == 1
    assert row["long_enrichment_ratio"] == pytest.approx(1.8)
    assert row["short_enrichment_ratio"] == pytest.approx(1.0)
    assert row["enrichment_delta"] == pytest.approx(0.8)
    assert row["enrichment_log2_ratio"] == pytest.approx(0.8479969)
    assert row["contrast_class"] == "long_lived_specific_interface_divergence"
    assert row["contrast_priority"] == 1
    assert row["has_multiple_short_lived_controls"] is False
    assert row["has_multiple_long_lived_species"] is False
    assert row["short_lived_baseline_is_single_species"] is True
    assert row["contrast_class_is_directional"] is True
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "technical_single_baseline_review"
    assert "single-species" in row["robustness_note"]
    assert row["contrast_status"] == "technical_contrast_ready"
    assert (
        row["recommended_next_action"]
        == "review_technical_contrast_checkpoint_without_biological_claims"
    )
    assert row["contrast_dry_run_allowed"] is True
    assert row["controlled_claim_allowed"] is False
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "technical_contrast_checkpoint"
    assert "not a biological claim" in row["contrast_note"]


def test_build_generic_gated_contrast_allows_limited_dry_run() -> None:
    contrast = build_generic_gated_contrast(
        gated_rows(
            [
                _row(
                    target_species="naked_mole_rat",
                    target_species_taxid=10181,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.8,
                    effect_size=0.9,
                    strict_panel_status="strict_panel_accepted_for_limited_dry_run",
                ),
                _row(
                    target_species="mouse",
                    target_species_taxid=10090,
                    species_group="short_lived_control",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                    strict_panel_status="strict_panel_accepted_for_limited_dry_run",
                ),
            ]
        )
    )

    row = contrast.row(0, named=True)

    assert row["contrast_status"] == "technical_contrast_limited_dry_run"
    assert row["recommended_next_action"] == "review_limited_technical_contrast_with_caveat"
    assert row["contrast_dry_run_allowed"] is True
    assert row["controlled_claim_allowed"] is False
    assert row["contrast_class_is_directional"] is True
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "technical_limited_dry_run_review"


def test_build_generic_gated_contrast_blocks_strict_panel_not_ready() -> None:
    contrast = build_generic_gated_contrast(
        gated_rows(
            [
                _row(
                    target_species="naked_mole_rat",
                    target_species_taxid=10181,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.8,
                    effect_size=0.9,
                    strict_panel_status="blocked_control_readiness",
                    contrast_dry_run_allowed=False,
                ),
                _row(
                    target_species="mouse",
                    target_species_taxid=10090,
                    species_group="short_lived_control",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                    strict_panel_status="blocked_control_readiness",
                    contrast_dry_run_allowed=False,
                ),
            ]
        )
    )

    assert contrast.height == 1
    row = contrast.row(0, named=True)

    assert row["contrast_status"] == "blocked_strict_panel_not_ready"
    assert row["recommended_next_action"] == "resolve_strict_panel_before_contrast"
    assert row["contrast_dry_run_allowed"] is False
    assert row["contrast_class"] == "weak_or_unresolved_contrast"
    assert row["contrast_class_is_directional"] is False
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "blocked_before_robustness_review"


def test_build_generic_gated_contrast_blocks_missing_long_lived_rows() -> None:
    contrast = build_generic_gated_contrast(
        gated_rows(
            [
                _row(
                    target_species="mouse",
                    target_species_taxid=10090,
                    species_group="short_lived_control",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                )
            ]
        )
    )

    row = contrast.row(0, named=True)

    assert row["contrast_status"] == "blocked_missing_long_lived_rows"
    assert row["recommended_next_action"] == "add_ready_long_lived_rows_before_contrast"
    assert row["contrast_class_is_directional"] is False
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "blocked_before_robustness_review"


def test_build_generic_gated_contrast_blocks_missing_short_lived_controls() -> None:
    contrast = build_generic_gated_contrast(
        gated_rows(
            [
                _row(
                    target_species="naked_mole_rat",
                    target_species_taxid=10181,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.8,
                    effect_size=0.9,
                )
            ]
        )
    )

    row = contrast.row(0, named=True)

    assert row["contrast_status"] == "blocked_missing_short_lived_controls"
    assert row["recommended_next_action"] == "add_ready_short_lived_control_rows_before_contrast"
    assert row["contrast_class_is_directional"] is False
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "blocked_before_robustness_review"


def test_build_generic_gated_contrast_blocks_missing_metrics() -> None:
    frame = ready_input().with_columns(pl.lit(None).cast(pl.Float64).alias("p_two_sided"))

    contrast = build_generic_gated_contrast(frame)
    row = contrast.row(0, named=True)

    assert row["contrast_status"] == "blocked_missing_required_metrics"
    assert row["recommended_next_action"] == "compute_required_metrics_before_contrast"
    assert row["contrast_class_is_directional"] is False
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "blocked_before_robustness_review"


def test_build_generic_gated_contrast_aggregates_multiple_short_lived_controls() -> None:
    contrast = build_generic_gated_contrast(
        gated_rows(
            [
                _row(
                    target_species="naked_mole_rat",
                    target_species_taxid=10181,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.8,
                    effect_size=0.9,
                ),
                _row(
                    target_species="mouse",
                    target_species_taxid=10090,
                    species_group="short_lived_control",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                ),
                _row(
                    target_species="rat",
                    target_species_taxid=10116,
                    species_group="short_lived_control",
                    enrichment_ratio=1.2,
                    effect_size=0.2,
                ),
                _row(
                    target_species="hamster",
                    target_species_taxid=10036,
                    species_group="short_lived_control",
                    enrichment_ratio=0.8,
                    effect_size=-0.2,
                ),
            ]
        )
    )

    row = contrast.row(0, named=True)

    assert row["short_lived_species"] == "hamster,mouse,rat"
    assert row["short_lived_control_count"] == 3
    assert row["short_enrichment_ratio"] == pytest.approx(1.0)
    assert row["contrast_class"] == "long_lived_specific_interface_divergence"
    assert row["has_multiple_short_lived_controls"] is True
    assert row["short_lived_baseline_is_single_species"] is False
    assert row["has_multiple_long_lived_species"] is False
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "technical_single_long_lived_review"


def test_build_generic_gated_contrast_marks_multiple_long_lived_species() -> None:
    contrast = build_generic_gated_contrast(
        gated_rows(
            [
                _row(
                    target_species="naked_mole_rat",
                    target_species_taxid=10181,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.8,
                    effect_size=0.9,
                ),
                _row(
                    target_species="myotis",
                    target_species_taxid=59463,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.7,
                    effect_size=0.8,
                ),
                _row(
                    target_species="mouse",
                    target_species_taxid=10090,
                    species_group="short_lived_control",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                ),
                _row(
                    target_species="rat",
                    target_species_taxid=10116,
                    species_group="short_lived_control",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                ),
            ]
        )
    )

    assert contrast.height == 2
    assert set(contrast["long_lived_species"].to_list()) == {
        "myotis",
        "naked_mole_rat",
    }

    for row in contrast.iter_rows(named=True):
        assert row["has_multiple_short_lived_controls"] is True
        assert row["has_multiple_long_lived_species"] is True
        assert row["short_lived_baseline_is_single_species"] is False
        assert row["contrast_class_is_directional"] is True
        assert row["contrast_requires_review"] is False
        assert row["robustness_status"] == "technical_multispecies_contrast"


def test_build_generic_gated_contrast_marks_weak_or_unresolved_for_review() -> None:
    contrast = build_generic_gated_contrast(
        gated_rows(
            [
                _row(
                    target_species="naked_mole_rat",
                    target_species_taxid=10181,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.05,
                    effect_size=0.05,
                ),
                _row(
                    target_species="mouse",
                    target_species_taxid=10090,
                    species_group="short_lived_control",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                ),
            ]
        )
    )

    row = contrast.row(0, named=True)

    assert row["contrast_class"] == "weak_or_unresolved_contrast"
    assert row["contrast_class_is_directional"] is False
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "technical_weak_or_unresolved_review"


def test_build_generic_gated_contrast_keeps_multiple_candidates_separate() -> None:
    contrast = build_generic_gated_contrast(
        gated_rows(
            [
                _row(
                    target_species="naked_mole_rat",
                    target_species_taxid=10181,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.8,
                    effect_size=0.9,
                    candidate_id="candidate_a",
                    priority="1",
                ),
                _row(
                    target_species="mouse",
                    target_species_taxid=10090,
                    species_group="short_lived_control",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                    candidate_id="candidate_a",
                    priority="1",
                ),
                _row(
                    target_species="naked_mole_rat",
                    target_species_taxid=10181,
                    species_group="long_lived_small_body",
                    enrichment_ratio=1.0,
                    effect_size=0.0,
                    candidate_id="candidate_b",
                    priority="2",
                ),
                _row(
                    target_species="mouse",
                    target_species_taxid=10090,
                    species_group="short_lived_control",
                    enrichment_ratio=1.5,
                    effect_size=0.5,
                    candidate_id="candidate_b",
                    priority="2",
                ),
            ]
        )
    )

    assert contrast.height == 2
    assert set(contrast["candidate_id"].to_list()) == {"candidate_a", "candidate_b"}
    assert contrast.row(0, named=True)["candidate_id"] == "candidate_a"


def test_build_generic_gated_contrast_validates_required_columns() -> None:
    frame = ready_input().drop("strict_panel_status")

    with pytest.raises(ValueError, match="gated_contrast_input is missing required columns"):
        build_generic_gated_contrast(frame)


def test_empty_generic_gated_contrast_has_schema() -> None:
    contrast = build_generic_gated_contrast(gated_rows([]))

    assert contrast.is_empty()
    assert contrast.schema == GATED_CONTRAST_SCHEMA


def test_gated_contrast_status_counts_summarizes_rows() -> None:
    contrast = build_generic_gated_contrast(ready_input())

    assert gated_contrast_status_counts(contrast) == {"technical_contrast_ready": 1}
