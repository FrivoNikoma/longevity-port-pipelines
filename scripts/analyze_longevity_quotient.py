#!/usr/bin/env python3
"""Longevity-quotient reanalysis: does the signal live on size-adjusted longevity?

The power calibration (docs/results/2026-08-05-power-calibration) showed the lifespan+mass
PGLS pays ~0.06 in detectable |r| to the mass-lifespan collinearity (r=0.70). The
longevity-quotient (LQ) removes that: LQ = the residual of log10(lifespan) on log10(mass),
i.e. how much longer/shorter a species lives than its body size predicts. Used as a single
predictor it restores power *and* asks a cleaner question — does the metric track
**exceptional** (size-corrected) longevity, not just "big and long-lived"?

Reruns the three main per-species responses under LQ and reports them beside the original
lifespan+mass fit:
  * classical 3' and 5' UTR divergence  (recomputed via analyze_utr3_divergence; cached)
  * Enformer-predicted CAGE expression  (via analyze_enformer_expression)

Outputs: docs/results/2026-08-05-power-calibration/longevity_quotient.{json,png}
No network, no Biohub credits.
"""
from __future__ import annotations

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
OUT_DIR = REPO / "docs" / "results" / "2026-08-05-power-calibration"
DIV_CACHE = REPO / "data" / "interim" / "utr" / "div_cache"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


UTR = _load("analyze_utr3_divergence")
ENF = _load("analyze_enformer_expression")
TRAITS = UTR.TRAITS


def lq_predictor() -> dict[str, float]:
    sp = list(TRAITS)
    xl = np.log10([TRAITS[s][0] for s in sp])
    xm = np.log10([TRAITS[s][1] for s in sp])
    b1, b0 = np.polyfit(xm, xl, 1)
    resid = xl - (b0 + b1 * xm)
    z = (resid - resid.mean()) / resid.std()
    return dict(zip(sp, z, strict=True))


LQ = lq_predictor()


