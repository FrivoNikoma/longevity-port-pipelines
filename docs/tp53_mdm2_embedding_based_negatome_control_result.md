# TP53/MDM2 embedding-based NEGATOME control result

## Result

```text
result_status=actual_negatome_control_ratio_computed
negatome_control_ratio=1.2482765910897506
runtime_blocker=none
checked_blocker_count=0
```

The existing
`longevity_port_pipelines.stages.negatome_analyze.compute_negatome_control_ratio`
runtime executed successfully.

This is a result-bearing runtime checkpoint, not a preflight-only,
authorization-only, audit-only, scaffold-only, or generic-refactor-only PR.

## G3UAZ0 embedding contract

```text
target=G3UAZ0
sequence_length=364
model=esmc-300m-2024-12
shape=364x960
dtype=float32
finite=true
sha256=3ed7778c8f9d139382c2c8cc5674b287b031a564ab5cc6ff93a5a9a59d120e1e
tracked=false
ignored=true
staged=false
```

The local ignored artifact is
`data/interim/negatome_embeddings/esmc-300m-2024-12/G3UAZ0.npy`.
It is not committed.

## Inputs

```text
human_accession=Q00987
human_shape=491x960
human_embedding_sha256=ee0b8d9025dd6b5a18ecf5f1a344b8ab819f559f652d92f32ea23a006a0d8eeb

elephant_accession=G3SX30
elephant_shape=492x960
elephant_embedding_sha256=98ec10a07986e07c65a11f370f542e5b6c88453c544f9f0f49fb2fe0f8e6315c

mapped_interface_count=47
mapped_indices=24|25|26|27|47|48|49|50|51|52|53|54|55|56|57|58|59|60|61|62|65|66|67|68|69|70|71|72|73|74|81|85|90|91|92|93|94|95|96|97|98|99|100|102|103|106|108
negative_control_lookup_key=tp53_mdm2_elephant_seed_mdm2_chain|mdm2|elephant
```

## Technical interpretation

The control metric is the mean absolute cross-species change in
embedding-coupling to the G3UAZ0 partner pool on mapped interface positions,
divided by the corresponding mean outside the interface.

The value `1.2482765910897506` means that the interface mean is approximately
`24.82765910897506%` above the non-interface mean under this exact technical
metric.

This does not establish binding, non-binding, binding strength, functional
significance, beneficial breakage, adaptation, elephant compatibility,
longevity evidence, or any other biological claim.

## Cross-platform hashes

```text
mapping_canonical_utf8_lf_sha256=73cc5548869e537cd90d78a3cf1a417097f85b9dde99818d8c09f96cce8aa325
mapping_raw_windows_worktree_sha256=aa2aaa053f492e083071830bcbedff0b2d7443e7e779ecc0a87b892fc9b7ec4e
mapping_raw_differs_from_canonical=true

pair_canonical_utf8_lf_sha256=3a97680c46914b468cf1ef1de72bf5da9e51109a31f4d2ba5ee3cdc3af61eb73
pair_raw_windows_worktree_sha256=cdba63779575723026fdc28accba7c820a68e2d8d17903e68787b23cf4041049
pair_raw_differs_from_canonical=true
```

The raw/canonical differences are line-ending byte representation differences;
the canonical contents remain unchanged.

## External evidence

```text
live_report_sha256=063f4c09a628be136c933e82a1e6e62e524b57bf5b072589108f147f93efdde7
live_guard_sha256=a4903c895e55ba537f5495f5072c93ebd88b4fd5389c68f6a64ddc955cf961c9
runtime_commit=c1d8504ebea567e5481b23bac0790900ea347350
live_result_timestamp_utc=2026-07-16T07:06:39.798956+00:00
```

The external JSON files are not committed. Their hashes are recorded in the
tracked result row.

## Gate state

```text
gate6_control_readiness_status_after=blocked_pending_control_result_integration
gate6_control_readiness_resolved_after=false
gate6_control_closure_blocked_after=true
gate7_entry_allowed_after=false
gate8_promoted=false
gate9_promoted=false
```

The runtime blocker is resolved, but this result has not yet been integrated
into the previously committed TP53/MDM2 control-closure decision. The next
result-bearing action is that integration and an explicit Gate 6 decision.

## Boundaries

```text
biohub_esmc_called=true
new_embeddings_generated=1
npy_artifact_written=true
npy_artifact_committed=false
data_output_artifact_committed=false
boltz_called=false
af3_called=false
chai_called=false
biological_claim_made=false
```

No additional live embedding was generated beyond G3UAZ0.

## Result identity

```text
result_metadata_sha256=d253e79b5bb345c66494347cb0858e54672151cf8406c370b97c70480ba19bc8
```
