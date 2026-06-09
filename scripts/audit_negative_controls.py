from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.negative_controls import build_negative_control_audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit shuffled and NEGATOME-style negative controls for mini-pilot enrichment results."
    )
    parser.add_argument(
        "--input",
        default="data/output/sirt6_mini_pilot_enrichment_mapped.parquet",
        help="Input enrichment parquet path.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_negative_control_audit.csv",
        help="Output negative-control audit CSV path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Missing enrichment parquet: {input_path}")

    df = pl.read_parquet(input_path)
    audit = build_negative_control_audit(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit.write_csv(output_path)

    print(f"Wrote negative-control audit -> {output_path}")
    print()
    print("Control status counts:")
    print(audit.group_by("control_status").len().sort("len", descending=True))

    print()
    print("Audit preview:")
    print(
        audit.select(
            [
                "complex_id",
                "chain",
                "target_species",
                "enrichment_ratio",
                "shuffled_control_ratio",
                "negatome_control_ratio",
                "control_status",
            ]
        )
    )


if __name__ == "__main__":
    main()
