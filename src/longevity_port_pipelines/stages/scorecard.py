from __future__ import annotations

from pathlib import Path

import polars as pl


def biological_process(complex_id: str, chain: str) -> str:
    if "8bot" in complex_id:
        return "DNA double-strand break repair / non-homologous end joining"

    if "7s68" in complex_id:
        return "DNA damage sensing / PARP1-mediated repair signaling"

    if "8f86" in complex_id:
        if chain == "receptor":
            return "SIRT6 chromatin interaction / histone-associated DNA repair regulation"
        return "Histone H3 chromatin substrate context"

    return "unannotated"


def protein_label(complex_id: str, chain: str) -> str:
    if "8bot" in complex_id:
        if chain == "receptor":
            return "Ku70 / XRCC6"
        if chain == "ligand":
            return "Ku80 / XRCC5"

    if "7s68" in complex_id:
        return "PARP1"

    if "8f86" in complex_id:
        if chain == "receptor":
            return "SIRT6"
        if chain == "ligand":
            return "Histone H3"

    return chain


def control_interpretation(control_status: str) -> str:
    if control_status == "has_shuffled_and_negatome":
        return "shuffled_and_negatome_controls"

    if control_status == "missing_negatome":
        return "shuffled_only_missing_negatome"

    if control_status == "missing_shuffled":
        return "negatome_only_missing_shuffled"

    if control_status == "missing_all_controls":
        return "missing_all_controls"

    return "control_status_unknown"


def append_control_warning(recommendation: str, control_status: str) -> str:
    if control_status == "has_shuffled_and_negatome":
        return recommendation

    if control_status == "missing_negatome":
        return (
            f"{recommendation} Control note: NEGATOME-style control is currently missing; "
            "treat as shuffled-control-only evidence."
        )

    if control_status == "missing_shuffled":
        return (
            f"{recommendation} Control note: shuffled-mask control is missing; inspect before "
            "using this candidate for prioritization."
        )

    return (
        f"{recommendation} Control note: negative-control coverage is incomplete; do not treat "
        "this as fully controlled enrichment evidence."
    )


def action_recommendation(
    outcome_class: str,
    confidence: str,
    engineering_priority: str,
    assay_priority: str,
    control_status: str,
) -> str:
    if outcome_class == "maintained_candidate" and confidence == "high":
        recommendation = (
            "Treat as a likely maintained-interface candidate. Prioritize as a portability "
            "control or low-engineering transfer candidate; validate binding if selected for wet-lab follow-up."
        )
        return append_control_warning(recommendation, control_status)

    if outcome_class == "maintained_candidate":
        recommendation = (
            "Keep as a possible maintained-interface candidate. Re-evaluate after expanding "
            "species and complexes before committing to assays."
        )
        return append_control_warning(recommendation, control_status)

    if outcome_class == "possible_interface_remodeling_or_incompatibility":
        recommendation = (
            "Prioritize structural inspection and multi-partner validation. This may represent "
            "species-specific remodeling, functional breakage, or incompatibility requiring engineering."
        )
        return append_control_warning(recommendation, control_status)

    if outcome_class == "possible_interface_remodeling_low_confidence":
        recommendation = (
            "Do not prioritize yet. Revisit after adding more species, more partners, "
            "or structural visualization."
        )
        return append_control_warning(recommendation, control_status)

    if outcome_class == "possible_maintained_low_confidence":
        recommendation = (
            "Track as a weak maintained-interface signal. Useful mainly as background evidence."
        )
        return append_control_warning(recommendation, control_status)

    if "high" in engineering_priority or "high" in assay_priority:
        recommendation = (
            "Review manually because priority flags are high despite unresolved classification."
        )
        return append_control_warning(recommendation, control_status)

    recommendation = (
        "Do not prioritize in the current mini-pilot; keep for future larger-scale reruns."
    )
    return append_control_warning(recommendation, control_status)


def numeric_score(
    outcome_class: str,
    confidence: str,
    effect_size: float,
    p_directional: float,
    n_recurrent_residues: int,
) -> float:
    confidence_score = {
        "high": 4.0,
        "medium": 3.0,
        "low": 2.0,
        "very_low": 1.0,
    }.get(confidence, 0.0)

    outcome_score = {
        "possible_interface_remodeling_or_incompatibility": 4.0,
        "maintained_candidate": 3.0,
        "possible_interface_remodeling_low_confidence": 2.0,
        "possible_maintained_low_confidence": 2.0,
        "unresolved": 0.5,
    }.get(outcome_class, 0.0)

    p_score = 0.0
    if p_directional < 0.001:
        p_score = 3.0
    elif p_directional < 0.01:
        p_score = 2.0
    elif p_directional < 0.05:
        p_score = 1.0

    recurrence_score = min(float(n_recurrent_residues), 5.0) * 0.5

    return outcome_score + confidence_score + abs(effect_size) * 2.0 + p_score + recurrence_score


