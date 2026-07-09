# G3SX30 one-row live embedding runtime observation

This note records the guarded one-row G3SX30 live embedding runtime observation.

The live call used the manifest-aware wrapper added in this PR. It did not use ordinary `curated-embedding-single` as a substitute.

## Command

The live command was:

```powershell
uv run g3sx30-live-embedding-one-row --yes-live --max-live-batch-size 1
```

The command output was captured outside the repository:

```text
D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_output.txt
```

The validation JSON was also written outside the repository:

```text
D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json
```

These external observation artifacts are not committed.

## Reviewed inputs

The command validated:

```text
manifest_path = data/input/g3sx30_dry_run_preflight_manifest.csv
manifest_row_index = 1
reviewed_sequence_fasta = D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta
candidate_id = tp53_mdm2_elephant_seed_mdm2_chain
chain = mdm2
target_accession = G3SX30
target_taxid = 9785
gene_symbol = MDM2
model_name = esmc-300m-2024-12
sequence_length = 492
sequence_sha256 = e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f
```

## Live result

```text
mode = live
status = live_completed
embedding_shape = 492x960
live_exit_code = 0
embedding_exists = true
```

The generated local runtime artifact is:

```text
data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy
```

The generated `.npy` artifact is local runtime output and is not committed.

## Local artifact validation

```text
embedding_exists = true
shape = 492x960
dtype = float32
finite = true
sequence_length_matches = true
biohub_esmc_called = true
embedding_generation_performed = true
npy_artifact_created = true
data_output_artifact_committed = false
ready_for_preflight_promoted = false
gate8_promoted = false
gate9_promoted = false
biological_claim_made = false
artifact_location = local_runtime_data_output_ignored_by_git
```

## Boundary

This runtime observation does not:

- commit the generated `.npy` artifact
- commit any `data/output` artifact
- commit the external FASTA artifact
- commit the external live log
- commit the external validation JSON
- promote `ready_for_preflight`
- promote Gate 8 or Gate 9
- call Boltz / AF3 / Chai
- rerun enrichment or contrast
- make biological claims

## Next state

This closes the first guarded G3SX30 one-row live embedding runtime observation.

The result is a technical runtime checkpoint only. It confirms that the reviewed G3SX30 MDM2 sequence can be embedded with the remote Biohub / ESMC path under explicit one-row guardrails. It does not make a biological claim and does not unlock downstream gates by itself.
