#!/usr/bin/env python3
"""AI regulatory-divergence test: DNA-LM embedding divergence vs longevity.

The direct AI mirror of the ESM interface method, one biological level up. For each gene
and UTR region, per-species divergence = L2 distance between the species' UTR embedding
and the human UTR embedding (Nucleotide Transformer; scripts/embed_utr_dna_lm.py). Those
divergences are regressed on log10(max lifespan) + log10(body mass), OLS and PGLS
(Brownian phylogenetic GLS), two-sided, with Benjamini-Hochberg FDR across genes -- the
identical statistical machine used for the interface screen and the classical UTR test.

Inputs:  data/interim/utr_emb/{GENE}_{region}.npz   (arrays keyed by species name)
Outputs: docs/results/2026-08-04-utr3-regulatory-divergence/{utr_embedding_divergence.json,png}
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy.stats import pearsonr
from scipy.stats import t as tdist

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
EMB_DIR = REPO / "data" / "interim" / "utr_emb"
OUT_DIR = REPO / "docs" / "results" / "2026-08-04-utr3-regulatory-divergence"

TRAITS = {
    "naked_mole_rat": (31.0, 0.035), "damaraland_mole_rat": (20.0, 0.11),
    "blind_mole_rat": (21.0, 0.15), "myotis_lucifugus": (34.0, 0.0075),
    "greater_horseshoe_bat": (30.0, 0.022),
    "elephant": (65.0, 4000.0), "blue_whale": (110.0, 100000.0),
    "beluga": (80.0, 1500.0), "sperm_whale": (77.0, 40000.0), "white_rhino": (50.0, 2300.0),
    "mouse": (4.0, 0.020), "rat": (3.8, 0.30), "hamster": (3.9, 0.12),
    "guinea_pig": (12.0, 0.70), "rhesus": (40.0, 7.0), "sheep": (22.8, 60.0),
    "opossum": (5.9, 0.10), "dog": (24.0, 25.0), "mouse_lemur": (18.2, 0.06),
    "ground_squirrel": (7.9, 0.15), "hedgehog": (11.7, 0.80), "cat": (30.0, 4.0),
}

AGE = {
    "TH": 160, "PLAC": 100, "BOREO": 95, "EUARCH": 90, "PRIM": 70,
    "RODENTIA": 72, "NONSCIUR": 71, "HYSTRICOMORPHA": 45, "BATHYERGIDAE": 26,
    "MYOMORPHA": 45, "MUROIDEA": 25, "MURINAE": 13,
    "LAURAS": 80, "SCROTIFERA": 78, "CHIROPTERA": 55, "FEREUUNG": 76,
    "ZOOAMATA": 75, "CARNIVORA": 54, "CETARTIO": 60, "CETACEA": 35, "ODONTOCETI": 33,
}
ROOT_AGE = AGE["TH"]
_E = ["TH", "PLAC", "BOREO", "EUARCH"]
_R = _E + ["RODENTIA"]
_RN = _R + ["NONSCIUR"]
_L = ["TH", "PLAC", "BOREO", "LAURAS"]
_LS = _L + ["SCROTIFERA"]
_LF = _LS + ["FEREUUNG"]
PATH = {
    "opossum": ["TH"],
    "elephant": ["TH", "PLAC"],
    "rhesus": _E + ["PRIM"], "mouse_lemur": _E + ["PRIM"],
    "ground_squirrel": _R,
    "guinea_pig": _RN + ["HYSTRICOMORPHA"],
    "naked_mole_rat": _RN + ["HYSTRICOMORPHA", "BATHYERGIDAE"],
    "damaraland_mole_rat": _RN + ["HYSTRICOMORPHA", "BATHYERGIDAE"],
    "blind_mole_rat": _RN + ["MYOMORPHA"],
    "hamster": _RN + ["MYOMORPHA", "MUROIDEA"],
    "mouse": _RN + ["MYOMORPHA", "MUROIDEA", "MURINAE"],
    "rat": _RN + ["MYOMORPHA", "MUROIDEA", "MURINAE"],
    "hedgehog": _L,
    "myotis_lucifugus": _LS + ["CHIROPTERA"], "greater_horseshoe_bat": _LS + ["CHIROPTERA"],
    "white_rhino": _LF + ["ZOOAMATA"],
    "dog": _LF + ["ZOOAMATA", "CARNIVORA"], "cat": _LF + ["ZOOAMATA", "CARNIVORA"],
    "sheep": _LF + ["CETARTIO"],
    "blue_whale": _LF + ["CETARTIO", "CETACEA"],
    "beluga": _LF + ["CETARTIO", "CETACEA", "ODONTOCETI"],
    "sperm_whale": _LF + ["CETARTIO", "CETACEA", "ODONTOCETI"],
}


def mrca_age(a: str, b: str) -> float:
    shared = set(PATH[a]) & set(PATH[b])
    return min(AGE[c] for c in shared)


def vcv(species: list[str]) -> np.ndarray:
    n = len(species)
    C = np.zeros((n, n))
    for i, j in itertools.product(range(n), range(n)):
        C[i, j] = ROOT_AGE - (0.0 if i == j else mrca_age(species[i], species[j]))
    return C


def gls(y: np.ndarray, X: np.ndarray, C: np.ndarray):
    Cinv = np.linalg.inv(C)
    XtCi = X.T @ Cinv
    beta = np.linalg.solve(XtCi @ X, XtCi @ y)
    resid = y - X @ beta
    n, k = X.shape
    covb = (float(resid.T @ Cinv @ resid) / (n - k)) * np.linalg.inv(XtCi @ X)
    se = np.sqrt(np.diag(covb))
    pvals = 2 * tdist.sf(np.abs(beta / se), n - k)
    return beta, pvals


def fit(y: np.ndarray, life: np.ndarray, mass: np.ndarray, C: np.ndarray) -> dict:
    Xl = (np.log10(life) - np.log10(life).mean()) / np.log10(life).std()
    Xm = (np.log10(mass) - np.log10(mass).mean()) / np.log10(mass).std()
    X = np.column_stack([np.ones_like(y), Xl, Xm])
    n = len(y)
    b_o, p_o = gls(y, X, np.eye(n))
    b_p, p_p = gls(y, X, C)
    return {
        "n": int(n),
        "collinearity_r": round(float(pearsonr(Xl, Xm)[0]), 3),
        "ols_p_lifespan": round(float(p_o[1]), 4),
        "pgls_beta_lifespan": round(float(b_p[1]), 4),
        "pgls_p_lifespan": round(float(p_p[1]), 4),
        "pgls_p_mass": round(float(p_p[2]), 4),
        "_Xl": Xl, "_y": y,
    }


def bh_fdr(pvals: list[float], alpha: float = 0.05) -> int:
    m = len(pvals)
    if m == 0:
        return 0
    order = np.argsort(pvals)
    survivors = 0
    for rank, idx in enumerate(order, start=1):
        if pvals[idx] <= alpha * rank / m:
            survivors = rank
    return survivors


def embedding_divergence(path: Path) -> dict[str, float]:
    data = np.load(path)
    if "human" not in data.files:
        return {}
    href = data["human"].astype(np.float64)
    out: dict[str, float] = {}
    for sp in data.files:
        if sp == "human":
            continue
        out[sp] = float(np.linalg.norm(data[sp].astype(np.float64) - href))
    return out


def run_region(region: str) -> dict:
    files = sorted(EMB_DIR.glob(f"*_{region}.npz"))
    per_gene: list[dict] = []
    per_species_sum: dict[str, list[float]] = {}
    for fp in files:
        gene = fp.name.replace(f"_{region}.npz", "")
        div = embedding_divergence(fp)
        species = [s for s in div if s in TRAITS]
        if len(species) < 6:
            per_gene.append({"gene": gene, "n": len(species), "status": "too_few_species"})
            continue
        y = np.array([div[s] for s in species])
        life = np.array([TRAITS[s][0] for s in species])
        mass = np.array([TRAITS[s][1] for s in species])
        res = fit(y, life, mass, vcv(species))
        per_gene.append({
            "gene": gene, "n": res["n"],
            "ols_p_lifespan": res["ols_p_lifespan"],
            "pgls_p_lifespan": res["pgls_p_lifespan"],
            "pgls_beta_lifespan": res["pgls_beta_lifespan"],
            "direction": "diverge" if res["pgls_beta_lifespan"] > 0 else "conserve",
        })
        for s in species:
            per_species_sum.setdefault(s, []).append(div[s])

    tested = [g for g in per_gene if "pgls_p_lifespan" in g]
    survivors = bh_fdr([g["pgls_p_lifespan"] for g in tested])

    pooled: dict = {"status": "insufficient"}
    fig = None
    species = [s for s in per_species_sum if s in TRAITS]
    if len(species) >= 6:
        y = np.array([float(np.mean(per_species_sum[s])) for s in species])
        life = np.array([TRAITS[s][0] for s in species])
        mass = np.array([TRAITS[s][1] for s in species])
        res = fit(y, life, mass, vcv(species))
        pooled = {k: v for k, v in res.items() if not k.startswith("_")}
        fig = (res["_Xl"], res["_y"], life, res["pgls_p_lifespan"])

    return {
        "region": region, "n_genes_tested": len(tested), "fdr_survivors": survivors,
        "per_gene": per_gene, "pooled": pooled, "_fig": fig,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not EMB_DIR.exists() or not any(EMB_DIR.glob("*_utr*.npz")):
        print(f"No embeddings in {EMB_DIR}. Run scripts/embed_utr_dna_lm.py first.")
        return 1

    regions = {r: run_region(r) for r in ("utr3", "utr5")}
    summary = {
        "analysis": "utr_dna_lm_embedding_divergence_vs_longevity",
        "model": "InstaDeepAI/nucleotide-transformer-v2-50m-multi-species",
        "metric": "L2 distance of mean-pooled UTR embedding to human; OLS + PGLS on "
                  "log10(lifespan)+log10(mass); two-sided; BH-FDR across genes",
        "n_species_panel": len(TRAITS),
        "regions": {r: {k: v for k, v in d.items() if not k.startswith("_")}
                    for r, d in regions.items()},
    }
    (OUT_DIR / "utr_embedding_divergence.json").write_text(json.dumps(summary, indent=2))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, region in zip(axes, ("utr3", "utr5"), strict=True):
        fg = regions[region]["_fig"]
        ax.set_xlabel("log10 max lifespan (yr)")
        ax.set_ylabel("mean embedding L2 to human")
        if fg is None:
            ax.text(0.5, 0.5, "insufficient data", ha="center", transform=ax.transAxes)
            continue
        Xl, y, life, pgls_p = fg
        ax.scatter(np.log10(life), y, s=40, c="#9b59b6")
        b = np.polyfit(Xl, y, 1)
        xs = np.linspace(np.log10(life).min(), np.log10(life).max(), 50)
        xs_z = (xs - np.log10(life).mean()) / np.log10(life).std()
        ax.plot(xs, b[0] * xs_z + b[1], c="grey", ls="--")
        ax.set_title(f"{region.upper()} DNA-LM embedding vs lifespan\nPGLS p={pgls_p:.3f} "
                     f"(FDR {regions[region]['fdr_survivors']}/"
                     f"{regions[region]['n_genes_tested']})", fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "utr_embedding_divergence.png", dpi=140)

    for region, d in regions.items():
        p = d["pooled"]
        print(f"\n== {region.upper()} (DNA-LM) ==  genes tested={d['n_genes_tested']} "
              f"FDR survivors={d['fdr_survivors']}")
        print(f"   pooled PGLS lifespan p={p.get('pgls_p_lifespan', 'NA')} "
              f"beta={p.get('pgls_beta_lifespan', 'NA')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
