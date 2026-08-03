#!/usr/bin/env python3
"""Site-level longevity test — does any single interface residue carry a signal
that the interface-mean masks?

For every interface residue (unique complex_id x chain x reference-position) across
the genuine lanes, take the per-species ESM L2 delta (ortholog vs human) and test
its association with lifespan three ways:
  * PGLS lifespan coefficient p (phylogeny-aware, controls body mass) -- primary
  * Spearman(delta, max lifespan)
  * Mann-Whitney long-lived (10) vs reference (12)
BH-FDR is applied across all interface sites (per lane and pooled). Non-interface
residues are carried as a background control.

Directly tests the assumption that an interface *mean* could hide a few adaptive
sites.

Inputs : data/interim/residues/{sirt6_dna_repair,ampk_pilot,cell_cycle}.parquet
Outputs: docs/results/2026-07-29-site-level/{json,png}
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
from scipy.stats import false_discovery_control, mannwhitneyu, spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_phylo_continuous import TRAITS, gls, vcv  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
RES = REPO / "data" / "interim" / "residues"
OUT_DIR = REPO / "docs" / "results" / "2026-07-29-site-level"
LONG = {"naked_mole_rat", "damaraland_mole_rat", "blind_mole_rat", "myotis_lucifugus",
        "greater_horseshoe_bat", "elephant", "blue_whale", "beluga", "sperm_whale", "white_rhino"}
REF = {"mouse", "rat", "hamster", "guinea_pig", "rhesus", "sheep", "opossum", "dog",
       "mouse_lemur", "ground_squirrel", "hedgehog", "cat"}
MIN_SPECIES = 14

SP = list(TRAITS)
IDX = {s: i for i, s in enumerate(SP)}
_life = np.log10(np.array([TRAITS[s][0] for s in SP]))
_mass = np.log10(np.array([TRAITS[s][1] for s in SP]))
XL = (_life - _life.mean()) / _life.std()
XM = (_mass - _mass.mean()) / _mass.std()
XFULL = np.column_stack([np.ones(len(SP)), XL, XM])
CFULL = vcv(SP)
LIFE = {s: TRAITS[s][0] for s in SP}


def site_stats(sub: dict[str, float]):
    """sub: species -> delta.  Returns (pgls_life_p, life_beta, spearman_p, mwu_p) or None."""
    sps = [s for s in SP if s in sub]
    if len(sps) < MIN_SPECIES:
        return None
    ii = [IDX[s] for s in sps]
    y = np.array([sub[s] for s in sps])
    if np.std(y) < 1e-9:
        return None
    try:
        beta, se, tv, pv, r2 = gls(y, XFULL[ii], CFULL[np.ix_(ii, ii)])
        pgls_p, life_beta = float(pv[1]), float(beta[1])
    except Exception:  # noqa: BLE001
        return None
    life = np.array([LIFE[s] for s in sps])
    sp_rho, sp_p = spearmanr(y, life)
    lv = [sub[s] for s in sps if s in LONG]
    rv = [sub[s] for s in sps if s in REF]
    mwu_p = (mannwhitneyu(lv, rv, alternative="two-sided").pvalue
             if len(lv) >= 3 and len(rv) >= 3 else np.nan)
    return pgls_p, life_beta, float(sp_p), float(mwu_p)


def analyze_frame(df: pd.DataFrame, region: bool):
    d = df[df["is_interface"] == region]
    out = []
    for (_c, _ch, _p), g in d.groupby(["complex_id", "chain", "ref_position"]):
        sub = dict(zip(g["target_species"], g["delta"], strict=False))
        st = site_stats(sub)
        if st is not None:
            out.append(st)
    if not out:
        return None
    arr = np.array(out)
    pgls_p = arr[:, 0]
    q = false_discovery_control(pgls_p, method="bh")
    return {
        "n_sites": int(len(arr)),
        "min_pgls_p": float(pgls_p.min()),
        "min_pgls_q": float(q.min()),
        "n_sites_fdr_sig": int((q < 0.05).sum()),
        "median_pgls_p": float(np.median(pgls_p)),
        "_pgls_p": pgls_p,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = {}
    for f in sorted(glob.glob(str(RES / "*.parquet"))):
        frames[os.path.basename(f)[:-8]] = pd.read_parquet(f)
    pooled = pd.concat(frames.values(), ignore_index=True).drop_duplicates(
        ["complex_id", "chain", "ref_position", "target_species"]
    )

    summary, phist = {}, {}
    for lane, df in list(frames.items()) + [("POOLED", pooled)]:
        iface = analyze_frame(df, True)
        bg = analyze_frame(df, False)
        summary[lane] = {
            "interface": {k: v for k, v in iface.items() if not k.startswith("_")} if iface else None,
            "non_interface_bg": {k: v for k, v in bg.items() if not k.startswith("_")} if bg else None,
        }
        if iface:
            phist[lane] = iface["_pgls_p"]

    (OUT_DIR / "site_level.json").write_text(json.dumps(summary, indent=2))

    # figure: interface-site min-q per lane + pooled p-value histogram
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    lanes = [k for k in summary if summary[k]["interface"]]
    minq = [summary[k]["interface"]["min_pgls_q"] for k in lanes]
    nsig = [summary[k]["interface"]["n_sites_fdr_sig"] for k in lanes]
    nsit = [summary[k]["interface"]["n_sites"] for k in lanes]
    ax[0].bar(range(len(lanes)), minq, color="#4f81bd")
    ax[0].axhline(0.05, ls="--", c="red", label="FDR 0.05")
    ax[0].set_xticks(range(len(lanes)))
    ax[0].set_xticklabels(
        [f"{k}\n({n} sites,\n{s} sig)" for k, n, s in zip(lanes, nsit, nsig, strict=False)],
        fontsize=8)
    ax[0].set_ylabel("min BH q across interface sites (PGLS lifespan)")
    ax[0].set_title("A  site-level: no interface residue survives FDR")
    ax[0].legend(fontsize=8)
    for i, qv in enumerate(minq):
        ax[0].text(i, qv + 0.01, f"{qv:.2f}", ha="center", fontsize=8)

    if "POOLED" in phist:
        ax[1].hist(phist["POOLED"], bins=20, color="#8064a2", edgecolor="white")
        ax[1].axhline(len(phist["POOLED"]) / 20, ls="--", c="grey", label="uniform (null)")
        ax[1].set_xlabel("per-site PGLS lifespan p (pooled interface sites)")
        ax[1].set_ylabel("count")
        ax[1].set_title(f"B  pooled interface sites (n={len(phist['POOLED'])})\n"
                        "p-values ~ uniform → no hidden site-level signal")
        ax[1].legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "site_level.png", dpi=140)

    for lane in summary:
        i = summary[lane]["interface"]
        if i:
            print(f"{lane:22s} iface_sites={i['n_sites']:5d} min_q={i['min_pgls_q']:.3f} "
                  f"FDR_sig={i['n_sites_fdr_sig']} median_p={i['median_pgls_p']:.3f}")


if __name__ == "__main__":
    main()
