# Neutral control: the proximal 3' UTR indel deficit is specific, not a genome-wide rate effect

The previous layer showed that the proximal 3' UTR longevity signal is carried by **indels**,
not substitutions ([constraint nature](../2026-08-07-utr-constraint-nature/RESULT.md)). It left
one alternative standing, and it was the obvious one: long-lived mammals have longer generation
times and lower per-year mutation rates, so they may accumulate indels more slowly *everywhere*.
If so, nothing about the 3' UTR is special.

That layer's background control was **internal** — the distal half of the same UTRs — which
shares locus, annotation and alignment procedure with the window under test and is not neutral
sequence. This is the external version: intronic windows from the same genes in the same
species, through the identical alignment and indel machinery.

## Design

`scripts/fetch_gene_introns.py` retrieves a 3 kb window centred on the **midpoint of the gene
body** for each (gene, species) — for genes of this size the exonic fraction is a few percent,
so a mid-gene window is intronic with high probability without needing exon-level annotation.
Genes whose genomic span is below 20 kb are skipped rather than risking an exon-dense window.

The windows behave as neutral sequence should. For ATM: GC content 0.384 in the intron against
0.559 in the 3' UTR (intronic sequence is AT-rich; an exonic window would not be), and the
intron is **more** divergent than the UTR on both metrics — substitutions 0.220 vs 0.209, indels
0.306 vs 0.116. The near-threefold indel gap confirms both that indels are genuinely suppressed
in the 3' UTR and that the control has the dynamic range to detect a rate effect if one exists.

Every comparison below is restricted to the **11 genes with data in both regions**
(ATM, ATR, BUB1B, CDC25A, CDK6, CHEK1, CHEK2, MDM2, MDM4, RB1, TFDP1), so the contrast is not
confounded by gene composition.

## Results

Same 11 genes, same 57 species, same PGLS:

| region and metric | slope | 95 % CI | p |
|---|---|---|---|
| **3' UTR proximal, indel** | **−0.0331** | [−0.0642, −0.0020] | **0.038** |
| **intron, indel** (neutral control) | **−0.0040** | **[−0.0218, +0.0138]** | 0.65 |
| 3' UTR proximal, substitution | −0.0044 | [−0.0150, +0.0062] | 0.41 |
| intron, substitution | −0.0088 | [−0.0189, +0.0013] | 0.087 |

**The intron result is a genuine null, not a power failure.** The point is not that p = 0.65;
it is that the intron confidence interval **excludes the slope observed in the 3' UTR**
(−0.0331 lies below −0.0218). The intron effect is 8.3× smaller, and the data are not compatible
with a UTR-sized effect. Adjusting the 3' UTR test for each species' intronic indel rate leaves
it standing: slope −0.0316, p = 0.044 (covariate p = 0.11).

**The rate effect that does exist sits in substitutions, in neutral sequence.** The intron
substitution slope (−0.0088, p = 0.087) is a weak trend in the expected direction, and it is
*larger* than the proximal 3' UTR substitution slope (−0.0044, p = 0.41). That is exactly the
shape of a mild generation-time effect: visible in neutral sequence, absent from the constrained
window, and confined to substitutions rather than indels.

**The internal control was measuring something else.** The species' proximal 3' UTR indel rate
correlates with its intronic rate at only **r = 0.15**, against r = 0.67 with the distal half of
the same UTR used as background in the previous layer. Most of that internal correlation was
therefore shared technical variation — per-species annotation quality, the same locus, the same
alignment — rather than a biological mutation rate. The external control is the stricter test,
and it is the one that matters.

## Interpretation

The generation-time / genome-wide indel-rate explanation is rejected by direct external
evidence. Long-lived mammals do not carry fewer indels everywhere; they carry fewer indels in
the stop-proximal 3' UTR specifically. The constraint on proximal 3' UTR architecture stands as
a regional, selection-like signal rather than a by-product of lineage mutation rates, and the
previous layer's headline can be read as supported rather than provisional.

## Bounds

- **The control is on a subset.** Intron windows require a genomic span above 20 kb, so the
  comparison runs on 11 of the 25 cell-cycle genes, biased toward long genes. On this subset
  the 3' UTR effect itself is much weaker than on the full module (p = 0.038 here against
  p = 0.0003 across 25 genes) — mostly a power difference, but the subset is not a random
  sample of the module and the two numbers should not be quoted interchangeably.
- **"Intronic" is probabilistic, not annotated.** A mid-gene window is intronic with high
  probability for genes of this size, but exon overlap was not explicitly excluded. Occasional
  overlap adds noise; it would only bias the result if exon density correlated with lifespan.
- Introns are **not strictly neutral** — they carry splicing, regulatory and structural
  elements — so this is a near-neutral reference, not a true neutral one.
- Human-anchored pairwise alignment throughout, inherited from the whole arc; indel calls remain
  alignment calls under one gap-penalty regime.
- The intron windows are single 3 kb samples per gene, not the whole intronic complement, so the
  per-species intronic rate is an estimate with its own sampling error — which, being noise in a
  covariate, biases the adjusted test toward leaving the 3' UTR effect standing.

## Reproducing

```
uv run python scripts/fetch_gene_introns.py            # network: NCBI, ~30 min
uv run python scripts/analyze_utr_constraint_geometry.py --region intron --cache-only
uv run python scripts/analyze_intron_neutral_control.py \
    --out-dir docs/results/2026-08-08-intron-neutral-control
```

Intron fastas land in `data/interim/utr_panel/{GENE}_intron.fasta` with the panel's own header
format, so the existing alignment and indel machinery reads them unchanged; alignments are
cached in `data/interim/utr_panel/aln_cache/`. Both are gitignored and regenerable.
