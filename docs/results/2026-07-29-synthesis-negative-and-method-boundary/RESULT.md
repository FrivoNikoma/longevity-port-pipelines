# Synthesis — the convergent–divergent interface model is not supported, and the negative is localized to the method's molecular level

Date: 2026-07-29
Status: **synthesis of the completed series — a bounded negative result, not a validated biological claim.**
Scope: pulls together every lane and rigor check to date into one verdict, with the actual numbers and
an explicit account of what was ruled out and what was not.

---

## 1. One-paragraph verdict

Across **two predicted pathways × two experimental designs × three built-in controls**, the ESM
interface-divergence method returns **no FDR-surviving, cross-lineage longevity signal**. An
**orthogonal selection metric (dN/dS)** applied to the one recurring crumb agrees: sub-FDR, and finds
nothing itself. A **battery of five design/statistical rigor checks** — continuous phylogenetic
regression, all-lane pooling, a direction (constraint) test, a per-residue site-level test, and a
residue-class-stratified test — each reproduces the null. The negative is therefore **not** an
artifact of binary grouping, species non-independence, mass/lifespan confounding, interface averaging,
or residue-class pooling. It **localizes to the method's molecular level**: L2 divergence of ESM
embeddings at coding interfaces is not a detector of lineage-specific selection (dN/dS confirms this),
and the biology — where the project has any positive signal at all (HAS2 functional-axis rescue,
elephant TP53 dosage) — lives at a **regulatory / dosage level this metric does not see**.

---

## 2. The model under test

The convergent–divergent hypothesis proposes two routes to exceptional longevity with two different
molecular signatures, testable as elevated interface divergence in the long-lived group:

- **ELLSM** (extremely long-lived small mammals: mole-rats, bats) → intensified selection on
  **cellular maintenance / DNA repair**. Tested with the **SIRT6** DNA-repair panel.
- **BMAL** (big-bodied, long-lived: whales, elephant, rhino) → intensified selection on **cell-cycle
  / tumour-suppressor control** (Peto's paradox). Tested with the **cell_cycle** panel.
- **AMPK** (energy sensing) served as the model's **negative-control pathway**.

Strata (22 species + human anchor): ELLSM 5 (naked / Damaraland / blind mole-rat, *Myotis*, greater
horseshoe bat), BMAL 5 (elephant, blue whale, beluga, sperm whale, white rhino), Reference 12.

## 3. The method and its controls

Per-residue ESM-C (`esmc-300m-2024-12`) embeddings; interface = 8 Å inter-chain contacts;
`enrichment_ratio` = mean interface L2 delta / mean non-interface delta (ortholog vs human). Group
contrasts by Mann-Whitney U with **BH-FDR across interfaces**, plus three controls: shuffled-mask
(1000 permutations), NEGATOME (universal β-tubulin partner → specificity), and cross-lineage
convergence (min-long > max-short).

---

## 4. Results across the series

| Lane / test | design | outcome | reference |
|---|---|---|---|
| SIRT6 5×4 | pooled long-vs-short | negative, 0/26 FDR | PR #362 |
| AMPK 5×4 | pooled long-vs-short | negative, 0/30; 5iso lead killed by NEGATOME | prior |
| SIRT6 + AMPK stratified | ELLSM-vs-Ref, BMAL-vs-Ref, BMAL-vs-ELLSM | all 0/25–0/29 FDR | `../2026-07-28-*-stratified/` |
| **cell_cycle (BMAL-predicted)** | stratified, 15 interfaces | **0/28 FDR; direction inverted (BMAL more conserved)** | `../2026-07-29-cell-cycle-panel/` |
| **Ku80/8AG5 dN/dS (orthogonal)** | Nei–Gojobori, ELLSM-vs-Ref | **0/42 FDR; interface elevation is a surface effect** | `../2026-07-29-ku80-interface-dnds-orthogonal/` |

Key details:

- **cell_cycle** interfaces are *more conserved than the rest of the protein* (mean enrichment 0.90 <
  1) and sit below the shuffled (1.00) and NEGATOME (1.22) baselines — the opposite of a specific
  adaptive signal. The BMAL prediction fails **and its nominal direction is inverted**.
- **Ku80/8AG5** is Ku80's contact surface for the **vaccinia C10** antagonist (a host–virus interface,
  a priori a good place for diversifying selection). ELLSM ω = 0.72 is a low-synonymous-denominator
  artifact (pN_ELLSM 0.138 ≈ pN_Ref 0.125); the interface's 1.83× elevation over the whole protein
  falls to 1.56× (p = 0.12) against a solvent-exposure-matched background. Residues 246/262/368 are
  nominally ELLSM-ward but 0/42 survive FDR — the crumb dies at FDR on dN/dS **exactly as it did on
  ESM-L2**.

## 5. The single recurring crumb, closed on two metrics

