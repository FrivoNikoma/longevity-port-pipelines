# First independent pairwise embedding control result

This PR creates the first independent numerical embedding-space comparator for
the committed human MDM2 `Q00987` versus elephant MDM2 `G3SX30` pairwise lane.

The source baseline is:

- `data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv#1`

The source internal robustness result is:

- `data/input/g3sx30_first_controlled_human_elephant_mdm2_pairwise_embedding_robustness_checks.csv#1`

The new repo-visible result is:

- `data/input/g3sx30_first_independent_pairwise_embedding_control_results.csv#1`

This is a result-bearing numerical control PR, not an inventory-only,
control-plan-only, approval, review, preparation, or scaffold layer.

## Selection was frozen before similarity

The local inventory inspected 216 existing `.npy` files without calculating any
mean-pooled vectors, cosine similarities, distances, or other pairwise metrics.

The predefined eligibility rule required:

- an existing local ignored embedding;
- model `esmc-300m-2024-12`;
- a two-dimensional array with embedding dimension `960`;
- dtype `float32`;
- finite values;
- no `MDM2` or `TP53` in the artifact path;
- at least one exact committed reference;
- preference for taxid `9606`, followed by any other taxid;
- a lexicographic artifact-path tie-break inside a priority tier.

The inventory recorded:

```text
selection_rule_frozen_before_similarity = true
inventory_similarity_computed = false
inventory_embedding_file_count = 216
inventory_technical_candidate_count = 1
```

Exactly one artifact satisfied the frozen technical rule:

```text
data/output/embeddings/esmc-300m-2024-12/4xhu__A1_P09874--4xhu__B1_Q9UNS1_receptor_109478.npy
```

The comparator was selected before its similarity to human MDM2 was known.

## Comparator provenance

The selected artifact is the curated Brandt's bat receptor candidate for the
human/reference source accession `P09874`:

```text
source_accession = P09874
target_accession = EPQ16369.1
target_accession_db = NCBI Protein
target_species = brandts_bat
target_taxid = 109478
complex_id = 4xhu__A1_P09874--4xhu__B1_Q9UNS1
chain = receptor
model = esmc-300m-2024-12
```

Committed provenance documents confirm:

- the curated candidate identity;
- `curated status: primary_candidate`;
- a unique matching coverage row;
- successful live ESMC generation;
- shape `1024x960`;
- dtype `float32`;
- finite values;
- the exact canonical artifact path.

The comparator is biologically distinct from MDM2 and comes from another
candidate lane, but this PR does **not** label it a validated biological
negative control. It is an independent embedding-space comparator selected by
the frozen rule.

## Calculation

The anchor is the existing local ignored human MDM2 `Q00987` embedding:

```text
shape = 491x960
dtype = float32
finite = true
```

The comparator embedding records:

```text
shape = 1024x960
dtype = float32
finite = true
```

Each matrix is independently mean-pooled over its residue axis to obtain one
960-dimensional vector. Cosine similarity is calculated in `float64` and
recorded to 16 decimal places. No residue alignment is performed.

## Numerical result

```text
baseline_mdm2_cosine_similarity = 0.9973314302339468
independent_control_cosine_similarity = 0.8316190559481323
baseline_minus_control_delta = 0.1657123742858144
baseline_greater_than_independent_control = true
independent_control_status =
first_independent_pairwise_embedding_control_result_created
control_result_created = true
```

The external detailed result JSON has SHA256:

```text
577b0b24c6a0657c78e0db2ab8b71499cf8dd2a5dd72b6ee33c241058bdbcf23
```

The external JSON remains outside the repository.

The numerical observation is limited to this selected comparator: the
human-elephant MDM2 baseline similarity is higher than the human-MDM2-to-P09874
comparator similarity by `0.1657123742858144`.

## Interpretation boundary

This is a numerical embedding-space independent comparator only.

It is:

- not a validated biological negative control;
- not residue alignment;
- not interface analysis;
- not a binding result;
- not orthology proof;
- not functional-equivalence evidence;
- not longevity evidence;
- not a biological claim.

One independent comparator is insufficient to establish specificity,
functional conservation, binding equivalence, or a longevity mechanism.

## Runtime and repository boundary

This PR records:

```text
biohub_esmc_called = false
new_embedding_generated = false
npy_artifact_committed = false
raw_embedding_vectors_committed = false
data_output_artifact_committed = false
boltz_called = false
af3_called = false
chai_called = false
enrichment_rerun = false
contrast_rerun = false
gate8_promoted = false
gate9_promoted = false
biological_claim_made = false
```

Both `.npy` matrices remain local, ignored, untracked, and uncommitted. The
inventory JSON, inventory CSV, and detailed control JSON remain outside the
repository.

## Next result-bearing step

The next concrete result is:

```text
add_first_matched_elephant_mdm2_independent_control_result_before_interpretation
```

That step should use elephant MDM2 `G3SX30` as the anchor and reuse the same
already frozen Brandt's bat `P09874` comparator. It must not reselect a
comparator after seeing the current metrics.

No control-plan-only, inventory-only, approval, review, runtime-preparation,
scaffold, or other non-result PR should be inserted before that concrete
numerical result.
