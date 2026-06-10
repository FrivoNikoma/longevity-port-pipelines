from __future__ import annotations

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


def read_table(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input table: {path}")

    return pl.read_parquet(path) if path.suffix == ".parquet" else pl.read_csv(path)


def read_expected_results(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing expected results file: {path}")

    df = read_table(path)

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


def validate_schema(pairs: pl.DataFrame, path: Path | None = None) -> None:
    missing = REQUIRED_COLUMNS - set(pairs.columns)
    if not missing:
        return

    if path is None:
        raise ValueError(f"Negative-control input is missing required columns: {sorted(missing)}")

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


def duplicate_key_columns() -> list[str]:
    return [
        "complex_id",
        "chain",
        "target_species",
        "negative_partner_uniprot",
        "control_type",
    ]


def find_duplicate_negative_control_rows(pairs: pl.DataFrame) -> pl.DataFrame:
    validate_schema(pairs)

    duplicate_keys = duplicate_key_columns()

    return (
        pairs.group_by(duplicate_keys)
        .len()
        .filter(pl.col("len") > 1)
        .select(duplicate_keys + ["len"])
    )


def filter_nonempty_negative_control_pairs(pairs: pl.DataFrame) -> pl.DataFrame:
    validate_schema(pairs)

    return pairs.filter(
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


def build_negative_control_coverage(pairs: pl.DataFrame) -> pl.DataFrame:
    nonempty_pairs = filter_nonempty_negative_control_pairs(pairs)

    if nonempty_pairs.is_empty():
        return pl.DataFrame(
            {
                "complex_id": [],
                "chain": [],
                "target_species": [],
                "n_negative_control_pairs": [],
                "negative_partner_uniprots": [],
                "control_types": [],
                "negative_partner_sources": [],
            }
        )

    return (
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


def build_negatome_input_validation(
    expected: pl.DataFrame,
    pairs: pl.DataFrame | None,
) -> pl.DataFrame:
    expected_keys = expected.select(KEY_COLUMNS).unique().sort(KEY_COLUMNS)

    if pairs is None:
        return empty_validation(expected_keys)

    validate_schema(pairs)

    coverage = build_negative_control_coverage(pairs)

    return (
        expected_keys.join(coverage, on=KEY_COLUMNS, how="left")
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
