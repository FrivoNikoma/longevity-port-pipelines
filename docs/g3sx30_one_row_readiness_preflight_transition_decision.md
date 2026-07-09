# G3SX30 one-row readiness/preflight transition path decision

This PR records the final decision before the actual one-row G3SX30 readiness/preflight transition/check.

It approves the transition path from the passed local embedding preflight result, but it does not run the transition itself.

## Source result

The decision sources:

- `source_result_table = data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv`
- `source_result_row_index = 1`
- `source_check_name = g3sx30_one_row_local_embedding_preflight_check`
- `source_check_status = local_preflight_pass`

The source result records:

- `source_embedding_shape = 492x960`
- `source_embedding_dtype = float32`
- `source_embedding_finite = true`
- `source_sequence_length_matches = true`
- `source_local_runtime_embedding_tracked = false`
- `source_local_runtime_embedding_committed = false`

The source result identifies:

- `candidate_id = tp53_mdm2_elephant_seed_mdm2_chain`
- `target_accession = G3SX30`
- `target_accession_db = UniProtKB TrEMBL`
- `target_species = Loxodonta africana`
- `target_taxid = 9785`
- `gene_symbol = MDM2`

## Decision

The machine-readable decision table is:

- `data/input/g3sx30_one_row_readiness_preflight_transition_decisions.csv`

The decision records:

- `decision = approve_one_row_readiness_preflight_transition_path`
- `approved_for_next_transition_step = true`
- `ready_for_preflight = false`
- `gate8_promoted = false`
- `gate9_promoted = false`
- `biological_claim_made = false`
- `allowed_next_action = run_one_row_g3sx30_readiness_preflight_transition`

Important distinction:

- `approved_for_next_transition_step = true` means the next concrete one-row readiness/preflight transition/check is allowed.
- It does not mean `ready_for_preflight = true`.
- It does not promote Gate 8 or Gate 9.
- It does not make a biological claim.

## Anti-loop rule

This is the final decision PR before the actual transition/check.

The decision records:

- `next_pr_must_be_actual_transition_check = true`
- `no_additional_decision_before_transition = true`
- `next_required_pr_title = Run one-row G3SX30 readiness/preflight transition`

After this PR, the next PR must run the one-row G3SX30 readiness/preflight transition.

Do not add another decision, review, scaffold, or binding layer before that.

## Boundary

This decision PR does not:

- make a Biohub / ESMC call
- rerun live embedding
- generate a new embedding
- commit the generated `.npy` artifact
- commit any `data/output` artifact
- commit external FASTA, live log, validation JSON, or local preflight JSON artifacts
- promote `ready_for_preflight`
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- rerun enrichment or contrast
- make a biological claim

## Required next PR

After this PR, the next PR must be:

- `Run one-row G3SX30 readiness/preflight transition`

No additional decision/review/scaffold/binding layer may be inserted before that transition/check.
