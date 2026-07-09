# G3SX30 post-live local artifact status

This short audit records the local runtime artifact status after the already-merged guarded one-row G3SX30 live embedding.

The first guarded Biohub / ESMC live embedding call has already happened and was already recorded as:

status = live_completed
embedding_shape = 492x960
live_exit_code = 0
embedding_exists = true

This checkpoint does not run live embedding again.

## Local runtime artifact

The local runtime embedding artifact exists at:

data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy

Local status:

local_runtime_embedding_exists = true
tracked_embedding_files = none
ignore_rule = .gitignore:9:data/output/*
local_runtime_embedding_tracked = false
local_runtime_embedding_committed = false
artifact_location = local_runtime_data_output_ignored_by_git

## External non-committed artifacts

The following observation artifacts exist outside the repository and are not committed:

D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_output.txt
D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json
D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta
D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence_validation.json

## Validation summary

The external validation JSON records:

shape = 492x960
dtype = float32
finite = true
sequence_length_matches = true
biohub_esmc_called = true
embedding_generation_performed = true
npy_artifact_created = true
data_output_artifact_committed = false
ready_for_preflight_promoted = false
gate8_promoted = false
gate9_promoted = false
biological_claim_made = false

## Boundary

This audit does not:

- make a new Biohub / ESMC call
- rerun live embedding
- generate a new embedding
- commit the generated .npy artifact
- commit any data/output artifact
- commit the external FASTA artifact
- commit the external live log
- commit the external validation JSON
- promote ready_for_preflight
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- rerun enrichment or contrast
- make a biological claim

## Next practical step

After this short post-live audit, do not add another generic checkpoint, review, scaffold, or decision layer.

The next practical PR should decide how to use the local embedding artifact safely, for example:

Review G3SX30 local embedding artifact and decide readiness/preflight path

or:

Approve G3SX30 local embedding artifact for one-row readiness/preflight input
