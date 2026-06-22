from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import polars as pl

from longevity_port_pipelines.config import LONG_LIVED_SPECIES, SHORT_LIVED_SPECIES

DEFAULT_INPUT = "data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet"
DEFAULT_OUTPUT_CSV = "data/output/sirt6_mini_pilot_v2_species_coverage_audit.csv"
DEFAULT_OUTPUT_MD = "data/output/sirt6_mini_pilot_v2_species_coverage_audit.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit expected long-lived and short-lived species coverage in "
            "mapped enrichment outputs."
        )
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help="Input mapped enrichment parquet path.",
    )
    parser.add_argument(
        "--output-csv",
        default=DEFAULT_OUTPUT_CSV,
        help="Output species coverage audit CSV path.",
    )
    parser.add_argument(
        "--output-md",
        default=DEFAULT_OUTPUT_MD,
        help="Output species coverage audit Markdown path.",
    )
    return parser.parse_args()


def require_columns(df: pl.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def expected_species() -> list[tuple[str, str]]:
    rows = []
    rows.extend(("long_lived", species.name) for species in LONG_LIVED_SPECIES)
    rows.extend(("short_lived", species.name) for species in SHORT_LIVED_SPECIES)
    return rows


def species_counts(df: pl.DataFrame) -> dict[str, int]:
    counts = df.group_by("target_species").len().rename({"len": "row_count"}).sort("target_species")
    return {
        str(row["target_species"]): int(row["row_count"]) for row in counts.iter_rows(named=True)
    }


def build_species_coverage_audit(df: pl.DataFrame) -> pl.DataFrame:
    require_columns(df, ["target_species"])

    counts = species_counts(df)
    records: list[dict[str, Any]] = []

    for species_group, species_name in expected_species():
        row_count = counts.get(species_name, 0)
        records.append(
            {
                "species_group": species_group,
                "species": species_name,
                "present": row_count > 0,
                "row_count": row_count,
            }
        )

    return pl.DataFrame(records)


def markdown_table(frame: pl.DataFrame) -> str:
    columns = frame.columns
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")

    for row in frame.iter_rows(named=True):
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")

    return "\n".join(lines)


def write_markdown_report(
    coverage: pl.DataFrame,
    *,
    output_path: Path,
    input_path: Path,
) -> None:
    summary = (
        coverage.group_by("species_group")
        .agg(
            [
                pl.len().alias("expected_species"),
                pl.col("present").sum().alias("present_species"),
                (~pl.col("present")).sum().alias("missing_species"),
                pl.col("row_count").sum().alias("total_rows"),
            ]
        )
        .sort("species_group")
    )

    missing = coverage.filter(~pl.col("present")).select(["species_group", "species", "row_count"])
    present = coverage.filter(pl.col("present")).select(["species_group", "species", "row_count"])

    lines = [
        "# Longevity species coverage audit",
        "",
        f"Input: `{input_path}`",
        "",
        "This report audits whether the expected long-lived and short-lived species "
        "are present in a mapped enrichment parquet file.",
        "",
        "## Summary",
        "",
        markdown_table(summary),
        "",
        "## Present expected species",
        "",
        markdown_table(present) if present.height else "_No expected species present._",
        "",
        "## Missing expected species",
        "",
        markdown_table(missing) if missing.height else "_No expected species missing._",
        "",
        "## Full coverage table",
        "",
        markdown_table(coverage),
    ]

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_csv = Path(args.output_csv)
    output_md = Path(args.output_md)

    if not input_path.exists():
        raise FileNotFoundError(f"Missing mapped enrichment parquet: {input_path}")

    df = pl.read_parquet(input_path)
    coverage = build_species_coverage_audit(df)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    coverage.write_csv(output_csv)
    write_markdown_report(coverage, output_path=output_md, input_path=input_path)

    print(f"Wrote species coverage audit CSV -> {output_csv}")
    print(f"Wrote species coverage audit Markdown -> {output_md}")

    print()
    print("Species coverage:")
    print(coverage)


if __name__ == "__main__":
    main()
