# Elephant p53-R9 accession-first checkpoint

Date: 2026-07-27

Repository base: `06506c939458d4f626839b7cb3f32c6ca98be671`

## Primary result

- Study label: `p53-R9`
- GenBank accession: `KF715863.1`
- Working protein length: `180 aa`
- BOX-I state: `W23G`
- Normalized protein SHA-256:
  `5513900767cd0d62d981f298e6960f8f80b753252c660d0fcaef4e91ecf685ef`

Homology-guided reconstruction recovered `W23G` in all 18
audited `KF715855.1-KF715872.1` records. This is a
family-level MDM2-binding-core change and is not by itself
copy-discriminating.

## Identity decision

Cross-study labels `RTG9` and `TP53RTG12` are not treated as
stable identifiers. The eLife peer-review response reports
100% nucleotide and protein identity between Abegglen RTG9
and the Sulak TP53RTG12 sequence.

The checkpoint therefore uses accession plus a hashed working
sequence as the primary identity. The exact
expression-plasmid insert sequence was not independently
recovered.

## Excluded technical comparator

A homology-guided 168-aa reconstruction from `KF715866.1`
was produced during exploratory analysis. It is not included
as a biological TP53RTG12 comparator in this checkpoint,
because the exact historical expression construct was not
independently recovered and cross-study ordinal names are
inconsistent.

## Functional interpretation

Published work supports a mitochondrial Tid1/Bax-associated
apoptotic function for p53-R9 after heterologous expression.
Published TP53RTG12 experiments support interaction with TP53
and lack of detected interaction with MDM2.

These observations motivate a beneficial-breakage hypothesis,
but do not establish that `W23G` causes the mitochondrial
phenotype.

## Decision

- Result class:
  `positive_sequence_resolved_candidate`
- Primary candidate:
  `KF715863.1 / p53-R9 / 180 aa / W23G`
- Full-family embedding campaign:
  `not_justified`
- Exact next experiment:
  compare p53-R9 WT with `G23W` reversion.

Required readouts:

- MDM2 binding;
- stability and ubiquitination;
- Tid1 and Bax interaction;
- mitochondrial localization;
- apoptosis.

Include a matched 180-aa canonical elephant TP53 truncation
control.

## Causal experiment package

This checkpoint now includes a pre-specified experiment that
resolves the main biological uncertainty rather than launching
a full-family embedding campaign.

The primary contrast is:

`p53-R9 WT (G23)` versus `p53-R9 G23W`.

The package also includes matched 180-aa canonical elephant
TP53 truncation controls so that a W23G effect can be
distinguished from a generic effect of losing the C-terminal
half of TP53.

Evidence is assigned to three claim tiers:

1. `binding_causal`: `G23W` restores MDM2 association in
   orthogonal assays;
2. `regulatory_causal`: binding rescue changes p53-R9
   regulation or its guardian effect on canonical TP53;
3. `phenotype_causal`: the regulatory effect changes
   abundance-adjusted apoptosis or TP53 signaling and is not
   fully explained by matched truncation controls.

Because the 180-aa p53-R9 protein lacks the predominant
C-terminal p53 ubiquitination sites, unchanged turnover does
not by itself refute restored MDM2 binding.

The package separately tests the guardian and Tid1/Bax
mitochondrial mechanisms and records the published conflict
over whether the retrogene protein binds MDM2.

See:

- `experiment_spec.md`
- `construct_panel.csv`
- `causal_hypotheses.csv`
- `claim_tiers.csv`
- `readout_decision_table.csv`
- `published_evidence_conflicts.csv`

## Claim boundaries

- Homology-guided reconstruction is technical sequence
  evidence, not endogenous expression evidence.
- Heterologous expression does not establish organism-level
  longevity causality.
- `W23G` has not yet been shown to cause the p53-R9
  mitochondrial phenotype.
- No BioHub, ESMC embedding, Boltz or structural-model call
  was performed for this checkpoint.

## Sources

- Abegglen et al. 2015:
  `10.1001/jama.2015.13134`
- Sulak et al. 2016:
  `10.7554/eLife.11994`
- Preston et al. 2023:
  `10.1038/s41420-023-01348-7`
