#!/usr/bin/env python3
"""Neutral control: is the proximal 3' UTR indel deficit specific, or a genome-wide rate effect?

The proximal 3' UTR indel result (docs/results/2026-08-07-utr-constraint-nature) has one
alternative explanation that its internal controls could not rule out: long-lived mammals have
longer generation times and lower per-year mutation rates, so they may accumulate indels more
slowly *everywhere*. The background control used there was built from the distal half of the
same UTRs — the same locus, same annotation, same alignment — which shares technical variation
with the window under test and is not neutral sequence.

This is the external version. Intronic windows from the same genes in the same species
(scripts/fetch_gene_introns.py) go through the identical alignment and indel machinery, and the
question becomes a straight comparison of effect sizes in the same model:

    if the intron indel rate falls with lifespan too  -> genome-wide rate effect, 3' UTR result deflates
    if introns are flat                               -> the deficit is specific to the proximal 3' UTR

Reporting effect sizes with confidence intervals, not just p-values, is the point: a
non-significant intron slope is only informative if its interval also excludes the slope
observed in the 3' UTR. Both are therefore reported, on the identical gene subset.

Every comparison is restricted to genes that have BOTH intron and 3' UTR data, so the contrast
is not confounded by gene composition. Intron windows exist only for genes whose genomic span
exceeds the fetch threshold, so this subset is smaller than, and biased toward longer genes
than, the full cell-cycle module.

Statistics are the project standard: PGLS on log10(lifespan) + log10(mass) with the TimeTree
Brownian covariance, two-sided.

Inputs:  data/interim/utr_panel/{GENE}_{intron,utr3}.fasta  (+ the shared alignment cache)
Outputs: docs/results/2026-08-08-intron-neutral-control/intron_neutral_control.{json,png}
No network, no Biohub credits.
"""

from __future__ import annotations

import argparse
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
OUT_DIR = REPO / "docs" / "results" / "2026-08-08-intron-neutral-control"
MIN_SPECIES_PER_GENE = 40


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


GEO = _load("analyze_utr_constraint_geometry")
PANEL = GEO.PANEL


def whole_window(genes: list[str], region: str, traits: dict,
                 metric: str) -> dict[str, list[float]]:
    """Per-species score over the entire window (used for intronic windows)."""
    acc: dict[str, list[float]] = {}
    for gene in genes:
        tracks = GEO.gene_tracks(gene, region)
        if not tracks:
            continue
        n = len(tracks.get("_human", ""))
        for sp, track in tracks.items():
            if sp == "_human" or sp not in traits:
                continue
            v = GEO.score(track, 0, n, metric)
            if v is not None:
                acc.setdefault(sp, []).append(v)
    return acc


