#!/usr/bin/env python3
"""Extended-panel 3'/5' UTR divergence vs longevity (real TimeTree phylogeny).

Powers up the one real signal (3' UTR conservation, |r|~0.55 at the n=22 detection edge) by
enlarging the species panel to ~60 mammals. Traits come from AnAge (maximum longevity, adult
weight) resolved by scientific name; the phylogeny is a real dated TimeTree tree (Newick) with
the phylogenetic covariance built from its branch lengths (Brownian: C[i,j] = root-to-MRCA
distance). Divergence per species is the Jukes-Cantor distance of a pairwise UTR alignment to
human, reusing scripts/analyze_utr3_divergence. PGLS on log10(lifespan)+log10(mass), two-sided,
BH-FDR across genes.

Inputs:
  data/config/species_panel_extended.tsv
  data/interim/phylo/anage/anage_data.txt      (AnAge dataset)
  data/interim/phylo/timetree.nwk              (TimeTree Newick for the panel)
  data/interim/utr_panel/{GENE}_utr3.fasta,_utr5.fasta
Outputs:
  docs/results/2026-08-05-extended-panel/panel_utr_divergence.{json,png}
No network, no Biohub credits.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import importlib.util
import json
import re
from pathlib import Path

import matplotlib
import numpy as np
from scipy.stats import binomtest
from scipy.stats import t as tdist

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
PANEL = REPO / "data" / "config" / "species_panel_extended.tsv"
ANAGE = REPO / "data" / "interim" / "phylo" / "anage" / "anage_data.txt"
NWK = REPO / "data" / "interim" / "phylo" / "timetree.nwk"
UTR_DIR = REPO / "data" / "interim" / "utr_panel"
HUMAN_DIR = REPO / "data" / "interim" / "utr"   # original fetch holds the human reference
OUT_DIR = REPO / "docs" / "results" / "2026-08-05-extended-panel"

# TimeTree label differs from the panel scientific name for a few species
TREE_ALIAS = {"Physeter macrocephalus": "Physeter catodon"}

# cell-cycle / tumour-suppressor module (for the --gene-set cellcycle focused test)
CELLCYCLE = [
    "RB1", "TP53", "CDK1", "CDK2", "CDK4", "CDK6", "ATM", "ATR", "CDC20",
    "E2F1", "TFDP1", "CCND1", "CCNE1", "CCNA2", "CCNB1", "CDKN1A", "CDKN1B",
    "CDKN2A", "MDM2", "MDM4", "CHEK1", "CHEK2", "WEE1", "CDC25A", "BUB1B",
]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


UTR = _load("analyze_utr3_divergence")  # jc_distance, load_fasta, MAX_ALN, _proximal

# AnAge scientific-name synonyms (panel name -> AnAge name)
SYN = {
    "Fukomys damarensis": "Cryptomys damarensis", "Papio anubis": "Papio hamadryas",
    "Chlorocebus sabaeus": "Chlorocebus aethiops", "Pongo abelii": "Pongo pygmaeus",
    "Canis lupus familiaris": "Canis familiaris", "Mustela putorius furo": "Mustela putorius",
    "Physeter catodon": "Physeter macrocephalus",
}
# hand-curated fallback for species AnAge lacks (short_name -> (lifespan_yr, mass_kg))
FALLBACK = {"blind_mole_rat": (21.0, 0.15)}


def load_panel() -> list[tuple[str, str, str]]:
    with open(PANEL, newline="") as fh:
        return [(r["short_name"], r["scientific_name"], r["clade"])
                for r in csv.DictReader(fh, delimiter="\t")]


def load_anage() -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    with open(ANAGE, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            sci = f"{r.get('Genus', '')} {r.get('Species', '')}".strip()
            life, wt = r.get("Maximum longevity (yrs)", ""), r.get("Adult weight (g)", "")
            if life and wt:
                with contextlib.suppress(ValueError):
                    out[sci] = (float(life), float(wt) / 1000.0)
    return out


def load_traits() -> dict[str, tuple[float, float]]:
    anage = load_anage()
    traits: dict[str, tuple[float, float]] = {}
    for short, sci, _clade in load_panel():
        val = anage.get(sci) or anage.get(SYN.get(sci, "")) or FALLBACK.get(short)
        if val:
            traits[short] = val
    return traits


# --------------------------------------------------------------- Newick -> covariance
class _Node:
    __slots__ = ("name", "length", "children", "parent")

    def __init__(self) -> None:
        self.name = ""
        self.length = 0.0
        self.children: list[_Node] = []
        self.parent: _Node | None = None


def parse_newick(text: str) -> _Node:
    text = text.strip().rstrip(";")
    pos = 0

    def parse() -> _Node:
        nonlocal pos
        node = _Node()
        if text[pos] == "(":
            pos += 1
            while True:
                child = parse()
                child.parent = node
                node.children.append(child)
                if text[pos] == ",":
                    pos += 1
                    continue
                if text[pos] == ")":
                    pos += 1
                    break
        # name
        m = re.match(r"[^,():;]+", text[pos:])
        if m:
            node.name = m.group(0)
            pos += len(node.name)
        # branch length
        if pos < len(text) and text[pos] == ":":
            pos += 1
            m = re.match(r"[-0-9.eE+]+", text[pos:])
            if m:
                node.length = float(m.group(0))
                pos += len(m.group(0))
        return node

    return parse()


def _norm(label: str) -> str:
    return re.sub(r"[^a-z]", "", label.lower())


def vcv_from_newick(text: str, wanted: dict[str, str]) -> tuple[list[str], np.ndarray]:
    """wanted: short_name -> scientific_name. Return (short_names_present, C)."""
    root = parse_newick(text)
    # depth (root-to-node distance) and leaf lookup by normalized label
    depth: dict[int, float] = {}
    leaves: dict[str, _Node] = {}

    def walk(n: _Node, d: float) -> None:
        depth[id(n)] = d
        if not n.children:
            leaves[_norm(n.name)] = n
        for c in n.children:
            walk(c, d + c.length)

    walk(root, 0.0)

    def ancestors(n: _Node) -> list[_Node]:
        chain = []
        while n is not None:
            chain.append(n)
            n = n.parent  # type: ignore[assignment]
        return chain

    def find_leaf(sci: str) -> _Node | None:
        for key in (_norm(sci), _norm(TREE_ALIAS.get(sci, ""))):
            if key and key in leaves:
                return leaves[key]
        return None

    present = [(s, n) for s, sci in wanted.items() if (n := find_leaf(sci)) is not None]
    names = [s for s, _ in present]
    nodes = [n for _, n in present]
    k = len(nodes)
    C = np.zeros((k, k))
    anc = [ancestors(n) for n in nodes]
    for i in range(k):
        for j in range(k):
            if i == j:
                C[i, j] = depth[id(nodes[i])]
            else:
                seti = {id(a) for a in anc[i]}
                mrca = next(a for a in anc[j] if id(a) in seti)
                C[i, j] = depth[id(mrca)]
    return names, C


# --------------------------------------------------------------- PGLS
def gls(y: np.ndarray, X: np.ndarray, C: np.ndarray):
    Cinv = np.linalg.inv(C)
    XtCi = X.T @ Cinv
    beta = np.linalg.solve(XtCi @ X, XtCi @ y)
    resid = y - X @ beta
    n, kk = X.shape
    covb = (float(resid.T @ Cinv @ resid) / (n - kk)) * np.linalg.inv(XtCi @ X)
    se = np.sqrt(np.diag(covb))
    return beta, 2 * tdist.sf(np.abs(beta / se), n - kk)


def fit(y, life, mass, C):
    Xl = (np.log10(life) - np.log10(life).mean()) / np.log10(life).std()
    Xm = (np.log10(mass) - np.log10(mass).mean()) / np.log10(mass).std()
    b, p = gls(y, np.column_stack([np.ones(len(y)), Xl, Xm]), C)
    return float(b[1]), float(p[1]), float(p[2]), Xl


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


def human_ref(gene: str, region: str) -> str | None:
    for base in (UTR_DIR, HUMAN_DIR):  # prefer reference embedded in the panel fasta
        fp = base / f"{gene}_{region}.fasta"
        if fp.exists():
            h = UTR.load_fasta(fp).get("human")
            if h:
                return h
    return None


DIV_CACHE = UTR_DIR / "div_cache"


def divergence(path: Path, region: str, traits: dict) -> dict[str, float]:
    gene = path.name.replace(f"_{region}.fasta", "")
    cache = DIV_CACHE / f"{gene}_{region}.json"
    if cache.exists():
        return {k: float(v) for k, v in json.loads(cache.read_text()).items() if k in traits}
    ref_seq = human_ref(gene, region)
    if not ref_seq:
        return {}
    ref = UTR._proximal(ref_seq, region)
    seqs = UTR.load_fasta(path)
    out = {}
    for sp, seq in seqs.items():
        if sp == "human" or sp not in traits:
            continue
        d = UTR.jc_distance(ref, UTR._proximal(seq, region))
        if not np.isnan(d):
            out[sp] = d
    DIV_CACHE.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out))
    return out


def run_region(region: str, traits: dict, wanted: dict, genes: set[str] | None = None) -> dict:
    per_gene, psum = [], {}
    for fp in sorted(UTR_DIR.glob(f"*_{region}.fasta")):
        gene = fp.name.replace(f"_{region}.fasta", "")
        if genes is not None and gene not in genes:
            continue
        div = divergence(fp, region, traits)
        sp = [s for s in div if s in wanted]
        if len(sp) >= 8:
            names, C = vcv_from_newick(NWK.read_text(), {s: wanted[s] for s in sp})
            y = np.array([div[s] for s in names])
            life = np.array([traits[s][0] for s in names])
            mass = np.array([traits[s][1] for s in names])
            b, p, pm, _ = fit(y, life, mass, C)
            per_gene.append({"gene": gene, "n": len(names), "pgls_p_lifespan": round(p, 4),
                             "pgls_beta_lifespan": round(b, 4),
                             "direction": "conserve" if b < 0 else "diverge"})
        for s in sp:
            psum.setdefault(s, []).append(div[s])
    sp = list(psum)
    pooled, fig = {"status": "insufficient"}, None
    if len(sp) >= 8:
        names, C = vcv_from_newick(NWK.read_text(), {s: wanted[s] for s in sp})
        y = np.array([float(np.mean(psum[s])) for s in names])
        life = np.array([traits[s][0] for s in names])
        mass = np.array([traits[s][1] for s in names])
        b, p, pm, Xl = fit(y, life, mass, C)
        r = float(np.corrcoef(y, Xl)[0, 1])
        pooled = {"n": len(names), "pgls_p_lifespan": round(p, 4),
                  "pgls_beta_lifespan": round(b, 4), "pgls_p_mass": round(pm, 4),
                  "marginal_r": round(r, 3)}
        fig = (life, y, p)
    ps = [g["pgls_p_lifespan"] for g in per_gene]
    cons = sum(1 for g in per_gene if g["pgls_beta_lifespan"] < 0)
    sign_p = float(binomtest(cons, len(per_gene), 0.5).pvalue) if per_gene else 1.0
    return {"region": region, "n_genes": len(per_gene), "fdr_survivors": bh(ps),
            "conserve": cons, "sign_test_p": round(sign_p, 4),
            "per_gene": per_gene, "pooled": pooled, "_fig": fig}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gene-set", choices=["all", "cellcycle"], default="all")
    ap.add_argument("--out-dir", default=str(OUT_DIR),
                    help="result directory (default: the extended-panel dir)")
    args = ap.parse_args()
    genes = set(CELLCYCLE) if args.gene_set == "cellcycle" else None
    out_dir = Path(args.out_dir)

    for need in (PANEL, ANAGE, NWK):
        if not need.exists():
            print(f"Missing {need}")
            return 1
    if not any(UTR_DIR.glob("*_utr3.fasta")):
        print(f"No panel UTRs in {UTR_DIR}. Run scripts/fetch_panel_utr.py first.")
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    traits = load_traits()
    wanted = {s: sci for s, sci, _ in load_panel() if s in traits}

    regions = {r: run_region(r, traits, wanted, genes) for r in ("utr3", "utr5")}
    summary = {
        "analysis": f"panel_utr_divergence_vs_longevity_{args.gene_set}",
        "gene_set": args.gene_set,
        "n_species_with_traits": len(traits),
        "phylogeny": "TimeTree (Newick), Brownian VCV from branch lengths",
        "regions": {r: {k: v for k, v in d.items() if not k.startswith("_")}
                    for r, d in regions.items()},
    }
    (out_dir / "panel_utr_divergence.json").write_text(json.dumps(summary, indent=2))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, region in zip(axes, ("utr3", "utr5"), strict=True):
        fg = regions[region]["_fig"]
        ax.set_xlabel("log10 max lifespan (yr)")
        ax.set_ylabel("mean JC distance to human")
        if fg is None:
            ax.text(0.5, 0.5, "insufficient", ha="center", transform=ax.transAxes)
            continue
        life, y, p = fg
        ax.scatter(np.log10(life), y, s=25, c="#16a085")
        ax.set_title(f"{region.upper()} pooled (n={regions[region]['pooled'].get('n')})\n"
                     f"PGLS p={p:.3f} FDR {regions[region]['fdr_survivors']}/"
                     f"{regions[region]['n_genes']}", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_dir / "panel_utr_divergence.png", dpi=140)

    for region, d in regions.items():
        pl = d["pooled"]
        print(f"== {region} ==  genes={d['n_genes']} FDR={d['fdr_survivors']} "
              f"conserve={d['conserve']}/{d['n_genes']} sign_p={d['sign_test_p']}  "
              f"pooled p={pl.get('pgls_p_lifespan')} beta={pl.get('pgls_beta_lifespan')} "
              f"r={pl.get('marginal_r')} n={pl.get('n')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
