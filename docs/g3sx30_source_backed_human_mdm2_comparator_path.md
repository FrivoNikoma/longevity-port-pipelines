# G3SX30 source-backed human MDM2 comparator path

This PR creates the first concrete comparator/blocker result for a future
pairwise embedding comparison between elephant MDM2 `G3SX30` and the committed
human MDM2 pilot reference `Q00987`.

It consumes:

- `data/input/tp53_mdm2_pilot_manifest.csv#2`
- `data/input/tp53_mdm2_ortholog_repair_decisions.csv#2`
- `data/input/ortholog_evidence_review_decisions.csv#1`
- `data/input/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv#1`

It creates the repo-visible one-row result:

- `data/input/g3sx30_source_backed_human_mdm2_comparator_paths.csv#1`

This is a result-bearing transition:

```text
source-backed human reference identity + elephant embedding availability
-> explicit human-embedding blocker for the first pairwise summary
```

## Human reference identity result

The row records:

- `human_reference_source_backed = true`
- `human_reference_source_scope = committed_pilot_manifest_reference_identity`
- `human_reference_accession = Q00987`
- `human_reference_species = Homo sapiens`
- `human_reference_taxid = 9606`
- `human_reference_gene_symbol = MDM2`
- `human_reference_pdb_id = 1ycr`
- `human_reference_chain = A`
- `human_reference_partner_uniprot = P04637`

Here, `source_backed` means the reference identity is present in the committed
TP53/MDM2 pilot manifest. This result does not claim reviewed human sequence
provenance, orthology, or functional equivalence with `G3SX30`.

## Elephant target and embedding result

The row traces to the later reviewed-for-planning G3SX30 evidence and the
committed elephant scalar-summary row:

- `elephant_target_accession = G3SX30`
- `elephant_target_database = UniProtKB TrEMBL`
- `elephant_target_species = Loxodonta africana`
- `elephant_target_taxid = 9785`
- `elephant_target_gene_symbol = MDM2`
- `elephant_embedding_available = true`
- `elephant_embedding_shape = 492x960`
- `elephant_embedding_dtype = float32`
- `elephant_embedding_finite = true`

The historical repair row keeps `target_uniprot = unresolved`. This PR preserves
that historical state and uses the later reviewed-for-planning G3SX30 row plus
the later embedding result as the current comparator target sources.

## Concrete blocker result

Exact local runtime filename inspection found no `.npy` with the human MDM2
aliases `Q00987` or `1ycr`.

The committed row records:

- `comparator_status = source_backed_human_mdm2_comparator_path_created`
- `comparator_type = human_elephant_mdm2_reference_identity_comparator_for_pairwise_embedding`
- `comparator_scope = reference_identity_and_embedding_availability_only_no_biological_claim`
- `human_embedding_available = false`
- `elephant_embedding_available = true`
- `pairwise_summary_created = false`
- `pairwise_blocker = source_backed_human_mdm2_embedding_not_available`

Taxid-only `9606` filename matches from unrelated human proteins are not treated
as human MDM2 embeddings.

## Claim policy

This row may state only that the committed human MDM2 pilot reference is
`Q00987`, PDB `1ycr`, chain `A`; the ignored G3SX30 elephant embedding is
available; no exact `Q00987` or `1ycr` local runtime embedding was found; and a
pairwise summary has not been created because the human embedding is absent.

It is not an orthology result, not a functional-equivalence result, not a
biological comparison, not an interface result, not a protein-binding result,
not a beneficial-breakage result, and not longevity evidence.

## Boundary

The row keeps all of the following false:

- `gate8_promoted`
- `gate9_promoted`
- `biological_claim_made`
- `data_output_artifact_committed`
- `biohub_esmc_called_by_comparator_path`
- `live_embedding_rerun_by_comparator_path`
- `embedding_generation_performed_by_comparator_path`
- `npy_artifact_created_by_comparator_path`
- `raw_embedding_values_committed`
- `boltz_called`
- `af3_called`
- `chai_called`
- `enrichment_rerun`
- `contrast_rerun`

No human embedding is generated and no raw embedding vector or `data/output`
artifact is committed.

## Next result-bearing step

The row records:

- `next_step = generate_source_backed_human_mdm2_embedding_and_create_first_pairwise_summary`
- `explicit_runtime_scope_required_for_next_step = true`
- `runtime_scope_must_be_encoded_in_result_bearing_step = true`
- `no_additional_comparator_approval_before_pairwise_result = true`
- `no_additional_comparator_review_before_pairwise_result = true`
- `no_additional_non_result_layer_before_next_concrete_step = true`

The runtime boundary must be encoded inside the next result-bearing step. Do not
insert another comparator approval, review, preparation, scaffold, or decision
layer before a human embedding runtime result or the pairwise summary.
