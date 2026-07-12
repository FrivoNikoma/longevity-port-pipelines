# First matched elephant MDM2 independent control result

## Purpose

This result completes the matched-anchor use of the exact comparator frozen in
the preceding independent-control step.

The preceding row compared human MDM2 `Q00987` with the source-backed Brandt's
bat `P09874` candidate `EPQ16369.1`. This row switches only the anchor to
elephant MDM2 `G3SX30`. It does not run a new inventory and does not select a
different comparator after inspecting the earlier similarity.

## Frozen source

The result consumes:

`data/input/g3sx30_first_independent_pairwise_embedding_control_results.csv#1`

Required source facts include:

- comparator selection was frozen before similarity inspection;
- inventory similarity was not computed during selection;
- source accession: `P09874`;
- target accession: `EPQ16369.1`;
- target species: `brandts_bat`;
- target taxid: `109478`;
- comparator must remain frozen;
- the next step required the matched elephant MDM2 result.

## Local ignored artifacts

Elephant MDM2 anchor:

`data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`

- accession: `G3SX30`
- species: `Loxodonta africana`
- taxid: `9785`
- shape: `492x960`
- dtype: `float32`
- finite: `true`

Frozen comparator:

`data/output/embeddings/esmc-300m-2024-12/4xhu__A1_P09874--4xhu__B1_Q9UNS1_receptor_109478.npy`

- source accession: `P09874`
- target accession: `EPQ16369.1`
- species: `brandts_bat`
- taxid: `109478`
- shape: `1024x960`
- dtype: `float32`
- finite: `true`

Both arrays remain local, ignored, untracked, and uncommitted.

## Calculation

Both arrays are independently mean-pooled over their residue axes in `float64`.
Cosine similarity is then computed between the two mean vectors.

No residue alignment is performed.

## Numerical result

The committed result row is:

`data/input/g3sx30_first_matched_elephant_mdm2_independent_control_results.csv#1`

It records:

```text
baseline_human_elephant_mdm2_cosine_similarity=0.9973314302339468
human_mdm2_to_frozen_comparator_cosine_similarity=0.8316190559481323
elephant_mdm2_to_frozen_comparator_cosine_similarity=0.8409825967886765
baseline_minus_elephant_control_delta=0.1563488334452703
baseline_greater_than_elephant_control=true
human_control_minus_elephant_control_delta=-0.0093635408405441
absolute_human_elephant_control_similarity_difference=0.0093635408405441
elephant_anchor_mean_vector_l2_norm=0.8347860929210978
frozen_comparator_mean_vector_l2_norm=0.7998408962311685
```

The external detailed JSON had SHA256:

`4fe3e2ec90e83eb82a4e6ac792845259fec47c03f151e0f979cd2b4d71d73301`

The external JSON remains outside the repository.

## What this result establishes

For this one frozen comparator and this numerical representation:

- the human MDM2 to comparator cosine is `0.8316190559481323`;
- the elephant MDM2 to comparator cosine is `0.8409825967886765`;
- their absolute difference is `0.0093635408405441`;
- both are below the human-elephant MDM2 baseline of
  `0.9973314302339468`.

These statements describe only the committed embedding-space measurements.

## Claim boundary

This result is not a validated biological negative control.

It is not:

- residue alignment;
- interface analysis;
- a binding result;
- orthology proof;
- functional-equivalence evidence;
- longevity evidence;
- a biological claim.

A single shared comparator cannot establish biological specificity.

## Runtime and artifact boundary

This result:

- does not perform a new inventory;
- does not reselect the comparator;
- does not call Biohub or ESMC;
- does not generate an embedding;
- does not commit `.npy` arrays or raw embedding vectors;
- does not commit a `data/output` artifact;
- does not call Boltz, AF3, or Chai;
- does not rerun enrichment or contrast;
- does not promote Gate 8 or Gate 9;
- does not make a biological claim.

## Next result-bearing step

The next step is:

`add_first_additional_source_backed_independent_comparator_result_with_selection_frozen_in_same_step`

Any additional comparator selection must be frozen before its similarity is
inspected and must be encoded in the same result-bearing step. No separate
inventory-only, control-plan-only, approval, review, preparation, or scaffold
PR should be inserted first.
