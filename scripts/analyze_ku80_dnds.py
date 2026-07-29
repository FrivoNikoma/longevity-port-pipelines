#!/usr/bin/env python3
"""Site-level Nei-Gojobori dN/dS on Ku80 (XRCC5), interface vs non-interface and
ELLSM vs reference contrast.

Orthogonal test for the ESM interface-divergence "crumb": Ku80/8ag5 was stably
ELLSM-ward on the ESM L2 metric but never survived FDR. Here we ask whether a
metric that measures *selection* (dN/dS) rather than embedding distance sees a
lineage-specific signal at the Ku80 surface that contacts the vaccinia C10
antagonist (chain B vs chain D in 8AG5).

Inputs (relative to repo root):
    data/interim/ku80/ku80_cds.fasta   (from scripts/fetch_ku80_cds.py)
    data/interim/pdb/8ag5.cif

Outputs:
    data/interim/ku80/ku80_codon_alignment.fasta
    data/interim/ku80/ku80_dnds_results.json
    data/interim/ku80/ku80_dnds_by_column.tsv
    docs/results/ku80_dnds.md  (written by a separate step)

Pure-Python engine: pyfamsa (MSA), Bio.PDB (structure), numpy/scipy (stats).
"""
from __future__ import annotations

import itertools
import json
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import false_discovery_control

warnings.simplefilter("ignore")

REPO = Path(__file__).resolve().parents[1]
CDS_FASTA = REPO / "data" / "interim" / "ku80" / "ku80_cds.fasta"
CIF = REPO / "data" / "interim" / "pdb" / "8ag5.cif"
OUT_DIR = REPO / "data" / "interim" / "ku80"
INTERFACE_CUTOFF = 8.0  # Angstrom
KU80_CHAIN = "B"
PARTNER_CHAINS = ("D",)      # vaccinia C10 copy paired with Ku80 chain B (pipeline B1--D1)
PARTNER_CHAINS_ALL = ("C", "D")
N_PERM = 2000
RNG = np.random.default_rng(20260729)

BASES = "TCAG"
CODONS = [a + b + c for a in BASES for b in BASES for c in BASES]
AA = ("FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG")
CODON2AA = dict(zip(CODONS, AA, strict=True))


def translate(nt: str) -> str:
    nt = nt.upper().replace("U", "T")
    return "".join(CODON2AA.get(nt[i : i + 3], "X") for i in range(0, len(nt) - 2, 3))


# --------------------------------------------------------------- load + align
def load_cds():
    seqs, meta, h = {}, {}, None
    for line in CDS_FASTA.read_text().splitlines():
        line = line.strip()
        if line.startswith(">"):
            h = line[1:]
            taxid, name, group, acc = h.split("|")
            meta[name] = {"taxid": int(taxid), "group": group, "acc": acc}
            seqs[name] = []
            _cur = name
        elif line:
            seqs[_cur].append(line)
    seqs = {k: "".join(v) for k, v in seqs.items()}
    return seqs, meta


def codon_align(seqs: dict[str, str]):
    """Protein MSA (pyfamsa) threaded back onto codons."""
    from pyfamsa import Aligner, Sequence

    codon_lists, prots = {}, {}
    for name, nt in seqs.items():
        codons = [nt[i : i + 3] for i in range(0, len(nt) - 2, 3)]
        prot = translate(nt)
        if prot.endswith("*"):
            prot, codons = prot[:-1], codons[:-1]
        codon_lists[name], prots[name] = codons, prot

    aln = Aligner(guide_tree="upgma").align(
        [Sequence(n.encode(), p.encode()) for n, p in prots.items()]
    )
    aligned_prot = {s.id.decode(): s.sequence.decode() for s in aln}

    codon_aln = {}
    for name, ap in aligned_prot.items():
        codons, out, ci = codon_lists[name], [], 0
        for a in ap:
            if a == "-":
                out.append("---")
            else:
                out.append(codons[ci])
                ci += 1
        codon_aln[name] = out
    ncol = len(next(iter(codon_aln.values())))
    return codon_aln, aligned_prot, ncol


# --------------------------------------------------------------- interface mask
def three_to_one(resname: str) -> str:
    m = {
        "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
        "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
        "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
        "TYR": "Y", "VAL": "V", "MSE": "M",
    }
    return m.get(resname, "X")


