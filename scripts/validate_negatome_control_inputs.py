from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

REQUIRED_COLUMNS = {
    "complex_id",
    "chain",
    "target_species",
    "source_uniprot",
    "negative_partner_uniprot",
    "negative_partner_source",
    "negative_partner_sequence",
    "control_type",
}

KEY_COLUMNS = [
    "complex_id",
    "chain",
    "target_species",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate NEGATOME-style negative-control input pairs for the mini-pilot."
    )
    parser.add_argument(
        "--negative-control-pairs",
        default="data/interim/negatome_control_pairs.csv",
        help="Input CSV containing NEGATOME-style or curated negative-control partner pairs.",
    )
    parser.add_argument(
        "--expected-results",
        default="data/output/sirt6_mini_pilot_enrichment_mapped.parquet",
        help="Expected mini-pilot enrichment results used to audit coverage.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_negatome_control_input_validation.csv",
        help="Output validation CSV.",
    )
    return parser.parse_args()


def read_expected_results(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing expected results file: {path}")

    df = pl.read_parquet(path) if path.suffix == ".parquet" else pl.read_csv(path)

    required = set(KEY_COLUMNS)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Expected results file is missing required columns: {sorted(missing)}")

    return df.select(KEY_COLUMNS).unique().sort(KEY_COLUMNS)


def empty_validation(expected: pl.DataFrame) -> pl.DataFrame:
    return expected.with_columns(
        [
            pl.lit(0).alias("n_negative_control_pairs"),
            pl.lit(False).alias("has_negative_control_input"),
            pl.lit("missing_input_file").alias("input_status"),
            pl.lit(
                "No negative-control pair file was found. NEGATOME-style controls cannot be populated yet."
            ).alias("validation_note"),
        ]
    )


def validate_schema(pairs: pl.DataFrame, path: Path) -> None:
    missing = REQUIRED_COLUMNS - set(pairs.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")


def validation_note_expr() -> pl.Expr:
    return (
        pl.when(pl.col("n_negative_control_pairs") > 0)
        .then(
            pl.lit(
                "Negative-control input exists for this complex/chain/species row. "
                "This enables a future NEGATOME-style control-ratio calculation."
            )
        )
        .otherwise(
            pl.lit(
                "No negative-control input exists for this complex/chain/species row. "
                "The enrichment result should remain marked as missing_negatome."
            )
        )
    )


def input_status_expr() -> pl.Expr:
    return (
        pl.when(pl.col("n_negative_control_pairs") > 0)
        .then(pl.lit("has_negative_control_input"))
        .otherwise(pl.lit("missing_negative_control_input"))
    )


def main() -> None:
    args = parse_args()

    negative_control_path = Path(args.negative_control_pairs)
    expected_path = Path(args.expected_results)
    output_path = Path(args.output)

    expected = read_expected_results(expected_path)

    if not negative_control_path.exists():
        validation = empty_validation(expected)
    else:
        pairs = pl.read_csv(negative_control_path)
        validate_schema(pairs, negative_control_path)

        duplicate_keys = [
            "complex_id",
            "chain",
            "target_species",
            "negative_partner_uniprot",
            "control_type",
        ]

        duplicate_rows = (
            pairs.group_by(duplicate_keys)
            .len()
            .filter(pl.col("len") > 1)
            .select(duplicate_keys + ["len"])
        )

        if duplicate_rows.height > 0:
            print("Duplicate negative-control rows detected:")
            print(duplicate_rows)

        nonempty_pairs = pairs.filter(
            pl.all_horizontal(
                [
                    pl.col("complex_id").is_not_null(),
                    pl.col("chain").is_not_null(),
                    pl.col("target_species").is_not_null(),
                    pl.col("source_uniprot").is_not_null(),
                    pl.col("negative_partner_uniprot").is_not_null(),
                    pl.col("negative_partner_sequence").is_not_null(),
                    pl.col("negative_partner_sequence").str.len_chars() > 0,
                ]
            )
        )

        coverage = (
            nonempty_pairs.group_by(KEY_COLUMNS)
            .agg(
                [
                    pl.len().alias("n_negative_control_pairs"),
                    pl.col("negative_partner_uniprot")
                    .unique()
                    .sort()
                    .str.join(";")
                    .alias("negative_partner_uniprots"),
                    pl.col("control_type").unique().sort().str.join(";").alias("control_types"),
                    pl.col("negative_partner_source")
                    .unique()
                    .sort()
                    .str.join(";")
                    .alias("negative_partner_sources"),
                ]
            )
            .sort(KEY_COLUMNS)
        )

        validation = (
            expected.join(coverage, on=KEY_COLUMNS, how="left")
            .with_columns(
                [
                    pl.col("n_negative_control_pairs").fill_null(0),
                    pl.col("negative_partner_uniprots").fill_null(""),
                    pl.col("control_types").fill_null(""),
                    pl.col("negative_partner_sources").fill_null(""),
                ]
            )
            .with_columns(
                [
                    (pl.col("n_negative_control_pairs") > 0).alias("has_negative_control_input"),
                    input_status_expr().alias("input_status"),
                    validation_note_expr().alias("validation_note"),
                ]
            )
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    validation.write_csv(output_path)

    print(f"Wrote NEGATOME-control input validation -> {output_path}")
    print()
    print("Input status counts:")
    print(validation.group_by("input_status").len().sort("len", descending=True))

    print()
    print("Validation preview:")
    print(validation)


if __name__ == "__main__":
    main()
