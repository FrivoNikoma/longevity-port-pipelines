"""Task A: Load candidate longevity proteins from data/input/candidates.csv.

The CSV is the single source of truth for the candidate universe.
"""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

from longevity_port_pipelines.models import LongevityCategory

logger = logging.getLogger(__name__)

CANDIDATES_FILE = "candidates.csv"

VALID_CATEGORIES = {c.value for c in LongevityCategory}


def candidates_dataframe(input_dir: Path) -> pl.DataFrame:
    """Load candidates from data/input/candidates.csv."""
    csv_path = input_dir / CANDIDATES_FILE
    if not csv_path.exists():
        msg = f"Candidates file not found: {csv_path}"
        raise FileNotFoundError(msg)

    lines = [
        line for line in csv_path.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if len(lines) <= 1:
        msg = f"No candidate rows in {csv_path}"
        raise ValueError(msg)

    csv_text = "\n".join(lines)
    df = pl.read_csv(csv_text.encode())

    required = {"gene_name", "uniprot_id", "category"}
    missing = required - set(df.columns)
    if missing:
        msg = f"Candidates CSV missing columns: {missing}"
        raise ValueError(msg)

    if "description" not in df.columns:
        df = df.with_columns(pl.lit("").alias("description"))

    bad_cats = set(df.get_column("category").to_list()) - VALID_CATEGORIES
    if bad_cats:
        logger.warning(
            "Unknown categories in candidates CSV: %s (valid: %s)",
            bad_cats, sorted(VALID_CATEGORIES),
        )

    df = df.unique(subset=["gene_name"], keep="first")
    return df


def run_stage(output_dir: Path, input_dir: Path = Path("data/input")) -> pl.DataFrame:
    """Write candidates.csv and return the DataFrame."""
    output_dir.mkdir(parents=True, exist_ok=True)

    df = candidates_dataframe(input_dir)
    out_path = output_dir / "candidates.csv"
    df.write_csv(out_path)
    logger.info("Wrote %d candidate proteins -> %s", len(df), out_path)

    summary = df.group_by("category").len().sort("len", descending=True)
    for row in summary.iter_rows(named=True):
        logger.info("  %s: %d proteins", row["category"], row["len"])

    return df
