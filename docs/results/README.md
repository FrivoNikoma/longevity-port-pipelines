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
| Can an AI metric see it? | [Embedding panel re-test](2026-08-06-utr-embedding-panel/) | re-tested at n = 57 with a 3'UTR-domain model: embedding distance **adds nothing beyond the alignment** (`emb given JC` ns in all 16 cells) and misses both FDR survivors; the old n = 22 AI null was largely a **power** artifact |
| What *kind* of constraint is it? | [Constraint nature](2026-08-07-utr-constraint-nature/) | not secondary structure (delta p = 0.14, with the method shown to detect structure at Wilcoxon p = 5e-4); the proximal localisation is carried by **indels, not substitutions** — proximal indel p = 0.0003 vs substitution p = 0.15, robust to UTR-length mismatch (p = 0.0009) and to gene/clade jackknives |
| Or is it just a slower mutation clock? | [Intron neutral control](2026-08-08-intron-neutral-control/) | no: intronic windows of the same genes are **flat** (slope −0.004, 95 % CI [−0.022, +0.014], p = 0.65) and the interval **excludes** the 3' UTR slope (−0.033), so the null is real rather than underpowered; the weak generation-time trend that does exist sits in intronic *substitutions* (p = 0.087) |

## What this shows

The concrete finding is **stabilizing selection on the proximal 3' UTR of the cell-cycle /
tumour-suppressor module in long-lived mammals** — consistent with tighter cell-cycle control in
large, cancer-resistant species (Peto's paradox). It is a comparative-genomics correlation, not
a demonstrated mechanism. But it is the project's first positive, phylogenetically controlled,
FDR-surviving regulatory signal, and it vindicates changing the unit of analysis off the coding
interface.

The [constraint-nature layer](2026-08-07-utr-constraint-nature/) then identifies what the
proximal component of that signal *is*. Three composition hypotheses failed in a row — miRNA
sites, AREs, secondary structure — and the reason is that the proximal signal is not a
substitution signal at all. Separating gaps from mismatches on the same alignments shows the
localisation is carried by **indels** (proximal indel p = 0.0003; proximal substitution
p = 0.15). Long-lived mammals carry fewer insertions and deletions in the stop-proximal
3' UTR: the constraint is on UTR architecture — the length and spacing of the proximal region —
rather than on which bases occupy it. This refines the positional map rather than overturning
it; that result reproduces exactly here, but its per-position score counted a gap as a
mismatch, so it could not separate the two classes of event.

The obvious alternative — that long-lived mammals simply accumulate indels more slowly
everywhere, given their longer generation times — is rejected by an
[external neutral control](2026-08-08-intron-neutral-control/): intronic windows from the same
genes are flat, and their confidence interval excludes the 3' UTR slope, so the deficit is
regional rather than genome-wide.

The AI arms (ESM protein embeddings; Nucleotide Transformer DNA embeddings; Enformer expression)
were each null, and the [embedding panel re-test](2026-08-06-utr-embedding-panel/) sharpens what
that null means. Re-run at n = 57 with a proximal window and a 3'UTR-pretrained model, the
embedding metric reaches nominal significance — so "embeddings are blind to lineage-specific
selection" was too strong, and the earlier null was substantially a power artifact. But the
metric adds **nothing beyond the alignment** in any cell of the grid (r ≈ 0.7–0.85 with JC
distance; partial p never significant), and it misses both FDR survivors. Embedding distance is
not blind, it is redundant: a compressed, noisier restatement of sequence identity whose loss
falls on exactly the genes and sub-region that carry the signal. Classical sequence conservation
remains the only method here that resolves it.

## Reproducing

All analyses are scripted (`scripts/`) and regenerable; `data/` intermediates are gitignored.
The extended-panel result pins its exact inputs (tree, traits, UTR sequences) under
[2026-08-05-extended-panel/inputs](2026-08-05-extended-panel/inputs/) for bit-reproducibility.
Each result directory contains a `RESULT.md`, the machine-readable outputs, and the figure.
