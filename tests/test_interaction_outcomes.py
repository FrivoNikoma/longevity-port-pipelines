from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.interaction_outcomes import (
    assay_priority,
    build_interaction_outcome_summary,
    classify_outcome,
    confidence_label,
    directional_p,
    engineering_priority,
    residue_summary,
)


def signal_row(
    *,
    signal_class: str,
    effect_size: float,
    p_greater: float = 0.001,
    p_less: float = 0.999,
) -> dict[str, object]:
    return {
        "complex_id": "c1",
        "chain": "receptor",
        "target_species": "mouse",
        "enrichment_ratio": 0.75,
        "effect_size_cohens_d": effect_size,
        "p_interface_greater": p_greater,
        "p_interface_less": p_less,
        "signal_class": signal_class,
        "biological_context": "test context",
    }


def residue_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["c1", "c1", "c2"],
            "chain": ["receptor", "receptor", "ligand"],
            "target_species": ["mouse", "mouse", "mouse"],
            "residue_number_1based": [10, 20, 30],
            "residue_aa": ["A", "G", "S"],
            "delta": [1.2345, 0.4567, 0.1],
        }
    )


def test_directional_p_uses_greater_for_positive_effect() -> None:
    row = signal_row(signal_class="interface_divergent", effect_size=0.5, p_greater=0.007)
    assert directional_p(row) == pytest.approx(0.007)


def test_directional_p_uses_less_for_negative_effect() -> None:
    row = signal_row(signal_class="interface_constrained", effect_size=-0.5, p_less=0.008)
    assert directional_p(row) == pytest.approx(0.008)


def test_confidence_label_high_medium_low_very_low() -> None:
    assert confidence_label(0.6, 0.001) == "high"
    assert confidence_label(0.3, 0.02) == "medium"
    assert confidence_label(0.3, 0.2) == "low"
    assert confidence_label(0.1, 0.001) == "very_low"


def test_classify_interface_constrained() -> None:
    row = signal_row(signal_class="interface_constrained", effect_size=-0.6, p_less=0.001)
    outcome_class, confidence, rationale = classify_outcome(row)

    assert outcome_class == "maintained_candidate"
    assert confidence == "high"
    assert "conserved interaction surface" in rationale


def test_classify_interface_divergent() -> None:
    row = signal_row(signal_class="interface_divergent", effect_size=0.6, p_greater=0.001)
    outcome_class, confidence, rationale = classify_outcome(row)

    assert outcome_class == "possible_interface_remodeling_or_incompatibility"
    assert confidence == "high"
    assert "interface remodeling" in rationale


def test_assay_and_engineering_priority() -> None:
    assert "medium" in assay_priority("maintained_candidate", "high")
    assert "high" in assay_priority("possible_interface_remodeling_or_incompatibility", "medium")
    assert "high" in engineering_priority(
        "possible_interface_remodeling_or_incompatibility", "medium"
    )


def test_residue_summary_formats_top_hits() -> None:
    summary = residue_summary(
        residue_rows(),
        complex_id="c1",
        chain="receptor",
        target_species="mouse",
    )

    assert summary == "10A:1.234;20G:0.457"


def test_residue_summary_returns_empty_for_missing_columns() -> None:
    summary = residue_summary(
        pl.DataFrame({"complex_id": ["c1"]}),
        complex_id="c1",
        chain="receptor",
        target_species="mouse",
    )

    assert summary == ""


def test_build_interaction_outcome_summary() -> None:
    signal_df = pl.DataFrame(
        [
            signal_row(
                signal_class="interface_constrained",
                effect_size=-0.6,
                p_less=0.001,
            ),
            signal_row(
                signal_class="weak_or_mixed",
                effect_size=0.1,
                p_greater=0.5,
                p_less=0.5,
            ),
        ]
    )

    outcome = build_interaction_outcome_summary(
        signal_df=signal_df,
        top_divergent_df=residue_rows(),
        top_constrained_df=residue_rows(),
    )

    assert outcome.height == 2
    assert outcome.filter(pl.col("proposal_outcome_class") == "maintained_candidate").height == 1
    assert outcome.filter(pl.col("proposal_outcome_class") == "unresolved").height == 1


def test_build_interaction_outcome_summary_requires_signal_columns() -> None:
    with pytest.raises(ValueError, match="Signal summary is missing required columns"):
        build_interaction_outcome_summary(
            signal_df=pl.DataFrame({"complex_id": ["c1"]}),
            top_divergent_df=pl.DataFrame(),
            top_constrained_df=pl.DataFrame(),
        )
