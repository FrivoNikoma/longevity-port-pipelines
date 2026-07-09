
# G3SX30 one-row live embedding strict guardrail wrapper

This note records the source-level guardrail wrapper for the `Execute one-row G3SX30 live embedding with strict guardrails` PR.

The wrapper is an executable boundary for exactly one reviewed G3SX30 row. It exists because the ordinary `curated-embedding-single` command is not manifest-aware and must not be used as a substitute for G3SX30 manifest row #1 execution.

## Command

The command entry point is:

```text
g3sx30-live-embedding-one-row = longevity_port_pipelines.stages.g3sx30_live_embedding_one_row:app
```

The default dry-run command is:

```powershell
uv run g3sx30-live-embedding-one-row
```

The live command must be explicit:

```powershell
uv run g3sx30-live-embedding-one-row --yes-live --max-live-batch-size 1
```

## Required sources

The wrapper reads the committed identity manifest:

```text
data/input/g3sx30_dry_run_preflight_manifest.csv#1
```

It also reads the external non-committed reviewed sequence artifact:

```text
D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta
```

The external FASTA is not committed.

The wrapper validates the prior approval checkpoint from:

```text
docs/current_gate_map.md
```

## Guardrails

The wrapper requires:

```text
manifest_row_index = 1
candidate_id = tp53_mdm2_elephant_seed_mdm2_chain
chain = mdm2
target_accession = G3SX30
target_taxid = 9785
gene_symbol = MDM2
reviewed_sequence_length = 492
reviewed_sequence_sha256 = e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f
approved_next_action = execute_one_row_g3sx30_live_embedding_with_strict_guardrails
max_live_batch_size = 1
explicit --yes-live for Biohub / ESMC
```

The expected local runtime embedding path is:

```text
data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy
```

## Boundary

This wrapper does not permit:

- more than one manifest row
- any manifest row except row #1
- a sequence fetch during live embedding execution
- a committed FASTA sequence artifact
- a committed `.npy` artifact
- a committed `data/output` artifact
- `ready_for_preflight` promotion
- Gate 8 promotion
- Gate 9 promotion
- Boltz / AF3 / Chai calls
- enrichment or contrast reruns
- biological claims

## Current checkpoint

This source checkpoint adds the strict wrapper and tests.

It does not itself call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output`, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make biological claims.

After this checkpoint, the same PR may run the guarded command with explicit `--yes-live --max-live-batch-size 1` and then record the live runtime observation without committing the generated `.npy`.
