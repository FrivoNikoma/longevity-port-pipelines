from __future__ import annotations

import polars as pl

REQUIRED_NEGATIVE_CONTROL_AUDIT_COLUMNS = {
    "complex_id",
    "chain",
    "target_species",
    "enrichment_ratio",
    "shuffled_control_ratio",
    "negatome_control_ratio",
    "mann_whitney_p",
    "p_interface_greater",
    "p_interface_less",
    "p_two_sided",
    "effect_size_cohens_d",
}

DEFAULT_CONTROL_RATIO_MARGIN = 1.1
DEFAULT_CONTROL_P_ALPHA = 0.05


def control_signal_direction(enrichment_ratio: float) -> str:
    return "divergence" if enrichment_ratio >= 1.0 else "constraint"


def passes_controls(
    *,
    enrichment_ratio: float,
    shuffled_control_ratio: float | None,
    negatome_control_ratio: float | None,
    p_interface_greater: float,
    p_interface_less: float,
    control_status: str,
    ratio_margin: float = DEFAULT_CONTROL_RATIO_MARGIN,
    p_alpha: float = DEFAULT_CONTROL_P_ALPHA,
) -> bool:
    if control_status != "has_shuffled_and_negatome":
        return False

    if shuffled_control_ratio is None or negatome_control_ratio is None:
        return False

    if shuffled_control_ratio <= 0.0 or negatome_control_ratio <= 0.0:
        return False

    direction = control_signal_direction(enrichment_ratio)
    if direction == "divergence":
        return (
            enrichment_ratio > shuffled_control_ratio * ratio_margin
            and enrichment_ratio > negatome_control_ratio * ratio_margin
            and p_interface_greater < p_alpha
        )

    return (
        enrichment_ratio < shuffled_control_ratio / ratio_margin
        and enrichment_ratio < negatome_control_ratio / ratio_margin
        and p_interface_less < p_alpha
    )


def passes_controls_note(
    *,
    passes: bool,
    control_status: str,
    enrichment_ratio: float,
) -> str:
    if control_status != "has_shuffled_and_negatome":
        return "Controls incomplete; strict pass/fail gate not applicable."

    direction = control_signal_direction(enrichment_ratio)
    if passes:
        return (
            f"Controlled {direction} signal passes ratio and directional p-value gates "
            f"(margin={DEFAULT_CONTROL_RATIO_MARGIN}, alpha={DEFAULT_CONTROL_P_ALPHA})."
        )

    return (
        f"Controlled {direction} signal does not pass ratio and/or directional p-value gates "
        f"(margin={DEFAULT_CONTROL_RATIO_MARGIN}, alpha={DEFAULT_CONTROL_P_ALPHA})."
    )


def control_evidence_tier(
    *,
    control_status: str,
    passes: bool,
) -> str:
    if control_status == "has_shuffled_and_negatome":
        return "controlled_pass" if passes else "controlled_fail"
    if control_status == "missing_negatome":
        return "preliminary_shuffled_only"
    if control_status == "missing_shuffled":
        return "incomplete_control_evidence"
    if control_status == "missing_all_controls":
        return "missing_all_controls"
    return "not_audited"


def passes_controls_expr(
    ratio_margin: float = DEFAULT_CONTROL_RATIO_MARGIN,
    p_alpha: float = DEFAULT_CONTROL_P_ALPHA,
) -> pl.Expr:
    has_both_controls = pl.col("control_status") == pl.lit("has_shuffled_and_negatome")
    divergence = pl.col("enrichment_ratio") >= 1.0

    divergence_pass = (
        (pl.col("enrichment_ratio") > pl.col("shuffled_control_ratio") * ratio_margin)
        & (pl.col("enrichment_ratio") > pl.col("negatome_control_ratio") * ratio_margin)
        & (pl.col("p_interface_greater") < p_alpha)
    )
    constraint_pass = (
        (pl.col("enrichment_ratio") < pl.col("shuffled_control_ratio") / ratio_margin)
        & (pl.col("enrichment_ratio") < pl.col("negatome_control_ratio") / ratio_margin)
        & (pl.col("p_interface_less") < p_alpha)
    )

    return (
        pl.when(has_both_controls & divergence)
        .then(divergence_pass)
        .when(has_both_controls & ~divergence)
        .then(constraint_pass)
        .otherwise(pl.lit(False))
    )


def control_evidence_tier_expr() -> pl.Expr:
    return (
        pl.when(pl.col("control_status") == "has_shuffled_and_negatome")
        .then(
            pl.when(pl.col("passes_controls"))
            .then(pl.lit("controlled_pass"))
            .otherwise(pl.lit("controlled_fail"))
        )
        .when(pl.col("control_status") == "missing_negatome")
        .then(pl.lit("preliminary_shuffled_only"))
        .when(pl.col("control_status") == "missing_shuffled")
        .then(pl.lit("incomplete_control_evidence"))
        .when(pl.col("control_status") == "missing_all_controls")
        .then(pl.lit("missing_all_controls"))
        .otherwise(pl.lit("not_audited"))
    )


