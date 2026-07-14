# First three-comparator pairwise embedding-control summary

## Purpose

This checkpoint aggregates the committed human–elephant MDM2 baseline and all
three committed comparator result pairs into one numerical summary.

It reads only committed CSV rows. It does not load any `.npy` embedding array,
perform a new inventory, select a comparator, or compute a new cosine
similarity.

This is a result-bearing aggregation checkpoint, not an inventory-only,
control-plan-only, approval-only, review-only, runtime-preparation-only, or
scaffold-only layer.

## Committed sources

Baseline:

```text
data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv#1
```

First matched comparator pair:

```text
data/input/g3sx30_first_matched_elephant_mdm2_independent_control_results.csv#1
```

Second comparator pair:

```text
data/input/g3sx30_first_additional_source_backed_independent_comparator_results.csv#1
```

Third comparator pair:

```text
data/input/g3sx30_first_third_source_backed_independent_comparator_results.csv#1
```

All four source rows are loaded through their existing validators. The three comparator artifact references must remain distinct.

## Source values

```text
human–elephant MDM2 baseline
=0.9973314302339468

first comparator:
human control=0.8316190559481323
elephant control=0.8409825967886765
absolute anchor difference=0.0093635408405441

second comparator:
human control=0.8095126148075514
elephant control=0.8203721870665286
absolute anchor difference=0.0108595722589772

third comparator:
human control=0.7472839682873271
elephant control=0.7516055327169140
absolute anchor difference=0.0043215644295869
```

## Aggregation method

Means use:

```text
math.fsum(values) / count
```

All committed decimal strings are parsed as Python `float`, and result fields
are formatted to 16 decimal places.

No embedding vectors or residue-level values participate in this aggregation.

## Numerical summary

Anchor-specific means:

```text
human control mean
=0.7961385463476702

elephant control mean
=0.8043201055240398

human mean minus elephant mean
=-0.0081815591763695

absolute human–elephant control-mean difference
=0.0081815591763695
```

Six-value comparator summary:

```text
all-control mean
=0.8002293259358551

minimum control
=0.7472839682873271

maximum control
=0.8409825967886765

control range
=0.0936986285013494
```

Baseline separation:

```text
minimum baseline minus control delta
=0.1563488334452703

maximum baseline minus control delta
=0.2500474619466196

baseline_greater_than_all_six_controls=true
first_comparator_baseline_greater_than_both_anchors=true
second_comparator_baseline_greater_than_both_anchors=true
third_comparator_baseline_greater_than_both_anchors=true
```

Matched-anchor differences:

```text
mean absolute human–elephant control difference
=0.0081815591763694

maximum absolute human–elephant control difference
=0.0108595722589772

elephant_control_greater_than_human_control_count=3
anchor_ordering_consistent_across_comparators=true
all_comparator_artifact_references_distinct=true
```

The ordering fields mean only that elephant-anchor similarity is numerically
above human-anchor similarity for all three committed comparators. They are not
a biological interpretation.

## Interpretation boundary

The committed human–elephant MDM2 baseline is numerically greater than all six
committed comparator similarities. The smallest baseline-minus-control delta
is `0.1563488334452703`, while the largest is `0.2500474619466196`.

The third comparator lowers the three-comparator means relative to the earlier
two-comparator summary, but the same elephant-above-human numerical ordering
remains present for all three comparator pairs.

These facts describe only committed whole-protein mean-pooled ESMC
embedding-space numbers. Three technical comparators do not form a validated
biological negative-control panel and do not establish biological specificity.

Explicitly, this result is:

- not a validated biological negative-control panel;
- not evidence of biological specificity;
- not residue alignment;
- not interface analysis;
- not a binding result;
- not orthology proof;
- not functional-equivalence evidence;
- not longevity evidence;
- not a biological claim.

The whole-protein comparators do not replace shuffled interface controls or a
curated NEGATOME control.

## Runtime and artifact boundary

This checkpoint:

- reads committed CSV rows only;
- does not load source embedding arrays;
- does not compute a new cosine similarity;
- does not perform a new inventory;
- does not select or reselect a comparator;
- does not call Biohub or ESMC;
- does not generate an embedding;
- does not read or commit `.npy` artifacts;
- does not commit raw embedding vectors;
- does not commit `data/output` artifacts;
- does not create an external result JSON;
- does not call Boltz, AF3, or Chai;
- does not rerun enrichment or contrast;
- does not promote Gate 8 or Gate 9;
- does not make a biological claim.

## Repository-visible result

This checkpoint adds:

- a machine-readable three-comparator summary schema;
- a one-row committed numerical summary;
- a committed-row aggregator and validator;
- focused numerical and documentation tests;
- this result document;
- a current gate-map checkpoint.

## Next result-bearing step

```text
add_first_tp53_mdm2_interface_ready_manifest_result
```

The next result must move from whole-protein calibration to a concrete
TP53/MDM2 interface-ready manifest. It must identify exact TP53 and MDM2 chains,
the interface-residue source, partner context, human reference, elephant
ortholog mapping, and structure-confidence policy before interface scoring.

No inventory-only, control-plan-only, approval-only, review-only,
runtime-preparation-only, scaffold-only, or other non-result PR should be
inserted before that manifest result.
