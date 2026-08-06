#!/usr/bin/env python3
"""Is the proximal 3' UTR indel deficit specific to the cell-cycle module?

Everything in the regulatory arc has been measured on cell-cycle / tumour-suppressor genes, and
the working claim is framed accordingly — tighter cell-cycle control in long-lived, cancer-
resistant mammals (Peto's paradox). That framing has never been tested. If housekeeping genes
show the same proximal indel deficit, the claim is not about the cell cycle at all but about
3' UTRs of long-lived mammals in general — a different, arguably larger, statement.

Control modules (`data/config/control_modules.tsv`): ribosomal proteins, core glycolysis, and
cytoskeleton / TCA enzymes. They are chosen to be broadly expressed and strongly constrained at
the protein level — comparable to the cell-cycle set in overall constraint — while having no
established link to lifespan.

**The primary statistic is a within-species contrast**, the same device that kept the structure
and embedding layers interpretable:

    delta = proximal indel rate (cell-cycle) - proximal indel rate (control modules)

Both terms are measured in the same species with the same machinery, so every species-level
nuisance — mutation rate, generation time, genome and annotation quality, alignment behaviour —
cancels in the difference. If the constraint is cell-cycle-specific, delta falls with lifespan.
If both modules are constrained alike, delta is flat while each module separately still shows
the effect, and the arc's framing has to widen.

Statistics are the project standard: PGLS on log10(lifespan) + log10(mass) with the TimeTree
Brownian covariance, two-sided, with 95 % confidence intervals on the slopes.

Inputs:  data/config/control_modules.tsv
         data/interim/utr_panel/{GENE}_utr3.fasta for both gene sets
Outputs: docs/results/2026-08-09-module-specificity/module_specificity.{json,png}
No network, no Biohub credits.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy.stats import t as tdist

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
UTR_DIR = REPO / "data" / "interim" / "utr_panel"
CONTROL_CFG = REPO / "data" / "config" / "control_modules.tsv"
OUT_DIR = REPO / "docs" / "results" / "2026-08-09-module-specificity"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


GEO = _load("analyze_utr_constraint_geometry")
PANEL = GEO.PANEL


def load_control_modules() -> dict[str, list[str]]:
    mods: dict[str, list[str]] = {}
    with open(CONTROL_CFG, newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            mods.setdefault(row["module"], []).append(row["gene"])
    return mods


def available(genes: list[str]) -> list[str]:
    return [g for g in genes if (UTR_DIR / f"{g}_utr3.fasta").exists()
            and GEO.gene_tracks(g, "utr3")]


def fit(acc: dict[str, list[float]], traits: dict, wanted: dict, nwk: str) -> dict | None:
    """PGLS with a 95 % confidence interval on the lifespan slope."""
    sp = [s for s in acc if s in wanted]
    if len(sp) < 8:
        return None
    names, cov = PANEL.vcv_from_newick(nwk, {s: wanted[s] for s in sp})
    y = np.array([float(np.mean(acc[s])) for s in names])
    if y.std() == 0:
        return None
    life = np.log10(np.array([traits[s][0] for s in names]))
    mass = np.log10(np.array([traits[s][1] for s in names]))

    def z(v):
        return (v - v.mean()) / v.std()

    x = np.column_stack([np.ones(len(y)), z(life), z(mass)])
    cinv = np.linalg.inv(cov)
    xt = x.T @ cinv
    beta = np.linalg.solve(xt @ x, xt @ y)
    resid = y - x @ beta
    n, k = x.shape
    covb = (float(resid.T @ cinv @ resid) / (n - k)) * np.linalg.inv(xt @ x)
    se = np.sqrt(np.diag(covb))
    tcrit = tdist.ppf(0.975, n - k)
    return {"n": int(n), "beta_lifespan": round(float(beta[1]), 4),
            "ci95": [round(float(beta[1] - tcrit * se[1]), 4),
                     round(float(beta[1] + tcrit * se[1]), 4)],
            "p_lifespan": round(float(2 * tdist.sf(abs(beta[1] / se[1]), n - k)), 4),
            "p_mass": round(float(2 * tdist.sf(abs(beta[2] / se[2]), n - k)), 4),
            "mean": round(float(y.mean()), 4)}


def contrast(a: dict[str, list[float]], b: dict[str, list[float]]) -> dict[str, list[float]]:
    """Per-species difference of two module means (the within-species contrast)."""
    return {s: [float(np.mean(a[s])) - float(np.mean(b[s]))] for s in a if s in b}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--metric", choices=["indel", "substitution", "combined"], default="indel")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    if not CONTROL_CFG.exists():
        print(f"Missing {CONTROL_CFG}")
        return 1
    traits = PANEL.load_traits()
    wanted = {s: sci for s, sci, _ in PANEL.load_panel() if s in traits}
    nwk = PANEL.NWK.read_text()

    cellcycle = available(list(PANEL.CELLCYCLE))
    modules = load_control_modules()
    per_module = {m: available(gs) for m, gs in modules.items()}
    control_all = [g for gs in per_module.values() for g in gs]
    missing = {m: sorted(set(gs) - set(per_module[m])) for m, gs in modules.items()}
    if not control_all:
        print(f"No control-module UTRs in {UTR_DIR}. Fetch them first:\n"
              f"  uv run python scripts/fetch_panel_utr.py --genes "
              f"{','.join(g for gs in modules.values() for g in gs)}")
        return 1

    def scores(genes: list[str]) -> dict[str, list[float]]:
        return GEO.proximal_scores(genes, "utr3", traits, args.metric)

    cc = scores(cellcycle)
    ctrl = scores(control_all)
    results = {
        "cellcycle": fit(cc, traits, wanted, nwk),
        "control_all": fit(ctrl, traits, wanted, nwk),
        **{f"control_{m}": fit(scores(gs), traits, wanted, nwk)
           for m, gs in per_module.items() if gs},
    }
    delta = fit(contrast(cc, ctrl), traits, wanted, nwk)

    verdict = "insufficient data"
    if results["cellcycle"] and results["control_all"] and delta:
        cc_sig = results["cellcycle"]["p_lifespan"] < 0.05
        ct_sig = results["control_all"]["p_lifespan"] < 0.05
        d_sig = delta["p_lifespan"] < 0.05
        if d_sig and cc_sig and not ct_sig:
            verdict = ("module-specific: the cell-cycle set is constrained, the housekeeping "
                       "controls are not, and the within-species contrast is significant")
        elif not d_sig and cc_sig and ct_sig:
            verdict = ("not module-specific: both gene sets show the deficit and the contrast "
                       "is flat - the finding is about 3' UTRs of long-lived mammals generally")
        elif not d_sig and cc_sig and not ct_sig:
            verdict = ("suggestive but not resolved: the control set is not significant on its "
                       "own, yet the contrast does not separate the modules")
        else:
            verdict = "mixed: see the per-module table"

    summary = {
        "analysis": "module_specificity_of_proximal_utr3_indel_deficit",
        "metric": args.metric,
        "primary": "delta = cellcycle - control_all, within-species contrast",
        "n_genes": {"cellcycle": len(cellcycle), "control_all": len(control_all),
                    **{m: len(gs) for m, gs in per_module.items()}},
        "genes": {"cellcycle": cellcycle, **per_module},
        "missing_control_genes": {m: gs for m, gs in missing.items() if gs},
        "results": results,
        "delta_cellcycle_minus_control": delta,
        "verdict": verdict,
    }
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"module_specificity_{args.metric}.json").write_text(
        json.dumps(summary, indent=2))

    keys = [k for k in ["cellcycle", "control_all", *sorted(
        k for k in results if k.startswith("control_") and k != "control_all")]
        if results.get(k)]
    fig, ax = plt.subplots(figsize=(9, 5))
    for idx, key in enumerate(keys):
        r = results[key]
        lo, hi = r["ci95"]
        colour = "#c0392b" if key == "cellcycle" else "#2980b9"
        ax.plot([idx, idx], [lo, hi], color=colour, lw=2.5, zorder=1)
        ax.scatter([idx], [r["beta_lifespan"]], color=colour, s=60, zorder=2)
        ax.annotate(f"p={r['p_lifespan']}", (idx, hi), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=8)
    if delta:
        idx = len(keys)
        lo, hi = delta["ci95"]
        ax.plot([idx, idx], [lo, hi], color="#8e44ad", lw=2.5)
        ax.scatter([idx], [delta["beta_lifespan"]], color="#8e44ad", s=70, marker="D")
        ax.annotate(f"p={delta['p_lifespan']}", (idx, hi), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=8)
        keys = [*keys, "delta\n(cc - control)"]
    ax.axhline(0, color="#333", lw=0.8, ls="--")
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([k.replace("control_", "") for k in keys], fontsize=8, rotation=20,
                       ha="right")
    ax.set_ylabel(f"PGLS lifespan slope, proximal {args.metric} (95% CI)")
    ax.set_title("Is the proximal 3' UTR indel deficit cell-cycle specific?", fontsize=10)
    plt.tight_layout()
    plt.savefig(out_dir / f"module_specificity_{args.metric}.png", dpi=140)

    print(f"metric: {args.metric}")
    for key in keys:
        r = results.get(key.split("\n")[0])
        if r:
            print(f"  {key:22s} n_genes={summary['n_genes'].get(key.replace('control_', ''), '')!s:>3} "
                  f"beta={r['beta_lifespan']:+.4f} CI[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] "
                  f"p={r['p_lifespan']}")
    if delta:
        print(f"  {'DELTA (cc - control)':22s} beta={delta['beta_lifespan']:+.4f} "
              f"CI[{delta['ci95'][0]:+.4f},{delta['ci95'][1]:+.4f}] p={delta['p_lifespan']}")
    if summary["missing_control_genes"]:
        print(f"  missing control genes: {summary['missing_control_genes']}")
    print(f"\n  -> {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
