# Brandt's bat P09874 curated embedding preflight

This note records a dry-run embedding preflight for the curated Brandt's bat
`P09874` ortholog candidate.

It is an audit checkpoint only. It does not generate embeddings, call Biohub/ESMC,
modify ortholog coverage, rerun enrichment analysis, or call Boltz.

## Context

The curated ortholog input contains a primary Brandt's bat candidate for the
human/reference `P09874` receptor chain in:
```text
4xhu__A1_P09874--4xhu__B1_Q9UNS1
```

The curated target candidate is:
```text
target_species: brandts_bat
target_species_taxid: 109478
target_accession: EPQ16369.1
target_accession_db: NCBI Protein
chain: receptor
```

The curated merge dry-run previously showed that this candidate can be promoted
into merged ortholog coverage as a curated mapping, but that does not by itself
create ESMC embeddings.

## Command

The preflight was run with:
```powershell
uv run curated-embedding-preflight
```

This command checks primary curated ortholog candidates against the canonical
embedding path convention:
```text
data/output/embeddings/<model_name>/<complex_id>_<chain>_<species_taxid>.npy
```

For this repository, the current default model is:
```text
esmc-300m-2024-12
```

## Result

The dry-run output was:
```text
primary curated candidates: 1
missing embeddings: 1
```

The missing curated embedding was:
```text
complex_id: 4xhu__A1_P09874--4xhu__B1_Q9UNS1
chain: receptor
target_species: brandts_bat
target_species_taxid: 109478
target_accession: EPQ16369.1
model_name: esmc-300m-2024-12
```

Expected embedding path:
```text
data/output/embeddings/esmc-300m-2024-12/4xhu__A1_P09874--4xhu__B1_Q9UNS1_receptor_109478.npy
```

## Interpretation

This preflight means that the curated Brandt's bat `P09874` candidate is now
visible to the curated embedding audit layer, but its ESMC embedding has not yet
been generated.

This does not mean that:

* downstream enrichment has been recomputed;

* the curated candidate is already included in embedding-based analysis;

* the full `4xhu` / `P09874` species panel is complete;

* `bowhead_whale` has a safe curated mapping;

* Boltz species-panel runs should start.

## Safety notes

This dry-run did not:

* call Biohub / ESMC;

* generate a `.npy` embedding file;

* modify standard or merged ortholog coverage;

* rerun enrichment analysis;

* call Boltz;

* commit any `data/output/` artifact.

The generated local audit CSV remains a runtime output and should not be
committed:
```text
data/output/curated_ortholog_embedding_preflight.csv
```

## Next step

The next live step should be narrow and explicit: generate only the single
missing curated Brandt's bat receptor embedding for:
```text
4xhu__A1_P09874--4xhu__B1_Q9UNS1 receptor taxid=109478
```

That step should be handled separately from this documentation checkpoint,
because it will require an actual Biohub/ESMC call.
