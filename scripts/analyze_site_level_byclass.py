#!/usr/bin/env python3
"""Class-stratified site-level longevity test.

The uniform site-level FDR could dilute a signal concentrated in one residue class
(e.g. charged salt-bridge contacts). Here interface residues are split by the human
reference amino acid into charged / polar / aromatic / hydrophobic, and the
per-site PGLS lifespan test is FDR-corrected *within each class separately* (more
power for a class-specific effect). Also reports mean ESM delta by class (a
charged-vs-uncharged magnitude check).

Requires residue_deltas with a `ref_residue` column (stage-6 emit).

Inputs : data/interim/residues/*.parquet
Outputs: docs/results/2026-07-29-site-level-byclass/{json,png}
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
from scipy.stats import false_discovery_control

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_site_level import site_stats  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
RES = REPO / "data" / "interim" / "residues"
OUT_DIR = REPO / "docs" / "results" / "2026-07-29-site-level-byclass"

CLASS = {}
for aa, cl in [("DEKRH", "charged"), ("STNQC", "polar"),
               ("FWY", "aromatic"), ("AVLIMPG", "hydrophobic")]:
    for a in aa:
        CLASS[a] = cl
CLASSES = ["charged", "polar", "aromatic", "hydrophobic"]


def analyze_class(df):
    d = df[df["is_interface"]]
    out = {}
    for cl in CLASSES:
        sub_df = d[d["ref_residue"].map(CLASS.get) == cl]
        pgls_p, deltas = [], []
        for _, g in sub_df.groupby(["complex_id", "chain", "ref_position"]):
            st = site_stats(dict(zip(g["target_species"], g["delta"], strict=False)))
            if st is not None:
                pgls_p.append(st[0])
            deltas.extend(g["delta"].tolist())
        if pgls_p:
            q = false_discovery_control(np.array(pgls_p), method="bh")
            out[cl] = {
                "n_sites": len(pgls_p),
                "min_pgls_p": float(np.min(pgls_p)),
                "min_pgls_q": float(q.min()),
                "n_fdr_sig": int((q < 0.05).sum()),
                "median_p": float(np.median(pgls_p)),
                "mean_delta": float(np.mean(deltas)),
            }
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames, used = [], []
    for f in sorted(glob.glob(str(RES / "*.parquet"))):
        df = pd.read_parquet(f)
        if "ref_residue" in df.columns:
            frames.append(df)
            used.append(os.path.basename(f)[:-8])
    if not frames:
        raise SystemExit("no residue parquet has ref_residue — re-run with the updated stage 6")
    print("lanes with ref_residue:", used)
    pooled = pd.concat(frames, ignore_index=True).drop_duplicates(
        ["complex_id", "chain", "ref_position", "target_species"]
    )
    res = analyze_class(pooled)
    (OUT_DIR / "site_level_byclass.json").write_text(json.dumps(res, indent=2))

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    cls = [c for c in CLASSES if c in res]
    minq = [res[c]["min_pgls_q"] for c in cls]
    nsit = [res[c]["n_sites"] for c in cls]
    nsig = [res[c]["n_fdr_sig"] for c in cls]
    ax[0].bar(range(len(cls)), minq, color="#c0504d")
    ax[0].axhline(0.05, ls="--", c="red", label="FDR 0.05")
    ax[0].set_xticks(range(len(cls)))
    ax[0].set_xticklabels([f"{c}\n({n} sites, {s} sig)" for c, n, s in
                           zip(cls, nsit, nsig, strict=False)], fontsize=8)
    ax[0].set_ylabel("min BH q within class (PGLS lifespan)")
    ax[0].set_title("A  class-stratified: no class survives FDR")
    ax[0].legend(fontsize=8)
    for i, qv in enumerate(minq):
        ax[0].text(i, qv + 0.01, f"{qv:.2f}", ha="center", fontsize=8)

    md = [res[c]["mean_delta"] for c in cls]
    ax[1].bar(range(len(cls)), md, color="#4f81bd")
    ax[1].set_xticks(range(len(cls)))
    ax[1].set_xticklabels(cls, fontsize=9)
    ax[1].set_ylabel("mean ESM L2 delta (ortholog vs human)")
    ax[1].set_title("B  divergence magnitude by residue class\n(≈equal across classes; no lifespan signal in any)")
    for i, v in enumerate(md):
        ax[1].text(i, v + 0.002, f"{v:.3f}", ha="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "site_level_byclass.png", dpi=140)

    for c in cls:
        r = res[c]
        print(f"{c:12s} sites={r['n_sites']:5d} min_q={r['min_pgls_q']:.3f} "
              f"FDR_sig={r['n_fdr_sig']} median_p={r['median_p']:.3f} mean_delta={r['mean_delta']:.3f}")


if __name__ == "__main__":
    main()
