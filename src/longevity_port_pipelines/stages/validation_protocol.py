"""Task D: Computational validation protocol — score and prioritise candidates.

Checks each candidate against 10 criteria, generates scored CSV, markdown
protocol, and SVG summary plots.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import requests

from longevity_port_pipelines.config import PipelineConfig

logger = logging.getLogger(__name__)

ALPHAFOLD_API = "https://alphafold.ebi.ac.uk/api/prediction"


def _to_float(val: object, default: float = 0.0) -> float:
    try:
        return float(val)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def check_alphafold_structure(uniprot_id: str, cache_dir: Path) -> bool:
    """Check if AlphaFold DB has a predicted structure for this protein."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"alphafold_{uniprot_id}.json"

    if cache_file.exists():
        with open(cache_file) as f:
            data = json.load(f)
        return bool(data)

    url = f"{ALPHAFOLD_API}/{uniprot_id}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 404:
            with open(cache_file, "w") as f:
                json.dump([], f)
            return False
        resp.raise_for_status()
        data = resp.json()
        with open(cache_file, "w") as f:
            json.dump(data, f)
        return bool(data)
    except requests.RequestException:
        logger.warning("AlphaFold DB check failed for %s", uniprot_id)
        return False


def score_candidates(
    candidates_df: pl.DataFrame,
    interactome_df: pl.DataFrame,
    cfg: PipelineConfig,
) -> pl.DataFrame:
    """Score each candidate on 10 validation criteria."""
    alphafold_cache = cfg.interim_dir / "alphafold"
    breakage_path = cfg.output_dir / "breakage_taxonomy.csv"
    has_breakage_table = breakage_path.exists()

    rows: list[dict[str, object]] = []

    for cand_row in candidates_df.iter_rows(named=True):
        gene: str = cand_row["gene_name"]
        uniprot_id: str = cand_row["uniprot_id"]
        category: str = cand_row["category"]

        inter_match = interactome_df.filter(pl.col("gene_name") == gene)
        if inter_match.height == 0:
            logger.warning("No interactome data for %s — skipping", gene)
            continue

        inter_row = inter_match.row(0, named=True)

        has_structure = check_alphafold_structure(uniprot_id, alphafold_cache)
        n_partners = int(inter_row.get("n_partners", 0))
        has_interactors = n_partners > 0
        is_hub = bool(inter_row.get("is_hub", False))
        size_kda = _to_float(inter_row.get("size_kda", 0))
        under_80kda = 0 < size_kda < 80
        is_membrane = bool(inter_row.get("is_membrane", False))
        has_glycosylation = bool(inter_row.get("has_glycosylation", False))
        can_express_cellfree = under_80kda and not is_membrane and not has_glycosylation

        has_breakage_pattern = False
        if has_breakage_table:
            bt = pl.read_csv(breakage_path)
            filled = bt.filter(
                (pl.col("protein") == gene)
                & (pl.col("desired_interaction_state") != "")
            )
            has_breakage_pattern = filled.height > 0

        score = sum([
            has_structure,
            True,
            has_interactors,
            not is_hub,
            under_80kda and not is_membrane,
            has_breakage_pattern,
            can_express_cellfree,
            under_80kda,
            not is_membrane,
            not has_glycosylation,
        ])

        if score >= 8:
            tier = "high"
        elif score >= 5:
            tier = "medium"
        else:
            tier = "low"

        rows.append({
            "gene_name": gene,
            "uniprot_id": uniprot_id,
            "category": category,
            "has_structure": has_structure,
            "has_human_ortholog": True,
            "has_interactors": has_interactors,
            "n_partners": n_partners,
            "is_hub": is_hub,
            "has_breakage_pattern": has_breakage_pattern,
            "can_express_cellfree": can_express_cellfree,
            "size_kda": size_kda,
            "under_80kda": under_80kda,
            "is_membrane": is_membrane,
            "has_glycosylation": has_glycosylation,
            "priority_score": score,
            "priority_tier": tier,
        })

    return pl.DataFrame(rows) if rows else pl.DataFrame()


# ---------------------------------------------------------------------------
# SVG plots
# ---------------------------------------------------------------------------

