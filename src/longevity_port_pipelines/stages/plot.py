"""Stage 7: Visualization with Plotly."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from longevity_port_pipelines.models import EnrichmentResult

logger = logging.getLogger(__name__)


def plot_delta_track(
    complex_id: str,
    residue_deltas: np.ndarray,
    interface_mask: np.ndarray,
    model_name: str,
    target_species: str,
    output_dir: Path,
) -> Path:
    """Per-residue delta track with interface residues highlighted."""
    fig = go.Figure()

    positions = np.arange(len(residue_deltas))

    fig.add_trace(go.Scatter(
        x=positions,
        y=residue_deltas,
        mode="lines",
        name="All residues",
        line=dict(color="steelblue", width=1),
    ))

    iface_positions = positions[interface_mask]
    iface_deltas = residue_deltas[interface_mask]
    fig.add_trace(go.Scatter(
        x=iface_positions,
        y=iface_deltas,
        mode="markers",
        name="Interface",
        marker=dict(color="crimson", size=4),
    ))

    fig.update_layout(
        title=f"{complex_id} — {model_name} — vs {target_species}",
        xaxis_title="Residue position",
        yaxis_title="Embedding delta (L2)",
        template="plotly_white",
        showlegend=True,
    )

    out_path = output_dir / "plots" / f"delta_track_{complex_id}_{model_name}_{target_species}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out_path))
    logger.info("Wrote delta track: %s", out_path)
    return out_path


def plot_enrichment_summary(
    results: list[EnrichmentResult],
    output_dir: Path,
) -> Path:
    """Summary bar chart: real enrichment vs both controls across all complexes."""
    if not results:
        logger.warning("No enrichment results to plot")
        return output_dir / "plots" / "enrichment_summary.html"

    labels = [f"{r.complex_id}/{r.chain}\n{r.target_species}" for r in results]

    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Bar(
        x=labels,
        y=[r.enrichment_ratio for r in results],
        name="Real interface",
        marker_color="crimson",
    ))

    fig.add_trace(go.Bar(
        x=labels,
        y=[r.shuffled_control_ratio for r in results],
        name="Shuffled control",
        marker_color="lightgray",
    ))

    negatome_vals = [r.negatome_control_ratio for r in results if r.negatome_control_ratio is not None]
    if negatome_vals:
        fig.add_trace(go.Bar(
            x=[labels[i] for i, r in enumerate(results) if r.negatome_control_ratio is not None],
            y=negatome_vals,
            name="NEGATOME control",
            marker_color="lightyellow",
        ))

    fig.add_hline(y=1.0, line_dash="dash", line_color="black", annotation_text="No enrichment")

    fig.update_layout(
        title="Interface enrichment vs controls",
        xaxis_title="Complex / species",
        yaxis_title="Enrichment ratio (interface / non-interface)",
        barmode="group",
        template="plotly_white",
    )

    out_path = output_dir / "plots" / "enrichment_summary.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out_path))
    logger.info("Wrote enrichment summary: %s", out_path)
    return out_path


def plot_pvalue_volcano(
    results: list[EnrichmentResult],
    output_dir: Path,
) -> Path:
    """Volcano-style plot: effect size vs -log10(p-value)."""
    if not results:
        return output_dir / "plots" / "volcano.html"

    fig = go.Figure()

    effect_sizes = [r.effect_size_cohens_d for r in results]
    neg_log_p = [-np.log10(max(r.mann_whitney_p, 1e-300)) for r in results]
    labels = [f"{r.complex_id}/{r.chain} vs {r.target_species}" for r in results]
    colors = ["crimson" if r.mann_whitney_p < 0.05 else "gray" for r in results]

    fig.add_trace(go.Scatter(
        x=effect_sizes,
        y=neg_log_p,
        mode="markers+text",
        text=labels,
        textposition="top center",
        textfont=dict(size=8),
        marker=dict(color=colors, size=8),
    ))

    fig.add_hline(y=-np.log10(0.05), line_dash="dash", line_color="gray",
                  annotation_text="p=0.05")

    fig.update_layout(
        title="Effect size vs significance",
        xaxis_title="Cohen's d",
        yaxis_title="-log10(p-value)",
        template="plotly_white",
    )

    out_path = output_dir / "plots" / "volcano.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out_path))
    logger.info("Wrote volcano plot: %s", out_path)
    return out_path
