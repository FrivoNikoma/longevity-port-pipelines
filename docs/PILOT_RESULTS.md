# Pilot results & roadmap

## The core metric: enrichment_ratio

```
enrichment_ratio = interface_mean_delta / noninterface_mean_delta
```

- **> 1** — interface changes more than background → *interface_divergent* (altered recognition / incompatibility risk)
- **< 1** — interface changes less than background → *interface_constrained* (preserved surface, safer to port)
- **≈ 1** — no localization → *weak_or_mixed*

Each row also carries a Mann-Whitney p-value, directional p-values, and Cohen's d.
The ratio alone can be inflated by a few extreme residues; the supporting statistics
guard against that.

## v2 pilot headline numbers

43 complexes, 13,415 residue-level deltas, 438 recurrent interface-residue candidates.

| Complex | Chain | Species | Enrichment | p-value | Cohen's d | Classification |
|---------|-------|---------|-----------|---------|-----------|----------------|
| 8bhv (XLF/NHEJ1, NHEJ repair) | ligand | naked mole-rat | ~2.59 | 4.55e-12 | 4.29 | interface_divergent |
| 8bhv (XLF/NHEJ1, NHEJ repair) | ligand | mouse | ~2.34 | 4.55e-12 | 3.80 | interface_divergent |
| 1nfi (RELA/p65, NF-kB) | receptor | — | moderate | — | — | interface_divergent |
| 4xhu (PARP1) | receptor | — | low | — | — | interface_constrained |

The signals fall in pathways central to aging: NHEJ DNA double-strand-break repair
(XLF/NHEJ1), NF-kB stress/inflammatory regulation (RELA), and PARP1-associated repair.

**Honest read:** the naked mole-rat and mouse signals at 8bhv are close (2.59 vs 2.34).
Both are non-human orthologs compared to the human reference, so both are expected to
diverge. The pilot shows the method detects interface-localized divergence — not yet
that the divergence is longevity-specific.

## Signal classification

The pipeline classifies each (complex, chain, species) row into one of:

- `interface_divergent` — enrichment > 1, significant
- `interface_constrained` — enrichment < 1, significant
- `interface_divergent_not_significant` — ratio > 1, but p-value too high
- `interface_constrained_not_significant` — ratio < 1, but p-value too high
- `weak_or_mixed` — no clear pattern

These map to biological outcomes:

| Classification | Biological interpretation |
|---------------|--------------------------|
| interface_divergent | possible_interface_remodeling_or_incompatibility |
| interface_constrained | maintained_candidate (safer to port) |
| not significant | possible_maintained_low_confidence |
| weak_or_mixed | unresolved |

## Known limitations

1. **Missing NEGATOME controls.** All 43 rows have `missing_negatome` status — the
   non-interacting-pair negative control is not yet populated. The shuffled-mask control
   passes, but NEGATOME is the stronger test. This is the main limitation.
2. **No longevity-specific contrast.** Enrichment is per-species vs human. The next step
   is a long-lived vs short-lived contrast — a candidate is only called longevity-relevant
   where long-lived species diverge and the short-lived one does not.
3. **Residue independence assumption.** The Mann-Whitney test treats residues as
   independent, but nearby residues are correlated. P-values are indicators of
   localization, not literal significance.

## Roadmap

The interface-divergence analysis is layer one. Four additional stages are planned:

1. **Unbiased discovery.** Structural phylogenetics (structural-rate convergence across
   independent long-lived lineages) + ESM Atlas neighborhood search to find candidates
   beyond the curated list.
2. **Porting hints (per-residue).** ESM C zero-shot scoring (per-position entropy,
   log-likelihood ratios) to flag which residues are safe to port into human context.
3. **Compatibility classification.** Co-fold the cross-species complex (AlphaFold3 /
   Boltz-2 / Chai-1) and classify as maintained / broken / incompatible.
4. **MD validation (top 5-10 candidates).** Short molecular-dynamics simulations
   (50-100 ns) on co-folded complexes to quantify interface stability — binding free
   energy estimates (MM-PBSA/GBSA), interface RMSF, contact survival rates. This
   bridges the gap between embedding-level signal and wet-lab binding assays: a
   candidate whose ortholog complex falls apart in simulation is deprioritised before
   synthesis. In-house MD capacity at the Institute of Biochemistry of the
   Romanian Academy (biochim.ro) makes this a zero-cost filter.
5. **Hybrid design.** For incompatible interfaces, use generative tools (ESM3,
   RFdiffusion, ProteinMPNN) to design chimeric variants that keep function while
   restoring a compatible interface.

### Wet-lab validation (if funded)

- **Adaptyv Bio** — cell-free expression + BLI/SPR binding assays (~21-day turnaround).
  Each ortholog tested against functional and regulatory partners, with wild-type controls.
- **Chimera design** — RFdiffusion / ProteinMPNN / ESM3 for incompatible interfaces,
  filtered in silico before synthesis, plus MD checks on top predicted complexes.
- **Functional assays** — DR-GFP (DNA repair), SA-beta-gal (senescence),
  oxidative-stress resistance for top hits.
