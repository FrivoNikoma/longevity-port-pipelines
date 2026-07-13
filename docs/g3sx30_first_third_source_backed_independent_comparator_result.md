# First third source-backed independent comparator result

## Purpose

This checkpoint records the third independently selected numerical whole-protein
embedding-space comparator for human MDM2 `Q00987` and elephant MDM2 `G3SX30`.

The external calculation was result-bearing:

```text
selection_rule_sha256=aab50c4dcbd198f2ccd7525f29616071cd93b0ba2cbc6c735104e30990e59042
selection_rule_frozen_before_similarity=true
similarity_used_for_selection=false
selection_and_result_in_same_step=true
```

It is not an inventory-only, plan-only, approval-only, review-only,
runtime-preparation-only, or scaffold-only checkpoint.

## Source checkpoint

The result validates:

```text
data/input/g3sx30_first_two_comparator_pairwise_embedding_control_summaries.csv#1
```

The source summary records the human-elephant MDM2 baseline and the first two
comparator pairs, and requires this third result-bearing comparator step.

## Inventory continuity

The selector recalculated the local same-model inventory before selection:

```text
historical_inventory_file_count=216
current_inventory_file_count=216
inventory_file_count_delta=0
added_inventory_path_count=0
removed_inventory_path_count=0
inventory_universe_sha256=30ddb570feda2438c7c1864d466f43521ce8ab03ce1561f91f75f3cab78a8022
source_backed_eligible_candidate_count=94
```

The first two comparator artifacts and their complex contexts were excluded.
All eligible candidates had to be local ignored, untracked, unstaged,
two-dimensional finite `float32` ESMC arrays with embedding dimension `960`.

## Frozen selection

The rank-1 selected artifact was:

```text
data/output/embeddings/esmc-300m-2024-12/7s68__D1_P09874--7s68__C1_P09874_ligand_9606.npy
```

Technical state:

```text
shape=211x960
dtype=float32
finite=true
ignored=true
tracked=false
staged=false
committed=false
pdb_token=7s68
accession_tokens=P09874
taxid=9606
reference_tier=3
```

The selection freeze JSON was written and verified before cosine calculation:

```text
selection_freeze_json_sha256=d6b3ccb2f621dbac7d5723eef9fa126ac141815fea2ddb49f741869f06b36a8e
```

The external final result JSON had SHA256:

```text
82fc8b408d815816dc5834e3d2e79de0d3f83699bb481d0b4a061b754873c043
```

Both JSON files remain outside the repository.

## Provenance boundary

The selector mechanically assigned tier 3 because `P09874` and taxid `9606`
co-occurred in committed files. The post-selection review then found `26` exact tracked references to the complex:

```text
7s68__D1_P09874--7s68__C1_P09874
```

Repository-visible supplemental evidence records `7s68` as a selected
PARP1/PARP1 context:

```text
source accession=P09874
partner accession=P09874
intermolecular contacts=50
context status=v1_selected
```

The supplemental files are:

```text
docs/sirt6_mini_pilot_v2_candidate_selection.md
docs/parp1_negatome_evidence_notes.md
```

This confirms a narrow complex/role/accession/taxid context. It does **not**
confirm the exact sequence-to-embedding byte chain:

```text
exact_artifact_path_reference_found=false
exact_artifact_basename_reference_found=false
complex_role_accession_taxid_context_confirmed=true
exact_embedding_byte_provenance_confirmed=false
exact_sequence_hash_provenance_confirmed=false
```

The mechanical tier-3 files are retained as selection-time evidence, but they
must not be described as exact `7s68` artifact provenance.

## Numerical result

The three arrays were independently mean-pooled over their residue axes in
`float64`. No residue alignment was performed.

```text
human-elephant MDM2 baseline=0.9973314302339468

human MDM2 to third comparator=0.7472839682873271
elephant MDM2 to third comparator=0.7516055327169140
```

Deltas from the baseline:

```text
baseline minus human third control=0.2500474619466196
baseline minus elephant third control=0.2457258975170328
```

Matched-anchor difference:

```text
human third control minus elephant third control=-0.0043215644295869
absolute human-elephant third control difference=0.0043215644295869
```

Mean-vector norms:

```text
human MDM2=0.8317611517806081
elephant MDM2=0.8347860929210978
third comparator=0.8067238204277115
```

## Interpretation boundary

The third comparator similarities are lower than both earlier comparator pairs.
The same anchor ordering remains present: the elephant-MDM2 similarity is
slightly greater than the human-MDM2 similarity. The absolute anchor difference
is smaller than for either earlier comparator.

This is useful for a later three-comparator calibration summary. It does not
show biological specificity. Three whole-protein comparators are not a
validated biological negative-control panel and do not replace
interface-versus-background analysis.

Explicitly, this result is:

- not a validated biological negative control;
- not evidence of biological specificity;
- not exact embedding-byte provenance;
- not exact sequence-hash provenance;
- not residue alignment;
- not interface analysis;
- not a binding result;
- not orthology proof;
- not functional-equivalence evidence;
- not longevity evidence;
- not a biological claim.

## Runtime and artifact boundary

This checkpoint does not:

- call Biohub or ESMC;
- generate a new embedding;
- commit `.npy` arrays or raw embedding vectors;
- commit a `data/output` artifact;
- commit either external JSON;
- call Boltz, AF3, or Chai;
- rerun enrichment or contrast;
- promote Gate 8 or Gate 9;
- make a biological claim.

## Repository-visible result

This checkpoint adds:

- a machine-readable schema;
- a one-row committed numerical result table;
- a validator and local reproducer;
- focused result and documentation tests;
- this result document;
- a current gate-map checkpoint.

## Next result-bearing step

```text
add_first_three_comparator_pairwise_embedding_control_summary_before_interface_manifest
```

That summary should aggregate the baseline and all six MDM2-to-comparator
similarities, quantify the lower third-comparator values, test ordering
consistency across all three comparators, and close whole-protein comparator
calibration before the TP53/MDM2 interface-ready manifest.

No inventory-only, control-plan-only, approval, review, runtime-preparation,
scaffold, or other non-result PR should be inserted before that summary.
