from __future__ import annotations

import io
from pathlib import Path

import polars as pl

DEFAULT_CORE3_PREFIX = "sirt6_mini_pilot_v2_core3_expanded"


def write_closure_summary(
    *,
    enrichment: pl.DataFrame,
    audit: pl.DataFrame,
    scorecard: pl.DataFrame,
    output_path: Path,
    title_prefix: str = DEFAULT_CORE3_PREFIX,
) -> None:
    lines = [
        f"# {title_prefix} validation closure summary",
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
