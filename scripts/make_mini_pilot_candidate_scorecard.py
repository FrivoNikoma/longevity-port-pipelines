from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a candidate scorecard from mini-pilot outcome and residue-level summaries."
    )
    parser.add_argument(
        "--outcomes",
        default="data/output/sirt6_mini_pilot_interaction_outcome_summary.csv",
        help="Interaction outcome summary CSV.",
    )
    parser.add_argument(
        "--recurrent-residues",
        default="data/output/sirt6_mini_pilot_recurrent_interface_residues.csv",
        help="Recurrent residue candidates CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_candidate_scorecard.csv",
        help="Output candidate scorecard CSV.",
    )
    return parser.parse_args()


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


def action_recommendation(
    outcome_class: str,
    confidence: str,
    engineering_priority: str,
    assay_priority: str,
) -> str:
    if outcome_class == "maintained_candidate" and confidence == "high":
        return (
            "Treat as a likely maintained-interface candidate. Prioritize as a portability "
            "control or low-engineering transfer candidate; validate binding if selected for wet-lab follow-up."
        )

    if outcome_class == "maintained_candidate":
        return (
            "Keep as a possible maintained-interface candidate. Re-evaluate after expanding "
            "species and complexes before committing to assays."
        )

    if outcome_class == "possible_interface_remodeling_or_incompatibility":
        return (
            "Prioritize structural inspection and multi-partner validation. This may represent "
            "species-specific remodeling, functional breakage, or incompatibility requiring engineering."
        )

    if outcome_class == "possible_interface_remodeling_low_confidence":
        return "Do not prioritize yet. Revisit after adding more species, more partners, or structural visualization."

    if outcome_class == "possible_maintained_low_confidence":
        return "Track as a weak maintained-interface signal. Useful mainly as background evidence."

    if "high" in engineering_priority or "high" in assay_priority:
        return "Review manually because priority flags are high despite unresolved classification."

    return "Do not prioritize in the current mini-pilot; keep for future larger-scale reruns."


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


def load_recurrent_counts(path: Path) -> pl.DataFrame:
    if not path.exists():
        return pl.DataFrame(
            {
                "complex_id": [],
                "chain": [],
                "candidate_type": [],
                "n_recurrent_residues": [],
                "recurrent_residue_summary": [],
            }
        )

    recurrent = pl.read_csv(path)

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
        return pl.DataFrame(
            {
                "complex_id": [],
                "chain": [],
                "candidate_type": [],
                "n_recurrent_residues": [],
                "recurrent_residue_summary": [],
            }
        )

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


def main() -> None:
    args = parse_args()

    outcome_path = Path(args.outcomes)
    recurrent_path = Path(args.recurrent_residues)
    output_path = Path(args.output)

    if not outcome_path.exists():
        raise FileNotFoundError(f"Missing interaction outcome summary: {outcome_path}")

    outcomes = pl.read_csv(outcome_path)
    recurrent_counts = load_recurrent_counts(recurrent_path)

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

    scorecard = scorecard.with_columns(
        [
            pl.col("n_recurrent_divergent_residues").fill_null(0),
            pl.col("n_recurrent_constrained_residues").fill_null(0),
            pl.col("recurrent_divergent_residues").fill_null(""),
            pl.col("recurrent_constrained_residues").fill_null(""),
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
                ),
                "rationale": row["rationale"],
            }
        )

    out_df = pl.DataFrame(rows).sort("score", descending=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.write_csv(output_path)

    print(f"Wrote candidate scorecard -> {output_path}")
    print()
    print("Scorecard shape:")
    print(out_df.shape)

    print()
    print("Top scorecard candidates:")
    print(
        out_df.select(
            [
                "candidate_id",
                "protein",
                "target_species",
                "proposal_outcome_class",
                "confidence",
                "score",
                "effect_size_cohens_d",
                "p_directional",
                "n_recurrent_divergent_residues",
                "n_recurrent_constrained_residues",
                "recommended_next_action",
            ]
        ).head(15)
    )

    print()
    print("Outcome counts:")
    print(
        out_df.group_by(["proposal_outcome_class", "confidence"]).len().sort("len", descending=True)
    )


if __name__ == "__main__":
    main()
