# G3SX30 wrapper execution-plan review gate

## Status

```text
execution_plan_review_status = execution_plan_review_gate_runtime_blocked
execution_plan_review_decision = require_separate_review_before_any_execution
help_observation_status = observed_help_only
help_exit_code = 0
observed_help_target = g3sx30-wrapper-dry-run
observed_manifest_option = true
observed_manifest_row_index_option = true
observed_output_path_option = true
observed_help_option = true
dry_run_plan_review_required_before_execution = true
non_committed_output_path_review_required = true
output_path_selected_for_execution = false
command_selected_for_execution = false
execution_plan_materialized = false
wrapper_execution_authorized = false
dry_run_execution_authorized = false
live_execution_authorized = false
ready_for_preflight_authorized = false
biohub_esmc_authorized = false
embedding_generation_authorized = false
runtime_still_blocked = true
```

This checkpoint follows the actual G3SX30 wrapper help observation. Help was observed, but help observation is not execution authorization.

## Concrete row

The machine-readable row is:

```text
data/interim/g3sx30_wrapper_execution_plan_review_gate.csv#1
```

It is built by:

```text
src/longevity_port_pipelines/stages/g3sx30_wrapper_execution_plan_review_gate.py
```

and checked by:

```text
tests/test_g3sx30_wrapper_execution_plan_review_gate.py
```

## What this gate means

This gate requires a separate reviewed execution plan before any future G3SX30 wrapper dry-run can be considered.

That future reviewed plan would need, at minimum:

```text
explicit non-committed output path
no Biohub / ESMC
no embedding generation
no .npy artifact
no committed data/output artifact
ready_for_preflight remains false
Gate 8 remains blocked
Gate 9 remains blocked
no biological claim
```

## Why this is not execution

This PR does not run `g3sx30-wrapper-dry-run`.

It does not run the wrapper without `--help`, does not execute a dry-run, does not execute a live run, does not read or execute the G3SX30 manifest, does not select a command for execution, does not select an output path for execution, and does not materialize an execution plan.

It also does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not write `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, and does not make biological claims.

## Natural next step

The natural next layer is still not dry-run execution.

A later PR may add a source-level runtime blocker or a non-executable execution-plan object scaffold. Runtime execution should remain blocked until a separate reviewed gate explicitly authorizes a dry-run path with a non-committed output location and all live/embedding permissions false.
