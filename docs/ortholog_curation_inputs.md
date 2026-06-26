# Curated ortholog input contract

This document defines a conservative input contract for curated ortholog candidate rows.

The goal is to separate three states:

```text
curation evidence exists
curated ortholog candidate input exists
standard ortholog_coverage outputs are populated from curated inputs

Only the last state should be interpreted as populated ortholog coverage.

This contract intentionally does not modify the standard OMA/UniProt ortholog lookup path.
It only defines how curated candidates should be represented and validated before a future
override or merge step is added.

Why this layer exists

Some target species may have biologically plausible ortholog candidates that are not recovered
by the current automated lookup path.

For example, the 4xhu / P09874 follow-up found candidate evidence for brandts_bat
/ Myotis brandtii, while bowhead_whale remains unresolved. That evidence should be
preserved without implying that the species panel is complete or that live Boltz runs should
start.

Input location

Future populated curated candidate tables should use:

data/input/curated_ortholog_candidates.csv

A header-only example is provided at:

data/input/ortholog_candidates.example.csv
Required columns
complex_id
chain
target_species
source_uniprot
source_species_taxid
target_species_taxid
target_accession
target_accession_db
target_sequence
target_sequence_length
curation_status
evidence_source
curation_note
Column meanings
complex_id

The PINDER-style complex identifier.

Example:

4xhu__A1_P09874--4xhu__B1_Q9UNS1
chain

The chain role being curated.

Expected values should match downstream pipeline conventions, usually:

receptor
ligand
target_species

Repository species alias.

Example:

brandts_bat
source_uniprot

Human/reference source UniProt ID.

Example:

P09874
source_species_taxid

Reference species taxid.

For human reference rows, this should usually be:

9606
target_species_taxid

NCBI taxonomy ID for the target species.

Example for Brandt's bat:

109478
target_accession

Candidate ortholog accession.

This may come from UniProt, NCBI Protein, Ensembl, or another explicitly recorded source.

target_accession_db

Database or source namespace for target_accession.

Examples:

UniProt
NCBI Protein
Ensembl
target_sequence

Candidate amino-acid sequence.

Rows without a non-empty target_sequence are not counted as active curated candidates.

target_sequence_length

Length of the candidate amino-acid sequence.

This is included so reviewers can quickly distinguish full-length-like candidates from
short fragments or isoform-like candidates.

curation_status

Recommended values:

primary_candidate
supporting_candidate
rejected_candidate
unresolved

Only these active statuses are counted as curated candidates by the validator:

primary_candidate
supporting_candidate

Rejected or unresolved rows may be useful in evidence notes, but should not populate curated
candidate coverage.

evidence_source

Short provenance label.

Examples:

local_broad_probe
local_exact_taxid_probe
manual_literature_review
curation_note

Human-readable explanation of why the row is included, rejected, or unresolved.

Validation behavior

The validator distinguishes:

missing_input_file
missing_curated_ortholog_candidate
has_curated_ortholog_candidate

A row is counted as has_curated_ortholog_candidate only if it has:

all required columns;
non-empty target_accession;
non-empty target_accession_db;
non-empty target_sequence;
curation_status equal to primary_candidate or supporting_candidate.
Current interpretation guard

This contract does not mean that:

curated ortholog coverage is populated;
curated rows are automatically used by fetch_ortholog();
the 4xhu / P09874 species panel is complete;
bowhead_whale has a safe curated mapping;
live Boltz species-panel runs should start.

A future PR may add a dedicated merge/override step that converts validated curated rows into
standard ortholog coverage rows.

## Merging curated candidates into ortholog coverage

The contract also supports a conservative merge step:

```text
standard ortholog coverage
+ primary curated ortholog candidates
-> merged ortholog coverage

The merge step is implemented in:

scripts/merge_curated_ortholog_coverage.py

It converts only primary_candidate rows into OrthologMapping rows. supporting_candidate
rows remain evidence/validation rows and are not promoted into standard coverage by default.

The generated source_db value is prefixed with:

curated:

For example:

curated:NCBI Protein
Conflict policy

A conflict means that standard coverage and curated coverage both contain a mapping for the same:

source_uniprot
source_species_taxid
target_species_taxid

The default policy is:

keep_standard

This means a standard OMA/UniProt mapping is not silently overwritten by a curated row.

Supported policies:

keep_standard
prefer_curated
error

Recommended default for production-like runs:

keep_standard

Recommended debugging policy:

error
Example command
uv run python -m scripts.merge_curated_ortholog_coverage \
  --standard-coverage data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage.csv \
  --curated-orthologs data/input/curated_ortholog_candidates.csv \
  --output data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage_with_curated.csv \
  --conflict-policy keep_standard

This still does not run Boltz and does not change live species-panel behavior by itself.
