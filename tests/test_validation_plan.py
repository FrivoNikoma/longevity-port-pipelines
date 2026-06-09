from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.validation_plan import (
    build_validation_plan,
    evidence_level,
    validation_priority,
)


def test_evidence_level_missing_negatome_high_confidence() -> None:
    assert evidence_level("missing_negatome", "high") == "preliminary_shuffled_only"


def test_evidence_level_missing_negatome_low_confidence() -> None:
    assert evidence_level("missing_negatome", "very_low") == "low_confidence_shuffled_only"


def test_evidence_level_controlled_high_confidence() -> None:
    assert evidence_level("has_shuffled_and_negatome", "high") == "controlled_high_confidence"


def test_validation_priority_missing_negatome_maintained_high_score() -> None:
    assert (
        validation_priority(
            outcome_class="maintained_candidate",
            confidence="high",
            control_status="missing_negatome",
            score=12.0,
        )
        == "medium_preliminary"
    )


def test_validation_priority_missing_negatome_unresolved_low_confidence() -> None:
    assert (
        validation_priority(
            outcome_class="unresolved",
            confidence="very_low",
            control_status="missing_negatome",
            score=4.0,
        )
        == "defer"
    )


def test_validation_priority_controlled_remodeling_high_confidence() -> None:
    assert (
        validation_priority(
            outcome_class="possible_interface_remodeling_or_incompatibility",
            confidence="high",
            control_status="has_shuffled_and_negatome",
            score=11.0,
        )
        == "high"
    )


def test_build_validation_plan_requires_scorecard_columns() -> None:
    with pytest.raises(ValueError, match="Scorecard is missing required columns"):
        build_validation_plan(pl.DataFrame({"candidate_id": ["x"]}))


def test_build_validation_plan_marks_missing_negatome_as_preliminary() -> None:
    scorecard = pl.DataFrame(
        {
            "candidate_id": ["candidate-1"],
            "protein": ["Ku70 / XRCC6"],
            "target_species": ["mouse"],
            "biological_process": ["DNA double-strand break repair / non-homologous end joining"],
            "proposal_outcome_class": ["maintained_candidate"],
            "confidence": ["high"],
            "score": [12.0],
            "effect_size_cohens_d": [-0.7],
            "p_directional": [0.0001],
            "control_status": ["missing_negatome"],
            "assay_priority": ["medium"],
            "engineering_priority": ["low"],
            "top_divergent_interface_residues": [""],
            "top_constrained_interface_residues": ["331C:0.148"],
            "recommended_next_action": ["Treat as maintained candidate."],
        }
    )

    plan = build_validation_plan(scorecard)
    row = plan.row(0, named=True)

    assert row["evidence_level"] == "preliminary_shuffled_only"
    assert row["validation_priority"] == "medium_preliminary"
    assert "Interaction-retention assay" in row["primary_validation_assay"]
    assert "NEGATOME-style" in row["control_requirement"]
