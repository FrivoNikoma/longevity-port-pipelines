from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify mini-pilot interface embedding signals into proposal-level interaction outcomes."
    )
    parser.add_argument(
        "--signal-summary",
        default="data/output/sirt6_mini_pilot_embedding_signal_summary.csv",
        help="Input embedding signal summary CSV.",
    )
    parser.add_argument(
        "--top-divergent",
        default="data/output/sirt6_mini_pilot_top_divergent_interface_residues.csv",
        help="Top divergent residue candidates CSV.",
    )
    parser.add_argument(
        "--top-constrained",
        default="data/output/sirt6_mini_pilot_top_constrained_interface_residues.csv",
        help="Top constrained residue candidates CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_interaction_outcome_summary.csv",
        help="Output interaction outcome summary CSV.",
    )
    return parser.parse_args()


def directional_p(row: dict[str, object]) -> float:
    effect_size = float(row["effect_size_cohens_d"])
    if effect_size >= 0:
        return float(row.get("p_interface_greater", row.get("mann_whitney_p", 1.0)))
    return float(row.get("p_interface_less", 1.0))


def confidence_label(effect_size: float, p_value: float) -> str:
    abs_effect = abs(effect_size)
    if p_value < 0.01 and abs_effect >= 0.5:
        return "high"
    if p_value < 0.05 and abs_effect >= 0.2:
        return "medium"
    if abs_effect >= 0.2:
        return "low"
    return "very_low"


def classify_outcome(row: dict[str, object]) -> tuple[str, str, str]:
    signal_class = str(row["signal_class"])
    effect_size = float(row["effect_size_cohens_d"])
    p_value = directional_p(row)
    confidence = confidence_label(effect_size, p_value)

    if signal_class == "interface_constrained":
        return (
            "maintained_candidate",
            confidence,
            (
                "Interface residues are less divergent than non-interface residues. "
                "This suggests a conserved interaction surface and supports the maintained-interaction branch of the proposal taxonomy."
            ),
        )

    if signal_class == "interface_divergent":
        return (
            "possible_interface_remodeling_or_incompatibility",
            confidence,
            (
                "Interface residues are more divergent than non-interface residues. "
                "This may indicate species-specific interface remodeling, functional breakage, or incompatibility; structural and partner-level validation are needed."
            ),
        )

    if signal_class == "interface_divergent_not_significant":
        return (
            "possible_interface_remodeling_low_confidence",
            confidence,
            (
                "The direction suggests interface divergence, but statistical support is weak in the current mini-pilot. "
                "This should be treated as hypothesis-generating only."
            ),
        )

    if signal_class == "interface_constrained_not_significant":
        return (
            "possible_maintained_low_confidence",
            confidence,
            (
                "The direction suggests interface constraint, but statistical support is weak in the current mini-pilot. "
                "This may become a maintained-interaction candidate with more data."
            ),
        )

    return (
        "unresolved",
        confidence,
        (
            "The interface-vs-background embedding signal is weak or mixed. "
            "No proposal-level interaction outcome should be assigned yet."
        ),
    )


def assay_priority(outcome_class: str, confidence: str) -> str:
    if outcome_class == "maintained_candidate" and confidence in {"high", "medium"}:
        return "medium: verify preservation of key binding partner if candidate is prioritized"

    if outcome_class == "possible_interface_remodeling_or_incompatibility":
        return "high: inspect structure and test multiple partners before engineering decisions"

    if outcome_class == "possible_interface_remodeling_low_confidence":
        return "low: revisit after expanding species and complexes"

    if outcome_class == "possible_maintained_low_confidence":
        return "low: keep as background conserved-interface signal"

    return "low: insufficient signal for assay planning"


def engineering_priority(outcome_class: str, confidence: str) -> str:
    if outcome_class == "possible_interface_remodeling_or_incompatibility" and confidence in {
        "high",
        "medium",
    }:
        return "high: candidate for chimera/interface compatibility analysis"

    if outcome_class == "maintained_candidate" and confidence == "high":
        return "low: likely portable without interface engineering"

    if outcome_class == "maintained_candidate":
        return "medium-low: validate before assuming portability"

    return "low: not enough evidence for engineering"


