# First TP53/MDM2 embedding-based NEGATOME control result

## Outcome

This is a result-bearing checked blocker result for the first attempted
TP53/MDM2 embedding-based NEGATOME control.

The existing runtime is available, and the local read-only audit confirmed
that the ignored human `Q00987` and elephant `G3SX30` MDM2 embeddings exist,
are finite `float32` matrices, are not tracked, and are not staged.

A control ratio was not computed because two concrete inputs are missing:

```text
checked_blocker_count=2
primary_missing_input_kind=chain_local_to_full_length_interface_mapping_not_verified
primary_expected_path=data/interim/pdb/1ycr.pdb
secondary_missing_input_kind=exact_negatome_pair_lookup_key_missing
secondary_expected_path=data/interim/negatome_control_pairs.csv
```

## Available embeddings

```text
human_embedding_shape=491x960
human_embedding_sha256=ee0b8d9025dd6b5a18ecf5f1a344b8ab819f559f652d92f32ea23a006a0d8eeb
elephant_embedding_shape=492x960
elephant_embedding_sha256=98ec10a07986e07c65a11f370f542e5b6c88453c544f9f0f49fb2fe0f8e6315c
```

The audit read the ignored `.npy` files only to verify shape, dtype, finiteness,
and SHA256. This PR writes or commits no `.npy` artifact and commits no
`data/output` artifact.

## Blocker 1: interface-coordinate mapping

The committed MDM2 mask uses
`zero_based_chain_local_residue_indices` for `85` observed residues in 1YCR
chain A, while the human Q00987 embedding spans `491` residues.

```text
interface_mask_direct_full_length_compatible=false
interface_mask_requires_canonical_sequence_mapping=true
local_1ycr_pdb_candidate_count=0
interface_mask_canonical_mapping_verified=false
```

The audit therefore did not apply the 47 chain-local interface indices to the
full-length embedding.

## Blocker 2: exact NEGATOME pair row

The ignored local pair table exists and contains `11` rows, but it has no row
for the exact runtime key:

```text
tp53_mdm2_elephant_seed_mdm2_chain|mdm2|elephant
```

The audit records:

```text
negatome_pair_related_row_count=0
negatome_pair_exact_lookup_row_count=0
exact_negatome_pair_lookup_available=false
```

Without the exact row, the negative-partner identifier, sequence, and expected
embedding path cannot be resolved.

## Result and gate state

```text
embedding_based_negatome_control_computed=false
negatome_control_ratio_available=false
negatome_control_ratio=not_computed
gate6_control_readiness_status_after=blocked_pending_control_repair
gate6_control_readiness_resolved_after=false
gate7_entry_allowed_after=false
biological_approval_granted=false
```

No surrogate ratio is invented. This result does not open Gate 7. This result is not biological approval.

This PR performs no automatic Biohub / ESMC call, generates no new embedding,
writes no `.npy`, performs no interface or elephant interface scoring, calls
no Boltz / AF3 / Chai runtime, promotes no Gate 7, Gate 8, or Gate 9 state,
and makes no biological claim.

## Result identity

```text
result_metadata_sha256=e92c045e44db2800fe2cb643bab281d875a1de6e0ce2413a2fed9b23bc3a49c2
```

## Next result-bearing action

```text
repair_local_mapping_and_exact_pair_then_add_first_tp53_mdm2_embedding_based_negatome_control_result
```

The local input repair must not become a separate inventory-only, plan-only,
scaffold-only, runtime-preparation-only, or generic-refactor-only PR.
