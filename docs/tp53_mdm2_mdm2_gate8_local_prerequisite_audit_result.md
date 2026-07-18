# TP53/MDM2 MDM2 Gate 8 local prerequisite audit result

## Purpose

This result is the first panel-level execution-readiness checkpoint after the
MDM2 Gate 7 source panel became multi-species ready.

The committed Gate 7 MDM2 source panel is:

- elephant: `G3SX30`;
- mouse: `P23804`;
- hamster: `A0ABM2YB85`.

Rat remains deferred and is not part of the strict panel. TP53 remains
`deferred_pending_source`.

## Sources

The audit reads the committed source decisions from:

- `data/input/tp53_mdm2_gate7_coverage_repair_resolutions.csv` for elephant;
- `data/input/tp53_mdm2_mdm2_short_lived_control_results.csv` for mouse and
  hamster;
- `data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv` for
  the already accession-bound G3SX30 local artifact result.

The external read-only observation is recorded at:

`D:/biohub_projects/_chatgpt_observations/tp53_mdm2_mdm2_gate8_local_prerequisite_audit.json`

The external JSON and local `.npy` files are not committed.

## Result

The machine-readable result is:

`data/input/tp53_mdm2_mdm2_gate8_local_prerequisite_audit_results.csv`

All rows use model `esmc-300m-2024-12` and the canonical MDM2 embedding path
family:

`data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_<taxid>.npy`

### Elephant — G3SX30

The exact elephant path exists and is already bound to accession `G3SX30` by
the existing one-row local preflight result.

Recorded checks:

- `local_embedding_status=present_valid`;
- `embedding_shape=492x960`;
- `embedding_dtype=float32`;
- `embedding_numeric=true`;
- `embedding_finite=true`;
- `embedding_sequence_length_matches=true`;
- `runtime_blocker_code=none`.

This audit does not create a new elephant approval or readiness transition.

### Mouse — P23804

The exact mouse path is absent.

Recorded outcome:

- `local_embedding_status=missing`;
- `runtime_blocker_code=missing_exact_local_embedding`;
- `local_runtime_embedding_exists=false`.

### Hamster — A0ABM2YB85

The exact hamster path is absent.

Recorded outcome:

- `local_embedding_status=missing`;
- `runtime_blocker_code=missing_exact_local_embedding`;
- `local_runtime_embedding_exists=false`.

## Panel decision

The panel-level result is:

- `panel_valid_accessions=G3SX30`;
- `panel_missing_accessions=P23804|A0ABM2YB85`;
- `panel_local_prerequisites_status=blocked_missing_exact_local_embeddings`;
- `panel_runtime_blocker_code=missing_exact_local_embeddings_for_ready_mdm2_controls`;
- `later_mdm2_dry_run_manifest_allowed=false`;
- `allowed_next_action=prepare_separate_scoped_missing_embedding_fill`.

This does not reverse Gate 7 readiness. MDM2 remains
`strict_panel_ready` with `mdm2_gate7_contrast_dry_run_allowed=true`.
The separate local execution-prerequisite audit remains blocked until exact
local embeddings exist for both ready short-lived controls.

## Boundaries

This audit:

- does not call Biohub or ESMC;
- does not generate or rerun embeddings;
- does not run contrast;
- does not create or commit `.npy` artifacts;
- does not commit `data/output` artifacts;
- does not commit the external observation JSON;
- does not add rat to the strict panel;
- keeps TP53 deferred;
- keeps aggregate Gate 7 entry closed;
- keeps aggregate Gate 8 entry closed;
- keeps Gate 8 and Gate 9 unpromoted;
- does not call Boltz, AF3, or Chai;
- makes no biological claim.

A later PR may prepare a separately scoped missing-embedding fill for
`P23804` and `A0ABM2YB85`. This audit does not authorize that live action.
