# Pinned inputs for the extended-panel result (CDK4 / CDC20 3' UTR conservation)

`data/interim/` is gitignored, so the sequences, tree and traits that produced
`../panel_utr_divergence.{json,png}` are not otherwise in the repo. This folder pins the
**exact inputs** so the FDR-surviving hits are bit-reproducible, independent of later NCBI /
AnAge / TimeTree updates.

Contents:
- `timetree.nwk` — the exact dated TimeTree tree used (Newick, branch lengths).
- `traits.tsv` — the exact AnAge-derived max lifespan (yr) and adult mass (kg) per species.
- `utr/{GENE}_utr3.fasta`, `utr/{GENE}_utr5.fasta` — the exact UTR sequences for the 15 genes,
  including the `human` reference record (headers `>{taxid}|{short_name}|{clade}`).

The pipeline is deterministic: identical inputs give identical numbers. Verified — from these
pinned inputs, CDK4 3' UTR PGLS **p = 0.000015** and CDC20 **p = 0.003176**, matching the
published JSON exactly.

## Reproduce a hit from the pin (self-contained)

```python
import importlib.util, csv, numpy as np, pathlib
spec = importlib.util.spec_from_file_location("m", "scripts/analyze_panel_utr_divergence.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
UTR = m.UTR
PIN = pathlib.Path("docs/results/2026-08-05-extended-panel/inputs")

traits, wanted = {}, {}
for r in csv.DictReader(open(PIN / "traits.tsv"), delimiter="\t"):
    traits[r["short_name"]] = (float(r["max_lifespan_yr"]), float(r["adult_mass_kg"]))
    wanted[r["short_name"]] = r["scientific_name"]
tree = (PIN / "timetree.nwk").read_text()

def pgls_gene(gene):
    seqs = UTR.load_fasta(PIN / "utr" / f"{gene}_utr3.fasta")
    ref = UTR._proximal(seqs["human"], "utr3")
    div = {sp: UTR.jc_distance(ref, UTR._proximal(seq, "utr3"))
           for sp, seq in seqs.items() if sp != "human" and sp in traits}
    div = {k: v for k, v in div.items() if not np.isnan(v)}
    names, C = m.vcv_from_newick(tree, {s: wanted[s] for s in div})
    y = np.array([div[s] for s in names])
    life = np.array([traits[s][0] for s in names]); mass = np.array([traits[s][1] for s in names])
    _, p, _, _ = m.fit(y, life, mass, C)
    return p, len(names)

print("CDK4 ", pgls_gene("CDK4"))    # -> ~1.5e-5
print("CDC20", pgls_gene("CDC20"))   # -> ~3.2e-3
```

To reproduce the full run, copy `utr/*` into `data/interim/utr_panel/` and `timetree.nwk` into
`data/interim/phylo/`, then `uv run python scripts/analyze_panel_utr_divergence.py`.
