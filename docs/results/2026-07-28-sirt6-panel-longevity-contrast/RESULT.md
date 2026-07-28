# SIRT6 DNA-repair panel — long-lived vs short-lived interface-divergence contrast

Date: 2026-07-28
Candidate set: `sirt6_dna_repair`
Status: **technical checkpoint / preliminary result — not a validated biological claim.**
Both negative controls (shuffled-mask + NEGATOME) applied.

## Summary

We ran the full interface-embedding pipeline (`select → orthologs → embed → analyze`) on the
SIRT6 DNA-repair candidate set, expanded to **23 protein-protein interfaces** (complex × chain,
136 non-degenerate rows) spanning NHEJ DNA repair, apoptosis, p53 regulation, and inflammation,
with a balanced species panel of **3 long-lived** (elephant, naked mole-rat, *Myotis lucifugus*)
vs **3 short-lived** (mouse, rat, hamster) orthologs, human as reference.

**Headline: across all 23 interfaces, interface divergence is NOT concentrated in long-lived
species.** No interface shows a significant long-lived-vs-short-lived contrast after
Benjamini-Hochberg correction (0/23; all q ≥ 0.71). The method itself works and both controls
are populated: it detects significant interface localization in **67/136** (interface, species)
rows (BH q < 0.05), the shuffled-mask control passes everywhere, and the NEGATOME control
confirms interface-specificity. This is a broad, two-control, FDR-corrected **negative result**.

## Method (brief)

Per-residue ESM C embeddings (`esmc-300m-2024-12`, Biohub) for the human reference chain and each
ortholog. Residues aligned by BLOSUM62 global alignment; per-position L2 embedding delta computed.
`enrichment_ratio = mean interface delta / mean non-interface delta` (interface = 8 Å inter-chain
heavy-atom contacts on the reference structure). `> 1` = interface-divergent; `< 1` =
interface-constrained. Each row carries Mann-Whitney p-values, Cohen's d, a 1000-permutation
shuffled-mask control, and a NEGATOME coupling control. Long-vs-short contrast tested per interface
by Mann-Whitney U (3 vs 3, two-sided), corrected across interfaces by Benjamini-Hochberg.

## Panel & coverage

20 complexes selected from PINDER; **23 complex × chain interfaces** yielded extractable interfaces
and non-degenerate signal (154 rows written, 136 valid). Modules covered: **NHEJ repair**
(Ku80/Ku70 8bot, Ku80 8ag5), **apoptosis** (caspase-3 7xn5/1i3o, XIAP, Bcl-xL 2mej), **p53
regulation** (ASPP2 1ycs, CBP 2l14, EP300 2mzd, and several p53 complexes), **inflammation**
(RELA/IκBα 1nfi), **kinase signaling** (CDK5 7vdr, ERK2 4iz5).

Orthologs for bowhead whale and Brandt's bat were unavailable in both OMA and UniProt for these
proteins (a real coverage gap for the most extreme long-lived species) and were excluded. A few
complexes were dropped by structural chain-naming mismatches (7mo7, 1h2k, 8bhy, 4xr8, 7s68). Hamster
orthologs are predicted structures (lower confidence).

## Results

### Long-lived vs short-lived contrast — no interface survives FDR

Representative interfaces, ranked by |Δ| (long−short mean `enrichment_ratio`):

| Gene | PDB | Chain | Long | Short | Δ (long−short) | Contrast p (3v3) | FDR q |
|---|---|---|---|---|---|---|---|
| ERK2 | 4iz5 | receptor | 0.750 | 1.098 | −0.348 | 0.077 | 0.71 |
| TP53 | 2h1l | ligand | 1.073 | 0.773 | +0.299 | 0.40 | 0.71 |
| TP53 | 1ycs | ligand | 0.918 | 0.785 | +0.133 | 0.40 | 0.71 |
| Bcl-xL | 2mej | ligand | 0.859 | 0.960 | −0.100 | 0.40 | 0.71 |
| Ku80 | 8ag5 | receptor | 1.188 | 1.094 | +0.094 | 0.10 | 0.71 |
| Ku70 | 8bot | ligand | 1.003 | 1.088 | −0.085 | 0.20 | 0.71 |
| RELA | 1nfi | receptor | 1.309 | 1.244 | +0.065 | 0.40 | 0.71 |
| CDK5 | 7vdr | receptor | 0.624 | 0.662 | −0.039 | 0.38 | 0.71 |
| Ku80 | 8bot | receptor | 0.770 | 0.767 | +0.003 | 0.70 | 0.81 |

