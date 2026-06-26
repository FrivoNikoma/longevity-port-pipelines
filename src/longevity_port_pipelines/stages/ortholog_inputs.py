from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import polars as pl

from longevity_port_pipelines.models import OrthologMapping

ConflictPolicy = Literal["keep_standard", "prefer_curated", "error"]

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

PRIMARY_CURATION_STATUS = "primary_candidate"

PRIMARY_MAPPING_KEY_COLUMNS = [
    "source_uniprot",
    "source_species_taxid",
    "target_species_taxid",
]

ORTHOLOG_MAPPING_COLUMNS = [
    "source_uniprot",
    "source_species_taxid",
    "target_uniprot",
    "target_species_taxid",
    "target_sequence",
    "is_reviewed",
    "source_db",
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
                "row. Run the explicit curated-ortholog merge step before downstream "
                "ortholog_coverage, embedding, or analysis outputs use curated inputs."
            )
        )
        .otherwise(
            pl.lit(
                "No curated ortholog candidate input exists for this complex/chain/species/source "
                "row. Use the standard OMA/UniProt ortholog lookup unless a curated input row "
                "is added and the explicit curated-ortholog merge step is run."
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


def filter_primary_curated_ortholog_candidates(candidates: pl.DataFrame) -> pl.DataFrame:
    active_candidates = filter_active_curated_ortholog_candidates(candidates)

    return active_candidates.filter(pl.col("curation_status") == PRIMARY_CURATION_STATUS)


def find_duplicate_primary_candidate_rows(candidates: pl.DataFrame) -> pl.DataFrame:
    primary_candidates = filter_primary_curated_ortholog_candidates(candidates)

    if primary_candidates.is_empty():
        return pl.DataFrame(
            schema={
                "source_uniprot": pl.Utf8,
                "source_species_taxid": pl.Int64,
                "target_species_taxid": pl.Int64,
                "len": pl.UInt32,
            }
        )

    return (
        primary_candidates.group_by(PRIMARY_MAPPING_KEY_COLUMNS)
        .len()
        .filter(pl.col("len") > 1)
        .select(PRIMARY_MAPPING_KEY_COLUMNS + ["len"])
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


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False

    raise ValueError(f"Cannot interpret boolean value: {value!r}")


def ortholog_mappings_from_frame(frame: pl.DataFrame) -> list[OrthologMapping]:
    missing = set(ORTHOLOG_MAPPING_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Ortholog coverage frame is missing required columns: {sorted(missing)}")

    mappings: list[OrthologMapping] = []
    for row in frame.select(ORTHOLOG_MAPPING_COLUMNS).iter_rows(named=True):
        mappings.append(
            OrthologMapping(
                source_uniprot=str(row["source_uniprot"]).strip(),
                source_species_taxid=int(row["source_species_taxid"]),
                target_uniprot=str(row["target_uniprot"]).strip(),
                target_species_taxid=int(row["target_species_taxid"]),
                target_sequence=str(row["target_sequence"]).strip(),
                is_reviewed=_as_bool(row["is_reviewed"]),
                source_db=str(row["source_db"]).strip(),
            )
        )

    return mappings


def ortholog_mappings_to_frame(mappings: Sequence[OrthologMapping]) -> pl.DataFrame:
    if not mappings:
        return pl.DataFrame(
            schema={
                "source_uniprot": pl.Utf8,
                "source_species_taxid": pl.Int64,
                "target_uniprot": pl.Utf8,
                "target_species_taxid": pl.Int64,
                "target_sequence": pl.Utf8,
                "is_reviewed": pl.Boolean,
                "source_db": pl.Utf8,
            }
        )

    return pl.DataFrame([mapping.model_dump() for mapping in mappings]).select(
        ORTHOLOG_MAPPING_COLUMNS
    )


def curated_candidates_to_ortholog_mappings(candidates: pl.DataFrame) -> list[OrthologMapping]:
    validate_schema(candidates)

    duplicates = find_duplicate_primary_candidate_rows(candidates)
    if duplicates.height > 0:
        raise ValueError(
            "Multiple primary curated ortholog candidates found for the same "
            f"source/species mapping key:\n{duplicates}"
        )

    mappings: list[OrthologMapping] = []
    for row in filter_primary_curated_ortholog_candidates(candidates).iter_rows(named=True):
        target_accession_db = str(row["target_accession_db"]).strip()
        mappings.append(
            OrthologMapping(
                source_uniprot=str(row["source_uniprot"]).strip(),
                source_species_taxid=int(row["source_species_taxid"]),
                target_uniprot=str(row["target_accession"]).strip(),
                target_species_taxid=int(row["target_species_taxid"]),
                target_sequence=str(row["target_sequence"]).strip(),
                is_reviewed=False,
                source_db=f"curated:{target_accession_db}",
            )
        )

    return mappings


def ortholog_mapping_key(mapping: OrthologMapping) -> tuple[str, int, int]:
    return (
        mapping.source_uniprot,
        mapping.source_species_taxid,
        mapping.target_species_taxid,
    )


def merge_ortholog_mappings(
    standard_mappings: Sequence[OrthologMapping],
    curated_mappings: Sequence[OrthologMapping],
    *,
    conflict_policy: ConflictPolicy = "keep_standard",
) -> list[OrthologMapping]:
    if conflict_policy not in {"keep_standard", "prefer_curated", "error"}:
        raise ValueError(f"Unsupported conflict policy: {conflict_policy}")

    merged_by_key: dict[tuple[str, int, int], OrthologMapping] = {}
    ordered_keys: list[tuple[str, int, int]] = []

    for mapping in standard_mappings:
        key = ortholog_mapping_key(mapping)
        if key in merged_by_key:
            raise ValueError(f"Duplicate standard ortholog mapping key: {key}")
        merged_by_key[key] = mapping
        ordered_keys.append(key)

    for mapping in curated_mappings:
        key = ortholog_mapping_key(mapping)
        if key in merged_by_key:
            if conflict_policy == "keep_standard":
                continue
            if conflict_policy == "prefer_curated":
                merged_by_key[key] = mapping
                continue
            if conflict_policy == "error":
                raise ValueError(f"Curated ortholog mapping conflicts with standard mapping: {key}")

        merged_by_key[key] = mapping
        ordered_keys.append(key)

    return [merged_by_key[key] for key in ordered_keys]
