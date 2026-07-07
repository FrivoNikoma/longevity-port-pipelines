# G3SX30 wrapper dry-run observation checkpoint

This checkpoint records the already-executed G3SX30 wrapper dry-run external observation.

It does not rerun the dry-run.

## External observation

The observation file was created outside the repository:

```text
D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json
```

The external JSON observation is not committed.

## Observed result

The observed dry-run result recorded:

```text
dry_run_executed = true
manifest_row_index = 1
target_accession = G3SX30
target_taxid = 9785
reviewed_sequence_length = 492
reviewed_sequence_sha256 = e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f
biohub_esmc_called = false
embedding_generation_performed = false
npy_artifact_created = false
data_output_artifact_created = false
ready_for_preflight_promoted = false
gate8_promoted = false
gate9_promoted = false
biological_claim_made = false
```

The observed dry-run also recorded:

```text
manifest_row_read = true
manifest_row_validated = true
sequence_fetch_performed = false
live_execution_performed = false
manifest_execution_performed = false
curated_embedding_preflight_run = false
curated_embedding_single_run = false
boltz_called = false
af3_called = false
chai_called = false
enrichment_rerun = false
contrast_rerun = false
claim_status = technical_checkpoint
```

## Boundary

This checkpoint records only the already-observed external JSON summary.

It does not:

- rerun `g3sx30-wrapper-dry-run`
- commit the external JSON observation
- call Biohub / ESMC
- generate embeddings
- create `.npy` artifacts
- create or commit `data/output` artifacts
- run a live path
- promote `ready_for_preflight`
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- rerun enrichment or contrast
- make biological claims

## Next practical step

After this checkpoint, do not add another generic checkpoint, review, scaffold, or blocker layer.

The next practical step should be:

```text
Review G3SX30 dry-run observation and decide the next data-producing step
```

That decision should either prepare a one-row live embedding decision or repair a concrete blocker found in the dry-run observation.