def plot_priority_overview(scores_df: pl.DataFrame, plots_dir: Path) -> None:
    """Bar chart of candidates coloured by priority tier, sorted by score."""
    plots_dir.mkdir(parents=True, exist_ok=True)

    df = scores_df.sort("priority_score", descending=True)
    colour_map = {"high": "#2ecc71", "medium": "#f39c12", "low": "#e74c3c"}

    fig = px.bar(
        df.to_pandas(),
        x="gene_name",
        y="priority_score",
        color="priority_tier",
        color_discrete_map=colour_map,
        title="Candidate Priority Scores",
        labels={"gene_name": "Gene", "priority_score": "Score (0-10)", "priority_tier": "Tier"},
    )
    fig.update_layout(xaxis_tickangle=-45, template="plotly_white")
    fig.write_image(str(plots_dir / "priority_scores.svg"))
    logger.info("Wrote priority_scores.svg")


def plot_hub_vs_score(scores_df: pl.DataFrame, plots_dir: Path) -> None:
    """Scatter: partner count vs priority score, sized by kDa."""
    plots_dir.mkdir(parents=True, exist_ok=True)

    colour_map = {"high": "#2ecc71", "medium": "#f39c12", "low": "#e74c3c"}
    fig = px.scatter(
        scores_df.to_pandas(),
        x="n_partners",
        y="priority_score",
        color="priority_tier",
        color_discrete_map=colour_map,
        size="size_kda",
        text="gene_name",
        title="Hub Status vs Priority Score",
        labels={"n_partners": "Interaction Partners", "priority_score": "Score (0-10)"},
    )
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.update_layout(template="plotly_white")
    fig.write_image(str(plots_dir / "hub_vs_score.svg"))
    logger.info("Wrote hub_vs_score.svg")


def plot_category_breakdown(scores_df: pl.DataFrame, plots_dir: Path) -> None:
    """Grouped bar: category vs mean score."""
    plots_dir.mkdir(parents=True, exist_ok=True)

    cat_summary = (
        scores_df.group_by("category")
        .agg(
            pl.col("priority_score").mean().alias("mean_score"),
            pl.col("priority_score").count().alias("n_proteins"),
            (pl.col("priority_tier") == "high").sum().alias("n_high"),
        )
        .sort("mean_score", descending=True)
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cat_summary.get_column("category").to_list(),
        y=cat_summary.get_column("mean_score").to_list(),
        name="Mean Score",
        marker_color="#3498db",
        text=[f"{v:.1f}" for v in cat_summary.get_column("mean_score").to_list()],
        textposition="outside",
    ))
    fig.update_layout(
        title="Mean Priority Score by Category",
        xaxis_title="Category", yaxis_title="Mean Score",
        template="plotly_white", xaxis_tickangle=-30,
    )
    fig.write_image(str(plots_dir / "category_breakdown.svg"))
    logger.info("Wrote category_breakdown.svg")


# ---------------------------------------------------------------------------
# Markdown protocol
# ---------------------------------------------------------------------------

