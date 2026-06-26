from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.ortholog_inputs import (
    build_curated_ortholog_input_validation,
    find_duplicate_curated_ortholog_rows,
    read_expected_results,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate curated ortholog candidate inputs for candidate/species rows."
    )
    parser.add_argument(
        "--curated-orthologs",
        default="data/input/curated_ortholog_candidates.csv",
        help="Input CSV containing curated ortholog candidate rows.",
    )
    parser.add_argument(
        "--expected-results",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_enrichment_mapped.parquet",
        help="Expected enrichment/results table used to audit candidate coverage.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_curated_ortholog_input_validation.csv",
        help="Output validation CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    curated_ortholog_path = Path(args.curated_orthologs)
    expected_path = Path(args.expected_results)
    output_path = Path(args.output)

    expected = read_expected_results(expected_path)

    if curated_ortholog_path.exists():
        candidates: pl.DataFrame | None = pl.read_csv(curated_ortholog_path)

        duplicate_rows = find_duplicate_curated_ortholog_rows(candidates)
        if duplicate_rows.height > 0:
            print("Duplicate curated ortholog rows detected:")
            print(duplicate_rows)
    else:
        candidates = None

    validation = build_curated_ortholog_input_validation(expected, candidates)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    validation.write_csv(output_path)

    print(f"Wrote curated ortholog input validation -> {output_path}")
    print()
    print("Input status counts:")
    for row in (
        validation.group_by("input_status").len().sort("len", descending=True).iter_rows(named=True)
    ):
        print(f"  {row['input_status']}: {row['len']}")
    print()
    print(
        "Rows with curated ortholog candidates: "
        f"{validation.filter(pl.col('has_curated_ortholog_candidate')).height}"
    )


if __name__ == "__main__":
    main()
