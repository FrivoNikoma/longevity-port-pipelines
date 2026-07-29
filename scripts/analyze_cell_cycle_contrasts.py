#!/usr/bin/env python3
"""Stratified longevity contrasts for the cell_cycle panel (BMAL-predicted pathway).

Reads data/output/enrichment.parquet (ESM interface-divergence enrichment_ratio per
interface x species) and computes the three stratified contrasts used across the
project -- BMAL-vs-Reference (the predicted positive), ELLSM-vs-Reference and
BMAL-vs-ELLSM -- with Mann-Whitney U per interface and BH-FDR across interfaces,
plus the shuffled-mask / NEGATOME specificity controls.

Outputs (committed under the dated results dir):
    cell_cycle_contrasts.json
    cell_cycle_contrasts.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import false_discovery_control, mannwhitneyu

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
PARQUET = REPO / "data" / "output" / "enrichment.parquet"
OUT_DIR = REPO / "docs" / "results" / "2026-07-29-cell-cycle-panel"

ELLSM = {"naked_mole_rat", "damaraland_mole_rat", "blind_mole_rat",
         "myotis_lucifugus", "greater_horseshoe_bat"}
BMAL = {"elephant", "blue_whale", "beluga", "sperm_whale", "white_rhino"}
REF = {"mouse", "rat", "hamster", "guinea_pig", "rhesus", "sheep", "opossum",
       "dog", "mouse_lemur", "ground_squirrel", "hedgehog", "cat"}
METRIC = "enrichment_ratio"


def group(s: str) -> str:
    return "ELLSM" if s in ELLSM else "BMAL" if s in BMAL else "REF" if s in REF else "?"


def run_contrast(df: pd.DataFrame, a: str, b: str):
    rows = []
    for iface, g in df.groupby("iface"):
        va = g[g.grp == a][METRIC].to_numpy()
        vb = g[g.grp == b][METRIC].to_numpy()
        if len(va) >= 3 and len(vb) >= 3:
            try:
                p = mannwhitneyu(va, vb, alternative="two-sided").pvalue
            except ValueError:
                continue
            rows.append({"iface": iface, "na": len(va), "nb": len(vb),
                         f"mean_{a}": float(np.mean(va)), f"mean_{b}": float(np.mean(vb)),
                         "p": float(p)})
    r = pd.DataFrame(rows)
    r["q"] = false_discovery_control(r["p"], method="bh")
    r = r.sort_values("p").reset_index(drop=True)
    top = r.iloc[0]
    return {
        "a": a, "b": b, "n_interfaces": int(len(r)),
        "min_p": float(r["p"].min()), "min_q": float(r["q"].min()),
        "n_sig_fdr": int((r["q"] < 0.05).sum()),
        "top_interface": top["iface"],
        f"top_mean_{a}": float(top[f"mean_{a}"]), f"top_mean_{b}": float(top[f"mean_{b}"]),
        "top_direction": a if top[f"mean_{a}"] > top[f"mean_{b}"] else b,
        "table": r,
    }


def main():
    df = pd.read_parquet(PARQUET)
    df["grp"] = df["target_species"].map(group)
    df["iface"] = df["complex_id"] + "|" + df["chain"]

    c_pred = run_contrast(df, "BMAL", "REF")     # predicted positive
    c_ell = run_contrast(df, "ELLSM", "REF")
    c_be = run_contrast(df, "BMAL", "ELLSM")

    controls = {
        "mean_enrichment_ratio": float(df[METRIC].mean()),
        "mean_shuffled_control_ratio": float(df["shuffled_control_ratio"].mean()),
        "mean_negatome_control_ratio": float(df["negatome_control_ratio"].mean()),
        "frac_rows_enrichment_gt_shuffled": float((df[METRIC] > df["shuffled_control_ratio"]).mean()),
    }
    pooled = {g: float(df[df.grp == g][METRIC].mean()) for g in ("ELLSM", "BMAL", "REF")}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "n_interfaces": df.groupby("iface").ngroups,
        "n_species": int(df["target_species"].nunique()),
        "pooled_group_mean_enrichment": pooled,
        "controls": controls,
        "contrasts": {
            "BMAL_vs_REF_predicted_positive": {k: v for k, v in c_pred.items() if k != "table"},
            "ELLSM_vs_REF": {k: v for k, v in c_ell.items() if k != "table"},
            "BMAL_vs_ELLSM": {k: v for k, v in c_be.items() if k != "table"},
        },
    }
    (OUT_DIR / "cell_cycle_contrasts.json").write_text(json.dumps(summary, indent=2))

    # ---- figure
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    # A: pooled group-mean enrichment_ratio
    gs = ["ELLSM", "BMAL", "REF"]
    ax[0].bar(gs, [pooled[g] for g in gs], color=["#c0504d", "#8064a2", "#4f81bd"])
    ax[0].axhline(1.0, ls=":", c="grey")
    ax[0].set_ylabel("mean enrichment_ratio (interface/non-interface)")
    ax[0].set_title("A  pooled interface divergence by group\n(all <1 = interfaces MORE conserved)")
    for i, g in enumerate(gs):
        ax[0].text(i, pooled[g] + 0.005, f"{pooled[g]:.3f}", ha="center", fontsize=9)

    # B: predicted-positive per-interface BMAL vs REF
    t = c_pred["table"]
    ax[1].scatter(t["mean_REF"], t["mean_BMAL"], c=np.where(t["q"] < 0.05, "#c0504d", "#b0b0b0"),
                  s=30)
    lim = [min(t["mean_REF"].min(), t["mean_BMAL"].min()) - 0.05,
           max(t["mean_REF"].max(), t["mean_BMAL"].max()) + 0.05]
    ax[1].plot(lim, lim, ls="--", c="k", lw=0.8)
    ax[1].set_xlim(lim)
    ax[1].set_ylim(lim)
    ax[1].set_xlabel("Reference mean")
    ax[1].set_ylabel("BMAL mean")
    ax[1].set_title(f"B  PREDICTED positive: BMAL vs Reference\n"
                    f"0/{c_pred['n_interfaces']} FDR (min q={c_pred['min_q']:.2f}); "
                    f"points below line = BMAL more conserved")

    # C: min-q per contrast
    labels = ["BMAL-vs-Ref\n(predicted+)", "ELLSM-vs-Ref", "BMAL-vs-ELLSM"]
    minq = [c_pred["min_q"], c_ell["min_q"], c_be["min_q"]]
    ax[2].bar(labels, minq, color=["#8064a2", "#c0504d", "#4bacc6"])
    ax[2].axhline(0.05, ls="--", c="red", label="FDR 0.05")
    ax[2].set_ylabel("minimum BH q across interfaces")
    ax[2].set_title("C  nothing survives FDR in any contrast")
    ax[2].legend(fontsize=8)
    for i, q in enumerate(minq):
        ax[2].text(i, q + 0.01, f"{q:.2f}", ha="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "cell_cycle_contrasts.png", dpi=140)

    # ---- console
    for c in (c_pred, c_ell, c_be):
        print(f"{c['a']}-vs-{c['b']}: n={c['n_interfaces']} min_p={c['min_p']:.4f} "
              f"min_q={c['min_q']:.3f} sig={c['n_sig_fdr']} "
              f"top={c['top_interface']} -> {c['top_direction']}-ward")
    print("pooled:", pooled)
    print("controls:", controls)


if __name__ == "__main__":
    main()
