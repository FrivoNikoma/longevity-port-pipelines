#!/usr/bin/env python3
"""Where does the 3' UTR conservation sit? miRNA target-site conservation vs longevity.

The classical 3' UTR test (analyze_utr3_divergence.py) found a diffuse, direction-consistent
conservation trend in long-lived species. 3' UTRs do not act uniformly: their main
post-transcriptional dosage lever is the set of short miRNA target sites (a miRNA binds a
6-8 nt seed match and represses the transcript). This script zooms from "the whole 3' UTR"
to "the specific miRNA sites", asking whether the conservation is concentrated on
regulatory sites.

For each gene:
  * canonical 7mer-m8 sites = reverse-complement of the miRNA seed+m8 for every broadly
    conserved human miRNA family (TargetScan miR_Family_Info.txt), located in the human
    3' UTR;
  * per species, retention = fraction of human sites whose exact 7-nt motif survives at the
    aligned position in the ortholog (biotite pairwise alignment); and site density =
    sites per kb of that species' 3' UTR (regulatory load);
  * regress each on log10(lifespan) + log10(mass), OLS + PGLS, two-sided, BH-FDR across
    genes -- the same machine as the interface battery and the UTR-divergence test.

Inputs:  data/interim/utr/{GENE}_utr3.fasta
         data/interim/mirna/miR_Family_Info.txt   (TargetScan release; download separately)
Outputs: docs/results/2026-08-04-utr3-regulatory-divergence/mirna_site_conservation.{json,png}
No Biohub credits used.
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
SEED_FILE = REPO / "data" / "interim" / "mirna" / "miR_Family_Info.txt"
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


# --- sequence helpers
_COMP = str.maketrans("ACGT", "TGCA")


def revcomp(seq: str) -> str:
    return seq.translate(_COMP)[::-1]


def load_seeds(path: Path, min_conservation: int = 2) -> set[str]:
    """Return canonical 7mer-m8 target-site motifs for broadly conserved human families."""
    motifs: set[str] = set()
    for line in path.read_text().splitlines():
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 6 or parts[2].strip() != "9606":
            continue
        try:
            cons = int(float(parts[5]))
        except ValueError:
            continue
        if cons < min_conservation:
            continue
        seed_m8 = parts[1].strip().upper().replace("U", "T")  # positions 2-8 of miRNA
        if len(seed_m8) == 7 and set(seed_m8) <= set("ACGT"):
            motifs.add(revcomp(seed_m8))  # site on the sense mRNA strand
    return motifs


def find_sites(seq: str, motifs: set[str]) -> list[int]:
    starts: list[int] = []
    for m in motifs:
        i = seq.find(m)
        while i != -1:
            starts.append(i)
            i = seq.find(m, i + 1)
    return sorted(set(starts))  # dedupe overlapping identical starts


def load_fasta(path: Path) -> dict[str, str]:
    seqs: dict[str, str] = {}
    name = None
    buf: list[str] = []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if name is not None:
                seqs[name] = "".join(buf)
            name = line[1:].split("|")[1]
            buf = []
        elif line.strip():
            buf.append(line.strip())
    if name is not None:
        seqs[name] = "".join(buf)
    return {k: "".join(c for c in v.upper().replace("U", "T") if c in "ACGT")
            for k, v in seqs.items()}


_MATRIX = balign.SubstitutionMatrix.std_nucleotide_matrix()
MAX_ALN = 3000


def human_to_species_map(human: str, species: str) -> dict[int, int]:
    aln = balign.align_optimal(
        bseq.NucleotideSequence(human), bseq.NucleotideSequence(species),
        _MATRIX, gap_penalty=(-10, -1), terminal_penalty=False,
    )[0]
    trace = aln.trace
    return {int(h): int(s) for h, s in trace if h >= 0 and s >= 0}


def retained_fraction(human: str, species: str, motif_len: int,
                      site_starts: list[int]) -> tuple[int, int]:
    """(retained, total) human sites whose exact motif survives at the aligned position."""
    hmap = human_to_species_map(human[:MAX_ALN], species[:MAX_ALN])
    retained = 0
    total = 0
    for st in site_starts:
        if st + motif_len > MAX_ALN:
            continue
        total += 1
        cols = [hmap.get(st + k, -1) for k in range(motif_len)]
        if -1 in cols:
            continue
        sub = "".join(species[c] for c in cols)
        if sub == human[st : st + motif_len]:
            retained += 1
    return retained, total


def run() -> dict:
    motifs = load_seeds(SEED_FILE)
    files = sorted(UTR_DIR.glob("*_utr3.fasta"))
    per_gene_ret: list[dict] = []
    ret_num: dict[str, int] = {}
    ret_den: dict[str, int] = {}
    dens_sites: dict[str, int] = {}
    dens_len: dict[str, int] = {}
    for fp in files:
        gene = fp.name.replace("_utr3.fasta", "")
        seqs = load_fasta(fp)
        if "human" not in seqs:
            continue
        human = seqs["human"]
        h_sites = find_sites(human[:MAX_ALN], motifs)
        gene_ret: dict[str, float] = {}
        for sp, seq in seqs.items():
            dens_sites[sp] = dens_sites.get(sp, 0) + len(find_sites(seq, motifs))
            dens_len[sp] = dens_len.get(sp, 0) + max(len(seq), 1)
            if sp == "human" or not h_sites:
                continue
            r, t = retained_fraction(human, seq, 7, h_sites)
            if t > 0:
                gene_ret[sp] = r / t
                ret_num[sp] = ret_num.get(sp, 0) + r
                ret_den[sp] = ret_den.get(sp, 0) + t
        species = [s for s in gene_ret if s in TRAITS]
        if len(h_sites) >= 3 and len(species) >= 6:
            y = np.array([gene_ret[s] for s in species])
            life = np.array([TRAITS[s][0] for s in species])
            mass = np.array([TRAITS[s][1] for s in species])
            res = fit(y, life, mass, vcv(species))
            per_gene_ret.append({
                "gene": gene, "n_human_sites": len(h_sites), "n": res["n"],
                "pgls_p_lifespan": res["pgls_p_lifespan"],
                "pgls_beta_lifespan": res["pgls_beta_lifespan"],
                "direction": "conserve" if res["pgls_beta_lifespan"] > 0 else "lose",
            })

    def pooled(num: dict[str, float], den: dict[str, float]) -> dict:
        species = [s for s in num if s in TRAITS and den.get(s, 0) > 0]
        if len(species) < 6:
            return {"status": "insufficient"}
        y = np.array([num[s] / den[s] for s in species])
        life = np.array([TRAITS[s][0] for s in species])
        mass = np.array([TRAITS[s][1] for s in species])
        res = fit(y, life, mass, vcv(species))
        out = {k: v for k, v in res.items() if not k.startswith("_")}
        out["_fig"] = (res["_Xl"], res["_y"], life, res["pgls_p_lifespan"])
        return out

    ret_pooled = pooled({s: float(v) for s, v in ret_num.items()},
                        {s: float(v) for s, v in ret_den.items()})
    dens_pooled = pooled({s: float(v) for s, v in dens_sites.items()},
                         {s: float(v) / 1000.0 for s, v in dens_len.items()})
    tested = [g["pgls_p_lifespan"] for g in per_gene_ret]
    return {
        "n_mirna_families": len(motifs),
        "retention": {"n_genes_tested": len(per_gene_ret), "fdr_survivors": bh_fdr(tested),
                      "per_gene": per_gene_ret, "pooled": ret_pooled},
        "density": {"pooled": dens_pooled},
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SEED_FILE.exists():
        print(f"Missing {SEED_FILE}. Download TargetScan miR_Family_Info.txt first.")
        return 1
    if not any(UTR_DIR.glob("*_utr3.fasta")):
        print(f"No 3' UTR FASTAs in {UTR_DIR}. Run scripts/fetch_lane_utr3.py first.")
        return 1

    res = run()
    figs = {"retention": res["retention"]["pooled"].pop("_fig", None),
            "density": res["density"]["pooled"].pop("_fig", None)}
    (OUT_DIR / "mirna_site_conservation.json").write_text(json.dumps(res, indent=2))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (label, fg) in zip(axes, figs.items(), strict=True):
        ax.set_xlabel("log10 max lifespan (yr)")
        ax.set_ylabel("miRNA-site retention" if label == "retention" else "sites per kb")
        if fg is None:
            ax.text(0.5, 0.5, "insufficient", ha="center", transform=ax.transAxes)
            continue
        Xl, y, life, p = fg
        ax.scatter(np.log10(life), y, s=40, c="#27ae60")
        b = np.polyfit(Xl, y, 1)
        xs = np.linspace(np.log10(life).min(), np.log10(life).max(), 50)
        ax.plot(xs, b[0] * ((xs - np.log10(life).mean()) / np.log10(life).std()) + b[1],
                c="grey", ls="--")
        ax.set_title(f"miRNA {label} vs lifespan\nPGLS p={p:.3f}", fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "mirna_site_conservation.png", dpi=140)

    r = res["retention"]
    print(f"miRNA families: {res['n_mirna_families']}")
    print(f"retention: genes tested={r['n_genes_tested']} FDR survivors={r['fdr_survivors']} "
          f"pooled PGLS p={r['pooled'].get('pgls_p_lifespan')} "
          f"beta={r['pooled'].get('pgls_beta_lifespan')}")
    print(f"density: pooled PGLS p={res['density']['pooled'].get('pgls_p_lifespan')} "
          f"beta={res['density']['pooled'].get('pgls_beta_lifespan')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
