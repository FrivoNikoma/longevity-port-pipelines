# G3SX30 wrapper dry-run execution plan scaffold

This is a non-executable dry-run execution plan scaffold for the TP53/MDM2 elephant / G3SX30 lane.

It follows the source runtime fail-closed tests. The actual entrypoint has been tested to fail closed for non-help invocation, so this scaffold can now select a concrete future command form and a concrete future non-committed output path without executing anything.

## Status

```text
execution_plan_scaffold_status = dry_run_execution_plan_scaffold_non_executable
execution_plan_scaffold_decision = select_future_command_form_and_external_output_path_only
future_command_form_selected = true
future_non_committed_output_path_selected = true
command_selected_for_execution = false
output_path_selected_for_execution = false
execution_plan_materialized = false
dry_run_execution_authorized = false
runtime_still_blocked = true
claim_status = technical_checkpoint
```

## Concrete future command form

```powershell
uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json
```

This command form is recorded for future review only.

It is not run by this PR.

## Concrete future non-committed output path

```text
D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json
```

This path is outside the repository and outside `data/output`.

The path is not created by this PR. The output file is not created by this PR. No output directory is created by this PR.

## Files

```text
data/config/g3sx30_wrapper_dry_run_execution_plan_scaffold_schema.yaml
data/interim/g3sx30_wrapper_dry_run_execution_plan_scaffold.csv#1
src/longevity_port_pipelines/stages/g3sx30_wrapper_dry_run_execution_plan_scaffold.py
tests/test_g3sx30_wrapper_dry_run_execution_plan_scaffold.py
tests/test_g3sx30_wrapper_dry_run_execution_plan_scaffold_doc.py
```

## What this scaffold does

This scaffold records a future command form and future non-committed output path.

It keeps:

```text
command_selected_for_execution = false
output_path_selected_for_execution = false
execution_plan_materialized = false
wrapper_execution_authorized = false
dry_run_execution_authorized = false
live_execution_authorized = false
manifest_execution_authorized = false
ready_for_preflight_authorized = false
biohub_esmc_authorized = false
embedding_generation_authorized = false
npy_artifact_authorized = false
data_output_artifact_commit_authorized = false
gate8_promotion_authorized = false
gate9_promotion_authorized = false
biological_claim_authorized = false
runtime_still_blocked = true
```

## What this scaffold does not do

This scaffold does not run `g3sx30-wrapper-dry-run`.

It does not:

- run a dry-run
- run a live path
- execute the G3SX30 manifest
- call Biohub / ESMC
- generate embeddings
- create `.npy` artifacts
- create the future output file
- create the future output directory
- write `data/output` artifacts
- mark anything `ready_for_preflight`
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- make biological claims

## Natural next step

The natural next step is review of this scaffold before any execution is considered.

A later PR may review the selected future command form and external output path. Execution must remain blocked until a separate reviewed gate explicitly authorizes a dry-run.
