from __future__ import annotations

from pathlib import Path

import polars as pl

REQUIRED_COLUMNS = {
    "complex_id",
    "chain",
    "target_species",
    "source_uniprot",
    "source_species_taxid",
    "target_species_taxid",
    "target_accession",
    "target_accession_db",
    "target_sequence",
    "target_sequence_length",
    "curation_status",
    "evidence_source",
    "curation_note",
}

KEY_COLUMNS = [
    "complex_id",
    "chain",
    "target_species",
    "source_uniprot",
]

ACTIVE_CURATION_STATUSES = [
    "primary_candidate",
    "supporting_candidate",
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
            pl.lit(0).alias("n_curated_ortholog_candidates"),
            pl.lit(False).alias("has_curated_ortholog_candidate"),
            pl.lit("").alias("target_accessions"),
            pl.lit("").alias("target_accession_dbs"),
            pl.lit("").alias("curation_statuses"),
            pl.lit("missing_input_file").alias("input_status"),
            pl.lit(
                "No curated ortholog candidate file was found. Standard ortholog coverage "
                "should remain unchanged."
            ).alias("validation_note"),
        ]
    )


def validate_schema(candidates: pl.DataFrame, path: Path | None = None) -> None:
    missing = REQUIRED_COLUMNS - set(candidates.columns)
    if not missing:
        return

    if path is None:
        raise ValueError(f"Curated ortholog input is missing required columns: {sorted(missing)}")

    raise ValueError(f"{path} is missing required columns: {sorted(missing)}")


def validation_note_expr() -> pl.Expr:
    return (
        pl.when(pl.col("n_curated_ortholog_candidates") > 0)
        .then(
            pl.lit(
                "Curated ortholog candidate input exists for this complex/chain/species/source "
                "row. This is candidate evidence only; a dedicated override step is still needed "
                "before standard ortholog_coverage outputs are populated from curated inputs."
            )
        )
        .otherwise(
            pl.lit(
                "No curated ortholog candidate input exists for this complex/chain/species/source "
                "row. Use the standard OMA/UniProt ortholog lookup unless a future curated "
                "override is added."
            )
        )
    )


def input_status_expr() -> pl.Expr:
    return (
        pl.when(pl.col("n_curated_ortholog_candidates") > 0)
        .then(pl.lit("has_curated_ortholog_candidate"))
        .otherwise(pl.lit("missing_curated_ortholog_candidate"))
    )


def duplicate_key_columns() -> list[str]:
    return [
        "complex_id",
        "chain",
        "target_species",
        "source_uniprot",
        "target_accession",
        "target_accession_db",
        "curation_status",
    ]


def find_duplicate_curated_ortholog_rows(candidates: pl.DataFrame) -> pl.DataFrame:
    validate_schema(candidates)

    duplicate_keys = duplicate_key_columns()

    return (
        candidates.group_by(duplicate_keys)
        .len()
        .filter(pl.col("len") > 1)
        .select(duplicate_keys + ["len"])
    )


def filter_active_curated_ortholog_candidates(candidates: pl.DataFrame) -> pl.DataFrame:
    validate_schema(candidates)

    return candidates.filter(
        pl.all_horizontal(
            [
                pl.col("complex_id").is_not_null(),
                pl.col("chain").is_not_null(),
                pl.col("target_species").is_not_null(),
                pl.col("source_uniprot").is_not_null(),
                pl.col("target_accession").is_not_null(),
                pl.col("target_accession").str.len_chars() > 0,
                pl.col("target_accession_db").is_not_null(),
                pl.col("target_accession_db").str.len_chars() > 0,
                pl.col("target_sequence").is_not_null(),
                pl.col("target_sequence").str.len_chars() > 0,
                pl.col("curation_status").is_in(ACTIVE_CURATION_STATUSES),
            ]
        )
    )


def build_curated_ortholog_candidate_coverage(candidates: pl.DataFrame) -> pl.DataFrame:
    active_candidates = filter_active_curated_ortholog_candidates(candidates)

    if active_candidates.is_empty():
        return pl.DataFrame(
            {
                "complex_id": [],
                "chain": [],
                "target_species": [],
                "source_uniprot": [],
                "n_curated_ortholog_candidates": [],
                "target_accessions": [],
                "target_accession_dbs": [],
                "curation_statuses": [],
            }
        )

    return (
        active_candidates.group_by(KEY_COLUMNS)
        .agg(
            [
                pl.len().alias("n_curated_ortholog_candidates"),
                pl.col("target_accession").unique().sort().str.join(";").alias("target_accessions"),
                pl.col("target_accession_db")
                .unique()
                .sort()
                .str.join(";")
                .alias("target_accession_dbs"),
                pl.col("curation_status").unique().sort().str.join(";").alias("curation_statuses"),
            ]
        )
        .sort(KEY_COLUMNS)
    )


def build_curated_ortholog_input_validation(
    expected: pl.DataFrame,
    candidates: pl.DataFrame | None,
) -> pl.DataFrame:
    expected_keys = expected.select(KEY_COLUMNS).unique().sort(KEY_COLUMNS)

    if candidates is None:
        return empty_validation(expected_keys)

    validate_schema(candidates)

    coverage = build_curated_ortholog_candidate_coverage(candidates)

    return (
        expected_keys.join(coverage, on=KEY_COLUMNS, how="left")
        .with_columns(
            [
                pl.col("n_curated_ortholog_candidates").fill_null(0),
                pl.col("target_accessions").fill_null(""),
                pl.col("target_accession_dbs").fill_null(""),
                pl.col("curation_statuses").fill_null(""),
            ]
        )
        .with_columns(
            [
                (pl.col("n_curated_ortholog_candidates") > 0).alias(
                    "has_curated_ortholog_candidate"
                ),
                input_status_expr().alias("input_status"),
                validation_note_expr().alias("validation_note"),
            ]
        )
    )