def interface_residues(partner_chains):
    from Bio.PDB import MMCIFParser, NeighborSearch

    model = next(iter(MMCIFParser(QUIET=True).get_structure("x", str(CIF))))
    partner_atoms = [a for ch in partner_chains if ch in model
                     for res in model[ch] if res.id[0] == " " for a in res]
    ns = NeighborSearch(partner_atoms)
    ku = model[KU80_CHAIN]
    iface, ku_seq, ku_nums = set(), [], []
    for res in ku:
        if res.id[0] != " ":
            continue
        num = res.id[1]
        ku_seq.append(three_to_one(res.get_resname()))
        ku_nums.append(num)
        for atom in res:
            if ns.search(atom.coord, INTERFACE_CUTOFF):
                iface.add(num)
                break
    return iface, "".join(ku_seq), ku_nums


# Tien et al. 2013 theoretical max ASA (A^2)
MAX_ASA = {
    "A": 129, "R": 274, "N": 195, "D": 193, "C": 167, "Q": 225, "E": 223,
    "G": 104, "H": 224, "I": 197, "L": 201, "K": 236, "M": 224, "F": 240,
    "P": 159, "S": 155, "T": 172, "W": 285, "Y": 263, "V": 174,
}


def surface_residues(rsa_cutoff: float = 0.20):
    """Auth residue numbers of Ku80 (chain B) that are solvent-exposed when the
    chain is considered in isolation (so interface residues also count as surface)."""
    from Bio.PDB import MMCIFParser
    from Bio.PDB.SASA import ShrakeRupley

    struct = MMCIFParser(QUIET=True).get_structure("x", str(CIF))
    model = next(iter(struct))
    for ch in list(model):
        if ch.id != KU80_CHAIN:
            model.detach_child(ch.id)
    ShrakeRupley().compute(model, level="R")
    surf = set()
    for res in model[KU80_CHAIN]:
        if res.id[0] != " ":
            continue
        aa = three_to_one(res.get_resname())
        if aa in MAX_ASA and res.sasa / MAX_ASA[aa] >= rsa_cutoff:
            surf.add(res.id[1])
    return surf


def map_auth_to_columns(ku_seq, ku_nums, human_aligned):
    """auth residue number -> alignment column, via aligning the structure Ku80
    sequence to the human aligned row."""
    from Bio.Align import PairwiseAligner

    human_ungapped, col_of = [], []
    for col, a in enumerate(human_aligned):
        if a != "-":
            human_ungapped.append(a)
            col_of.append(col)
    human_ungapped = "".join(human_ungapped)

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.open_gap_score = -10
    aligner.extend_gap_score = -0.5
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aln = aligner.align(ku_seq, human_ungapped)[0]
    # build map: struct index -> human ungapped index
    struct2hum = {}
    for (s0, s1), (h0, _h1) in zip(aln.aligned[0], aln.aligned[1], strict=False):
        for off in range(s1 - s0):
            struct2hum[s0 + off] = h0 + off
    auth2col = {}
    for si, num in enumerate(ku_nums):
        hi = struct2hum.get(si)
        if hi is not None and hi < len(col_of):
            auth2col[num] = col_of[hi]
    return auth2col


# --------------------------------------------------------------- Nei-Gojobori
def _syn_sites(codon: str) -> float:
    if codon not in CODON2AA or CODON2AA[codon] == "*":
        return np.nan
    aa = CODON2AA[codon]
    s = 0.0
    for i in range(3):
        for b in BASES:
            if b == codon[i]:
                continue
            mut = codon[:i] + b + codon[i + 1 :]
            if CODON2AA.get(mut) == "*":
                continue
            if CODON2AA.get(mut) == aa:
                s += 1.0 / 3.0
    return s


SYN_SITES = {c: _syn_sites(c) for c in CODONS}


def _diffs(c1: str, c2: str):
    """Return (Sd, Nd) between two codons averaging over mutational pathways."""
    if c1 == c2:
        return 0.0, 0.0
    pos = [i for i in range(3) if c1[i] != c2[i]]
    paths, sd_acc, nd_acc, npaths = list(itertools.permutations(pos)), 0.0, 0.0, 0
    for path in paths:
        cur, sd, nd, ok = c1, 0.0, 0.0, True
        for i in path:
            nxt = cur[:i] + c2[i] + cur[i + 1 :]
            if CODON2AA.get(nxt) == "*" or CODON2AA.get(cur) == "*":
                ok = False
                break
            if CODON2AA.get(nxt) == CODON2AA.get(cur):
                sd += 1
            else:
                nd += 1
            cur = nxt
        if ok:
            sd_acc += sd
            nd_acc += nd
            npaths += 1
    if npaths == 0:
        return np.nan, np.nan
    return sd_acc / npaths, nd_acc / npaths


