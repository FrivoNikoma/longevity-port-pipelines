#!/usr/bin/env python3
"""Phylogeny-aware continuous reanalysis of the longevity signal.

Instead of binary ELLSM/BMAL/Reference groups + Mann-Whitney, regress per-species
molecular divergence on **maximum lifespan and adult body mass jointly**, with and
without phylogenetic correction (PGLS under Brownian motion). This dissociates
body mass from longevity and accounts for the non-independence of related species
(the mole-rats, the bats and the whales are not independent samples).

Two response variables:
  A) ESM interface divergence  = per-species mean cell_cycle enrichment_ratio
                                 (data/output/enrichment.parquet)
  B) selection (dN/dS)         = per-species pairwise Nei-Gojobori omega vs human
                                 on Ku80 (data/interim/ku80/ku80_codon_alignment.fasta)

Predictors: log10(max lifespan, yr), log10(adult body mass, kg).

Method: OLS multiple regression vs PGLS (GLS with a Brownian-motion phylogenetic
variance-covariance matrix built from an approximate mammalian timetree).

Outputs: docs/results/2026-07-29-phylo-continuous-reanalysis/{json,png}

Trait values are literature maxima (AnAge / PanTHERIA-consistent); the tree is an
approximate TimeTree topology with rounded divergence times -- adequate for
down-weighting close relatives in an exploratory PGLS, not a formal dated tree.
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
PARQUET = REPO / "data" / "output" / "enrichment.parquet"
KU80_ALN = REPO / "data" / "interim" / "ku80" / "ku80_codon_alignment.fasta"
OUT_DIR = REPO / "docs" / "results" / "2026-07-29-phylo-continuous-reanalysis"

# --- traits: species -> (max_lifespan_yr, adult_body_mass_kg)  [AnAge/PanTHERIA-consistent]
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

# --- approximate timetree: clade node ages (Mya BP) and per-species ancestral node path
AGE = {
    "TH": 160, "PLAC": 100, "BOREO": 95, "EUARCH": 90, "PRIM": 70,
    "RODENTIA": 72, "NONSCIUR": 71, "HYSTRICOMORPHA": 45, "BATHYERGIDAE": 26,
    "MYOMORPHA": 45, "MUROIDEA": 25, "MURINAE": 13,
    "LAURAS": 80, "SCROTIFERA": 78, "CHIROPTERA": 55, "FEREUUNG": 76,
    "ZOOAMATA": 75, "CARNIVORA": 54, "CETARTIO": 60, "CETACEA": 35, "ODONTOCETI": 33,
}
ROOT_AGE = AGE["TH"]
_E = ["TH", "PLAC", "BOREO", "EUARCH"]          # to Euarchontoglires
_R = _E + ["RODENTIA"]                          # to Rodentia
_RN = _R + ["NONSCIUR"]
_L = ["TH", "PLAC", "BOREO", "LAURAS"]          # to Laurasiatheria
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


# --- Nei-Gojobori (compact) for response B
BASES = "TCAG"
CODONS = [a + b + c for a in BASES for b in BASES for c in BASES]
AA = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
C2A = dict(zip(CODONS, AA, strict=True))


def _syn(codon):
    if C2A.get(codon, "*") == "*":
        return np.nan
    aa, s = C2A[codon], 0.0
    for i in range(3):
        for b in BASES:
            if b != codon[i]:
                m = codon[:i] + b + codon[i + 1:]
                if C2A.get(m) != "*" and C2A.get(m) == aa:
                    s += 1 / 3
    return s


SYN = {c: _syn(c) for c in CODONS}


def _diff(c1, c2):
    if c1 == c2:
        return 0.0, 0.0
    pos = [i for i in range(3) if c1[i] != c2[i]]
    sd = nd = 0.0
    npath = 0
    for perm in itertools.permutations(pos):
        cur, s, n_, ok = c1, 0.0, 0.0, True
        for i in perm:
            nxt = cur[:i] + c2[i] + cur[i + 1:]
            if C2A.get(nxt) == "*" or C2A.get(cur) == "*":
                ok = False
                break
            if C2A.get(nxt) == C2A.get(cur):
                s += 1
            else:
                n_ += 1
            cur = nxt
        if ok:
            sd += s
            nd += n_
            npath += 1
    return (sd / npath, nd / npath) if npath else (np.nan, np.nan)


def load_codon_aln():
    seqs, name = {}, None
    for line in KU80_ALN.read_text().splitlines():
        if line.startswith(">"):
            name = line[1:].split("|")[0]
            seqs[name] = []
        elif line.strip():
            seqs[name].append(line.strip())
    return {k: "".join(v) for k, v in seqs.items()}


def ku80_omega_vs_human():
    aln = load_codon_aln()
    ref = aln["human"]
    ncod = len(ref) // 3
    core = [c for c in range(ncod)
            if "-" not in ref[c * 3:c * 3 + 3] and C2A.get(ref[c * 3:c * 3 + 3], "*") != "*"]
    out = {}
    for sp, seq in aln.items():
        if sp == "human":
            continue
        Sd = Nd = Ss = Ns = 0.0
        for c in core:
            c1, c2 = ref[c * 3:c * 3 + 3], seq[c * 3:c * 3 + 3]
            if "-" in c2 or "N" in c1 or "N" in c2 or C2A.get(c2, "*") == "*":
                continue
            s1, s2 = SYN[c1], SYN.get(c2, np.nan)
            if np.isnan(s1) or np.isnan(s2):
                continue
            sd, nd = _diff(c1, c2)
            if np.isnan(sd):
                continue
            S = (s1 + s2) / 2
            Sd += sd
            Nd += nd
            Ss += S
            Ns += 3 - S
        pS, pN = (Sd / Ss if Ss else np.nan), (Nd / Ns if Ns else np.nan)

        def jc(p):
            return np.nan if (np.isnan(p) or p >= 0.75) else -0.75 * np.log(1 - 4 / 3 * p)

        dS, dN = jc(pS), jc(pN)
        out[sp] = (dN / dS) if (dS and dS > 0 and not np.isnan(dN)) else np.nan
    return out


# --- regression engines
def gls(y, X, C):
    Cinv = np.linalg.inv(C)
    XtCi = X.T @ Cinv
    beta = np.linalg.solve(XtCi @ X, XtCi @ y)
    resid = y - X @ beta
    n, k = X.shape
    sigma2 = float(resid.T @ Cinv @ resid) / (n - k)
    covb = sigma2 * np.linalg.inv(XtCi @ X)
    se = np.sqrt(np.diag(covb))
    tvals = beta / se
    pvals = 2 * tdist.sf(np.abs(tvals), n - k)
    # generalized R^2 vs GLS intercept-only
    one = np.ones((n, 1))
    b0 = np.linalg.solve(one.T @ Cinv @ one, one.T @ Cinv @ y)
    r0 = y - one @ b0
    ss_res = float(resid.T @ Cinv @ resid)
    ss_tot = float(r0.T @ Cinv @ r0)
    r2 = 1 - ss_res / ss_tot
    return beta, se, tvals, pvals, r2


def fit(y, life, mass, C, label):
    # z-score predictors
    Xl = (np.log10(life) - np.log10(life).mean()) / np.log10(life).std()
    Xm = (np.log10(mass) - np.log10(mass).mean()) / np.log10(mass).std()
    X = np.column_stack([np.ones_like(y), Xl, Xm])
    n = len(y)
    b_ols, se_o, t_o, p_o, r2_o = gls(y, X, np.eye(n))
    b_p, se_p, t_p, p_p, r2_p = gls(y, X, C)
    coll = float(pearsonr(Xl, Xm)[0])
    r_life = pearsonr(Xl, y)
    r_mass = pearsonr(Xm, y)
    return {
        "label": label, "n": int(n),
        "predictor_collinearity_r(logLife,logMass)": round(coll, 3),
        "raw_pearson_r_vs_logLifespan": [round(r_life[0], 3), round(r_life[1], 4)],
        "raw_pearson_r_vs_logMass": [round(r_mass[0], 3), round(r_mass[1], 4)],
        "OLS": {"beta_lifespan": round(b_ols[1], 4), "p_lifespan": round(p_o[1], 4),
                "beta_mass": round(b_ols[2], 4), "p_mass": round(p_o[2], 4),
                "R2": round(r2_o, 3)},
        "PGLS": {"beta_lifespan": round(b_p[1], 4), "p_lifespan": round(p_p[1], 4),
                 "beta_mass": round(b_p[2], 4), "p_mass": round(p_p[2], 4),
                 "R2": round(r2_p, 3)},
        "_Xl": Xl, "_y": y,
    }


def main():
    import pandas as pd
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # response A: per-species mean cell_cycle enrichment_ratio
    df = pd.read_parquet(PARQUET)
    embA = df.groupby("target_species")["enrichment_ratio"].mean()

    # response B: Ku80 dN/dS vs human
    omega = ku80_omega_vs_human()

    species = [s for s in TRAITS if s in embA.index]
    life = np.array([TRAITS[s][0] for s in species])
    mass = np.array([TRAITS[s][1] for s in species])
    C = vcv(species)

    yA = np.array([embA[s] for s in species])
    resA = fit(yA, life, mass, C, "ESM interface divergence (cell_cycle)")

    sp_b = [s for s in species if s in omega and not np.isnan(omega[s])]
    lifeb = np.array([TRAITS[s][0] for s in sp_b])
    massb = np.array([TRAITS[s][1] for s in sp_b])
    Cb = vcv(sp_b)
    yB = np.array([omega[s] for s in sp_b])
    resB = fit(yB, lifeb, massb, Cb, "Ku80 dN/dS vs human")

    out = {k: v for k, v in resA.items() if not k.startswith("_")}
    out2 = {k: v for k, v in resB.items() if not k.startswith("_")}
    summary = {"n_species": len(species), "responseA_embedding": out, "responseB_dnds": out2}
    (OUT_DIR / "phylo_continuous.json").write_text(json.dumps(summary, indent=2))

    # figure
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    for a, res, life_, ylab in [(ax[0], resA, life, "mean enrichment_ratio (ESM)"),
                                (ax[1], resB, lifeb, "Ku80 dN/dS vs human")]:
        Xl, y = res["_Xl"], res["_y"]
        a.scatter(np.log10(life_), y, s=40, c="#4f81bd")
        xs = np.linspace(np.log10(life_).min(), np.log10(life_).max(), 50)
        xs_z = (xs - np.log10(life_).mean()) / np.log10(life_).std()
        # marginal OLS line (lifespan only, for visual)
        b = np.polyfit(Xl, y, 1)
        a.plot(xs, b[0] * xs_z + b[1], c="grey", ls="--", label="OLS (lifespan-marginal)")
        a.set_xlabel("log10 max lifespan (yr)")
        a.set_ylabel(ylab)
        ols, pg = res["OLS"], res["PGLS"]
        a.set_title(f"{res['label']}\n"
                    f"OLS lifespan p={ols['p_lifespan']:.3f} | "
                    f"PGLS lifespan p={pg['p_lifespan']:.3f}\n"
                    f"(controlling for mass; collinearity r="
                    f"{res['predictor_collinearity_r(logLife,logMass)']})", fontsize=9)
        a.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "phylo_continuous.png", dpi=140)

    # console
    for res in (resA, resB):
        print(f"\n== {res['label']}  (n={res['n']}) ==")
        print(f"  collinearity log(life)~log(mass) r={res['predictor_collinearity_r(logLife,logMass)']}")
        print(f"  raw r vs logLifespan={res['raw_pearson_r_vs_logLifespan']}  "
              f"vs logMass={res['raw_pearson_r_vs_logMass']}")
        print(f"  OLS : lifespan b={res['OLS']['beta_lifespan']:+.3f} p={res['OLS']['p_lifespan']:.3f} | "
              f"mass b={res['OLS']['beta_mass']:+.3f} p={res['OLS']['p_mass']:.3f} | R2={res['OLS']['R2']}")
        print(f"  PGLS: lifespan b={res['PGLS']['beta_lifespan']:+.3f} p={res['PGLS']['p_lifespan']:.3f} | "
              f"mass b={res['PGLS']['beta_mass']:+.3f} p={res['PGLS']['p_mass']:.3f} | R2={res['PGLS']['R2']}")


if __name__ == "__main__":
    main()
