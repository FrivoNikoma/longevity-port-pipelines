# SIRT6 DNA-repair panel — long-lived vs short-lived interface-divergence contrast

Date: 2026-07-28
Candidate set: `sirt6_dna_repair`
Status: **technical checkpoint / preliminary result — not a validated biological claim.**
Second negative control (NEGATOME) not yet applied (see Limitations).

## Summary

We ran the full interface-embedding pipeline (`select → orthologs → embed → analyze`) on
the SIRT6 DNA-repair candidate set with a balanced species panel of **3 long-lived**
(elephant, naked mole-rat, *Myotis lucifugus*) vs **3 short-lived** (mouse, rat, hamster)
orthologs, human as reference.

**Headline: on this panel, interface divergence is NOT concentrated in long-lived
species.** No complex shows a significant long-lived-vs-short-lived contrast. The method
itself behaves correctly — it detects significant interface localization in 25/42 tested
(complex, chain, species) rows (Benjamini-Hochberg q < 0.05) and the shuffled-mask control
passes everywhere (ratios ≈ 1.00) — but the signal is species-general, not
longevity-specific. This is a clean, well-controlled negative result. The single
longevity-leaning lead is the NF-κB RELA interface (see below).

## Method (brief)

Per-residue ESM C embeddings (`esmc-300m-2024-12`, Biohub) for the human reference chain
and each ortholog. Residues aligned by BLOSUM62 global alignment; per-position L2 embedding
delta computed. `enrichment_ratio = mean interface delta / mean non-interface delta`
(interface defined by 8 Å inter-chain heavy-atom contacts on the reference structure).
`> 1` = interface diverges more than background (interface-divergent); `< 1` =
interface-constrained. Each row carries Mann-Whitney p-values, Cohen's d, and a 1000-permutation
shuffled-mask control. Long-vs-short contrast tested by Mann-Whitney U (3 vs 3, two-sided).

## Panel & coverage

Six complexes selected from PINDER; four yielded extractable interfaces across all 6 species
(48 rows; 42 non-degenerate). Two were dropped by structural chain-naming mismatches
(`7mo7` ligand chain absent; `1h2k` HIF1A modeled as chain `S`). Orthologs for bowhead
whale and Brandt's bat were unavailable in OMA and excluded. Hamster orthologs are
predicted structures (lower confidence).

Valid complexes: **8bot** Ku80/Ku70 (XRCC5/XRCC6, NHEJ core), **1nfi** RELA/IκBα (NF-κB),
**7vdr** CDK5/p35, **2mzd** EP300/p53 (receptor only; p53 ligand is a peptide → degenerate).

## Results

### Long-lived vs short-lived contrast (mean `enrichment_ratio`)

| Complex | Chain | Protein | Long mean | Short mean | Δ (long−short) | Contrast p (MWU 3v3) | Interface class |
|---|---|---|---|---|---|---|---|
| 8bot | receptor | Ku80 (XRCC5) | 0.770 | 0.767 | +0.003 | 0.70 | strongly constrained |
| 8bot | ligand | Ku70 (XRCC6) | 1.003 | 1.088 | −0.085 | 0.20 | short-leaning |
| 1nfi | receptor | RELA (p65) | 1.309 | 1.244 | **+0.065** | 0.40 | divergent, long-leaning |
| 1nfi | ligand | IκBα | 1.063 | 1.130 | −0.067 | 0.40 | divergent, short-leaning |
| 7vdr | receptor | CDK5 | 0.624 | 0.662 | −0.039 | 0.38 | constrained |
| 7vdr | ligand | p35 (CDK5R1) | 0.850 | 0.845 | +0.004 | 0.08 | constrained, flat |
| 2mzd | receptor | EP300 | 1.031 | 1.037 | −0.005 | 0.70 | flat |

No contrast reaches significance. With 3 vs 3 species the Mann-Whitney floor is p = 0.10, so
this test is **underpowered by design** — the contrast is reported descriptively (direction +
magnitude). All |Δ| < 0.09.

### Flagship: 8bot Ku80 (XRCC5) interface is strongly, uniformly constrained

