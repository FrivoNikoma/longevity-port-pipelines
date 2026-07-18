# TP53/MDM2 MDM2 missing-embedding exact-sequence provenance audit result

This checkpoint audits committed exact-sequence provenance for the two MDM2
strict-panel accessions whose local `esmc-300m-2024-12` embeddings are missing:

- mouse `P23804`;
- hamster `A0ABM2YB85`.

It is a committed result, not a console-only observation and not another
approval layer.

## Mouse: P23804

The committed Gate 7 row confirms reviewed UniProtKB Swiss-Prot identity,
`Mus musculus`, taxid `10090`, MDM2, a complete sequence, and expected length
`489`.

No committed exact sequence SHA-256 was found on a committed row keyed exactly
to `P23804`.

The official accession FASTA endpoint is identified for a later external,
non-committed materialization step, but exact sequence bytes are not yet bound
or hash-reviewed for controlled fill.

Result:

- `source_identity_provenance_ready=true`;
- `committed_exact_sequence_sha256_status=missing_not_committed`;
- `external_exact_sequence_bytes_bindable=true`;
- `external_exact_sequence_bytes_bound=false`;
- `controlled_fill_sequence_input_status=blocked_missing_committed_sha256_and_non_committed_exact_sequence_binding`.

## Hamster: A0ABM2YB85

The committed hamster complete-sequence review confirms the accepted
`A0ABM2YB85` / `XP_040610761.1` 510-aa sequence group.

The exact committed sequence SHA-256 is:

`77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5`

The official accession FASTA endpoint is identified, but the exact sequence
bytes are still not bound as an external non-committed controlled-fill input.

Result:

- `source_identity_provenance_ready=true`;
- `committed_exact_sequence_sha256_status=present_committed`;
- `external_exact_sequence_bytes_bindable=true`;
- `external_exact_sequence_bytes_bound=false`;
- `controlled_fill_sequence_input_status=blocked_pending_non_committed_exact_sequence_binding`.

## Panel result

The combined panel result is:

- `panel_source_identity_ready_accessions=P23804|A0ABM2YB85`;
- `panel_sha256_ready_accessions=A0ABM2YB85`;
- `panel_sha256_missing_accessions=P23804`;
- `panel_exact_sequence_bytes_bound_accessions=none`;
- `panel_sequence_provenance_status=blocked_pending_exact_sequence_bindings_and_mouse_hash`;
- `later_missing_embedding_fill_manifest_allowed=false`;
- `panel_allowed_next_action=prepare_external_non_committed_exact_sequence_bindings_and_mouse_hash_review`.

## Boundaries

This checkpoint:

- fetches no sequence in repository runtime;
- calls neither BioHub nor ESMC;
- generates no embedding;
- creates or commits no `.npy` artifact;
- commits no `data/output` artifact;
- runs no contrast;
- keeps Gate 8 and Gate 9 closed;
- makes no biological claim.
