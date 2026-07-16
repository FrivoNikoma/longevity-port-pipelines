# TP53/MDM2 embedding-based NEGATOME input repair and retry result

## Review question

Can the two checked input blockers from the first TP53/MDM2
embedding-based NEGATOME attempt be repaired sufficiently to execute
`compute_negatome_control_ratio`, or does a new concrete blocker remain?

## Result

This is a result-bearing repair/retry, not a preflight-only, audit-only,
scaffold-only, vocabulary-only, or generic-refactor-only checkpoint.

The two blockers recorded by the first attempt are repaired:

```text
chain_local_to_full_length_interface_mapping_not_verified -> resolved
exact_negatome_pair_lookup_key_missing -> resolved
```

One new concrete blocker remains:

```text
negative_partner_embedding_missing_or_invalid
```

The reviewed negative-partner embedding path is:

```text
data/interim/negatome_embeddings/esmc-300m-2024-12/G3UAZ0.npy
```

That file was absent during the read-only retry. Therefore
`compute_negatome_control_ratio` was not executed and
`negatome_control_ratio=not_computed`.

## Official 1YCR chain A to full-length Q00987 mapping

Official RCSB DBREF maps 1YCR chain A to human MDM2 `Q00987`, residues
`17..125`. The 85 observed coordinate residues form the continuous interval
`GLU25..VAL109`.

The committed 47 chain-local interface indices map with the unique zero-based
offset `+24` to these full-length Q00987 indices:

```text
24|25|26|27|47|48|49|50|51|52|53|54|55|56|57|58|59|60|61|62|65|66|67|68|69|70|71|72|73|74|81|85|90|91|92|93|94|95|96|97|98|99|100|102|103|106|108
```

All required mapping invariants pass:

```text
mapping_unique=true
mapped_interface_count=47
mapped_indices_unique=true
mapped_indices_in_bounds=true
residue_identity_consistent=true
```

The tracked mapping table is
`data/input/tp53_mdm2_1ycr_q00987_interface_mapping.csv` with SHA256
`73cc5548869e537cd90d78a3cf1a417097f85b9dde99818d8c09f96cce8aa325`.

The current official PDB download SHA256
`d8f23749da9ec22da2e17bb31c33803e3db6123233cd0404bdc005111196e7a3` differs from the earlier committed extraction
artifact SHA256 `7b4e503dea1fe3a6966b9676a1b98caf511c735cde01029cd0998e2319e75493`. This byte-level difference
is recorded explicitly. The committed interface labels and residue-level
mapping were revalidated against the current official structure and canonical
Q00987 sequence.

## TP53RTG12 protein-level provenance

The article-reported Ensembl gene `ENSLAFG00000028299` resolves to one
transcript `ENSLAFT00000037003`, one protein translation
`ENSLAFP00000024998`, and UniProtKB protein accession `G3UAZ0`.

Ensembl and UniProt return the same exact 364-aa sequence:

```text
sequence_length=364
sequence_sha256=29fff7f2b98f31a8b3efc8aed0f9498206086e556950c818d1004ad41231bff7
cross_source_sequence_exact_match=true
negative_partner_sequence_deterministic=true
protein_level_negative_partner_resolved=true
```

Alignment to human TP53 confirms the reported anchor context:

```text
F19 -> F19
W23 -> G23
L26 -> L26
reported_w23g_alignment_consistent=true
```

## Exact reviewed NEGATOME-style pair

The runtime-schema-valid row is committed in
`data/input/tp53_mdm2_repaired_negatome_control_pairs.csv`:

```text
lookup_key=tp53_mdm2_elephant_seed_mdm2_chain|mdm2|elephant
source_uniprot=Q00987
negative_partner_uniprot=G3UAZ0
control_type=negative_coimmunoprecipitation_partner_context
exact_pair_schema_valid=true
repaired_pair_runtime_loadable=true
```

Pair table SHA256: `3a97680c46914b468cf1ef1de72bf5da9e51109a31f4d2ba5ee3cdc3af61eb73`.

This is a manually literature-curated NEGATOME-style negative context. It is
not represented as official membership in the NEGATOME database.

## Embedding invariants and retry boundary

Human MDM2 and elephant MDM2 pass the required ESMC invariants:

```text
model_name=esmc-300m-2024-12
human_shape=491x960
elephant_shape=492x960
dtype=float32
finite=true
embedding_rows_equal_exact_reviewed_sequence_length=true
```

The required G3UAZ0 contract would be:

```text
embedding.shape[0] == 364
embedding.shape[1] == 960
model_name == esmc-300m-2024-12
dtype == float32
finite == true
```

No G3UAZ0 embedding existed, no new embedding was generated, and no Biohub / ESMC call was made.

## Gate state

```text
checked_blocker_count=1
checked_blocker=negative_partner_embedding_missing_or_invalid
embedding_based_negatome_control_computed=false
negatome_control_ratio=not_computed
proposed_gate6_repair_status=blocked_pending_control_repair
gate6_control_readiness_resolved_after=false
gate7_entry_allowed_after=false
gate8_promoted=false
gate9_promoted=false
biological_claim_made=false
```

This result does not open Gate 7, does not promote Gate 8 or Gate 9, does not
call Boltz / AF3 / Chai, commits no `.npy` or `data/output` artifact, and makes
no binding, functional, beneficial-breakage, adaptation, longevity, or other
biological claim.

## Result identity

```text
audit_report_sha256=ad54f4a73715f2093ebb359d0bd359b921672475f84f3af23ec5fb93bb8bdc71
audit_summary_sha256=f4e151a0d5495db226e2229a5d3302f3c287117ffd2efbc046cd47ac3b680b95
audit_candidate_pair_sha256=cdba63779575723026fdc28accba7c820a68e2d8d17903e68787b23cf4041049
result_metadata_sha256=412763e453ff99d4271fff95839dbf38e1d636f9ebfab497cb2f3b41862de068
```
