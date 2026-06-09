from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.scorecard import (
    action_recommendation,
    biological_process,
    build_candidate_scorecard,
    control_interpretation,
    numeric_score,
    prepare_negative_control_audit,
    protein_label,
    summarize_recurrent_counts,
)


def outcome_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["8bot__U1_P13010--8bot__T1_P12956"],
            "chain": ["receptor"],
            "target_species": ["mouse"],
            "proposal_outcome_class": ["maintained_candidate"],
            "confidence": ["high"],
            "effect_size_cohens_d": [-0.7],
            "p_directional": [0.0001],
            "enrichment_ratio": [0.75],
            "signal_class": ["interface_constrained"],
            "assay_priority": ["medium"],
            "engineering_priority": ["low"],
            "top_divergent_interface_residues": ["1N:1.191"],
            "top_constrained_interface_residues": ["331C:0.148"],
            "biological_context": ["Ku70/Ku80 DNA repair complex"],
            "rationale": ["Strong constrained interface signal."],
        }
    )


def recurrent_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "candidate_type": ["constrained", "constrained", "divergent"],
            "complex_id": [
                "8bot__U1_P13010--8bot__T1_P12956",
                "8bot__U1_P13010--8bot__T1_P12956",
                "8bot__U1_P13010--8bot__T1_P12956",
            ],
            "chain": ["receptor", "receptor", "receptor"],
            "residue_number_1based": [331, 302, 1],
            "residue_aa": ["C", "G", "N"],
            "n_species": [2, 2, 1],
            "mean_delta": [0.148, 0.146, 1.191],
        }
    )


def negative_control_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["8bot__U1_P13010--8bot__T1_P12956"],
            "chain": ["receptor"],
            "target_species": ["mouse"],
            "control_status": ["missing_negatome"],
            "shuffled_control_ratio": [1.0],
            "negatome_control_ratio": [None],
            "ratio_vs_shuffled_control": [0.75],
            "ratio_vs_negatome_control": [None],
            "control_note": ["Shuffled-only evidence."],
        }
    )


def test_protein_label_known_complexes() -> None:
    assert protein_label("8bot__U1_P13010--8bot__T1_P12956", "receptor") == "Ku70 / XRCC6"
    assert protein_label("8bot__U1_P13010--8bot__T1_P12956", "ligand") == "Ku80 / XRCC5"
    assert protein_label("7s68__D1_P09874--7s68__C1_P09874", "receptor") == "PARP1"
    assert protein_label("8f86__K1_Q8N6T7--8f86__A1_P84233", "receptor") == "SIRT6"


def test_biological_process_known_complex() -> None:
    assert "double-strand break repair" in biological_process(
        "8bot__U1_P13010--8bot__T1_P12956", "receptor"
    )


def test_control_interpretation_missing_negatome() -> None:
    assert control_interpretation("missing_negatome") == "shuffled_only_missing_negatome"


def test_action_recommendation_appends_control_warning() -> None:
    recommendation = action_recommendation(
        outcome_class="maintained_candidate",
        confidence="high",
        engineering_priority="low",
        assay_priority="medium",
        control_status="missing_negatome",
    )

    assert "likely maintained-interface candidate" in recommendation
    assert "NEGATOME-style control is currently missing" in recommendation


def test_numeric_score_rewards_confidence_pvalue_and_recurrence() -> None:
    high_score = numeric_score(
        outcome_class="maintained_candidate",
        confidence="high",
        effect_size=-0.7,
        p_directional=0.0001,
        n_recurrent_residues=5,
    )
    low_score = numeric_score(
        outcome_class="unresolved",
        confidence="very_low",
        effect_size=0.0,
        p_directional=0.5,
        n_recurrent_residues=0,
    )

    assert high_score > low_score


def test_summarize_recurrent_counts() -> None:
    recurrent = summarize_recurrent_counts(recurrent_rows())

    row = recurrent.filter(
        (pl.col("candidate_type") == "constrained")
        & (pl.col("complex_id") == "8bot__U1_P13010--8bot__T1_P12956")
    ).row(0, named=True)

    assert row["n_recurrent_residues"] == 2
    assert "331C:2sp" in row["recurrent_residue_summary"]


def test_prepare_negative_control_audit_adds_interpretation() -> None:
    audit = prepare_negative_control_audit(negative_control_rows())
    row = audit.row(0, named=True)

    assert row["control_interpretation"] == "shuffled_only_missing_negatome"


def test_build_candidate_scorecard() -> None:
    scorecard = build_candidate_scorecard(
        outcomes=outcome_rows(),
        recurrent_counts=summarize_recurrent_counts(recurrent_rows()),
        negative_control_audit=prepare_negative_control_audit(negative_control_rows()),
    )

    row = scorecard.row(0, named=True)

    assert row["candidate_id"] == "8bot__U1_P13010--8bot__T1_P12956/receptor/mouse"
    assert row["protein"] == "Ku70 / XRCC6"
    assert row["control_status"] == "missing_negatome"
    assert row["control_interpretation"] == "shuffled_only_missing_negatome"
    assert row["n_recurrent_constrained_residues"] == 2
    assert "NEGATOME-style control is currently missing" in row["recommended_next_action"]


def test_build_candidate_scorecard_requires_outcome_columns() -> None:
    with pytest.raises(ValueError, match="Outcome summary is missing required columns"):
        build_candidate_scorecard(
            outcomes=pl.DataFrame({"complex_id": ["x"]}),
            recurrent_counts=summarize_recurrent_counts(recurrent_rows()),
            negative_control_audit=prepare_negative_control_audit(negative_control_rows()),
        )
