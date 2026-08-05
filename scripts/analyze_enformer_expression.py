#!/usr/bin/env python3
"""Does Enformer-predicted expression at the TSS track longevity? (pilot: 3 genes)

The functional AI readout of the regulatory investigation. For each (gene, species) window
Enformer predicts 5313 human tracks at the TSS bin (scripts/run_enformer_expression.py).
Predicted expression per species = mean over CAGE tracks (if the Enformer human targets file
is present to identify them) else mean over all tracks. Each gene's per-species expression is
z-scored (gene expression scales differ) and regressed on log10(lifespan) + log10(mass),
OLS + PGLS, two-sided; pooled per-species mean-z gives the power-maximising test. Same PGLS
machine as every other lane.

Because Enformer is trained on the human genome, the per-species prediction is a comparative
in-silico readout ("what the human model predicts for this species' sequence"): the sequence
varies, the reader is fixed. This is out-of-distribution for non-mammalian-model species and
is a pilot on 3 genes (HAS2, TP53, CDK2), not a screen.

Inputs:  data/interim/enformer/{GENE}_{species}.npy       (5313-vector, central-bin mean)
         data/interim/enformer/targets_human.txt          (optional; to select CAGE tracks)
Outputs: docs/results/2026-08-04-utr3-regulatory-divergence/enformer_expression.{json,png}
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
EMB_DIR = REPO / "data" / "interim" / "enformer"
TARGETS = EMB_DIR / "targets_human.txt"
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
    "PRIMATE_H": 90,
}
ROOT_AGE = AGE["TH"]
_E = ["TH", "PLAC", "BOREO", "EUARCH"]
_R = _E + ["RODENTIA"]
_RN = _R + ["NONSCIUR"]
_L = ["TH", "PLAC", "BOREO", "LAURAS"]
_LS = _L + ["SCROTIFERA"]
_LF = _LS + ["FEREUUNG"]
PATH = {
    "human": _E + ["PRIM", "PRIMATE_H"],
    "opossum": ["TH"], "elephant": ["TH", "PLAC"],
    "rhesus": _E + ["PRIM"], "mouse_lemur": _E + ["PRIM"],
    "ground_squirrel": _R, "guinea_pig": _RN + ["HYSTRICOMORPHA"],
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
    return min(AGE[c] for c in set(PATH[a]) & set(PATH[b]))


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
    return beta, 2 * tdist.sf(np.abs(beta / se), n - k)


def fit(y: np.ndarray, life: np.ndarray, mass: np.ndarray, C: np.ndarray) -> dict:
    Xl = (np.log10(life) - np.log10(life).mean()) / np.log10(life).std()
    Xm = (np.log10(mass) - np.log10(mass).mean()) / np.log10(mass).std()
    X = np.column_stack([np.ones_like(y), Xl, Xm])
    b_o, p_o = gls(y, X, np.eye(len(y)))
    b_p, p_p = gls(y, X, C)
    return {
        "n": int(len(y)), "collinearity_r": round(float(pearsonr(Xl, Xm)[0]), 3),
        "ols_p_lifespan": round(float(p_o[1]), 4),
        "pgls_beta_lifespan": round(float(b_p[1]), 4),
        "pgls_p_lifespan": round(float(p_p[1]), 4),
        "pgls_p_mass": round(float(p_p[2]), 4), "_Xl": Xl, "_y": y,
    }


def cage_indices() -> tuple[list[int], str]:
    """Track indices whose description mentions CAGE (one targets row per track, in order)."""
    if not TARGETS.exists():
        return [], "all tracks (CAGE metadata absent)"
    lines = TARGETS.read_text().splitlines()
    rows = lines[1:] if lines and "description" in lines[0].lower() else lines
    idx = [i for i, line in enumerate(rows) if "CAGE" in line.upper()]
    if idx:
        return idx, f"CAGE ({len(idx)} tracks)"
    return [], "all tracks (no CAGE rows matched)"


def expr_per_gene(gene: str, cage: list[int]) -> dict[str, float]:
    out: dict[str, float] = {}
    for fp in EMB_DIR.glob(f"{gene}_*.npy"):
        sp = fp.name[len(gene) + 1 : -4]
        vec = np.load(fp)
        out[sp] = float(vec[cage].mean() if cage else vec.mean())
    return out


def zscore(d: dict[str, float]) -> dict[str, float]:
    vals = np.array(list(d.values()))
    mu, sd = vals.mean(), vals.std() or 1.0
    return {k: (v - mu) / sd for k, v in d.items()}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not EMB_DIR.exists() or not any(EMB_DIR.glob("*.npy")):
        print(f"No Enformer predictions in {EMB_DIR}. Run scripts/run_enformer_expression.py.")
        return 1
    cage, track_desc = cage_indices()
    genes = sorted({fp.name.split("_", 1)[0] for fp in EMB_DIR.glob("*.npy")})

    per_gene: list[dict] = []
    zsum: dict[str, list[float]] = {}
    figs: dict[str, tuple] = {}
    for gene in genes:
        expr = expr_per_gene(gene, cage)
        species = [s for s in expr if s in TRAITS]
        if len(species) < 6:
            continue
        y = np.array([expr[s] for s in species])
        life = np.array([TRAITS[s][0] for s in species])
        mass = np.array([TRAITS[s][1] for s in species])
        res = fit(y, life, mass, vcv(species))
        per_gene.append({
            "gene": gene, "n": res["n"], "ols_p_lifespan": res["ols_p_lifespan"],
            "pgls_p_lifespan": res["pgls_p_lifespan"], "pgls_beta_lifespan": res["pgls_beta_lifespan"],
            "direction": "up" if res["pgls_beta_lifespan"] > 0 else "down",
        })
        figs[gene] = (np.log10(life), y, res["pgls_p_lifespan"])
        for s, z in zscore({s: expr[s] for s in species}).items():
            zsum.setdefault(s, []).append(z)

    species = [s for s in zsum if s in TRAITS]
    pooled = {"status": "insufficient"}
    pfig = None
    if len(species) >= 6:
        y = np.array([float(np.mean(zsum[s])) for s in species])
        life = np.array([TRAITS[s][0] for s in species])
        mass = np.array([TRAITS[s][1] for s in species])
        res = fit(y, life, mass, vcv(species))
        pooled = {k: v for k, v in res.items() if not k.startswith("_")}
        pfig = (np.log10(life), y, res["pgls_p_lifespan"])

    summary = {
        "analysis": "enformer_predicted_expression_vs_longevity_pilot",
        "model": "Enformer (EleutherAI/enformer-official-rough), human head, TSS central bins",
        "tracks_used": track_desc, "genes": genes, "n_species_panel": len(species),
        "per_gene": per_gene, "pooled": pooled,
    }
    (OUT_DIR / "enformer_expression.json").write_text(json.dumps(summary, indent=2))

    ncol = len(genes) + 1
    fig, axes = plt.subplots(1, ncol, figsize=(4 * ncol, 4))
    for ax, gene in zip(axes[:-1], genes, strict=False):
        lx, y, p = figs[gene]
        ax.scatter(lx, y, s=35, c="#e67e22")
        ax.set_title(f"{gene}\nPGLS p={p:.3f}", fontsize=9)
        ax.set_xlabel("log10 lifespan")
        ax.set_ylabel("pred. expression")
    if pfig is not None:
        lx, y, p = pfig
        axes[-1].scatter(lx, y, s=35, c="#c0392b")
        axes[-1].set_title(f"pooled (mean-z)\nPGLS p={p:.3f}", fontsize=9)
        axes[-1].set_xlabel("log10 lifespan")
        axes[-1].set_ylabel("mean-z pred. expression")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "enformer_expression.png", dpi=140)

    print(f"tracks: {track_desc}")
    for g in per_gene:
        print(f"  {g['gene']:6s} n={g['n']} PGLS p={g['pgls_p_lifespan']} "
              f"beta={g['pgls_beta_lifespan']:+.3f} {g['direction']}")
    print(f"pooled PGLS lifespan p={pooled.get('pgls_p_lifespan')} "
          f"beta={pooled.get('pgls_beta_lifespan')} mass p={pooled.get('pgls_p_mass')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
