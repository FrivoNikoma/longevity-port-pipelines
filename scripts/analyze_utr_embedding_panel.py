#!/usr/bin/env python3
"""AI re-test at panel scale: RNA-LM embedding divergence of UTRs vs longevity.

This is the deliberate mirror of the classical extended-panel test
(`scripts/analyze_panel_utr_divergence.py`). **Everything is held identical** - the same
57-species panel, the same AnAge traits, the same TimeTree Brownian covariance, the same
PGLS on log10(lifespan) + log10(mass), the same Benjamini-Hochberg FDR across genes, the
same pooled per-species-mean test, the same sign test. The single swapped component is the
divergence metric: instead of the Jukes-Cantor distance of a pairwise alignment to human,
per-species divergence is the distance to the human UTR **in language-model embedding
space** (`scripts/embed_utr_rna_lm.py`).

Because only the metric changes, the comparison is apples-to-apples: any difference in
outcome is attributable to the metric, not to the panel, the tree or the statistics.

The earlier DNA-LM null (n = 22, Nucleotide Transformer, whole-UTR L2) confounded sample
size, model domain and window. This script reports the full grid in one pass -

    window  in {prox, full}     - proximal 38 % (where the positional map put the signal)
                                  vs the whole UTR (what the old null measured)
    metric  in {cosine, l2}     - direction-only vs magnitude-inclusive distance

- so the old null can be decomposed rather than merely repeated. Run it once per model
(3UTRBERT, RiNALMo, UTR-LM as a domain-mismatch control, and Nucleotide Transformer as the
literal old-null control at the new n) and the three factors separate.

**Circularity control (the decisive part).** A language-model embedding partly encodes
sequence identity itself, so a cosine-to-human distance can simply re-measure the
Jukes-Cantor divergence and inherit the classical signal without adding anything
functional. A bare "the embedding is significant" result would therefore be
uninterpretable. Every cell of the grid is accordingly reported head to head against the
classical JC distance on the identical species set (`head_to_head`):

    r_emb_jc            how much the two metrics are the same measurement to begin with
    p_emb_given_jc      PGLS lifespan p for the embedding, with JC distance as a covariate
    p_jc_given_emb      PGLS lifespan p for JC, with the embedding distance as a covariate

Pre-registered reading of that pair, including the likeliest outcome:

    emb yes / jc no   the embedding carries lifespan information beyond sequence identity
    emb no  / jc yes  the embedding is a lossy proxy for the alignment
    emb no  / jc no   *the expected middle case* - the two are one measurement; the
                      embedding tracks JC and adds nothing. Not a failure, a bound.
    emb yes / jc yes  partly independent components; report both

**Bound that does not go away: species-OOD.** 3UTRBERT is pretrained on *human* 3' UTRs.
The domain match is on the *region type* (3' UTR rather than whole genome), NOT on the
species. Embedding a naked mole-rat or whale UTR with a human-trained model is the same
out-of-distribution problem Enformer had, only milder. Anchoring on cosine-to-human
mitigates it (the reader is fixed; only the sequence varies) but does not remove it, and
no result here should be phrased as if it did.

Inputs:  data/interim/utr_panel_emb/{model_slug}/{GENE}_{region}.npz
         data/interim/utr_panel/{GENE}_{region}.fasta  (+ div_cache, for the JC comparator)
Outputs: docs/results/2026-08-06-utr-embedding-panel/
             utr_embedding_panel_{model_slug}.{json,png}
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy.stats import binomtest

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
EMB_ROOT = REPO / "data" / "interim" / "utr_panel_emb"
OUT_DIR = REPO / "docs" / "results" / "2026-08-06-utr-embedding-panel"

WINDOWS = ("prox", "full")
METRICS = ("cosine", "l2")
PRIMARY = "prox|cosine"  # pre-registered primary cell of the grid


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


PANEL = _load("analyze_panel_utr_divergence")  # traits, TimeTree VCV, PGLS, BH, CELLCYCLE


def model_slug(model: str) -> str:
    return model.replace("/", "__")


def distances(npz: Path, window: str, metric: str, traits: dict) -> dict[str, float]:
    """Per-species embedding distance to the human UTR of the same gene."""
    data = np.load(npz)
    ref_key = f"human|{window}"
    if ref_key not in data.files:
        return {}
    ref = data[ref_key].astype(np.float64)
    ref_norm = float(np.linalg.norm(ref))
    if ref_norm == 0.0:
        return {}
    out: dict[str, float] = {}
    for key in data.files:
        sp, _, win = key.partition("|")
        if win != window or sp == "human" or sp not in traits:
            continue
        vec = data[key].astype(np.float64)
        norm = float(np.linalg.norm(vec))
        if norm == 0.0:
            continue
        if metric == "cosine":
            out[sp] = 1.0 - float(vec @ ref) / (norm * ref_norm)
        else:
            out[sp] = float(np.linalg.norm(vec - ref))
    return out


def _verdict(p_emb_given_jc: float, p_jc_given_emb: float, r: float,
             alpha: float = 0.05, r_high: float = 0.7) -> str:
    """The pre-registered reading of the circularity control.

    ``r`` (the plain embedding-vs-JC correlation) separates two very different ways the
    embedding can fail to add anything: it duplicates the alignment, or it is simply noise.
    """
    emb, jc, tracks = p_emb_given_jc < alpha, p_jc_given_emb < alpha, abs(r) >= r_high
    if emb and not jc:
        return "embedding adds lifespan information beyond sequence identity"
    if emb and jc:
        return "partly independent components; both carry signal"
    if jc and not emb:
        return ("embedding is a lossy proxy for the alignment" if tracks
                else "embedding is uninformative here; JC carries the signal")
    return ("one measurement: the embedding tracks JC and adds nothing beyond it" if tracks
            else "neither metric resolves lifespan after mutual adjustment")


def _z(v: np.ndarray) -> np.ndarray:
    sd = float(v.std())
    return (v - float(v.mean())) / sd if sd > 0 else v - float(v.mean())


def fit_with_covariate(y, life, mass, extra, cov):
    """PGLS of y on lifespan + mass + one extra covariate. Returns (beta, p) for lifespan."""
    x = np.column_stack([np.ones(len(y)), _z(np.log10(life)), _z(np.log10(mass)), _z(extra)])
    b, p = PANEL.gls(y, x, cov)
    return float(b[1]), float(p[1])


def head_to_head(gene: str, div: dict[str, float], region: str, traits: dict,
                 wanted: dict, nwk: str) -> dict | None:
    """Is the embedding distance anything more than the JC distance it partly encodes?"""
    fasta = PANEL.UTR_DIR / f"{gene}_{region}.fasta"
    if not fasta.exists():
        return None
    jc = PANEL.divergence(fasta, region, traits)
    sp = [s for s in div if s in jc and s in wanted]
    if len(sp) < 8:
        return None
    names, cov = PANEL.vcv_from_newick(nwk, {s: wanted[s] for s in sp})
    ye = np.array([div[s] for s in names])
    yj = np.array([jc[s] for s in names])
    if ye.std() == 0 or yj.std() == 0:
        return None
    life = np.array([traits[s][0] for s in names])
    mass = np.array([traits[s][1] for s in names])
    _, p_emb_alone, _, _ = PANEL.fit(ye, life, mass, cov)
    _, p_jc_alone, _, _ = PANEL.fit(yj, life, mass, cov)
    b_e, p_e = fit_with_covariate(ye, life, mass, yj, cov)
    b_j, p_j = fit_with_covariate(yj, life, mass, ye, cov)
    return {"gene": gene, "n": len(names),
            "r_emb_jc": round(float(np.corrcoef(ye, yj)[0, 1]), 3),
            "p_emb_alone": round(p_emb_alone, 4), "p_jc_alone": round(p_jc_alone, 4),
            "p_emb_given_jc": round(p_e, 4), "beta_emb_given_jc": round(b_e, 4),
            "p_jc_given_emb": round(p_j, 4), "beta_jc_given_emb": round(b_j, 4)}


def run_region(emb_dir: Path, region: str, window: str, metric: str,
               traits: dict, wanted: dict, genes: set[str] | None) -> dict:
    """Byte-for-byte the classical run_region, with the embedding metric substituted."""
    nwk = PANEL.NWK.read_text()
    per_gene: list[dict] = []
    h2h: list[dict] = []
    psum: dict[str, list[float]] = {}
    jsum: dict[str, list[float]] = {}

    for fp in sorted(emb_dir.glob(f"*_{region}.npz")):
        gene = fp.name.replace(f"_{region}.npz", "")
        if genes is not None and gene not in genes:
            continue
        div = distances(fp, window, metric, traits)
        sp = [s for s in div if s in wanted]
        if len(sp) >= 8:
            names, cov = PANEL.vcv_from_newick(nwk, {s: wanted[s] for s in sp})
            y = np.array([div[s] for s in names])
            life = np.array([traits[s][0] for s in names])
            mass = np.array([traits[s][1] for s in names])
            b, p, _pm, _ = PANEL.fit(y, life, mass, cov)
            per_gene.append({"gene": gene, "n": len(names), "pgls_p_lifespan": round(p, 4),
                             "pgls_beta_lifespan": round(b, 4),
                             "direction": "conserve" if b < 0 else "diverge"})
        # Pool z-scores, not raw distances. Unlike JC distances, embedding distances have
        # no common scale across genes (different UTR lengths, different local geometry),
        # so a raw mean would let one high-variance gene dominate the pooled test. Per-gene
        # PGLS p-values are invariant to this rescaling, so only pooling is affected.
        if len(sp) >= 8:
            vals = np.array([div[s] for s in sp])
            if float(vals.std()) > 0:
                zs = _z(vals)
                for s, z in zip(sp, zs, strict=True):
                    psum.setdefault(s, []).append(float(z))
            # matching pool of the classical comparator, on the same species
            fasta = PANEL.UTR_DIR / f"{gene}_{region}.fasta"
            jc = PANEL.divergence(fasta, region, traits) if fasta.exists() else {}
            jsp = [s for s in sp if s in jc]
            jvals = np.array([jc[s] for s in jsp])
            if len(jsp) >= 8 and float(jvals.std()) > 0:
                for s, z in zip(jsp, _z(jvals), strict=True):
                    jsum.setdefault(s, []).append(float(z))

            hh = head_to_head(gene, div, region, traits, wanted, nwk)
            if hh:
                h2h.append(hh)

    sp = list(psum)
    pooled: dict = {"status": "insufficient"}
    fig = None
    if len(sp) >= 8:
        names, cov = PANEL.vcv_from_newick(nwk, {s: wanted[s] for s in sp})
        y = np.array([float(np.mean(psum[s])) for s in names])
        life = np.array([traits[s][0] for s in names])
        mass = np.array([traits[s][1] for s in names])
        b, p, pm, xl = PANEL.fit(y, life, mass, cov)
        r = float(np.corrcoef(y, xl)[0, 1])
        pooled = {"n": len(names), "pgls_p_lifespan": round(p, 4),
                  "pgls_beta_lifespan": round(b, 4), "pgls_p_mass": round(pm, 4),
                  "marginal_r": round(r, 3)}
        fig = (life, y, p)

    # pooled circularity control: module-level embedding vs JC, each z-scored per gene
    both = [s for s in psum if s in jsum]
    pooled_h2h: dict = {"status": "insufficient"}
    if len(both) >= 8:
        names, cov = PANEL.vcv_from_newick(nwk, {s: wanted[s] for s in both})
        ye = np.array([float(np.mean(psum[s])) for s in names])
        yj = np.array([float(np.mean(jsum[s])) for s in names])
        life = np.array([traits[s][0] for s in names])
        mass = np.array([traits[s][1] for s in names])
        _, pe0, _, _ = PANEL.fit(ye, life, mass, cov)
        _, pj0, _, _ = PANEL.fit(yj, life, mass, cov)
        be, pe = fit_with_covariate(ye, life, mass, yj, cov)
        bj, pj = fit_with_covariate(yj, life, mass, ye, cov)
        r_ej = float(np.corrcoef(ye, yj)[0, 1])
        pooled_h2h = {"n": len(names), "r_emb_jc": round(r_ej, 3),
                      "p_emb_alone": round(pe0, 4), "p_jc_alone": round(pj0, 4),
                      "p_emb_given_jc": round(pe, 4), "beta_emb_given_jc": round(be, 4),
                      "p_jc_given_emb": round(pj, 4), "beta_jc_given_emb": round(bj, 4),
                      "verdict": _verdict(pe, pj, r_ej)}

    ps = [g["pgls_p_lifespan"] for g in per_gene]
    cons = sum(1 for g in per_gene if g["pgls_beta_lifespan"] < 0)
    sign_p = float(binomtest(cons, len(per_gene), 0.5).pvalue) if per_gene else 1.0
    return {"region": region, "window": window, "metric": metric,
            "n_genes": len(per_gene), "fdr_survivors": PANEL.bh(ps),
            "conserve": cons, "sign_test_p": round(sign_p, 4),
            "per_gene": per_gene, "pooled": pooled,
            "head_to_head": h2h, "pooled_head_to_head": pooled_h2h, "_fig": fig}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="multimolecule/utrbert-3mer")
    ap.add_argument("--gene-set", choices=["all", "cellcycle"], default="cellcycle")
    ap.add_argument("--regions", default="utr3,utr5")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    emb_dir = EMB_ROOT / model_slug(args.model)
    if not emb_dir.exists() or not any(emb_dir.glob("*.npz")):
        print(f"No embeddings in {emb_dir}. Run scripts/embed_utr_rna_lm.py first.")
        return 1
    for need in (PANEL.PANEL, PANEL.ANAGE, PANEL.NWK):
        if not need.exists():
            print(f"Missing {need}")
            return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    genes = set(PANEL.CELLCYCLE) if args.gene_set == "cellcycle" else None
    traits = PANEL.load_traits()
    wanted = {s: sci for s, sci, _ in PANEL.load_panel() if s in traits}
    regions = [r.strip() for r in args.regions.split(",") if r.strip()]

    grid: dict[str, dict] = {}
    for region in regions:
        for window in WINDOWS:
            for metric in METRICS:
                key = f"{region}|{window}|{metric}"
                grid[key] = run_region(emb_dir, region, window, metric, traits, wanted, genes)

    summary = {
        "analysis": "utr_embedding_panel_vs_longevity",
        "model": args.model,
        "gene_set": args.gene_set,
        "primary_cell": f"utr3|{PRIMARY}",
        "n_species_with_traits": len(traits),
        "phylogeny": "TimeTree (Newick), Brownian VCV from branch lengths",
        "note": ("identical panel / tree / PGLS / FDR as analyze_panel_utr_divergence.py; "
                 "only the divergence metric differs (LM embedding distance vs JC)"),
        "grid": {k: {kk: vv for kk, vv in d.items() if not kk.startswith("_")}
                 for k, d in grid.items()},
    }
    slug = model_slug(args.model)
    (out_dir / f"utr_embedding_panel_{slug}.json").write_text(json.dumps(summary, indent=2))

    cells = [k for k in grid if k.endswith(PRIMARY)] or list(grid)
    fig, axes = plt.subplots(1, len(cells), figsize=(6 * len(cells), 5), squeeze=False)
    for ax, key in zip(axes[0], cells, strict=True):
        d = grid[key]
        ax.set_xlabel("log10 max lifespan (yr)")
        ax.set_ylabel(f"pooled z-scored {d['metric']} distance to human ({d['window']})")
        if d["_fig"] is None:
            ax.text(0.5, 0.5, "insufficient", ha="center", transform=ax.transAxes)
            continue
        life, y, p = d["_fig"]
        ax.scatter(np.log10(life), y, s=25, c="#8e44ad")
        ax.set_title(f"{key}  (n={d['pooled'].get('n')})\n"
                     f"PGLS p={p:.3f}  FDR {d['fdr_survivors']}/{d['n_genes']}", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_dir / f"utr_embedding_panel_{slug}.png", dpi=140)

    print(f"model: {args.model}   gene set: {args.gene_set}")
    for key, d in grid.items():
        pl = d["pooled"]
        star = "  <- primary" if key.endswith(PRIMARY) and key.startswith("utr3") else ""
        print(f"== {key:22s} genes={d['n_genes']:2d} FDR={d['fdr_survivors']} "
              f"conserve={d['conserve']}/{d['n_genes']} sign_p={d['sign_test_p']}  "
              f"pooled p={pl.get('pgls_p_lifespan')} beta={pl.get('pgls_beta_lifespan')} "
              f"r={pl.get('marginal_r')} n={pl.get('n')}{star}")
        hh = d["pooled_head_to_head"]
        if "verdict" in hh:
            print(f"   vs JC: r={hh['r_emb_jc']}  alone emb={hh['p_emb_alone']} "
                  f"jc={hh['p_jc_alone']}  |  emb|jc={hh['p_emb_given_jc']} "
                  f"jc|emb={hh['p_jc_given_emb']}  -> {hh['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
