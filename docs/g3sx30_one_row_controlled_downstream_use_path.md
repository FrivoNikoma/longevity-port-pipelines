# G3SX30 one-row controlled downstream use path

This PR creates the first controlled downstream use path for the one-row ready G3SX30 elephant MDM2 artifact.

It consumes the actual readiness/preflight transition result and creates a concrete controlled handle for the single ready row.

This is not another decision layer.

## Source transition result

The downstream-use path sources:

- `source_transition_result_table = data/input/g3sx30_one_row_readiness_preflight_transition_results.csv`
- `source_transition_result_row_index = 1`
- `source_transition_status = one_row_readiness_preflight_transition_passed`
- `source_ready_for_preflight = true`
- `source_allowed_downstream_use_path = first_controlled_downstream_use_path_for_one_row_ready_artifact`

## Controlled downstream handle

The downstream-use path table is:

- `data/input/g3sx30_one_row_controlled_downstream_use_paths.csv`

The controlled handle records:

- `controlled_downstream_use_path = first_controlled_downstream_use_path_for_one_row_ready_artifact`
- `controlled_handle_id = g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle`
- `controlled_input_status = one_row_ready_artifact_available_for_controlled_downstream_use`
- `one_row_only = true`
- `candidate_id = tp53_mdm2_elephant_seed_mdm2_chain`
- `target_accession = G3SX30`
- `target_species = Loxodonta africana`
- `target_taxid = 9785`
- `gene_symbol = MDM2`
- `ready_scope = one_row_g3sx30_elephant_mdm2_only`
- `next_pr_must_be_actual_controlled_downstream_read_check = true`
- `no_additional_downstream_approval_before_read_check = true`

## Boundary

This downstream-use path does not make a Biohub / ESMC call, rerun live embedding, generate a new embedding, commit the generated `.npy` artifact, commit any `data/output` artifact, promote Gate 8 or Gate 9, call Boltz / AF3 / Chai, rerun enrichment or contrast, or make a biological claim.

It records:

- `gate8_promoted = false`
- `gate9_promoted = false`
- `biological_claim_made = false`
- `data_output_artifact_committed = false`
- `biohub_esmc_called_by_path_creation = false`
- `live_embedding_rerun_by_path_creation = false`
- `embedding_generation_performed_by_path_creation = false`
- `npy_artifact_created_by_path_creation = false`

## Next step

After this PR, the next PR must run an actual controlled downstream read/check for the one-row ready G3SX30 artifact. No additional downstream approval/review/scaffold/binding layer is allowed before that read/check.

The actual read/check next action is:

- `run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact`
