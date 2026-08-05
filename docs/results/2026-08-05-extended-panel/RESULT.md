# Extended panel (57 species, TimeTree): a regulatory longevity signal survives FDR

**Status (2026-08-05): the first FDR-surviving, regulatory-level longevity signal in the
project.** The power calibration
([2026-08-05-power-calibration](../2026-08-05-power-calibration/RESULT.md)) showed the 3' UTR
conservation trend was a real, sizeable effect (\|r\| ~ 0.55) sitting exactly at the n = 22
detection floor — real but underpowered. Enlarging the panel from 22 to ~60 mammals, as that
calibration prescribed, was the test: keep the effect size, add power, and see whether the
edge signal crosses FDR. It does.

## Design

- **Panel:** 59 mammals with traits (57 placed on the tree), spanning rodents, bats,
  primates, carnivores, cetaceans, artiodactyls, afrotherians and a marsupial outgroup;
  max lifespan 3.8-122 yr, body mass 7.5 g-100 t. Species curated by scientific name
  (`data/config/species_panel_extended.tsv`); NCBI taxids resolved from names.
- **Traits:** AnAge maximum longevity and adult weight, resolved by scientific name (with a
  small synonym map); UTRs fetched by (gene, taxid) as before
  (`scripts/fetch_panel_utr.py`).
- **Phylogeny:** a real dated **TimeTree** tree (Newick); the phylogenetic covariance is
  built from its actual branch lengths (Brownian: C[i,j] = root-to-MRCA distance) — replacing
  the hand-built approximate tree used at n = 22.
- **Metric & test:** unchanged — Jukes-Cantor distance of a pairwise UTR alignment to human,
  PGLS on log10(lifespan) + log10(mass), two-sided, BH-FDR across the 15 genes
  (`scripts/analyze_panel_utr_divergence.py`).

## Results

| Region | n (species) | FDR survivors | Pooled PGLS lifespan p | Direction | Sign-test |
|---|---|---|---|---|---|
| **3' UTR** | 57 | **2 / 15** (CDK4, CDC20) | 0.022 (\|r\| = 0.55) | **13 / 15 conserve** | p = 0.0074 |
| 5' UTR | 57 | 0 / 15 | 0.60 | 8 / 15 | ns |

Per-gene 3' UTR (PGLS lifespan p; all leading genes conserve — more conserved in long-lived):

| Gene | p | dir | | Gene | p | dir |
|---|---|---|---|---|---|---|
| **CDK4** | **4e-5** | conserve | | RB1 | 0.054 | conserve |
| **CDC20** | **0.0032** | conserve | | CDK6 | 0.081 | conserve |
| IGF1R | 0.014 | conserve | | PRKAA2 | 0.12 | conserve |
| CDK2 | 0.039 | conserve | | TP53 | 0.16 | conserve |
| SIRT6 | 0.042 | conserve | | HAS2 | 0.29 | conserve |

**Two genes survive FDR, and the survivors are robust.** Leave-one-species-out jackknife:
CDK4 worst-case p = 1e-4, CDC20 worst-case p = 0.013 — neither is driven by a single species.
Body mass carries no pooled signal (p = 0.87), so this is a lifespan association, not an
allometric artifact. The 5' UTR is a clean null throughout — the effect is specific to the
3' UTR (mRNA-stability / dosage control), exactly as at n = 22.

**The signal is cell-cycle, not HAS2.** At n = 22 the apparent lead was HAS2 (p = 0.007);
with tripled data HAS2 falls to p = 0.29, while the robust, FDR-surviving hits are
**cell-cycle / tumour-suppressor genes — CDK4, CDC20, CDK2, RB1, IGF1R, all conserving**. The
small-panel HAS2 lead was largely sampling noise; the real, replicable signal is 3' UTR
conservation of cell-cycle control genes in long-lived mammals — coherent with tighter
cell-cycle and cancer-resistance control in large, long-lived species (Peto's paradox).

## Interpretation

This is the payoff of the whole regulatory arc. The interface screen was closed as negative;
the level was moved to the regulatory 3' UTR, where a diffuse conservation trend appeared
(n = 22) that neither embeddings nor miRNA-site nor Enformer expression explained, and that a
power calibration diagnosed as **real but underpowered**. Enlarging the panel exactly as the
calibration prescribed converts it into a **replicable, FDR-surviving, phylogenetically
controlled signal**: long-lived mammals are under stabilizing selection on the 3' UTRs of
cell-cycle genes. It is the first positive, regulatory-level longevity result the project has
produced, and it vindicates changing the unit of analysis rather than screening more proteins
at the coding interface.

**Bounds and next steps.** This is a comparative-genomics correlation, not a demonstrated
mechanism: divergence is human-anchored and pairwise (not a full branch model), the tree and
traits are from TimeTree/AnAge, and the alignment uses the proximal <=3000 nt of each UTR.
Two FDR survivors on 15 genes is a real but modest yield. The bowhead whale (211 yr) lacks
NCBI mRNA annotation and could not be included; the dog was dropped by TimeTree. Motivated
follow-ups: functional dissection of the CDK4 / CDC20 3' UTRs (miRNA sites, ARE / stability
elements) at nucleotide resolution; a branch-site (non-human-anchored) substitution model;
and expansion of the cell-cycle gene set, where the signal concentrates.

## Reproducing

```
uv run python scripts/fetch_panel_utr.py                      # panel UTRs -> data/interim/utr_panel (gitignored)
# + AnAge dataset and a TimeTree Newick under data/interim/phylo/ (downloaded separately)
uv run python scripts/analyze_panel_utr_divergence.py         # -> panel_utr_divergence.{json,png}
```

`data/interim` intermediates are gitignored; no Biohub credits used.
