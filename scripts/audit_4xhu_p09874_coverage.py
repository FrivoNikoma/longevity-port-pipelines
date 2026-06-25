from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from longevity_port_pipelines.config import SPECIES_REGISTRY
from longevity_port_pipelines.models import LifespanCategory

TARGET_COMPLEX_ID = "4xhu__A1_P09874--4xhu__B1_Q9UNS1"
TARGET_PDB_ID = "4xhu"
TARGET_CHAIN = "receptor"
TARGET_SOURCE_UNIPROT = "P09874"

DATA_OUTPUT = Path("data/output")
DATA_INTERIM = Path("data/interim")

ORTHOLOG_RAW_OUT = DATA_INTERIM / "4xhu_p09874_ortholog_coverage_raw_hits.csv"
LOCAL_FILE_RAW_OUT = DATA_INTERIM / "4xhu_p09874_local_file_rows_raw_hits.csv"
SUMMARY_OUT = DATA_INTERIM / "4xhu_p09874_species_coverage_audit.csv"


def target_species_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for species in SPECIES_REGISTRY.values():
        if species.category == LifespanCategory.REFERENCE:
            continue

        rows.append(
            {
                "target_species": species.name,
                "target_species_taxid": species.taxid,
                "group": species.category.value,
            }
        )

    group_order = {
        LifespanCategory.LONG_LIVED.value: 0,
        LifespanCategory.SHORT_LIVED.value: 1,
    }

    return sorted(
        rows,
        key=lambda row: (
            group_order.get(str(row["group"]), 99),
            str(row["target_species"]),
        ),
    )


def read_table(path: Path) -> pl.DataFrame | None:
    try:
        if path.suffix.lower() == ".parquet":
            return pl.read_parquet(path)
        if path.suffix.lower() == ".csv":
            return pl.read_csv(path, infer_schema_length=10000)
    except Exception as exc:
        print(f"SKIP {path}: {exc}")

    return None


def join_unique(values: list[Any]) -> str:
    clean = sorted({str(value) for value in values if value is not None and str(value)})
    return ", ".join(clean)


def sequence_length(value: Any) -> int | None:
    if value is None:
        return None

    text = str(value)
    if not text or text.lower() == "null":
        return None

    return len(text)


def audit_ortholog_coverage(species_rows: list[dict[str, Any]]) -> pl.DataFrame:
    taxid_to_species = {
        int(row["target_species_taxid"]): str(row["target_species"]) for row in species_rows
    }

    raw_rows: list[dict[str, Any]] = []

    for path in sorted(DATA_OUTPUT.glob("*ortholog_coverage*.csv")):
        df = read_table(path)
        if df is None:
            continue

        required = {"source_uniprot", "target_species_taxid", "target_sequence"}
        if not required.issubset(set(df.columns)):
            continue

        hits = df.filter(pl.col("source_uniprot") == TARGET_SOURCE_UNIPROT)

        for row in hits.iter_rows(named=True):
            taxid = row.get("target_species_taxid")
            if taxid is None:
                continue

            species_name = taxid_to_species.get(int(taxid))
            if species_name is None:
                continue

            raw_rows.append(
                {
                    "target_species": species_name,
                    "target_species_taxid": int(taxid),
                    "target_uniprot": row.get("target_uniprot"),
                    "target_sequence_length": sequence_length(row.get("target_sequence")),
                    "is_reviewed": row.get("is_reviewed"),
                    "source_db": row.get("source_db"),
                    "source_file": str(path),
                }
            )

    if raw_rows:
        return pl.DataFrame(raw_rows).sort(["target_species", "source_file"])

    return pl.DataFrame(
        schema={
            "target_species": pl.Utf8,
            "target_species_taxid": pl.Int64,
            "target_uniprot": pl.Utf8,
            "target_sequence_length": pl.Int64,
            "is_reviewed": pl.Boolean,
            "source_db": pl.Utf8,
            "source_file": pl.Utf8,
        }
    )


def row_matches_4xhu(df: pl.DataFrame) -> pl.Expr | None:
    masks: list[pl.Expr] = []

    if "complex_id" in df.columns:
        masks.append(pl.col("complex_id").cast(pl.Utf8).str.contains(TARGET_PDB_ID, literal=True))

    if "id" in df.columns:
        masks.append(pl.col("id").cast(pl.Utf8).str.contains(TARGET_PDB_ID, literal=True))

    if "pdb_id" in df.columns:
        masks.append(pl.col("pdb_id").cast(pl.Utf8) == TARGET_PDB_ID)

    if not masks:
        return None

    mask = masks[0]
    for extra in masks[1:]:
        mask = mask | extra

    if "chain" in df.columns:
        mask = mask & (pl.col("chain").cast(pl.Utf8) == TARGET_CHAIN)

    if "source_uniprot" in df.columns:
        mask = mask & (pl.col("source_uniprot").cast(pl.Utf8) == TARGET_SOURCE_UNIPROT)

    return mask


