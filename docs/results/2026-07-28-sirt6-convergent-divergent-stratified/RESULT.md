# SIRT6 DNA-repair module — convergent-divergent stratified contrast (the decisive test)

Date: 2026-07-28
Candidate set: `sirt6_dna_repair`
Status: **technical checkpoint / preliminary result — not a validated biological claim.**
Companion to `../2026-07-28-ampk-convergent-divergent-stratified/` (same BMAL / ELLSM / Reference
design). Supersedes the pooled 5×4 SIRT6 contrast (`../2026-07-28-sirt6-panel-5x4-powered/`).

## Why this is the decisive test

The convergent-divergent model predicts that **extremely long-lived small mammals (ELLSM)** show
*intensified* selection specifically in **cellular-maintenance / DNA-repair** pathways. SIRT6 is a
DNA-repair panel, so **ELLSM-vs-Reference here is the contrast where a positive is actually
expected**. The AMPK companion was the model's negative-control pathway (energy sensing); this is the
predicted-positive pathway.

## Design

Identical strata to the AMPK stratified run (all species covered ≥20 orthologs for SIRT6):

- **ELLSM (5):** naked mole-rat, Damaraland mole-rat, blind mole-rat, *Myotis lucifugus*, greater
  horseshoe bat (3 independent mole-rat + 2 independent bat lineages).
- **BMAL (5):** African elephant, blue whale, beluga, sperm whale, white rhino.
- **Reference (12):** mouse, rat, hamster, guinea pig, rhesus, sheep, opossum, dog, mouse lemur,
  ground squirrel, hedgehog, cat.

Per-residue ESM C (`esmc-300m-2024-12`) embeddings, BLOSUM62 alignment, interface = 8 Å inter-chain
contacts. 558 rows across 22 species. Three contrasts by Mann-Whitney U, BH-FDR across interfaces,
plus clean-convergence check. Modules: NHEJ (Ku70/Ku80 8bot, Ku80 8ag5), apoptosis (caspase-3
7xn5/1i3o, Bcl-xL 2mej), p53 regulation (2h1l/2ruk/6yn1, …), inflammation (RELA/IκBα 1nfi),
kinase (ERK2 4iz5).

## Results — the predicted positive does not appear

| Contrast | interfaces | min p | min BH q | q<0.05 | clean convergence |
|---|---|---|---|---|---|
| **ELLSM vs Reference** | 25 | 0.014 | 0.34 | **0** | 0 |
| BMAL vs Reference | 25 | 0.019 | 0.32 | **0** | 0 |
| BMAL vs ELLSM | 25 | 0.008 | 0.099 | **0** | 2 (die at FDR) |

**ELLSM-vs-Reference on the DNA-repair panel is null: 0 / 25 interfaces survive FDR**, no clean
cross-lineage convergence. The lowest ELLSM-vs-Reference p (7xn5 caspase-3 ligand, p = 0.014) is in
the *lower* direction (ELLSM 0.768 < Reference 0.901 — more constrained, not more divergent). The
closest anything comes to significance anywhere is BMAL-vs-ELLSM min q = 0.099 (7xn5 ligand and 1i3o
receptor, both apoptosis-module, BMAL > ELLSM), still short of FDR.

**Recurring crumb — Ku80 / 8ag5.** The NHEJ Ku80 interface again ranks as the top nominal
ELLSM-ward signal (ELLSM 1.221 > Reference 1.145, p = 0.049, q = 0.43) — the same interface that
reached nominal significance at 3×3 and 5×4. Across every design it is long-ward at the nominal
level, but it never survives FDR and never shows clean convergence (bats/whales do not follow the
mole-rat lineages). It is the single most persistent weak signal in the project, and it remains a weak
signal.

### Method validation

- **255 / 558** (interface, species) rows show significant interface localization (BH q < 0.05) —
  the embedding signal is strong; the null is not a metric/power failure.
- Shuffled-mask control ≈ 1.00 across all rows (0.996–1.03, mean 1.001).

## Interpretation

1. **The decisive prediction fails.** On the pathway where the convergent-divergent model expects an
   ELLSM-specific signal (DNA repair), stratified ELLSM-vs-Reference is null (0/25 FDR). Stratifying
   by strategy did not convert the negative into a positive on its best-case pathway.
2. **Cross-module, cross-design consistency.** Two pathways (AMPK energy-sensing, SIRT6 DNA-repair) ×
   two designs (pooled long-vs-short, strategy-stratified) all give panel-wide nulls. The interface-
   divergence hypothesis is not supported, robustly.
3. **The negative localizes to the method, not (only) the biology.** Comparative-genomics studies
   detect the divergent-strategy signal via *lineage-specific selection intensity* (dN/dS, RELAX-type
   tests) and transcriptomics. Per-residue **ESM-embedding L2 divergence at a PPI interface is a
   different quantity** and does not appear to capture that signal in this panel. This is an
   informative scope conclusion: interface-embedding divergence is the wrong readout for
   lineage-specific longevity selection, at least at this panel size.
4. Ku80/8ag5 is the one interface worth revisiting with an orthogonal method (e.g. site-level
   dN/dS on the NHEJ core), given it is persistently long-ward — but it is not a hit here.

## Limitations

- 5 per long-lived stratum vs 12 reference is well-powered at the group level (MWU floor ≈ 3×10⁻⁴) but
  thin for per-lineage resolution; single structure per interface; embedding proxy.
- No NEGATOME applied (a specificity control for *positive* leads; there are none).
- Strategy split is body-mass-based, not a formal phylogenetic-independent-contrast.

## Reproduce

```bash
uv run select --candidate-set sirt6_dna_repair --count 20
uv run orthologs        # 5 ELLSM × 5 BMAL × 12 Reference all covered ≥20
uv run embed
uv run analyze          # enrichment.parquet (558 rows), shuffled control
```

Three stratified contrasts + BH-FDR + convergence computed from `data/output/enrichment.parquet` over
ELLSM = {naked_mole_rat, damaraland_mole_rat, blind_mole_rat, myotis_lucifugus, greater_horseshoe_bat},
BMAL = {elephant, blue_whale, beluga, sperm_whale, white_rhino},
Reference = {mouse, rat, hamster, guinea_pig, rhesus, sheep, opossum, dog, mouse_lemur,
ground_squirrel, hedgehog, cat}.