def fit(acc: dict[str, list[float]], traits: dict, wanted: dict, nwk: str,
        extra: dict[str, list[float]] | None = None) -> dict | None:
    """PGLS with a 95% confidence interval on the lifespan slope."""
    sp = [s for s in acc if s in wanted and (extra is None or s in extra)]
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

    cols = [np.ones(len(y)), z(life), z(mass)]
    if extra is not None:
        cols.append(z(np.array([float(np.mean(extra[s])) for s in names])))
    x = np.column_stack(cols)
    cinv = np.linalg.inv(cov)
    xt = x.T @ cinv
    beta = np.linalg.solve(xt @ x, xt @ y)
    resid = y - x @ beta
    n, k = x.shape
    covb = (float(resid.T @ cinv @ resid) / (n - k)) * np.linalg.inv(xt @ x)
    se = np.sqrt(np.diag(covb))
    tcrit = tdist.ppf(0.975, n - k)
    out = {
        "n": int(n), "beta_lifespan": round(float(beta[1]), 4),
        "ci95": [round(float(beta[1] - tcrit * se[1]), 4),
                 round(float(beta[1] + tcrit * se[1]), 4)],
        "p_lifespan": round(float(2 * tdist.sf(abs(beta[1] / se[1]), n - k)), 4),
        "p_mass": round(float(2 * tdist.sf(abs(beta[2] / se[2]), n - k)), 4),
        "mean": round(float(y.mean()), 4),
    }
    if extra is not None:
        out["p_covariate"] = round(float(2 * tdist.sf(abs(beta[3] / se[3]), n - k)), 4)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-species", type=int, default=MIN_SPECIES_PER_GENE)
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    traits = PANEL.load_traits()
    wanted = {s: sci for s, sci, _ in PANEL.load_panel() if s in traits}
    nwk = PANEL.NWK.read_text()

    genes = []
    for fp in sorted(UTR_DIR.glob("*_intron.fasta")):
        gene = fp.name[: -len("_intron.fasta")]
        tracks = GEO.gene_tracks(gene, "intron")
        usable = sum(1 for s in tracks if s != "_human" and s in traits)
        if usable >= args.min_species and GEO.gene_tracks(gene, "utr3"):
            genes.append(gene)
    if not genes:
        print(f"No genes with intron windows in {UTR_DIR}. "
              "Run scripts/fetch_gene_introns.py first.")
        return 1

    intron_indel = whole_window(genes, "intron", traits, "indel")
    intron_sub = whole_window(genes, "intron", traits, "substitution")
    utr_indel = GEO.proximal_scores(genes, "utr3", traits, "indel")
    utr_sub = GEO.proximal_scores(genes, "utr3", traits, "substitution")

    res = {
        "utr3_proximal_indel": fit(utr_indel, traits, wanted, nwk),
        "intron_indel": fit(intron_indel, traits, wanted, nwk),
        "utr3_proximal_substitution": fit(utr_sub, traits, wanted, nwk),
        "intron_substitution": fit(intron_sub, traits, wanted, nwk),
        "utr3_proximal_indel_adjusted_for_intron_indel":
            fit(utr_indel, traits, wanted, nwk, extra=intron_indel),
    }

    shared = [s for s in utr_indel if s in intron_indel]
    a = np.array([float(np.mean(utr_indel[s])) for s in shared])
    b = np.array([float(np.mean(intron_indel[s])) for s in shared])
    u, i = res["utr3_proximal_indel"], res["intron_indel"]
    excluded = bool(u and i and u["beta_lifespan"] < i["ci95"][0])

    summary = {
        "analysis": "intron_neutral_control_for_proximal_utr3_indel_deficit",
        "genes": genes, "n_genes": len(genes),
        "min_species_per_gene": args.min_species,
        "question": ("does the lifespan-linked indel deficit also appear in neutral intronic "
                     "sequence of the same genes (genome-wide rate effect) or not (specific)"),
        "results": res,
        "r_utr3_vs_intron_indel": round(float(np.corrcoef(a, b)[0, 1]), 3),
        "mean_indel_rate": {"utr3_proximal": round(float(a.mean()), 4),
                            "intron": round(float(b.mean()), 4)},
        "intron_ci_excludes_utr3_effect": excluded,
        "verdict": ("the intron interval excludes the observed 3' UTR slope: this is a genuine "
                    "null, not a power failure" if excluded else
                    "the intron interval is compatible with the 3' UTR slope: the control "
                    "cannot separate the two explanations"),
    }
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "intron_neutral_control.json").write_text(json.dumps(summary, indent=2))

    labels = ["3'UTR proximal\nindel", "intron\nindel", "3'UTR proximal\nsubstitution",
              "intron\nsubstitution"]
    keys = ["utr3_proximal_indel", "intron_indel", "utr3_proximal_substitution",
            "intron_substitution"]
    fig, ax = plt.subplots(figsize=(8, 5))
    for idx, key in enumerate(keys):
        r = res[key]
        if not r:
            continue
        lo, hi = r["ci95"]
        colour = "#c0392b" if "intron" not in key else "#2980b9"
        ax.plot([idx, idx], [lo, hi], color=colour, lw=2.5, zorder=1)
        ax.scatter([idx], [r["beta_lifespan"]], color=colour, s=60, zorder=2)
        ax.annotate(f"p={r['p_lifespan']}", (idx, hi), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=8)
    ax.axhline(0, color="#333", lw=0.8, ls="--")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("PGLS lifespan slope (95% CI)")
    ax.set_title(f"Neutral control on {len(genes)} genes with both regions\n"
                 "red = 3' UTR, blue = intron", fontsize=10)
    plt.tight_layout()
    plt.savefig(out_dir / "intron_neutral_control.png", dpi=140)

    print(f"genes with both regions ({len(genes)}): {', '.join(genes)}")
    for key in keys + ["utr3_proximal_indel_adjusted_for_intron_indel"]:
        r = res[key]
        if r:
            cov_s = f"  covar p={r['p_covariate']}" if "p_covariate" in r else ""
            print(f"  {key:48s} beta={r['beta_lifespan']:+.4f} "
                  f"CI[{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] p={r['p_lifespan']}{cov_s}")
    print(f"\n  r(3'UTR proximal indel, intron indel) = {summary['r_utr3_vs_intron_indel']}")
    print(f"  intron CI excludes the 3' UTR effect: {excluded}")
    print(f"  -> {summary['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
