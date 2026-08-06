# The AI metric re-tested at panel scale: the embedding tracks the alignment and adds nothing

The project's AI arcs (ESM interfaces, Nucleotide Transformer UTRs, Enformer expression) were
all null, and the working summary had become "embedding distance is a weak detector of
lineage-specific selection". That summary rested on a measurement taken in the wrong regime.
The **NT UTR null** ([utr3-regulatory-divergence](../2026-08-04-utr3-regulatory-divergence/RESULT.md),
pooled p = 0.85, 9/15) was produced at **n = 22** on a hand-built tree, over the **whole UTR**,
with a **genome-generic** model. The [power calibration](../2026-08-05-power-calibration/RESULT.md)
later showed n = 22 sits at the detection floor — the regime where the *classical* signal was
also invisible — and the [positional map](../2026-08-05-utr-positional/RESULT.md) showed the real
signal lives in the proximal 38 % of the 3' UTR. That null therefore confounded three things:
sample size, window, and model class. This layer separates them.

## Design

Everything is held identical to the classical extended-panel test
(`scripts/analyze_panel_utr_divergence.py`): the same 57-species panel, the same AnAge traits,
the same TimeTree Brownian covariance, the same PGLS on log10(lifespan) + log10(mass), the same
BH-FDR across genes, the same pooled per-species-mean test, the same sign test. **Exactly one
component is swapped** — divergence is the distance to the human UTR in language-model embedding
space instead of the Jukes-Cantor distance of a pairwise alignment. Any difference in outcome is
therefore attributable to the metric.

- **Models:** `multimolecule/utrbert-3mer` (3UTRBERT, pretrained on human 3' UTRs — the
  region-domain match) and `InstaDeepAI/nucleotide-transformer-v2-50m-multi-species` (the
  literal old-null control, re-run at the new n). NT is deliberately run against the project's
  pinned transformers 4.57.6, i.e. the environment the old null came from.
- **Windows:** proximal (first 38 %) vs full UTR. 3UTRBERT caps at 510 tokens (~512 nt), so
  truncating would have collapsed the two windows into the same first-512-nt string for 28 % of
  cell-cycle sequences; instead both windows are chunked and length-weighted mean-pooled, so each
  is a genuine representation of its region at any length (`scripts/embed_utr_rna_lm.py`).
- **Metrics:** cosine and L2. Pooling is over per-gene z-scores, since embedding distances have no
  common scale across genes; per-gene PGLS p-values are invariant to that rescaling.
- **Circularity control (the decisive part):** an LM embedding partly encodes sequence identity,
  so a cosine-to-human distance can simply re-measure JC divergence and inherit the classical
  signal without adding anything. Every cell is therefore reported head to head against JC on the
  identical species set: `r(emb, JC)`, plus partial PGLS `p_emb_given_jc` and `p_jc_given_emb`.

## Results

Pre-registered primary cell: 3' UTR, proximal window, cosine, cell-cycle module, n = 57.

| Model | pooled p | FDR | direction | r(emb, JC) | emb given JC | JC given emb |
|---|---|---|---|---|---|---|
| **3UTRBERT** (primary) | 0.20 | 0/25 | conserve 17/25 | 0.74 | **0.80** | 0.059 |
| NT-50M (control) | 0.054 | 0/25 | conserve 15/25 | 0.80 | **0.28** | 0.106 |
| *classical JC, same species* | *0.023* | — | *conserve* | — | — | — |

Full grid, 3' UTR, cell-cycle, n = 57 (pooled PGLS lifespan p / `emb given JC`):

| Cell | 3UTRBERT | NT-50M |
|---|---|---|
| prox / cosine | 0.20 / 0.80 | 0.054 / 0.28 |
| prox / L2 | 0.14 / 0.77 | 0.038 / 0.26 |
| full / cosine | 0.13 / 0.56 | 0.30 / 0.73 |
| full / L2 | 0.057 / 0.41 | 0.30 / 0.85 |

**The embedding never adds anything beyond the alignment.** Across the twelve cells run (two
model families × two windows × two metrics on the 3' UTR, plus the four 5' UTR control cells),
`p_emb_given_jc` is **never** significant — range 0.26–0.88. Meanwhile `p_jc_given_emb` stays at
0.041–0.14 on the 3' UTR: the alignment largely survives adjustment for the embedding, not the
other way round. With r(emb, JC) = 0.66–0.85 on the 3' UTR, the embedding is a compressed,
noisier restatement of sequence identity.

**Both models miss the FDR survivors.** CDK4 is p = 4e-5 classically and **0.53** under 3UTRBERT
(0.83, wrong direction, under NT); CDC20 is 0.0032 classically and **0.49** under 3UTRBERT (0.041
under NT). Neither model's own best genes (3UTRBERT: CDK2 0.058; NT: CDC20 0.041) survive FDR.

**Decomposing the old null** — same NT model, same L2 metric, same 15 lane genes as the original
arc, moving one factor at a time:

