#!/usr/bin/env python3
"""Positional map: where along the 3' UTR does the lifespan-linked conservation sit?

The cell-cycle 3' UTR conservation signal (docs/results/2026-08-05-cellcycle-expansion) is a
whole-UTR mean. This localises it *along* the UTR. For each gene, each species is aligned to
the human 3' UTR; every human position is scored 0 (conserved: same base) or 1 (divergent:
mismatch or gap). The human UTR is split into relative bins (proximal -> distal); per species,
per bin, divergence = mean position score in that bin. Then, pooled across the cell-cycle
module, each bin's per-species mean divergence is regressed on lifespan + mass (PGLS). A bin
whose divergence falls with lifespan (negative slope, small p) is where long-lived species
conserve most.

Outputs: docs/results/2026-08-05-utr-positional/utr_positional.{json,png}
No network, no Biohub credits.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
UTR_DIR = REPO / "data" / "interim" / "utr_panel"
NWK = REPO / "data" / "interim" / "phylo" / "timetree.nwk"
CACHE = UTR_DIR / "pos_cache"
OUT_DIR = REPO / "docs" / "results" / "2026-08-05-utr-positional"
NBINS = 8
REGION = "utr3"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


P = _load("analyze_panel_utr_divergence")
UTR = P.UTR


def per_bin_divergence(gene: str, traits: dict) -> dict[str, list[float]]:
    """{species: [divergence in each of NBINS human-position bins]} for a gene's 3' UTR."""
    ref_seq = P.human_ref(gene, REGION)
    if not ref_seq:
        return {}
    human = "".join(c for c in UTR._proximal(ref_seq, REGION).upper() if c in "ACGT")
    if len(human) < NBINS * 10:
        return {}
    edges = np.linspace(0, len(human), NBINS + 1).astype(int)
    seqs = UTR.load_fasta(UTR_DIR / f"{gene}_{REGION}.fasta")
    out: dict[str, list[float]] = {}
    h_seq = UTR.bseq.NucleotideSequence(human)
    for sp, raw in seqs.items():
        if sp == "human" or sp not in traits:
            continue
        s = "".join(c for c in UTR._proximal(raw, REGION).upper() if c in "ACGT")
        if len(s) < 20:
            continue
        aln = UTR.balign.align_optimal(
            h_seq, UTR.bseq.NucleotideSequence(s), UTR._MATRIX,
            gap_penalty=(-10, -1), terminal_penalty=False,
        )[0]
        score = np.full(len(human), np.nan)
        for h_idx, s_idx in aln.trace:
            if h_idx < 0:
                continue
            score[h_idx] = 0.0 if (s_idx >= 0 and human[h_idx] == s[s_idx]) else 1.0
        bins = []
        for b in range(NBINS):
            seg = score[edges[b]:edges[b + 1]]
            seg = seg[~np.isnan(seg)]
            bins.append(float(seg.mean()) if len(seg) else np.nan)
        out[sp] = bins
    return out


def main() -> int:
    if not NWK.exists() or not any(UTR_DIR.glob(f"*_{REGION}.fasta")):
        print("Missing panel UTRs or tree.")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    traits = P.load_traits()
    wanted = {s: sci for s, sci, _ in P.load_panel() if s in traits}
    tree = NWK.read_text()

    # accumulate per-species divergence per bin, pooled across the cell-cycle module
    per_species_bins: dict[str, list[list[float]]] = {}
    for gene in P.CELLCYCLE:
        cache = CACHE / f"{gene}.json"
        if cache.exists():
            data = json.loads(cache.read_text())
        else:
            data = per_bin_divergence(gene, traits)
            cache.write_text(json.dumps(data))
        for sp, bins in data.items():
            per_species_bins.setdefault(sp, []).append(bins)

    # per bin: per-species mean across genes, then PGLS on lifespan + mass
    profile = []
    for b in range(NBINS):
        vals = {}
        for sp, gene_bins in per_species_bins.items():
            xs = [gb[b] for gb in gene_bins if gb[b] == gb[b]]  # drop NaN
            if xs and sp in wanted:
                vals[sp] = float(np.mean(xs))
        sp = list(vals)
        if len(sp) < 8:
            profile.append({"bin": b, "status": "insufficient"})
            continue
        names, C = P.vcv_from_newick(tree, {s: wanted[s] for s in sp})
        y = np.array([vals[s] for s in names])
        life = np.array([traits[s][0] for s in names])
        mass = np.array([traits[s][1] for s in names])
        beta, p, pm, _ = P.fit(y, life, mass, C)
        profile.append({"bin": b, "rel_start": round(b / NBINS, 2),
                        "rel_end": round((b + 1) / NBINS, 2), "n": len(names),
                        "pgls_p_lifespan": round(p, 4), "pgls_beta_lifespan": round(beta, 5),
                        "direction": "conserve" if beta < 0 else "diverge"})

    summary = {"analysis": "cellcycle_3utr_positional_conservation", "region": REGION,
               "n_bins": NBINS, "genes": P.CELLCYCLE, "profile": profile}
    (OUT_DIR / "utr_positional.json").write_text(json.dumps(summary, indent=2))

    tested = [b for b in profile if "pgls_p_lifespan" in b]
    xs = [(b["rel_start"] + b["rel_end"]) / 2 for b in tested]
    slopes = [b["pgls_beta_lifespan"] for b in tested]
    logp = [-np.log10(max(b["pgls_p_lifespan"], 1e-6)) for b in tested]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    a1.bar(xs, slopes, width=0.9 / NBINS, color=["#c0392b" if s < 0 else "#7f8c8d" for s in slopes])
    a1.axhline(0, c="k", lw=0.6)
    a1.set_ylabel("PGLS lifespan slope\n(neg = conserve)")
    a1.set_title("Cell-cycle 3' UTR: where conservation tracks lifespan\n"
                 "(proximal = near stop codon, left)", fontsize=10)
    a2.bar(xs, logp, width=0.9 / NBINS, color="#2980b9")
    a2.axhline(-np.log10(0.05), c="grey", ls="--", lw=1)
    a2.set_ylabel("-log10 PGLS p")
    a2.set_xlabel("relative position along 3' UTR (0 = proximal/stop, 1 = distal/poly-A)")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "utr_positional.png", dpi=140)

    print(f"cell-cycle 3' UTR positional profile ({NBINS} bins, proximal -> distal):")
    for b in profile:
        if "pgls_p_lifespan" in b:
            print(f"  bin {b['bin']} ({b['rel_start']:.2f}-{b['rel_end']:.2f}): "
                  f"p={b['pgls_p_lifespan']} slope={b['pgls_beta_lifespan']:+.5f} {b['direction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
