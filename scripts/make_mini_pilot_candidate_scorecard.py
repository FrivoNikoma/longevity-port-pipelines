from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.scorecard import (
    build_candidate_scorecard,
    load_negative_control_audit,
    load_recurrent_counts,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a candidate scorecard from mini-pilot outcome and residue-level summaries."
    )
    parser.add_argument(
        "--outcomes",
        default="data/output/sirt6_mini_pilot_interaction_outcome_summary.csv",
        help="Interaction outcome summary CSV.",
    )
    parser.add_argument(
        "--recurrent-residues",
        default="data/output/sirt6_mini_pilot_recurrent_interface_residues.csv",
        help="Recurrent residue candidates CSV.",
    )
    parser.add_argument(
        "--negative-control-audit",
        default="data/output/sirt6_mini_pilot_negative_control_audit.csv",
        help="Negative-control audit CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_candidate_scorecard.csv",
        help="Output candidate scorecard CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    outcome_path = Path(args.outcomes)
    recurrent_path = Path(args.recurrent_residues)
    negative_control_path = Path(args.negative_control_audit)
    output_path = Path(args.output)

    if not outcome_path.exists():
        raise FileNotFoundError(f"Missing interaction outcome summary: {outcome_path}")

    outcomes = pl.read_csv(outcome_path)
    recurrent_counts = load_recurrent_counts(recurrent_path)
    negative_control_audit = load_negative_control_audit(negative_control_path)

    out_df = build_candidate_scorecard(
        outcomes=outcomes,
        recurrent_counts=recurrent_counts,
        negative_control_audit=negative_control_audit,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.write_csv(output_path)

    print(f"Wrote candidate scorecard -> {output_path}")
    print()
    print(f"Scorecard shape: {out_df.shape}")

    print()
    print("Control status counts:")
    for row in (
        out_df.group_by(["control_status", "control_interpretation"])
        .len()
        .sort("len", descending=True)
        .iter_rows(named=True)
    ):
        print(f"  {row['control_status']} / {row['control_interpretation']}: {row['len']}")
    print()
    print(f"Controlled pass count: {out_df.filter(pl.col('passes_controls')).height}")
    print(f"Top scorecard row count shown: {min(out_df.height, 15)}")

    print()
    print("Outcome counts:")
    for row in (
        out_df.group_by(["proposal_outcome_class", "confidence"])
        .len()
        .sort("len", descending=True)
        .iter_rows(named=True)
    ):
        print(f"  {row['proposal_outcome_class']} / {row['confidence']}: {row['len']}")


if __name__ == "__main__":
    main()
