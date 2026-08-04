#!/usr/bin/env python3
"""Regulatory-divergence test: does UTR divergence track longevity across species?

This moves the *unit of analysis* off the coding interface (where the ESM screen is
formally closed as negative) and onto the non-coding regulatory sequence that sets gene
dosage: the 5' UTR (translation efficiency) and 3' UTR (mRNA stability / miRNA control).

For each gene and UTR region:
  * per-species divergence = Jukes-Cantor distance of a global pairwise alignment of the
    species UTR to the human UTR (biotite, affine gaps, no terminal penalty),
  * regress divergence on log10(max lifespan) and log10(body mass), OLS and PGLS
    (Brownian-motion phylogenetic GLS) -- identical machinery to the interface rigor
    battery (analyze_phylo_continuous.py). Two-sided: a positive lifespan slope means
    long-lived species diverge MORE (regulatory rewiring); negative means MORE conserved
    (stabilizing / dosage constraint). Both are informative.

Pooled per-species mean divergence gives one power-maximising test per region; per-gene
tests are Benjamini-Hochberg FDR-controlled to report survivors exactly as the interface
lanes did (e.g. "0 / N genes survive FDR").

Inputs:  data/interim/utr/{GENE}_utr5.fasta, {GENE}_utr3.fasta   (headers >{taxid}|{name}|{group})
Outputs: docs/results/2026-08-04-utr3-regulatory-divergence/{json,png}
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import biotite.sequence as bseq
import biotite.sequence.align as balign
import matplotlib
import numpy as np
from scipy.stats import pearsonr
from scipy.stats import t as tdist

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
UTR_DIR = REPO / "data" / "interim" / "utr"
OUT_DIR = REPO / "docs" / "results" / "2026-08-04-utr3-regulatory-divergence"

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

# --- approximate timetree (clade node ages Mya BP) + per-species ancestral node path
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


# --- regression engines (OLS = GLS with identity C; PGLS = GLS with Brownian C)
def gls(y: np.ndarray, X: np.ndarray, C: np.ndarray):
    Cinv = np.linalg.inv(C)
    XtCi = X.T @ Cinv
    beta = np.linalg.solve(XtCi @ X, XtCi @ y)
    resid = y - X @ beta
    n, k = X.shape
    covb = (float(resid.T @ Cinv @ resid) / (n - k)) * np.linalg.inv(XtCi @ X)
    se = np.sqrt(np.diag(covb))
    tvals = beta / se
    pvals = 2 * tdist.sf(np.abs(tvals), n - k)
    return beta, se, pvals


def fit(y: np.ndarray, life: np.ndarray, mass: np.ndarray, C: np.ndarray) -> dict:
    Xl = (np.log10(life) - np.log10(life).mean()) / np.log10(life).std()
    Xm = (np.log10(mass) - np.log10(mass).mean()) / np.log10(mass).std()
    X = np.column_stack([np.ones_like(y), Xl, Xm])
    n = len(y)
    b_o, _se_o, p_o = gls(y, X, np.eye(n))
    b_p, _se_p, p_p = gls(y, X, C)
    return {
        "n": int(n),
        "collinearity_r": round(float(pearsonr(Xl, Xm)[0]), 3),
        "ols_beta_lifespan": round(float(b_o[1]), 4), "ols_p_lifespan": round(float(p_o[1]), 4),
        "pgls_beta_lifespan": round(float(b_p[1]), 4), "pgls_p_lifespan": round(float(p_p[1]), 4),
        "pgls_p_mass": round(float(p_p[2]), 4),
        "_Xl": Xl, "_y": y,
    }


# --- UTR divergence via global pairwise alignment (biotite)
_NUC = set("ACGT")
_MATRIX = balign.SubstitutionMatrix.std_nucleotide_matrix()


def _clean(seq: str) -> str:
    return "".join(c for c in seq.upper().replace("U", "T") if c in _NUC)


def jc_distance(a: str, b: str, min_len: int = 20) -> float:
    a, b = _clean(a), _clean(b)
    if len(a) < min_len or len(b) < min_len:
        return float("nan")
    aln = balign.align_optimal(
        bseq.NucleotideSequence(a), bseq.NucleotideSequence(b),
        _MATRIX, gap_penalty=(-10, -1), terminal_penalty=False,
    )[0]
    trace = aln.trace
    paired = trace[(trace[:, 0] >= 0) & (trace[:, 1] >= 0)]
    if len(paired) < min_len:
        return float("nan")
    aa = np.frombuffer(a.encode(), dtype=np.uint8)[paired[:, 0]]
    bb = np.frombuffer(b.encode(), dtype=np.uint8)[paired[:, 1]]
    matches = int(np.sum(aa == bb))
    p = 1.0 - matches / len(paired)
    if p >= 0.75:
        return float("nan")
    return float(-0.75 * np.log(1 - 4 / 3 * p))


def load_fasta(path: Path) -> dict[str, str]:
    seqs: dict[str, str] = {}
    name = None
    buf: list[str] = []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if name is not None:
                seqs[name] = "".join(buf)
            name = line[1:].split("|")[1]  # >{taxid}|{name}|{group}
            buf = []
        elif line.strip():
            buf.append(line.strip())
    if name is not None:
        seqs[name] = "".join(buf)
    return seqs


MAX_ALN = 3000  # cap alignment length; keep the region proximal to the CDS


def _proximal(seq: str, region: str) -> str:
    """Keep the functional UTR portion nearest the coding sequence, capped to MAX_ALN.

    For a 3' UTR that is the 5' end (just past the stop codon); for a 5' UTR the 3' end
    (just before the start codon). Bounds O(L^2) alignment cost for very long UTRs.
    """
    if len(seq) <= MAX_ALN:
        return seq
    return seq[:MAX_ALN] if region == "utr3" else seq[-MAX_ALN:]


def species_divergence(path: Path, region: str) -> dict[str, float]:
    seqs = load_fasta(path)
    if "human" not in seqs:
        return {}
    ref = _proximal(seqs["human"], region)
    out: dict[str, float] = {}
    for sp, seq in seqs.items():
        if sp == "human":
            continue
        d = jc_distance(ref, _proximal(seq, region))
        if not np.isnan(d):
            out[sp] = d
    return out


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


def run_region(region: str) -> dict:
    files = sorted(UTR_DIR.glob(f"*_{region}.fasta"))
    per_gene: list[dict] = []
    per_species_sum: dict[str, list[float]] = {}
    for fp in files:
        gene = fp.name.replace(f"_{region}.fasta", "")
        div = species_divergence(fp, region)
        species = [s for s in div if s in TRAITS]
        if len(species) < 6:  # need df for 3-param fit
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
    pvals = [g["pgls_p_lifespan"] for g in tested]
    survivors = bh_fdr(pvals)

    pooled: dict = {"status": "insufficient"}
    pooled_fig = None
    species = [s for s in per_species_sum if len(per_species_sum[s]) >= 1 and s in TRAITS]
    if len(species) >= 6:
        y = np.array([float(np.mean(per_species_sum[s])) for s in species])
        life = np.array([TRAITS[s][0] for s in species])
        mass = np.array([TRAITS[s][1] for s in species])
        res = fit(y, life, mass, vcv(species))
        pooled = {k: v for k, v in res.items() if not k.startswith("_")}
        pooled_fig = (res["_Xl"], res["_y"], life, res["pgls_p_lifespan"])

    return {
        "region": region,
        "n_genes_tested": len(tested),
        "fdr_survivors": survivors,
        "per_gene": per_gene,
        "pooled": pooled,
        "_fig": pooled_fig,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not UTR_DIR.exists() or not any(UTR_DIR.glob("*_utr*.fasta")):
        print(f"No UTR FASTAs in {UTR_DIR}. Run scripts/fetch_lane_utr3.py first.")
        return 1

    regions = {}
    for region in ("utr3", "utr5"):
        regions[region] = run_region(region)

    summary = {
        "analysis": "utr_regulatory_divergence_vs_longevity",
        "method": "per-species JC distance of pairwise UTR alignment to human; OLS + PGLS "
                  "on log10(lifespan)+log10(mass); two-sided; BH-FDR across genes",
        "n_species_panel": len(TRAITS),
        "regions": {r: {k: v for k, v in d.items() if not k.startswith("_")}
                    for r, d in regions.items()},
    }
    (OUT_DIR / "utr_divergence.json").write_text(json.dumps(summary, indent=2))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, region in zip(axes, ("utr3", "utr5"), strict=True):
        fg = regions[region]["_fig"]
        ax.set_title(f"{region.upper()} pooled divergence vs lifespan")
        ax.set_xlabel("log10 max lifespan (yr)")
        ax.set_ylabel("mean JC distance to human")
        if fg is None:
            ax.text(0.5, 0.5, "insufficient data", ha="center", transform=ax.transAxes)
            continue
        Xl, y, life, pgls_p = fg
        ax.scatter(np.log10(life), y, s=40, c="#4f81bd")
        b = np.polyfit(Xl, y, 1)
        xs = np.linspace(np.log10(life).min(), np.log10(life).max(), 50)
        xs_z = (xs - np.log10(life).mean()) / np.log10(life).std()
        ax.plot(xs, b[0] * xs_z + b[1], c="grey", ls="--")
        ax.set_title(f"{region.upper()} pooled vs lifespan\nPGLS lifespan p={pgls_p:.3f} "
                     f"(FDR survivors: {regions[region]['fdr_survivors']}/"
                     f"{regions[region]['n_genes_tested']})", fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "utr_divergence.png", dpi=140)

    for region, d in regions.items():
        p = d["pooled"]
        pooled_p = p.get("pgls_p_lifespan", "NA")
        print(f"\n== {region.upper()} ==  genes tested={d['n_genes_tested']} "
              f"FDR survivors={d['fdr_survivors']}")
        print(f"   pooled PGLS lifespan p={pooled_p}  (mass p={p.get('pgls_p_mass', 'NA')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
