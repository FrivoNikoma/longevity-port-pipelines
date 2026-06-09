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
            ]
        )
        .sort(["control_status", "complex_id", "chain", "target_species"])
    )
