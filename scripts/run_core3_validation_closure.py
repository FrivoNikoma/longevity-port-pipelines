from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path

import polars as pl

CORE3_PREFIX = "sirt6_mini_pilot_v2_core3_expanded"
SIGNAL_SUMMARY = Path(f"data/output/{CORE3_PREFIX}_embedding_signal_summary.csv")
ENRICHMENT_PARQUET = Path(f"data/output/{CORE3_PREFIX}_enrichment_mapped.parquet")
NEGATOME_PAIRS = Path("data/interim/negatome_control_pairs.csv")
NEGATOME_VALIDATION = Path(f"data/output/{CORE3_PREFIX}_negatome_control_input_validation.csv")
NEGATIVE_CONTROL_AUDIT = Path(f"data/output/{CORE3_PREFIX}_negative_control_audit.csv")
OUTCOME_SUMMARY = Path(f"data/output/{CORE3_PREFIX}_interaction_outcome_summary.csv")
SCORECARD = Path(f"data/output/{CORE3_PREFIX}_candidate_scorecard.csv")
VALIDATION_PLAN_CSV = Path(f"data/output/{CORE3_PREFIX}_validation_plan.csv")
VALIDATION_PLAN_MD = Path(f"data/output/{CORE3_PREFIX}_validation_plan.md")
VALIDATION_SUMMARY_MD = Path(f"data/output/{CORE3_PREFIX}_validation_closure_summary.md")
SELECTION = Path(f"data/output/{CORE3_PREFIX}_selection.csv")
COVERAGE = Path(f"data/output/{CORE3_PREFIX}_ortholog_coverage.csv")
EMBEDDING_DIR = Path("data/output/embeddings")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run phase-0 validation closure for the core3-expanded mini-pilot."
    )
    parser.add_argument(
        "--skip-embed",
        action="store_true",
        help="Skip Biohub embedding steps even when BIOHUB_API_TOKEN is available.",
    )
    parser.add_argument(
        "--skip-analyze",
        action="store_true",
        help="Skip mapped enrichment re-analysis; use existing enrichment parquet only.",
    )
    return parser.parse_args()


def run_step(label: str, command: list[str]) -> None:
    print(f"\n=== {label} ===")
    print(" ".join(command))
    subprocess.run(command, check=True)


def normalize_enrichment_numeric_columns(df: pl.DataFrame) -> pl.DataFrame:
    numeric_columns = [
        "interface_mean_delta",
        "noninterface_mean_delta",
        "enrichment_ratio",
        "shuffled_control_ratio",
        "negatome_control_ratio",
        "mann_whitney_p",
        "p_interface_greater",
        "p_interface_less",
        "p_two_sided",
        "effect_size_cohens_d",
    ]
    expressions = [
        pl.col(column).cast(pl.Float64, strict=False)
        for column in numeric_columns
        if column in df.columns
    ]
    if not expressions:
        return df
    return df.with_columns(expressions)


def filter_core3_viewer_rows(signal_summary: pl.DataFrame, viewer_path: Path) -> pl.DataFrame:
    viewer = pl.read_csv(viewer_path)
    keys = viewer.select(["complex_id", "chain", "target_species"]).unique()
    return signal_summary.join(keys, on=["complex_id", "chain", "target_species"], how="inner")