def load_optional_residue_table(path: Path) -> pl.DataFrame:
    if path.exists():
        return pl.read_csv(path)
    return pl.DataFrame()


def residue_summary(
    residue_df: pl.DataFrame,
    *,
    complex_id: str,
    chain: str,
    target_species: str,
    top_n: int = 5,
) -> str:
    if residue_df.is_empty():
        return ""

    required = {
        "complex_id",
        "chain",
        "target_species",
        "residue_number_1based",
        "residue_aa",
        "delta",
    }
    if not required.issubset(set(residue_df.columns)):
        return ""

    hits = (
        residue_df.filter(
            (pl.col("complex_id") == complex_id)
            & (pl.col("chain") == chain)
            & (pl.col("target_species") == target_species)
        )
        .head(top_n)
        .select(["residue_number_1based", "residue_aa", "delta"])
    )

    if hits.is_empty():
        return ""

    return ";".join(
        f"{int(row['residue_number_1based'])}{row['residue_aa']}:{float(row['delta']):.3f}"
        for row in hits.iter_rows(named=True)
    )


def main() -> None:
    args = parse_args()

    signal_path = Path(args.signal_summary)
    top_divergent_path = Path(args.top_divergent)
    top_constrained_path = Path(args.top_constrained)
    output_path = Path(args.output)

    if not signal_path.exists():
        raise FileNotFoundError(f"Missing signal summary CSV: {signal_path}")

    signal_df = pl.read_csv(signal_path)
    top_divergent_df = load_optional_residue_table(top_divergent_path)
    top_constrained_df = load_optional_residue_table(top_constrained_path)

    rows: list[dict[str, object]] = []

    for row in signal_df.iter_rows(named=True):
        complex_id = str(row["complex_id"])
        chain = str(row["chain"])
        target_species = str(row["target_species"])
        effect_size = float(row["effect_size_cohens_d"])
        p_value = directional_p(row)

        outcome_class, confidence, rationale = classify_outcome(row)

        top_divergent_residues = residue_summary(
            top_divergent_df,
            complex_id=complex_id,
            chain=chain,
            target_species=target_species,
        )
        top_constrained_residues = residue_summary(
            top_constrained_df,
            complex_id=complex_id,
            chain=chain,
            target_species=target_species,
        )

        rows.append(
            {
                "complex_id": complex_id,
                "chain": chain,
                "target_species": target_species,
                "enrichment_ratio": float(row["enrichment_ratio"]),
                "effect_size_cohens_d": effect_size,
                "p_directional": p_value,
                "signal_class": str(row["signal_class"]),
                "proposal_outcome_class": outcome_class,
                "confidence": confidence,
                "assay_priority": assay_priority(outcome_class, confidence),
                "engineering_priority": engineering_priority(outcome_class, confidence),
                "top_divergent_interface_residues": top_divergent_residues,
                "top_constrained_interface_residues": top_constrained_residues,
                "biological_context": str(row.get("biological_context", "")),
                "rationale": rationale,
            }
        )

    out_df = pl.DataFrame(rows).sort(
        ["confidence", "proposal_outcome_class", "effect_size_cohens_d"],
        descending=[False, False, True],
    )

    confidence_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
        "very_low": 3,
    }

    out_df = out_df.with_columns(
        pl.col("confidence")
        .map_elements(lambda value: confidence_order.get(str(value), 99), return_dtype=pl.Int64)
        .alias("confidence_rank")
    ).sort(["confidence_rank", "proposal_outcome_class", "effect_size_cohens_d"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.drop("confidence_rank").write_csv(output_path)

    print(f"Wrote interaction outcome summary -> {output_path}")
    print()
    print("Outcome class counts:")
    print(
        out_df.group_by(["proposal_outcome_class", "confidence"]).len().sort("len", descending=True)
    )

    print()
    print("High/medium priority candidates:")
    print(
        out_df.filter(pl.col("confidence").is_in(["high", "medium"]))
        .drop("confidence_rank")
        .select(
            [
                "complex_id",
                "chain",
                "target_species",
                "signal_class",
                "proposal_outcome_class",
                "confidence",
                "effect_size_cohens_d",
                "p_directional",
                "top_divergent_interface_residues",
                "top_constrained_interface_residues",
            ]
        )
    )


if __name__ == "__main__":
    main()
