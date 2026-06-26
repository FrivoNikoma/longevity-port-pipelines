# Brandt's bat P09874 curated merge dry-run

This note records a local dry-run of the curated ortholog merge path
for the `4xhu` / `P09874` receptor-chain follow-up.

## Input

Curated input file:

`data/input/curated_ortholog_candidates.csv`

Curated row:

* complex_id: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
* chain: `receptor`
* source_uniprot: `P09874`
* source_species_taxid: `9606`
* target_species: `brandts_bat`
* target_species_taxid: `109478`
* target_accession: `EPQ16369.1`
* target_accession_db: `NCBI Protein`
* curation_status: `primary_candidate`
* target_sequence_length: `1024`

NCBI Protein FASTA header:

`>EPQ16369.1 Poly [ADP-ribose] polymerase 1 [Myotis brandtii]`

## Validation dry-run

The curated input validation reported:

```text
Input status counts:
  has_curated_ortholog_candidate: 1

Rows with curated ortholog candidates: 1
```

The validated row had:

* target_accessions: `EPQ16369.1`
* target_accession_dbs: `NCBI Protein`
* curation_statuses: `primary_candidate`
* input_status: `has_curated_ortholog_candidate`

## Merge dry-run

Merge script:

`scripts/merge_curated_ortholog_coverage.py`

Inputs:

* standard coverage:
  `data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage.csv`
* curated orthologs:
  `data/input/curated_ortholog_candidates.csv`
* output:
  `data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage_with_curated.csv`
* conflict policy:
  `keep_standard`

Result:

```text
standard mappings: 69
curated mappings: 1
merged mappings: 70
conflict policy: keep_standard
```

The merged row was:

* source_uniprot: `P09874`
* source_species_taxid: `9606`
* target_uniprot: `EPQ16369.1`
* target_species_taxid: `109478`
* is_reviewed: `false`
* source_db: `curated:NCBI Protein`
* target_sequence_length: `1024`

## Interpretation

This confirms that the curated ortholog input can be converted into
an `OrthologMapping` and merged with the existing core3-expanded
ortholog coverage table.

This does not mean that:

* embeddings have been generated for the curated Brandt's bat sequence;
* downstream enrichment has been recomputed;
* Boltz has been called;
* the full 5-vs-3 species panel is complete;
* `bowhead_whale` has been resolved.

No Boltz API calls were made.
No `data/output/` artifacts are committed.
