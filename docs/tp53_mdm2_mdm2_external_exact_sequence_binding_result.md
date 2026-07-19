# TP53/MDM2 external exact-sequence binding result

This checkpoint records metadata-only bindings for the two MDM2 strict-panel
accessions whose local `esmc-300m-2024-12` embeddings are missing:

- mouse `P23804`;
- hamster `A0ABM2YB85`.

The raw FASTA files and normalized amino-acid sequence bytes are stored outside
the repository under a user-provided
`LONGEVITY_PORT_EXTERNAL_SEQUENCE_BINDING_ROOT`. The committed table contains
only portable relative filenames, source metadata, lengths, and hashes.

## P23804

The externally materialized UniProtKB FASTA record passed:

- accession check: `P23804`;
- taxid check: `10090`;
- expected length check: `489`;
- exact normalized sequence SHA-256:
  `0841e7c8ebd6a4a9e9e051538600d8f201c6682b3246dfb95ba301ab6233a3e3`.

This checkpoint establishes the exact sequence SHA-256 that was absent from the
preceding provenance audit.

## A0ABM2YB85

The externally materialized UniProtKB FASTA record passed:

- accession check: `A0ABM2YB85`;
- taxid check: `10036`;
- expected length check: `510`;
- exact normalized sequence SHA-256:
  `77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5`.

The observed hamster hash matches the already committed complete-sequence
review hash.

## Permission boundary

Both bindings have status
`passed_exact_external_non_committed_binding`. Therefore:

- `panel_binding_ready_accessions=P23804|A0ABM2YB85`;
- `panel_binding_status=ready_for_scoped_missing_embedding_fill_manifest`;
- `panel_runtime_blocker_code=none`;
- `later_missing_embedding_fill_manifest_allowed=true`;
- `allowed_next_action=prepare_scoped_missing_embedding_fill_manifest_dry_run`.

This permission is limited to preparing a later scoped missing-embedding fill
manifest and its dry-run validation. It does not authorize a live embedding
fill.

## Boundaries

This checkpoint:

- commits no raw FASTA or amino-acid sequence bytes;
- stores no machine-specific absolute binding path;
- makes no BioHub or ESMC call;
- generates no embedding;
- creates or commits no `.npy`;
- commits no `data/output` artifact;
- runs no contrast;
- keeps Gate 8 and Gate 9 closed;
- makes no biological claim.
