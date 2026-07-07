# G3SX30 wrapper help target inspection blocker

## Status

```text
help_target_inspection_status = inspected_target_missing
real_g3sx30_wrapper_help_target_found = false
pyproject_g3sx30_script_entry_present = false
pyproject_wrapper_script_entry_present = false
ordinary_curated_embedding_scripts_present = true
ordinary_scripts_valid_as_substitutes = false
actual_cli_help_observed = false
actual_command_verified = false
command_selected = false
output_path_selected = false
execution_plan_materialized = false
runtime_still_blocked = true
```

This note records the result of source inspection after the final pre-help observation note. The inspection found no real G3SX30 manifest-aware wrapper help target. Therefore no `--help` command is safe to run for the G3SX30 wrapper path yet.

## Source inspection result

The source inspection looked for the planned future command family:

```text
curated_embedding_preflight_dry_run_wrapper
```

The string is present only as an expected future command family in scaffold/config/docs/tests, not as a real executable script entry point or implemented wrapper command.

The `pyproject.toml` script table exposes only ordinary curated embedding commands:

```text
curated-embedding-preflight
curated-embedding-single
```

No `g3sx30` script entry and no wrapper script entry were found in `pyproject.toml`.

## Decision

Because no real G3SX30 manifest-aware wrapper help target exists yet, the actual help-observation step is blocked.

The ordinary commands must not be observed as substitutes:

```text
curated-embedding-preflight
curated_embedding_preflight
curated-embedding-single
curated_embedding_single
```

Those commands are not the planned G3SX30 manifest-aware wrapper target. Observing their help output would not verify the wrapper interface and would create a misleading observed-help claim.

## Why this is not a help observation

This PR does not run `--help`. It records source inspection only.

It does not observe help output, does not verify actual CLI flags, does not select a command, does not select an output path, and does not materialize an execution plan.

## Stop condition

The stop condition is:

```text
no real G3SX30 manifest-aware wrapper help target exists
```

Until that blocker is resolved, the G3SX30 wrapper path remains runtime-blocked and must not proceed to help observation.

## What remains blocked

This blocker note does not authorize:

```text
--help run
ordinary command help substitution
actual command run
observed-help claims
actual CLI flag verification claims
pyproject script entry point
Typer executable wrapper
wrapper implementation
wrapper execution
dry-run execution
live execution
command selection
output path selection
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

The natural next step is not help observation yet. The next complete safe layer should create an explicitly non-executed G3SX30 manifest-aware wrapper source/entry-point implementation plan or implementation boundary, depending on the selected architecture.

Only after a real wrapper help target exists may a later PR perform actual help-only observation. That later PR must still be help-only, still no wrapper execution, still no dry-run execution, still no Biohub / ESMC, and still no embeddings.
