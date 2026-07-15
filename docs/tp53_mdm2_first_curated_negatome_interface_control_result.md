# First TP53/MDM2 curated NEGATOME interface-control result

## Concrete result

This result reviews one real peer-reviewed manual NEGATOME-style negative
context for human MDM2 `Q00987` and records the concrete outcome

`curated_negatome_record_reviewed_no_computable_interface_control`.

The committed row is
`data/input/tp53_mdm2_first_curated_negatome_interface_control_results.csv#1`.

This is not an inventory, plan, scaffold, or generic refactor. A specific
record was reviewed, its provenance was frozen, and the absence of a
scientifically valid no-embedding MDM2-side metric was recorded as the result.

## Curated negative record

The reviewed primary-research record is Sulak et al., eLife 2016,
DOI `10.7554/eLife.11994`, Figure `10E`.

The reported context uses transiently expressed African-elephant TP53RTG12
(`ENSLAFG00000028299`) in HEK-293 cells. Endogenous human MDM2 was
immunoprecipitated and the readout was Western blotting. Endogenous human TP53
was detected as an internal positive co-immunoprecipitation control, whereas
Myc-tagged TP53RTG12 was not detected in the MDM2 immunoprecipitate.

The record also reports the partner-side TP53 anchor context `F19`, `W23`, and `L26`, including the TP53RTG12 substitution `W23G`. These facts are committed
as provenance and context fields. They are not converted into a binding score
or an invented interface-strength quantity.

Canonical record-metadata SHA256:

`5c9b77284294997ad5067be4a6991a54892bf883f9d91c0e334004d9068089c0`

## Why no interface-control metric is computed

The existing geometric result is an MDM2 chain-`A` mask containing `47` of
`85` observed residues from human `1YCR`.

The curated record supplies a partner-side sequence observation and a negative
co-immunoprecipitation observation, but it does not supply:

- a negative-complex experimental structure;
- a negative-context MDM2 chain;
- an MDM2-side negative residue mask;
- a deterministic MDM2-side sequence context that can be compared with the
  existing `47 / 85` mask.

Therefore:

```text
residue_level_context_available=false
deterministic_sequence_context_available=false
interface_control_metric_computed=false
no_computable_control_reason=curated_record_does_not_define_residue_level_or_deterministic_sequence_context
```

These availability fields are scoped to an MDM2-side negative-interface
context sufficient for the requested comparison. The separately recorded
partner-side `W23G` context does not satisfy that requirement.

The result does not replace the missing metric with conditional interface strength, random overlap, protein length, or arbitrary sequence similarity.
No empirical null or add-one empirical p-value is reported.

## Separation from the existing NEGATOME runtime

The existing NEGATOME path remains valid for an embedding-based NEGATOME
control ratio when reference, ortholog, and negative-partner per-residue
embeddings and `.npy` runtime artifacts are available.

This PR is a result-specific no-embedding curated NEGATOME interface-control
review. The existing runtime path is not reused because it
`requires_embed_sequence_npy_and_per_residue_embeddings`.

The committed row records:

```text
existing_runtime_negatome_path_reused=false
existing_runtime_negatome_path_status=valid_for_embedding_based_negatome_control_ratio
embedding_control_ratio_computed=false
new_embeddings_generated=false
biohub_esmc_called=false
npy_artifact_read=false
npy_artifact_written=false
data_output_artifact_committed=false
```

The existing embedding-based NEGATOME code is not removed, deprecated, or
classified as unnecessary.

## Interpretation boundary

The reviewed observation is a curated negative experimental context. This
checkpoint does not establish binding, non-binding, binding strength,
functional significance, biological specificity, adaptation, elephant
compatibility, beneficial breakage, or longevity evidence. It is not a biological claim.

This PR performs no Biohub / ESMC call, creates no new embeddings, reads or
writes no `.npy` artifact, commits no `data/output` artifact, computes no
embedding-control ratio, calls no Boltz / AF3 / Chai service, and promotes
neither Gate 8 nor Gate 9.

The curated NEGATOME interface control is reviewed but not computationally
closed:

```text
curated_negatome_control_computed=false
curated_negatome_control_closed=false
```

## Next result-bearing action

`add_first_tp53_mdm2_control_closure_result`

The next result must explicitly combine the completed shuffled-control result
with this reviewed no-computable NEGATOME outcome and record whether Gate 6
control closure remains blocked. No inventory-only, plan-only, scaffold-only,
approval-only, review-only, runtime-preparation-only, or generic-refactor-only
PR should precede that concrete control-closure result.
