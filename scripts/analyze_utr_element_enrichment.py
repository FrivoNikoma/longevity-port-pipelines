#!/usr/bin/env python3
"""Which element carries the proximal 3' UTR conservation: miRNA sites, AREs, or neither?

The cell-cycle 3' UTR conservation is proximal (docs/results/2026-08-05-utr-positional). This
asks *what* the conserved positions are. Every human 3' UTR position is classified as:
  * miRNA  - inside a canonical 7mer-m8 target site of a broadly conserved human miRNA family
             (TargetScan miR_Family_Info.txt);
  * ARE    - inside an AU-rich element core (ATTTA pentamer) and not a miRNA site;
  * background - neither.
Each species is aligned to the human UTR; per species, per class, divergence = mean
position mismatch/gap. Pooled across the cell-cycle module, each class' per-species mean
divergence is regressed on lifespan + mass (PGLS). The class whose divergence falls most
steeply with lifespan is the element long-lived species conserve.

Comparing miRNA, ARE and background side by side isolates which element type - if any - carries
the signal, rather than testing each in a vacuum.

Outputs: docs/results/2026-08-05-utr-element-enrichment/utr_element_enrichment.{json,png}
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
CACHE = UTR_DIR / "elem_cache"
OUT_DIR = REPO / "docs" / "results" / "2026-08-05-utr-element-enrichment"
REGION = "utr3"
ARE = "ATTTA"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


P = _load("analyze_panel_utr_divergence")
M = _load("analyze_mirna_site_conservation")
UTR = P.UTR
MOTIFS = M.load_seeds(M.SEED_FILE)


def classify_positions(human: str) -> np.ndarray:
    """0 = background, 1 = miRNA site, 2 = ARE (ATTTA, non-miRNA)."""
    cls = np.zeros(len(human), dtype=np.int8)
    for st in M.find_sites(human, MOTIFS):
        cls[st:st + 7] = 1
    i = human.find(ARE)
    while i != -1:
        for k in range(i, i + len(ARE)):
            if cls[k] == 0:
                cls[k] = 2
        i = human.find(ARE, i + 1)
    return cls


def per_class_divergence(gene: str, traits: dict) -> dict[str, list[float]]:
    """{species: [div_background, div_miRNA, div_ARE]} for a gene's 3' UTR."""
    ref = P.human_ref(gene, REGION)
    if not ref:
        return {}
    human = "".join(c for c in UTR._proximal(ref, REGION).upper() if c in "ACGT")
    if len(human) < 60:
        return {}
    cls = classify_positions(human)
    h_seq = UTR.bseq.NucleotideSequence(human)
    seqs = UTR.load_fasta(UTR_DIR / f"{gene}_{REGION}.fasta")
    out: dict[str, list[float]] = {}
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
        row = []
        for c in (0, 1, 2):
            seg = score[cls == c]
            seg = seg[~np.isnan(seg)]
            row.append(float(seg.mean()) if len(seg) >= 5 else np.nan)
        out[sp] = row
    return out


def main() -> int:
    if not NWK.exists() or not M.SEED_FILE.exists():
        print("Missing tree or TargetScan seeds.")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    traits = P.load_traits()
    wanted = {s: sci for s, sci, _ in P.load_panel() if s in traits}
    tree = NWK.read_text()

    per_species: dict[str, list[list[float]]] = {}
    for gene in P.CELLCYCLE:
        cache = CACHE / f"{gene}.json"
        data = json.loads(cache.read_text()) if cache.exists() else per_class_divergence(gene, traits)
        if not cache.exists():
            cache.write_text(json.dumps(data))
        for sp, row in data.items():
            per_species.setdefault(sp, []).append(row)

    labels = ["background", "miRNA_site", "ARE"]
    classes = []
    figdata = []
    for c, lab in enumerate(labels):
        vals = {}
        for sp, rows in per_species.items():
            xs = [r[c] for r in rows if r[c] == r[c]]
            if xs and sp in wanted:
                vals[sp] = float(np.mean(xs))
        sp = list(vals)
        names, C = P.vcv_from_newick(tree, {s: wanted[s] for s in sp})
        y = np.array([vals[s] for s in names])
        life = np.array([traits[s][0] for s in names])
        mass = np.array([traits[s][1] for s in names])
        beta, p, pm, Xl = P.fit(y, life, mass, C)
        r = float(np.corrcoef(y, Xl)[0, 1])
        classes.append({"class": lab, "n_species": len(names),
                        "pgls_p_lifespan": round(p, 4), "pgls_beta_lifespan": round(beta, 5),
                        "marginal_r": round(r, 3),
                        "direction": "conserve" if beta < 0 else "diverge"})
        figdata.append((lab, beta, p))

    summary = {"analysis": "cellcycle_3utr_element_enrichment", "region": REGION,
               "n_mirna_families": len(MOTIFS), "genes": P.CELLCYCLE, "classes": classes}
    (OUT_DIR / "utr_element_enrichment.json").write_text(json.dumps(summary, indent=2))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    labs = [f[0] for f in figdata]
    a1.bar(labs, [f[1] for f in figdata],
           color=["#7f8c8d", "#c0392b", "#e67e22"])
    a1.axhline(0, c="k", lw=0.6)
    a1.set_ylabel("PGLS lifespan slope (neg = conserve)")
    a1.set_title("Conservation-lifespan slope by element", fontsize=10)
    a2.bar(labs, [-np.log10(max(f[2], 1e-6)) for f in figdata],
           color=["#7f8c8d", "#c0392b", "#e67e22"])
    a2.axhline(-np.log10(0.05), c="grey", ls="--", lw=1)
    a2.set_ylabel("-log10 PGLS p")
    a2.set_title("Significance by element", fontsize=10)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "utr_element_enrichment.png", dpi=140)

    print(f"miRNA families: {len(MOTIFS)}")
    for c in classes:
        print(f"  {c['class']:11s} n={c['n_species']} p={c['pgls_p_lifespan']} "
              f"slope={c['pgls_beta_lifespan']:+.5f} r={c['marginal_r']:+.3f} {c['direction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
