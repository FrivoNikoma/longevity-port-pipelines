# First controlled human-elephant MDM2 pairwise embedding robustness check

This PR creates the first numerical robustness control for the committed
human MDM2 `Q00987` versus elephant MDM2 `G3SX30` mean-pooled embedding
comparison.

The source result is:

- `data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv#1`

The new repo-visible result is:

- `data/input/g3sx30_first_controlled_human_elephant_mdm2_pairwise_embedding_robustness_checks.csv#1`

This is a result-bearing control PR, not an approval, review, control plan,
runtime-preparation step, or scaffold.

## Baseline

The source pairwise result records:

```text
baseline_cosine_similarity = 0.9973314302339468
source_pairwise_summary_status =
first_human_elephant_mdm2_mean_pooled_embedding_summary_created
```

The robustness calculation independently re-read the two ignored local
embedding matrices and reproduced the committed baseline before creating
the control values.

## Deterministic residue-block jackknife

The control type is:

```text
deterministic_residue_block_jackknife_mean_pooling
```

Each species' residue axis is partitioned independently into ten contiguous
blocks with `numpy.array_split`.

The human embedding has 491 rows:

- one block contains 50 rows
- nine blocks contain 49 rows

The elephant embedding has 492 rows:

- two blocks contain 50 rows
- eight blocks contain 49 rows

The calculation creates 20 controls:

- ten comparisons delete one human block at a time while keeping the full
  elephant embedding;
- ten comparisons delete one elephant block at a time while keeping the full
  human embedding.

Only one species loses one block in each comparison. No paired cross-species
block deletion and no residue alignment are performed. After deletion, each
remaining matrix is independently mean-pooled over its residue axis and the
cosine similarity is calculated in `float64`.

## Numerical control result

```text
robustness_check_status =
first_controlled_pairwise_embedding_robustness_check_created
block_count = 10
block_count_per_species = 10
control_comparison_count = 20
min_control_cosine_similarity = 0.9896092392687877
max_control_cosine_similarity = 0.9974979683829747
mean_control_cosine_similarity = 0.9949019040387004
std_control_cosine_similarity = 0.0023610146368762
max_abs_delta_from_baseline = 0.0077221909651590
baseline_within_control_range = true
control_result_created = true
```

The external calculation JSON has SHA256:

```text
1ca19556000320bf4cb1842c5cd3723f7c2c107d889c496a3826ae59bc335399
```

The committed row contains aggregate numerical control metrics and
provenance. It does not commit the 20 raw control vectors or either source
embedding matrix.

## Interpretation boundary

This is a numerical embedding-space control only.

It is:

- not residue alignment
- not interface analysis
- not binding result
- not orthology proof
- not functional-equivalence evidence
- not longevity evidence
- not a biological claim

The control measures sensitivity of the mean-pooled cosine similarity to
deleting contiguous portions of either input embedding. It does not prove
conserved function, equivalent binding, or any longevity mechanism.

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

Both `.npy` files remain local, ignored, untracked, and uncommitted. The
external JSON remains outside the repository.

## Next result-bearing step

The next concrete result is:

```text
add_first_independent_pairwise_embedding_control_result_before_interpretation
```

No control-plan-only, approval, review, runtime-preparation, scaffold, or
other non-result PR should be inserted before that concrete control result.
This first internal sensitivity check is not by itself a basis for biological
interpretation.
