# AMPK signaling module — long-lived vs short-lived interface-divergence contrast (5×4)

Date: 2026-07-28
Candidate set: `ampk_pilot`
Status: **technical checkpoint / preliminary result — not a validated biological claim.**
All three controls applied (shuffled-mask + NEGATOME + cross-lineage convergence).
Companion to the SIRT6 DNA-repair result (`../2026-07-28-sirt6-panel-5x4-powered/`) — second module,
same 5-long × 4-short panel, for a cross-module picture.

## Summary

Second independent module on the same higher-powered panel: **5 long-lived** (elephant, naked
mole-rat, *Myotis lucifugus*, Damaraland mole-rat, blind mole-rat) × **4 short-lived** (mouse, rat,
hamster, guinea pig), human reference. AMPK is the canonical energy-sensing longevity kinase, so it
is the natural contrast to the SIRT6 DNA-repair panel.

**Headline: panel-wide negative, consistent with SIRT6 — but with one instructive near-miss.**
Across **30 interfaces**, **0 survive Benjamini-Hochberg FDR** (min q = 0.86). Unlike SIRT6, one
interface — the **AMPKα2–β1 subunit interface (`5iso`)** — passes *both* nominal significance
(p = 0.029, long-ward) *and* clean raw cross-lineage convergence (all 5 long-lived above all 4
short-lived). It is the strongest lead seen across either module. But it **collapses under the
NEGATOME control**: normalized to the non-partner baseline the longevity edge disappears entirely.
This is the clearest demonstration in the project of why the NEGATOME control is necessary.

## Method (brief)

Identical to the SIRT6 5×4 analysis. Per-residue ESM C embeddings (`esmc-300m-2024-12`, Biohub) for
the human reference chain and each ortholog; BLOSUM62 alignment; per-position L2 delta;
`enrichment_ratio = mean interface delta / mean non-interface delta` (interface = 8 Å inter-chain
contacts). Long-vs-short contrast by Mann-Whitney U, BH-corrected across interfaces. Three controls:
1000-permutation shuffled-mask, NEGATOME coupling baseline (universal β-tubulin non-partner,
`enr/neg > 1` = interface-specific), and cross-lineage convergence (min-long > max-short).

## Panel & coverage

15 complexes / **30 complex × chain interfaces** yielded valid signal (270 rows in the 9-species
panel). Per-species coverage: blind mole-rat 30, naked mole-rat 33, *Myotis* 29, elephant 28,
Damaraland 19 (long); mouse 35, rat 35, guinea pig 32, hamster 29 (short). Bowhead whale and Brandt's
bat again had no ortholog coverage. Five complexes were dropped on structural chain-naming mismatches
(1u8f, 5kz5 ×2, 6k7x, 7dvq). AMPK subunits (PRKAA1/2, PRKAB1) and partners (STRAD, PP1, EP300, etc.)
are represented.

## Results

### Long-lived vs short-lived contrast — nothing survives FDR

Interfaces ranked by contrast p (5 long vs 4 short, `enrichment_ratio`):

| Interface | PDB | Chain | mean Long | mean Short | Δ (L−S) | p | BH q | raw converg. |
|---|---|---|---|---|---|---|---|---|
| **AMPKα2–β1** | **5iso** | receptor | 1.697 | 1.531 | **+0.166** | **0.029** | 0.86 | **clean** |
| AMPKα2–STRADβ | 6b2e | receptor | 1.362 | 1.300 | +0.063 | 0.057 | 0.86 | no |
| EP300–CITED2 | 1p4q | receptor | — | — | −0.014 | 0.190 | 1.0 | no |
| — | 7qm2 | ligand | — | — | −0.024 | 0.286 | 1.0 | no |
| — | 5u2d | receptor | — | — | −0.017 | 0.343 | 1.0 | no |

**0 of 30** interface contrasts significant after FDR. Directions inconsistent, magnitudes small.
Only **1 / 30** shows clean raw up-convergence (5iso).

