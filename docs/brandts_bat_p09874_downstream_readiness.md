# Brandt's bat P09874 downstream readiness

This note records the local downstream-readiness checkpoint for the curated Brandt's bat `P09874` receptor candidate after live ESMC embedding generation.

This is an audit checkpoint only. It does not commit any runtime artifact from `data/output/`.

## Target
```text
complex_id: 4xhu__A1_P09874--4xhu__B1_Q9UNS1
chain: receptor
source_uniprot: P09874
source_species_taxid: 9606
target_species: brandts_bat
target_species_taxid: 109478
target_accession: EPQ16369.1
target_sequence_length: 1024
model_name: esmc-300m-2024-12
```

Expected local embedding path:
```text
data/output/embeddings/esmc-300m-2024-12/4xhu__A1_P09874--4xhu__B1_Q9UNS1_receptor_109478.npy
```

## Local readiness checks

The curated input file was present:
```text
curated input exists: True
```

The curated candidate row was present and uniquely matched:
```text
curated matching rows: 1
curated status: primary_candidate
target species: brandts_bat
target accession: EPQ16369.1
target sequence length: 1024
```

The merged curated coverage file was present:
```text
merged coverage exists: True
```

The merged coverage schema was:
```text
source_uniprot, source_species_taxid, target_uniprot, target_species_taxid, target_sequence, is_reviewed, source_db
```

The merged coverage contained the expected human `P09874` to Brandt's bat taxid `109478` mapping:
```text
coverage matching rows: 1
source_uniprot: P09874
source_species_taxid: 9606
target_species_taxid: 109478
```

The local embedding artifact was present at the expected canonical path:
```text
embedding exists: True
```

A follow-up curated embedding preflight confirmed:
```text
primary curated candidates: 1
present embeddings: 1
```

## Interpretation

This checkpoint confirms that the curated Brandt's bat `P09874` receptor candidate is ready for the next downstream analysis layer:

- the curated input row exists;
- the merged coverage contains the corresponding human `P09874` to Brandt's bat taxid `109478` mapping;
- the local ESMC embedding exists at the canonical embedding path;
- the curated embedding preflight reports the candidate as present.

## Safety notes

This checkpoint did not:

- call Biohub / ESMC;
- call Boltz;
- rerun enrichment analysis;
- modify curated ortholog inputs;
- commit the local `.npy` embedding artifact;
- commit any `data/output/` artifact.
