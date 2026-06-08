from __future__ import annotations

from pathlib import Path

import polars as pl


def classify_signal(
    enrichment_ratio: float,
    effect_size: float,
    p_interface_greater: float,
    p_interface_less: float,
    min_abs_effect: float = 0.2,
    alpha: float = 0.05,
) -> str:
    if abs(effect_size) < min_abs_effect:
        return "weak_or_mixed"

    if enrichment_ratio > 1.0 and effect_size > 0:
        if p_interface_greater < alpha:
            return "interface_divergent"
        return "interface_divergent_not_significant"

    if enrichment_ratio < 1.0 and effect_size < 0:
        if p_interface_less < alpha:
            return "interface_constrained"
        return "interface_constrained_not_significant"

    return "weak_or_mixed"


def biological_note(complex_id: str, chain: str) -> str:
    if "8bot" in complex_id:
        if chain == "receptor":
            return "Ku70/XRCC6 side of Ku70-Ku80 DNA double-strand break repair complex"
        if chain == "ligand":
            return "Ku80/XRCC5 side of Ku70-Ku80 DNA double-strand break repair complex"

    if "7s68" in complex_id:
        return "PARP1/PARP1 DNA damage response complex"

    if "8f86" in complex_id:
        if chain == "receptor":
            return "SIRT6 side of SIRT6-Histone H3 chromatin interaction"
        if chain == "ligand":
            return "Histone H3 side of SIRT6-Histone H3 chromatin interaction"

    return "unannotated mini-pilot complex"


def interpretation(signal_class: str) -> str:
    if signal_class == "interface_divergent":
        return (
            "Interface residues differ more than non-interface residues; candidate for "
            "interface remodeling or altered partner/substrate recognition."
        )

    if signal_class == "interface_constrained":
        return (
            "Interface residues differ less than non-interface residues; candidate for "
            "maintained interaction surface under stronger structural/functional constraint."
        )

    if signal_class == "interface_divergent_not_significant":
        return (
            "Direction suggests interface divergence, but statistical support is weak in this "
            "mini-pilot sample."
        )

    if signal_class == "interface_constrained_not_significant":
        return (
            "Direction suggests interface constraint, but statistical support is weak in this "
            "mini-pilot sample."
        )

    return "Weak, mixed, or currently uninterpretable interface-vs-background signal."


def main() -> None:
    in_path = Path("data/output/sirt6_mini_pilot_enrichment_mapped.parquet")
    out_csv = Path("data/output/sirt6_mini_pilot_embedding_signal_summary.csv")
    out_md = Path("data/output/sirt6_mini_pilot_embedding_signal_summary.md")

    df = pl.read_parquet(in_path)

    # The current mann_whitney_p column is interpreted as the one-sided test
    # for interface_delta > noninterface_delta. For the opposite direction,
    # we use the complementary one-sided p-value as a pragmatic summary-level fix.
    df = df.with_columns(
        [
            pl.col("mann_whitney_p").alias("p_interface_greater"),
            (1.0 - pl.col("mann_whitney_p")).clip(0.0, 1.0).alias("p_interface_less"),
        ]
    )

    summary = (
        df.with_columns(
            [
                pl.struct(
                    [
                        "enrichment_ratio",
                        "effect_size_cohens_d",
                        "p_interface_greater",
                        "p_interface_less",
                    ]
                )
                .map_elements(
                    lambda row: classify_signal(
                        enrichment_ratio=float(row["enrichment_ratio"]),
                        effect_size=float(row["effect_size_cohens_d"]),
                        p_interface_greater=float(row["p_interface_greater"]),
                        p_interface_less=float(row["p_interface_less"]),
                    ),
                    return_dtype=pl.Utf8,
                )
                .alias("signal_class"),
                pl.struct(["complex_id", "chain"])
                .map_elements(
                    lambda row: biological_note(
                        complex_id=str(row["complex_id"]),
                        chain=str(row["chain"]),
                    ),
                    return_dtype=pl.Utf8,
                )
                .alias("biological_context"),
            ]
        )
        .with_columns(
            [
                pl.col("signal_class")
                .map_elements(interpretation, return_dtype=pl.Utf8)
                .alias("interpretation"),
                pl.col("effect_size_cohens_d").abs().alias("abs_effect_size"),
                pl.when(pl.col("effect_size_cohens_d") >= 0)
                .then(pl.col("p_interface_greater"))
                .otherwise(pl.col("p_interface_less"))
                .alias("p_directional"),
            ]
        )
        .sort(["abs_effect_size", "p_directional"], descending=[True, False])
    )

    summary.write_csv(out_csv)

    columns = [
        "complex_id",
        "chain",
        "target_species",
        "interface_mean_delta",
        "noninterface_mean_delta",
        "enrichment_ratio",
        "p_interface_greater",
        "p_interface_less",
        "mann_whitney_p",
        "effect_size_cohens_d",
        "signal_class",
        "biological_context",
        "interpretation",
    ]

    top = summary.select(columns)

    markdown = [
        "# SIRT6 mini-pilot embedding signal summary",
        "",
        "This table summarizes whether mapped interface residues show stronger or weaker embedding-space divergence than non-interface residues.",
        "",
        "| complex_id | chain | target_species | enrichment_ratio | p_greater | p_less | effect_size | signal_class | biological_context | interpretation |",
        "|---|---|---|---:|---:|---:|---:|---|---|---|",
    ]

    for row in top.iter_rows(named=True):
        markdown.append(
            "| "
            f"{row['complex_id']} | "
            f"{row['chain']} | "
            f"{row['target_species']} | "
            f"{float(row['enrichment_ratio']):.3f} | "
            f"{float(row['p_interface_greater']):.3g} | "
            f"{float(row['p_interface_less']):.3g} | "
            f"{float(row['effect_size_cohens_d']):.3f} | "
            f"{row['signal_class']} | "
            f"{row['biological_context']} | "
            f"{row['interpretation']} |"
        )

    out_md.write_text("\n".join(markdown), encoding="utf-8")

    print(f"Wrote CSV summary -> {out_csv}")
    print(f"Wrote Markdown summary -> {out_md}")
    print()
    print(
        top.select(
            [
                "complex_id",
                "chain",
                "target_species",
                "enrichment_ratio",
                "p_interface_greater",
                "p_interface_less",
                "effect_size_cohens_d",
                "signal_class",
            ]
        )
    )

    print()
    print("Signal class counts:")
    print(summary.group_by("signal_class").len().sort("len", descending=True))


if __name__ == "__main__":
    main()