### The lead: AMPKα2–β1 (`5iso`) — passes two tests, fails NEGATOME

The AMPKα2–β1 subunit interface is the strongest candidate in the whole project so far. Per-species
raw enrichment (only 4 long-lived covered here; Damaraland absent):

| Species | Group | enrichment | NEGATOME `enr/neg` |
|---|---|---|---|
| blind mole-rat | long | 1.995 | 0.60 |
| *Myotis lucifugus* | long | 1.612 | 0.67 |
| elephant | long | 1.596 | 0.81 |
| naked mole-rat | long | 1.583 | 0.88 |
| guinea pig | short | 1.568 | 0.87 |
| mouse | short | 1.560 | 0.87 |
| rat | short | 1.542 | 0.80 |
| hamster | short | 1.452 | 0.65 |

1. **Nominal significance — PASS:** p = 0.029, long-ward (Δ = +0.166).
2. **Raw convergence — PASS:** all 4 long-lived (1.583–1.995) exceed all 4 short-lived (1.452–1.568)
   — though by a thin margin (min-long 1.583 vs max-short 1.568).
3. **FDR — FAIL:** q = 0.86 (30 tests).
4. **NEGATOME — FAIL, decisively:** `enr/neg < 1` in **all 8 species** (0.60–0.88) — the interface
   diverges *less* than the generic tubulin baseline, which is itself hugely variable here
   (negatome ratios 1.8–3.3×). Crucially, **once normalized to that baseline the longevity edge
   disappears**: `enr/neg` for long-lived (0.60–0.88) no longer exceeds short-lived (0.65–0.87);
   min-long (0.60) is the *lowest* value overall. The raw convergence was riding on a generally
   hyper-variable surface, not an interface-specific longevity change.

### Method validation

- **164 / 270** (interface, species) rows show significant interface localization (BH q < 0.05) —
  strong, broad embedding signal.
- Shuffled-mask control ≈ 1.00 across all rows (0.996–1.027, mean 1.003).
- NEGATOME control populated for **270 / 270** in-panel rows.

## Interpretation

1. **Cross-module consistency:** two independent modules — DNA repair (SIRT6) and energy sensing
   (AMPK) — both give a **panel-wide negative** (0 interfaces survive FDR). The hypothesis that
   PPI interfaces diverge specifically in long-lived species is not supported in either.
2. **The value of NEGATOME:** AMPK produced the single strongest lead of the project (AMPKα2–β1,
   nominally significant *and* raw-convergent). It is exactly the kind of hit that a two-control
   pipeline would have flagged as a candidate — and it dissolves only under the NEGATOME baseline.
   Reporting it as a candidate without NEGATOME would have been a false positive.
3. No interface is a longevity-portability candidate on this panel.

## Limitations

- **NEGATOME** uses a single generic partner (β-tubulin) applied uniformly; per-source-protein
  NEGATOME-verified non-interactors would be stronger. (Here tubulin itself is highly variable at
  these interfaces, which is what exposes the 5iso lead — but a per-protein baseline is the rigorous
  version.)
- **Phylogenetic confounding** (as in SIRT6): three of five long-lived species are rodents.
- **Embedding proxy;** single structure per interface; Damaraland coverage thin (19 rows); five
  complexes dropped on chain-naming mismatches.

## Reproduce

```bash
uv run select --candidate-set ampk_pilot --count 20
uv run orthologs
uv run embed
uv run analyze                                             # shuffled control
cp data/input/ampk_negatome_control_pairs.csv data/interim/negatome_control_pairs.csv
uv run analyze                                             # populates NEGATOME (9 species)
```

Contrast + FDR + convergence computed from `data/output/enrichment.parquet` over
long = {elephant, naked_mole_rat, myotis_lucifugus, damaraland_mole_rat, blind_mole_rat},
short = {guinea_pig, rat, mouse, hamster}.
