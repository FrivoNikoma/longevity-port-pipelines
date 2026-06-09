from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages.validation_plan import build_validation_plan

DEFAULT_SCORECARD = "data/output/sirt6_mini_pilot_candidate_scorecard.csv"
DEFAULT_OUTPUT_CSV = "data/output/sirt6_mini_pilot_validation_plan.csv"
DEFAULT_OUTPUT_MD = "data/output/sirt6_mini_pilot_validation_plan.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a preliminary validation plan from the mini-pilot candidate scorecard."
    )
    parser.add_argument(
        "--scorecard",
        default=DEFAULT_SCORECARD,
        help="Input mini-pilot candidate scorecard CSV.",
    )
    parser.add_argument(
        "--output-csv",
        default=DEFAULT_OUTPUT_CSV,
        help="Output validation plan CSV.",
    )
    parser.add_argument(
        "--output-md",
        default=DEFAULT_OUTPUT_MD,
        help="Output validation plan Markdown.",
    )
    return parser.parse_args()


def write_markdown(plan: pl.DataFrame, output_path: Path) -> None:
    columns = [
        "candidate_id",
        "protein",
        "target_species",
        "proposal_outcome_class",
        "confidence",
        "control_status",
        "evidence_level",
        "validation_priority",
        "primary_validation_assay",
        "control_requirement",
    ]

    lines = [
        "# SIRT6 mini-pilot validation plan",
        "",
        "This is a preliminary validation plan generated from the mini-pilot candidate scorecard.",
        "",
        "Important: candidates with `missing_negatome` are not fully controlled hits. They should be treated as shuffled-control-only evidence until NEGATOME-style control ratios are populated.",
        "",
        "| candidate_id | protein | target_species | outcome | confidence | control_status | evidence_level | validation_priority | primary_validation_assay | control_requirement |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for row in plan.select(columns).iter_rows(named=True):
        lines.append(
            "| "
            f"{row['candidate_id']} | "
            f"{row['protein']} | "
            f"{row['target_species']} | "
            f"{row['proposal_outcome_class']} | "
            f"{row['confidence']} | "
            f"{row['control_status']} | "
            f"{row['evidence_level']} | "
            f"{row['validation_priority']} | "
            f"{row['primary_validation_assay']} | "
            f"{row['control_requirement']} |"
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    scorecard_path = Path(args.scorecard)
    output_csv_path = Path(args.output_csv)
    output_md_path = Path(args.output_md)

    if not scorecard_path.exists():
        raise FileNotFoundError(f"Missing candidate scorecard: {scorecard_path}")

    scorecard = pl.read_csv(scorecard_path)
    plan = build_validation_plan(scorecard)

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    plan.write_csv(output_csv_path)
    write_markdown(plan, output_md_path)

    print(f"Wrote validation plan CSV -> {output_csv_path}")
    print(f"Wrote validation plan Markdown -> {output_md_path}")
    print()
    print("Validation priority counts:")
    print(
        plan.group_by(["validation_priority", "evidence_level"]).len().sort("len", descending=True)
    )

    print()
    print("Validation plan preview:")
    print(
        plan.select(
            [
                "candidate_id",
                "protein",
                "target_species",
                "proposal_outcome_class",
                "confidence",
                "control_status",
                "evidence_level",
                "validation_priority",
                "primary_validation_assay",
            ]
        ).head(15)
    )


if __name__ == "__main__":
    main()
