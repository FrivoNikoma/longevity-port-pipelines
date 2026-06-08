# SIRT6 mini-pilot biology report

## 1. Purpose

This mini-pilot tests whether protein-language-model embedding shifts are enriched or depleted at mapped protein interaction interfaces in longevity-relevant complexes.

The core biological question is:

> Do interface residues in DNA repair and chromatin-related complexes show a distinct cross-species embedding signal compared with non-interface residues?

In this first mini-pilot, the strongest emerging pattern is not broad interface divergence, but **interface constraint**: many interface residues show lower embedding-space divergence than non-interface residues. This suggests that interaction surfaces in these complexes may be under stronger functional constraint than the rest of the protein.

## 2. Complexes analyzed

The mini-pilot currently includes three structural complexes.

### 8bot: Ku70 / Ku80

- Receptor side: P13010, Ku70 / XRCC6
- Ligand side: P12956, Ku80 / XRCC5
- Biological process: DNA double-strand break repair, especially non-homologous end joining (NHEJ)

Ku70 and Ku80 form a heterodimer that binds DNA double-strand break ends and helps recruit downstream NHEJ repair machinery. This complex is highly relevant to longevity biology because DNA double-strand break repair is one of the central mechanisms repeatedly implicated in long-lived species.

### 7s68: PARP1 / PARP1

- Both sides: P09874, PARP1
- Biological process: DNA damage sensing and poly-ADP-ribosylation

PARP1 detects DNA damage and helps recruit or regulate repair machinery through poly-ADP-ribosylation. In this mini-pilot, it serves as another DNA damage response complex, complementary to Ku70/Ku80.

### 8f86: SIRT6 / Histone H3

- Receptor side: Q8N6T7, SIRT6
- Ligand side: P84233, Histone H3
- Biological process: chromatin regulation, DNA repair, histone-associated enzymatic activity

SIRT6 is a central benchmark for this project because comparative studies in long-lived species suggest that SIRT6 activity is connected to more efficient DNA double-strand break repair. The SIRT6 / Histone H3 complex links the pipeline to chromatin context, not just soluble protein-protein interactions.

## 3. Chain-pair QC results

A key technical issue was that some structures contain multiple copies of the same proteins. Sequence-only mapping can therefore select chains that are correct by sequence but wrong in 3D space.

This was observed in 8bot: the structure contains two Ku70-like chains and two Ku80-like chains. Some sequence-compatible pairs do not physically contact each other.

The mapped chain-pair selection was updated to choose spatially contacting pairs among sequence-compatible candidates.

Current QC results:

| PDB | Complex | Selected chains | Interface R | Interface L | Atom contacts | Status |
|---|---|---:|---:|---:|---:|---|
| 8bot | Ku70 / Ku80 | U / T | 316 | 283 | 48543 | ok |
| 7s68 | PARP1 / PARP1 | A / B | 25 | 53 | 3315 | ok |
| 8f86 | SIRT6 / Histone H3 | K / A | 44 | 10 | 2450 | ok |

Biological interpretation:

- 8bot has a large, dense Ku70/Ku80 interface, consistent with a stable repair heterodimer.
- 7s68 has a smaller PARP1/PARP1 interface.
- 8f86 has a compact SIRT6/H3 interface, consistent with a more localized chromatin or substrate-recognition contact.

## 4. Embedding signal classification

The enrichment analysis compares per-residue embedding deltas at interface residues versus non-interface residues.

The directional Mann-Whitney tests now distinguish two biologically different cases:

- `interface_divergent`: interface deltas are larger than non-interface deltas.
- `interface_constrained`: interface deltas are smaller than non-interface deltas.

Current mini-pilot signal counts:

| Signal class | Count |
|---|---:|
| interface_constrained | 8 |
| weak_or_mixed | 5 |
| interface_divergent | 1 |
| interface_divergent_not_significant | 1 |

Main observation:

> The dominant signal in this mini-pilot is **interface constraint**, not interface divergence.

This means that, across the current DNA repair / chromatin-related complexes, interface residues often show lower embedding-space divergence than the non-interface background.

## 5. Strongest constrained signals

The strongest constrained signals are:

