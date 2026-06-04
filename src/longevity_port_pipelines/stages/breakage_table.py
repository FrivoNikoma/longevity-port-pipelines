"""Task C: Breakage taxonomy table.

For each candidate x target species, list functional and regulatory/degradation
partners with a desired-interaction-state column for human annotation.
"""

from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

from longevity_port_pipelines.config import LONG_LIVED_SPECIES, SHORT_LIVED_SPECIES

logger = logging.getLogger(__name__)

DEGRADATION_KEYWORDS = frozenset({
    "ubiquitin", "proteasome", "e3 ligase", "deubiquitin", "autophagy",
    "lysosome", "caspase", "apoptosis", "degradation",
})

REGULATORY_KEYWORDS = frozenset({
    "kinase", "phosphatase", "acetyltransferase", "deacetylase",
    "methyltransferase", "sumo", "nedd",
})


def _classify_partner(partner_gene: str) -> str:
    """Heuristic: regulatory/degradation vs functional based on gene name."""
    lower = partner_gene.lower()
    if any(kw in lower for kw in DEGRADATION_KEYWORDS | REGULATORY_KEYWORDS):
        return "regulatory"
    return "functional"


def build_breakage_table(
    candidates_df: pl.DataFrame,
    interactome_df: pl.DataFrame,
) -> pl.DataFrame:
    """Build the breakage taxonomy skeleton."""
    species_list = [s.name for s in LONG_LIVED_SPECIES + SHORT_LIVED_SPECIES]
    rows: list[dict[str, object]] = []

    for cand_row in candidates_df.iter_rows(named=True):
        gene: str = cand_row["gene_name"]
        uniprot_id: str = cand_row["uniprot_id"]
        category: str = cand_row["category"]

        top_partners_str = ""
        inter_match = interactome_df.filter(pl.col("gene_name") == gene)
        if inter_match.height > 0:
            top_partners_str = str(inter_match.row(0, named=True).get("top_partners", ""))

        partner_names = [p.strip() for p in top_partners_str.split(",") if p.strip()]

        functional = [p for p in partner_names if _classify_partner(p) == "functional"]
        regulatory = [p for p in partner_names if _classify_partner(p) == "regulatory"]

        for species in species_list:
            rows.append({
                "protein": gene,
                "uniprot_id": uniprot_id,
                "category": category,
                "species": species,
                "functional_partners": ", ".join(functional[:10]),
                "n_functional": len(functional),
                "regulatory_degradation_partners": ", ".join(regulatory[:10]),
                "n_regulatory": len(regulatory),
                "desired_interaction_state": "",
            })

    return pl.DataFrame(rows) if rows else pl.DataFrame()


def run_stage(output_dir: Path, candidates_df: pl.DataFrame) -> pl.DataFrame:
    """Run the breakage table stage. Reads interactome.csv, writes breakage_taxonomy.csv."""
    interactome_path = output_dir / "interactome.csv"
    if not interactome_path.exists():
        msg = f"Missing {interactome_path} — run `uv run interactome` first."
        raise FileNotFoundError(msg)

    interactome_df = pl.read_csv(interactome_path)
    table = build_breakage_table(candidates_df, interactome_df)

    out_path = output_dir / "breakage_taxonomy.csv"
    table.write_csv(out_path)
    logger.info("Wrote breakage taxonomy: %d rows -> %s", len(table), out_path)

    return table
