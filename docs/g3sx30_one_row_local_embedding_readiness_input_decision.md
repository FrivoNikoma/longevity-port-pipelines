# G3SX30 one-row local embedding readiness/preflight input decision

This decision records a bounded use decision for the already-generated local runtime G3SX30 embedding artifact.

It reviews the local artifact status and approves the artifact path as a one-row readiness/preflight input reference, while keeping runtime and downstream gates blocked.

## Source state

The source live runtime observation is:

- `docs/g3sx30_one_row_live_embedding_runtime_observation.md`

The source post-live local artifact status audit is:

- `docs/g3sx30_post_live_local_artifact_status.md`

The local runtime artifact path is:

- `data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`

The external validation JSON path is:

- `D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json`

The artifact remains local runtime output:

- `local_runtime_embedding_exists = true`
- `local_runtime_embedding_tracked = false`
- `local_runtime_embedding_committed = false`
- `artifact_location = local_runtime_data_output_ignored_by_git`

## Validation summary reviewed

The reviewed validation summary is:

- `embedding_shape = 492x960`
- `embedding_dtype = float32`
- `embedding_finite = true`
- `sequence_length_matches = true`
- `validation_ready_for_preflight_promoted = false`
- `validation_gate8_promoted = false`
- `validation_gate9_promoted = false`
- `validation_biological_claim_made = false`

## Decision

The repo-visible decision row is recorded in:

- `data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv`

The decision is:

- `approved_for_one_row_readiness_preflight_input = true`
- `readiness_preflight_input_record_status = approved_local_runtime_artifact_as_one_row_readiness_preflight_input`
- `ready_for_preflight = false`
- `gate8_promoted = false`
- `gate9_promoted = false`
- `biological_claim_made = false`

Important distinction:

- approving the local artifact path as a one-row readiness/preflight input reference is allowed
- promoting the row to `ready_for_preflight` is not allowed in this PR
- promoting Gate 8 or Gate 9 is not allowed in this PR
- making a biological claim is not allowed in this PR

## Boundary

This decision does not:

- make a new Biohub / ESMC call
- rerun live embedding
- generate a new embedding
- commit the generated `.npy` artifact
- commit any `data/output` artifact
- commit the external FASTA artifact
- commit the external live log
- commit the external validation JSON
- promote `ready_for_preflight`
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- rerun enrichment or contrast
- make a biological claim

## Next actionable step

The next actionable step is:

- `prepare_one_row_non_committed_preflight_input_consumer_or_manifest_binding_pr`

That next PR should consume or bind this one-row decision record without committing the local `.npy`, without using committed `data/output`, without promoting `ready_for_preflight`, without Gate 8 / Gate 9 promotion, and without biological claims.
