# G3SX30 one-row non-committed preflight input binding

This PR binds the already-generated local runtime G3SX30 / elephant MDM2 ESMC embedding artifact as a repo-visible, non-committed one-row preflight input reference.

It is a practical bridge to the next concrete local artifact preflight/readiness check. It is not another open-ended review layer and it does not consume the artifact for downstream analysis.

## Biological target and artifact

- `candidate_id = tp53_mdm2_elephant_seed_mdm2_chain`
- `target_accession = G3SX30`
- `target_accession_db = UniProtKB TrEMBL`
- `target_species = Loxodonta africana`
- `target_taxid = 9785`
- `gene_symbol = MDM2`
- `sequence_length = 492`
- `local_embedding_path = data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`
- `artifact_location = local_runtime_data_output_ignored_by_git`
- `local_runtime_embedding_tracked = false`
- `local_runtime_embedding_committed = false`
- `embedding_shape = 492x960`
- `embedding_dtype = float32`
- `embedding_finite = true`
- `sequence_length_matches = true`

## Source decision

- `source_decision_table = data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv`
- `source_decision_row_index = 1`
- `source_decision_status = approved_local_runtime_artifact_as_one_row_readiness_preflight_input`
- `approved_for_one_row_readiness_preflight_input = true`

## Binding decision

The machine-readable binding table is:

- `data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv`

The binding records:

- `non_committed_preflight_input_reference_created = true`
- `ready_for_preflight = false`
- `gate8_promoted = false`
- `gate9_promoted = false`
- `biological_claim_made = false`

Creating `non_committed_preflight_input_reference_created = true` is allowed. Promoting `ready_for_preflight = true`, Gate 8, Gate 9, or a biological claim is not allowed in this PR.

## Next concrete check

- `next_concrete_check = run_record_g3sx30_one_row_local_embedding_preflight_check`
- `next_check_scope = local_artifact_shape_dtype_finiteness_sequence_length_path_policy_only`
- `next_check_input = data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv#1`
- `next_check_output_policy = external_non_committed_observation_only`
- `next_check_output_example = D:/biohub_projects/_chatgpt_observations/g3sx30_one_row_local_embedding_preflight_check.json`

After this PR, the next PR should be `Run/record G3SX30 one-row local embedding preflight check`.

## Boundary

This binding PR does not:

- make a new Biohub / ESMC call
- rerun live embedding
- generate a new embedding
- commit the generated `.npy` artifact
- commit any `data/output` artifact
- copy external validation JSON into the repo
- commit the external FASTA artifact
- commit the external live log
- promote `ready_for_preflight`
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- rerun enrichment or contrast
- make a biological claim
