#!/usr/bin/env python3
"""Power calibration: what effect size can our n=22 PGLS actually detect?

Every lane in this project returns a null. Before reading that as biology we must know the
detection floor: with 22 species, a lifespan-plus-mass PGLS, and the real mass-lifespan
collinearity (r ~= 0.70), how large must a true lifespan effect be before we reliably see it?

Method: on the real 22-species trait table and Brownian phylogenetic covariance, simulate a
response y = beta * z(log10 lifespan) + phylogenetic residual (unit variance), then fit the
exact model used in the analyses (PGLS with lifespan + mass) and record whether lifespan
reaches p < 0.05. Repeating over many draws and a grid of beta gives the power curve; the
same simulation without the mass covariate isolates the power lost to collinearity. Effect
size is reported as the marginal correlation r = beta / sqrt(beta^2 + 1) for interpretability.

Outputs: docs/results/<date>-power-calibration/power_calibration.{json,png}
Pure simulation; no network, no Biohub credits.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import matplotlib
import numpy as np
from scipy.stats import t as tdist

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "results" / "2026-08-05-power-calibration"

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


def pgls_p_lifespan(y: np.ndarray, X: np.ndarray, Cinv: np.ndarray) -> float:
    XtCi = X.T @ Cinv
    beta = np.linalg.solve(XtCi @ X, XtCi @ y)
    resid = y - X @ beta
    n, k = X.shape
    covb = (float(resid.T @ Cinv @ resid) / (n - k)) * np.linalg.inv(XtCi @ X)
    se = np.sqrt(np.diag(covb))
    return float(2 * tdist.sf(abs(beta[1] / se[1]), n - k))


def main() -> int:
    rng = np.random.default_rng(0)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    species = list(TRAITS)
    n = len(species)
    life = np.array([TRAITS[s][0] for s in species])
    mass = np.array([TRAITS[s][1] for s in species])
    Xl = (np.log10(life) - np.log10(life).mean()) / np.log10(life).std()
    Xm = (np.log10(mass) - np.log10(mass).mean()) / np.log10(mass).std()
    coll = float(np.corrcoef(Xl, Xm)[0, 1])

    C = vcv(species)
    Cn = C / np.mean(np.diag(C))          # unit-variance Brownian residual
    L = np.linalg.cholesky(Cn)
    Cinv = np.linalg.inv(C)

    X_full = np.column_stack([np.ones(n), Xl, Xm])
    X_life = np.column_stack([np.ones(n), Xl])

    betas = np.round(np.linspace(0.0, 1.2, 13), 3)
    reps = 3000
    rows = []
    for b in betas:
        hit_full = hit_life = 0
        for _ in range(reps):
            y = b * Xl + L @ rng.standard_normal(n)
            if pgls_p_lifespan(y, X_full, Cinv) < 0.05:
                hit_full += 1
            if pgls_p_lifespan(y, X_life, Cinv) < 0.05:
                hit_life += 1
        rows.append({
            "beta": float(b),
            "marginal_r": round(float(b / np.sqrt(b * b + 1)), 3),
            "power_pgls_lifespan_plus_mass": round(hit_full / reps, 3),
            "power_pgls_lifespan_only": round(hit_life / reps, 3),
        })

    def min_r_for_power(key: str, target: float = 0.8) -> float | None:
        for r in rows:
            if r[key] >= target:
                return r["marginal_r"]
        return None

    summary = {
        "n_species": n, "reps_per_beta": reps, "alpha": 0.05,
        "mass_lifespan_collinearity_r": round(coll, 3),
        "min_marginal_r_for_80pct_power_with_mass": min_r_for_power("power_pgls_lifespan_plus_mass"),
        "min_marginal_r_for_80pct_power_lifespan_only": min_r_for_power("power_pgls_lifespan_only"),
        "curve": rows,
    }
    (OUT_DIR / "power_calibration.json").write_text(json.dumps(summary, indent=2))

    # observed pooled marginal |r| of key analyses (computed from their result data)
    observed = {"classical 3' UTR divergence": 0.545, "Enformer CAGE expression": 0.026}

    r_axis = [r["marginal_r"] for r in rows]
    plt.figure(figsize=(7, 5))
    plt.plot(r_axis, [r["power_pgls_lifespan_plus_mass"] for r in rows],
             "-o", c="#c0392b", label="PGLS lifespan + mass (as run)")
    plt.plot(r_axis, [r["power_pgls_lifespan_only"] for r in rows],
             "-o", c="#2980b9", label="PGLS lifespan only")
    plt.axhline(0.8, ls="--", c="grey", lw=1)
    for name, rv in observed.items():
        plt.axvline(rv, ls=":", c="#27ae60", lw=1.2)
        plt.text(rv + 0.005, 0.05, name, rotation=90, va="bottom", fontsize=7, c="#1e8449")
    plt.xlabel("true effect size (marginal correlation |r|)")
    plt.ylabel("power (P detect at p<0.05)")
    plt.title(f"Detection floor at n={n} (mass-lifespan collinearity r={coll:.2f})", fontsize=10)
    plt.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "power_calibration.png", dpi=140)

    print(f"n={n}  collinearity r={coll:.2f}")
    print(f"min |r| for 80% power (lifespan+mass): "
          f"{summary['min_marginal_r_for_80pct_power_with_mass']}")
    print(f"min |r| for 80% power (lifespan only): "
          f"{summary['min_marginal_r_for_80pct_power_lifespan_only']}")
    for r in rows:
        print(f"  r={r['marginal_r']:.2f}  power(+mass)={r['power_pgls_lifespan_plus_mass']:.2f}"
              f"  power(life-only)={r['power_pgls_lifespan_only']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
