# Brandt's bat P09874 live embedding generation

This note records the first live Biohub / ESMC embedding generation for the curated Brandt's bat `P09874` receptor candidate.

This is an audit checkpoint only. The generated `.npy` embedding is a runtime artifact under `data/output/` and is not committed.

## Target

```text
complex_id: 4xhu__A1_P09874--4xhu__B1_Q9UNS1
chain: receptor
target_species: brandts_bat
target_species_taxid: 109478
target_accession: EPQ16369.1
target_accession_db: NCBI Protein
model_name: esmc-300m-2024-12
```

Expected embedding path:

```text
data/output/embeddings/esmc-300m-2024-12/4xhu__A1_P09874--4xhu__B1_Q9UNS1_receptor_109478.npy
```

## Pre-live dry-run

Before the live call, the single curated embedding runner reported:

```text
target_sequence_length: 1024
actual_sequence_length: 1024
sequence_length_status: matches
embedding_exists: False
mode: dry-run; add --yes-live to call Biohub/ESMC
status: dry_run_missing
```

## Live command

The live embedding was generated with:

```powershell
uv run curated-embedding-single `
   --complex-id 4xhu__A1_P09874--4xhu__B1_Q9UNS1 `
   --chain receptor `
   --target-species-taxid 109478 `
   --yes-live
```

## Live result

The live run completed successfully:

```text
mode: live
status: live_completed
embedding_shape: 1024x960
```

## Artifact validation

The generated local artifact was validated directly from the `.npy` file:

```text
exists: True
shape: (1024, 960)
dtype: float32
finite: True
```

A follow-up dry-run confirmed that the runner now sees the saved embedding:

```text
embedding_exists: True
status: dry_run_present
```

A follow-up curated embedding preflight confirmed:

```text
primary curated candidates: 1
present embeddings: 1
```

## Safety notes

This checkpoint did not:

- commit the `.npy` embedding artifact;
- modify curated ortholog inputs;
- modify ortholog coverage;
- rerun enrichment analysis;
- call Boltz;
- commit any `data/output/` artifact.

The generated embedding remains a local runtime artifact.
