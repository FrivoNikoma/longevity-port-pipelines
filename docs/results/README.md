# Results index — a closed interface screen and a regulatory longevity signal

**Status (2026-08-05).** Two acts.

**(1) Broad interface-divergence screening is closed as a standalone discovery method.** Across
two predicted pathways, two experimental designs, three built-in controls, an orthogonal dN/dS
metric, and a five-way rigor battery, the ESM interface-divergence metric produced **no
FDR-surviving, cross-lineage longevity signal**. The negative is not an artifact of design or
statistics — it localizes to the metric's molecular level: *L2 divergence of protein-language-model
embeddings at coding interfaces is not a detector of lineage-specific selection.*

**(2) Moving the unit of analysis to the non-coding regulatory level surfaced the project's
first FDR-surviving longevity signal.** Across a 57-species mammalian panel with a dated
phylogeny, the **3' UTRs of cell-cycle genes are more conserved in long-lived species** — CDK4
and CDC20 survive FDR, 20 of 25 module genes conserve directionally, the signal sits in the
**proximal** 3' UTR, and it is **not** attributable to canonical miRNA target sites or AU-rich
elements. The interface null and this regulatory positive are the same lesson from both sides:
the lineage-specific longevity signal in these genes is regulatory / dosage-level, not
coding-interface-level.

---

## Act 1 — interface screening: a bounded negative

Full argument with numbers:
**[synthesis](2026-07-29-synthesis-negative-and-method-boundary/RESULT.md)**.

### Primary screens (all negative under FDR)

| Result | design | outcome |
|---|---|---|
| [SIRT6 5×4](2026-07-28-sirt6-panel-5x4-powered/) | DNA-repair panel, long-vs-short | 0/26 FDR |
| [AMPK 5×4](2026-07-28-ampk-module-5x4/) | energy-sensing control | 0/30 FDR; lead killed by NEGATOME |
| [SIRT6 stratified](2026-07-28-sirt6-convergent-divergent-stratified/) | ELLSM/BMAL/Reference | 0/25–29 FDR |
| [AMPK stratified](2026-07-28-ampk-convergent-divergent-stratified/) | ELLSM/BMAL/Reference | 0/25–29 FDR |
| [cell-cycle (BMAL-predicted)](2026-07-29-cell-cycle-panel/) | Peto's-paradox panel | 0/28 FDR; **direction inverted** |

### Orthogonal metric + rigor battery

| Check | Result |
|---|---|
| [Ku80 dN/dS](2026-07-29-ku80-interface-dnds-orthogonal/) | 0/42 FDR; interface "elevation" is a solvent-exposure effect |
| [Continuous PGLS](2026-07-29-phylo-continuous-reanalysis/) | lifespan **p = 0.96** |
| [Pooled 52 interfaces](2026-07-29-phylo-all-lanes/) | lifespan **p = 0.73** |
| [Site-level](2026-07-29-site-level/) | **0 / 5 618** residues survive FDR |
| [By residue class](2026-07-29-site-level-byclass/) | **0** in any class |

## Act 2 — regulatory level: an FDR-surviving signal

| Step | Result | outcome |
|---|---|---|
| Change the unit of analysis | [UTR divergence (classical + AI)](2026-08-04-utr3-regulatory-divergence/) | 3' UTR conservation trend appears (pooled p = 0.022); DNA-LM embeddings and Enformer expression are null; the signal is not in miRNA sites |
| Is the null real or underpowered? | [Power calibration + LQ](2026-08-05-power-calibration/) | detection floor \|r\| ≈ 0.57 at n = 22; the 3' UTR effect (\|r\| = 0.55) is **real but underpowered**, on the general lifespan axis |
| Add power (57 species, TimeTree) | [Extended panel](2026-08-05-extended-panel/) | **CDK4 p = 4e-5, CDC20 p = 0.003 survive FDR**; jackknife-robust; mass-independent |
| Two genes or a module? | [Cell-cycle expansion (25 genes)](2026-08-05-cellcycle-expansion/) | **20 / 25 genes conserve** (sign-test p = 0.004); pooled p = 0.016 — module-wide |
| Where along the UTR? | [Positional map](2026-08-05-utr-positional/) | **proximal** (first ~38 %, next to the stop codon; p ≤ 0.013), fading distally |
| Which element? | [Element enrichment](2026-08-05-utr-element-enrichment/) | **not** miRNA sites or AREs — diffuse across the proximal region |

## What this shows

The concrete finding is **stabilizing selection on the proximal 3' UTR of the cell-cycle /
tumour-suppressor module in long-lived mammals** — consistent with tighter cell-cycle control in
large, cancer-resistant species (Peto's paradox). It is a comparative-genomics correlation, not
a demonstrated mechanism, and the responsible proximal-3' UTR feature is not yet identified
(it is neither canonical miRNA sites nor AREs). But it is the project's first positive,
phylogenetically controlled, FDR-surviving regulatory signal, and it vindicates changing the
unit of analysis off the coding interface. The two AI arms (ESM protein embeddings; Nucleotide
Transformer DNA embeddings and Enformer expression) were each null — informative in bounding
where the signal is *not* (embedding-distance and predicted-expression space), and in showing
that classical sequence conservation, not embedding L2, is what detects it.

## Reproducing

All analyses are scripted (`scripts/`) and regenerable; `data/` intermediates are gitignored.
The extended-panel result pins its exact inputs (tree, traits, UTR sequences) under
[2026-08-05-extended-panel/inputs](2026-08-05-extended-panel/inputs/) for bit-reproducibility.
Each result directory contains a `RESULT.md`, the machine-readable outputs, and the figure.
