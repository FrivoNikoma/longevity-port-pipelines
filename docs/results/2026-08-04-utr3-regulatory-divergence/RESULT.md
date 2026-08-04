# Regulatory-level reanalysis: UTR divergence vs longevity (classical + DNA-LM)

**Status (2026-08-04): a level-swap probe, not a discovery.** Broad interface-divergence
screening on coding sequence is formally closed as negative
([synthesis](../2026-07-29-synthesis-negative-and-method-boundary/RESULT.md)); the project's
only positive leads (naked mole-rat HAS2 output; elephant TP53 dosage) sit at a
**regulatory / dosage** level that coding-interface metrics cannot see. This result moves
the *unit of analysis* off the coding interface and onto the non-coding sequence that sets
gene dosage — the 5' UTR (translation efficiency) and 3' UTR (mRNA stability, miRNA
control) — and asks the same question one level up: *is UTR divergence elevated (or
suppressed) on long-lived lineages, after phylogenetic control?*

Two metrics are run in parallel on the identical panel: a **classical** alignment metric
and an **AI** metric (a DNA language model), so the AI result can be read against an
orthogonal baseline rather than on its own.

## Design

- **Panel:** 15 genes — the cell-cycle focus set (RB1, TP53, CDK1/2/4/6, ATM, ATR, CDC20)
  plus the five registry lane leads (SIRT6, TP53, HAS2, IGF1R, MTOR, PRKAA1, PRKAA2) —
  across the 22-species longevity panel (max lifespan 3.8–110 yr; body mass 7.5 g–100 t).
  UTRs resolved by NCBI Gene → RefSeq mRNA → CDS-substring slicing
  (`scripts/fetch_lane_utr3.py`): 326/345 (gene, species) pairs recovered both UTRs.
- **Classical metric** (`scripts/analyze_utr3_divergence.py`): per-species Jukes-Cantor
  distance of a global pairwise alignment of the species UTR to the human UTR (biotite,
  affine gaps, no terminal penalty; proximal ≤3000 nt).
- **AI metric** (`scripts/embed_utr_dna_lm.py` + `analyze_utr_embedding_divergence.py`):
  per-species **L2 distance** between the species and human UTR embeddings from a DNA
  language model, **Nucleotide Transformer v2 (50M, multi-species)** — the direct
  counterpart, one level up, of the ESM interface-embedding approach the project closed.
- **Statistics (both):** regress divergence on log10(max lifespan) + log10(body mass),
  OLS and PGLS (Brownian phylogenetic GLS), two-sided; Benjamini-Hochberg FDR across the 15
  genes; pooled per-species-mean fit for one power-maximising test per region. This is the
  identical machine used for the interface rigor battery
  ([phylo-continuous](../2026-07-29-phylo-continuous-reanalysis/RESULT.md)).

A **negative lifespan slope = more conserved** UTR on long-lived lineages (stabilizing /
dosage constraint); a positive slope = more divergent (regulatory rewiring). Both are
informative — direction was decisive once before (the cell-cycle panel inverted).

## Results

No test survives FDR in any region under either metric (0 / 15 throughout). The one
coherent thread is a **direction-consistent 3' UTR conservation trend under the classical
metric**, which the AI metric does not corroborate.

| Metric | Region | FDR survivors | Pooled PGLS lifespan p | Direction consistency (genes conserving) | Sign-test p |
|---|---|---|---|---|---|
| Classical (alignment) | **3' UTR** | 0 / 15 | **0.022** (slope < 0) | **13 / 15 conserve** | **0.0074** |
| Classical (alignment) | 5' UTR | 0 / 15 | 0.48 | 8 / 15 | 1.0 |
| DNA-LM (NT-50M) | 3' UTR | 0 / 15 | 0.85 | 9 / 15 | 0.61 |
| DNA-LM (NT-50M) | 5' UTR | 0 / 15 | 0.18 | 11 / 15 | 0.12 |

Classical 3' UTR, per-gene PGLS lifespan slope (all nominal hits conserve; none survive FDR):

| Gene | PGLS p | slope | | Gene | PGLS p | slope |
|---|---|---|---|---|---|---|
| **HAS2** | **0.0073** | −0.031 | | CDK6 | 0.069 | −0.024 |
| CDK4 | 0.014 | −0.038 | | CDC20 | 0.099 | −0.031 |
| IGF1R | 0.018 | −0.032 | | RB1 | 0.100 | −0.027 |
| PRKAA1 | 0.023 | −0.034 | | TP53 | 0.169 | −0.026 |
| CDK2 | 0.043 | −0.033 | | SIRT6 | 0.222 | −0.017 |
| CDK1 | 0.056 | −0.040 | | others | ≥0.36 | ≈0 |