def _pair_stats(c1: str, c2: str):
    """(Sd, Nd, S, N) for a species-vs-ref codon pair, or None if not countable."""
    if "-" in c1 or "-" in c2 or "N" in c1 or "N" in c2:
        return None
    if c1 not in CODON2AA or c2 not in CODON2AA:
        return None
    if CODON2AA[c1] == "*" or CODON2AA[c2] == "*":
        return None
    s1, s2 = SYN_SITES[c1], SYN_SITES[c2]
    if np.isnan(s1) or np.isnan(s2):
        return None
    sd, nd = _diffs(c1, c2)
    if np.isnan(sd):
        return None
    S = (s1 + s2) / 2.0
    return sd, nd, S, 3.0 - S


def build_matrices(codon_aln, species, core_cols, ref="human"):
    """Precompute Sd/Nd/S/N per (species, core-column) vs ref. NaN where uncountable."""
    ns, nc = len(species), len(core_cols)
    Sd = np.full((ns, nc), np.nan)
    Nd = np.full((ns, nc), np.nan)
    Ss = np.full((ns, nc), np.nan)
    Ns = np.full((ns, nc), np.nan)
    ref_cod = codon_aln[ref]
    for si, name in enumerate(species):
        sp = codon_aln[name]
        for ci, col in enumerate(core_cols):
            st = _pair_stats(ref_cod[col], sp[col])
            if st is not None:
                Sd[si, ci], Nd[si, ci], Ss[si, ci], Ns[si, ci] = st
    return Sd, Nd, Ss, Ns


def jc(p):
    if np.isnan(p) or p >= 0.75:
        return np.nan
    return -0.75 * np.log(1 - 4.0 / 3.0 * p)