def empty_recurrent_counts() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [],
            "chain": [],
            "candidate_type": [],
            "n_recurrent_residues": [],
            "recurrent_residue_summary": [],
        }
    )


def summarize_recurrent_counts(recurrent: pl.DataFrame) -> pl.DataFrame:
    required = {
        "candidate_type",
        "complex_id",
        "chain",
        "residue_number_1based",
        "residue_aa",
        "n_species",
        "mean_delta",
    }

    if recurrent.is_empty() or not required.issubset(set(recurrent.columns)):
        return empty_recurrent_counts()

    return (
        recurrent.with_columns(
            (
                pl.col("residue_number_1based").cast(pl.Utf8)
                + pl.col("residue_aa")
                + ":"
                + pl.col("n_species").cast(pl.Utf8)
                + "sp"
            ).alias("residue_hit")
        )
        .group_by(["complex_id", "chain", "candidate_type"])
        .agg(
            [
                pl.len().alias("n_recurrent_residues"),
                pl.col("residue_hit").head(10).str.join(";").alias("recurrent_residue_summary"),
            ]
        )
    )


def load_recurrent_counts(path: Path) -> pl.DataFrame:
    if not path.exists():
        return empty_recurrent_counts()

    return summarize_recurrent_counts(pl.read_csv(path))


def empty_negative_control_audit() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [],
            "chain": [],
            "target_species": [],
            "control_status": [],
            "control_interpretation": [],
            "shuffled_control_ratio": [],
            "negatome_control_ratio": [],
            "ratio_vs_shuffled_control": [],
            "ratio_vs_negatome_control": [],
            "passes_controls": [],
            "control_evidence_tier": [],
            "passes_controls_note": [],
            "control_note": [],
        }
    )


def prepare_negative_control_audit(audit: pl.DataFrame) -> pl.DataFrame:
    required = {
        "complex_id",
        "chain",
        "target_species",
        "control_status",
        "shuffled_control_ratio",
        "negatome_control_ratio",
        "ratio_vs_shuffled_control",
        "ratio_vs_negatome_control",
        "passes_controls",
        "control_evidence_tier",
        "passes_controls_note",
        "control_note",
    }

    if audit.is_empty() or not required.issubset(set(audit.columns)):
        return empty_negative_control_audit()

    return audit.select(
        [
            "complex_id",
            "chain",
            "target_species",
            "control_status",
            "shuffled_control_ratio",
            "negatome_control_ratio",
            "ratio_vs_shuffled_control",
            "ratio_vs_negatome_control",
            "passes_controls",
            "control_evidence_tier",
            "passes_controls_note",
            "control_note",
        ]
    ).with_columns(
        pl.col("control_status")
        .map_elements(control_interpretation, return_dtype=pl.Utf8)
        .alias("control_interpretation")
    )


def load_negative_control_audit(path: Path) -> pl.DataFrame:
    if not path.exists():
        return empty_negative_control_audit()

    return prepare_negative_control_audit(pl.read_csv(path))


def required_outcome_columns() -> set[str]:
    return {
        "complex_id",
        "chain",
        "target_species",
        "proposal_outcome_class",
        "confidence",
        "effect_size_cohens_d",
        "p_directional",
        "enrichment_ratio",
        "signal_class",
        "assay_priority",
        "engineering_priority",
        "top_divergent_interface_residues",
        "top_constrained_interface_residues",
        "biological_context",
        "rationale",
    }


def validate_outcomes(outcomes: pl.DataFrame) -> None:
    missing = required_outcome_columns() - set(outcomes.columns)
    if missing:
        raise ValueError(f"Outcome summary is missing required columns: {sorted(missing)}")


