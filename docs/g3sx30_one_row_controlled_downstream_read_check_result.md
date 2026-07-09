# G3SX30 one-row controlled downstream read/check result

This PR records the actual controlled downstream read/check result for the one-row ready G3SX30 elephant MDM2 artifact.

It consumes the existing controlled downstream handle and reads/checks the ignored local runtime `.npy` artifact reference.

This is not another approval layer, scaffold, handle, or decision layer.

## Source controlled downstream use path

The read/check result sources:

- `source_downstream_use_path_table = data/input/g3sx30_one_row_controlled_downstream_use_paths.csv`
- `source_downstream_use_path_row_index = 1`
- `source_controlled_downstream_use_path = first_controlled_downstream_use_path_for_one_row_ready_artifact`
- `source_controlled_handle_id = g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle`
- `source_controlled_input_status = one_row_ready_artifact_available_for_controlled_downstream_use`
- `source_ready_artifact_reference = data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`
- `source_next_pr_must_be_actual_controlled_downstream_read_check = true`
- `source_no_additional_downstream_approval_before_read_check = true`
- `source_next_step = run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact`

## Controlled read/check result

The read/check result table is:

- `data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv`

The result records:

- `read_check_action = run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact`
- `read_check_status = controlled_downstream_read_check_passed`
- `controlled_handle_id = g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle`
- `controlled_input_status = one_row_ready_artifact_available_for_controlled_downstream_use`
- `one_row_only = true`
- `candidate_id = tp53_mdm2_elephant_seed_mdm2_chain`
- `target_accession = G3SX30`
- `target_species = Loxodonta africana`
- `target_taxid = 9785`
- `gene_symbol = MDM2`
- `ready_scope = one_row_g3sx30_elephant_mdm2_only`

## Local artifact read/check

The local artifact read/check confirmed:

- `local_runtime_embedding_exists = true`
- `local_runtime_embedding_tracked = false`
- `local_runtime_embedding_committed = false`
- `git_ignore_rule_status = data_output_ignored`
- `embedding_shape = 492x960`
- `embedding_dtype = float32`
- `embedding_finite = true`
- `sequence_length = 492`
- `sequence_length_matches = true`

The `.npy` artifact remains a local runtime artifact under ignored `data/output`.

## Boundary

This read/check does not make a Biohub / ESMC call, rerun live embedding, generate a new embedding, commit the generated `.npy` artifact, commit any `data/output` artifact, promote Gate 8 or Gate 9, call Boltz / AF3 / Chai, rerun enrichment or contrast, or make a biological claim.

It records:

- `gate8_promoted = false`
- `gate9_promoted = false`
- `biological_claim_made = false`
- `data_output_artifact_committed = false`
- `biohub_esmc_called_by_read_check = false`
- `live_embedding_rerun_by_read_check = false`
- `embedding_generation_performed_by_read_check = false`
- `npy_artifact_created_by_read_check = false`
- `boltz_called = false`
- `af3_called = false`
- `chai_called = false`
- `enrichment_rerun = false`
- `contrast_rerun = false`

## Next step

After this read/check result passes, the next step should move toward the first minimal controlled downstream output:

- `move_toward_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact`

This PR records:

- `next_pr_should_move_toward_first_minimal_controlled_downstream_output = true`
- `no_additional_read_check_approval_before_output = true`

Do not add another read/check approval, review, scaffold, handle, or decision layer before that output-oriented step.
