#!/usr/bin/env python3
"""Is the proximal 3' UTR conservation structural? Paired vs unpaired positions.

The cell-cycle 3' UTR conservation is proximal
(docs/results/2026-08-05-utr-positional) and sits on neither miRNA target sites nor AREs
(docs/results/2026-08-05-utr-element-enrichment) - it is diffuse across the proximal region.
RNA secondary structure is the leading remaining candidate for a constraint that is spread
over a region rather than concentrated on a motif: base pairing constrains many positions at
once, and it tolerates substitution as long as the pairing survives.

**The statistic is internally normalised, on purpose.** A naive "how much structure is
conserved" score would rise and fall with overall sequence divergence and would simply
re-measure the Jukes-Cantor distance - exactly the circularity that sank the embedding metric
(docs/results/2026-08-06-utr-embedding-panel). So the primary quantity is a *within-sequence
contrast*:

    delta = divergence(unpaired positions) - divergence(paired positions)

Positive delta means paired positions are better conserved than unpaired ones in the same UTR,
i.e. selection is tracking the structure. The question of this layer is whether that gap widens
with lifespan. Because overall substitution rate cancels in the difference, delta cannot track
JC by construction.

Second statistic, the classical signature of structural constraint: among human base pairs
where a substitution occurred, the fraction that still form a valid pair (Watson-Crick or GU) -
a compensatory / consistent-substitution rate.

Controls
    shuffled   the paired mask is permuted, preserving the number of paired positions but
               destroying their placement; the delta must vanish
    vs JC      the same head-to-head partial PGLS used in the embedding layer
    utr5       region control
    bpp        pairing taken from partition-function base-pair probabilities at a threshold,
               not only from the single MFE structure

Statistics are the project standard, unchanged: PGLS on log10(lifespan) + log10(mass) with the
TimeTree Brownian covariance, two-sided, BH-FDR across genes, plus a pooled per-species-mean fit.

Needs ViennaRNA (not a project dependency, no network)::

    uv run --with ViennaRNA python scripts/analyze_utr_structure_conservation.py

Inputs:  data/interim/utr_panel/{GENE}_{region}.fasta (+ human reference)
Outputs: docs/results/2026-08-07-utr-constraint-nature/utr_structure_conservation.{json,png}
Cache:   data/interim/utr_panel/struct_cache/{GENE}_{region}.json  (per-species position stats)
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
from scipy.stats import binomtest

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
UTR_DIR = REPO / "data" / "interim" / "utr_panel"
CACHE = UTR_DIR / "struct_cache"
OUT_DIR = REPO / "docs" / "results" / "2026-08-07-utr-constraint-nature"

PROXIMAL_FRAC = 0.38  # the window the positional map localised the signal to
MIN_WIN = 60
MAX_WIN = 1200  # bounds the O(n^3) fold and the O(n*m) alignment
MIN_PAIRED = 10  # a species needs this many usable paired positions to contribute
VALID_PAIRS = {("A", "T"), ("T", "A"), ("G", "C"), ("C", "G"), ("G", "T"), ("T", "G")}
_MATRIX = balign.SubstitutionMatrix.std_nucleotide_matrix()
_NUC = set("ACGT")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


PANEL = _load("analyze_panel_utr_divergence")  # traits, TimeTree VCV, PGLS, BH, CELLCYCLE


def clean(seq: str) -> str:
    return "".join(c for c in seq.upper().replace("U", "T") if c in _NUC)


def window(seq: str, region: str, frac: float) -> str:
    """The stop-proximal (3' UTR) or start-proximal (5' UTR) fraction of a UTR."""
    cut = min(MAX_WIN, max(MIN_WIN, int(round(len(seq) * frac))))
    return seq[:cut] if region == "utr3" else seq[-cut:]


def fold_pairs(seq: str, bpp_threshold: float = 0.0,
               max_span: int = 0) -> tuple[list[tuple[int, int]], str]:
    """Base pairs of the human window: MFE structure, or partition-function bpp if asked.

    ``max_span`` bounds how far apart two paired bases may be. Global MFE folding of a
    kilobase-scale mRNA window is not reliable - long-range pairs in the prediction are mostly
    artifacts - so a local fold (the RNAplfold convention, span ~100-200 nt) is the honest
    default for this question. 0 keeps the unrestricted global fold, for comparison.
    """
    import RNA  # noqa: PLC0415  (heavy, non-project dependency)

    rna = seq.replace("T", "U")
    if max_span > 0:
        md = RNA.md()
        md.max_bp_span = max_span
        fc = RNA.fold_compound(rna, md)
    else:
        fc = RNA.fold_compound(rna)
    structure, mfe = fc.mfe()
    if bpp_threshold <= 0.0:
        stack: list[int] = []
        pairs: list[tuple[int, int]] = []
        for i, ch in enumerate(structure):
            if ch == "(":
                stack.append(i)
            elif ch == ")" and stack:
                pairs.append((stack.pop(), i))
        return pairs, structure
    fc.exp_params_rescale(mfe)
    fc.pf()
    bppm = fc.bpp()
    pairs = [
        (i - 1, j - 1)
        for i in range(1, len(rna) + 1)
        for j in range(i + 1, len(rna) + 1)
        if bppm[i][j] >= bpp_threshold
    ]
    return pairs, structure


def align_to_human(ref: str, query: str) -> list[str | None]:
    """For each human window position, the aligned species base (None where gapped)."""
    a, b = clean(ref), clean(query)
    if len(a) < MIN_WIN or len(b) < 20:
        return []
    aln = balign.align_optimal(
        bseq.NucleotideSequence(a), bseq.NucleotideSequence(b),
        _MATRIX, gap_penalty=(-10, -1), terminal_penalty=False,
    )[0]
    out: list[str | None] = [None] * len(a)
    for hi, si in aln.trace:
        if hi >= 0:
            out[hi] = b[si] if si >= 0 else None
    return out


def gene_stats(gene: str, region: str, frac: float, bpp: float, max_span: int,
               seed: int = 0) -> dict[str, dict]:
    """Per-species paired/unpaired divergence and compensatory rate for one gene."""
    fasta = UTR_DIR / f"{gene}_{region}.fasta"
    href = PANEL.human_ref(gene, region)
    if not fasta.exists() or not href:
        return {}
    ref = clean(window(href, region, frac))
    if len(ref) < MIN_WIN:
        return {}
    pairs, structure = fold_pairs(ref, bpp, max_span)
    n = len(ref)
    paired = np.zeros(n, dtype=bool)
    for i, j in pairs:
        if i < n and j < n:
            paired[i] = paired[j] = True
    if paired.sum() < MIN_PAIRED or (~paired).sum() < MIN_PAIRED:
        return {}

    rng = np.random.default_rng(seed)
    shuffled = rng.permutation(paired)  # same count of paired positions, placement destroyed

    seqs = PANEL.UTR.load_fasta(fasta)
    out: dict[str, dict] = {}
    for sp, raw in seqs.items():
        if sp == "human":
            continue
        aligned = align_to_human(ref, window(raw, region, frac))
        if not aligned:
            continue
        div = np.array([1.0 if (b is None or b != ref[k]) else 0.0
                        for k, b in enumerate(aligned)])
        usable = np.array([b is not None for b in aligned])
        pu, uu = paired & usable, (~paired) & usable
        if pu.sum() < MIN_PAIRED or uu.sum() < MIN_PAIRED:
            continue
        su, nu = shuffled & usable, (~shuffled) & usable

        n_sub = n_valid = 0
        for i, j in pairs:
            if i >= n or j >= n:
                continue
            bi, bj = aligned[i], aligned[j]
            if bi is None or bj is None:
                continue
            if bi == ref[i] and bj == ref[j]:
                continue
            n_sub += 1
            if (bi, bj) in VALID_PAIRS:
                n_valid += 1

        out[sp] = {
            "div_paired": float(div[pu].mean()),
            "div_unpaired": float(div[uu].mean()),
            "delta": float(div[uu].mean() - div[pu].mean()),
            "delta_shuffled": float(div[nu].mean() - div[su].mean())
            if su.sum() >= MIN_PAIRED and nu.sum() >= MIN_PAIRED else None,
            "comp_rate": (n_valid / n_sub) if n_sub >= 5 else None,
            "n_paired": int(pu.sum()), "n_unpaired": int(uu.sum()), "n_sub_pairs": n_sub,
        }
    return {"_meta": {"n": n, "n_paired": int(paired.sum()), "structure": structure}, **out}


def cached_stats(gene: str, region: str, frac: float, bpp: float, max_span: int,
                 force: bool) -> dict:
    tag = f"{gene}_{region}_f{int(frac * 100)}_b{int(bpp * 100)}_s{max_span}"
    fp = CACHE / f"{tag}.json"
    if fp.exists() and not force:
        return json.loads(fp.read_text())
    stats = gene_stats(gene, region, frac, bpp, max_span)
    CACHE.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(stats))
    return stats


def run(metric: str, region: str, genes: list[str], traits: dict, wanted: dict,
        frac: float, bpp: float, max_span: int, force: bool) -> dict:
    """PGLS of one per-species statistic on lifespan + mass, gene by gene and pooled."""
    nwk = PANEL.NWK.read_text()
    per_gene: list[dict] = []
    psum: dict[str, list[float]] = {}
    for gene in genes:
        stats = cached_stats(gene, region, frac, bpp, max_span, force)
        vals = {s: d[metric] for s, d in stats.items()
                if s != "_meta" and d.get(metric) is not None and s in traits and s in wanted}
        sp = list(vals)
        if len(sp) < 8:
            continue
        names, cov = PANEL.vcv_from_newick(nwk, {s: wanted[s] for s in sp})
        y = np.array([vals[s] for s in names])
        if y.std() == 0:
            continue
        life = np.array([traits[s][0] for s in names])
        mass = np.array([traits[s][1] for s in names])
        b, p, _pm, _ = PANEL.fit(y, life, mass, cov)
        per_gene.append({"gene": gene, "n": len(names), "pgls_p_lifespan": round(p, 4),
                         "pgls_beta_lifespan": round(b, 4),
                         "direction": "structure-conserving" if b > 0 else "structure-eroding",
                         "mean": round(float(y.mean()), 4)})
        for s, v in zip(names, y, strict=True):
            psum.setdefault(s, []).append(float(v))

    sp = list(psum)
    pooled: dict = {"status": "insufficient"}
    fig = None
    if len(sp) >= 8:
        names, cov = PANEL.vcv_from_newick(nwk, {s: wanted[s] for s in sp})
        y = np.array([float(np.mean(psum[s])) for s in names])
        life = np.array([traits[s][0] for s in names])
        mass = np.array([traits[s][1] for s in names])
        b, p, pm, xl = PANEL.fit(y, life, mass, cov)
        pooled = {"n": len(names), "pgls_p_lifespan": round(p, 4),
                  "pgls_beta_lifespan": round(b, 4), "pgls_p_mass": round(pm, 4),
                  "marginal_r": round(float(np.corrcoef(y, xl)[0, 1]), 3),
                  "mean": round(float(y.mean()), 4)}
        fig = (life, y, p)

    ps = [g["pgls_p_lifespan"] for g in per_gene]
    pos = sum(1 for g in per_gene if g["pgls_beta_lifespan"] > 0)
    sign_p = float(binomtest(pos, len(per_gene), 0.5).pvalue) if per_gene else 1.0
    return {"metric": metric, "region": region, "n_genes": len(per_gene),
            "fdr_survivors": PANEL.bh(ps), "positive_slope": pos,
            "sign_test_p": round(sign_p, 4), "per_gene": per_gene, "pooled": pooled,
            "_fig": fig}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gene-set", choices=["all", "cellcycle"], default="cellcycle")
    ap.add_argument("--regions", default="utr3")
    ap.add_argument("--proximal-frac", type=float, default=PROXIMAL_FRAC)
    ap.add_argument("--bpp", type=float, default=0.0,
                    help="pair threshold from the partition function (0 = use MFE structure)")
    ap.add_argument("--max-span", type=int, default=150,
                    help="max base-pair span for local folding (0 = global MFE)")
    ap.add_argument("--force", action="store_true", help="ignore the alignment/fold cache")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    for need in (PANEL.PANEL, PANEL.ANAGE, PANEL.NWK):
        if not need.exists():
            print(f"Missing {need}")
            return 1
    traits = PANEL.load_traits()
    wanted = {s: sci for s, sci, _ in PANEL.load_panel() if s in traits}
    all_genes = sorted({f.name.split("_utr")[0] for f in UTR_DIR.glob("*_utr3.fasta")})
    genes = [g for g in all_genes if args.gene_set == "all" or g in set(PANEL.CELLCYCLE)]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, dict] = {}
    for region in [r.strip() for r in args.regions.split(",") if r.strip()]:
        for metric in ("delta", "delta_shuffled", "comp_rate", "div_paired", "div_unpaired"):
            results[f"{region}|{metric}"] = run(metric, region, genes, traits, wanted,
                                                args.proximal_frac, args.bpp, args.max_span,
                                                args.force)

    summary = {
        "analysis": "utr_structure_conservation_vs_longevity",
        "gene_set": args.gene_set,
        "proximal_frac": args.proximal_frac,
        "pairing": ("MFE structure" if args.bpp <= 0 else f"bpp >= {args.bpp}")
                   + (f", local fold max_bp_span={args.max_span}" if args.max_span > 0
                      else ", global fold"),
        "primary": "utr3|delta",
        "note": ("delta = divergence(unpaired) - divergence(paired), a within-sequence "
                 "contrast; positive slope on lifespan = structure-tracking constraint "
                 "strengthens in long-lived species"),
        "n_species_with_traits": len(traits),
        "results": {k: {kk: vv for kk, vv in d.items() if not kk.startswith("_")}
                    for k, d in results.items()},
    }
    (out_dir / "utr_structure_conservation.json").write_text(json.dumps(summary, indent=2))

    cells = [k for k in results if k.endswith("|delta") or k.endswith("|delta_shuffled")]
    fig, axes = plt.subplots(1, len(cells), figsize=(6 * len(cells), 5), squeeze=False)
    for ax, key in zip(axes[0], cells, strict=True):
        d = results[key]
        ax.set_xlabel("log10 max lifespan (yr)")
        ax.set_ylabel("unpaired - paired divergence")
        ax.axhline(0, color="#999", lw=0.8, ls="--")
        if d["_fig"] is None:
            ax.text(0.5, 0.5, "insufficient", ha="center", transform=ax.transAxes)
            continue
        life, y, p = d["_fig"]
        ax.scatter(np.log10(life), y, s=25, c="#c0392b")
        ax.set_title(f"{key} (n={d['pooled'].get('n')})\nPGLS p={p:.3f}  "
                     f"FDR {d['fdr_survivors']}/{d['n_genes']}", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_dir / "utr_structure_conservation.png", dpi=140)

    for key, d in results.items():
        pl = d["pooled"]
        print(f"== {key:22s} genes={d['n_genes']:2d} FDR={d['fdr_survivors']} "
              f"pos={d['positive_slope']}/{d['n_genes']} sign_p={d['sign_test_p']}  "
              f"pooled p={pl.get('pgls_p_lifespan')} beta={pl.get('pgls_beta_lifespan')} "
              f"mean={pl.get('mean')} n={pl.get('n')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