def build_candidate_scorecard(
    outcomes: pl.DataFrame,
    recurrent_counts: pl.DataFrame,
    negative_control_audit: pl.DataFrame,
) -> pl.DataFrame:
    validate_outcomes(outcomes)

    divergent_recurrent = recurrent_counts.filter(pl.col("candidate_type") == "divergent").rename(
        {
            "n_recurrent_residues": "n_recurrent_divergent_residues",
            "recurrent_residue_summary": "recurrent_divergent_residues",
        }
    )

    constrained_recurrent = recurrent_counts.filter(
        pl.col("candidate_type") == "constrained"
    ).rename(
        {
            "n_recurrent_residues": "n_recurrent_constrained_residues",
            "recurrent_residue_summary": "recurrent_constrained_residues",
        }
    )

    scorecard = outcomes.join(
        divergent_recurrent.select(
            [
                "complex_id",
                "chain",
                "n_recurrent_divergent_residues",
                "recurrent_divergent_residues",
            ]
        ),
        on=["complex_id", "chain"],
        how="left",
    ).join(
        constrained_recurrent.select(
            [
                "complex_id",
                "chain",
                "n_recurrent_constrained_residues",
                "recurrent_constrained_residues",
            ]
        ),
        on=["complex_id", "chain"],
        how="left",
    )

    scorecard = scorecard.join(
        negative_control_audit,
        on=["complex_id", "chain", "target_species"],
        how="left",
    )

    scorecard = scorecard.with_columns(
        [
            pl.col("n_recurrent_divergent_residues").fill_null(0),
            pl.col("n_recurrent_constrained_residues").fill_null(0),
            pl.col("recurrent_divergent_residues").fill_null(""),
            pl.col("recurrent_constrained_residues").fill_null(""),
            pl.col("control_status").fill_null("not_audited"),
            pl.col("control_interpretation").fill_null("not_audited"),
            pl.col("passes_controls").fill_null(False),
            pl.col("control_evidence_tier").fill_null("not_audited"),
            pl.col("passes_controls_note").fill_null(""),
            pl.col("control_note").fill_null("Negative-control audit was not available."),
        ]
    )

    rows: list[dict[str, object]] = []
    for row in scorecard.iter_rows(named=True):
        complex_id = str(row["complex_id"])
        chain = str(row["chain"])
        outcome_class = str(row["proposal_outcome_class"])
        confidence = str(row["confidence"])
        effect_size = float(row["effect_size_cohens_d"])
        p_directional = float(row["p_directional"])
        control_status = str(row["control_status"])

        n_recurrent_divergent = int(row["n_recurrent_divergent_residues"])
        n_recurrent_constrained = int(row["n_recurrent_constrained_residues"])

        n_recurrent_for_score = (
            n_recurrent_divergent
            if "remodeling" in outcome_class or "incompatibility" in outcome_class
            else n_recurrent_constrained
        )

        rows.append(
            {
                "candidate_id": f"{complex_id}/{chain}/{row['target_species']}",
                "complex_id": complex_id,
                "chain": chain,
                "protein": protein_label(complex_id, chain),
                "target_species": row["target_species"],
                "biological_process": biological_process(complex_id, chain),
                "proposal_outcome_class": outcome_class,
                "confidence": confidence,
                "score": numeric_score(
                    outcome_class=outcome_class,
                    confidence=confidence,
                    effect_size=effect_size,
                    p_directional=p_directional,
                    n_recurrent_residues=n_recurrent_for_score,
                ),
                "enrichment_ratio": row["enrichment_ratio"],
                "effect_size_cohens_d": effect_size,
                "p_directional": p_directional,
                "signal_class": row["signal_class"],
                "control_status": control_status,
                "control_interpretation": row["control_interpretation"],
                "shuffled_control_ratio": row.get("shuffled_control_ratio"),
                "negatome_control_ratio": row.get("negatome_control_ratio"),
                "ratio_vs_shuffled_control": row.get("ratio_vs_shuffled_control"),
                "ratio_vs_negatome_control": row.get("ratio_vs_negatome_control"),
                "passes_controls": bool(row.get("passes_controls", False)),
                "control_evidence_tier": row.get("control_evidence_tier", "not_audited"),
                "passes_controls_note": row.get("passes_controls_note", ""),
                "control_note": row["control_note"],
                "assay_priority": row["assay_priority"],
                "engineering_priority": row["engineering_priority"],
                "top_divergent_interface_residues": row["top_divergent_interface_residues"],
                "top_constrained_interface_residues": row["top_constrained_interface_residues"],
                "n_recurrent_divergent_residues": n_recurrent_divergent,
                "recurrent_divergent_residues": row["recurrent_divergent_residues"],
                "n_recurrent_constrained_residues": n_recurrent_constrained,
                "recurrent_constrained_residues": row["recurrent_constrained_residues"],
                "biological_context": row["biological_context"],
                "recommended_next_action": action_recommendation(
                    outcome_class=outcome_class,
                    confidence=confidence,
                    engineering_priority=str(row["engineering_priority"]),
                    assay_priority=str(row["assay_priority"]),
                    control_status=control_status,
                ),
                "rationale": row["rationale"],
            }
        )

    return pl.DataFrame(rows).sort("score", descending=True)