def write_protocol_markdown(scores_df: pl.DataFrame, output_dir: Path) -> Path:
    """Write the computational validation protocol as markdown."""
    out_path = output_dir / "validation_protocol.md"

    high = scores_df.filter(pl.col("priority_tier") == "high")
    medium = scores_df.filter(pl.col("priority_tier") == "medium")
    low = scores_df.filter(pl.col("priority_tier") == "low")

    lines: list[str] = [
        "# Computational Validation Protocol",
        "",
        "## 1. Input",
        "",
        "- Candidate protein (gene name, UniProt ID)",
        "- Target species: naked mole-rat (10181), bowhead whale (27622), "
        "Myotis lucifugus (59463), mouse (10090)",
        "- Known interactors from OmniPath (STRING + BioGRID + IntAct + Reactome)",
        "",
        "## 2. Output",
        "",
        "Priority ranking for AF3/Boltz/Chai structure prediction and Adaptyv "
        "experimental validation.",
        "",
        "## 3. Scoring criteria (10 points max)",
        "",
        "| # | Criterion | Weight | Source |",
        "|---|-----------|--------|--------|",
        "| 1 | Has AlphaFold structural model | 1 | AlphaFold DB API |",
        "| 2 | Has human ortholog | 1 | Always true (start from human) |",
        "| 3 | Has known interactors | 1 | OmniPath |",
        "| 4 | Not excessive hub (<=15 partners) | 1 | OmniPath partner count |",
        "| 5 | Assay feasibility (not membrane, <80 kDa) | 1 | UniProt |",
        "| 6 | Has defined breakage/maintained pattern | 1 | Breakage taxonomy |",
        "| 7 | Cell-free expressible (<80 kDa, soluble, no glycosylation) | 1 | UniProt |",
        "| 8 | Size < 80 kDa | 1 | UniProt sequence mass |",
        "| 9 | Not a membrane protein | 1 | UniProt subcellular location |",
        "| 10 | No glycosylation requirement | 1 | UniProt PTM features |",
        "",
        "**Tiers:** high (8-10), medium (5-7), low (0-4)",
        "",
        "## 4. Candidate ranking",
        "",
    ]

    for label, df in [("HIGH priority", high), ("MEDIUM priority", medium), ("LOW priority", low)]:
        lines.append(f"### {label} ({df.height} proteins)")
        lines.append("")
        if df.height == 0:
            lines.append("(none)")
            lines.append("")
            continue
        lines.append(
            "| Gene | UniProt | Category | Score | Size (kDa) | Hub | Membrane | Glyco |"
        )
        lines.append("|------|---------|----------|-------|------------|-----|----------|-------|")
        for r in df.sort("priority_score", descending=True).iter_rows(named=True):
            lines.append(
                f"| {r['gene_name']} | {r['uniprot_id']} | {r['category']} "
                f"| {r['priority_score']}/10 | {r['size_kda']:.1f} "
                f"| {'YES' if r['is_hub'] else 'no'} "
                f"| {'YES' if r['is_membrane'] else 'no'} "
                f"| {'YES' if r['has_glycosylation'] else 'no'} |"
            )
        lines.append("")

    lines.extend([
        "## 5. Recommended workflow",
        "",
        "1. **Review this ranking** — adjust scores for domain knowledge.",
        "2. **Fill breakage_taxonomy.csv** — mark desired interaction states "
        "(maintained / broken / rewired).",
        "3. **Fetch orthologs** — `uv run orthologs` for cross-species coverage.",
        "4. **Submit to AF3/Boltz/Chai** — high-priority, non-hub candidates.",
        "5. **Adaptyv validation** — prioritise cell-free expressible candidates.",
        "",
        "## 6. Plots",
        "",
        "See `data/output/plots/` for:",
        "- `priority_scores.svg` — bar chart of all candidates by score",
        "- `hub_vs_score.svg` — partner count vs priority (hub filter rationale)",
        "- `category_breakdown.svg` — mean score per functional category",
        "",
    ])

    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    logger.info("Wrote validation protocol -> %s", out_path)
    return out_path


# ---------------------------------------------------------------------------
# Stage runner
# ---------------------------------------------------------------------------

def run_stage(cfg: PipelineConfig, candidates_df: pl.DataFrame) -> pl.DataFrame:
    """Run validation scoring. Writes scores CSV, protocol MD, and SVG plots."""
    interactome_path = cfg.output_dir / "interactome.csv"
    if not interactome_path.exists():
        msg = f"Missing {interactome_path} — run `uv run interactome` first."
        raise FileNotFoundError(msg)

    interactome_df = pl.read_csv(interactome_path)
    scores_df = score_candidates(candidates_df, interactome_df, cfg)

    scores_path = cfg.output_dir / "validation_scores.csv"
    scores_df.write_csv(scores_path)
    logger.info("Wrote validation scores: %d proteins -> %s", len(scores_df), scores_path)

    write_protocol_markdown(scores_df, cfg.output_dir)

    plots_dir = cfg.output_dir / "plots"
    plot_priority_overview(scores_df, plots_dir)
    plot_hub_vs_score(scores_df, plots_dir)
    plot_category_breakdown(scores_df, plots_dir)

    return scores_df
