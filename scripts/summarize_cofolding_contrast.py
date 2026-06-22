"""
Summarize the cofolding contrast: join the ESM-C interface-divergence signal
(enrichment.parquet) with the Boltz structural co-folding result
(cofolding_results.parquet), so the two analysis layers sit side by side.

For each (complex_id, chain) it shows, per target species:
    enrichment_ratio   -- ESM-C interface divergence (higher = more divergent)
    iptm               -- Boltz interface confidence (higher = better-formed interface)
    binding_confidence -- Boltz binding confidence
    boltz_classification

It then computes a long-lived-vs-short-lived-control contrast on both layers,
so you can see whether the structural signal agrees with the embedding signal.

This is a reporting tool. Outputs go to gitignored data/output/ and are NOT
committed — only this script is.

Usage:
    uv run python scripts/summarize_cofolding_contrast.py
    uv run python scripts/summarize_cofolding_contrast.py --complex 5iso__A1_P54646--5iso__B1_Q9Y478
"""

from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.config import LONG_LIVED_SPECIES, SHORT_LIVED_SPECIES

DATA_OUTPUT = Path("data/output")
ENRICHMENT_PATH = DATA_OUTPUT / "enrichment.parquet"
COFOLDING_PATH = DATA_OUTPUT / "cofolding_results.parquet"
SUMMARY_CSV = DATA_OUTPUT / "cofolding_contrast_summary.csv"
SUMMARY_MD = DATA_OUTPUT / "cofolding_contrast_summary.md"

LONG_LIVED = [species.name for species in LONG_LIVED_SPECIES]
SHORT_LIVED_CONTROLS = [species.name for species in SHORT_LIVED_SPECIES]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize ESM vs Boltz cofolding contrast.")
    parser.add_argument(
        "--complex",
        default=None,
        help="Restrict to a single complex_id. Default: all complexes present in cofolding results.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not ENRICHMENT_PATH.exists():
        raise SystemExit(f"Missing {ENRICHMENT_PATH}. Run `uv run analyze` first.")
    if not COFOLDING_PATH.exists():
        raise SystemExit(f"Missing {COFOLDING_PATH}. Run `uv run cofolding` first.")

    enrichment = pl.read_parquet(ENRICHMENT_PATH)
    cofolding = pl.read_parquet(COFOLDING_PATH)

    # Columns we care about from each layer.
    esm = enrichment.select(["complex_id", "chain", "target_species", "enrichment_ratio"]).unique(
        subset=["complex_id", "chain", "target_species"], keep="first"
    )

    boltz_cols = [
        "complex_id",
        "chain",
        "target_species",
        "iptm",
        "binding_confidence",
        "boltz_classification",
    ]
    boltz_cols = [c for c in boltz_cols if c in cofolding.columns]
    boltz = cofolding.select(boltz_cols).unique(
        subset=["complex_id", "chain", "target_species"], keep="first"
    )

    # Inner join: only rows we actually co-folded.
    merged = boltz.join(esm, on=["complex_id", "chain", "target_species"], how="left")

    if args.complex:
        merged = merged.filter(pl.col("complex_id") == args.complex)

    if merged.is_empty():
        raise SystemExit("No overlapping rows between enrichment and cofolding results.")

    merged = merged.sort(["complex_id", "chain", "target_species"])

    # Write the per-row table.
    DATA_OUTPUT.mkdir(parents=True, exist_ok=True)
    merged.write_csv(SUMMARY_CSV)

    # Build a contrast view: long-lived vs short-lived controls, per (complex_id, chain).
    lines: list[str] = []
    lines.append("# Cofolding contrast summary")
    lines.append("")
    lines.append("ESM-C interface divergence (enrichment_ratio) vs Boltz structural")
    lines.append("co-folding (iptm, binding_confidence), per target species.")
    lines.append("")
    lines.append("Higher enrichment_ratio = more interface divergence (ESM).")
    lines.append("Higher iptm = better-formed interface (Boltz).")
    lines.append("")

    for (cid, chain), group in merged.group_by(["complex_id", "chain"], maintain_order=True):
        lines.append(f"## {cid}  /  {chain}")
        lines.append("")
        lines.append("| species | enrichment_ratio | iptm | binding_conf | class |")
        lines.append("|---|---|---|---|---|")
        for r in group.iter_rows(named=True):
            er = r.get("enrichment_ratio")
            iptm = r.get("iptm")
            bc = r.get("binding_confidence")
            cls = r.get("boltz_classification", "")
            er_s = f"{er:.3f}" if er is not None else "-"
            iptm_s = f"{iptm:.3f}" if iptm is not None else "-"
            bc_s = f"{bc:.3f}" if bc is not None else "-"
            lines.append(f"| {r['target_species']} | {er_s} | {iptm_s} | {bc_s} | {cls} |")
        lines.append("")

        # Contrast: best long-lived vs short-lived controls, on both layers.
        rows = {r["target_species"]: r for r in group.iter_rows(named=True)}
        short_present = [s for s in SHORT_LIVED_CONTROLS if s in rows]
        ll_present = [s for s in LONG_LIVED if s in rows]

        if short_present and ll_present:
            ll_esm = [
                rows[s]["enrichment_ratio"]
                for s in ll_present
                if rows[s].get("enrichment_ratio") is not None
            ]
            short_esm = [
                rows[s]["enrichment_ratio"]
                for s in short_present
                if rows[s].get("enrichment_ratio") is not None
            ]
            ll_iptm = [rows[s]["iptm"] for s in ll_present if rows[s].get("iptm") is not None]
            short_iptm = [rows[s]["iptm"] for s in short_present if rows[s].get("iptm") is not None]

            note_parts = []
            d_esm = None
            d_iptm = None
            if ll_esm and short_esm:
                short_esm_mean = sum(short_esm) / len(short_esm)
                d_esm = max(ll_esm) - short_esm_mean
                note_parts.append(
                    f"ESM contrast (max long-lived - mean short-lived controls): {d_esm:+.3f}"
                )
            if ll_iptm and short_iptm:
                short_iptm_mean = sum(short_iptm) / len(short_iptm)
                d_iptm = max(ll_iptm) - short_iptm_mean
                note_parts.append(
                    "Boltz iptm contrast "
                    f"(max long-lived - mean short-lived controls): {d_iptm:+.3f}"
                )
            if note_parts:
                lines.append("**Contrast:** " + "; ".join(note_parts))
                lines.append(
                    "_Groups: long-lived = "
                    + ", ".join(ll_present)
                    + "; short-lived controls = "
                    + ", ".join(short_present)
                    + "_"
                )
                # Plain-language interpretation.
                if d_esm is not None and d_iptm is not None:
                    if d_esm > 0.3 and d_iptm >= 0:
                        verdict = (
                            "Long-lived interface diverges more (ESM) but stays at least as "
                            "well-formed structurally (Boltz) -> consistent with "
                            "rewiring/maintained, not breakage."
                        )
                    elif d_esm > 0.3 and d_iptm < 0:
                        verdict = (
                            "Long-lived interface diverges more (ESM) AND is less "
                            "well-formed structurally (Boltz) -> candidate for "
                            "functional weakening."
                        )
                    else:
                        verdict = "Weak or unresolved contrast."
                    lines.append("")
                    lines.append(f"_Interpretation: {verdict}_")
                lines.append("")

    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {SUMMARY_CSV} ({merged.height} rows)")
    print(f"Wrote {SUMMARY_MD}")
    print()
    print(merged)


if __name__ == "__main__":
    main()
