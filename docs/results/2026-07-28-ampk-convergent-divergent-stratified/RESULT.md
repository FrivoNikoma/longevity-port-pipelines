# AMPK module — convergent-divergent stratified contrast (BMAL / ELLSM / Reference)

Date: 2026-07-28
Candidate set: `ampk_pilot`
Status: **technical checkpoint / preliminary result — not a validated biological claim.**
Supersedes the pooled 5×4 AMPK contrast (`../2026-07-28-ampk-module-5x4/`) with a
phylogenetically-broader, strategy-stratified design.

## Motivation

Recent comparative work argues that mammalian longevity is a **convergent phenotype reached through
divergent molecular strategies**: extremely long-lived *small* mammals (ELLSM: mole-rats, bats) show
*intensified* selection for cellular maintenance (DNA repair, autophagy), whereas *body-mass-associated*
long-lived mammals (BMAL: elephants, whales, rhino) show genome-wide *relaxed* selection with
constraint concentrated on cell-cycle and DNA-repair pathways, with limited overlap between the two.

If longevity strategies are divergent, then **pooling all long-lived species into one group can
cancel signal**. This analysis therefore replaces the pooled "long vs short" contrast with three
stratified tests and a phylogenetically broad reference group.

## Design

Groups (only species with ortholog coverage retained after scoping):

- **ELLSM (5):** naked mole-rat, Damaraland mole-rat, blind mole-rat (*three independent
  subterranean-rodent lineages*), *Myotis lucifugus* and greater horseshoe bat (*two independent bat
  lineages* — Yangochiroptera vs Yinpterochiroptera).
- **BMAL (5):** African elephant, blue whale, beluga, sperm whale, white rhino (*first real
  large-bodied stratum in this project* — whales/rhino had zero coverage before).
- **Reference (12):** mouse, rat, hamster, guinea pig, rhesus, sheep, opossum, dog, mouse lemur,
  ground squirrel, hedgehog, cat — a phylogenetically broad "typical lifespan-for-size" comparison
  spanning primates, rodents, carnivores, ungulates, eulipotyphlans and a marsupial.

Contrasts (Mann-Whitney U on per-species `enrichment_ratio`, two-sided, BH-FDR across interfaces;
clean convergence = one group's values entirely above/below the other's):

1. **ELLSM vs Reference** — is the small-bodied maintenance stratum divergent at AMPK interfaces?
2. **BMAL vs Reference** — is the large-bodied stratum divergent?
3. **BMAL vs ELLSM** — direct test of the *divergent-strategies* prediction.

Method otherwise identical to prior AMPK runs (per-residue ESM C `esmc-300m-2024-12` embeddings,
BLOSUM62 alignment, interface = 8 Å inter-chain contacts). 625 rows across 22 species. Config species
groups live in `config.py` (`_BMAL_NAMES` / `_ELLSM_NAMES` / `_REFERENCE_NAMES`).

## Results — robust negative across all three contrasts

| Contrast | interfaces | min p | min BH q | q<0.05 | clean convergence |
|---|---|---|---|---|---|
| ELLSM vs Reference | 28 | 0.058 | 0.73 | **0** | 0 |
| BMAL vs Reference | 29 | 0.041 | 0.41 | **0** | 0 |
| BMAL vs ELLSM | 27 | 0.016 | 0.21 | **0** | 2 (die at FDR) |

Nothing survives FDR in any contrast. The direct **BMAL-vs-ELLSM** test — the one that should be most
sensitive if the two strata use divergent strategies at these interfaces — is also null (0/27; the
two clean separations, `6no7` ligand and `8soi` receptor, both sit at q = 0.21).

### The denser reference dissolves the earlier lead (design validation)

The pooled 5×4 analysis flagged **AMPKα2–β1 (`5iso`, receptor)** as the strongest lead of the project
(p = 0.029, long-ward, clean raw convergence over 4 short-lived). Under this design it dissolves:

| Group | n | mean enrichment | range |
|---|---|---|---|
| ELLSM | 4 | 1.698 | 1.583–1.995 |
| BMAL | 4 | 1.601 | 1.571–1.633 |
| Reference (12) | 12 | 1.559 | 1.434–1.615 |

ELLSM-vs-Reference p rises from 0.029 (vs 4 rodent-heavy short-lived) to **0.078** (vs 12
phylogenetically broad reference), and the groups now overlap (ELLSM min 1.583 < Reference max 1.615)
— no clean separation. Broadening the reference from a narrow, rodent-dominated short group to 12
lineages **removed a lead that was tracking phylogeny**, which is exactly what the design is meant to do.

### Method validation

- **366 / 625** (interface, species) rows show significant interface localization (BH q < 0.05) — the
  embedding signal is strong and broad; the null is not a power/artifact failure of the metric.
- Shuffled-mask control ≈ 1.00 across all rows (0.996–1.031, mean 1.003).

## Interpretation

1. **AMPK interfaces show no longevity-strategy signal** under the strongest design used so far —
   not for ELLSM, not for BMAL, and not between them.
2. **A null for AMPK is consistent with the convergent-divergent model**, which predicts stratum-specific
   signal in *maintenance / DNA-repair* (ELLSM) and *cell-cycle* (BMAL) pathways — **AMPK (energy
   sensing) is neither**. AMPK here is effectively the *negative-control pathway* for the model.
3. The result also flags a **scope limit of the method**: lineage-specific selection intensity
   (dN/dS-style signals those papers detect) is a different quantity than per-residue ESM-embedding
   divergence at a PPI interface. This panel/metric may simply not capture the divergent-strategy signal.
4. **Design validation is the concrete positive:** a phylogenetically broad, strategy-stratified panel
   dissolves the pooled-design's strongest lead, confirming it was clade-driven.

**The decisive test of the model is the SIRT6 DNA-repair panel under this same design** — that is the
pathway where ELLSM-specific interface divergence is actually predicted. Re-running SIRT6 with these
BMAL/ELLSM/Reference groups is the recommended next step.

## Limitations

- 5 vs 12 is well-powered (MWU floor ≈ 3×10⁻⁴), but 5 per long-lived stratum still limits per-lineage
  resolution; BMAL/ELLSM coverage is uneven per interface.
- Embedding proxy; single structure per interface; no NEGATOME applied here (not needed for a null —
  it is a specificity control for a *positive* lead).
- BMAL/ELLSM is a body-mass / strategy split, **not** a formal phylogenetic-independent-contrast; a
  tree-based continuous-trait PIC remains a further refinement.

## Reproduce

```bash
# config.py carries BMAL/ELLSM/Reference species + *_NAMES groups
uv run select --candidate-set ampk_pilot --count 20
uv run orthologs        # scope coverage across the expanded panel
uv run embed
uv run analyze          # enrichment.parquet (625 rows), shuffled control
```

Three stratified contrasts + BH-FDR + convergence computed from `data/output/enrichment.parquet` over
ELLSM = {naked_mole_rat, damaraland_mole_rat, blind_mole_rat, myotis_lucifugus, greater_horseshoe_bat},
BMAL = {elephant, blue_whale, beluga, sperm_whale, white_rhino},
Reference = {mouse, rat, hamster, guinea_pig, rhesus, sheep, opossum, dog, mouse_lemur,
ground_squirrel, hedgehog, cat}.
