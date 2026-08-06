# What kind of constraint is it? The proximal 3' UTR signal is indels, not substitutions

Three hypotheses about the diffuse proximal 3' UTR conservation have now failed: it is not
canonical miRNA target sites, not AREs
([element enrichment](../2026-08-05-utr-element-enrichment/RESULT.md)), and — shown here — not
RNA secondary structure. All three are hypotheses about *sequence composition*, and all three
were tested with substitution-based metrics. This layer asks the prior question those tests
skipped: **what kind of evolutionary event is actually constrained?**

The answer reorganises the arc. The published proximal localisation
([positional map](../2026-08-05-utr-positional/RESULT.md)) scored an alignment gap exactly like
a mismatch. Separating the two shows the proximal signal is carried almost entirely by
**indels**. Point substitutions in the proximal window are not significantly lifespan-linked at
all.

## Probe 1 — secondary structure: no

The human proximal 3' UTR is folded (ViennaRNA, local fold with `max_bp_span=150`, the
RNAplfold convention — a global MFE fold of a kilobase mRNA window produces mostly artifactual
long-range pairs), each species is aligned to it, and divergence is computed separately over
paired and unpaired positions. The primary statistic is a **within-sequence contrast**,

    delta = divergence(unpaired) - divergence(paired)

so the overall substitution rate cancels and the metric cannot re-measure Jukes-Cantor distance
— the circularity that sank the embedding metric
([embedding panel](../2026-08-06-utr-embedding-panel/RESULT.md)). It worked: **r(delta, JC) =
+0.035**, against r = 0.74 for the embedding distance.

| statistic (cell-cycle, n = 57) | PGLS lifespan p | slope |
|---|---|---|
| **delta (primary)** | **0.14** | −0.0059 |
| delta, shuffled pairing mask (control) | 0.42 | +0.0028 |
| compensatory-substitution rate | 0.37 | +0.0094 |
| divergence at paired positions | 0.066 | −0.0087 |
| divergence at unpaired positions | 0.0016 | −0.0146 |

**The negative is interpretable because the method demonstrably sees structure.** Real pairing
masks versus length-matched shuffled masks across 1 376 species–gene pairs: mean delta +0.0080
vs +0.0005, **Wilcoxon p = 4.7e-4**. Predicted base pairs really are better conserved than
random positions — baseline structural constraint exists and is detected. It simply does not
scale with lifespan. Paired and unpaired positions both conserve with lifespan, and unpaired
slightly *more* (0.0016 vs 0.066), so the constraint is on the region, not on the pairing.
The 5' UTR behaves the same way (delta p = 0.32).

Under a global fold the compensatory rate reached p = 0.071 — a hint that disappears (p = 0.37)
under local folding. The apparent structural signal was an artifact of unreliable long-range
pairs.

## Probe 2 — indels vs substitutions

Identical alignments, three per-position metrics: **combined** (gap or mismatch scores 1 — the
published convention), **substitution** (gapped positions dropped), **indel** (fraction gapped).

| relative bin | combined (published) | substitution | indel |
|---|---|---|---|
| 0.00–0.12 | **0.0005** | 0.061 | **0.0022** |
| 0.12–0.25 | **0.0008** | 0.39 | **0.0014** |
| 0.25–0.38 | **0.013** | 0.14 | **0.015** |
| 0.38–0.50 | 0.080 | **0.0045** | 0.17 |
| 0.50–0.62 | 0.12 | **0.0086** | 0.23 |
| 0.62–0.75 | 0.15 | 0.085 | 0.24 |
| 0.75–0.88 | 0.24 | 0.058 | 0.34 |
| 0.88–1.00 | 0.29 | 0.054 | 0.42 |

The combined column **reproduces the published positional map exactly** (0.0005 / 0.0008 /
0.013), which validates this reimplementation against the earlier one. The decomposition then
shows where those numbers came from: the indel column carries the proximal concentration; the
substitution column does not, and its significant bins sit mid-UTR instead.

Over the proximal window as a whole:

| metric | PGLS lifespan p | slope | mean |
|---|---|---|---|
| combined (published convention) | 0.0002 | −0.045 | 0.330 |
| **substitution only** | **0.15** | −0.0063 | 0.151 |
| **indel only** | **0.0003** | −0.047 | 0.216 |

**Two confounds that could have manufactured this do not.**

*UTR length mismatch.* Gaps are mechanically produced by UTR length differences, and human —
the alignment anchor — is itself long-lived, so "long-lived species look more human" is a live
alternative. Length mismatch does drive gaps (r = +0.53), but it is **uncorrelated with
lifespan** (r = −0.029), and entering it as a third covariate leaves the effect intact:
**p = 0.0009**, slope −0.039 (covariate p = 5e-4).

