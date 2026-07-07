# G3SX30 wrapper help observation note

## Status

```text
help_observation_status = planned_not_observed
actual_cli_help_observed = false
actual_command_verified = false
command_selected = false
output_path_selected = false
execution_plan_materialized = false
runtime_still_blocked = true
```

This is the final pre-help observation note for the TP53/MDM2 elephant / G3SX30 lane. It prepares the exact conditions for a future help-only observation PR, but it does not run `--help`, does not observe help output, does not verify actual CLI flags, does not implement a wrapper, and does not execute anything.

## Source context

This note follows:

```text
data/interim/g3sx30_wrapper_source_guardrail_scaffold.csv#1
```

The source guardrail scaffold keeps the lane runtime-blocked and records:

```text
source_guardrail_status = source_guardrail_scaffold_runtime_blocked
source_guardrail_decision = define_source_level_guardrails_only
guardrail_scope = future_wrapper_source_checks_only
guardrail_runtime_effect = no_runtime_effect
allowed_next_action_after_source_guardrail = add_wrapper_help_observation_note_pr
```

## Which command may be observed later

A later PR may observe help output only for the future G3SX30 manifest-aware wrapper command family recorded as:

```text
curated_embedding_preflight_dry_run_wrapper
```

That later observation must be help-only. It may only inspect help text for a future wrapper entry point or directly invoked module that is explicitly intended to be the G3SX30 manifest-aware dry-run wrapper.

This note does not select the actual command name. The actual command remains unselected until a later PR can point to concrete source code and run only the help form.

## Which commands must not be observed

The future help-observation PR must not use this note to observe or run ordinary runtime commands such as:

```text
curated-embedding-preflight
curated_embedding_preflight
curated-embedding-single
curated_embedding_single
```

It must also not run a manifest, not run a dry-run preflight, not call Biohub / ESMC, and not use `--yes-live`.

## What counts as safe help-only observation

Safe help-only observation means:

```text
the command is invoked only with --help or an equivalent help flag
the process exits before runtime work
no manifest row is executed
no sequence is fetched
no Biohub / ESMC client is initialized for live work
no embedding is generated
no .npy artifact is created
no data/output artifact is created or committed
no ready_for_preflight status is written
no Gate 8 / Gate 9 status is changed
```

The future help-only observation PR must capture the command that was used, the exact help-output text or a committed safe excerpt, the exit status, and explicit evidence that no runtime artifact was produced.

## What must be captured later

A later actual help-observation PR must capture:

```text
observed command form
observed help output or safe excerpt
exit status
working directory
repo commit
proof that no data/output artifact was created
proof that no .npy artifact was created
proof that no Biohub / ESMC call was made
proof that no embedding generation happened
proof that no ready_for_preflight state changed
```

That future PR may then set `actual_cli_help_observed=true` only if the observation really happened in that later PR.

## Strings and flags that must be checked later

The future help output must be checked for manifest-aware dry-run guardrails. The check must look for clear support for the following concepts before any later execution step can be considered:

```text
G3SX30-specific or manifest-row-specific input control
dry-run-only behavior
no-live-call behavior
max-live-batch-size 0 behavior
non-committed output path requirement
rejection of committed data/output artifacts
no embedding generation during help observation
no Biohub / ESMC live call during help observation
```

The exact flag spelling is not verified here. This PR does not claim `observed_help_flags`, `actual_supported_args`, or `verified_cli_contract`.

## Stop conditions before any later execution

Any later help-observation or post-help PR must stop before execution if any of these are true:

```text
no wrapper source exists
the command is not clearly the G3SX30 manifest-aware wrapper
help output cannot be observed with help-only invocation
help invocation creates data/output artifacts
help invocation creates .npy artifacts
help invocation requires Biohub / ESMC credentials
help invocation initializes live embedding generation
help output lacks manifest-row control
help output lacks dry-run-only or no-live-call controls
help output lacks non-committed output-path controls
help output permits ready_for_preflight promotion
help output suggests Gate 8 / Gate 9 promotion
```

## Why help observation is still not execution

Help observation is metadata inspection. It may show what an interface advertises, but it does not process the G3SX30 manifest row, does not generate embeddings, does not fill missing data, does not evaluate contrast, and does not run a biological or structural inference step.

Therefore, even after a later successful help-only observation, the lane remains runtime-blocked until a separate PR explicitly reviews the observed help output and decides whether a dry-run execution PR is safe.

## Why help observation is not ready_for_preflight

Help observation cannot mark G3SX30 `ready_for_preflight` because it does not prove that the wrapper executed safely against the manifest row. It only checks whether the interface advertises the required safety controls.

A later dry-run execution decision would still require a separate review of observed help output, explicit command selection, explicit non-committed output path selection, and a separate authorization boundary.

## Why help observation is not Biohub / ESMC / embedding generation

The future help-only observation must not call Biohub / ESMC and must not generate embeddings. Help text inspection is only an interface check. It is not a live call, not an embedding fill, not a sequence fetch, not a `.npy` artifact generation step, and not a `data/output` artifact commit.

## This PR does not authorize

This note does not authorize:

```text
--help run
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

If this note is accepted, the natural next PR should be:

```text
actual G3SX30 wrapper help observation PR
```

That future PR should still be help-only, still no execution, still no Biohub / ESMC, and still no embeddings.