def pooled(Sd, Nd, Ss, Ns, srows, ccols):
    """Pool precomputed stats over species rows and column indices -> dN/dS dict."""
    sl = np.ix_(srows, ccols)
    tSd = np.nansum(Sd[sl])
    tNd = np.nansum(Nd[sl])
    tSs = np.nansum(Ss[sl])
    tNs = np.nansum(Ns[sl])
    pS = tSd / tSs if tSs > 0 else np.nan
    pN = tNd / tNs if tNs > 0 else np.nan
    dS, dN = jc(pS), jc(pN)
    omega = (dN / dS) if (dS and dS > 0 and not np.isnan(dN)) else np.nan
    return {"pN": pN, "pS": pS, "dN": dN, "dS": dS, "omega": omega,
            "Nd": tNd, "Sd": tSd, "N_sites": tNs, "S_sites": tSs}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seqs, meta = load_cds()
    codon_aln, aligned_prot, ncol = codon_align(seqs)

    # save codon alignment
    with open(OUT_DIR / "ku80_codon_alignment.fasta", "w") as fh:
        for name, cod in codon_aln.items():
            g = meta[name]["group"]
            fh.write(f">{name}|{g}\n{''.join(cod)}\n")

    iface_auth, ku_seq, ku_nums = interface_residues(PARTNER_CHAINS)
    iface_auth_all, _, _ = interface_residues(PARTNER_CHAINS_ALL)
    auth2col = map_auth_to_columns(ku_seq, ku_nums, aligned_prot["human"])

    iface_cols = sorted({auth2col[n] for n in iface_auth if n in auth2col})
    iface_cols_all = sorted({auth2col[n] for n in iface_auth_all if n in auth2col})

    # eligible "core" columns: human non-gap AND >=60% sequences non-gap
    nseq = len(codon_aln)
    core_cols = []
    human_cod = codon_aln["human"]
    for col in range(ncol):
        if "-" in human_cod[col]:
            continue
        cov = sum(1 for n in codon_aln if "-" not in codon_aln[n][col])
        if cov >= 0.6 * nseq:
            core_cols.append(col)
    core_set = set(core_cols)
    iface_cols = [c for c in iface_cols if c in core_set]
    iface_cols_all = [c for c in iface_cols_all if c in core_set]
    noniface_cols = [c for c in core_cols if c not in set(iface_cols)]

    groups = {"ELLSM": [], "BMAL": [], "REFERENCE": []}
    for name, m in meta.items():
        if name == "human":
            continue
        groups[m["group"]].append(name)
    all_species = [n for n in codon_aln if n != "human"]

    # precompute NG stat matrices over core columns (species x core-column)
    Sd, Nd, Ss, Ns = build_matrices(codon_aln, all_species, core_cols)
    sp_idx = {n: i for i, n in enumerate(all_species)}
    col_idx = {c: i for i, c in enumerate(core_cols)}
    iface_ci = [col_idx[c] for c in iface_cols]
    noniface_ci = [col_idx[c] for c in noniface_cols]

    def rows(members):
        return [sp_idx[n] for n in members]

    # ---- pooled omega table: group x region
    table = {}
    for gname, members in {**groups, "ALL": all_species}.items():
        r = rows(members)
        table[gname] = {
            "interface": pooled(Sd, Nd, Ss, Ns, r, iface_ci),
            "non_interface": pooled(Sd, Nd, Ss, Ns, r, noniface_ci),
        }

    # ---- Test 1: interface enrichment (all species), permute column labels
    all_rows = rows(all_species)
    all_ci = list(range(len(core_cols)))

    def enrichment(rws, ici):
        oi = pooled(Sd, Nd, Ss, Ns, rws, ici)
        ncols = [c for c in all_ci if c not in set(ici)]
        ob = pooled(Sd, Nd, Ss, Ns, rws, ncols)
        if np.isnan(oi["omega"]) or np.isnan(ob["omega"]) or ob["omega"] == 0:
            return np.nan, oi, ob
        return oi["omega"] / ob["omega"], oi, ob

    obs_enr, oi_all, ob_all = enrichment(all_rows, iface_ci)
    k = len(iface_ci)
    perm = []
    for _ in range(N_PERM):
        samp = list(RNG.choice(all_ci, size=k, replace=False))
        e, _, _ = enrichment(all_rows, samp)
        if not np.isnan(e):
            perm.append(e)
    perm = np.array(perm)
    p_enr = (np.sum(perm >= obs_enr) + 1) / (len(perm) + 1) if not np.isnan(obs_enr) else np.nan

    # ---- Test 1b: interface vs SURFACE non-interface (controls for exposure)
    surf_auth = surface_residues()
    surf_cols = {auth2col[n] for n in surf_auth if n in auth2col} & core_set
    surf_noniface_ci = [col_idx[c] for c in surf_cols if c not in set(iface_cols)]
    surf_pool_ci = iface_ci + surf_noniface_ci

    def ratio_over(rws, ici, bg_ci, metric="omega"):
        oi = pooled(Sd, Nd, Ss, Ns, rws, ici)
        ob = pooled(Sd, Nd, Ss, Ns, rws, bg_ci)
        if ob[metric] and ob[metric] > 0 and not np.isnan(oi[metric]):
            return oi[metric] / ob[metric], oi, ob
        return np.nan, oi, ob

    obs_surf, oi_s, ob_s = ratio_over(all_rows, iface_ci, surf_noniface_ci)
    obs_surf_pN, _, _ = ratio_over(all_rows, iface_ci, surf_noniface_ci, "pN")
    perm_s = []
    for _ in range(N_PERM):
        samp = list(RNG.choice(surf_pool_ci, size=k, replace=False))
        bg = [c for c in surf_pool_ci if c not in set(samp)]
        r, _, _ = ratio_over(all_rows, samp, bg)
        if not np.isnan(r):
            perm_s.append(r)
    perm_s = np.array(perm_s)
    p_surf = (np.sum(perm_s >= obs_surf) + 1) / (len(perm_s) + 1) if not np.isnan(obs_surf) else np.nan

    # ---- Test 2: ELLSM vs REFERENCE at interface (pN), permute species labels
    def pN_rows(rws, ci):
        return pooled(Sd, Nd, Ss, Ns, rws, ci)["pN"]

    ell, ref = groups["ELLSM"], groups["REFERENCE"]
    ell_r, ref_r = rows(ell), rows(ref)
    obs_stat = pN_rows(ell_r, iface_ci) - pN_rows(ref_r, iface_ci)
    pool_r = ell_r + ref_r
    nell = len(ell_r)
    perm2 = []
    for _ in range(N_PERM):
        RNG.shuffle(pool_r)
        perm2.append(pN_rows(pool_r[:nell], iface_ci) - pN_rows(pool_r[nell:], iface_ci))
    perm2 = np.array(perm2)
    p_ellsm = (np.sum(np.abs(perm2) >= abs(obs_stat)) + 1) / (N_PERM + 1)

    # ---- per-column ELLSM-vs-REF (interface): pN diff + permutation p, BH-FDR
    percol = []
    for col in iface_cols:
        ci = [col_idx[col]]
        de = pN_rows(ell_r, ci)
        dr = pN_rows(ref_r, ci)
        stat = (0 if np.isnan(de) else de) - (0 if np.isnan(dr) else dr)
        cnt = 0
        for _ in range(1000):
            RNG.shuffle(pool_r)
            da = pN_rows(pool_r[:nell], ci)
            db = pN_rows(pool_r[nell:], ci)
            s = (0 if np.isnan(da) else da) - (0 if np.isnan(db) else db)
            if abs(s) >= abs(stat):
                cnt += 1
        pval = (cnt + 1) / 1001
        auth = next((n for n, c in auth2col.items() if c == col), None)
        percol.append({"column": col, "auth_residue": auth,
                       "pN_ELLSM": de, "pN_REF": dr, "diff": stat, "p": pval})
    if percol:
        qs = false_discovery_control([r["p"] for r in percol], method="bh")
        for r, q in zip(percol, qs, strict=True):
            r["q"] = float(q)

    results = {
        "n_species": len(all_species),
        "groups": {g: v for g, v in groups.items()},
        "n_alignment_columns": ncol,
        "n_core_columns": len(core_cols),
        "interface_residues_BD": sorted(iface_auth),
        "interface_residues_BCD": sorted(iface_auth_all),
        "n_interface_columns_BD": len(iface_cols),
        "n_interface_columns_BCD": len(iface_cols_all),
        "omega_table": table,
        "test1_interface_enrichment_vs_wholeprotein": {
            "observed_omega_ratio": obs_enr, "p_perm": p_enr,
            "omega_interface": oi_all["omega"], "omega_background": ob_all["omega"],
        },
        "test1b_interface_vs_surface": {
            "n_surface_noniface_columns": len(surf_noniface_ci),
            "observed_omega_ratio": obs_surf, "p_perm": p_surf,
            "observed_pN_ratio": obs_surf_pN,
            "omega_interface": oi_s["omega"], "omega_surface_bg": ob_s["omega"],
            "pN_interface": oi_s["pN"], "pN_surface_bg": ob_s["pN"],
        },
        "test2_ellsm_vs_ref_interface": {
            "obs_pN_diff": obs_stat, "p_perm": p_ellsm,
            "pN_ELLSM_iface": pN_rows(ell_r, iface_ci),
            "pN_REF_iface": pN_rows(ref_r, iface_ci),
        },
        "per_column_interface": percol,
        "n_columns_FDR_sig": int(sum(1 for r in percol if r.get("q", 1) < 0.05)),
    }

    (OUT_DIR / "ku80_dnds_results.json").write_text(json.dumps(results, indent=2, default=float))
    with open(OUT_DIR / "ku80_dnds_by_column.tsv", "w") as fh:
        fh.write("column\tauth_residue\tpN_ELLSM\tpN_REF\tdiff\tp\tq\n")
        for r in percol:
            fh.write(f"{r['column']}\t{r['auth_residue']}\t{r['pN_ELLSM']}\t"
                     f"{r['pN_REF']}\t{r['diff']}\t{r['p']}\t{r.get('q','')}\n")

    # ---- console summary
    print(f"species={len(all_species)}  columns={ncol}  core={len(core_cols)}")
    print(f"interface residues (B-D)={len(iface_auth)}  -> columns={len(iface_cols)}")
    print(f"interface residues (B-C/D)={len(iface_auth_all)} -> columns={len(iface_cols_all)}")
    print("\nomega (dN/dS), species-vs-human pooled:")
    print(f"{'group':10s} {'interface':>12s} {'non_iface':>12s}")
    for g in ("ELLSM", "BMAL", "REFERENCE", "ALL"):
        oi = table[g]["interface"]["omega"]
        on = table[g]["non_interface"]["omega"]
        print(f"{g:10s} {oi:12.4f} {on:12.4f}")
    print(f"\nTest1 interface vs whole-protein (ALL): omega ratio={obs_enr:.3f} p={p_enr:.4f}")
    print(f"   omega_iface={oi_all['omega']:.4f} omega_bg={ob_all['omega']:.4f}")
    print(f"Test1b interface vs SURFACE-noniface (n={len(surf_noniface_ci)}): "
          f"omega ratio={obs_surf:.3f} p={p_surf:.4f}  pN ratio={obs_surf_pN:.3f}")
    print(f"   omega_iface={oi_s['omega']:.4f} omega_surf_bg={ob_s['omega']:.4f}")
    print(f"Test2 ELLSM-vs-REF interface pN diff={obs_stat:+.5f} p={p_ellsm:.4f}")
    print(f"   pN_ELLSM_iface={pN_rows(ell_r, iface_ci):.5f} "
          f"pN_REF_iface={pN_rows(ref_r, iface_ci):.5f}")
    print(f"per-column interface FDR<0.05: {results['n_columns_FDR_sig']}/{len(percol)}")
    return results


if __name__ == "__main__":
    main()
