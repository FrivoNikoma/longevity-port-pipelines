#!/usr/bin/env python3
"""Phylogeny-aware continuous PGLS across all regenerated lanes.

Extends scripts/analyze_phylo_continuous.py from a single panel to every lane whose
enrichment could be regenerated Biohub-free from cache (data/interim/lanes/*.parquet).
Per-species mean ESM interface divergence is regressed on log lifespan + log mass,
OLS vs PGLS, for each genuine lane, for the pooled union of all unique interfaces
(max power), and against the Ku80 dN/dS response.

Note: only sirt6 and ampk reproduced their own lane biology from cache; the
tp53/igf/has2 selections collapsed to off-target cached interfaces under partner-aware
selection, so they are reported only inside the pooled union, not as lane claims.

Outputs: docs/results/2026-07-29-phylo-all-lanes/{json,png}
"""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_phylo_continuous import TRAITS, fit, ku80_omega_vs_human, vcv  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
LANES = REPO / "data" / "interim" / "lanes"
OUT_DIR = REPO / "docs" / "results" / "2026-07-29-phylo-all-lanes"
GENUINE = {"sirt6_dna_repair", "ampk_pilot"}  # cache reproduced their own biology


def species_means(df):
    d = df.drop_duplicates(["complex_id", "chain", "target_species"])
    return d.groupby("target_species")["enrichment_ratio"].mean()


def run_set(series, label):
    species = [s for s in TRAITS if s in series.index]
    life = np.array([TRAITS[s][0] for s in species])
    mass = np.array([TRAITS[s][1] for s in species])
    y = np.array([series[s] for s in species])
    res = fit(y, life, mass, vcv(species), label)
    return {k: v for k, v in res.items() if not k.startswith("_")}, res


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = {}
    for f in sorted(glob.glob(str(LANES / "*.parquet"))):
        lane = os.path.basename(f)[:-8]
        frames[lane] = pd.read_parquet(f)

    results = {}
    keep_scatter = None
    for lane, df in frames.items():
        summ, full = run_set(species_means(df), lane)
        summ["genuine_lane"] = lane in GENUINE
        summ["n_interfaces"] = int(df.groupby(["complex_id", "chain"]).ngroups)
        results[lane] = summ

    pooled_df = pd.concat(frames.values(), ignore_index=True)
    summ, full_p = run_set(species_means(pooled_df), "POOLED (all unique interfaces)")
    summ["n_interfaces"] = int(
        pooled_df.drop_duplicates(["complex_id", "chain"]).groupby(["complex_id", "chain"]).ngroups
    )
    results["POOLED"] = summ
    keep_scatter = full_p

    # Ku80 dN/dS response
    omega = ku80_omega_vs_human()
    sp_b = [s for s in TRAITS if s in omega and not np.isnan(omega[s])]
    yB = np.array([omega[s] for s in sp_b])
    lifeb = np.array([TRAITS[s][0] for s in sp_b])
    massb = np.array([TRAITS[s][1] for s in sp_b])
    resB = fit(yB, lifeb, massb, vcv(sp_b), "Ku80 dN/dS vs human")
    results["Ku80_dNdS"] = {k: v for k, v in resB.items() if not k.startswith("_")}

    (OUT_DIR / "phylo_all_lanes.json").write_text(json.dumps(results, indent=2))

    # ---- figure: PGLS lifespan p per set + pooled scatter
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    order = ["sirt6_dna_repair", "ampk_pilot", "tp53_mdm2_elephant", "igf_rheb_mtor",
             "has2_cd44_nmr", "POOLED", "Ku80_dNdS"]
    order = [o for o in order if o in results]
    ps = [results[o]["PGLS"]["p_lifespan"] for o in order]
    genuine = [results[o].get("genuine_lane", o in ("POOLED", "Ku80_dNdS")) for o in order]
    colors = ["#4f81bd" if g else "#b0b0b0" for g in genuine]
    labels = [o.replace("_", "\n") for o in order]
    ax[0].bar(range(len(order)), ps, color=colors)
    ax[0].axhline(0.05, ls="--", c="red", label="p=0.05")
    ax[0].set_xticks(range(len(order)))
    ax[0].set_xticklabels(labels, fontsize=8)
    ax[0].set_ylabel("PGLS lifespan p (controlling mass + phylogeny)")
    ax[0].set_title("A  no lifespan signal in any set\n(blue = genuine lane / pooled / dN/dS; "
                    "grey = off-target cached)")
    ax[0].legend(fontsize=8)
    for i, p in enumerate(ps):
        ax[0].text(i, p + 0.01, f"{p:.2f}", ha="center", fontsize=8)

    Xl, y = keep_scatter["_Xl"], keep_scatter["_y"]
    life_p = np.array([TRAITS[s][0] for s in TRAITS
                       if s in species_means(pooled_df).index])
    ax[1].scatter(np.log10(life_p), y, s=40, c="#4f81bd")
    b = np.polyfit(Xl, y, 1)
    xs = np.linspace(Xl.min(), Xl.max(), 50)
    ax[1].plot(np.log10(life_p).min() + (xs - Xl.min()) *
               (np.log10(life_p).max() - np.log10(life_p).min()) / (Xl.max() - Xl.min()),
               b[0] * xs + b[1], c="grey", ls="--")
    ax[1].set_xlabel("log10 max lifespan (yr)")
    ax[1].set_ylabel("pooled mean enrichment_ratio")
    pl = results["POOLED"]
    ax[1].set_title(f"B  pooled: 52 interfaces, 22 species\n"
                    f"OLS lifespan p={pl['OLS']['p_lifespan']:.3f} | "
                    f"PGLS p={pl['PGLS']['p_lifespan']:.3f}", fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "phylo_all_lanes.png", dpi=140)

    # console
    for k in order:
        r = results[k]
        print(f"{k:22s} n_if={r.get('n_interfaces','-'):>3} "
              f"OLS_life_p={r['OLS']['p_lifespan']:.3f} PGLS_life_p={r['PGLS']['p_lifespan']:.3f} "
              f"PGLS_mass_p={r['PGLS']['p_mass']:.3f}  raw_r_life={r['raw_pearson_r_vs_logLifespan']}")


if __name__ == "__main__":
    main()
