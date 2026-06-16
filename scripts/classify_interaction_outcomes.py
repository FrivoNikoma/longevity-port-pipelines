from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.interaction_outcomes import (
    build_interaction_outcome_summary,
    load_optional_residue_table,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify mini-pilot interface embedding signals into proposal-level interaction outcomes."
    )
    parser.add_argument(
        "--signal-summary",
        default="data/output/sirt6_mini_pilot_embedding_signal_summary.csv",
        help="Input embedding signal summary CSV.",
    )
    parser.add_argument(
        "--top-divergent",
        default="data/output/sirt6_mini_pilot_top_divergent_interface_residues.csv",
        help="Top divergent residue candidates CSV.",
    )
    parser.add_argument(
        "--top-constrained",
        default="data/output/sirt6_mini_pilot_top_constrained_interface_residues.csv",
        help="Top constrained residue candidates CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_interaction_outcome_summary.csv",
        help="Output interaction outcome summary CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    signal_path = Path(args.signal_summary)
    top_divergent_path = Path(args.top_divergent)
    top_constrained_path = Path(args.top_constrained)
    output_path = Path(args.output)

    if not signal_path.exists():
        raise FileNotFoundError(f"Missing signal summary CSV: {signal_path}")

    signal_df = pl.read_csv(signal_path)
    top_divergent_df = load_optional_residue_table(top_divergent_path)
    top_constrained_df = load_optional_residue_table(top_constrained_path)

    out_df = build_interaction_outcome_summary(
        signal_df=signal_df,
        top_divergent_df=top_divergent_df,
        top_constrained_df=top_constrained_df,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.write_csv(output_path)

    print(f"Wrote interaction outcome summary -> {output_path}")
    print()
    print("Outcome class counts:")
    for row in (
        out_df.group_by(["proposal_outcome_class", "confidence"])
        .len()
        .sort("len", descending=True)
        .iter_rows(named=True)
    ):
        print(f"  {row['proposal_outcome_class']} / {row['confidence']}: {row['len']}")
    print()
    print(
        f"High/medium priority candidates: "
        f"{out_df.filter(pl.col('confidence').is_in(['high', 'medium'])).height}"
    )


if __name__ == "__main__":
    main()
