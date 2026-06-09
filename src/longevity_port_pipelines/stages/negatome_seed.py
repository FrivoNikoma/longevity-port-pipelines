from __future__ import annotations

from pathlib import Path

import polars as pl

REQUIRED_RESIDUE_DELTA_COLUMNS = {
    "complex_id",
    "chain",
    "target_species",
    "source_uniprot",
    "target_uniprot",
}

NEGATOME_CANDIDATE_COLUMNS = [
    "complex_id",
    "chain",
    "target_species",
    "source_uniprot",
    "target_uniprot",
    "negative_partner_uniprot",
    "negative_partner_source",
    "negative_partner_sequence",
    "control_type",
    "ready_for_input_contract",
    "curation_note",
]


def read_table(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input table: {path}")

    if path.suffix == ".parquet":
        return pl.read_parquet(path)

    return pl.read_csv(path)


def validate_residue_delta_input(df: pl.DataFrame) -> None:
    missing = REQUIRED_RESIDUE_DELTA_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Residue delta table is missing required columns: {sorted(missing)}")


def build_negatome_control_pair_candidates(residue_deltas: pl.DataFrame) -> pl.DataFrame:
    validate_residue_delta_input(residue_deltas)

    return (
        residue_deltas.select(
            [
                "complex_id",
                "chain",
                "target_species",
                "source_uniprot",
                "target_uniprot",
            ]
        )
        .unique()
        .sort(["complex_id", "chain", "target_species", "source_uniprot", "target_uniprot"])
        .with_columns(
            [
                pl.lit("").alias("negative_partner_uniprot"),
                pl.lit("curation_required").alias("negative_partner_source"),
                pl.lit("").alias("negative_partner_sequence"),
                pl.lit("negatome_style_curation_required").alias("control_type"),
                pl.lit(False).alias("ready_for_input_contract"),
                pl.lit(
                    "Candidate row only. Populate negative_partner_uniprot and "
                    "negative_partner_sequence before using as data/interim/negatome_control_pairs.csv."
                ).alias("curation_note"),
            ]
        )
        .select(NEGATOME_CANDIDATE_COLUMNS)
    )