def pgls(y: np.ndarray, X: np.ndarray, C: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    Cinv = np.linalg.inv(C)
    XtCi = X.T @ Cinv
    beta = np.linalg.solve(XtCi @ X, XtCi @ y)
    resid = y - X @ beta
    n, k = X.shape
    covb = (float(resid.T @ Cinv @ resid) / (n - k)) * np.linalg.inv(XtCi @ X)
    se = np.sqrt(np.diag(covb))
    return beta, 2 * tdist.sf(np.abs(beta / se), n - k)


def fit_both(resp: dict[str, float]) -> dict:
    """PGLS of a per-species response under (a) lifespan+mass and (b) LQ single predictor."""
    sp = [s for s in resp if s in TRAITS]
    if len(sp) < 6:
        return {"status": "insufficient"}
    y = np.array([resp[s] for s in sp])
    life = np.array([TRAITS[s][0] for s in sp])
    mass = np.array([TRAITS[s][1] for s in sp])
    C = UTR.vcv(sp)
    Xl = (np.log10(life) - np.log10(life).mean()) / np.log10(life).std()
    Xm = (np.log10(mass) - np.log10(mass).mean()) / np.log10(mass).std()
    _, p_lm = pgls(y, np.column_stack([np.ones(len(sp)), Xl, Xm]), C)
    lq = np.array([LQ[s] for s in sp])
    b_lq, p_lq = pgls(y, np.column_stack([np.ones(len(sp)), lq]), C)
    return {
        "n": len(sp),
        "pooled_p_lifespan_plus_mass": round(float(p_lm[1]), 4),
        "pooled_p_lq": round(float(p_lq[1]), 4),
        "lq_beta": round(float(b_lq[1]), 4),
        "_lq": lq, "_y": y,
    }


def bh(pvals: list[float]) -> int:
    m = len(pvals)
    if m == 0:
        return 0
    order = np.argsort(pvals)
    s = 0
    for rank, i in enumerate(order, 1):
        if pvals[i] <= 0.05 * rank / m:
            s = rank
    return s


def utr_response(region: str) -> tuple[dict[str, float], list[dict]]:
    """Per-species pooled divergence + per-gene LQ tests (cached)."""
    DIV_CACHE.mkdir(parents=True, exist_ok=True)
    per_gene: list[dict] = []
    psum: dict[str, list[float]] = {}
    for fp in sorted(UTR.UTR_DIR.glob(f"*_{region}.fasta")):
        gene = fp.name.replace(f"_{region}.fasta", "")
        cache = DIV_CACHE / f"{gene}_{region}.json"
        if cache.exists():
            div = {k: float(v) for k, v in json.loads(cache.read_text()).items()}
        else:
            div = UTR.species_divergence(fp, region)
            cache.write_text(json.dumps(div))
        sp = [s for s in div if s in TRAITS]
        if len(sp) >= 6:
            lq = np.array([LQ[s] for s in sp])
            b, p = pgls(np.array([div[s] for s in sp]),
                        np.column_stack([np.ones(len(sp)), lq]), UTR.vcv(sp))
            per_gene.append({"gene": gene, "lq_p": round(float(p[1]), 4),
                             "lq_beta": round(float(b[1]), 4)})
        for s in sp:
            psum.setdefault(s, []).append(div[s])
    pooled = {s: float(np.mean(v)) for s, v in psum.items()}
    return pooled, per_gene


def enformer_response() -> dict[str, float]:
    cage, _ = ENF.cage_indices()
    genes = sorted({fp.name.split("_", 1)[0] for fp in ENF.EMB_DIR.glob("*.npy")})
    z: dict[str, list[float]] = {}
    for g in genes:
        expr = ENF.expr_per_gene(g, cage)
        sub = [s for s in expr if s in TRAITS]
        for s, zz in ENF.zscore({s: expr[s] for s in sub}).items():
            z.setdefault(s, []).append(zz)
    return {s: float(np.mean(v)) for s, v in z.items()}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}
    fig_lq = None

    for region in ("utr3", "utr5"):
        pooled, per_gene = utr_response(region)
        res = fit_both(pooled)
        res["fdr_survivors_lq"] = bh([g["lq_p"] for g in per_gene])
        res["n_genes"] = len(per_gene)
        res["conserve_dir_lq"] = sum(1 for g in per_gene if g["lq_beta"] < 0)
        if region == "utr3":
            fig_lq = (res.pop("_lq"), res.pop("_y"))
        results[f"classical_{region}_divergence"] = {
            k: v for k, v in res.items() if not k.startswith("_")}

    enf_res = fit_both(enformer_response())
    results["enformer_cage_expression"] = {
        k: v for k, v in enf_res.items() if not k.startswith("_")}

    summary = {
        "analysis": "longevity_quotient_reanalysis",
        "note": "LQ = residual of log10(lifespan) on log10(mass); single-predictor PGLS "
                "vs the original lifespan+mass PGLS",
        "results": results,
    }
    (OUT_DIR / "longevity_quotient.json").write_text(json.dumps(summary, indent=2))

    plt.figure(figsize=(6, 5))
    if fig_lq is not None:
        lq, y = fig_lq
        plt.scatter(lq, y, s=40, c="#8e44ad")
        b = np.polyfit(lq, y, 1)
        xs = np.linspace(lq.min(), lq.max(), 50)
        plt.plot(xs, b[0] * xs + b[1], c="grey", ls="--")
    plt.xlabel("longevity quotient (size-adjusted lifespan, z)")
    plt.ylabel("mean 3' UTR JC divergence")
    p3 = results["classical_utr3_divergence"].get("pooled_p_lq")
    plt.title(f"3' UTR divergence vs longevity quotient\nPGLS p={p3}", fontsize=10)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "longevity_quotient.png", dpi=140)

    for name, r in results.items():
        print(f"{name}: pooled p  lifespan+mass={r.get('pooled_p_lifespan_plus_mass')}  "
              f"LQ={r.get('pooled_p_lq')}  FDR_lq={r.get('fdr_survivors_lq', '-')}/"
              f"{r.get('n_genes', '-')}  conserve_lq={r.get('conserve_dir_lq', '-')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
