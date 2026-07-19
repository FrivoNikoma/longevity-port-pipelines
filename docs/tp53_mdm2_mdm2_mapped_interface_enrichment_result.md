# Scoped MDM2 mapped-interface enrichment result

## Scope

This checkpoint records three species-specific MDM2 technical enrichment rows:

1. elephant `G3SX30` (long-lived);
2. mouse `P23804` (short-lived control);
3. hamster `A0ABM2YB85` (short-lived control).

It creates input for a later Gate 8 disposition. It is not a
long-lived-vs-short-lived contrast and does not promote Gate 8 or Gate 9.

## Coordinate provenance

The structural interface originates from chain A of human TP53/MDM2 complex
`1YCR`. The extractor's observed-chain-local indices are translated through
`data/input/tp53_mdm2_1ycr_q00987_interface_mapping.csv` to full-length human
MDM2 `Q00987` zero-based coordinates before alignment to each target.

The committed mapping has canonical SHA-256
`73cc5548869e537cd90d78a3cf1a417097f85b9dde99818d8c09f96cce8aa325`.
All 47 source interface residues map to every target, with zero dropped or
unmapped residues. The selected first-optimal alignments have 9 tied optima
for `G3SX30`, 8 for `P23804`, and 2 for `A0ABM2YB85`; sensitivity to these
alternatives is deferred to A2.

## Primary metric

The metric family is
`human_reference_to_ortholog_per_residue_esmc_l2_mapped_interface_vs_noninterface_enrichment`.
For each aligned residue, the runner computes the Euclidean L2 distance
between the human and target ESMC residue vectors. Enrichment is the mean
distance at mapped interface residues divided by the mean distance at aligned
non-interface residues.

| Target | Aligned | Mapped interface | Interface mean | Non-interface mean | Ratio | Cohen's d | one-sided p (interface less) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| elephant `G3SX30` | 490 | 47 | 0.15222034793584904 | 0.25682065358835338 | 0.59271069444374358 | -0.56760338487777706 | 1.3014435494622037e-06 |
| mouse `P23804` | 483 | 47 | 0.17450980160464633 | 0.33908896827899399 | 0.51464311118804662 | -0.78297289815452131 | 1.4319184890115312e-09 |
| hamster `A0ABM2YB85` | 481 | 47 | 0.1880302554432382 | 0.31430748781438245 | 0.59823664002011123 | -0.65845373223330916 | 4.2167380961486949e-08 |

All three ratios are below 1.0. This is a technical interface-depletion result:
the mapped interface has a smaller human-to-target embedding shift than the
aligned non-interface background in this metric family.

It does not establish preserved binding, altered TP53 regulation, a longevity
mechanism, or a long-lived-lineage-specific effect.

## Metric-compatible shuffled control

Each target uses 1,000 masks sampled uniformly without replacement from the
aligned residue pairs. Every mask has exactly 47 residues, matching the actual
mapped interface count. NumPy `default_rng` uses deterministic seed `42`.

For all three targets, zero shuffled ratios are less than or equal to the
observed ratio and all 1,000 are greater than or equal to it. With add-one
empirical correction:

- lower-tail p = `0.000999000999000999`;
- two-sided p = `0.001998001998001998`.

Historical geometric shuffled compactness results are not reused. The
embedding-based NEGATOME result is also not numerically combined here because
its compatibility with this residue-level metric family remains unaudited.

## Artifact and claim boundaries

The exact external FASTA files and four `.npy` arrays remain local runtime
artifacts. No raw sequence, `.npy`, or `data/output` artifact is committed.

This checkpoint:

- made no Biohub/ESMC, Boltz, AF3, or Chai call;
- generated no new embedding;
- ran no long-lived-vs-short-lived Gate 8 contrast;
- ran no mapping/cutoff/alignment sensitivity;
- ran no leave-one-control-out or residue-block jackknife;
- retains the single-long-lived-lineage limitation;
- did not run a Gate 8 disposition;
- did not promote Gate 8 or Gate 9;
- made no biological claim.

## Next permitted action

The exact next action is:

`run_mapping_cutoff_and_alignment_sensitivity`

Later A3 must perform leave-one-control-out and residue-block jackknife checks.
Only a separate A4 disposition may decide whether the evidence is suitable for
Gate 8, explicitly retaining the single-long-lived-lineage limitation.
