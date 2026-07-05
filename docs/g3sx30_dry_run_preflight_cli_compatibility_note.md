# G3SX30 dry-run preflight CLI compatibility note

This is a docs-only compatibility note comparing the G3SX30 dry-run preflight checklist and command discovery expectations against the actual current CLI implementation.

It does not run `curated-embedding-preflight`, does not run `curated_embedding_preflight`, does not run `curated-embedding-single`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.

## Source documents

This compatibility note resolves the rough edge between:

- `docs/g3sx30_dry_run_preflight_execution_checklist.md`
- `docs/g3sx30_dry_run_preflight_command_discovery_note.md`
- the actual CLI implementation

The source manifest row remains `data/input/g3sx30_dry_run_preflight_manifest.csv#1`.

That source manifest row remains planning-only and records:

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

## Actual observed script names

`pyproject.toml` exposes these script entry points:

- `curated-embedding-preflight = longevity_port_pipelines.stages.curated_embedding_preflight:app`
- `curated-embedding-single = longevity_port_pipelines.stages.curated_embedding_single:app`

This compatibility note records those script names from source inspection only. It does not run either script and does not run `--help`.

## Actual `curated-embedding-preflight` behavior

`src/longevity_port_pipelines/stages/curated_embedding_preflight.py` defines a Typer app and a `main` command with these parameters:

- `curated_orthologs`
- `output_dir`
- `model_name`
- `output`

The observed defaults are:

- `curated_orthologs=data/input/curated_ortholog_candidates.csv`
- `output_dir=data/output`
- `model_name=esmc-300m-2024-12`
- `output=data/output/curated_ortholog_embedding_preflight.csv`

Observed compatibility with checklist expectations:

| Checklist expectation | Actual current `curated-embedding-preflight` behavior |
| --- | --- |
| manifest input flag | absent; the command reads curated ortholog candidates, not the G3SX30 manifest |
| candidate/accession filtering flag | absent for G3SX30 manifest use; filtering is primary curated-ortholog filtering |
| explicit dry-run flag | absent |
| no-live-call/provider-disable flag | absent |
| max-live-batch-size or zero-live-work guardrail | absent |
| no-output-artifacts or output-disable flag | absent |
| behavior when manifest flags are false | absent/ambiguous; the command does not read the manifest flags |
| dry-run-only implementation | satisfied by implementation: it checks embedding availability and does not call Biohub / ESMC |
| output behavior | writes an output CSV by default |
| default output path | `data/output/curated_ortholog_embedding_preflight.csv` |

Important interpretation: `curated-embedding-preflight` is already dry-run-only by implementation, but it is not manifest-aware and does not expose the explicit runtime guardrail flags expected by the G3SX30 checklist. It should not be treated as a direct G3SX30 manifest-row execution command as-is.

## Actual `curated-embedding-single` behavior

`src/longevity_port_pipelines/stages/curated_embedding_single.py` defines a Typer app and a `main` command with these relevant parameters:

- `complex_id`
- `chain`
- `target_species_taxid`
- `curated_orthologs`
- `output_dir`
- `model_name`
- `biohub_api_url`
- `yes_live`
- `skip_existing`

Observed compatibility with checklist expectations:

| Checklist expectation | Actual current `curated-embedding-single` behavior |
| --- | --- |
| manifest input flag | absent; the command reads curated ortholog candidates, not the G3SX30 manifest |
| candidate/accession filtering flag | partially satisfied through `complex_id`, `chain`, and `target_species_taxid`; no direct G3SX30 manifest row filter |
| explicit dry-run flag | absent |
| no-live-call/provider-disable flag | partially satisfied by default `yes_live=false`; live call requires `--yes-live` |
| max-live-batch-size or zero-live-work guardrail | absent |
| no-output-artifacts or output-disable flag | absent |
| behavior when manifest flags are false | absent/ambiguous; the command does not read the manifest flags |
| dry-run by default | satisfied: without `--yes-live`, it returns dry-run status |
| accidental live-call risk | present if `--yes-live` is passed |
| Biohub/ESMC call path | present behind `--yes-live` through token loading and embedding generation |

Important interpretation: `curated-embedding-single` is dry-run by default, but it can call Biohub / ESMC if misused with `--yes-live`. It is not manifest-aware and should not be used for G3SX30 execution until a manifest-aware wrapper/adapter or stronger explicit guardrails exist.

