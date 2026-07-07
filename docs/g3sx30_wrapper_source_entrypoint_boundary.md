# G3SX30 wrapper source entry-point boundary

## Status

```text
entrypoint_boundary_status = source_entrypoint_boundary_runtime_blocked
script_entry_point = g3sx30-wrapper-dry-run
expected_command_family = curated_embedding_preflight_dry_run_wrapper
actual_cli_help_observed = false
actual_command_verified = false
command_selected_for_execution = false
output_path_selected_for_execution = false
execution_plan_materialized = false
wrapper_execution_authorized = false
dry_run_execution_authorized = false
live_execution_authorized = false
ready_for_preflight_authorized = false
biohub_esmc_authorized = false
embedding_generation_authorized = false
runtime_still_blocked = true
```

This boundary creates a real G3SX30 wrapper help target for a later help-only observation PR. It follows the G3SX30 wrapper help target inspection blocker, which found that no real wrapper help target existed yet.

## Entry point

This PR adds a `pyproject.toml` script entry point:

```text
g3sx30-wrapper-dry-run = "longevity_port_pipelines.stages.g3sx30_wrapper_source_entrypoint_boundary:app"
```

The entry point is associated with the expected future command family:

```text
curated_embedding_preflight_dry_run_wrapper
```

## What this boundary may be used for later

A later PR may observe:

```text
uv run g3sx30-wrapper-dry-run --help
```

That later PR must still be help-only. It must not run the command without `--help`, must not execute the wrapper, must not execute a dry-run, must not call Biohub / ESMC, and must not generate embeddings.

## Why this is not help observation yet

This PR adds the source entry-point boundary, but it does not run `--help`.

Therefore this PR does not claim:

```text
actual_cli_help_observed = true
actual_command_verified = true
observed_help_flags
verified_cli_contract
```

Those claims can only appear in a later actual help-observation PR if `--help` is really run and the output is reviewed.

## Why this is not execution

The command body is intentionally runtime-blocked. If someone runs the command without `--help`, it stops before any runtime work.

The boundary does not read the G3SX30 manifest, does not execute a manifest row, does not select an output path for execution, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, and does not write `data/output` artifacts.

## Ordinary commands are still not substitutes

The ordinary commands remain invalid substitutes for this wrapper target:

```text
curated-embedding-preflight
curated_embedding_preflight
curated-embedding-single
curated_embedding_single
```

Help observation must target the new G3SX30 wrapper boundary, not the ordinary curated embedding commands.

## What remains blocked

This PR does not authorize:

```text
--help run
observed-help claims
actual CLI flag verification claims
wrapper execution
dry-run execution
live execution
command selection for execution
output path selection for execution
execution plan materialization
Biohub / ESMC
embeddings
.npy artifacts
data/output artifact commit
ready_for_preflight
manifest runtime unlock
Gate 8 / Gate 9
Boltz / AF3 / Chai
enrichment / contrast rerun
biological claim
```

## Natural next step

The natural next PR is an actual G3SX30 wrapper help observation PR.

That future PR should run only:

```text
uv run g3sx30-wrapper-dry-run --help
```

It should capture the observed help output, exit status, and no-runtime-artifact proof. It must still not run the wrapper, not run a dry-run, not call Biohub / ESMC, and not generate embeddings.