| Panel | Window | pooled p |
|---|---|---|
| n = 22 (published) | full | 0.85 |
| n = 57 | full | 0.28 |
| n = 57 | proximal | 0.24 |

Sample size was the dominant confound: the old null does not reproduce at n = 57 (0.85 → 0.28).
The proximal window adds little on this mixed 15-gene set (0.28 → 0.24) but matters inside the
cell-cycle module (0.30 → 0.038), which is where the classical signal lives. **"Embeddings are
blind to lineage-specific selection" was too strong** — NT reaches nominal p = 0.038 once the
panel and window are right. It still survives no FDR and still adds nothing beyond JC.

**The domain match did not help.** 3UTRBERT — pretrained on human 3' UTRs, the region-matched
model — does **not** beat genome-generic NT anywhere in the grid, and is worse in the primary
cell (0.20 vs 0.054). "Wrong model class" was not the explanation for the old null.

**Controls behave.** The 5' UTR is null under 3UTRBERT in the pre-registered window (prox/cosine
p = 0.94, prox/L2 p = 0.69), matching the classical 5' UTR null — the metric is not picking up a
generic artifact. One off-primary 5' UTR cell (full/L2) does carry a single FDR survivor at
pooled p = 0.12; with 5' UTR classical divergence itself at p = 0.10 on this species set, that is
read as noise in a non-primary cell rather than a 5' UTR signal, but it is recorded rather than
dropped.
The classical comparator recomputed independently inside this script gives pooled p = 0.023,
consistent with the published 0.022. The PGLS was re-derived through an independent Cholesky-whitening
route and matches `PANEL.gls` to 1e-8; the covariance is symmetric positive-definite.

**No proximal localisation in embedding space.** Classically the signal is sharply proximal
(p = 0.0005 proximal vs 0.27 distal). Under 3UTRBERT prox (0.20) is *weaker* than full (0.13) —
the embedding does not reproduce the sharpest structural feature of the classical result.

## Interpretation

This is a **well-powered, decomposed negative for embedding distance as a detector of regulatory
lifespan constraint** — a stronger statement than the earlier weak null, and partly a correction
of it. The metric is not blind; it is redundant. It measures roughly what the alignment measures,
with loss, and the loss falls exactly on the genes and the sub-region that carry the signal.
Classical sequence conservation remains the only method in this project that resolves the
cell-cycle 3' UTR longevity signal.

## Bounds

- **Species-OOD remains.** 3UTRBERT is pretrained on *human* 3' UTRs. The domain match is on the
  region type (3' UTR rather than whole genome), **not** on the species. Embedding a naked
  mole-rat or whale UTR with a human-trained model is the same out-of-distribution problem
  Enformer had, only milder. Anchoring on distance-to-human mitigates it — the reader is fixed,
  only the sequence varies — but does not remove it.
- **Mean pooling** over chunks is one readout among many; attention-weighted, per-position or
  fine-tuned representations are not tested here, and a real signal could live in a readout this
  one averages away.
- **Two model families**, both encoder-only and both modest (86M / 50M). RiNALMo-650M and
  fine-tuned variants are untested; the compute was deliberately kept to CPU.
- Human-anchored pairwise divergence, not branch-specific, exactly as in the classical test —
  so this layer inherits that bound rather than fixing it.
- The n = 22 → n = 57 rung of the decomposition ladder also changes the tree (hand-built →
  TimeTree), so it is a panel upgrade rather than a pure sample-size change.

## Reproducing

```
uv run --no-project --with torch --with transformers --with multimolecule --with numpy \
    python scripts/embed_utr_rna_lm.py --region utr3     # 3UTRBERT embeddings
uv run --no-project --with torch --with transformers --with multimolecule --with numpy \
    python scripts/embed_utr_rna_lm.py --region utr5     # 5' UTR control
uv run --with torch --with transformers --with numpy \
    python scripts/embed_utr_rna_lm.py --region utr3 --backend dna \
    --model InstaDeepAI/nucleotide-transformer-v2-50m-multi-species   # old-null control
uv run python scripts/analyze_utr_embedding_panel.py --model multimolecule/utrbert-3mer \
    --regions utr3,utr5 --gene-set cellcycle --out-dir docs/results/2026-08-06-utr-embedding-panel
uv run python scripts/analyze_utr_embedding_panel.py --gene-set cellcycle --regions utr3 \
    --model InstaDeepAI/nucleotide-transformer-v2-50m-multi-species \
    --out-dir docs/results/2026-08-06-utr-embedding-panel
```

`multimolecule` requires transformers >= 5, while the project lock pins the 4.57.6 fork that
`esm` needs — hence `--no-project` for the RNA runs. The NT control deliberately omits it, so the
control reproduces the environment the original null came from. Embeddings land in
`data/interim/utr_panel_emb/` (gitignored); the fetched UTRs and tree are the extended-panel
inputs pinned in [`../2026-08-05-extended-panel/inputs/`](../2026-08-05-extended-panel/inputs/).