| Species | Group | enrichment | Cohen's d | p (constrained dir.) | shuffled control |
|---|---|---|---|---|---|
| elephant | long | 0.724 | −0.729 | 1.0e-27 | 1.004 |
| naked_mole_rat | long | 0.781 | −0.545 | 8.5e-21 | 1.003 |
| myotis_lucifugus | long | 0.803 | −0.475 | 6.2e-17 | 1.003 |
| mouse | short | 0.753 | −0.666 | 1.3e-24 | 1.002 |
| rat | short | 0.766 | −0.609 | 2.2e-22 | 1.002 |
| hamster | short | 0.781 | −0.549 | 3.6e-19 | 1.002 |

The Ku80 binding interface diverges **significantly less** than its own background in every
species (depletion p ≈ 1e-17 to 1e-27; shuffled control ≈ 1.00 confirms this is real
localization, not a sampling artifact) — and to an essentially identical degree in long- and
short-lived species (Δ = +0.003). Biologically consistent with purifying selection on the
core NHEJ machinery, independent of lifespan.

### Method validation

- **25/42** (complex, chain, species) rows show significant interface localization at
  Benjamini-Hochberg q < 0.05 — the embedding signal is real.
- Shuffled-mask control ratios are ≈ 1.00 across all rows (no artifactual enrichment).
- The method cleanly separates a **constrained** interface (Ku80, d ≈ −0.6, depletion
  p ≈ 1e-20) from a **divergent** one (RELA, enrichment ≈ 1.3) — it discriminates as intended.

## Controls

- **Shuffled-mask control: PASS** (ratios ≈ 1.00 everywhere).
- **NEGATOME control: NOT YET APPLIED.** This is the stronger non-interacting-pair control.
  Its absence is the main open limitation. For the present negative result it is less
  pivotal (the shuffled control already rules out artifactual enrichment), but it is
  required before any positive longevity claim.

## Interpretation

1. The core hypothesis — that protein-protein interfaces diverge specifically in long-lived
   species — is **not supported on this DNA-repair/inflammation panel**. Divergence, where
   present, is species-general (evolutionary distance), not longevity-linked.
2. The NHEJ Ku70/Ku80 interface is under strong, lifespan-independent purifying selection —
   a robust and biologically sensible finding in its own right.
3. The one longevity-leaning candidate is **RELA (NF-κB)** interface divergence
   (long 1.31 vs short 1.24). It is not significant here but is mechanistically interesting
   (inflammaging) and is the natural target for a powered follow-up.

## Limitations

- **Power:** 3 long vs 3 short species → contrast test underpowered (p floor 0.10).
- **NEGATOME** second control not yet applied.
- **Embedding proxy:** L2 embedding shift is a heuristic for interface change, not a binding-energy measurement.
- **Single structure per complex** defines the interface; hamster orthologs are predicted structures.
- **Residue non-independence:** within-species p-values indicate localization, not literal independence-based significance.
- Two candidate complexes dropped on chain-naming mismatches; whale/bat orthologs unavailable in OMA.

## Next steps

1. Apply the NEGATOME control to close the second-control gap.
2. Increase power: add long-lived species (bowhead whale, Brandt's bat via direct UniProt
   fetch) and more short-lived controls; target ≥5 vs ≥5.
3. Powered follow-up on the RELA/NF-κB lead.
4. Expand the complex panel (recover 7mo7/1h2k via PINDER→structure chain mapping).

## Reproduce

```bash
uv run candidates
uv run interactome
uv run select --candidate-set sirt6_dna_repair --count 6   # --candidate-set added this sprint
uv run orthologs
uv run embed
uv run analyze                                              # → data/output/enrichment.parquet
```

Two code changes were required this sprint: a `--candidate-set` CLI option on `select`
(previously hard-coded to `ampk_pilot`), and switching interface extraction from the legacy
PDB format to mmCIF (`interface.py`) so large cryo-EM structures such as 8bot — which have no
legacy `.pdb` file — and multi-character PINDER chain IDs are handled. The latter fix is what
made the Ku70/Ku80 flagship analyzable.
