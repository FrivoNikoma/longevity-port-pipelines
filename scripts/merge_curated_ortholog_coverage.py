from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

import polars as pl

from longevity_port_pipelines.stages.ortholog_inputs import (
    ConflictPolicy,
    curated_candidates_to_ortholog_mappings,
    merge_ortholog_mappings,
    ortholog_mappings_from_frame,
    ortholog_mappings_to_frame,
    read_table,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge validated curated ortholog candidates into ortholog coverage rows."
    )
    parser.add_argument(
        "--standard-coverage",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage.csv",
        help="Existing standard ortholog coverage CSV.",
    )
    parser.add_argument(
        "--curated-orthologs",
        default="data/input/curated_ortholog_candidates.csv",
        help="Curated ortholog candidate CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage_with_curated.csv",
        help="Merged ortholog coverage output CSV.",
    )
    parser.add_argument(
        "--conflict-policy",
        choices=["keep_standard", "prefer_curated", "error"],
        default="keep_standard",
        help=(
            "How to handle source/species keys already present in standard coverage. "
            "Default keeps standard OMA/UniProt mappings."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    standard_path = Path(args.standard_coverage)
    curated_path = Path(args.curated_orthologs)
    output_path = Path(args.output)
    conflict_policy = cast(ConflictPolicy, args.conflict_policy)

    standard_mappings = ortholog_mappings_from_frame(read_table(standard_path))

    if curated_path.exists():
        curated_candidates = pl.read_csv(curated_path)
        curated_mappings = curated_candidates_to_ortholog_mappings(curated_candidates)
    else:
        curated_mappings = []

    merged = merge_ortholog_mappings(
        standard_mappings,
        curated_mappings,
        conflict_policy=conflict_policy,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ortholog_mappings_to_frame(merged).write_csv(output_path)

    print(f"standard mappings: {len(standard_mappings)}")
    print(f"curated mappings: {len(curated_mappings)}")
    print(f"merged mappings: {len(merged)}")
    print(f"conflict policy: {conflict_policy}")
    print(f"Wrote merged ortholog coverage -> {output_path}")


if __name__ == "__main__":
    main()
