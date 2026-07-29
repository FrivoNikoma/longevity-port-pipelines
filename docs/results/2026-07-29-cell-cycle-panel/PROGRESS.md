# Cell-cycle panel (BMAL-predicted pathway) — in-progress lane

Date started: 2026-07-29
Branch: `cell-cycle-panel`
Status: **embed stage in progress (Biohub daily-cap resume) — not yet analyzed.**

## Goal

Test the last unverified arm of the convergent-divergent model: the **BMAL (large-bodied)**
prediction that big-bodied longevity requires tighter **cell-cycle / tumor-suppressor control**
(Peto's paradox / cancer resistance). BMAL-vs-Reference is the contrast where a positive is
predicted; ELLSM-vs-Reference and BMAL-vs-ELLSM are controls. Same ESM interface-divergence method
and strata as the SIRT6 / AMPK stratified runs.

## Design

- Candidate set `cell_cycle` added to `data/config/candidate_sets.yaml` (9 focus genes, 21 partners,
  30 explicit UniProt IDs: RB1, TP53, CDK1/2/4/6, CDK3, cyclins A/B/D/E, CDKN1A/1B/2A, MDM2/4,
  ATM, ATR, CHEK1/2, WEE1, CDC25A/C, CDC20, FZR1, ANAPC2, CDC27, MAD2L1, BUB1B).
- New CLI flag `select --selection-mode explicit_only` (added to `src/.../cli.py`) so selection is
  restricted to complexes containing a listed protein (partner_aware pulled in off-target AMPK,
  histones, chromatin remodelers and was discarded).
- Strata (config): ELLSM 5 (naked/Damaraland/blind mole-rat, Myotis, greater horseshoe bat),
  BMAL 5 (elephant, blue whale, beluga, sperm whale, white rhino), Reference 12 + human anchor.

## Pipeline state

1. `uv run select --candidate-set cell_cycle --count 20 --selection-mode explicit_only` — **done**.
   97 PINDER complexes matched; top 20 written to `data/output/selection.csv`. On-target:
   CDK–cyclin (CDK1–CCNB1, CDK2–CCNE1/CCNA2/CCNB1, CDK4–CyclinD3, CDK3–CCNE1), CDK inhibitors
   (CDK6–p16/CDKN2A, CDK2–p27), spindle checkpoint (MAD1–MAD2, CDC20–BUB1B, CDC20–MAD2),
   APC/C (CDC27, CDC20, FZR1), CDK4 chaperones (HSP90–CDK4, CDC37–CDK4).
2. `uv run orthologs` — **done**. `ortholog_coverage.csv`, 504 rows, most proteins at full
   5 ELLSM / 5 BMAL / 12 Reference. Weak: CDKN2C/p18 (1 ortholog → 1jow drops on that chain),
   CDKN2A/p16 (BMAL 2).
3. `uv run embed` — **in progress**. Biohub daily credit cap = 100/day. ~742 of 866 sequences
   remain (~8 daily runs). Done: 5fwm, 1jsu, 6tlj. Embeddings cache per `.npy`, so re-running
   resumes automatically.
4. `uv run analyze` → `data/output/enrichment.parquet` — **pending** (after embed completes).
5. Stratified contrasts + RESULT.md + PR — **pending**.

## Daily resume routine (until embed finishes)

```powershell
cd C:\Users\nikom\projects\longevity-port-pipelines
uv run embed        # skips cached, does ~100 more, then 429 (harmless traceback) — repeat next day
```

When `uv run embed` completes without a 429 and prints "Embeddings written to …":

```powershell
uv run analyze      # writes data/output/enrichment.parquet
```

Then the stratified contrasts are computed ad-hoc from the parquet (sandbox cannot import the
package), mirroring `docs/results/2026-07-28-sirt6-convergent-divergent-stratified/`:
BMAL-vs-Reference (predicted positive), ELLSM-vs-Reference, BMAL-vs-ELLSM; per-interface
Mann-Whitney + BH-FDR; shuffled-mask / NEGATOME / cross-lineage convergence controls.

Nothing under `data/` is committed (gitignored); the run is fully regenerable from the two config
changes above plus these commands.
