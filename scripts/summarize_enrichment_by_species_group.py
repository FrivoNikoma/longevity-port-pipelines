from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from longevity_port_pipelines.config_utils import build_species_to_group_map, infer_species_group


def find_col(df: pd.DataFrame, candidates: list[str]) -> str:
    for col in candidates:
        if col in df.columns:
            return col

    raise ValueError(
        f"None of the expected columns found: {candidates}. "
        f"Available columns: {list(df.columns)}"
    )


def optional_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize interface-enrichment results by species group."
    )
    parser.add_argument(
        "--input",
        default="data/output/enrichment_top_with_fdr.csv",
        help="Input enrichment CSV with FDR columns.",
    )
    parser.add_argument(
        "--species-groups",
        default="data/config/species_groups.yaml",
        help="Species grouping config.",
    )
    parser.add_argument(
        "--output",
        default="data/output/enrichment_group_summary.csv",
        help="Output group-level summary CSV.",
    )
    parser.add_argument(
        "--annotated-output",
        default="data/output/enrichment_top_with_fdr_and_groups.csv",
        help="Annotated row-level output with species_group column.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path)

    species_col = find_col(df, ["species", "target_species", "ortholog_species"])
    enrichment_col = find_col(df, ["enrichment", "interface_enrichment", "enrichment_ratio"])

    q_col = optional_col(
    df,
    ["mann_whitney_q_bh", "q_value", "fdr", "bh_fdr", "p_adj", "padj"],
    )
    ratio_col = optional_col(
        df,
        ["vs_shuffled_ratio", "shuffled_ratio", "enrichment_vs_shuffled"],
    )

    species_to_group = build_species_to_group_map(args.species_groups)
    df["species_group"] = df[species_col].astype(str).map(
        lambda x: infer_species_group(x, species_to_group)
    )

    df["is_long_lived_group"] = df["species_group"].isin(
        ["long_lived_small_body", "long_lived_large_body"]
    )
    df["is_short_lived_control"] = df["species_group"].eq("short_lived_control")

    summary_aggs = {
        enrichment_col: ["count", "mean", "median", "std", "max"],
    }

    if q_col is not None:
        summary_aggs[q_col] = ["mean", "median", "min"]

    if ratio_col is not None:
        summary_aggs[ratio_col] = ["mean", "median", "max"]

    summary = df.groupby(["species_group"]).agg(summary_aggs)
    summary.columns = ["_".join([x for x in col if x]) for col in summary.columns.to_flat_index()]
    summary = summary.reset_index()

    long_mean = df.loc[df["is_long_lived_group"], enrichment_col].mean()
    short_mean = df.loc[df["is_short_lived_control"], enrichment_col].mean()

    delta = (
        long_mean - short_mean
        if pd.notna(long_mean) and pd.notna(short_mean)
        else float("nan")
    )

    meta_row = pd.DataFrame(
        [
            {
                "species_group": "__long_vs_short_delta__",
                f"{enrichment_col}_count": df[enrichment_col].notna().sum(),
                f"{enrichment_col}_mean": delta,
                f"{enrichment_col}_median": float("nan"),
                f"{enrichment_col}_std": float("nan"),
                f"{enrichment_col}_max": float("nan"),
            }
        ]
    )

    for col in summary.columns:
        if col not in meta_row.columns:
            meta_row[col] = float("nan")

    summary = pd.concat([summary, meta_row[summary.columns]], ignore_index=True)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(args.annotated_output, index=False)
    summary.to_csv(args.output, index=False)

    print(f"Input: {args.input}")
    print(f"Species column: {species_col}")
    print(f"Enrichment column: {enrichment_col}")
    print(f"FDR/q column: {q_col}")
    print(f"Shuffled-ratio column: {ratio_col}")
    print()
    print(f"Saved annotated results: {args.annotated_output}")
    print(f"Saved group summary: {args.output}")
    print()
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()