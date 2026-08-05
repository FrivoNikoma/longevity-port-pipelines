# Cell-cycle expansion: the 3' UTR conservation is a whole-module signal

The extended panel surfaced two FDR-surviving 3' UTR conservation hits, both cell-cycle genes
(CDK4, CDC20). That raised the question the interface work never could ask: is this two genes,
or the **cell-cycle module**? This layer expands the cell-cycle / tumour-suppressor gene set
from 9 to **25 genes** on the same 57-species panel and tests it as a focused set.

## Design

- **+16 cell-cycle genes** fetched across the panel (`scripts/fetch_panel_utr.py`, now also
  fetching the human reference): E2F1, TFDP1, CCND1, CCNE1, CCNA2, CCNB1, CDKN1A, CDKN1B,
  CDKN2A, MDM2, MDM4, CHEK1, CHEK2, WEE1, CDC25A, BUB1B — added to the 9 already present
  (RB1, TP53, CDK1/2/4/6, ATM, ATR, CDC20).
- Same metric, tree and statistics as the extended panel; BH-FDR now over the **25-gene
  cell-cycle set** (`scripts/analyze_panel_utr_divergence.py --gene-set cellcycle`).

## Results

| Region | n species | FDR survivors | Genes conserving | Sign-test | Pooled PGLS p | Mass p |
|---|---|---|---|---|---|---|
| **3' UTR** | 57 | 2 / 25 (CDK4, CDC20) | **20 / 25** | **p = 0.004** | 0.016 (r = −0.51) | 0.94 |
| 5' UTR | 57 | 0 / 25 | 18 / 25 | p = 0.043 | 0.10 | 0.59 |

**Expanding the gene set did not add individual FDR hits — it revealed a pathway-level
signal.** Only CDK4 (p = 4e-5) and CDC20 (p = 0.003) clear FDR (a stricter bar over 25 tests),
but **20 of 25 cell-cycle genes conserve their 3' UTR in long-lived species** (sign-test
p = 0.004), the pooled effect is significant and body-mass-independent (pooled p = 0.016, mass
p = 0.94, r = −0.51), and the near-significant genes are all conserving (CDK2 0.039, RB1 0.054,
CHEK1 0.056, CDK6 0.081, E2F1 0.097). The two FDR hits are the significant tips of a
**module-wide** iceberg, not isolated outliers.

**The module leans conserved on both UTRs, 3' more than 5'.** Unlike the mixed 15-gene panel
(where the 5' UTR was a clean null), the cell-cycle 5' UTR shows a weaker parallel trend
(18 / 25 conserve, sign-test p = 0.043; pooled p = 0.10). So the stabilizing selection is on
the **regulatory sequence of the cell-cycle module broadly**, strongest on the 3' UTR
(mRNA-stability / dosage lever) but not exclusive to it. A 6-gene non-cell-cycle contrast set
leans the same way (5 / 6 conserve on 3' UTR) but is underpowered (p = 0.22).

## Interpretation

The longevity-associated 3' UTR conservation found at n = 57 is not a two-gene curiosity: it
is a **coherent, module-wide property of the cell-cycle / tumour-suppressor program**. Across
25 genes, long-lived mammals stabilize the regulatory (especially 3' UTR) sequence of the
cell-cycle module, with CDK4 and CDC20 individually FDR-significant and the module as a whole
directionally significant (20 / 25, p = 0.004). This is consistent with tighter, more tightly
regulated cell-cycle and tumour-suppressor control in large, long-lived, cancer-resistant
species (Peto's paradox), and it is exactly the kind of dosage-level signal that motivated
moving off the coding interface in the first place.

**Bounds.** A comparative-genomics correlation, not a mechanism; the 5' UTR trend is only
nominal; CDKN2A is poorly annotated across species (n = 32) and contributes little; and the
per-gene effects (beyond CDK4/CDC20) are individually modest. The next step is functional:
dissect where in the CDK4 / CDC20 (and module) 3' UTRs the conservation sits — miRNA seed
sites, AU-rich stability elements, or structure.

## Reproducing

```
uv run python scripts/fetch_panel_utr.py --genes E2F1,TFDP1,CCND1,CCNE1,CCNA2,CCNB1,CDKN1A,CDKN1B,CDKN2A,MDM2,MDM4,CHEK1,CHEK2,WEE1,CDC25A,BUB1B
uv run python scripts/analyze_panel_utr_divergence.py --gene-set cellcycle --out-dir docs/results/2026-08-05-cellcycle-expansion
```

`data/interim` intermediates are gitignored; no Biohub credits used.
