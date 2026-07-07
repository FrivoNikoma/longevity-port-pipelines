# G3SX30 wrapper dry-run execution plan scaffold review

This is the final non-execution review layer for the selected G3SX30 wrapper dry-run execution plan scaffold.

It reviews the concrete future command form and the concrete external non-committed output path selected by the scaffold.

## Review decision

```text
review_status = dry_run_execution_plan_scaffold_reviewed
review_scope = final_non_execution_review_before_actual_dry_run_pr
review_decision = approve_selected_external_output_dry_run_for_next_pr
selected_command_form_reviewed = true
selected_external_output_path_reviewed = true
selected_manifest_row_reviewed = true
dry_run_execution_authorized_for_next_pr = true
dry_run_execution_authorized_in_this_pr = false
dry_run_executed = false
runtime_still_blocked_in_this_pr = true
allowed_next_action_after_review = execute_g3sx30_wrapper_dry_run_with_external_output_path
claim_status = technical_checkpoint
```

## Reviewed command form

```powershell
uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json
```

This command form is approved for the next PR only.

It is not run by this PR.

## Reviewed external output path

```text
D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json
```

This output path is approved for the next PR only.

It is outside the repository and outside `data/output`.

This PR does not create the external output file and does not create the external output directory.

## What is authorized

This review authorizes only the next PR to execute the reviewed G3SX30 wrapper dry-run with the reviewed external output path.

It does not authorize dry-run execution in this PR.

## What remains false in this PR

```text
dry_run_execution_authorized_in_this_pr = false
dry_run_executed = false
live_execution_authorized = false
manifest_execution_authorized_in_this_pr = false
biohub_esmc_authorized = false
embedding_generation_authorized = false
npy_artifact_authorized = false
output_file_created = false
output_directory_created = false
data_output_artifact_commit_authorized = false
ready_for_preflight_authorized = false
gate8_promotion_authorized = false
gate9_promotion_authorized = false
biological_claim_authorized = false
```

## What this PR does not do

This PR does not:

- run `g3sx30-wrapper-dry-run`
- run a dry-run
- run a live path
- execute the G3SX30 manifest in this PR
- create the external output file
- create the external output directory
- call Biohub / ESMC
- generate embeddings
- create `.npy` artifacts
- write `data/output` artifacts
- mark anything `ready_for_preflight`
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- make biological claims

## Required next PR

After this PR, do not add another blocker, review, or scaffold layer.

The next practical PR should be:

```text
Execute G3SX30 wrapper dry-run with external output path
```

That future PR should still have no Biohub / ESMC, no embeddings, no `.npy`, no `data/output` artifact commit, no Gate 8 / Gate 9, and no biological claim.
