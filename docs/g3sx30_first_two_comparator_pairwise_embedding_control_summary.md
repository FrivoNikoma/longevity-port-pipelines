# First two-comparator pairwise embedding-control summary

## Purpose

This checkpoint aggregates the committed human–elephant MDM2 baseline and two
committed comparator result pairs into one numerical summary.

It reads only committed CSV rows. It does not load any `.npy` embedding array,
perform a new inventory, select a comparator, or compute a new cosine
similarity.

This is a result-bearing aggregation checkpoint, not an inventory-only,
control-plan-only, approval, review, preparation, or scaffold layer.

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

All three source rows are loaded through their existing validators.

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
=0.8205658353778419

elephant control mean
=0.8306773919276025

human mean minus elephant mean
=-0.0101115565497606

absolute human–elephant control-mean difference
=0.0101115565497606
```

Four-value control panel summary:

```text
all-control mean
=0.8256216136527222

minimum control
=0.8095126148075514

maximum control
=0.8409825967886765

control range
=0.0314699819811251
```

Baseline separation:

```text
minimum baseline minus control delta
=0.1563488334452703

maximum baseline minus control delta
=0.1878188154263953

baseline_greater_than_all_four_controls=true
first_comparator_baseline_greater_than_both_anchors=true
second_comparator_baseline_greater_than_both_anchors=true
```

Matched-anchor differences:

```text
mean absolute human–elephant control difference
=0.0101115565497607

maximum absolute human–elephant control difference
=0.0108595722589772

anchor_ordering_consistent_across_comparators=true
```

The ordering flag means only that elephant-anchor control similarity is
numerically above human-anchor control similarity for both committed
comparators. It is not a biological interpretation.

## Interpretation boundary

The committed baseline is numerically greater than all four committed
control similarities, and the smallest observed baseline-minus-control delta
is `0.1563488334452703`.

Across the two comparators, the absolute human-versus-elephant matched-control
differences are approximately `0.00936` and `0.01086`.

These facts describe only the committed mean-pooled ESMC embedding-space
numbers. Two comparators do not form a validated biological negative-control
panel and do not establish biological specificity.

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

- a machine-readable summary schema;
- a one-row committed two-comparator numerical summary;
- a committed-row aggregator and validator;
- focused numerical and documentation tests;
- this result document;
- a current gate-map checkpoint.

## Next result-bearing step

```text
add_first_third_source_backed_independent_comparator_result_with_selection_frozen_in_same_step
```

A third comparator must be selected by a deterministic rule frozen before
similarity inspection, and selection plus numerical result must occur in the
same result-bearing step.

No inventory-only, control-plan-only, approval, review, runtime-preparation,
scaffold, or other non-result PR should be inserted before that concrete
result.
