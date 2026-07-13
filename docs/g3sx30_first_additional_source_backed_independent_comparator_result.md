# First additional source-backed independent comparator result

## Purpose

This checkpoint records the first **additional** source-backed numerical
embedding-space comparator result for the human MDM2 `Q00987` and elephant MDM2
`G3SX30` pairwise lane.

Comparator selection and metric calculation occurred in one external step. The
deterministic eligibility and ranking rule was frozen before any similarity was
calculated:

```text
selection_rule_sha256=73199752734c03778885d063556804e2c3bcdef1f55f31b6aed52e8604d1c3a4
selection_rule_frozen_before_similarity=true
similarity_used_for_selection=false
selection_and_result_in_same_step=true
```

This is a result-bearing checkpoint, not an inventory-only, plan-only, review,
approval, runtime-preparation, or scaffold layer.

## Source checkpoint

The result consumes:

```text
data/input/g3sx30_first_matched_elephant_mdm2_independent_control_results.csv#1
```

Required source values include:

```text
matched_control_status=first_matched_elephant_mdm2_independent_control_result_created
baseline_human_elephant_mdm2_cosine_similarity=0.9973314302339468
human_mdm2_to_frozen_comparator_cosine_similarity=0.8316190559481323
elephant_mdm2_to_frozen_comparator_cosine_similarity=0.8409825967886765
next_step=add_first_additional_source_backed_independent_comparator_result_with_selection_frozen_in_same_step
```

## Deterministic selection result

The external selector inspected `216` pre-existing local ignored ESMC
embedding files. It found `101` candidates satisfying its source-backed technical eligibility rule.

The rank-1 comparator was:

```text
data/output/embeddings/esmc-300m-2024-12/8bot__U1_P13010--8bot__T1_P12956_receptor_9606.npy
```

Recorded technical properties:

```text
shape=642x960
dtype=float32
finite=true
taxid=9606
pdb_token=8bot
accession_tokens=P12956|P13010
selected_comparator_reuses_previous_comparator=false
```

The selector's exact tier-2 path reference was:

```text
tests/test_analyze_saved_embeddings_mapped.py
```

That test contains the exact expected embedding path. The selector did not use
similarity values to rank candidates.

## Supplemental committed provenance

After the result was produced, the selected context was also checked against:

```text
docs/sirt6_mini_pilot_v2_candidate_selection.md
```

That document records `8bot` as a `v1_selected` context with:

```text
source accession=P13010
partner accession=P12956
intermolecular contacts=732
```

This supplemental provenance confirms that `8bot / P13010 / P12956` is a
repository-visible curated analysis context. It was not used for the selection ranking and did not retroactively change the selected comparator.

## Numerical result

All three embedding matrices were independently mean-pooled over their residue
axes in `float64`. No residue alignment was performed.

```text
baseline human-elephant MDM2 cosine
=0.9973314302339468

human MDM2 to additional comparator cosine
=0.8095126148075514

elephant MDM2 to additional comparator cosine
=0.8203721870665286
```

Deltas from the human-elephant MDM2 baseline:

```text
baseline minus human additional control
=0.1878188154263953

baseline minus elephant additional control
=0.1769592431674182
```

Matched-anchor difference for this comparator:

```text
human additional control minus elephant additional control
=-0.0108595722589772

absolute human-elephant additional control difference
=0.0108595722589772
```

Mean-vector norms:

```text
human MDM2=0.8317611517806081
elephant MDM2=0.8347860929210978
additional comparator=0.9081312113564025
```

The external detailed result JSON had SHA256:

```text
0180102edc74a4cee7f82a54d337bc30079e8d9f414bfb78589620a056d62a6b
```

The external JSON remains outside the repository.

## Numerical interpretation boundary

For this additional comparator, both MDM2-to-comparator similarities are below
the committed human-elephant MDM2 baseline. The human and elephant control
values differ by approximately `0.01086`.

Together with the preceding frozen-comparator values:

```text
previous human control=0.8316190559481323
previous elephant control=0.8409825967886765
previous absolute anchor difference=0.0093635408405441
```

the second comparator provides another numerical embedding-space measurement
with a similar small human-versus-elephant matched-control difference.

This is still not sufficient to establish biological specificity. Two
comparators do not constitute a validated biological negative-control panel.

Explicitly, this result is:

- not a validated biological negative control;
- not residue alignment;
- not interface analysis;
- not a binding result;
- not orthology proof;
- not functional-equivalence evidence;
- not longevity evidence;
- not a biological claim.

## Runtime and artifact boundary

Explicitly, this checkpoint does not promote Gate 8 or Gate 9.

This checkpoint does not:

- call Biohub or ESMC;
- generate a new embedding;
- commit `.npy` arrays or raw embedding vectors;
- commit a `data/output` artifact;
- commit the external detailed JSON;
- call Boltz, AF3, or Chai;
- rerun enrichment or contrast;
- promote Gate 8 or Gate 9;
- make a biological claim.

## Repository-visible result

This checkpoint adds:

- a machine-readable result schema;
- a one-row committed numerical result table;
- a validator and local reproducer;
- focused result and documentation tests;
- this result document;
- a current gate-map checkpoint.

## Next result-bearing step

```text
add_first_two_comparator_pairwise_embedding_control_summary_before_interpretation
```

That step should aggregate the already committed baseline and both comparator
result pairs into one compact numerical summary. It must remain an
embedding-space result and must not infer biological specificity.

No inventory-only, control-plan-only, approval, review, runtime-preparation,
scaffold, or other non-result PR should be inserted before that concrete
summary.
