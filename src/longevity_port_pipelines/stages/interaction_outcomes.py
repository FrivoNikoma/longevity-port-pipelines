from __future__ import annotations

from pathlib import Path

import polars as pl


def as_float(value: object, *, field_name: str) -> float:
    if value is None:
        raise ValueError(f"Missing numeric value for {field_name}")

    if isinstance(value, str | int | float):
        return float(value)

    raise TypeError(f"Expected numeric value for {field_name}, got {type(value).__name__}")


def directional_p(row: dict[str, object]) -> float:
    effect_size = as_float(row["effect_size_cohens_d"], field_name="effect_size_cohens_d")
    if effect_size >= 0:
        return as_float(
            row.get("p_interface_greater", row.get("mann_whitney_p", 1.0)),
            field_name="p_interface_greater",
        )
    return as_float(row.get("p_interface_less", 1.0), field_name="p_interface_less")


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
    effect_size = as_float(row["effect_size_cohens_d"], field_name="effect_size_cohens_d")
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
        f"{int(row['residue_number_1based'])}{row['residue_aa']}:{as_float(row['delta'], field_name='delta'):.3f}"
        for row in hits.iter_rows(named=True)
    )


def confidence_rank_expr() -> pl.Expr:
    confidence_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
        "very_low": 3,
    }

    return (
        pl.col("confidence")
        .map_elements(lambda value: confidence_order.get(str(value), 99), return_dtype=pl.Int64)
        .alias("confidence_rank")
    )


def required_signal_columns() -> set[str]:
    return {
        "complex_id",
        "chain",
        "target_species",
        "enrichment_ratio",
        "effect_size_cohens_d",
        "signal_class",
    }


def validate_signal_summary(signal_df: pl.DataFrame) -> None:
    missing = required_signal_columns() - set(signal_df.columns)
    if missing:
        raise ValueError(f"Signal summary is missing required columns: {sorted(missing)}")


def build_interaction_outcome_summary(
    signal_df: pl.DataFrame,
    top_divergent_df: pl.DataFrame,
    top_constrained_df: pl.DataFrame,
) -> pl.DataFrame:
    validate_signal_summary(signal_df)

    rows: list[dict[str, object]] = []

    for row in signal_df.iter_rows(named=True):
        complex_id = str(row["complex_id"])
        chain = str(row["chain"])
        target_species = str(row["target_species"])
        effect_size = as_float(row["effect_size_cohens_d"], field_name="effect_size_cohens_d")
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
                "enrichment_ratio": as_float(
                    row["enrichment_ratio"], field_name="enrichment_ratio"
                ),
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

    return (
        pl.DataFrame(rows)
        .with_columns(confidence_rank_expr())
        .sort(["confidence_rank", "proposal_outcome_class", "effect_size_cohens_d"])
        .drop("confidence_rank")
    )
