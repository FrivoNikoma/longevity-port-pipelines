# G3SX30 one-row first minimal controlled downstream output

This PR creates the first minimal controlled downstream output for the one-row ready G3SX30 elephant MDM2 artifact.

It consumes the passed controlled downstream read/check result and creates an actual one-row artifact identity and embedding health summary.

This is an output record, not another non-result layer.

## Source read/check result

The output sources:

- `source_read_check_result_table = data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv`
- `source_read_check_result_row_index = 1`
- `source_read_check_status = controlled_downstream_read_check_passed`
- `source_read_check_action = run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact`
- `source_controlled_handle_id = g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle`
- `source_controlled_input_status = one_row_ready_artifact_available_for_controlled_downstream_use`
- `source_ready_artifact_reference = data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`

## Minimal controlled output

The output table is:

- `data/input/g3sx30_one_row_first_minimal_controlled_downstream_outputs.csv`

The output records:

- `output_action = add_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact`
- `output_status = first_minimal_controlled_downstream_output_created`
- `output_type = one_row_artifact_identity_and_embedding_health_summary`
- `output_scope = identity_and_embedding_health_only_no_biological_claim`
- `candidate_id = tp53_mdm2_elephant_seed_mdm2_chain`
- `target_accession = G3SX30`
- `target_species = Loxodonta africana`
- `target_taxid = 9785`
- `gene_symbol = MDM2`
- `one_row_only = true`
- `ready_scope = one_row_g3sx30_elephant_mdm2_only`

## Artifact identity and embedding health

The output confirms:

- `candidate_identity_confirmed = true`
- `artifact_reference_confirmed = true`
- `embedding_health_confirmed = true`
- `source_embedding_shape = 492x960`
- `source_embedding_dtype = float32`
- `source_embedding_finite = true`
- `source_sequence_length = 492`
- `source_sequence_length_matches = true`

The output type is limited to identity and embedding-health facts. It makes no biological claim.

## Boundary

This output does not make a Biohub / ESMC call, rerun live embedding, generate a new embedding, commit the generated `.npy` artifact, commit any `data/output` artifact, promote Gate 8 or Gate 9, call Boltz / AF3 / Chai, rerun enrichment or contrast, or make a biological claim.

It records:

- `gate8_promoted = false`
- `gate9_promoted = false`
- `biological_claim_made = false`
- `data_output_artifact_committed = false`
- `biohub_esmc_called_by_output = false`
- `live_embedding_rerun_by_output = false`
- `embedding_generation_performed_by_output = false`
- `npy_artifact_created_by_output = false`
- `boltz_called = false`
- `af3_called = false`
- `chai_called = false`
- `enrichment_rerun = false`
- `contrast_rerun = false`

## Next step

After this output, the next step should be a concrete analysis-adjacent controlled output or another concrete biological-data-bearing step:

- `move_toward_first_analysis_adjacent_controlled_output_or_next_concrete_biological_data_bearing_step_for_one_row_ready_g3sx30_artifact`

This PR records:

- `next_pr_should_be_concrete_analysis_adjacent_or_biological_data_bearing_step = true`
- `no_additional_non_result_layer_before_next_concrete_step = true`

Do not insert another non-result layer before that concrete step.