*Species-level indel rate.* The obvious alternative is that long-lived mammals accumulate
indels more slowly everywhere — longer generation times, lower per-year mutation rate — so that
nothing about the 3' UTR is special. Each species' background indel propensity, measured off
the window of interest on the **distal half of the same UTRs**, tests this. The background rate
is strongly real (r = 0.665 with the proximal rate; covariate p = 1e-6) but is **not itself
lifespan-linked (p = 0.33)**, and the proximal effect survives holding it constant:
**p = 0.0002**, slope −0.039. The deficit is specific to the proximal window, not a property
of the species.

Jackknives: worst leave-one-gene-out p = 0.0042 (dropping WEE1), worst leave-one-clade-out
p = 0.0021 (dropping all rodents, n = 42).

In absolute coordinates the indel constraint spans roughly the first 400 nt from the stop codon
(0–50 p = 0.0048, 50–100 p = 0.012, 100–200 p = 0.0013, 200–400 p = 0.015) and fades beyond
(400–800 p = 0.090, 800–3000 p = 0.30). It is a stop-proximal zone of a few hundred nucleotides,
not a tight footprint of one complex. Substitutions in absolute coordinates are flat and weak
across the whole 0–800 nt range (p = 0.013–0.048).

## Interpretation

**Long-lived mammals carry fewer insertions and deletions in the stop-proximal 3' UTR.** The
constraint is on UTR architecture — length and spacing of the proximal region — rather than on
which bases occupy it. That single fact explains why three composition hypotheses in a row came
up empty: miRNA sites, AREs and secondary structure are all claims about *which bases are
there*, tested with substitution metrics, and there is no proximal substitution signal for them
to explain.

This **refines rather than overturns** the positional map. Its localisation is correct and
reproduces exactly; what was not established there is which class of mutation the localisation
belongs to, because the score merged both. The FDR-surviving gene-level result
([extended panel](../2026-08-05-extended-panel/RESULT.md)) used whole-UTR Jukes-Cantor distance
from the same alignments and is likewise a mixed measure; nothing here contradicts it, but the
proximal component of it should now be read as predominantly indel-driven.

An internal check supports the biology over an annotation artifact: the proximal 3' UTR boundary
is anchored by the stop codon and is therefore the most reliably annotated part of the
transcript, while the distal boundary (the poly-A site) is the least. Gap rates follow that
exactly — 0.21 proximal against 0.49 distal — so the signal sits where the data are *cleanest*,
which is the opposite of what an annotation artifact would produce.

## Bounds

- **Human-anchored pairwise alignment**, inherited from the whole arc. Length mismatch is
  controlled for explicitly, but a single reference and pairwise (not multiple) alignment remain.
- **Indel calls are alignment calls.** Gap placement depends on the affine penalty (−10, −1);
  gap *rate* over a window is far more stable than exact gap positions, and the analysis uses
  only the rate, but no alternative gap-penalty regime was tested.
- **3' UTR annotation quality varies across species** and is prediction-based for most
  non-model mammals. The stop-proximal anchoring argument bounds this but does not remove it.
- **MFE folding is a prediction, not measured structure**, and a single-sequence fold of the
  human window is not an alignment-consensus fold; the structure negative is a negative for
  predicted structure.
- Indel *rate* is measured, not indel *length spectrum* or the distinction between insertion
  and deletion, which would need an outgroup polarisation this design does not have.
- **The neutral-region control is internal, not external.** Species-level indel propensity is
  estimated from the distal half of the same 3' UTRs — the same transcripts, the same alignment
  procedure — which is the right comparison in every respect except one: the distal 3' UTR is
  not neutral sequence, and it is the *worst*-annotated part of the transcript, so it is a
  noisier background than an intron or an intergenic window would be. Noise in a covariate
  biases its adjustment toward zero, i.e. toward leaving the proximal effect standing. An
  external neutral control (introns of the same genes, same species) is the outstanding test
  and would be the decisive one; until it is done, "the deficit is specific to the proximal
  3' UTR" should be read as strongly supported rather than settled.
- **Generation time is only indirectly controlled.** Lifespan, body mass and generation time
  are tightly correlated in mammals; mass is a model term and the background-indel covariate
  absorbs the rate component that shows up in these transcripts, but generation time itself is
  not a variable in the model, and no per-lineage substitution-rate estimate was used.

## Reproducing

```
uv run --with ViennaRNA python scripts/analyze_utr_structure_conservation.py \
    --max-span 150 --regions utr3,utr5 \
    --out-dir docs/results/2026-08-07-utr-constraint-nature
uv run python scripts/analyze_utr_constraint_geometry.py \
    --out-dir docs/results/2026-08-07-utr-constraint-nature
```

Both read the extended-panel UTRs and the TimeTree tree pinned under
[`../2026-08-05-extended-panel/inputs/`](../2026-08-05-extended-panel/inputs/). Alignments are
cached in `data/interim/utr_panel/aln_cache/` (one character per human position: `0` conserved,
`1` substituted, `-` gapped) and folds in `struct_cache/`; both are gitignored and regenerable.
