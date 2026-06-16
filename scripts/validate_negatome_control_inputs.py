from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.negatome_inputs import (
    build_negatome_input_validation,
    find_duplicate_negative_control_rows,
    read_expected_results,
)


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


def main() -> None:
    args = parse_args()

    negative_control_path = Path(args.negative_control_pairs)
    expected_path = Path(args.expected_results)
    output_path = Path(args.output)

    expected = read_expected_results(expected_path)

    if negative_control_path.exists():
        pairs: pl.DataFrame | None = pl.read_csv(negative_control_path)

        duplicate_rows = find_duplicate_negative_control_rows(pairs)
        if duplicate_rows.height > 0:
            print("Duplicate negative-control rows detected:")
            print(duplicate_rows)
    else:
        pairs = None

    validation = build_negatome_input_validation(expected, pairs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    validation.write_csv(output_path)

    print(f"Wrote NEGATOME-control input validation -> {output_path}")
    print()
    print("Input status counts:")
    for row in (
        validation.group_by("input_status").len().sort("len", descending=True).iter_rows(named=True)
    ):
        print(f"  {row['input_status']}: {row['len']}")
    print()
    print(
        f"Rows with negative-control input: {validation.filter(pl.col('has_negative_control_input')).height}"
    )


if __name__ == "__main__":
    main()