Across every design the Ku80 interface was the one signal that reached nominal significance
ELLSM-ward and never survived FDR. Testing it with dN/dS — a metric that measures selection, not
embedding distance — reproduced the same verdict (nominal, sub-FDR) and added no new positive. Two
independent metrics converge on the same sub-FDR call for the same interface, which tightens the
negative rather than opening a lead.

## 6. Rigor battery — five ways the negative could have been an artifact, all ruled out

| Assumption that could hide a signal | Check | Result |
|---|---|---|
| Binary groups + species non-independence | continuous **PGLS** (divergence ~ log lifespan + log mass, Brownian VCV) | lifespan **p = 0.96** (embedding); Ku80 dN/dS raw 0.066 → **0.28** under mass+phylogeny |
| Single panel / low power | **all-lane PGLS**, pooled **52 interfaces** | lifespan **p = 0.73** |
| Wrong direction (constraint, not divergence) | long-lived-vs-reference at interfaces | neither: binomial **p = 0.21**, Wilcoxon **p = 0.36** |
| Interface mean masks a few adaptive sites | **site-level** PGLS, BH-FDR over sites | **0 / 5 618** interface residues survive FDR |
| Charged vs uncharged pooled | **class-stratified** FDR (charged/polar/aromatic/hydrophobic) | **0** in any class; classes ≈ equal in delta magnitude (0.385–0.414) |

Notable: phylogenetic correction *reduced* the one apparent hint (Ku80 dN/dS) rather than revealing
one — the direction expected when relatedness was inflating an effect. The rigor upgrades sharpened
the negative; none rescued a positive.

## 7. Where the negative localizes — the method boundary

The negative is **not** in the experimental design or the statistics; those were stress-tested five
ways. It localizes to the metric's **molecular level**:

- **ESM-L2 interface divergence ≠ lineage-specific selection.** The orthogonal dN/dS test confirms
  the crumb is sub-FDR on a genuine selection metric, and the interface "elevation" the embedding
  metric reports is largely **solvent exposure**, not adaptation.
- **The signal, if any, is at a different level.** Coding-interface divergence cannot capture
  regulatory change, gene dosage, isoform usage, or expression — and those are exactly where the
  project has its only positive leads (**HAS2** functional-axis sequence rescue; **elephant TP53**
  copy-number). A single ortholog's coding sequence also integrates selection over all tissues, so
  cell-type-specific proliferation biology is invisible to it by construction.

## 8. Limitations (honest boundaries of this synthesis)

- **Power.** n = 22 species with predictor collinearity r(log-lifespan, log-mass) = 0.70; a null is
  "not detected", not "proven absent".
- **Approximate inputs** for the PGLS: literature trait maxima and an approximate mammalian timetree.
- **dN/dS is one gene** (Ku80), counting-based (Nei–Gojobori), pairwise-vs-human; an ML branch-site
  model (codeml/HyPhy) across more genes would be the confirmatory step, though the raw signal already
  fails the mass + phylogeny control.
- **Lane reproduction.** Only SIRT6 and AMPK reproduced their own biology from the embedding cache;
  the tp53/igf/has2 panels collapsed to off-target cached interfaces under partner-aware selection and
  were used pooled-only. Their true modules were not re-tested at the PGLS/site level.
- **Level is untested directly.** We ruled out design and statistics, but did not positively test the
  regulatory/dosage level — that requires different data (expression, copy number), not this method.

## 9. Conclusion and what would move it

This is a **well-characterised negative**: the convergent–divergent interface-divergence model is not
supported for DNA-repair (ELLSM) or cell-cycle (BMAL) pathways, on either an embedding or a selection
metric, and the result is robust to every design and statistical variant we could apply. Its value is
the **localised cause** — the method measures the wrong molecular quantity for this biology, not that
the biology is absent.

Directions that could still find signal, in order of promise:
1. **Change the level** — regulatory/dosage/expression comparative analysis (the project's actual
   positives already point here).
2. **ML branch-site dN/dS** across each lane's lead proteins (CDS fetch per protein), to confirm the
   Ku80-style result generalises.
3. **Longevity-quotient phenotype** and larger species sampling to lift the n = 22 / collinearity
   power ceiling.

## 10. Provenance

Merged PRs: #362 (SIRT6), the AMPK/SIRT6 stratified runs, #364 (Ku80 dN/dS), #365 (cell_cycle),
#366 (PGLS continuous), #367 (PGLS all-lanes), #368 (site-level + class-stratified). Result
directories under `docs/results/2026-07-2[89]-*`. Analysis scripts under `scripts/` (`fetch_ku80_cds`,
`analyze_ku80_dnds`, `analyze_cell_cycle_contrasts`, `analyze_phylo_continuous`,
`analyze_phylo_all_lanes`, `analyze_site_level`, `analyze_site_level_byclass`, `filter_selection_to_cached`,
`check_embed_cache`). All `data/` intermediates are gitignored and regenerable.
