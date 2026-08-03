# Results index — formal closure of broad interface-divergence screening as a standalone discovery method

**Status (2026-07-29): broad interface-divergence screening is formally closed as a standalone
discovery method.** Across two predicted pathways, two experimental designs, and three built-in
controls, the ESM interface-divergence metric produced **no FDR-surviving, cross-lineage longevity
signal**. An orthogonal selection metric (dN/dS) applied to the single recurring crumb agrees
(sub-FDR, and finds nothing itself), and a five-way battery of design/statistical rigor checks each
reproduces the null. The negative is **not** an artifact of design or statistics — it localizes to the
metric's molecular level: *L2 divergence of protein-language-model embeddings at coding interfaces is
not a detector of lineage-specific selection.* Screening more proteins with the same metric would not
change this.

Full argument with numbers: **[synthesis](2026-07-29-synthesis-negative-and-method-boundary/RESULT.md)**.

## Evidence

### Primary screens (all negative under FDR)

| Result | design | outcome |
|---|---|---|
| [SIRT6 5×4](2026-07-28-sirt6-panel-5x4-powered/) | DNA-repair panel, long-vs-short | 0/26 FDR |
| [AMPK 5×4](2026-07-28-ampk-module-5x4/) | energy-sensing control | 0/30 FDR; lead killed by NEGATOME |
| [SIRT6 stratified](2026-07-28-sirt6-convergent-divergent-stratified/) | ELLSM/BMAL/Reference | 0/25–29 FDR |
| [AMPK stratified](2026-07-28-ampk-convergent-divergent-stratified/) | ELLSM/BMAL/Reference | 0/25–29 FDR |
| [cell-cycle (BMAL-predicted)](2026-07-29-cell-cycle-panel/) | Peto's-paradox panel | 0/28 FDR; **direction inverted** (BMAL more conserved) |

### Orthogonal metric (selection, not embeddings)

| Result | method | outcome |
|---|---|---|
| [Ku80 / 8AG5 dN/dS](2026-07-29-ku80-interface-dnds-orthogonal/) | Nei–Gojobori, host–virus interface | 0/42 FDR; interface "elevation" is a **solvent-exposure** effect; crumb dies at FDR on dN/dS exactly as on ESM |

### Rigor battery — five ways the negative could have been an artifact, all ruled out

| Assumption checked | Result |
|---|---|
| [Binary groups + species non-independence](2026-07-29-phylo-continuous-reanalysis/) | continuous PGLS: lifespan **p = 0.96** |
| [Single panel / low power](2026-07-29-phylo-all-lanes/) | pooled **52 interfaces**: lifespan **p = 0.73** |
| Direction (constraint vs divergence) | neither: binomial **p = 0.21**, Wilcoxon **p = 0.36** |
| [Interface mean masks adaptive sites](2026-07-29-site-level/) | **0 / 5 618** interface residues survive FDR |
| [Charged vs uncharged pooling](2026-07-29-site-level-byclass/) | **0** in any residue class; classes ≈ equal in magnitude |

Phylogenetic correction *reduced* the one apparent hint (Ku80 dN/dS: raw p = 0.066 → 0.28) rather
than revealing one — the direction expected when relatedness was inflating an effect. Every rigor
upgrade sharpened the negative; none rescued a positive.

## Why this matters

This is a **well-characterised negative with a localized cause**, released openly alongside the
positive and indeterminate results. It demonstrates that a signal which looks real under a naive
whole-interface metric does not survive stronger controls, an orthogonal selection metric, or
phylogeny-aware and site-level analysis — and it pinpoints *why* (wrong molecular level, not absent
biology). The project's only positive leads (naked-mole-rat HAS2 functional-axis rescue; elephant
TP53 dosage) sit at a regulatory/dosage level this metric cannot see, which is what motivates changing
the **unit of analysis** rather than screening more proteins the same way.

## Reproducing

All analyses are scripted (`scripts/`) and regenerable; `data/` intermediates are gitignored.
Embeddings are cached under `data/output/embeddings/` and re-used without new model calls via
`scripts/filter_selection_to_cached.py`. Each result directory contains a `RESULT.md`, the
machine-readable outputs, and the figure.