Notable: **HAS2 — a real project positive — is the single strongest 3' UTR gene** (p =
0.0073, conserve), and every one of the five nominal hits, plus 13 of 15 genes overall,
points the same way (more-conserved 3' UTR in long-lived species). The 5' UTR (translation
control) is flat under both metrics; the trend is specific to the 3' UTR (mRNA-stability /
dosage control), which is the biologically expected lever.

## Interpretation and boundary

**What this is.** The first regulatory-level signal in the project that is not a flat null.
At the coding interface, divergence was null in *both* direction and magnitude; here the
classical 3' UTR shows a coherent, lifespan-associated bias toward **conservation**
(stabilizing selection on mRNA-stability regulation), concentrated exactly where the
biology predicts (3' not 5' UTR) and led by a known positive (HAS2).

**What this is not.** A discovery. No gene survives per-gene FDR (0 / 15); the pooled signal
is only nominally significant (p = 0.022) and rests on a modest lifespan–mass collinearity
(r = 0.70, the n = 22 ceiling), though lifespan dominates the joint fit (mass p = 0.63).
Broad regulatory-divergence screening is therefore **not** established as a standalone
discovery method on this evidence — the same discipline applied to the interface.

**The AI result is itself informative.** The DNA-LM embedding metric (NT-50M L2) does not
reproduce the classical 3' UTR trend (pooled p = 0.85; 9 / 15). This mirrors, one level up,
the interface finding: **embedding-L2 divergence — whether protein (ESM) or DNA (Nucleotide
Transformer) — is a weak detector of lineage-specific selection**, and the alignment /
constraint view sees a direction that mean-pooled embedding distance misses. The right AI
tool for the regulatory level is probably not a sequence-embedding distance but an
**expression- or activity-prediction model** (e.g. Enformer / Borzoi), which scores the
regulatory *output* the dosage hypothesis is actually about.

**Where the signal (if any) is.** 3' UTR mRNA-stability / miRNA regulation, not 5' UTR
translation; conservation, not rewiring; strongest at HAS2. The motivated next steps are
targeted rather than broader: (1) miRNA-seed-site-level analysis within 3' UTRs;
(2) expression-prediction models on the same loci; (3) branch-specific (not human-anchored)
divergence; (4) more species to break the mass–lifespan collinearity.

## Follow-up: does the 3' UTR conservation sit on miRNA target sites?

The classical 3' UTR trend is diffuse (a whole-UTR mean). The main post-transcriptional
dosage lever in a 3' UTR is its set of **miRNA target sites**, so if the conservation is
regulatory it should concentrate there. Test: locate canonical 7mer-m8 sites for all **108
broadly conserved human miRNA families** (TargetScan `miR_Family_Info.txt`) in each human
3' UTR, then measure per-species **retention** (fraction of human sites whose exact motif
survives at the aligned ortholog position) and **site density** (sites / kb); PGLS + BH-FDR
as above (`scripts/analyze_mirna_site_conservation.py`).

| Metric | Genes tested | FDR survivors | Pooled PGLS lifespan p | Direction | Note |
|---|---|---|---|---|---|
| Site retention | 11 | 0 / 11 | 0.15 (slope > 0, conserve) | 9 / 11 conserve (sign-test p = 0.065) | strongest CDK2 (p = 0.009) |
| Site density | — | — | 0.69 | flat | no lifespan-linked regulatory load |

**This does not localize the signal — it narrows it.** Site retention shows only a weak,
same-direction tendency (pooled p = 0.15, vs 0.022 for the whole UTR) and, tellingly, is
**not** driven by HAS2 (retention p = 0.81, despite HAS2 leading the whole-UTR test); the
strongest gene here is CDK2. Site density is flat. So the whole-3' UTR conservation trend is
**diffuse, not concentrated on canonical miRNA seed sites** — it is not explained by a
simple miRNA-site-tuning mechanism, and points instead at broader 3' UTR sequence/structure
constraint (or a general conservation gradient). Four genes (ATM, ATR, MTOR, CDC20) carry
truncated reference 3' UTRs and drop out of the site test.

## Reproducing

```
uv run python scripts/fetch_lane_utr3.py                      # UTRs -> data/interim/utr (gitignored)
uv run python scripts/analyze_utr3_divergence.py             # classical -> utr_divergence.{json,png}
uv run --with torch --with transformers --with numpy \
    python scripts/embed_utr_dna_lm.py                       # DNA-LM embeddings (no Biohub credits)
uv run python scripts/analyze_utr_embedding_divergence.py    # AI -> utr_embedding_divergence.{json,png}
uv run python scripts/analyze_mirna_site_conservation.py     # miRNA sites -> mirna_site_conservation.{json,png}
```

`data/interim/mirna/miR_Family_Info.txt` is TargetScan release data (downloaded separately;
gitignored).

`data/` intermediates are gitignored; committed here are the two figures and the two
machine-readable JSON summaries. No Biohub/ESM credits are used — the AI metric runs a
public DNA language model locally.
