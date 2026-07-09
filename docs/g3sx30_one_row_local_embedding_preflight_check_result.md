# G3SX30 one-row local embedding preflight check result

This PR records the external local preflight check result for the already-generated local runtime G3SX30 / elephant MDM2 ESMC embedding artifact.

The check was executed externally and wrote only to:

- `D:/biohub_projects/_chatgpt_observations/g3sx30_one_row_local_embedding_preflight_check.json`

The external JSON is not committed.

## Source binding

The result sources the machine-readable binding row:

- `source_binding_table = data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv`
- `source_binding_row_index = 1`
- `source_binding_status = non_committed_preflight_input_reference_created`

The source binding identifies:

- `candidate_id = tp53_mdm2_elephant_seed_mdm2_chain`
- `target_accession = G3SX30`
- `target_accession_db = UniProtKB TrEMBL`
- `target_species = Loxodonta africana`
- `target_taxid = 9785`
- `gene_symbol = MDM2`
- `sequence_length = 492`

## Local preflight result

The recorded result table is:

- `data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv`

The recorded result is:

- `check_name = g3sx30_one_row_local_embedding_preflight_check`
- `check_status = local_preflight_pass`
- `local_embedding_path = data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`
- `artifact_location = local_runtime_data_output_ignored_by_git`
- `local_runtime_embedding_exists = true`
- `local_runtime_embedding_tracked = false`
- `local_runtime_embedding_committed = false`
- `git_ignore_rule_status = data_output_ignored`
- `embedding_shape = 492x960`
- `embedding_dtype = float32`
- `embedding_finite = true`
- `sequence_length = 492`
- `sequence_length_matches = true`

## No-side-effect result

The check records:

- `biohub_esmc_called_by_check = false`
- `live_embedding_rerun_by_check = false`
- `embedding_generation_performed_by_check = false`
- `npy_artifact_created_by_check = false`
- `data_output_artifact_committed = false`
- `external_validation_json_committed = false`
- `ready_for_preflight_promoted = false`
- `gate8_promoted = false`
- `gate9_promoted = false`
- `boltz_called = false`
- `af3_called = false`
- `chai_called = false`
- `enrichment_rerun = false`
- `contrast_rerun = false`
- `biological_claim_made = false`
- `downstream_gate_unlocked = false`

## Interpretation

This is a concrete local artifact preflight pass.

It means the already-generated local runtime G3SX30 / elephant MDM2 embedding artifact passed shape, dtype, finite-value, sequence-length, ignored/untracked/uncommitted artifact, and no-side-effect policy checks.

It does not mean `ready_for_preflight = true`.

It does not promote Gate 8 or Gate 9.

It does not make a biological claim.

## Next practical decision

The next practical decision is:

- `next_practical_decision = approve_one_row_readiness_preflight_transition_path_or_repair_concrete_blocker`

Because this result is `local_preflight_pass`, the pass decision path is:

- `pass_decision_path = approve_one_row_readiness_preflight_transition_path`

If a future equivalent check fails, the fail decision path is:

- `fail_decision_path = repair_concrete_local_preflight_blocker`

After this PR, do not add another generic checkpoint, review, scaffold, or binding layer. The next practical PR should make the concrete one-row readiness/preflight transition decision from this passed local preflight result.

## Boundary

This result record does not:

- commit the generated `.npy` artifact
- commit any `data/output` artifact
- commit the external local preflight JSON
- copy external validation JSON into the repo
- make a new Biohub / ESMC call
- rerun live embedding
- generate a new embedding
- promote `ready_for_preflight`
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- rerun enrichment or contrast
- make a biological claim