| Complex | Chain | Target species | Enrichment ratio | Effect size | Interpretation |
|---|---|---|---:|---:|---|
| 8bot | Ku70 / receptor | mouse | 0.747 | -0.680 | Ku70 interface is more conserved than background |
| 7s68 | PARP1 / ligand | myotis_lucifugus | 0.696 | -0.640 | PARP1 interface is more conserved than background |
| 7s68 | PARP1 / ligand | mouse | 0.766 | -0.607 | PARP1 interface is more conserved than background |
| 8bot | Ku70 / receptor | naked_mole_rat | 0.775 | -0.559 | Ku70 interface is more conserved than background |
| 7s68 | PARP1 / ligand | naked_mole_rat | 0.791 | -0.549 | PARP1 interface is more conserved than background |
| 8f86 | SIRT6 / receptor | mouse | 0.671 | -0.525 | SIRT6/H3-contacting region is more conserved than background |
| 8f86 | SIRT6 / receptor | naked_mole_rat | 0.593 | -0.492 | SIRT6/H3-contacting region is more conserved than background |
| 8bot | Ku70 / receptor | myotis_lucifugus | 0.790 | -0.504 | Ku70 interface is more conserved than background |

Biological interpretation:

These results suggest that the interaction surfaces of Ku70, PARP1, and SIRT6 may be more constrained than the rest of the protein. This is plausible because these proteins participate in essential DNA repair and chromatin-regulatory machinery, where disrupting interaction interfaces may be functionally costly.

## 6. Divergent candidate

The clearest interface-divergent signal is:

| Complex | Chain | Target species | Enrichment ratio | Effect size | Interpretation |
|---|---|---|---:|---:|---|
| 8bot | Ku80 / ligand | mouse | 1.130 | +0.253 | Ku80 interface differs more than background |

Interpretation:

The Ku80 side of the Ku70/Ku80 interface in mouse shows a statistically supported but moderate interface-divergent signal. This could reflect local interface remodeling, species-specific tuning, or a region where embedding changes are concentrated near the interaction surface.

This is currently the main divergent candidate in the mini-pilot, but the effect size is modest compared with the strongest constrained signals.

## 7. Current biological takeaway

The first mini-pilot does not yet identify a new longevity gene or a validated causal mechanism. However, it does show that the pipeline can detect structured, biologically interpretable embedding signals at real protein interfaces.

The strongest current conclusion is:

> In the current DNA repair / chromatin mini-pilot, protein interaction interfaces often appear more conserved in embedding space than non-interface regions.

This supports the idea that interface-aware structural analysis can separate functionally constrained interaction surfaces from the rest of the protein. That is an important intermediate result for the broader LongevityPort proposal.

## 8. Working biological model

The current results suggest a three-class model for future analysis:

1. **Maintained interface**
   - Interface residues are less divergent than background.
   - Interpretation: the interaction surface is functionally constrained and likely must be preserved.

2. **Adaptive interface divergence**
   - Interface residues are more divergent than background.
   - Interpretation: the interaction surface may be remodeled in a species-specific or longevity-associated way.

3. **Possible incompatibility**
   - Interface residues diverge strongly in a way that may disrupt cross-species transfer.
   - Interpretation: engineering or compensatory mutations may be needed to preserve interaction compatibility.

The current mini-pilot mostly supports class 1, with one candidate for class 2.

## 9. Limitations

This is still a small pilot, and several limitations remain:

- Only three complexes are included.
- The target species set is still small.
- Embedding deltas are not direct biochemical binding energies.
- Interface contact counts depend on the structural model and distance cutoff.
- Histone H3 ortholog mapping is currently missing for the 8f86 ligand side.
- The current analysis does not yet localize the strongest contributing residues within the interface.
- The current results should be treated as hypothesis-generating, not as causal evidence.

## 10. Next steps

Recommended next computational steps:

1. Add residue-level export for interface and non-interface deltas.
2. Rank individual residues by contribution to constrained or divergent signals.
3. Map top residues back onto structures for visual inspection.
4. Expand the mini-pilot to more DNA repair and chromatin complexes.
5. Compare long-lived species against short-lived controls more systematically.
6. Add pathway-level summaries: DNA repair, chromatin, proteostasis, inflammatory signaling.
7. Distinguish maintained-interface candidates from adaptive-divergence candidates.
8. Later, connect candidate interface changes to structural modeling and protein engineering workflows.

## 11. Short summary

The mini-pilot now produces a reproducible, QC-controlled interface embedding analysis. After correcting chain-pair selection and adding directional per-residue statistics, the dominant signal is interface constraint in DNA repair and chromatin-related complexes. This suggests that the method can detect biologically meaningful conservation of interaction surfaces, with Ku70/Ku80, PARP1, and SIRT6/H3 serving as initial proof-of-concept cases.
