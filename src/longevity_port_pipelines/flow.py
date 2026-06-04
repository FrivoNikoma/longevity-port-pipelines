"""Prefect orchestration — thin task wrappers around the typed stage modules.

The modules under src/longevity_port_pipelines/ are the product. Prefect just
sequences them, gives retries/caching on the download stages, and a run graph
with logs. Each task is a thin wrapper; the real logic lives in the modules.

Run with:  uv run run-pipeline           (via the typer CLI)
       or:  uv run python -m longevity_port_pipelines.flow
       or:  serve/deploy with Prefect for scheduled runs.
"""

from __future__ import annotations

import polars as pl
from prefect import flow, get_run_logger, task
from prefect.tasks import exponential_backoff

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.models import EnrichmentResult, OrthologMapping
from longevity_port_pipelines.pipeline import EmbeddingPair
from longevity_port_pipelines.stages import (
    fetch_orthologs,
    load_foldseek,
    load_pinder,
    load_string,
)

# Network-bound download stages get retries with backoff.
NETWORK_RETRIES = dict(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=5))


@task(name="load_pinder", **NETWORK_RETRIES)
def load_pinder_task(cfg: PipelineConfig) -> pl.LazyFrame:
    """Stage 1: download PINDER and select candidates."""
    return load_pinder.run_stage(cfg)


@task(name="load_foldseek", **NETWORK_RETRIES)
def load_foldseek_task(candidates: pl.LazyFrame, cfg: PipelineConfig) -> pl.LazyFrame:
    """Stage 2: structural-conservation filter."""
    return load_foldseek.run_stage(candidates, cfg)


@task(name="load_string", **NETWORK_RETRIES)
def load_string_task(candidates: pl.LazyFrame, cfg: PipelineConfig) -> pl.LazyFrame:
    """Stage 3: STRING hub annotation."""
    return load_string.run_stage(candidates, cfg)


@task(name="fetch_orthologs", **NETWORK_RETRIES)
def fetch_orthologs_task(
    candidates: pl.LazyFrame, cfg: PipelineConfig
) -> list[OrthologMapping]:
    """Stage 4: fetch orthologs for long-lived species."""
    _, mappings = fetch_orthologs.run_stage(candidates, cfg)
    return mappings


@task(name="embed")
def embed_task(
    candidates: pl.LazyFrame,
    mappings: list[OrthologMapping],
    cfg: PipelineConfig,
) -> list[EmbeddingPair]:
    """Stage 5: embedding via Biohub API (thin wrapper — logic in embed.py)."""
    from longevity_port_pipelines.pipeline import run_stage_5

    return run_stage_5(candidates, mappings, cfg)


@task(name="analyze")
def analyze_task(
    embedding_pairs: list[EmbeddingPair],
    cfg: PipelineConfig,
) -> list[EnrichmentResult]:
    """Stage 6: enrichment analysis with controls."""
    from longevity_port_pipelines.pipeline import run_stage_6

    return run_stage_6(embedding_pairs, cfg)


@task(name="plot")
def plot_task(results: list[EnrichmentResult], cfg: PipelineConfig) -> None:
    """Stage 7: Plotly figures."""
    from longevity_port_pipelines.pipeline import run_stage_7

    run_stage_7(results, cfg)


@flow(name="longevity-interface-signal")
def interface_signal_flow(
    cfg: PipelineConfig | None = None,
    pre_gpu_only: bool = False,
) -> list[EnrichmentResult]:
    """Full cross-species interface embedding signal check.

    Stages 1-4 produce selection.csv + ortholog_coverage.csv for human audit.
    Set pre_gpu_only=True to stop there (the documented audit checkpoint).
    """
    logger = get_run_logger()
    if cfg is None:
        cfg = PipelineConfig()
    cfg.ensure_dirs()

    candidates = load_pinder_task(cfg)
    candidates = load_foldseek_task(candidates, cfg)
    candidates = load_string_task(candidates, cfg)
    mappings = fetch_orthologs_task(candidates, cfg)

    logger.info(
        "PRE-GPU CHECKPOINT: review %s and %s before continuing",
        cfg.output_dir / "selection.csv",
        cfg.output_dir / "ortholog_coverage.csv",
    )

    if pre_gpu_only:
        logger.info("pre_gpu_only=True — stopping after stage 4")
        return []

    embedding_pairs = embed_task(candidates, mappings, cfg)
    results = analyze_task(embedding_pairs, cfg)
    plot_task(results, cfg)

    logger.info("Flow complete. Results in %s", cfg.output_dir)
    return results


def main() -> None:
    interface_signal_flow()


if __name__ == "__main__":
    main()
