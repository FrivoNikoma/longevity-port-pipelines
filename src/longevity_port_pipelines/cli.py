"""CLI entry points using Typer. Each pipeline stage is a direct command."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv

from longevity_port_pipelines.config import PipelineConfig

# Load .env so BIOHUB_API_TOKEN (and friends) are available to every command.
load_dotenv()

InputDir = Annotated[Path, typer.Option(help="Directory for downloaded source data")]
OutputDir = Annotated[Path, typer.Option(help="Directory for pipeline outputs")]
Verbose = Annotated[bool, typer.Option("--verbose", "-v", help="Enable debug logging")]


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )


def _cfg(input_dir: Path, output_dir: Path, **overrides: object) -> PipelineConfig:
    cfg = PipelineConfig(input_dir=input_dir, output_dir=output_dir, **overrides)  # type: ignore[arg-type]
    cfg.ensure_dirs()
    return cfg


def select(
    input_dir: InputDir = Path("data/input"),
    output_dir: OutputDir = Path("data/output"),
    count: Annotated[int, typer.Option(help="Number of complexes to select")] = 10,
    verbose: Verbose = False,
) -> None:
    """Stages 1-3: Load PINDER, filter by Foldseek conservation, annotate STRING hubs."""
    _setup_logging(verbose)
    from longevity_port_pipelines.stages import load_foldseek, load_pinder, load_string

    cfg = _cfg(input_dir, output_dir, selection_count=count)
    candidates = load_pinder.run_stage(cfg)
    candidates = load_foldseek.run_stage(candidates, cfg)
    load_string.run_stage(candidates, cfg)
    typer.echo(f"Selection written to {output_dir / 'selection.csv'}")


def orthologs(
    input_dir: InputDir = Path("data/input"),
    output_dir: OutputDir = Path("data/output"),
    verbose: Verbose = False,
) -> None:
    """Stage 4: Fetch orthologs from OMA/UniProt for long-lived species."""
    _setup_logging(verbose)
    import polars as pl

    from longevity_port_pipelines.stages import fetch_orthologs

    cfg = _cfg(input_dir, output_dir)

    selection_path = output_dir / "selection.csv"
    if not selection_path.exists():
        typer.echo("No selection.csv found — run `select` first.", err=True)
        raise typer.Exit(1)

    candidates = pl.scan_csv(selection_path)
    fetch_orthologs.run_stage(candidates, cfg)
    typer.echo(f"Ortholog coverage written to {output_dir / 'ortholog_coverage.csv'}")


def embed(
    input_dir: InputDir = Path("data/input"),
    output_dir: OutputDir = Path("data/output"),
    verbose: Verbose = False,
) -> None:
    """Stage 5: Embed reference + ortholog sequences with ESM C via the Biohub API."""
    _setup_logging(verbose)
    import polars as pl

    from longevity_port_pipelines.models import OrthologMapping
    from longevity_port_pipelines.pipeline import run_stage_5

    cfg = _cfg(input_dir, output_dir)

    selection_path = output_dir / "selection.csv"
    coverage_path = output_dir / "ortholog_coverage.csv"
    if not selection_path.exists() or not coverage_path.exists():
        typer.echo(
            "Missing selection.csv or ortholog_coverage.csv — run earlier stages first.", err=True
        )
        raise typer.Exit(1)

    candidates = pl.scan_csv(selection_path)
    coverage_df = pl.read_csv(coverage_path)
    mappings = [OrthologMapping(**row) for row in coverage_df.to_dicts()]

    run_stage_5(candidates, mappings, cfg)
    typer.echo(f"Embeddings written to {output_dir / 'embeddings'}")


def analyze(
    output_dir: OutputDir = Path("data/output"),
    verbose: Verbose = False,
) -> None:
    """Stage 6: Compute enrichment at interface vs non-interface residues."""
    _setup_logging(verbose)
    typer.echo(f"Results will be written to {output_dir / 'enrichment.parquet'}")
    typer.echo("(This stage runs as part of `run-pipeline` — standalone mode not yet wired)")


def plot(
    output_dir: OutputDir = Path("data/output"),
    verbose: Verbose = False,
) -> None:
    """Stage 7: Generate enrichment summary and volcano plots."""
    _setup_logging(verbose)
    import polars as pl

    from longevity_port_pipelines.models import EnrichmentResult
    from longevity_port_pipelines.stages.plot import plot_enrichment_summary, plot_pvalue_volcano

    enrichment_path = output_dir / "enrichment.parquet"
    if not enrichment_path.exists():
        typer.echo("No enrichment.parquet found — run analysis first.", err=True)
        raise typer.Exit(1)

    df = pl.read_parquet(enrichment_path)
    results = [EnrichmentResult(**row) for row in df.to_dicts()]
    plot_enrichment_summary(results, output_dir)
    plot_pvalue_volcano(results, output_dir)
    typer.echo(f"Plots written to {output_dir / 'plots'}")


def candidates(
    input_dir: InputDir = Path("data/input"),
    output_dir: OutputDir = Path("data/output"),
    verbose: Verbose = False,
) -> None:
    """Task A: Load candidate proteins from data/input/candidates.csv."""
    _setup_logging(verbose)
    import longevity_port_pipelines.stages.candidates as cand_mod

    df = cand_mod.run_stage(output_dir, input_dir)
    typer.echo(f"Wrote {len(df)} candidates -> {output_dir / 'candidates.csv'}")
    typer.echo(f"Edit the candidate list: {input_dir / 'candidates.csv'}")
    typer.echo("Categories:")
    for row in df.group_by("category").len().sort("len", descending=True).iter_rows(named=True):
        typer.echo(f"  {row['category']}: {row['len']}")


def interactome(
    input_dir: InputDir = Path("data/input"),
    output_dir: OutputDir = Path("data/output"),
    verbose: Verbose = False,
) -> None:
    """Task B: Fetch known interactors from OmniPath + UniProt for each candidate."""
    _setup_logging(verbose)
    import polars as pl

    import longevity_port_pipelines.stages.interactome as inter_mod

    cfg = _cfg(input_dir, output_dir)

    cand_path = output_dir / "candidates.csv"
    if not cand_path.exists():
        typer.echo("No candidates.csv found — run `uv run candidates` first.", err=True)
        raise typer.Exit(1)

    candidates_df = pl.read_csv(cand_path)
    summary_df, partners_df = inter_mod.run_stage(candidates_df, cfg)

    n_hubs = summary_df.filter(pl.col("is_hub")).height if "is_hub" in summary_df.columns else 0
    typer.echo(f"Interactome: {len(summary_df)} proteins, {len(partners_df)} interactions")
    typer.echo(f"Hub proteins (>{cfg.hub_partner_threshold} partners): {n_hubs}")
    typer.echo(
        f"Output: {output_dir / 'interactome.csv'}, {output_dir / 'interactome_partners.parquet'}"
    )


def breakage_table(
    output_dir: OutputDir = Path("data/output"),
    verbose: Verbose = False,
) -> None:
    """Task C: Generate breakage taxonomy table (protein x species x partners x desired state)."""
    _setup_logging(verbose)
    import polars as pl

    import longevity_port_pipelines.stages.breakage_table as bt_mod

    cand_path = output_dir / "candidates.csv"
    if not cand_path.exists():
        typer.echo("No candidates.csv found — run `uv run candidates` first.", err=True)
        raise typer.Exit(1)

    candidates_df = pl.read_csv(cand_path)
    table = bt_mod.run_stage(output_dir, candidates_df)
    typer.echo(f"Breakage taxonomy: {len(table)} rows -> {output_dir / 'breakage_taxonomy.csv'}")
    typer.echo("NOTE: 'desired_interaction_state' column is blank — fill manually for curation.")


def validation_protocol(
    input_dir: InputDir = Path("data/input"),
    output_dir: OutputDir = Path("data/output"),
    verbose: Verbose = False,
) -> None:
    """Task D: Score candidates and generate computational validation protocol."""
    _setup_logging(verbose)
    import polars as pl

    import longevity_port_pipelines.stages.validation_protocol as vp_mod

    cfg = _cfg(input_dir, output_dir)

    cand_path = output_dir / "candidates.csv"
    if not cand_path.exists():
        typer.echo("No candidates.csv found — run `uv run candidates` first.", err=True)
        raise typer.Exit(1)

    candidates_df = pl.read_csv(cand_path)
    scores_df = vp_mod.run_stage(cfg, candidates_df)

    for tier in ["high", "medium", "low"]:
        n = scores_df.filter(pl.col("priority_tier") == tier).height
        typer.echo(f"  {tier.upper()}: {n} proteins")

    typer.echo(f"Output: {output_dir / 'validation_scores.csv'}")
    typer.echo(f"Protocol: {output_dir / 'validation_protocol.md'}")


def run(
    input_dir: InputDir = Path("data/input"),
    output_dir: OutputDir = Path("data/output"),
    count: Annotated[int, typer.Option(help="Number of complexes to select")] = 10,
    pre_gpu_only: Annotated[
        bool, typer.Option(help="Stop after stage 4 (audit checkpoint)")
    ] = False,
    verbose: Verbose = False,
) -> None:
    """Run the full Prefect flow (all 7 stages), or stop at the pre-GPU checkpoint."""
    _setup_logging(verbose)
    from longevity_port_pipelines.flow import interface_signal_flow

    cfg = _cfg(input_dir, output_dir, selection_count=count)
    interface_signal_flow(cfg=cfg, pre_gpu_only=pre_gpu_only)
    typer.echo(f"Pipeline complete. Output: {output_dir}")


# --- console-script entry points -------------------------------------------------


def select_cmd() -> None:
    typer.run(select)


def orthologs_cmd() -> None:
    typer.run(orthologs)


def embed_cmd() -> None:
    typer.run(embed)


def analyze_cmd() -> None:
    typer.run(analyze)


def plot_cmd() -> None:
    typer.run(plot)


def run_cmd() -> None:
    typer.run(run)


def candidates_cmd() -> None:
    typer.run(candidates)


def interactome_cmd() -> None:
    typer.run(interactome)


def breakage_table_cmd() -> None:
    typer.run(breakage_table)


def validation_protocol_cmd() -> None:
    typer.run(validation_protocol)


# ── Poster rendering ──


def render_poster(
    html: Annotated[
        Path, typer.Option(help="Input HTML file")
    ] = Path("docs/poster/poster.html"),
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Output PNG path")
    ] = Path("docs/poster/poster.png"),
    width: Annotated[int, typer.Option(help="Viewport width (px)")] = 1680,
    height: Annotated[int, typer.Option(help="Viewport height (px)")] = 1800,
    verbose: Verbose = False,
) -> None:
    """Render the poster HTML to a PNG image using Chrome headless."""
    import shutil
    import subprocess

    _setup_logging(verbose)

    chrome = None
    for name in ("google-chrome", "chromium-browser", "chromium", "google-chrome-stable"):
        chrome = shutil.which(name)
        if chrome:
            break
    if not chrome:
        raise typer.BadParameter(
            "No Chrome/Chromium found. Install google-chrome or chromium-browser."
        )

    html_uri = html.resolve().as_uri()
    out = output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        chrome,
        "--headless",
        f"--screenshot={out}",
        f"--window-size={width},{height}",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        html_uri,
    ]

    logging.info("Rendering %s → %s (%dx%d)", html.name, out.name, width, height)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if not out.exists():
        logging.error("Chrome stderr: %s", result.stderr)
        raise typer.Exit(code=1)

    size_kb = out.stat().st_size / 1024
    logging.info("Done: %s (%.0f KB)", out, size_kb)


def render_poster_cmd() -> None:
    typer.run(render_poster)
