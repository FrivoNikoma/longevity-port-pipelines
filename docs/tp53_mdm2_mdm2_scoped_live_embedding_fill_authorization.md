# Scoped TP53/MDM2 live embedding fill authorization

This checkpoint authorizes a future controlled live fill for exactly mouse
`P23804` and hamster `A0ABM2YB85`. It is authorization-only and performs no
BioHub or ESMC call.

## Integrity binding

The authorization stores canonical UTF-8/LF text SHA-256 values for the preceding manifest
and its committed validation result. Any change to either source CSV invalidates
the authorization until it is reviewed and regenerated.

## Scope and execution policy

The contract records:

- `allowed_live_accessions=P23804|A0ABM2YB85`;
- `allowed_model=esmc-300m-2024-12`;
- `required_runner=curated_embedding_single`;
- `required_live_flag=--yes-live`;
- `explicit_human_opt_in_required=true`;
- `human_opt_in_scope=per_accession_per_invocation`;
- `max_live_batch_size=1`;
- `execution_order=sequential_one_accession_at_a_time`;
- `live_fill_allowed=true`;
- `fill_execution_allowed=true`;
- `allowed_next_action=execute_scoped_live_fill_with_immediate_post_fill_audit`.

Both accessions are authorized, but only one live invocation may run at a time.
The second accession cannot begin until the first passes immediate post-fill
audit.

## Pre-live and no-overwrite policy

Each accession requires a same-row dry-run with `status=dry_run_missing`,
`sequence_length_status=matches`, and `embedding_exists=false`. Explicit human
opt-in is required for every invocation. Default skip-existing behavior is
mandatory; `--no-skip-existing` and overwrite are forbidden.

## Partial failure policy

Execution stops after the first failed or invalid row. A later accession may
not run after either a live failure or a post-fill audit failure. A successful
prior artifact is retained only if its own audit passed. A failed artifact must
be quarantined or removed before a separately approved retry.

## Immediate post-fill audit

Expected shapes are `489x960` for `P23804` and `510x960` for `A0ABM2YB85`.
Each row must validate dtype `float32`, numeric and finite values, sequence-length
match, follow-up `dry_run_present`, and follow-up `present_valid`. Generated
`.npy` files remain untracked local runtime artifacts and must not be committed.

## Narrow MDM2-only exception

Aggregate TP53/MDM2 remains closed because TP53 is still
`deferred_pending_source`. This exception authorizes only the ready MDM2
source/provenance layer. It does not authorize TP53 execution, aggregate
contrast, Gate 8 entry or promotion, Gate 9 promotion, cofolding, or biological
claims.

## Boundaries

This PR performs no live execution, calls no BioHub/ESMC service, generates no
embedding, creates or commits no `.npy`, commits no `data/output` artifact, runs
no contrast, opens no downstream gate, and makes no biological claim.
