# First human-elephant MDM2 mean-pooled pairwise embedding summary

This PR completes the first numerical embedding-space comparison between the
source-backed human MDM2 reference `Q00987` and the reviewed-for-planning
elephant MDM2 target `G3SX30`.

The repo-visible result is:

- `data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv#1`

It consumes the historical comparator/blocker row:

- `data/input/g3sx30_source_backed_human_mdm2_comparator_paths.csv#1`

The older comparator row remains unchanged as a historical statement that the
human embedding was unavailable at that checkpoint. This PR records the later
runtime result and closes that blocker with a new result row.

## Human runtime scope

The live execution used an external, non-committed **Human MDM2 Q00987
reference self-embedding runtime input** with:

- `accession = Q00987`
- `species = Homo sapiens`
- `taxid = 9606`
- `gene_symbol = MDM2`
- `sequence_length = 491`
- `sequence_sha256 = 77ed25650e717b3f610e42ef8e5c1c88d50e7485725032f8535448a0ca8b61b1`
- `runtime_input_csv_sha256 = d86bf792c538a066d6085e69d3d0f0a1744e7dc5de2a7f179c3198d2e828b8fd`

The public UniProt FASTA fetch happened outside the repository before the live
step. The live embedding step did not fetch a sequence.

Exactly one guarded live embedding execution was performed for this one
accession. The execution completed with `live_execution_status=live_completed`.
No additional accession and no batch were run.

## Local embedding artifacts

The generated human embedding is:

- `data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9606.npy`
- shape `491x960`
- dtype `float32`
- all values finite

The reused elephant embedding is:

- `data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`
- shape `492x960`
- dtype `float32`
- all values finite

Both `.npy` files remain local, ignored, untracked, and uncommitted. No raw
embedding vector and no `data/output` artifact is committed.

## Calculation

The two proteins have different sequence lengths, so this result does not
perform residue-to-residue comparison. Each embedding matrix is independently
mean-pooled over the residue axis to produce one 960-dimensional vector.
Metrics are then calculated in `float64` and recorded to 16 decimal places.

The committed result is:

```text
human_mean_vector_l2_norm = 0.8317611517806080
elephant_mean_vector_l2_norm = 0.8347860929210978
mean_pooled_cosine_similarity = 0.9973314302339468
mean_pooled_cosine_distance = 0.0026685697660532
mean_pooled_euclidean_distance = 0.0609504211067301
pairwise_summary_status =
first_human_elephant_mdm2_mean_pooled_embedding_summary_created
```

The external calculation JSON had SHA256:

```text
e54a31e9aafa7d09c496007a0b4e8fdabc665f5582f1d3978b5d46849e581687
```

## Interpretation boundary

This is a numerical embedding-space comparison only.

It is:

- not residue alignment
- not interface analysis
- not binding result
- not orthology proof
- not functional-equivalence evidence
- not longevity evidence

A high cosine similarity in this summary is not interpreted biologically. The
result does not establish conserved function, equivalent binding, beneficial
breakage, or a longevity effect.

## Runtime and repository boundary

The committed row records:

- `biohub_esmc_live_execution_count = 1`
- `live_scope_accession_count = 1`
- `additional_accessions_embedded = false`
- `batch_run_performed = false`
- `sequence_fetch_performed_by_live_step = false`
- `raw_sequence_committed = false`
- `fasta_committed = false`
- `runtime_csv_committed = false`
- `npy_artifact_committed = false`
- `raw_embedding_values_committed = false`
- `data_output_artifact_committed = false`
- `gate8_promoted = false`
- `gate9_promoted = false`
- `biological_claim_made = false`
- `boltz_called = false`
- `af3_called = false`
- `chai_called = false`
- `enrichment_rerun = false`
- `contrast_rerun = false`

## Next result-bearing step

The next safe result-bearing step is:

```text
add_first_controlled_pairwise_embedding_robustness_check_before_interpretation
```

No separate runtime-approval layer and no embedding-generation-only layer
should be inserted before that concrete control result. No biological
interpretation is allowed before a predefined control or robustness check.

## Recorded runtime result

The external runtime source was the **Human MDM2 Q00987 reference self-embedding runtime input**.

- `live_execution_status=live_completed`
- `human_embedding_shape=491x960`
- `elephant_embedding_shape=492x960`
- `mean_pooled_cosine_similarity=0.9973314302339468`
- `mean_pooled_cosine_distance=0.0026685697660532`
- `mean_pooled_euclidean_distance=0.0609504211067301`
- `pairwise_summary_status=first_human_elephant_mdm2_mean_pooled_embedding_summary_created`

The FASTA, external runtime CSV, both `.npy` matrices, and raw embedding vectors remain outside the committed result.