def audit_local_file_rows(species_rows: list[dict[str, Any]]) -> pl.DataFrame:
    target_species = {str(row["target_species"]) for row in species_rows}
    raw_rows: list[dict[str, Any]] = []

    files = sorted(
        path
        for path in DATA_OUTPUT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".csv", ".parquet"}
    )

    for path in files:
        if "ortholog_coverage" in path.name:
            continue

        df = read_table(path)
        if df is None:
            continue

        if "target_species" not in df.columns:
            continue

        mask = row_matches_4xhu(df)
        if mask is None:
            continue

        hits = df.filter(mask)
        if hits.is_empty():
            continue

        for species in sorted(set(hits["target_species"].drop_nulls().to_list())):
            species_text = str(species)
            if species_text not in target_species:
                continue

            species_hits = hits.filter(pl.col("target_species").cast(pl.Utf8) == species_text)

            raw_rows.append(
                {
                    "target_species": species_text,
                    "source_file": str(path),
                    "n_rows": species_hits.height,
                }
            )

    if raw_rows:
        return pl.DataFrame(raw_rows).sort(["target_species", "source_file"])

    return pl.DataFrame(
        schema={
            "target_species": pl.Utf8,
            "source_file": pl.Utf8,
            "n_rows": pl.Int64,
        }
    )


def build_summary(
    species_rows: list[dict[str, Any]],
    ortholog_raw: pl.DataFrame,
    local_file_raw: pl.DataFrame,
) -> pl.DataFrame:
    rows: list[dict[str, Any]] = []

    for species_row in species_rows:
        species = str(species_row["target_species"])

        ortholog_hits = ortholog_raw.filter(pl.col("target_species") == species)
        local_file_hits = local_file_raw.filter(pl.col("target_species") == species)

        rows.append(
            {
                **species_row,
                "has_P09874_ortholog": not ortholog_hits.is_empty(),
                "n_ortholog_candidate_rows": ortholog_hits.height,
                "candidate_target_uniprots": join_unique(
                    ortholog_hits["target_uniprot"].drop_nulls().to_list()
                )
                if not ortholog_hits.is_empty()
                else "",
                "candidate_sequence_lengths": join_unique(
                    ortholog_hits["target_sequence_length"].drop_nulls().to_list()
                )
                if not ortholog_hits.is_empty()
                else "",
                "ortholog_source_dbs": join_unique(
                    ortholog_hits["source_db"].drop_nulls().to_list()
                )
                if not ortholog_hits.is_empty()
                else "",
                "ortholog_source_files": join_unique(ortholog_hits["source_file"].to_list())
                if not ortholog_hits.is_empty()
                else "",
                "has_local_4xhu_file_rows": not local_file_hits.is_empty(),
                "n_local_4xhu_file_rows": int(local_file_hits["n_rows"].sum())
                if not local_file_hits.is_empty()
                else 0,
                "local_files": join_unique(local_file_hits["source_file"].to_list())
                if not local_file_hits.is_empty()
                else "",
            }
        )

    return pl.DataFrame(rows)


def print_summary(summary: pl.DataFrame) -> None:
    print()
    print("4xhu / P09874 species coverage audit")
    print("=" * 80)
    print(f"complex_id: {TARGET_COMPLEX_ID}")
    print(f"chain:      {TARGET_CHAIN}")
    print(f"protein:    {TARGET_SOURCE_UNIPROT}")
    print()

    for row in summary.iter_rows(named=True):
        species = str(row["target_species"])
        group = str(row["group"])
        has_ortholog = "yes" if row["has_P09874_ortholog"] else "no"
        has_results = "yes" if row["has_local_4xhu_file_rows"] else "no"

        print(
            f"{species:18s} {group:12s} "
            f"ortholog={has_ortholog:3s} "
            f"ortholog_rows={row['n_ortholog_candidate_rows']:<2} "
            f"local_files={has_results:3s} "
            f"file_rows={row['n_local_4xhu_file_rows']}"
        )

    missing_orthologs = summary.filter(~pl.col("has_P09874_ortholog"))["target_species"].to_list()
    missing_results = summary.filter(~pl.col("has_local_4xhu_file_rows"))[
        "target_species"
    ].to_list()

    print()
    print("Missing P09874 ortholog coverage:", missing_orthologs)
    print("Missing local 4xhu file rows:", missing_results)

    if missing_orthologs:
        print()
        print("Interpretation guard:")
        print(
            "- Do not describe local readiness/file rows as usable coverage for a full 5-vs-3 species panel."
        )
        print("- Refresh/consolidate P09874 ortholog coverage before live Boltz panel runs.")
    else:
        print()
        print("Ortholog coverage is present for all configured target species.")


def main() -> None:
    species_rows = target_species_rows()

    ortholog_raw = audit_ortholog_coverage(species_rows)
    local_file_raw = audit_local_file_rows(species_rows)
    summary = build_summary(species_rows, ortholog_raw, local_file_raw)

    DATA_INTERIM.mkdir(parents=True, exist_ok=True)
    ortholog_raw.write_csv(ORTHOLOG_RAW_OUT)
    local_file_raw.write_csv(LOCAL_FILE_RAW_OUT)
    summary.write_csv(SUMMARY_OUT)

    print_summary(summary)

    print()
    print("Wrote:")
    print(f"- {ORTHOLOG_RAW_OUT}")
    print(f"- {LOCAL_FILE_RAW_OUT}")
    print(f"- {SUMMARY_OUT}")
    print()
    print("No Boltz API calls were made.")


if __name__ == "__main__":
    main()