def write_closure_summary(
    *,
    enrichment: pl.DataFrame,
    audit: pl.DataFrame,
    scorecard: pl.DataFrame,
    output_path: Path,
) -> None:
    lines = [
        f"# {CORE3_PREFIX} validation closure summary",
        "",
        "## Enrichment coverage",
        "",
        f"- Rows in core3 enrichment table: `{enrichment.height}`",
        f"- Rows with NEGATOME ratio populated: `{enrichment.filter(pl.col('negatome_control_ratio').is_not_null()).height}`",
        f"- Rows missing NEGATOME (no chain embeddings for patch): `{enrichment.filter(pl.col('negatome_control_ratio').is_null()).height}`",
        "",
        "## Control audit",
        "",
    ]

    if audit.height > 0:
        status_counts = audit.group_by("control_status").len().sort("len", descending=True)
        tier_counts = audit.group_by("control_evidence_tier").len().sort("len", descending=True)
        lines.append("Control status counts:")
        lines.append("")
        lines.append("```text")
        buffer = io.StringIO()
        status_counts.write_csv(buffer)
        lines.append(buffer.getvalue().strip())
        lines.append("```")
        lines.append("")
        lines.append("Control evidence tier counts:")
        lines.append("")
        lines.append("```text")
        buffer = io.StringIO()
        tier_counts.write_csv(buffer)
        lines.append(buffer.getvalue().strip())
        lines.append("```")
        lines.append("")
        passes = audit.filter(pl.col("passes_controls"))
        lines.append(f"- Controlled pass count: `{passes.height}`")
    else:
        lines.append("- Negative-control audit not available.")

    lines.extend(["", "## Scorecard", ""])
    if scorecard.height > 0:
        controlled = scorecard.filter(pl.col("control_evidence_tier") == "controlled_pass")
        lines.append(f"- Scorecard rows: `{scorecard.height}`")
        lines.append(f"- Controlled pass rows: `{controlled.height}`")
        lines.append("")
        lines.append("Top controlled-pass candidates:")
        lines.append("")
        if controlled.height > 0:
            lines.append("```text")
            buffer = io.StringIO()
            controlled.select(
                [
                    "candidate_id",
                    "proposal_outcome_class",
                    "confidence",
                    "score",
                    "control_evidence_tier",
                    "passes_controls",
                ]
            ).head(10).write_csv(buffer)
            lines.append(buffer.getvalue().strip())
            lines.append("```")
        else:
            lines.append("No rows currently pass the strict controlled gate.")
    else:
        lines.append("- Scorecard not available.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    viewer_path = Path(f"data/output/{CORE3_PREFIX}_viewer_structure_selections.csv")

    python = sys.executable

    run_step(
        "Build curated NEGATOME control pairs",
        [python, "-m", "scripts.build_core3_negatome_control_pairs"],
    )

    if not SIGNAL_SUMMARY.exists():
        raise FileNotFoundError(f"Missing signal summary: {SIGNAL_SUMMARY}")

    signal_summary = pl.read_csv(SIGNAL_SUMMARY)
    core3_enrichment = normalize_enrichment_numeric_columns(
        filter_core3_viewer_rows(signal_summary, viewer_path)
    )
    ENRICHMENT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    core3_enrichment.write_parquet(ENRICHMENT_PARQUET)
    print(
        f"\nWrote baseline core3 enrichment parquet -> {ENRICHMENT_PARQUET} ({core3_enrichment.height} rows)"
    )

    run_step(
        "Validate NEGATOME control inputs",
        [
            python,
            "-m",
            "scripts.validate_negatome_control_inputs",
            "--expected-results",
            str(ENRICHMENT_PARQUET),
            "--output",
            str(NEGATOME_VALIDATION),
        ],
    )

    has_embeddings = EMBEDDING_DIR.exists() and any(EMBEDDING_DIR.rglob("*.npy"))
    if not args.skip_embed and NEGATOME_PAIRS.exists():
        run_step(
            "Embed NEGATOME negative partners",
            [python, "-m", "scripts.embed_negatome_control_partners"],
        )

    if not args.skip_analyze and has_embeddings and NEGATOME_PAIRS.exists():
        run_step(
            "Patch NEGATOME controls onto enrichment",
            [python, "-m", "scripts.patch_core3_negatome_controls"],
        )
    elif not args.skip_analyze:
        print(
            "\nSkipping NEGATOME ratio patching. Using baseline enrichment parquet "
            f"(embeddings present={has_embeddings})."
        )

    run_step(
        "Audit negative controls",
        [
            python,
            "-m",
            "scripts.audit_negative_controls",
            "--input",
            str(ENRICHMENT_PARQUET),
            "--output",
            str(NEGATIVE_CONTROL_AUDIT),
        ],
    )

    run_step(
        "Classify interaction outcomes",
        [
            python,
            "-m",
            "scripts.classify_interaction_outcomes",
            "--signal-summary",
            str(SIGNAL_SUMMARY),
            "--output",
            str(OUTCOME_SUMMARY),
        ],
    )

    outcome_df = pl.read_csv(OUTCOME_SUMMARY)
    viewer_keys = (
        pl.read_csv(viewer_path).select(["complex_id", "chain", "target_species"]).unique()
    )
    filtered_outcomes = outcome_df.join(
        viewer_keys,
        on=["complex_id", "chain", "target_species"],
        how="inner",
    )
    filtered_outcomes.write_csv(OUTCOME_SUMMARY)

    run_step(
        "Build candidate scorecard",
        [
            python,
            "-m",
            "scripts.make_mini_pilot_candidate_scorecard",
            "--outcomes",
            str(OUTCOME_SUMMARY),
            "--negative-control-audit",
            str(NEGATIVE_CONTROL_AUDIT),
            "--output",
            str(SCORECARD),
        ],
    )

    run_step(
        "Generate validation plan",
        [
            python,
            "-m",
            "scripts.generate_mini_pilot_validation_plan",
            "--scorecard",
            str(SCORECARD),
            "--output-csv",
            str(VALIDATION_PLAN_CSV),
            "--output-md",
            str(VALIDATION_PLAN_MD),
        ],
    )

    enrichment = pl.read_parquet(ENRICHMENT_PARQUET)
    audit = (
        pl.read_csv(NEGATIVE_CONTROL_AUDIT) if NEGATIVE_CONTROL_AUDIT.exists() else pl.DataFrame()
    )
    scorecard = pl.read_csv(SCORECARD) if SCORECARD.exists() else pl.DataFrame()
    write_closure_summary(
        enrichment=enrichment,
        audit=audit,
        scorecard=scorecard,
        output_path=VALIDATION_SUMMARY_MD,
    )

    print(f"\nWrote validation closure summary -> {VALIDATION_SUMMARY_MD}")


if __name__ == "__main__":
    main()
