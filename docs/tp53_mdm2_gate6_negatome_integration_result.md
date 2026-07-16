# TP53/MDM2 Gate 6 NEGATOME result integration

## Integration question

Does the actual embedding-based NEGATOME control result complete the repair
required by the existing TP53/MDM2 Gate 6 blocker disposition?

## Result

Yes. The required repair is complete:

```text
integration_status=actual_negatome_result_integrated_gate6_readiness_resolved
required_embedding_control_repair_completed=true
generic_control_repair_status_after=completed
```

The integrated actual result is:

```text
source_actual_negatome_result_status=actual_negatome_control_ratio_computed
negatome_control_ratio=1.2482765910897506
negatome_runtime_blocker=none
```

## Gate 6 decision

Gate 6 is treated here as a control-evidence readiness gate. The defined
control layers are now present and the explicitly required embedding-based
repair has been completed.

```text
generic_control_readiness_status_after=ready
gate6_control_readiness_status_after=ready
gate6_control_readiness_resolved_after=true
gate6_control_closure_blocked_after=false
```

This resolves the previous Gate 6 control-readiness blocker. It does not mean
that the candidate passed a biological validation gate.

## Why no controlled pass or fail is recorded

The previously committed shuffled control is geometric:

```text
metric_family=sequence_adjacency_contiguous_runs_and_longest_run
n_permutations=1000
true_adjacent_pair_count=38
shuffled_adjacent_pair_count_mean=25.4239999999999995
adjacent_pair_empirical_upper_p_add_one=0.0009990009990010
```

It measures sequence compactness of the human `1YCR` MDM2 geometric contact
mask relative to random same-size masks.

The actual NEGATOME value `1.2482765910897506` is instead an embedding-based
interface-to-non-interface ratio of absolute cross-species coupling changes
to the G3UAZ0 partner pool.

These are different metric families:

```text
metric_families_directly_comparable=false
numerical_controlled_pass_fail_evaluated=false
controlled_pass=false
controlled_fail=false
```

The integration therefore records evidence availability and repair
completion, not a numerical comparison between unrelated quantities.

## Gate 7 and downstream state

Gate 7 is not opened automatically:

```text
gate7_entry_allowed_after=false
gate7_strict_panel_promoted=false
gate7_blocker_reason=explicit_gate7_strict_panel_entry_decision_required_after_gate6_readiness
gate8_entry_allowed=false
gate8_promoted=false
gate9_promoted=false
biological_approval_granted=false
```

The next result-bearing action is an explicit TP53/MDM2 Gate 7 strict-panel
entry decision.

## Source identities

```text
control_closure_evidence_sha256=57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7
blocker_disposition_metadata_sha256=1ef15df255929ca89e248fabec6eba6456d89a972b230389dd7135f24b13b4e4
actual_negatome_result_metadata_sha256=d253e79b5bb345c66494347cb0858e54672151cf8406c370b97c70480ba19bc8
actual_negatome_result_table_canonical_sha256=a7f733b00a4ffa1415bbc6c66193c515f9bdf37d022a174f7be7bc8bade4d184
geometric_shuffled_control_table_canonical_sha256=c2b36006abadd1d53017be824738b68567e2b98382ded8c7b07f7a220de553e3
```

## Runtime and artifact boundaries

This integration reads committed CSV rows only.

```text
evidence_recomputed=false
interface_scoring_performed=false
comparative_elephant_interface_scoring_performed=false
new_embeddings_generated_by_integration=false
biohub_esmc_called_by_integration=false
npy_artifact_read_by_integration=false
npy_artifact_written_by_integration=false
npy_artifact_committed=false
data_output_artifact_committed=false
boltz_called=false
af3_called=false
chai_called=false
biological_claim_made=false
```

No binding, non-binding, binding-strength, functional-significance,
biological-specificity, adaptation, elephant-compatibility,
beneficial-breakage, or longevity claim is made.

## Integration identity

```text
integration_metadata_sha256=d121b1fbcc28116c26bebe7db9e34cc6722a183d069c5bc51310b32d112b8341
```