## Compatibility verdict

The current CLI does not match the G3SX30 dry-run preflight checklist expectations closely enough for direct execution.

Satisfied or partly satisfied:

- actual script names exist
- `curated-embedding-preflight` is dry-run-only by implementation
- `curated-embedding-single` is dry-run by default
- `curated-embedding-single` has a live-call gate through `--yes-live`
- both commands can compute or report embedding paths without committing `.npy` artifacts when used in dry-run mode

Absent or ambiguous:

- no G3SX30 manifest input flag
- no direct manifest-row validation path
- no explicit `--dry-run` flag on `curated-embedding-preflight`
- no explicit `--dry-run` flag on `curated-embedding-single`
- no explicit `--no-live-call` flag
- no explicit `--max-live-batch-size 0` guardrail
- no explicit `--no-output-artifacts` guardrail
- no behavior tied to manifest flags such as `biohub_call_allowed=false`
- no behavior tied to `embedding_generation_allowed=false`
- no behavior tied to `curated_embedding_preflight_allowed=false`
- no behavior tied to `curated_embedding_single_allowed=false`
- no behavior tied to `ready_for_preflight_after_manifest=false`
- current `curated-embedding-preflight` writes a CSV under `data/output` by default

## Output-path implication

A future execution PR must not use the default `curated-embedding-preflight` output path if the output would be committed.

The default path is `data/output/curated_ortholog_embedding_preflight.csv`.

A future safe dry-run-only preflight, if allowed, should redirect output outside committed `data/output`, for example to a temporary or manually reviewed scratch path, and should explicitly confirm that the output is not committed.

Examples of safer output locations for a later PR discussion:

- local temp path outside the repository
- ignored scratch path
- `manual_reviews` path only if the PR explicitly intends to review and commit a small text/CSV review artifact

This compatibility note does not choose or run any output path.

## Adapter/wrapper implication

A manifest-aware dry-run adapter or wrapper is likely needed before execution.

The adapter/wrapper should:

- read `data/input/g3sx30_dry_run_preflight_manifest.csv#1`
- require `dry_run_only=true`
- require `max_live_batch_size=0`
- require `ready_for_preflight_after_manifest=false`
- require all runtime permission flags to remain false
- refuse Biohub / ESMC calls
- refuse embedding generation
- refuse `.npy` writes
- refuse committed `data/output` artifacts
- select or transform only the one intended G3SX30 row
- route any output to an explicitly reviewed non-runtime location
- preserve `claim_status=technical_checkpoint`
- refuse Gate 8 / Gate 9 promotion
- refuse biological claims

## Stop conditions before any actual run

Before any actual dry-run preflight execution, stop if any of the following remain true:

- the command is not manifest-aware
- the command cannot bind to `data/input/g3sx30_dry_run_preflight_manifest.csv#1`
- the command cannot verify `dry_run_only=true`
- the command cannot enforce `max_live_batch_size=0`
- the command cannot enforce `ready_for_preflight_after_manifest=false`
- the command cannot enforce `biohub_call_allowed=false`
- the command cannot enforce `esmc_call_allowed=false`
- the command cannot enforce `embedding_generation_allowed=false`
- the command cannot enforce `curated_embedding_preflight_allowed=false`
- the command cannot enforce `curated_embedding_single_allowed=false`
- the command would write committed `data/output` artifacts
- the command would write `.npy`
- the command would require Biohub or ESMC credentials
- the command would call Biohub / ESMC
- the command would change `ready_for_preflight`
- the command would unlock the manifest runtime path
- the command would promote Gate 8 or Gate 9
- the command would call Boltz, AF3, or Chai
- the command would rerun enrichment or contrast
- the command would add a biological claim

## Recommended next PR options

After this compatibility note, the next PR should choose one of these paths:

1. Add a manifest-aware dry-run preflight adapter/wrapper scaffold.
2. Add a tiny source-level guardrail to `curated-embedding-preflight` before any G3SX30 execution.
3. Stop and keep G3SX30 runtime-blocked because required guardrails are absent.

A future execution PR should not directly use the current `curated-embedding-preflight` default behavior against G3SX30 unless the manifest mismatch and output-path issue are resolved.
