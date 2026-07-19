# Scoped TP53/MDM2 missing-embedding fill manifest

This checkpoint prepares a reproducible, machine-readable execution contract
for the two missing MDM2 embeddings:

- mouse `P23804`;
- hamster `A0ABM2YB85`.

It is intentionally larger than a manifest-only fixture. It binds each row to
the committed external exact-sequence result and the committed local
prerequisite audit, declares the future canonical local embedding path, and
records a separate table-only validation result.

## Source state

The MDM2 Gate 7 strict panel is elephant `G3SX30`, mouse `P23804`, and hamster
`A0ABM2YB85`. `G3SX30` is excluded from this fill manifest because its local
embedding is already `present_valid`.

Rat remains `deferred_pending_source` and is excluded from the strict panel.
TP53 also remains `deferred_pending_source`. Aggregate Gate 7, Gate 8, and
Gate 9 remain closed.

PR #351 established passed external exact-sequence bindings for `P23804` and
`A0ABM2YB85`, including exact normalized sequence SHA-256 values. The local
prerequisite audit records both corresponding embeddings as `missing`.

## Execution contract

The two-row manifest records exact accession, taxid, sequence length, sequence
SHA-256, committed source table and row references, portable external sequence
filenames, model `esmc-300m-2024-12`, and declared canonical local `.npy` paths
under the ignored embedding root.

The `.npy` paths are declarations only. This checkpoint does not create those
files and does not write under `data/output`.

The contract records:

- `fill_scope=scoped_mdm2_missing_embeddings_only`;
- `execution_mode=table_only`;
- `fill_status=planning_policy_updated_runtime_blocked`;
- `live_fill_allowed=false`;
- `fill_execution_allowed=false`.

## Table-only validation result

The committed validation result records:

- `manifest_validation_status=passed_table_only_validation`;
- `scoped_missing_embedding_fill_manifest_status=prepared_execution_contract_only`;
- `validated_manifest_accessions=P23804|A0ABM2YB85`;
- `external_binding_validation_status=passed_exact_external_non_committed_binding`;
- `sequence_hash_binding_status=passed_exact_hash_bound`;
- `local_prerequisite_validation_status=passed_missing_embedding`;
- `embedding_artifact_status=missing_not_created`;
- `authorization_status=pending_explicit_scoped_live_fill_authorization`;
- `allowed_next_action=request_explicit_scoped_live_fill_authorization`.

Ordinary committed validation does not require
`LONGEVITY_PORT_EXTERNAL_SEQUENCE_BINDING_ROOT`. The external root is needed
only to rebuild or re-observe the underlying external sequence bindings.

## Boundaries

This checkpoint makes no BioHub or ESMC call, generates no embedding, creates
or commits no `.npy`, commits no `data/output` artifact, commits no raw FASTA
or normalized amino-acid sequence, runs no contrast, does not allow Gate 8
entry, does not promote Gate 8 or Gate 9, and makes no biological claim.

The next action is a separate request for explicit scoped live-fill
authorization. That authorization is not granted here.