**0 of 23** interface contrasts are significant after FDR. Directions are inconsistent (some
long-ward, some short-ward), magnitudes small (|Δ| < 0.35, most < 0.1). With 3 vs 3 species the
Mann-Whitney floor is p = 0.10, so per-interface contrast is underpowered by design; the largest
leans (ERK2 short-ward, TP53/2h1l long-ward) are non-significant and only flagged for follow-up.

### Method validation

- **67/136** (interface, species) rows show significant interface localization at BH q < 0.05 —
  the embedding signal is real and broad.
- Shuffled-mask control ≈ 1.00 across rows (no artifactual enrichment).
- The flagship **Ku70/Ku80 (8bot, NHEJ core)** interface is strongly, uniformly constrained across
  all six species (Ku80 enrichment ≈ 0.77, Cohen's d ≈ −0.5 to −0.7, depletion p ≈ 1e-17 to 1e-27),
  and interface-specific under NEGATOME (enrichment/negatome ≈ 0.71) — a robust lifespan-independent
  purifying-selection signal, but with no longevity contrast (Δ = +0.003).

## Controls (both applied)

- **Shuffled-mask control: PASS** (ratios ≈ 1.00) — enrichment/depletion is not a sampling artifact.
- **NEGATOME control: APPLIED** to all rows, using beta-tubulin (TUBB, P07437) as a generic
  non-interacting partner (`enr/neg` away from 1 = interface-specific). Populating this control at
  scale exposed and fixed a real indexing bug (see Code changes) — it had never been exercised on a
  panel where the reference is longer than an ortholog.

## Interpretation

1. The core hypothesis — that protein-protein interfaces diverge specifically in long-lived species
   — is **not supported across 23 interfaces** of DNA repair, apoptosis, p53 regulation, and
   inflammation. Divergence, where present, is species-general, not longevity-linked.
2. The NHEJ Ku70/Ku80 interface is under strong, lifespan-independent purifying selection — a robust
   finding in its own right, confirmed by both controls.
3. No individual lead survives correction. The largest (non-significant) leans are ERK2 (short-ward)
   and a p53 interface (2h1l, long-ward); RELA/NF-κB remains a mild long-ward lean. These are
   candidates for a properly powered follow-up, not claims.

## Limitations

- **Power:** 3 long vs 3 short species → per-interface contrast underpowered (p floor 0.10).
- **NEGATOME** uses a single generic partner (tubulin) applied uniformly; a stronger version uses
  per-source-protein NEGATOME-verified non-interactors and 2–3 partners per source (median).
- **Embedding proxy:** L2 embedding shift is a heuristic for interface change, not binding energy.
- **Single structure per interface;** hamster orthologs are predicted; a few complexes were dropped
  on chain-naming mismatches; whale/bat orthologs unavailable in OMA/UniProt.
- One high-magnitude interface (AnxA2 7nmi, enrichment ≈ 6) is driven by a short interface and
  should be treated as unstable.

## Code changes this sprint

- `select` gained a `--candidate-set` option (was hard-coded to `ampk_pilot`).
- Interface extraction moved from legacy PDB to mmCIF (`interface.py`), so large cryo-EM structures
  (e.g. 8bot) and multi-character PINDER chain IDs work; kept format-agnostic for `.pdb` fixtures.
- **Fixed a NEGATOME indexing bug** (`negatome_analyze.py`): the ortholog coupling was indexed with
  reference-frame positions, raising `IndexError` when the reference is longer than the ortholog.
  Now each embedding is indexed in its own alignment frame. Regression test added
  (`tests/test_negatome_analyze.py`).

## Reproduce

```bash
uv run candidates
uv run interactome
uv run select --candidate-set sirt6_dna_repair --count 20   # --candidate-set added this sprint
uv run orthologs
uv run embed
uv run analyze                                               # enrichment.parquet (shuffled control)
# NEGATOME second control: put committed pairs in place, then re-analyze
cp data/input/sirt6_negatome_control_pairs.csv data/interim/negatome_control_pairs.csv
uv run analyze                                               # now also populates negatome_control_ratio
```
