#!/usr/bin/env python3
"""What kind of constraint is the proximal 3' UTR signal? Indels, not substitutions.

The positional map (docs/results/2026-08-05-utr-positional) cut each 3' UTR into eight
*relative* bins and localised the lifespan-linked conservation to the first ~38 %. Its
per-position score counted an alignment gap as a divergence, exactly like a substitution.
This layer separates the two, and re-cuts the same alignments in absolute nucleotides.

Three per-position metrics on identical alignments:

    combined       gap or mismatch scores 1  -- the published convention, reproduced here
    substitution   gapped positions dropped; only base changes counted
    indel          fraction of human positions that are gapped in the species

Two coordinate systems:

    relative       eight equal fractions of the UTR (the published framing)
    absolute       nucleotides from the stop codon; relative bins mix wildly different
                   physical scales (CDC20's 3' UTR is 74 nt, RB1's is 1853 nt, so "the first
                   38 %" is 28 nt in one and 704 nt in the other)

The primary block tests the proximal indel rate directly, with the confound that matters:
gaps are mechanically produced by UTR length differences, and human -- the alignment anchor --
is itself long-lived, so "long-lived species look more human" could manufacture the effect.
The per-species mismatch between species and human UTR length is therefore entered as a
covariate, and the result is jackknifed by gene and by clade.

Statistics are the project standard: PGLS on log10(lifespan) + log10(mass) with the TimeTree
Brownian covariance, two-sided.

Inputs:  data/interim/utr_panel/{GENE}_{region}.fasta (+ human reference)
Outputs: docs/results/2026-08-07-utr-constraint-nature/utr_constraint_geometry.{json,png}
Cache:   data/interim/utr_panel/aln_cache/{GENE}_{region}.json
             per species, one character per human position: 0 conserved, 1 substituted, - gapped
No network, no Biohub credits.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import biotite.sequence as bseq
import biotite.sequence.align as balign
import matplotlib
import numpy as np
from scipy.stats import t as tdist

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
UTR_DIR = REPO / "data" / "interim" / "utr_panel"
ALN_CACHE = UTR_DIR / "aln_cache"
OUT_DIR = REPO / "docs" / "results" / "2026-08-07-utr-constraint-nature"

MAX_ALN = 3000  # same cap as the classical divergence test
MIN_BIN = 10
ABS_BINS = [(0, 50), (50, 100), (100, 200), (200, 400), (400, 800), (800, MAX_ALN)]
N_REL_BINS = 8
PROXIMAL_FRAC = 0.38  # the window the published positional map singled out
METRICS = ("combined", "substitution", "indel")
_MATRIX = balign.SubstitutionMatrix.std_nucleotide_matrix()
_NUC = set("ACGT")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


PANEL = _load("analyze_panel_utr_divergence")


def clean(seq: str) -> str:
    return "".join(c for c in seq.upper().replace("U", "T") if c in _NUC)


def proximal(seq: str, region: str) -> str:
    if len(seq) <= MAX_ALN:
        return seq
    return seq[:MAX_ALN] if region == "utr3" else seq[-MAX_ALN:]


def align_track(ref: str, query: str) -> str | None:
    """One character per human position: '0' conserved, '1' substituted, '-' gapped."""
    a, b = clean(ref), clean(query)
    if len(a) < 20 or len(b) < 20:
        return None
    aln = balign.align_optimal(
        bseq.NucleotideSequence(a), bseq.NucleotideSequence(b),
        _MATRIX, gap_penalty=(-10, -1), terminal_penalty=False,
    )[0]
    out = ["-"] * len(a)
    for hi, si in aln.trace:
        if hi >= 0:
            out[hi] = "-" if si < 0 else ("0" if b[si] == a[hi] else "1")
    return "".join(out)


def gene_tracks(gene: str, region: str, force: bool = False) -> dict[str, str]:
    """Per-species divergence tracks on human coordinates; cached (alignment is the slow part)."""
    fp = ALN_CACHE / f"{gene}_{region}.json"
    if fp.exists() and not force:
        return json.loads(fp.read_text())
    fasta = UTR_DIR / f"{gene}_{region}.fasta"
    href = PANEL.human_ref(gene, region)
    if not fasta.exists() or not href:
        return {}
    ref = clean(proximal(href, region))
    tracks: dict[str, str] = {"_human": ref}
    for sp, raw in PANEL.UTR.load_fasta(fasta).items():
        if sp == "human":
            continue
        t = align_track(ref, proximal(raw, region))
        if t:
            tracks[sp] = t
    ALN_CACHE.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(tracks))
    return tracks


def score(track: str, lo: int, hi: int, metric: str) -> float | None:
    """Per-position score of one window under one metric (None if too little data)."""
    seg = track[lo:hi]
    if metric == "substitution":
        usable = [c for c in seg if c != "-"]
        if len(usable) < MIN_BIN:
            return None
        return sum(1 for c in usable if c == "1") / len(usable)
    if len(seg) < MIN_BIN:
        return None
    if metric == "indel":
        return sum(1 for c in seg if c == "-") / len(seg)
    return sum(1 for c in seg if c != "0") / len(seg)  # combined (published convention)


def collect(genes: list[str], region: str, traits: dict, mode: str,
            metric: str) -> dict[str, dict[str, list[float]]]:
    """bin label -> species -> per-gene scores."""
    acc: dict[str, dict[str, list[float]]] = {}
    for gene in genes:
        tracks = gene_tracks(gene, region)
        if not tracks:
            continue
        n = len(tracks.get("_human", ""))
        if mode == "absolute":
            spans = [(f"{lo}-{hi}", lo, min(hi, n)) for lo, hi in ABS_BINS if lo < n]
        else:
            edges = np.linspace(0, n, N_REL_BINS + 1).astype(int)
            spans = [(f"{i / N_REL_BINS:.2f}-{(i + 1) / N_REL_BINS:.2f}",
                      int(edges[i]), int(edges[i + 1])) for i in range(N_REL_BINS)]
        for label, lo, hi in spans:
            if hi - lo < MIN_BIN:
                continue
            for sp, track in tracks.items():
                if sp == "_human" or sp not in traits:
                    continue
                v = score(track, lo, hi, metric)
                if v is not None:
                    acc.setdefault(label, {}).setdefault(sp, []).append(v)
    return acc


def proximal_scores(genes: list[str], region: str, traits: dict,
                    metric: str) -> dict[str, list[float]]:
    """Per-species scores over the proximal fraction, gene by gene."""
    acc: dict[str, list[float]] = {}
    for gene in genes:
        tracks = gene_tracks(gene, region)
        if not tracks:
            continue
        n = len(tracks.get("_human", ""))
        hi = int(round(n * PROXIMAL_FRAC))
        if hi < MIN_BIN:
            continue
        for sp, track in tracks.items():
            if sp == "_human" or sp not in traits:
                continue
            v = score(track, 0, hi, metric)
            if v is not None:
                acc.setdefault(sp, []).append(v)
    return acc


def background_indel(genes: list[str], region: str, traits: dict,
                     from_frac: float = 0.5) -> dict[str, list[float]]:
    """Per-species indel rate over the DISTAL half of the same UTRs.

    This is the species' own indel propensity measured off the window of interest, and it is
    the control for the alternative that long-lived mammals simply accumulate indels more
    slowly everywhere (longer generation times, lower per-year mutation rate). If the proximal
    deficit is a species-level rate effect, it disappears once this is held constant.
    """
    acc: dict[str, list[float]] = {}
    for gene in genes:
        tracks = gene_tracks(gene, region)
        if not tracks:
            continue
        n = len(tracks.get("_human", ""))
        lo = int(round(n * from_frac))
        if n - lo < MIN_BIN:
            continue
        for sp, track in tracks.items():
            if sp == "_human" or sp not in traits:
                continue
            v = score(track, lo, n, "indel")
            if v is not None:
                acc.setdefault(sp, []).append(v)
    return acc


def length_mismatch(genes: list[str], region: str, traits: dict) -> dict[str, list[float]]:
    """Per-species |log10 UTR length - log10 human UTR length|, gene by gene."""
    acc: dict[str, list[float]] = {}
    for gene in genes:
        href = PANEL.human_ref(gene, region)
        fasta = UTR_DIR / f"{gene}_{region}.fasta"
        if not href or not fasta.exists():
            continue
        hlen = max(len(href), 1)
        for sp, raw in PANEL.UTR.load_fasta(fasta).items():
            if sp == "human" or sp not in traits:
                continue
            acc.setdefault(sp, []).append(
                abs(np.log10(max(len(raw), 1)) - np.log10(hlen)))
    return acc


def _z(v: np.ndarray) -> np.ndarray:
    sd = float(v.std())
    return (v - float(v.mean())) / sd if sd > 0 else v - float(v.mean())


def gls_fit(y, cols, cov):
    """PGLS of y on an intercept plus the given standardised columns."""
    x = np.column_stack([np.ones(len(y))] + [_z(c) for c in cols])
    cinv = np.linalg.inv(cov)
    xt = x.T @ cinv
    beta = np.linalg.solve(xt @ x, xt @ y)
    resid = y - x @ beta
    n, k = x.shape
    covb = (float(resid.T @ cinv @ resid) / (n - k)) * np.linalg.inv(xt @ x)
    se = np.sqrt(np.diag(covb))
    return beta, 2 * tdist.sf(np.abs(beta / se), n - k)


def fit_species(acc: dict[str, list[float]], traits: dict, wanted: dict, nwk: str,
                extra: dict[str, list[float]] | None = None) -> dict | None:
    sp = [s for s in acc if s in wanted and (extra is None or s in extra)]
    if len(sp) < 8:
        return None
    names, cov = PANEL.vcv_from_newick(nwk, {s: wanted[s] for s in sp})
    y = np.array([float(np.mean(acc[s])) for s in names])
    if y.std() == 0:
        return None
    life = np.log10(np.array([traits[s][0] for s in names]))
    mass = np.log10(np.array([traits[s][1] for s in names]))
    cols = [life, mass]
    if extra is not None:
        cols.append(np.array([float(np.mean(extra[s])) for s in names]))
    beta, p = gls_fit(y, cols, cov)
    out = {"n": len(names), "beta_lifespan": round(float(beta[1]), 4),
           "p_lifespan": round(float(p[1]), 4), "p_mass": round(float(p[2]), 4),
           "mean": round(float(y.mean()), 4)}
    if extra is not None:
        out["beta_covariate"] = round(float(beta[3]), 4)
        out["p_covariate"] = round(float(p[3]), 6)
    return out


def pgls_bins(acc: dict, traits: dict, wanted: dict, nwk: str) -> list[dict]:
    rows = []
    for label, per_sp in acc.items():
        r = fit_species(per_sp, traits, wanted, nwk)
        if r:
            rows.append({"bin": label, **r,
                         "n_gene_obs": int(sum(len(v) for v in per_sp.values())),
                         "direction": "conserve" if r["beta_lifespan"] < 0 else "diverge"})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gene-set", choices=["all", "cellcycle"], default="cellcycle")
    ap.add_argument("--region", default="utr3")
    ap.add_argument("--genes", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--cache-only", action="store_true")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    traits = PANEL.load_traits()
    panel_rows = PANEL.load_panel()
    wanted = {s: sci for s, sci, _ in panel_rows if s in traits}
    clade = {s: cl for s, _sci, cl in panel_rows}
    nwk = PANEL.NWK.read_text()
    suffix = f"_{args.region}.fasta"
    all_genes = sorted({f.name[: -len(suffix)]
                        for f in UTR_DIR.glob(f"*{suffix}")})
    genes = [g for g in all_genes if args.gene_set == "all" or g in set(PANEL.CELLCYCLE)]
    if args.genes:
        pick = {g.strip() for g in args.genes.split(",") if g.strip()}
        genes = [g for g in genes if g in pick]

    if args.cache_only:
        for gene in genes:
            t = gene_tracks(gene, args.region, args.force)
            print(f"  {gene:10s} {len(t) - 1 if t else 0} species cached", flush=True)
        return 0

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    genes = [g for g in genes if gene_tracks(g, args.region)]

    bins = {f"{mode}|{metric}": pgls_bins(collect(genes, args.region, traits, mode, metric),
                                          traits, wanted, nwk)
            for mode in ("relative", "absolute") for metric in METRICS}

    # ---- primary: proximal indel rate, with the length-mismatch confound and jackknives
    prox = {m: proximal_scores(genes, args.region, traits, m) for m in METRICS}
    lm = length_mismatch(genes, args.region, traits)
    bg = background_indel(genes, args.region, traits)
    primary = {m: fit_species(prox[m], traits, wanted, nwk) for m in METRICS}
    adjusted = fit_species(prox["indel"], traits, wanted, nwk, extra=lm)
    background_alone = fit_species(bg, traits, wanted, nwk)
    adjusted_bg = fit_species(prox["indel"], traits, wanted, nwk, extra=bg)

    jack_gene = []
    for drop in genes:
        keep = [g for g in genes if g != drop]
        r = fit_species(proximal_scores(keep, args.region, traits, "indel"),
                        traits, wanted, nwk)
        if r:
            jack_gene.append({"dropped": drop, "p_lifespan": r["p_lifespan"],
                              "beta_lifespan": r["beta_lifespan"]})
    jack_clade = []
    for cl in sorted({clade[s] for s in prox["indel"] if s in clade}):
        keep_sp = {s: v for s, v in prox["indel"].items() if clade.get(s) != cl}
        r = fit_species(keep_sp, traits, wanted, nwk)
        if r:
            jack_clade.append({"dropped_clade": cl, "n": r["n"],
                               "p_lifespan": r["p_lifespan"],
                               "beta_lifespan": r["beta_lifespan"]})

    summary = {
        "analysis": "utr_constraint_geometry_indel_vs_substitution",
        "gene_set": args.gene_set, "region": args.region, "n_genes": len(genes),
        "proximal_frac": PROXIMAL_FRAC,
        "question": ("does the published proximal localisation come from substitutions or "
                     "from indels, and is it a fixed footprint or a proportional region"),
        "bins": bins,
        "primary_proximal": primary,
        "primary_indel_adjusted_for_utr_length_mismatch": adjusted,
        "background_indel_distal_half_alone": background_alone,
        "primary_indel_adjusted_for_background_indel": adjusted_bg,
        "jackknife_leave_one_gene_out": jack_gene,
        "jackknife_leave_one_clade_out": jack_clade,
    }
    (out_dir / "utr_constraint_geometry.json").write_text(json.dumps(summary, indent=2))

    fig, axes = plt.subplots(2, 3, figsize=(16, 8), sharey="row")
    for row, mode in enumerate(("relative", "absolute")):
        for col, metric in enumerate(METRICS):
            ax = axes[row][col]
            rows = bins[f"{mode}|{metric}"]
            if rows:
                ps = [-np.log10(max(r["p_lifespan"], 1e-12)) for r in rows]
                cols_ = ["#c0392b" if r["direction"] == "conserve" else "#7f8c8d"
                         for r in rows]
                ax.bar(range(len(rows)), ps, color=cols_)
                ax.set_xticks(range(len(rows)))
                ax.set_xticklabels([r["bin"] for r in rows], rotation=45, ha="right",
                                   fontsize=7)
            ax.axhline(-np.log10(0.05), color="#333", ls="--", lw=0.8)
            ax.set_title(f"{mode} bins - {metric}", fontsize=10)
            if col == 0:
                ax.set_ylabel("-log10 PGLS lifespan p")
    plt.tight_layout()
    plt.savefig(out_dir / "utr_constraint_geometry.png", dpi=140)

    for key, rows in bins.items():
        print(f"=== {key} ===")
        for r in rows:
            print(f"  {r['bin']:>12s}  p={r['p_lifespan']:<9} beta={r['beta_lifespan']:<+9} "
                  f"{r['direction']} n={r['n']}")
    print("=== proximal window, per metric ===")
    for m, r in primary.items():
        if r:
            print(f"  {m:13s} p={r['p_lifespan']:<9} beta={r['beta_lifespan']:<+9} "
                  f"mean={r['mean']} n={r['n']}")
    if adjusted:
        print(f"  indel + UTR-length-mismatch covariate: p={adjusted['p_lifespan']} "
              f"beta={adjusted['beta_lifespan']} (covariate p={adjusted['p_covariate']})")
    if background_alone:
        print(f"  background (distal half) indel alone:   p={background_alone['p_lifespan']} "
              f"beta={background_alone['beta_lifespan']}")
    if adjusted_bg:
        print(f"  indel + background-indel covariate:     p={adjusted_bg['p_lifespan']} "
              f"beta={adjusted_bg['beta_lifespan']} (covariate p={adjusted_bg['p_covariate']})")
    if jack_gene:
        worst = max(jack_gene, key=lambda r: r["p_lifespan"])
        print(f"=== jackknife: worst leave-one-gene-out p={worst['p_lifespan']} "
              f"(dropping {worst['dropped']})")
    if jack_clade:
        worst = max(jack_clade, key=lambda r: r["p_lifespan"])
        print(f"=== jackknife: worst leave-one-clade-out p={worst['p_lifespan']} "
              f"(dropping {worst['dropped_clade']}, n={worst['n']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
