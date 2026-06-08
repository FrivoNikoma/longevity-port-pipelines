from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize residue-level interface delta candidates."
    )
    parser.add_argument(
        "--input",
        default="data/output/sirt6_mini_pilot_residue_deltas_mapped.parquet",
        help="Input residue-level parquet path.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/output",
        help="Directory for summary CSV outputs.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=30,
        help="Number of global top residues to print/export.",
    )
    parser.add_argument(
        "--top-n-per-group",
        type=int,
        default=10,
        help="Number of top residues per complex/chain/species group used for recurrence.",
    )
    return parser.parse_args()


def add_interface_ranks(df: pl.DataFrame) -> pl.DataFrame:
    group_cols = ["complex_id", "chain", "target_species"]

    interface_df = df.filter(pl.col("is_interface")).with_columns(
        [
            pl.col("delta")
            .rank(method="ordinal", descending=True)
            .over(group_cols)
            .alias("divergent_rank_in_group"),
            pl.col("delta")
            .rank(method="ordinal", descending=False)
            .over(group_cols)
            .alias("constrained_rank_in_group"),
        ]
    )

    return interface_df


def summarize_recurrent_candidates(
    ranked_interface_df: pl.DataFrame,
    top_n_per_group: int,
) -> pl.DataFrame:
    divergent = (
        ranked_interface_df.filter(pl.col("divergent_rank_in_group") <= top_n_per_group)
        .with_columns(pl.lit("divergent").alias("candidate_type"))
        .select(
            [
                "candidate_type",
                "complex_id",
                "pdb_id",
                "chain",
                "source_uniprot",
                "residue_number_1based",
                "residue_aa",
                "target_species",
                "delta",
                "divergent_rank_in_group",
                "constrained_rank_in_group",
            ]
        )
    )

    constrained = (
        ranked_interface_df.filter(pl.col("constrained_rank_in_group") <= top_n_per_group)
        .with_columns(pl.lit("constrained").alias("candidate_type"))
        .select(
            [
                "candidate_type",
                "complex_id",
                "pdb_id",
                "chain",
                "source_uniprot",
                "residue_number_1based",
                "residue_aa",
                "target_species",
                "delta",
                "divergent_rank_in_group",
                "constrained_rank_in_group",
            ]
        )
    )

    candidates = pl.concat([divergent, constrained], how="vertical")

    return (
        candidates.group_by(
            [
                "candidate_type",
                "complex_id",
                "pdb_id",
                "chain",
                "source_uniprot",
                "residue_number_1based",
                "residue_aa",
            ]
        )
        .agg(
            [
                pl.len().alias("n_hits"),
                pl.col("target_species").n_unique().alias("n_species"),
                pl.col("target_species").unique().sort().str.join(";").alias("species"),
                pl.mean("delta").alias("mean_delta"),
                pl.median("delta").alias("median_delta"),
                pl.min("delta").alias("min_delta"),
                pl.max("delta").alias("max_delta"),
                pl.min("divergent_rank_in_group").alias("best_divergent_rank"),
                pl.min("constrained_rank_in_group").alias("best_constrained_rank"),
            ]
        )
        .sort(
            ["candidate_type", "n_species", "n_hits", "mean_delta"],
            descending=[False, True, True, True],
        )
    )


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Missing residue-level parquet: {input_path}")

    df = pl.read_parquet(input_path)
    ranked_interface_df = add_interface_ranks(df)

    top_divergent = (
        ranked_interface_df.sort("delta", descending=True)
        .select(
            [
                "complex_id",
                "pdb_id",
                "chain",
                "target_species",
                "source_uniprot",
                "target_uniprot",
                "residue_number_1based",
                "residue_aa",
                "delta",
                "divergent_rank_in_group",
            ]
        )
        .head(args.top_n)
    )

    top_constrained = (
        ranked_interface_df.sort("delta")
        .select(
            [
                "complex_id",
                "pdb_id",
                "chain",
                "target_species",
                "source_uniprot",
                "target_uniprot",
                "residue_number_1based",
                "residue_aa",
                "delta",
                "constrained_rank_in_group",
            ]
        )
        .head(args.top_n)
    )

    recurrent = summarize_recurrent_candidates(
        ranked_interface_df=ranked_interface_df,
        top_n_per_group=args.top_n_per_group,
    )

    top_divergent_path = output_dir / "sirt6_mini_pilot_top_divergent_interface_residues.csv"
    top_constrained_path = output_dir / "sirt6_mini_pilot_top_constrained_interface_residues.csv"
    recurrent_path = output_dir / "sirt6_mini_pilot_recurrent_interface_residues.csv"

    top_divergent.write_csv(top_divergent_path)
    top_constrained.write_csv(top_constrained_path)
    recurrent.write_csv(recurrent_path)

    print(f"Wrote top divergent interface residues -> {top_divergent_path}")
    print(f"Wrote top constrained interface residues -> {top_constrained_path}")
    print(f"Wrote recurrent interface residues -> {recurrent_path}")

    print()
    print("Input rows:")
    print(df.shape)

    print()
    print("Interface rows:")
    print(ranked_interface_df.shape)

    print()
    print("Top divergent interface residues:")
    print(top_divergent)

    print()
    print("Top constrained interface residues:")
    print(top_constrained)

    print()
    print("Recurrent interface residues:")
    print(recurrent.head(args.top_n))


if __name__ == "__main__":
    main()
