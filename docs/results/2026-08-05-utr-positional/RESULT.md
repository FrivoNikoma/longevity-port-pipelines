# Positional map: the cell-cycle 3' UTR conservation is proximal (near the stop codon)

The cell-cycle 3' UTR conservation signal
([cellcycle-expansion](../2026-08-05-cellcycle-expansion/RESULT.md)) is a whole-UTR mean. This
localises it *along* the UTR, to ask where the conserved-in-long-lived-species positions sit.

## Method

For each cell-cycle gene, every species is aligned to the human 3' UTR and each human position
scored 0 (conserved: same base) or 1 (divergent: mismatch or gap). The human UTR is split into
8 relative bins (proximal, near the stop codon, -> distal, near the poly-A); per species, per
bin, divergence is the mean position score in that bin. Pooled across the module, each bin's
per-species mean divergence is regressed on lifespan + mass (PGLS). A bin whose divergence
*falls* with lifespan is where long-lived species conserve most
(`scripts/analyze_utr_positional.py`).

## Results

| Bin (relative position) | PGLS lifespan p | slope | |
|---|---|---|---|
| 0.00-0.12 (proximal) | **0.0005** | −0.045 | conserve |
| 0.12-0.25 | **0.0008** | −0.046 | conserve |
| 0.25-0.38 | **0.013** | −0.047 | conserve |
| 0.38-0.50 | 0.094 | −0.036 | conserve |
| 0.50-0.62 | 0.12 | −0.037 | conserve |
| 0.62-0.75 | 0.15 | −0.038 | conserve |
| 0.75-0.88 | 0.24 | −0.031 | conserve |
| 0.88-1.00 (distal) | 0.27 | −0.030 | conserve |

**The signal is proximal.** Every bin conserves (negative slope), but the lifespan association
is concentrated in the **first ~38 % of the 3' UTR, next to the stop codon** (p = 0.0005,
0.0008, 0.013), and fades monotonically toward the distal poly-A end (p > 0.09). The
long-lived-species conservation is not spread evenly along the tail — it sits on the proximal
3' UTR, which is where the core post-transcriptional regulatory elements (many miRNA target
sites, AU-rich stability elements, and the stop-proximal regulatory region) cluster.

## Interpretation and bounds

This sharpens the module-wide signal into a concrete location: the cell-cycle 3' UTR
conservation in long-lived mammals is a **proximal-3' UTR** phenomenon. That is exactly where
functional regulatory motifs concentrate, so it makes the "which element" question tractable
and well-targeted: the next step is to test whether the proximal conserved region is enriched
for miRNA seed sites or ARE / stability motifs.

Bounds: a module-level, comparative-genomics profile. Genes with very short human 3' UTRs are
excluded from binning — notably **CDC20 (~74 nt) and ATM (~34 nt)**, so the two shortest FDR /
panel genes do not contribute to the positional map; the profile reflects the ~23 cell-cycle
genes with 3' UTRs long enough to bin. Relative (not absolute) bins are used because UTR length
varies across genes.

## Reproducing

```
uv run python scripts/analyze_utr_positional.py   # -> utr_positional.{json,png}
```

Requires the panel UTRs (data/interim/utr_panel) and TimeTree tree; data/interim is gitignored.
No Biohub credits used.