def passes_controls_note_expr() -> pl.Expr:
    return (
        pl.when(pl.col("control_status") != "has_shuffled_and_negatome")
        .then(pl.lit("Controls incomplete; strict pass/fail gate not applicable."))
        .when(pl.col("passes_controls"))
        .then(
            pl.concat_str(
                [
                    pl.lit("Controlled "),
                    pl.when(pl.col("enrichment_ratio") >= 1.0)
                    .then(pl.lit("divergence"))
                    .otherwise(pl.lit("constraint")),
                    pl.lit(
                        f" signal passes ratio and directional p-value gates "
                        f"(margin={DEFAULT_CONTROL_RATIO_MARGIN}, alpha={DEFAULT_CONTROL_P_ALPHA})."
                    ),
                ]
            )
        )
        .otherwise(
            pl.concat_str(
                [
                    pl.lit("Controlled "),
                    pl.when(pl.col("enrichment_ratio") >= 1.0)
                    .then(pl.lit("divergence"))
                    .otherwise(pl.lit("constraint")),
                    pl.lit(
                        f" signal does not pass ratio and/or directional p-value gates "
                        f"(margin={DEFAULT_CONTROL_RATIO_MARGIN}, alpha={DEFAULT_CONTROL_P_ALPHA})."
                    ),
                ]
            )
        )
    )


def control_status_expr() -> pl.Expr:
    has_shuffled = (
        pl.col("shuffled_control_ratio").is_not_null()
        & pl.col("shuffled_control_ratio").is_finite()
        & (pl.col("shuffled_control_ratio") > 0)
    )

    has_negatome = (
        pl.col("negatome_control_ratio").is_not_null()
        & pl.col("negatome_control_ratio").is_finite()
        & (pl.col("negatome_control_ratio") > 0)
    )

    return (
        pl.when(has_shuffled & has_negatome)
        .then(pl.lit("has_shuffled_and_negatome"))
        .when(has_shuffled & ~has_negatome)
        .then(pl.lit("missing_negatome"))
        .when(~has_shuffled & has_negatome)
        .then(pl.lit("missing_shuffled"))
        .otherwise(pl.lit("missing_all_controls"))
    )


def control_note_expr() -> pl.Expr:
    return (
        pl.when(pl.col("control_status") == "has_shuffled_and_negatome")
        .then(
            pl.lit(
                "Both shuffled-mask and NEGATOME-style controls are populated. "
                "Interpretation can consider both control families."
            )
        )
        .when(pl.col("control_status") == "missing_negatome")
        .then(
            pl.lit(
                "Shuffled-mask control is populated, but NEGATOME-style control is missing. "
                "Treat as shuffled-control-only evidence."
            )
        )
        .when(pl.col("control_status") == "missing_shuffled")
        .then(
            pl.lit(
                "NEGATOME-style control is populated, but shuffled-mask control is missing. "
                "This is unusual and should be inspected."
            )
        )
        .otherwise(
            pl.lit(
                "Both shuffled-mask and NEGATOME-style controls are missing or invalid. "
                "Do not interpret as controlled enrichment."
            )
        )
    )


def validate_negative_control_audit_input(df: pl.DataFrame) -> None:
    missing = REQUIRED_NEGATIVE_CONTROL_AUDIT_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")


def build_negative_control_audit(df: pl.DataFrame) -> pl.DataFrame:
    validate_negative_control_audit_input(df)

    return (
        df.with_columns(control_status_expr().alias("control_status"))
        .with_columns(control_note_expr().alias("control_note"))
        .with_columns(
            [
                (pl.col("enrichment_ratio") / pl.col("shuffled_control_ratio")).alias(
                    "ratio_vs_shuffled_control"
                ),
                pl.when(pl.col("negatome_control_ratio").is_not_null())
                .then(pl.col("enrichment_ratio") / pl.col("negatome_control_ratio"))
                .otherwise(None)
                .alias("ratio_vs_negatome_control"),
            ]
        )
        .with_columns(passes_controls_expr().alias("passes_controls"))
        .with_columns(control_evidence_tier_expr().alias("control_evidence_tier"))
        .with_columns(passes_controls_note_expr().alias("passes_controls_note"))
        .select(
            [
                "complex_id",
                "chain",
                "target_species",
                "enrichment_ratio",
                "shuffled_control_ratio",
                "negatome_control_ratio",
                "ratio_vs_shuffled_control",
                "ratio_vs_negatome_control",
                "mann_whitney_p",
                "p_interface_greater",
                "p_interface_less",
                "p_two_sided",
                "effect_size_cohens_d",
                "control_status",
                "control_note",
                "passes_controls",
                "control_evidence_tier",
                "passes_controls_note",
            ]
        )
        .sort(["control_status", "complex_id", "chain", "target_species"])
    )
