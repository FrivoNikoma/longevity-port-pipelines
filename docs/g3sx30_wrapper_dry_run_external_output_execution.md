# G3SX30 wrapper dry-run external output execution

This PR turns the reviewed G3SX30 wrapper dry-run command from a fail-closed placeholder into a minimal safe dry-run writer.

The reviewed command is:

```powershell
uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json
```

The reviewed external output path is:

```text
D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json
```

The output JSON is external and must not be committed.

## What the dry-run writes

The JSON observation records:

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

## What this PR allows

This PR allows only the reviewed external-output dry-run path.

It may:

- read and validate `data/input/g3sx30_dry_run_preflight_manifest.csv#1`
- validate the G3SX30 constants
- validate the reviewed external output path
- write the small JSON dry-run observation to the reviewed external output path

## What remains forbidden

This PR does not allow:

- Biohub / ESMC calls
- embedding generation
- `.npy` artifact creation
- `data/output` artifact commits
- live execution
- manifest execution beyond reading and validating reviewed row #1
- `ready_for_preflight`
- Gate 8 or Gate 9 promotion
- Boltz / AF3 / Chai calls
- enrichment or contrast reruns
- biological claims

## Output handling

The output JSON is written outside the repository.

The repository should commit source, tests, docs, and gate-map updates only. It should not commit the external JSON observation.
