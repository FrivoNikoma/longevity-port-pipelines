# G3SX30 dry-run preflight command discovery note

This is a docs-only command discovery note for a later G3SX30 dry-run preflight execution PR.

It does not run `curated-embedding-preflight`, does not run `curated_embedding_preflight`, does not run `curated-embedding-single`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, and does not make biological claims.

## Source checklist

The source checklist is `docs/g3sx30_dry_run_preflight_execution_checklist.md`.

That checklist points to `data/input/g3sx30_dry_run_preflight_manifest.csv#1`.

The source manifest row remains planning-only and records:

- `manifest_entry_status=manifest_scaffold_ready_runtime_blocked`
- `dry_run_only=true`
- `max_live_batch_size=0`
- `ready_for_preflight_after_manifest=false`
- `sequence_fetch_allowed=false`
- `biohub_call_allowed=false`
- `esmc_call_allowed=false`
- `embedding_generation_allowed=false`
- `curated_embedding_preflight_allowed=false`
- `curated_embedding_single_allowed=false`
- `reviewed_sequence_length=492`
- `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`
- `claim_status=technical_checkpoint`

## Repository script entry points to inspect later

`pyproject.toml` exposes these relevant script names:

- `curated-embedding-preflight`
- `curated-embedding-single`

This discovery note does not execute either script.

The later execution PR must inspect the help text first and document the exact observed dry-run flags before any run is attempted.

## Non-executed help commands for the later PR

These commands are help/discovery commands only. They are listed here as a future checklist and must not be run in this docs-only PR.

```powershell
# TEMPLATE ONLY — for a later command discovery or execution PR.
uv run curated-embedding-preflight --help
uv run curated-embedding-single --help
uv run python -m longevity_port_pipelines.stages.curated_embedding_preflight --help
uv run python -m longevity_port_pipelines.stages.curated_embedding_single --help
```

The later PR must paste or summarize the relevant help output into its PR body or a checked-in note before it executes any dry-run command.

## Required help-output checks for the later PR

Before any later dry-run execution, the help output must confirm:

- the real command name or module entry point
- the manifest input flag
- the candidate id or accession filtering flag
- the dry-run flag
- a no-live-call or equivalent provider-disable flag
- a max-live-batch-size or equivalent zero-live-work guardrail
- an output-disable or no-output-artifacts flag
- behavior when credentials are missing
- behavior when the manifest row has `biohub_call_allowed=false`
- behavior when the manifest row has `esmc_call_allowed=false`
- behavior when the manifest row has `embedding_generation_allowed=false`
- behavior when the manifest row has `curated_embedding_preflight_allowed=false`
- behavior when the manifest row has `curated_embedding_single_allowed=false`
- behavior when the manifest row has `ready_for_preflight_after_manifest=false`

If any check is absent or ambiguous, the later PR must stop at documentation and must not execute the dry-run.

## Required repository-search checks for the later PR

Before any later dry-run execution, search the repository for:

- the Typer app definition for `curated_embedding_preflight`
- the Typer app definition for `curated_embedding_single`
- the validation path for `g3sx30_dry_run_preflight_manifest.csv`
- any code path that writes `.npy`
- any code path that writes `data/output`
- any code path that calls Biohub
- any code path that calls ESMC
- any code path that changes `ready_for_preflight`
- any code path that updates Gate 8 or Gate 9
- any code path that calls Boltz, AF3, or Chai

The later PR must document which files were inspected and why the selected command remains dry-run-only.

## Required no-run proof for this PR

This command discovery note PR must remain docs-only. Its validation may run tests and linters, but it must not run preflight commands.

Allowed validation for this PR:

- `uv run ruff format src/ tests/`
- `uv run ruff check src/ tests/`
- `uv run ruff format --check src/ tests/`
- `uv run mypy src/`
- `uv run pytest -q`
- `git diff --check`

Forbidden validation for this PR:

- `uv run curated-embedding-preflight`
- `uv run curated-embedding-single`
- `uv run python -m longevity_port_pipelines.stages.curated_embedding_preflight`
- `uv run python -m longevity_port_pipelines.stages.curated_embedding_single`
- any command that calls Biohub / ESMC
- any command that generates embeddings
- any command that writes `.npy`
- any command that writes `data/output`
- any command that changes `ready_for_preflight`
- any command that promotes Gate 8 or Gate 9
- any command that calls Boltz, AF3, or Chai

## Stop conditions for the later execution PR

A later execution PR must stop before running anything if:

- the help text does not expose a dry-run flag
- the help text does not expose a no-live-call or equivalent guardrail
- the help text does not expose an output-disable or no-output-artifacts guardrail
- the command would require Biohub or ESMC credentials
- the command would generate embeddings
- the command would write `.npy`
- the command would write `data/output`
- the command would change `ready_for_preflight`
- the command would promote Gate 8 or Gate 9
- the command would call Boltz, AF3, or Chai
- the command would add a biological claim

## Allowed language

Use language like:

- command discovery note
- help-output checklist
- no-run proof
- docs-only checkpoint
- runtime remains blocked
- no live provider
- no output artifacts
- not ready_for_preflight
- no Gate 8 / Gate 9 promotion
- no biological claim

## Disallowed language

Do not describe this note as:

- a completed preflight run
- a dry-run execution result
- a live Biohub call
- an ESMC embedding generation
- an embedding fill
- `ready_for_preflight`
- Gate 8 eligible
- Gate 9 eligible
- Boltz ready
- AF3 ready
- Chai ready
- validated longevity signal
- validated biological hit
- confirmed binding change
- confirmed functional effect
- safe to port
- proven pro-longevity variant
