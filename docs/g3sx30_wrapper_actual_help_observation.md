# G3SX30 wrapper actual help observation

## Status

```text
help_observation_status = observed_help_only
help_command = uv run g3sx30-wrapper-dry-run --help
help_exit_code = 0
observed_help_target = g3sx30-wrapper-dry-run
observed_manifest_option = true
observed_manifest_row_index_option = true
observed_output_path_option = true
observed_help_option = true
actual_cli_help_observed = true
actual_command_verified_for_help = true
command_selected_for_execution = false
output_path_selected_for_execution = false
execution_plan_materialized = false
wrapper_execution_authorized = false
dry_run_execution_authorized = false
live_execution_authorized = false
biohub_esmc_authorized = false
embedding_generation_authorized = false
runtime_still_blocked = true
```

This note records a help-only observation of the G3SX30 wrapper source entry-point boundary.

The observed command was:

```powershell
uv run g3sx30-wrapper-dry-run --help
```

The observed exit code was:

```text
HELP_EXIT_CODE=0
```

The help output was captured outside the repository at:

```text
D:\biohub_projects\_chatgpt_observations\g3sx30_wrapper_help_output.txt
```

That external observation file is not a committed runtime artifact.

## Observed help target

The help output included:

```text
Usage: g3sx30-wrapper-dry-run [OPTIONS]
```

This confirms that the observed help target was the new G3SX30 wrapper boundary, not an ordinary curated embedding command.

## Observed options

The help output included these options:

```text
--manifest
--manifest-row-index
--output-path
--help
```

The help text described these options as interface-documentation-only controls. It stated that the boundary does not read or execute the manifest and does not write outputs.

## PowerShell stderr wrapper note

The captured file also included `uv` build/install warning output and a PowerShell `NativeCommandError` wrapper around stderr text.

That wrapper is not treated as command failure because the observed process exit code was:

```text
HELP_EXIT_CODE=0
```

The actual Typer help text was still printed and contained the expected G3SX30 wrapper help target and options.

## No-runtime-artifact proof

After the help-only observation, repository checks showed:

```text
git status -sb
## observe-g3sx30-wrapper-help

git ls-files --others --exclude-standard
```

The second command printed no untracked files.

This records that the help-only observation did not create runtime artifacts inside the repository.

## Why this is not wrapper execution

This PR observes `--help` only.

It does not run the wrapper without `--help`, does not execute a dry-run, does not execute a live run, does not read or execute the G3SX30 manifest, does not select a command for execution, does not select an output path for execution, does not materialize an execution plan, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, and does not write `data/output` artifacts.

## What remains blocked

This observation does not authorize:

```text
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

The natural next layer is not execution yet.

A later PR may create a stricter source-level runtime blocker or execution-plan review gate for the G3SX30 wrapper. Runtime execution should remain blocked until a separate reviewed gate explicitly authorizes a dry-run path with non-committed output location, no Biohub / ESMC, no embedding generation, and no `ready_for_preflight` promotion.
