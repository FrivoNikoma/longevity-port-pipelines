# G3SX30 dry-run preflight execution checklist

This checklist is a docs-only planning checkpoint for a later G3SX30 dry-run preflight execution PR.

It does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, and does not make biological claims.

## Source row

The checklist source is:

- `data/input/g3sx30_dry_run_preflight_manifest.csv#1`

That manifest row records:

- `target_accession=G3SX30`
- `target_accession_db=UniProtKB TrEMBL`
- `target_species=Loxodonta africana`
- `target_taxid=9785`
- `gene_symbol=MDM2`
- `source_dry_run_preflight_decision_table=data/input/g3sx30_dry_run_preflight_decisions.csv`
- `source_dry_run_preflight_decision_row_index=1`
- `source_dry_run_preflight_decision=approve_dry_run_preflight_for_planning`
- `source_dry_run_preflight_status_after_decision=dry_run_preflight_planning_approved_runtime_blocked`
- `source_allowed_next_action_after_decision=prepare_later_dry_run_preflight_manifest_pr`
- `source_max_live_batch_size_after_decision=0`
- `source_ready_for_preflight_after_decision=false`
- `reviewed_sequence_length=492`
- `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`
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
- `claim_status=technical_checkpoint`

## What a later execution PR may do

A later PR may prepare and run a dry-run-only preflight check only after explicitly confirming that the runtime command is still a dry-run and that no live provider or output artifact path is enabled.

The later execution PR must remain separate from this checklist PR.

The later execution PR must not silently convert this checklist into a live embedding fill, runtime unlock, Gate 8 promotion, Gate 9 promotion, Boltz run, AF3 run, Chai run, enrichment rerun, contrast rerun, or biological claim.

## Future command template

This is a non-executed template for a later PR. It must be checked against the repository's actual CLI/help before any execution.

```powershell
# TEMPLATE ONLY — do not run in this checklist PR.
# Before use, verify the real entry point and flags with the repository help text.
uv run python -m longevity_port_pipelines.stages.curated_embedding_preflight `
    --manifest data/input/g3sx30_dry_run_preflight_manifest.csv `
    --candidate-id tp53_mdm2_elephant_seed_mdm2_chain `
    --target-accession G3SX30 `
    --dry-run `
    --max-live-batch-size 0 `
    --no-live-call `
    --no-output-artifacts
```

If the real CLI differs from this template, the later PR must update the command explicitly and document why the replacement remains dry-run-only.

## Required pre-run checks for the later PR

Before any later dry-run execution, confirm all of the following:

- `git status -sb` is clean before the run.
- The branch name clearly says dry-run preflight execution.
- The source manifest row is still `data/input/g3sx30_dry_run_preflight_manifest.csv#1`.
- The source manifest row still has `dry_run_only=true`.
- The source manifest row still has `max_live_batch_size=0`.
- The source manifest row still has `ready_for_preflight_after_manifest=false`.
- The source manifest row still has `sequence_fetch_allowed=false`.
- The source manifest row still has `biohub_call_allowed=false`.
- The source manifest row still has `esmc_call_allowed=false`.
- The source manifest row still has `embedding_generation_allowed=false`.
- The source manifest row still has `curated_embedding_preflight_allowed=false`.
- The source manifest row still has `curated_embedding_single_allowed=false`.
- The source manifest row still has `reviewed_sequence_length=492`.
- The source manifest row still has `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`.
- The command is confirmed to be a dry-run command.
- The command is confirmed not to require Biohub or ESMC credentials.
- The command is confirmed not to generate embeddings.
- The command is confirmed not to write `.npy` artifacts.
- The command is confirmed not to write `data/output` artifacts.
- The command is confirmed not to change any status to `ready_for_preflight`.

## Required post-run checks for the later PR

After any later dry-run execution, confirm all of the following before committing:

- `git status -sb` shows only expected docs/table/test changes.
- No `.npy` files were created.
- No `data/output` artifacts were created or modified.
- No embedding files were created or modified.
- No Biohub / ESMC logs or credentials were committed.
- No target sequence row was mutated.
- No reviewed target sequence provenance row was mutated.
- No dry-run preflight decision row was mutated unless the PR explicitly says so.
- No manifest row was silently converted to `ready_for_preflight`.
- No Gate 8 or Gate 9 field was promoted.
- No Boltz, AF3, or Chai output was created.
- No enrichment or contrast output was created.
- No biological claim was added.

## Forbidden artifacts

The later dry-run execution PR must not commit:

- `.npy` files
- generated embedding arrays
- generated Biohub / ESMC output
- `data/output` artifacts
- Boltz output
- AF3 output
- Chai output
- enrichment rerun output
- contrast rerun output
- hidden credential files
- local cache files
- raw sequence fetch artifacts
- biological claim summaries

## Allowed language

Use language like:

- planning-only dry-run preflight execution checklist
- source manifest row
- dry-run-only preflight template
- runtime remains blocked
- no live provider
- no output artifacts
- not ready_for_preflight
- no Gate 8 / Gate 9 promotion
- no biological claim

## Disallowed language

Do not describe this checklist as:

- a completed preflight run
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
