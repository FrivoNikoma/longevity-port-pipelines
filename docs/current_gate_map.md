# Current LongevityPort gate map

This document tracks the current state of the LongevityPort gated decision
pipeline. It is intentionally conservative. A gate can be useful even when it
blocks a candidate, because blocked rows become an explicit repair, exclude, or
defer worklist.

## Gate summary

| Gate | Purpose | Current status |
| --- | --- | --- |
| Gate 0 - candidate sets configured | Candidate modules exist with biological modes. | Done for current configured lanes. SIRT6, TP53/MDM2, HAS2/CD44, IGF/RHEB/mTOR, and AMPK are represented as candidate sets. |
| Gate 1 - candidate lane contract | Define what every biological lane must provide. | Partly done / implemented as architecture docs and lane manifest constraints; continue extending as new lanes are added. |
| Gate 2 - lane registry | Register all lanes in one machine-readable format. | Done for current configured lanes. `data/config/candidate_lanes.yaml` records SIRT6, TP53/MDM2, HAS2/CD44, IGF/RHEB/mTOR, and AMPK. |
| Gate 3 - manifest | Explicit candidate rows exist for a lane. | Done for SIRT6; started for TP53/MDM2; pending for HAS2/CD44, IGF/RHEB/mTOR, and AMPK in the new architecture. |
| Gate 4 - coverage/provenance | Ortholog and local downstream evidence are explicit. | Advanced for SIRT6 and started for TP53/MDM2; both calibration lanes now expose generic coverage-helper traces. |
| Gate 5 - repair decisions | Coverage/provenance blockers are classified as repair/exclude/defer. | Advanced for SIRT6 and started for TP53/MDM2; repair decisions are now mapped into generic repair statuses in the calibration lane traces. |
| Gate 6 - control readiness | Shuffled and NEGATOME/control status are explicit. | Advanced for SIRT6; generic schema and helper now exist, and the candidate contrast gate records generic control-helper traces. Fully generic control outputs across all lanes are still pending. |
| Gate 7 - strict panel / contrast gate | Decide whether a candidate may enter technical contrast. | Advanced for SIRT6; SIRT6 summary records generic strict panel helper trace, the generic strict panel runtime builder exists, and TP53/MDM2 preflight now emits a generic strict panel summary while remaining blocked by coverage. |
| Gate 8 - long-lived vs short-lived contrast | Compute technical contrast under gate policy. | Implemented as a SIRT6 technical checkpoint; generic Gate 8 gated contrast schema, helper, runtime calculator, robustness annotations, SIRT6 generic input bridge, and SIRT6 generic dry-run wrapper now exist; TP53/MDM2 now emits a generic Gate 8 blocked summary while coverage remains unresolved. |
| Gate 9 - cofolding readiness | Produce contrast-gated cofolding planning rows. | Implemented for SIRT6 planning; generic Gate 9 cofolding readiness schema, helper, and runtime checklist now exist; generic dry-run manifest builder now exists; SIRT6 Gate 9 context builder and dry-run path are now recorded; TP53/MDM2 Gate 9 blocked context builder and blocked dry-run path are now recorded; additional lane context builders pending. |
| Gate 10 - live structural compatibility | Submit live structural calls only after explicit opt-in and review. | Not part of default pipeline. Must remain opt-in. |
| Gate 11 - decision package | Summarize candidate status, allowed claims, forbidden claims, and next action. | Not done. |
| Gate 12 - additional biological lanes | Add HAS2/CD44, IGF/RHEB/mTOR, AMPK, and future modules with real biological data. | Pending. |

## Current interpretation

The project has moved from a SIRT6-only coverage-repair phase into a multi-lane
gate architecture phase. After the Gate 8/Gate 9 calibration checkpoint, SIRT6 has a recorded dry-run path and TP53/MDM2 has a recorded blocked dry-run path.

- the Gate 8/Gate 9 calibration-lane roadmap checkpoint is recorded

Current calibration lanes:

- SIRT6/core3:
  - first calibration lane
  - most advanced gate stack
  - legacy technical contrast checkpoint exists
  - generic Gate 8 input bridge exists
  - generic Gate 8 dry-run wrapper exists
  - generic coverage-helper trace is recorded in the strict panel layer
  - not a validated biological claim
- TP53/MDM2 elephant:
  - second calibration lane
  - useful because `biological_mode = beneficial_breakage`
  - generic coverage-helper trace is recorded in the coverage preflight layer
  - generic strict panel builder emits a blocked Gate 7 summary
  - not yet at SIRT6-level gate maturity
  - emits a generic Gate 8 blocked summary while coverage remains unresolved
  - emits a generic Gate 9 blocked context while coverage remains unresolved
  - records a generic Gate 9 blocked dry-run path with empty eligible manifest expectation
  - not a validated biological claim

Current generic adoption checkpoint:

- the generic candidate lane registry exists for the current configured lanes
- the generic coverage preflight helper exists
- TP53/MDM2 uses the generic coverage helper
- SIRT6 uses the generic coverage helper
- the generic control readiness schema exists
- the generic control readiness helper exists
- the candidate contrast gate records generic control-helper traces
- the generic strict contrast panel schema exists
- the generic strict contrast panel helper exists
- the SIRT6 strict panel summary records generic strict panel helper trace
- the generic strict panel runtime builder exists
- TP53/MDM2 uses the generic strict panel builder
- the generic gated contrast schema exists
- the generic gated contrast helper exists
- the generic gated contrast runtime calculator exists
- the generic gated contrast runtime records contrast robustness annotations
- SIRT6 generic gated contrast input bridge exists
- SIRT6 generic gated contrast dry-run wrapper exists
- TP53/MDM2 emits a generic Gate 8 blocked summary while coverage remains unresolved
- TP53/MDM2 emits a generic Gate 9 blocked context while coverage remains unresolved
- TP53/MDM2 Gate 9 blocked dry-run path is recorded
- the generic cofolding readiness schema exists
- the generic cofolding readiness helper exists
- the generic cofolding readiness runtime checklist exists
- the generic cofolding dry-run manifest builder exists
- the SIRT6 Gate 9 cofolding context builder exists
- the SIRT6 Gate 9 dry-run path is recorded
- the next major frontier is wiring the generic gated contrast runtime into additional calibration lanes beyond SIRT6

Planned lanes:

- HAS2/CD44:
  - transferable_function lane
  - requires extracellular matrix and hyaluronan caveats
- IGF/RHEB/mTOR:
  - signaling_rewiring lane
  - requires hub-risk and network interpretation
- AMPK:
  - signaling_rewiring lane
  - useful for checking that the generic contract handles earlier pilot data

## Claim policy

Allowed language at the current stage:

- technical checkpoint
- coverage-aware planning
- dry-run gate
- repair worklist
- contrast readiness
- cofolding readiness

Disallowed language unless later validation closes the appropriate gates:

- validated longevity signal
- validated biological hit
- confirmed binding change
- confirmed functional effect
- safe to port
- proven pro-longevity variant

## Boltz policy

Boltz is a downstream compatibility classifier. It should not be used as a
discovery shortcut.

Live Boltz calls require:

- explicit candidate id
- explicit species / partner context
- dry-run input review
- opt-in live flag
- small num_samples by default
- recorded claim policy
- no committed signed structure URLs
- no biological overclaiming

## How to use this file after each PR

After every PR, update the relevant gate row if the PR changes project state.

Each PR description should answer:

- Which gate did this PR close or clarify?
- Which lane does it affect?
- Does it introduce data, code, docs, or runtime outputs?
- Does it allow any new claim?
- What remains blocked?

## Gate-aware embedding fill checkpoint

The gate-aware embedding fill plan is now recorded in `docs/gate_aware_embedding_fill_plan.md`.

This is a planning checkpoint only. It does not call Biohub, generate embeddings, submit Boltz jobs, or make biological claims.

## Controlled embedding fill protocol checkpoint

The controlled embedding fill protocol is now recorded in `docs/controlled_embedding_fill_protocol.md`.

This is a governance checkpoint only. It formalizes the Brandt's bat `P09874` precedent and requires `curated_embedding_preflight`, `curated_embedding_single` dry-run evidence, `sequence_length_status == matches`, explicit `--yes-live` approval for live calls, local `.npy` validation, no committed `data/output/` artifacts, no enrichment/contrast rerun by default, no Boltz calls, and no biological claims.

## Controlled embedding fill worklist schema checkpoint

The controlled embedding fill worklist schema is now recorded in `data/config/controlled_embedding_fill_worklist_schema.yaml`.

This is a schema checkpoint only. It defines machine-readable fill statuses, including `planning_policy_updated_runtime_blocked`, required worklist fields, single-row live-fill guardrails, `--yes-live` opt-in requirements, `sequence_length_status == matches`, no sequence fetch, no committed `data/output/` artifacts, no Biohub calls from schema checks, no Gate 8 or Gate 9 promotion, no Boltz/AF3/Chai calls, no enrichment/contrast rerun, and no biological claims.

## Controlled embedding fill worklist builder checkpoint

The controlled embedding fill worklist builder is now recorded in `src/longevity_port_pipelines/stages/controlled_embedding_fill_worklist.py`.

This is a table-only dry-run worklist builder. It consumes curated embedding preflight rows and emits controlled fill statuses under `data/config/controlled_embedding_fill_worklist_schema.yaml`. The builder can represent `planning_policy_updated_runtime_blocked` as a safe blocked vocabulary status, but it does not infer that status from ordinary preflight rows without explicit policy context. It does not fetch sequences, does not call Biohub, does not generate embeddings, does not commit `data/output/` artifacts, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment/contrast, and does not make biological claims.

## Brandt's bat P09874 controlled fill no-op checkpoint

The first controlled embedding fill worklist checkpoint is recorded in `data/interim/controlled_embedding_fill_worklist_brandts_bat_p09874_checkpoint.csv`.

This is a no-op table-only checkpoint. The Brandt's bat `P09874` embedding is already present, so the controlled fill worklist assigns `fill_status: do_not_fill` and `allowed_next_action: do_not_fill`. It does not call Biohub, does not generate embeddings, does not commit `data/output/` artifacts, does not call Boltz, does not rerun enrichment/contrast, and does not make biological claims.

## G3SX30 blocked controlled embedding-fill worklist checkpoint

The first G3SX30 blocked controlled embedding-fill worklist checkpoint is recorded in `data/interim/controlled_embedding_fill_worklist_g3sx30_blocked_checkpoint.csv`.

This is a one-row table-only blocked checkpoint sourced from `data/input/ortholog_evidence_gate45_policy_updates.csv#1`. It records `target_accession=G3SX30`, `target_sequence_length=492`, `sequence_length_status=not_fetched`, `embedding_path=not_applicable_runtime_blocked`, `fill_status: planning_policy_updated_runtime_blocked`, `allowed_next_action: keep_blocked`, `dry_run_required: false`, and `max_live_batch_size: 0`.

This checkpoint does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not fetch sequences, does not call Biohub / ESMC, does not generate embeddings, does not create or commit `.npy` artifacts, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.

## G3SX30 blocked embedding-fill exit criteria checkpoint

The G3SX30 blocked embedding-fill exit criteria are recorded in `docs/g3sx30_blocked_embedding_fill_exit_criteria.md`.

This is a docs-only review protocol for a later possible dry-run preflight decision. It does not change the G3SX30 worklist row, does not make G3SX30 preflight-ready, does not fetch sequences, does not call Biohub / ESMC, does not generate embeddings, does not create or commit `.npy` artifacts, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, and does not make biological claims.

## Reviewed target sequence provenance scaffold checkpoint

The reviewed target sequence provenance scaffold is now recorded in `data/config/reviewed_target_sequence_provenance_schema.yaml`, `data/input/reviewed_target_sequence_provenance.csv`, and `src/longevity_port_pipelines/stages/reviewed_target_sequence_provenance.py`.

This is a header-only reviewed target sequence provenance table plus table-only helper/validator. It does not add a G3SX30 sequence row, does not fetch sequences, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not create or commit `.npy` artifacts, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.

## G3SX30 deferred target sequence provenance row checkpoint

The first G3SX30 target sequence provenance row is recorded in `data/input/reviewed_target_sequence_provenance.csv`.

This is a deferred pending-review row only: `sequence_source_type=deferred_pending_review`, `sequence_length_status=not_fetched`, `sequence_review_status=deferred_pending_review`, `provenance_review_status=deferred`, and `allowed_next_action_after_sequence_review=defer_pending_sequence_review`.

It does not record reviewed sequence provenance, does not record `sequence_length_status=matches`, does not fetch sequences, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not change the G3SX30 controlled embedding-fill worklist row, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 target sequence review checklist checkpoint

The G3SX30 target sequence review checklist is recorded in `docs/g3sx30_target_sequence_review_checklist.md`.

This checklist documents the human-review requirements that must be satisfied before any later PR can consider moving the G3SX30 target sequence provenance row from `deferred_pending_review` to `reviewed_sequence_provenance`.

It requires traceability to `data/input/ortholog_evidence_gate45_policy_updates.csv#1`, identity checks for accession `G3SX30`, database `UniProtKB TrEMBL`, species `Loxodonta africana`, taxid `9785`, and gene symbol `MDM2`, explicit reviewed sequence artifact/hash checks, direct reviewed length checking against expected metadata length `492`, mismatch handling, and a separate later dry-run preflight decision.

It does not fetch sequences, does not add reviewed sequence provenance, does not record `sequence_length_status=matches`, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not change the G3SX30 controlled embedding-fill worklist row, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## Target sequence review decision scaffold checkpoint

The target sequence review decision scaffold is recorded in `data/config/target_sequence_review_decision_schema.yaml`, `data/input/target_sequence_review_decisions.csv`, and `src/longevity_port_pipelines/stages/target_sequence_review_decisions.py`.

This is a header-only decision scaffold for future human sequence review decisions. It adds no G3SX30 decision row and does not mutate the existing G3SX30 target sequence provenance row.

The scaffold defines future decision labels for `approve_reviewed_sequence_provenance_for_planning`, `defer_pending_sequence_review`, `reject_sequence_provenance`, and `keep_blocked_after_mismatch`. Even the approval path remains `sequence_reviewed_still_preflight_decision_blocked` and can only point to a separate later dry-run preflight decision PR.

It does not fetch sequences, does not add reviewed sequence provenance, does not record `sequence_length_status=matches`, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not mark ready_for_preflight, does not change the G3SX30 controlled embedding-fill worklist row, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 deferred target sequence review decision row checkpoint

The first G3SX30 target sequence review decision row is recorded in `data/input/target_sequence_review_decisions.csv`.

This is a deferred decision row only: `sequence_review_decision=defer_pending_sequence_review`, `sequence_length_status_after_decision=not_fetched`, `provenance_review_status_after_decision=deferred`, `decision_status=deferred_pending_review`, `downstream_block_status_after_decision=sequence_review_deferred_still_blocked`, and `allowed_next_action_after_decision=defer_pending_sequence_review`.

It does not approve reviewed sequence provenance, does not record `sequence_length_status_after_decision=matches`, does not mutate the source sequence provenance row, does not fetch sequences, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not change the G3SX30 controlled embedding-fill worklist row, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 official sequence source review preparation checkpoint

`docs/g3sx30_official_sequence_source_review_preparation.md` records a review-preparation checkpoint for a later possible G3SX30 reviewed target sequence provenance PR.

The checkpoint requires future official source record review for accession `G3SX30`, database `UniProtKB TrEMBL`, species `Loxodonta africana`, taxid `9785`, gene symbol `MDM2`, expected metadata length `492`, explicit sequence source traceability, stable `reviewed_sequence_sha256`, direct reviewed amino-acid sequence length calculation, direct length comparison, and explicit mismatch handling.

This checkpoint does not perform the review, does not fetch sequences inside the repository, does not commit a raw sequence artifact, does not mutate `data/input/reviewed_target_sequence_provenance.csv`, does not mutate `data/input/target_sequence_review_decisions.csv`, does not approve reviewed sequence provenance, does not record `sequence_length_status=matches`, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not change the G3SX30 controlled embedding-fill worklist row, does not mark anything `ready_for_preflight`, does not create or commit `.npy` artifacts, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 reviewed target sequence provenance row checkpoint

`data/input/reviewed_target_sequence_provenance.csv` now records one deferred G3SX30 provenance row plus one reviewed official UniProt sequence provenance row.

The reviewed row records `sequence_source_type=reviewed_external_database_record`, `sequence_source_reference=https://rest.uniprot.org/uniprotkb/G3SX30.fasta`, `reviewed_sequence_length=492`, `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, `sequence_length_status=matches`, `sequence_review_status=reviewed_sequence_provenance`, `provenance_review_status=reviewed`, and `allowed_next_action_after_sequence_review=consider_later_dry_run_preflight_decision_pr`.

The reviewed row is based on the manual official-source review package stored outside the repo. The committed row records the official UniProt FASTA source reference and metadata source reference, but does not commit the raw FASTA amino-acid sequence artifact.

This is reviewed sequence provenance for planning only. It does not mutate `data/input/target_sequence_review_decisions.csv`, does not mark anything `ready_for_preflight`, does not fetch sequences inside the repository, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not create or commit `.npy` artifacts, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 reviewed target sequence approval decision row checkpoint

`data/input/target_sequence_review_decisions.csv` now preserves one deferred G3SX30 decision row and adds one reviewed G3SX30 target sequence approval decision row.

The approval decision row references `data/input/reviewed_target_sequence_provenance.csv#2` and records `sequence_review_decision=approve_reviewed_sequence_provenance_for_planning`, `sequence_length_status_after_decision=matches`, `provenance_review_status_after_decision=reviewed`, `reviewed_sequence_length=492`, `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, `decision_status=reviewed_for_planning_still_preflight_blocked`, `downstream_block_status_after_decision=sequence_reviewed_still_preflight_decision_blocked`, and `allowed_next_action_after_decision=consider_later_dry_run_preflight_decision_pr`.

This is a planning-only approval decision. It does not mutate `data/input/reviewed_target_sequence_provenance.csv`, does not mark anything `ready_for_preflight`, does not fetch sequences inside the repository, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not create or commit `.npy` artifacts, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 dry-run preflight decision scaffold checkpoint

This checkpoint adds a header-only dry-run preflight decision scaffold for G3SX30.

The source row is `data/input/target_sequence_review_decisions.csv#2`, which records `sequence_review_decision=approve_reviewed_sequence_provenance_for_planning`, `sequence_length_status_after_decision=matches`, `provenance_review_status_after_decision=reviewed`, `reviewed_sequence_length=492`, `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, `decision_status=reviewed_for_planning_still_preflight_blocked`, and `allowed_next_action_after_decision=consider_later_dry_run_preflight_decision_pr`.

The new scaffold consists of `data/config/g3sx30_dry_run_preflight_decision_schema.yaml`, header-only `data/input/g3sx30_dry_run_preflight_decisions.csv`, and `src/longevity_port_pipelines/stages/g3sx30_dry_run_preflight_decisions.py`.

This scaffold adds no committed G3SX30 dry-run preflight decision row. It does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create or commit `.npy` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## First G3SX30 dry-run preflight decision row checkpoint

`data/input/g3sx30_dry_run_preflight_decisions.csv` now contains one G3SX30 dry-run preflight decision row.

The row references `data/input/target_sequence_review_decisions.csv#2` and records `dry_run_preflight_decision=approve_dry_run_preflight_for_planning`, `dry_run_preflight_status_after_decision=dry_run_preflight_planning_approved_runtime_blocked`, `allowed_next_action_after_decision=prepare_later_dry_run_preflight_manifest_pr`, `max_live_batch_size_after_decision=0`, `ready_for_preflight_after_decision=false`, `reviewed_sequence_length=492`, and `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`.

This is a planning-only dry-run preflight decision row. It authorizes only preparation of a later dry-run preflight manifest PR. It does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create or commit `.npy` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 dry-run preflight manifest scaffold checkpoint

This checkpoint adds a header-only dry-run preflight manifest scaffold for G3SX30.

The source row is `data/input/g3sx30_dry_run_preflight_decisions.csv#1`, which records `dry_run_preflight_decision=approve_dry_run_preflight_for_planning`, `dry_run_preflight_status_after_decision=dry_run_preflight_planning_approved_runtime_blocked`, `allowed_next_action_after_decision=prepare_later_dry_run_preflight_manifest_pr`, `max_live_batch_size_after_decision=0`, `ready_for_preflight_after_decision=false`, `reviewed_sequence_length=492`, and `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`.

The new scaffold consists of `data/config/g3sx30_dry_run_preflight_manifest_schema.yaml`, header-only `data/input/g3sx30_dry_run_preflight_manifest.csv`, and `src/longevity_port_pipelines/stages/g3sx30_dry_run_preflight_manifest.py`.

This scaffold adds no committed G3SX30 dry-run preflight manifest entry. It does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create or commit `.npy` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## First G3SX30 dry-run preflight manifest row checkpoint

`data/input/g3sx30_dry_run_preflight_manifest.csv` now contains one G3SX30 dry-run preflight manifest row.

The row references `data/input/g3sx30_dry_run_preflight_decisions.csv#1` and records `manifest_entry_status=manifest_scaffold_ready_runtime_blocked`, `dry_run_only=true`, `max_live_batch_size=0`, `ready_for_preflight_after_manifest=false`, `sequence_fetch_allowed=false`, `biohub_call_allowed=false`, `esmc_call_allowed=false`, `embedding_generation_allowed=false`, `curated_embedding_preflight_allowed=false`, `curated_embedding_single_allowed=false`, `reviewed_sequence_length=492`, and `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`.

This is a planning-only dry-run preflight manifest row. It does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create or commit `.npy` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 dry-run preflight execution checklist checkpoint

`docs/g3sx30_dry_run_preflight_execution_checklist.md` records a docs-only checklist for a later G3SX30 dry-run preflight execution PR.

The checklist source is `data/input/g3sx30_dry_run_preflight_manifest.csv#1`, which records `manifest_entry_status=manifest_scaffold_ready_runtime_blocked`, `dry_run_only=true`, `max_live_batch_size=0`, `ready_for_preflight_after_manifest=false`, `sequence_fetch_allowed=false`, `biohub_call_allowed=false`, `esmc_call_allowed=false`, `embedding_generation_allowed=false`, `curated_embedding_preflight_allowed=false`, `curated_embedding_single_allowed=false`, `reviewed_sequence_length=492`, and `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`.

This checklist adds only future dry-run command templating, pre-run checks, post-run checks, forbidden artifacts, allowed language, and disallowed language. It does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, and does not make biological claims.


## G3SX30 dry-run preflight command discovery note checkpoint

`docs/g3sx30_dry_run_preflight_command_discovery_note.md` records a docs-only command discovery note for a later G3SX30 dry-run preflight execution PR.

The note sources `docs/g3sx30_dry_run_preflight_execution_checklist.md`, which points to `data/input/g3sx30_dry_run_preflight_manifest.csv#1`. It records that `pyproject.toml` exposes the relevant script names `curated-embedding-preflight` and `curated-embedding-single`, but this PR does not execute either script.

The note lists non-executed help commands, required help-output checks, required repository-search checks, no-run proof for this PR, stop conditions for any later execution PR, allowed language, and disallowed language. It does not run `curated-embedding-preflight`, does not run `curated_embedding_preflight`, does not run `curated-embedding-single`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, and does not make biological claims.


## G3SX30 dry-run preflight CLI compatibility checkpoint

`docs/g3sx30_dry_run_preflight_cli_compatibility_note.md` records a docs-only compatibility note comparing the G3SX30 dry-run preflight checklist and command discovery expectations against the actual current CLI implementation.

The note sources `docs/g3sx30_dry_run_preflight_execution_checklist.md`, `docs/g3sx30_dry_run_preflight_command_discovery_note.md`, `pyproject.toml`, `src/longevity_port_pipelines/stages/curated_embedding_preflight.py`, and `src/longevity_port_pipelines/stages/curated_embedding_single.py`.

The compatibility verdict is that current CLI behavior does not match the G3SX30 dry-run preflight checklist expectations closely enough for direct execution: `curated-embedding-preflight` is dry-run-only by implementation but is not manifest-aware, has no explicit `--dry-run`, no `--no-live-call`, no `--max-live-batch-size 0`, no `--no-output-artifacts`, and writes `data/output/curated_ortholog_embedding_preflight.csv` by default; `curated-embedding-single` is dry-run by default but can call Biohub / ESMC if `--yes-live` is passed and is also not manifest-aware.

The note records that a future execution PR should not directly use the current `curated-embedding-preflight` default behavior against G3SX30 unless the manifest mismatch and output-path issue are resolved. It recommends either a manifest-aware dry-run adapter/wrapper scaffold, a tiny source-level guardrail before execution, or stopping while G3SX30 remains runtime-blocked.

This compatibility note does not run `curated-embedding-preflight`, does not run `curated_embedding_preflight`, does not run `curated-embedding-single`, does not run `curated_embedding_single`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 manifest-aware dry-run preflight adapter scaffold checkpoint

`src/longevity_port_pipelines/stages/g3sx30_manifest_aware_dry_run_preflight_adapter.py` adds a helper-only manifest-aware dry-run preflight adapter scaffold. The scaffold reads `data/input/g3sx30_dry_run_preflight_manifest.csv#1`, validates that the G3SX30 manifest row still has `dry_run_only=true`, `max_live_batch_size=0`, `ready_for_preflight_after_manifest=false`, all runtime permission flags false, reviewed sequence length `492`, reviewed sequence SHA256 `e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, and `claim_status=technical_checkpoint`, then returns a table-only adapter status.

The checked-in scaffold row is `data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1`; the schema is `data/config/g3sx30_manifest_aware_dry_run_preflight_adapter_schema.yaml`. The adapter status is `manifest_understood_runtime_blocked`, the adapter decision is `do_not_execute_current_cli_directly`, the current CLI compatibility status is `not_directly_executable_manifest_mismatch_output_path_issue`, the required next action is `add_manifest_aware_wrapper_or_guardrail_before_execution`, and the output path policy is `do_not_write_committed_data_output`.

This scaffold does not add a `pyproject.toml` script entry point, does not run `curated-embedding-preflight`, does not run `curated_embedding_preflight`, does not run `curated-embedding-single`, does not run `curated_embedding_single`, does not run `--help`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 manifest-aware adapter policy contract checkpoint

`src/longevity_port_pipelines/stages/g3sx30_manifest_aware_adapter_policy_contract.py` adds a machine-readable transition policy contract after the G3SX30 manifest-aware adapter scaffold. The policy contract sources `data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1` and keeps the old adapter scaffold row unchanged.

The concrete policy row is `data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1`. It records `policy_status=adapter_policy_runtime_blocked`, `policy_decision=require_manifest_aware_wrapper_before_execution`, `current_cli_direct_execution_decision=reject_current_cli_direct_execution`, `wrapper_scaffold_decision=allow_wrapper_scaffold_only`, `wrapper_execution_decision=not_authorized`, `dry_run_execution_decision=not_authorized`, `live_execution_decision=not_authorized`, `ready_for_preflight_decision=not_authorized`, `biohub_esmc_decision=not_authorized`, `embedding_generation_decision=not_authorized`, `artifact_decision=not_authorized`, and `allowed_next_action_after_policy=prepare_manifest_aware_wrapper_scaffold_pr`.

The policy contract clarifies that the old adapter scaffold value `required_next_action=add_manifest_aware_wrapper_or_guardrail_before_execution` means only blocked future actions: `prepare_manifest_aware_wrapper_scaffold_pr`, `add_source_level_manifest_guardrail_before_execution`, or `keep_runtime_blocked`. `allow_wrapper_scaffold_only` means only that a later PR may prepare a wrapper scaffold; it does not mean the wrapper exists, does not mean wrapper execution is allowed, and does not mean dry-run execution is allowed.

This contract does not add a `pyproject.toml` script entry point, does not implement a manifest-aware wrapper, does not authorize wrapper execution, does not authorize dry-run execution, does not run `curated-embedding-preflight`, does not run `curated_embedding_preflight`, does not run `curated-embedding-single`, does not run `curated_embedding_single`, does not run `--help`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 wrapper command contract scaffold checkpoint

`src/longevity_port_pipelines/stages/g3sx30_wrapper_command_contract_scaffold.py` adds a non-executable helper/table scaffold for the future G3SX30 wrapper command contract. The scaffold sources `data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1`, `data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1`, and `data/input/g3sx30_dry_run_preflight_manifest.csv#1`.

The concrete command contract scaffold row is `data/interim/g3sx30_wrapper_command_contract_scaffold.csv#1`. It records `command_contract_status=command_contract_scaffold_runtime_blocked`, `command_contract_decision=define_future_command_contract_only`, `source_wrapper_status=wrapper_scaffold_runtime_blocked`, `source_wrapper_decision=prepare_wrapper_plan_only`, `expected_command_family=curated_embedding_preflight_dry_run_wrapper`, `actual_cli_help_observed=false`, `actual_command_verified=false`, `command_selected=false`, `output_path_selected=false`, `execution_plan_materialized=false`, `execution_authorized=false`, `wrapper_execution_authorized=false`, `dry_run_execution_authorized=false`, `live_execution_authorized=false`, `ready_for_preflight_authorized=false`, `biohub_esmc_authorized=false`, `embedding_generation_authorized=false`, `npy_artifact_authorized=false`, `data_output_artifact_commit_authorized=false`, `output_path_policy=do_not_write_committed_data_output`, `allowed_output_location_policy=future_temp_or_manual_reviews_path_only`, `unverified_until_help_or_source_guardrail=true`, `future_command_contract_scaffold_only=true`, `runtime_still_blocked=true`, `allowed_next_action_after_command_contract=add_wrapper_source_guardrail_pr`, and `claim_status=technical_checkpoint`.

This scaffold may define expected future command contract vocabulary, required future args vocabulary, forbidden future args vocabulary, required future guardrails, forbidden actions, and output-path policy. It must not claim `actual_supported_args`, `observed_help_flags`, or `verified_cli_contract` because this PR does not run `--help` and does not inspect a source-level CLI guardrail. It does not add a `pyproject.toml` script entry point, does not add a Typer executable wrapper, does not authorize wrapper execution, does not authorize dry-run execution, does not authorize live execution, does not run any actual command, does not run `--help`, does not make observed-help claims, does not make actual CLI flag verification claims, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 wrapper source guardrail scaffold checkpoint

`src/longevity_port_pipelines/stages/g3sx30_wrapper_source_guardrail_scaffold.py` adds a non-executable helper/table scaffold for the future G3SX30 wrapper source-level guardrails. The scaffold sources `data/interim/g3sx30_wrapper_command_contract_scaffold.csv#1`, `data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1`, `data/input/g3sx30_dry_run_preflight_manifest.csv#1`, and `data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1`.

The concrete source guardrail scaffold row is `data/interim/g3sx30_wrapper_source_guardrail_scaffold.csv#1`. It records `source_guardrail_status=source_guardrail_scaffold_runtime_blocked`, `source_guardrail_decision=define_source_level_guardrails_only`, `guardrail_scope=future_wrapper_source_checks_only`, `guardrail_runtime_effect=no_runtime_effect`, `source_command_contract_status=command_contract_scaffold_runtime_blocked`, `source_command_contract_decision=define_future_command_contract_only`, `source_actual_cli_help_observed=false`, `source_actual_command_verified=false`, `source_command_selected=false`, `source_output_path_selected=false`, `source_execution_plan_materialized=false`, `source_runtime_still_blocked=true`, `manifest_row_required=true`, `manifest_row_index_required=1`, `reviewed_sequence_length=492`, `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, `max_live_batch_size_zero_required=true`, `all_runtime_permissions_false_required=true`, `non_committed_output_path_required_before_future_dry_run=true`, `committed_data_output_rejected=true`, `source_guardrail_verification_observed=false`, `source_guardrail_implemented=false`, `actual_source_code_modified=false`, `actual_cli_help_observed=false`, `actual_command_verified=false`, `wrapper_implementation_authorized=false`, `wrapper_execution_authorized=false`, `dry_run_execution_authorized=false`, `live_execution_authorized=false`, `ready_for_preflight_authorized=false`, `biohub_esmc_authorized=false`, `embedding_generation_authorized=false`, `npy_artifact_authorized=false`, `data_output_artifact_commit_authorized=false`, `gate8_promotion_authorized=false`, `gate9_promotion_authorized=false`, `biological_claim_authorized=false`, `allowed_next_action_after_source_guardrail=add_wrapper_help_observation_note_pr`, `claim_status=technical_checkpoint`, and `runtime_still_blocked=true`.

This scaffold defines future wrapper source checks only. It has no runtime effect, does not implement a source guardrail, does not modify actual wrapper source code, does not add a `pyproject.toml` script entry point, does not add a Typer executable wrapper, does not implement a manifest-aware wrapper, does not authorize wrapper execution, does not authorize dry-run execution, does not authorize live execution, does not run any actual command, does not run `--help`, does not make observed-help claims, does not make actual CLI flag verification claims, does not select a command, does not select an output path, does not materialize an execution plan, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 wrapper help observation note checkpoint

`docs/g3sx30_wrapper_help_observation_note.md` records the final pre-help observation note after the G3SX30 wrapper source guardrail scaffold. It is a docs-only checkpoint, not a schema/table/helper layer, and it follows `data/interim/g3sx30_wrapper_source_guardrail_scaffold.csv#1`.

The note records `help_observation_status=planned_not_observed`, `actual_cli_help_observed=false`, `actual_command_verified=false`, `command_selected=false`, `output_path_selected=false`, `execution_plan_materialized=false`, and `runtime_still_blocked=true`.

It concretely defines which future command family may be observed later (`curated_embedding_preflight_dry_run_wrapper`), which commands must not be observed as a substitute (`curated-embedding-preflight`, `curated_embedding_preflight`, `curated-embedding-single`, `curated_embedding_single`), what counts as safe help-only observation, what output/evidence must be captured later, which strings/flags must be checked later, and which stop conditions abort before any later execution. It also explains why help observation is still not execution, still not `ready_for_preflight`, and still not Biohub / ESMC / embedding generation.

This note does not run `--help`, does not run any actual command, does not make observed-help claims, does not make actual CLI flag verification claims, does not add a `pyproject.toml` script entry point, does not add a Typer executable wrapper, does not implement a wrapper, does not authorize wrapper execution, does not authorize dry-run execution, does not authorize live execution, does not select a command, does not select an output path, does not materialize an execution plan, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.

The natural next step after this note is the actual G3SX30 wrapper help observation PR. That future PR should still be help-only, still no execution, still no Biohub / ESMC, and still no embeddings.


## G3SX30 wrapper help target inspection blocker checkpoint

`docs/g3sx30_wrapper_help_target_inspection_blocker.md` records the source-inspection blocker after the G3SX30 wrapper help observation note. It is a docs/tests-only checkpoint that records source search results; it is not a schema/table/helper layer and it is not a help-observation evidence layer.

The note records `help_target_inspection_status=inspected_target_missing`, `real_g3sx30_wrapper_help_target_found=false`, `pyproject_g3sx30_script_entry_present=false`, `pyproject_wrapper_script_entry_present=false`, `ordinary_curated_embedding_scripts_present=true`, `ordinary_scripts_valid_as_substitutes=false`, `actual_cli_help_observed=false`, `actual_command_verified=false`, `command_selected=false`, `output_path_selected=false`, `execution_plan_materialized=false`, and `runtime_still_blocked=true`.

The inspection found `curated_embedding_preflight_dry_run_wrapper` only as an expected future command family in scaffold/config/docs/tests, not as a real executable script entry point or implemented wrapper command. It also found that `pyproject.toml` exposes ordinary curated embedding scripts (`curated-embedding-preflight` and `curated-embedding-single`) but no G3SX30 script entry and no wrapper script entry.

This blocker records that the ordinary commands `curated-embedding-preflight`, `curated_embedding_preflight`, `curated-embedding-single`, and `curated_embedding_single` must not be observed as substitutes for the missing G3SX30 manifest-aware wrapper target. Observing their help output would not verify the wrapper interface and would create a misleading observed-help claim.

This blocker does not run `--help`, does not run any actual command, does not make observed-help claims, does not make actual CLI flag verification claims, does not add a `pyproject.toml` script entry point, does not add a Typer executable wrapper, does not implement a wrapper, does not authorize wrapper execution, does not authorize dry-run execution, does not authorize live execution, does not select a command, does not select an output path, does not materialize an execution plan, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.

The natural next step is not help observation yet. The next complete safe layer should create an explicitly non-executed G3SX30 manifest-aware wrapper source/entry-point implementation plan or implementation boundary. Only after a real wrapper help target exists may a later PR perform actual help-only observation, still with no wrapper execution, no dry-run execution, no Biohub / ESMC, and no embeddings.


## G3SX30 wrapper source entry-point boundary checkpoint

`src/longevity_port_pipelines/stages/g3sx30_wrapper_source_entrypoint_boundary.py` adds a runtime-blocked G3SX30 wrapper source entry-point boundary, and `pyproject.toml` exposes it as `g3sx30-wrapper-dry-run`.

The boundary records `entrypoint_boundary_status=source_entrypoint_boundary_runtime_blocked`, `script_entry_point=g3sx30-wrapper-dry-run`, `expected_command_family=curated_embedding_preflight_dry_run_wrapper`, `actual_cli_help_observed=false`, `actual_command_verified=false`, `command_selected_for_execution=false`, `output_path_selected_for_execution=false`, `execution_plan_materialized=false`, `wrapper_execution_authorized=false`, `dry_run_execution_authorized=false`, `live_execution_authorized=false`, `ready_for_preflight_authorized=false`, `biohub_esmc_authorized=false`, `embedding_generation_authorized=false`, and `runtime_still_blocked=true`.

This closes the blocker found in `docs/g3sx30_wrapper_help_target_inspection_blocker.md`: a real wrapper help target now exists for a later help-only observation PR. The future help-only target is `uv run g3sx30-wrapper-dry-run --help`.

This boundary does not run `--help`, does not make observed-help claims, does not make actual CLI flag verification claims, does not execute the wrapper, does not execute a dry-run, does not execute a live run, does not select a command for execution, does not select an output path for execution, does not materialize an execution plan, does not read or execute the G3SX30 manifest, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.

The ordinary commands `curated-embedding-preflight`, `curated_embedding_preflight`, `curated-embedding-single`, and `curated_embedding_single` remain invalid substitutes. The natural next PR is an actual G3SX30 wrapper help observation PR, still help-only, still no wrapper execution, still no dry-run execution, still no Biohub / ESMC, and still no embeddings.


## G3SX30 wrapper actual help observation checkpoint

`docs/g3sx30_wrapper_actual_help_observation.md` records a help-only observation of the runtime-blocked G3SX30 wrapper source entry-point boundary.

The observed command was `uv run g3sx30-wrapper-dry-run --help`, with `HELP_EXIT_CODE=0`. The help output was captured outside the repository at `D:\biohub_projects\_chatgpt_observations\g3sx30_wrapper_help_output.txt`, and this external observation file is not a committed runtime artifact.

The observation records `help_observation_status=observed_help_only`, `observed_help_target=g3sx30-wrapper-dry-run`, `observed_manifest_option=true`, `observed_manifest_row_index_option=true`, `observed_output_path_option=true`, `observed_help_option=true`, `actual_cli_help_observed=true`, `actual_command_verified_for_help=true`, `command_selected_for_execution=false`, `output_path_selected_for_execution=false`, `execution_plan_materialized=false`, `wrapper_execution_authorized=false`, `dry_run_execution_authorized=false`, `live_execution_authorized=false`, `biohub_esmc_authorized=false`, `embedding_generation_authorized=false`, and `runtime_still_blocked=true`.

The observed help output included `Usage: g3sx30-wrapper-dry-run [OPTIONS]`, `--manifest`, `--manifest-row-index`, `--output-path`, and `--help`. The capture also included `uv` build/install warning output and a PowerShell `NativeCommandError` wrapper around stderr text, but this is not treated as command failure because `HELP_EXIT_CODE=0` was observed.

No-runtime-artifact proof after the help observation showed `git status -sb` on `observe-g3sx30-wrapper-help` with no modified files and `git ls-files --others --exclude-standard` with no untracked files.

This checkpoint does not run the wrapper without `--help`, does not execute a dry-run, does not execute a live run, does not read or execute the G3SX30 manifest, does not select a command for execution, does not select an output path for execution, does not materialize an execution plan, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not write `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.

The natural next layer is not execution yet. A later PR may create a stricter source-level runtime blocker or execution-plan review gate for the G3SX30 wrapper. Runtime execution should remain blocked until a separate reviewed gate explicitly authorizes a dry-run path with non-committed output location, no Biohub / ESMC, no embedding generation, and no `ready_for_preflight` promotion.


## G3SX30 wrapper execution-plan review gate checkpoint

`data/interim/g3sx30_wrapper_execution_plan_review_gate.csv#1` records a runtime-blocked execution-plan review gate after actual G3SX30 wrapper help observation.

The row records `execution_plan_review_status=execution_plan_review_gate_runtime_blocked`, `execution_plan_review_decision=require_separate_review_before_any_execution`, `help_observation_status=observed_help_only`, `help_exit_code=0`, `observed_help_target=g3sx30-wrapper-dry-run`, `observed_manifest_option=true`, `observed_manifest_row_index_option=true`, `observed_output_path_option=true`, `observed_help_option=true`, `dry_run_plan_review_required_before_execution=true`, `non_committed_output_path_review_required=true`, `output_path_selected_for_execution=false`, `command_selected_for_execution=false`, `execution_plan_materialized=false`, `wrapper_execution_authorized=false`, `dry_run_execution_authorized=false`, `live_execution_authorized=false`, `ready_for_preflight_authorized=false`, `biohub_esmc_authorized=false`, `embedding_generation_authorized=false`, `npy_artifact_authorized=false`, `data_output_artifact_commit_authorized=false`, `gate8_promotion_authorized=false`, `gate9_promotion_authorized=false`, `biological_claim_authorized=false`, `runtime_still_blocked=true`, `allowed_next_action_after_review_gate=add_g3sx30_wrapper_execution_plan_runtime_blocker`, and `claim_status=technical_checkpoint`.

This checkpoint means help observation is not execution authorization. A later execution plan must still be separately reviewed before any future dry-run can be considered, and it must require an explicit non-committed output path, reject committed `data/output` artifacts, reject Biohub / ESMC, reject embedding generation, reject `.npy` artifacts, keep `ready_for_preflight` false, keep Gate 8 and Gate 9 blocked, and make no biological claim.

This checkpoint does not run `g3sx30-wrapper-dry-run`, does not run the wrapper without `--help`, does not execute a dry-run, does not execute a live run, does not read or execute the G3SX30 manifest, does not select a command for execution, does not select an output path for execution, does not materialize an execution plan, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not write `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.

The natural next layer is still not dry-run execution. A later PR may add a source-level runtime blocker or a non-executable execution-plan object scaffold. Runtime execution should remain blocked until a separate reviewed gate explicitly authorizes a dry-run path with a non-committed output location and all live/embedding permissions false.


## G3SX30 wrapper source runtime fail-closed tests checkpoint

`tests/test_g3sx30_wrapper_source_entrypoint_boundary.py` now exercises the actual `g3sx30-wrapper-dry-run` Typer entrypoint for non-help invocation.

The source-level tests prove that invoking the entrypoint without `--help` exits blocked with exit code 2, prints the runtime-blocked boundary message, and does not authorize wrapper execution, dry-run execution, live execution, Biohub / ESMC calls, or embedding generation.

The tests also pass future-looking `--manifest`, `--manifest-row-index`, and `--output-path` arguments to the actual entrypoint and prove that those arguments remain interface-documentation-only: the manifest is not read or created, the output path is not written, no output directory is created, no command is selected for execution, no output path is selected for execution, no execution plan is materialized, all runtime authorization flags remain false, and `runtime_still_blocked` remains true.

This checkpoint does not run a dry-run, does not run a live path, does not execute the G3SX30 manifest, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not write `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, and does not make biological claims.

Because the actual source entrypoint now has source-level fail-closed tests, the next practical layer should be `Add G3SX30 wrapper dry-run execution plan scaffold`, not another blocker layer.


## G3SX30 one-row non-committed preflight input binding

`data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv` records a machine-readable one-row binding for the already-generated local runtime G3SX30 / elephant MDM2 ESMC embedding artifact.

The binding sources `data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv#1`, which already records `approved_for_one_row_readiness_preflight_input=true`, while keeping `ready_for_preflight=false`, `gate8_promoted=false`, `gate9_promoted=false`, and `biological_claim_made=false`.

The binding identifies the biological target as `candidate_id=tp53_mdm2_elephant_seed_mdm2_chain`, `target_accession=G3SX30`, `target_accession_db=UniProtKB TrEMBL`, `target_species=Loxodonta africana`, `target_taxid=9785`, `gene_symbol=MDM2`, and `sequence_length=492`.

The binding records `local_embedding_path=data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`, `artifact_location=local_runtime_data_output_ignored_by_git`, `local_runtime_embedding_tracked=false`, `local_runtime_embedding_committed=false`, `embedding_shape=492x960`, `embedding_dtype=float32`, `embedding_finite=true`, and `sequence_length_matches=true`.

The binding decision is `non_committed_preflight_input_reference_created=true`, while keeping `ready_for_preflight=false`, `gate8_promoted=false`, `gate9_promoted=false`, and `biological_claim_made=false`.

The next concrete check is `run_record_g3sx30_one_row_local_embedding_preflight_check`, with `next_check_scope=local_artifact_shape_dtype_finiteness_sequence_length_path_policy_only`, `next_check_input=data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv#1`, `next_check_output_policy=external_non_committed_observation_only`, and `next_check_output_example=D:/biohub_projects/_chatgpt_observations/g3sx30_one_row_local_embedding_preflight_check.json`. After this binding PR, do not add another review, scaffold, or binding layer; the next PR should run and record the G3SX30 one-row local embedding preflight check.

This binding does not make a new Biohub / ESMC call, does not rerun live embedding, does not generate a new embedding, does not commit the generated `.npy` artifact, does not commit any `data/output` artifact, does not copy external validation JSON into the repo, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make a biological claim.


## G3SX30 one-row local embedding readiness/preflight input decision

`data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv` records a one-row bounded use decision for the already-generated local runtime G3SX30 embedding artifact.

The source runtime observation is `docs/g3sx30_one_row_live_embedding_runtime_observation.md`, and the source post-live artifact audit is `docs/g3sx30_post_live_local_artifact_status.md`.

The decision records `local_embedding_path=data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`, `external_validation_json=D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json`, `local_runtime_embedding_exists=true`, `local_runtime_embedding_tracked=false`, `local_runtime_embedding_committed=false`, and `artifact_location=local_runtime_data_output_ignored_by_git`.

The reviewed validation summary records `embedding_shape=492x960`, `embedding_dtype=float32`, `embedding_finite=true`, `sequence_length_matches=true`, `validation_ready_for_preflight_promoted=false`, `validation_gate8_promoted=false`, `validation_gate9_promoted=false`, and `validation_biological_claim_made=false`.

The decision is `approved_for_one_row_readiness_preflight_input=true` and `readiness_preflight_input_record_status=approved_local_runtime_artifact_as_one_row_readiness_preflight_input`, while keeping `ready_for_preflight=false`, `gate8_promoted=false`, `gate9_promoted=false`, and `biological_claim_made=false`.

This distinction is intentional: approving the local artifact path as a one-row readiness/preflight input reference is allowed here, but promoting `ready_for_preflight`, Gate 8, Gate 9, or any biological claim is not allowed.

This decision does not make a new Biohub / ESMC call, does not rerun live embedding, does not generate a new embedding, does not commit the generated `.npy` artifact, does not commit any `data/output` artifact, does not commit the external FASTA artifact, does not commit the external live log, does not commit the external validation JSON, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make a biological claim.

The next actionable step is `prepare_one_row_non_committed_preflight_input_consumer_or_manifest_binding_pr`, which must consume or bind this one-row decision record without committing the local `.npy`, without using committed `data/output`, without promoting `ready_for_preflight`, without Gate 8 / Gate 9 promotion, and without biological claims.


## G3SX30 post-live local artifact status checkpoint

`docs/g3sx30_post_live_local_artifact_status.md` records the local runtime artifact status after the already-merged guarded one-row G3SX30 live embedding.

The first guarded Biohub / ESMC live embedding call has already happened and was already recorded as `status=live_completed`, `embedding_shape=492x960`, `live_exit_code=0`, and `embedding_exists=true`. This checkpoint does not run live embedding again.

The local runtime embedding artifact exists at `data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`. The local status is `local_runtime_embedding_exists=true`, `tracked_embedding_files=none`, `ignore_rule=.gitignore:9:data/output/*`, `local_runtime_embedding_tracked=false`, `local_runtime_embedding_committed=false`, and `artifact_location=local_runtime_data_output_ignored_by_git`.

The external observation artifacts exist outside the repository and are not committed: `D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_output.txt`, `D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json`, `D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta`, and `D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence_validation.json`.

The external validation JSON records `shape=492x960`, `dtype=float32`, `finite=true`, `sequence_length_matches=true`, `biohub_esmc_called=true`, `embedding_generation_performed=true`, `npy_artifact_created=true`, `data_output_artifact_committed=false`, `ready_for_preflight_promoted=false`, `gate8_promoted=false`, `gate9_promoted=false`, and `biological_claim_made=false`.

This audit does not make a new Biohub / ESMC call, does not rerun live embedding, does not generate a new embedding, does not commit the generated `.npy` artifact, does not commit any `data/output` artifact, does not commit the external FASTA artifact, does not commit the external live log, does not commit the external validation JSON, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make a biological claim.

After this short post-live audit, do not add another generic checkpoint, review, scaffold, or decision layer. The next practical PR should decide how to use the local embedding artifact safely, for example `Review G3SX30 local embedding artifact and decide readiness/preflight path` or `Approve G3SX30 local embedding artifact for one-row readiness/preflight input`.


## G3SX30 one-row live embedding runtime observation checkpoint

`docs/g3sx30_one_row_live_embedding_runtime_observation.md` records the guarded one-row G3SX30 live embedding runtime observation.

The live command was `uv run g3sx30-live-embedding-one-row --yes-live --max-live-batch-size 1`. The command output was captured outside the repository at `D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_output.txt`. The local validation JSON was written outside the repository at `D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json`. These external observation artifacts are not committed.

The command validated `manifest_path=data/input/g3sx30_dry_run_preflight_manifest.csv`, `manifest_row_index=1`, `reviewed_sequence_fasta=D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta`, `candidate_id=tp53_mdm2_elephant_seed_mdm2_chain`, `chain=mdm2`, `target_accession=G3SX30`, `target_taxid=9785`, `gene_symbol=MDM2`, `model_name=esmc-300m-2024-12`, `sequence_length=492`, and `sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`.

The live result recorded `mode=live`, `status=live_completed`, `embedding_shape=492x960`, `live_exit_code=0`, and `embedding_exists=true`.

The generated local runtime artifact is `data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`. The local artifact validation recorded `shape=492x960`, `dtype=float32`, `finite=true`, `sequence_length_matches=true`, `biohub_esmc_called=true`, `embedding_generation_performed=true`, `npy_artifact_created=true`, `data_output_artifact_committed=false`, `ready_for_preflight_promoted=false`, `gate8_promoted=false`, `gate9_promoted=false`, `biological_claim_made=false`, and `artifact_location=local_runtime_data_output_ignored_by_git`.

This runtime observation does not commit the generated `.npy` artifact, does not commit any `data/output` artifact, does not commit the external FASTA artifact, does not commit the external live log, does not commit the external validation JSON, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make biological claims.

This closes the first guarded G3SX30 one-row live embedding runtime observation as a technical runtime checkpoint only. It does not unlock downstream gates by itself.


## G3SX30 one-row live embedding strict guardrail wrapper checkpoint

`src/longevity_port_pipelines/stages/g3sx30_live_embedding_one_row.py` adds the source-level executable guardrail wrapper for `Execute one-row G3SX30 live embedding with strict guardrails`.

The command entry point is `g3sx30-live-embedding-one-row = longevity_port_pipelines.stages.g3sx30_live_embedding_one_row:app`. The default command is dry-run-only: `uv run g3sx30-live-embedding-one-row`. The live command must be explicit: `uv run g3sx30-live-embedding-one-row --yes-live --max-live-batch-size 1`.

The wrapper reads `data/input/g3sx30_dry_run_preflight_manifest.csv#1`, validates `docs/current_gate_map.md` contains the prior approval for `execute_one_row_g3sx30_live_embedding_with_strict_guardrails`, and validates the external non-committed reviewed sequence artifact `D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta`.

The wrapper requires `manifest_row_index=1`, `candidate_id=tp53_mdm2_elephant_seed_mdm2_chain`, `chain=mdm2`, `target_accession=G3SX30`, `target_taxid=9785`, `gene_symbol=MDM2`, `reviewed_sequence_length=492`, `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, `max_live_batch_size=1`, and explicit `--yes-live` before any Biohub / ESMC call.

The expected local runtime embedding path is `data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy`.

This checkpoint adds the wrapper and tests. It does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output`, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make biological claims.

After this checkpoint, the same PR may run the guarded command with explicit `--yes-live --max-live-batch-size 1` and then record the live runtime observation without committing the generated `.npy`.


## G3SX30 dry-run observation next data-step review checkpoint

`docs/g3sx30_dry_run_observation_next_data_step_review.md` reviews the already-observed G3SX30 wrapper dry-run external observation and directly decides the next data-producing step.

The reviewed external observation path is `D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json`. The external JSON observation remains outside the repository and is not committed.

The review records `dry_run_observation_reviewed=true`, `dry_run_observation_blocker_found=false`, `dry_run_executed=true`, `manifest_row_index=1`, `target_accession=G3SX30`, `target_taxid=9785`, `reviewed_sequence_length=492`, `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, `manifest_row_read=true`, `manifest_row_validated=true`, `biohub_esmc_called=false`, `embedding_generation_performed=false`, `npy_artifact_created=false`, `data_output_artifact_created=false`, `ready_for_preflight_promoted=false`, `gate8_promoted=false`, `gate9_promoted=false`, and `biological_claim_made=false`.

The next data-step decision is `next_data_step_decision=approve_one_row_live_embedding_for_next_pr`, `live_embedding_authorized_for_next_pr=true`, `live_embedding_authorized_in_this_pr=false`, `max_live_batch_size_for_next_pr=1`, `ready_for_preflight_authorized=false`, `gate8_promotion_authorized=false`, `gate9_promotion_authorized=false`, `biological_claim_authorized=false`, `allowed_next_action_after_review=execute_one_row_g3sx30_live_embedding_with_strict_guardrails`, and `claim_status=technical_checkpoint`.

This checkpoint does not rerun `g3sx30-wrapper-dry-run`, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not create or commit `data/output` artifacts, does not run a live path in this PR, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make biological claims.

After this checkpoint, do not add another generic checkpoint, review, scaffold, or decision layer. The next practical PR should be `Execute one-row G3SX30 live embedding with strict guardrails`: one row only, manifest row #1 only, explicit live opt-in required, max_live_batch_size=1, local runtime artifact only, no committed `.npy`, no committed `data/output`, no `ready_for_preflight`, no Gate 8 / Gate 9, no Boltz / AF3 / Chai, no enrichment or contrast rerun, and no biological claim.


## G3SX30 wrapper dry-run observation checkpoint

`docs/g3sx30_wrapper_dry_run_observation_checkpoint.md` records the already-executed G3SX30 wrapper dry-run external observation.

The external observation path is `D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json`. The external JSON observation is outside the repository and is not committed.

The observed external JSON recorded `dry_run_executed=true`, `manifest_row_index=1`, `target_accession=G3SX30`, `target_taxid=9785`, `reviewed_sequence_length=492`, `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, `manifest_row_read=true`, `manifest_row_validated=true`, `biohub_esmc_called=false`, `embedding_generation_performed=false`, `npy_artifact_created=false`, `data_output_artifact_created=false`, `ready_for_preflight_promoted=false`, `gate8_promoted=false`, `gate9_promoted=false`, `biological_claim_made=false`, `sequence_fetch_performed=false`, `live_execution_performed=false`, `manifest_execution_performed=false`, `curated_embedding_preflight_run=false`, `curated_embedding_single_run=false`, `boltz_called=false`, `af3_called=false`, `chai_called=false`, `enrichment_rerun=false`, `contrast_rerun=false`, and `claim_status=technical_checkpoint`.

This checkpoint does not rerun `g3sx30-wrapper-dry-run`, does not commit the external JSON observation, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not create or commit `data/output` artifacts, does not run a live path, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make biological claims.

After this checkpoint, do not add another generic checkpoint, review, scaffold, or blocker layer. The next practical step should be `Review G3SX30 dry-run observation and decide the next data-producing step`: either prepare a one-row live embedding decision or repair a concrete blocker found in the dry-run observation.


## G3SX30 wrapper dry-run external output execution checkpoint

`src/longevity_port_pipelines/stages/g3sx30_wrapper_source_entrypoint_boundary.py` now permits only the reviewed G3SX30 external-output dry-run path.

The reviewed command is `uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json`.

The source validates `data/input/g3sx30_dry_run_preflight_manifest.csv#1`, validates the G3SX30 constants, validates the reviewed external output path, and writes a small JSON observation to `D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json`. The JSON output is external and must not be committed.

The dry-run observation records `dry_run_executed=true`, `manifest_row_index=1`, `target_accession=G3SX30`, `target_taxid=9785`, `reviewed_sequence_length=492`, `reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, `biohub_esmc_called=false`, `embedding_generation_performed=false`, `npy_artifact_created=false`, `data_output_artifact_created=false`, `ready_for_preflight_promoted=false`, `gate8_promoted=false`, `gate9_promoted=false`, and `biological_claim_made=false`.

This checkpoint allows only the reviewed external-output dry-run. It does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not run a live path, does not promote `ready_for_preflight`, does not promote Gate 8 or Gate 9, does not call Boltz / AF3 / Chai, does not rerun enrichment or contrast, and does not make biological claims.


## G3SX30 wrapper dry-run execution plan scaffold review checkpoint

`src/longevity_port_pipelines/stages/g3sx30_wrapper_dry_run_execution_plan_review.py` adds the final non-execution review layer for the selected G3SX30 wrapper dry-run execution plan scaffold.

The concrete review row is `data/interim/g3sx30_wrapper_dry_run_execution_plan_review.csv#1`. It records `review_status=dry_run_execution_plan_scaffold_reviewed`, `review_scope=final_non_execution_review_before_actual_dry_run_pr`, `review_decision=approve_selected_external_output_dry_run_for_next_pr`, `selected_command_form_reviewed=true`, `selected_external_output_path_reviewed=true`, `selected_manifest_row_reviewed=true`, `dry_run_execution_authorized_for_next_pr=true`, `dry_run_execution_authorized_in_this_pr=false`, `dry_run_executed=false`, `live_execution_authorized=false`, `manifest_execution_authorized_in_this_pr=false`, `biohub_esmc_authorized=false`, `embedding_generation_authorized=false`, `npy_artifact_authorized=false`, `output_file_created=false`, `output_directory_created=false`, `data_output_artifact_commit_authorized=false`, `ready_for_preflight_authorized=false`, `gate8_promotion_authorized=false`, `gate9_promotion_authorized=false`, `biological_claim_authorized=false`, `runtime_still_blocked_in_this_pr=true`, `next_pr_must_use_reviewed_command_form=true`, `next_pr_must_use_reviewed_external_output_path=true`, `allowed_next_action_after_review=execute_g3sx30_wrapper_dry_run_with_external_output_path`, and `claim_status=technical_checkpoint`.

The reviewed command form is `uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json`. The reviewed external output path is `D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json`.

This checkpoint approves the selected command form and external output path for the next PR only. It does not run `g3sx30-wrapper-dry-run`, does not run a dry-run, does not run a live path, does not execute the G3SX30 manifest in this PR, does not create the external output file, does not create the external output directory, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not write `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, and does not make biological claims.

After this checkpoint, do not add another blocker, review, or scaffold layer. The next practical PR should be `Execute G3SX30 wrapper dry-run with external output path`, still with no Biohub / ESMC, no embeddings, no `.npy`, no `data/output` artifact commit, no Gate 8 / Gate 9, and no biological claim.


## G3SX30 wrapper dry-run execution plan scaffold checkpoint

`src/longevity_port_pipelines/stages/g3sx30_wrapper_dry_run_execution_plan_scaffold.py` adds a non-executable dry-run execution plan scaffold for the TP53/MDM2 elephant / G3SX30 lane.

The concrete scaffold row is `data/interim/g3sx30_wrapper_dry_run_execution_plan_scaffold.csv#1`. It records `execution_plan_scaffold_status=dry_run_execution_plan_scaffold_non_executable`, `execution_plan_scaffold_decision=select_future_command_form_and_external_output_path_only`, `script_entry_point=g3sx30-wrapper-dry-run`, `future_command_form_selected=true`, `future_non_committed_output_path_selected=true`, `future_output_path=D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json`, `output_path_policy=external_non_committed_observation_path_only`, `committed_data_output_rejected=true`, `output_file_created=false`, `output_directory_created=false`, `command_selected_for_execution=false`, `output_path_selected_for_execution=false`, `execution_plan_materialized=false`, `wrapper_execution_authorized=false`, `dry_run_execution_authorized=false`, `live_execution_authorized=false`, `manifest_execution_authorized=false`, `ready_for_preflight_authorized=false`, `biohub_esmc_authorized=false`, `embedding_generation_authorized=false`, `npy_artifact_authorized=false`, `data_output_artifact_commit_authorized=false`, `gate8_promotion_authorized=false`, `gate9_promotion_authorized=false`, `biological_claim_authorized=false`, `runtime_still_blocked=true`, `dry_run_execution_plan_scaffold_only=true`, and `claim_status=technical_checkpoint`.

The selected future command form is `uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json`. This is a future command form for review only, not a command selected for execution.

This checkpoint does not run `g3sx30-wrapper-dry-run`, does not run a dry-run, does not run a live path, does not execute the G3SX30 manifest, does not create the future output file, does not create the future output directory, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not write `data/output` artifacts, does not mark anything `ready_for_preflight`, does not promote Gate 8 or Gate 9, and does not make biological claims.

The natural next step is review of this scaffold before any execution is considered.


## G3SX30 manifest-aware dry-run wrapper scaffold checkpoint

`src/longevity_port_pipelines/stages/g3sx30_manifest_aware_dry_run_wrapper_scaffold.py` adds a non-executable helper/table scaffold representing the future G3SX30 manifest-aware dry-run wrapper boundary. The scaffold sources `data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1`, `data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1`, and `data/input/g3sx30_dry_run_preflight_manifest.csv#1`.

The concrete wrapper scaffold row is `data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1`. It records `wrapper_status=wrapper_scaffold_runtime_blocked`, `wrapper_decision=prepare_wrapper_plan_only`, `policy_contract_status=adapter_policy_runtime_blocked`, `policy_contract_decision=require_manifest_aware_wrapper_before_execution`, `current_cli_direct_execution_decision=reject_current_cli_direct_execution`, `wrapper_scaffold_decision=allow_wrapper_scaffold_only`, `wrapper_execution_decision=not_authorized`, `dry_run_execution_decision=not_authorized`, `live_execution_decision=not_authorized`, `ready_for_preflight_decision=not_authorized`, `biohub_esmc_decision=not_authorized`, `embedding_generation_decision=not_authorized`, `artifact_decision=not_authorized`, `command_selected=false`, `output_path_selected=false`, `execution_plan_materialized=false`, `runtime_still_blocked=true`, and `allowed_next_action_after_wrapper_scaffold=add_wrapper_command_contract_pr`.

This scaffold means only that the source policy contract, adapter scaffold, and manifest row are understood and that the future wrapper boundary is represented. It does not add a `pyproject.toml` script entry point, does not add a Typer executable wrapper, does not implement a manifest-aware wrapper, does not authorize wrapper execution, does not authorize dry-run execution, does not authorize live execution, does not run `curated-embedding-preflight`, does not run `curated_embedding_preflight`, does not run `curated-embedding-single`, does not run `curated_embedding_single`, does not run `--help`, does not select a command, does not select an output path, does not materialize an execution plan, does not call Biohub / ESMC, does not generate embeddings, does not create `.npy` artifacts, does not commit `data/output` artifacts, does not mark anything `ready_for_preflight`, does not unlock the manifest runtime path, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.


## Controlled missing embedding blocker checkpoint

The first controlled inspection for a reviewed missing embedding fill candidate is recorded in `docs/controlled_missing_embedding_blocker_checkpoint.md`.

This is a blocker checkpoint. The legacy `8f86` ligand-side `P84233` missing case is blocked by missing ortholog coverage and lacks reviewed target species, target taxid, target accession, and embedding path evidence. It is not selected for controlled dry-run or live fill.

The next safe action is coverage/provenance repair before any new embedding dry-run candidate selection. This checkpoint does not call Biohub, does not generate embeddings, does not use `curated_embedding_single --yes-live`, does not commit `data/output/` embedding artifacts, does not call Boltz, does not rerun enrichment/contrast, and does not make biological claims.

## Coverage/provenance repair queue checkpoint

The current Gate 4 / Gate 5 repair frontier is recorded in `docs/coverage_provenance_repair_queue_checkpoint.md`.

This checkpoint aligns the tracked SIRT6/core3 and TP53/MDM2 elephant repair queues without changing ortholog rows or fetching sequences. SIRT6/core3 has 11 rows in `data/input/sirt6_candidate_coverage_repair_decisions.csv` that require external/manual sequence provenance review. TP53/MDM2 elephant has two blocked seed rows in `data/input/tp53_mdm2_ortholog_repair_decisions.csv` that require source ortholog fetch/curation.

Both queues remain coverage/provenance blockers. They must not be bypassed by embedding fill, contrast, cofolding, live structural calls, or biological claims.

## TP53/MDM2 generic repair alignment checkpoint

The TP53/MDM2 elephant ortholog repair decision table is now aligned with the generic repair vocabulary in `docs/tp53_mdm2_generic_repair_alignment_checkpoint.md`.

The tracked table `data/input/tp53_mdm2_ortholog_repair_decisions.csv` now exposes generic fields including `lane_name`, `source_species`, `gene_symbol`, `target_uniprot`, `coverage_status`, `provenance_status`, `repair_status`, and `reviewer_note`.

Both TP53/MDM2 elephant seed rows remain blocked: `target_uniprot` is `unresolved`, `coverage_status` is `unresolved_downstream_provenance`, `provenance_status` is `unresolved`, and `repair_status` is `pending`. This alignment does not fetch sequences, does not resolve elephant orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not promote cofolding readiness, and does not make biological claims.

## Generic repair queue summary builder checkpoint

The first generic Gate 4 / Gate 5 repair queue summary builder is recorded in `docs/generic_repair_queue_summary_builder_checkpoint.md`.

The builder combines `data/input/sirt6_candidate_coverage_repair_decisions.csv` and `data/input/tp53_mdm2_ortholog_repair_decisions.csv` into a machine-readable repair queue summary. Current committed inputs are expected to produce 13 repair queue rows: 11 SIRT6/core3 rows and 2 TP53/MDM2 elephant rows.

The summary uses blocker-oriented fields including `repair_queue_status`, `downstream_block_status`, and `allowed_next_action`. It does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not promote Gate 8 or Gate 9, and does not make biological claims.

## Generic repair queue usage guide

The generic Gate 4 / Gate 5 repair queue usage guide is recorded in `docs/generic_repair_queue_usage_guide.md`.

The guide explains how to run `generic-repair-queue-summary`, how to interpret `repair_queue_status`, `downstream_block_status`, and `allowed_next_action`, and why these fields are repair-planning signals rather than downstream permissions.

The current committed repair queue summary is expected to contain 13 rows: 11 SIRT6/core3 rows and 2 TP53/MDM2 elephant rows. The guide explicitly keeps downstream gates blocked until ortholog/provenance evidence is reviewed and does not authorize sequence fetch, manual ortholog curation, Biohub calls, embedding generation, Boltz calls, Gate 8 promotion, Gate 9 promotion, or biological claims.

## Generic repair queue review checklist

The generic Gate 4 / Gate 5 repair queue review checklist is recorded in `docs/generic_repair_queue_review_checklist.md`.

The checklist explains how a reviewer should inspect repair queue rows before any row can be treated as reviewed-for-planning provenance evidence. It preserves blocker-first semantics: an unreviewed row remains a valid blocked repair-queue worklist item, not an invalid row.

This checklist does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not promote Gate 8 or Gate 9, and does not make biological claims.

## Generic repair queue reviewed-decision schema

The generic Gate 4 / Gate 5 repair queue reviewed-decision schema is recorded in `data/config/generic_repair_queue_review_schema.yaml`.

The schema defines how future manual provenance review decisions should be recorded machine-readably after checklist-based review. It covers row identity, pre-review blocker state, reviewed evidence, review decision vocabulary, downstream blocking policy, allowed next action, claim policy, claim status, and forbidden actions.

This schema does not record a reviewed biological provenance row by itself. It does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not promote Gate 8 or Gate 9, and does not make biological claims.

## First SIRT6 manual provenance review fixture

The first SIRT6 manual provenance review fixture is recorded in `data/input/generic_repair_queue_review_decisions.csv` and documented in `docs/sirt6_manual_provenance_review_checkpoint.md`.

This checkpoint reviews one concrete SIRT6 repair queue row as Level 1 biological provenance data. It checks whether the row can move from an unreviewed Gate 4 / Gate 5 blocker toward reviewed-for-planning provenance evidence.

The reviewed row remains blocked at Gate 4 / Gate 5 because the reviewed evidence records a deferred provenance decision rather than downstream eligibility. The row remains a valid blocked repair-queue worklist item.

This fixture does not fetch sequences, does not curate orthologs globally, does not call Biohub, does not generate embeddings, does not call Boltz, does not promote Gate 8 or Gate 9, and does not make biological claims.

## Generic repair queue reviewed-decision overlay

The generic repair queue summary builder can optionally consume reviewed decisions from data/input/generic_repair_queue_review_decisions.csv.

The overlay reads already-reviewed Gate 4 / Gate 5 provenance decisions and reflects them in the generic repair queue summary. Deferred decisions remain blocked at Gate 4 / Gate 5 and do not become downstream eligibility.

This overlay does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

## Generic repair queue summary checkpoint fixtures

The generic repair queue summary checkpoint fixtures are recorded in tests/fixtures/generic_repair_queue_summary_base.csv and tests/fixtures/generic_repair_queue_summary_reviewed_overlay.csv.

These fixtures freeze the expected base and reviewed-overlay repair queue summaries as regression checkpoints. The base fixture records 13 blocked Gate 4 / Gate 5 repair rows. The reviewed-overlay fixture records the same 13 rows with the reviewed SIRT6 row remaining deferred and blocked.

These fixtures do not fetch sequences, do not curate orthologs, do not call Biohub, do not generate embeddings, do not call Boltz, do not rerun enrichment or contrast, do not promote Gate 8 or Gate 9, and do not make biological claims.

## Gate 4 / Gate 5 repair policy helper

The Gate 4 / Gate 5 repair policy helper is documented in docs/gate_repair_policy_helper.md and implemented in src/longevity_port_pipelines/stages/gate_repair_policy.py.

The helper interprets repair queue and reviewed provenance states conservatively. Current blocked, deferred, rejected, second-review, and unknown states remain blocked at Gate 4 / Gate 5.

A reviewed-for-planning state may allow only a later explicit Gate 4 / Gate 5 policy update to be considered. It does not make a row Gate 8 eligible, does not make a row Gate 9 eligible, does not make embeddings ready, does not make Boltz ready, and does not allow biological claims.

The helper does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

## TP53/MDM2 provenance review checkpoint

The TP53/MDM2 provenance review checkpoint is documented in docs/tp53_mdm2_provenance_review_checkpoint.md.

This checkpoint adds reviewed provenance decisions for the elephant TP53 and MDM2 seed repair rows. Both reviewed decisions are deferred_pending_source because no accession-level elephant target ortholog evidence is accepted in this checkpoint.

Both TP53/MDM2 rows remain blocked at Gate 4 / Gate 5 as repair_worklist rows. The reviewed overlay fixture now records three reviewed rows total: one SIRT6 row and two TP53/MDM2 rows.

This checkpoint does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

## Ortholog evidence intake checklist

The ortholog evidence intake checklist is documented in docs/ortholog_evidence_intake_checklist.md.

This checklist defines how accession-level ortholog evidence should be recorded before a future reviewed-decision PR. It covers required row identity fields, minimum accession-level evidence fields, acceptable evidence sources, unacceptable evidence sources, intake outcomes, and blocker-first guardrails.

The checklist applies to the current SIRT6/core3 and TP53/MDM2 elephant lanes. It does not add new accessions, does not accept target orthologs, and does not change any repair queue row status.

Each intake row remains a Gate 4 / Gate 5 repair-queue worklist item until a later reviewed-decision PR and explicit Gate 4 / Gate 5 policy update say otherwise.

This checklist does not fetch sequences, does not curate orthologs automatically, does not call Biohub, does not generate embeddings, does not call Boltz, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

## Ortholog evidence intake ladder checkpoint

The Level 2 accession-level ortholog evidence intake ladder is now underway for the current Gate 4 / Gate 5 repair frontier.

The current ladder includes:

- `docs/ortholog_evidence_intake_checklist.md`
- `data/config/ortholog_evidence_intake_schema.yaml`
- `data/input/ortholog_evidence_intake.csv`
- `src/longevity_port_pipelines/stages/ortholog_evidence_intake.py`
- `data/config/ortholog_evidence_second_review_schema.yaml`
- `data/input/ortholog_evidence_second_review_queue.csv`
- `src/longevity_port_pipelines/stages/ortholog_evidence_second_review.py`
- `data/config/ortholog_stronger_source_evidence_request_schema.yaml`
- `data/input/ortholog_stronger_source_evidence_requests.csv`
- `src/longevity_port_pipelines/stages/ortholog_stronger_source_evidence_request.py`
- `data/config/ortholog_stronger_source_evidence_collection_schema.yaml`
- `data/input/ortholog_stronger_source_evidence_collection.csv`
- `src/longevity_port_pipelines/stages/ortholog_stronger_source_evidence_collection.py`
- `tests/test_ortholog_stronger_source_evidence_collection_schema.py`
- `tests/test_ortholog_stronger_source_evidence_collection_table.py`
- `tests/test_ortholog_stronger_source_evidence_collection_validator.py`
- `docs/ortholog_stronger_source_lookup_api_policy.md`
- `data/config/ortholog_stronger_source_lookup_plan_schema.yaml`
- `data/input/ortholog_stronger_source_lookup_plan.csv`
- `src/longevity_port_pipelines/stages/ortholog_stronger_source_lookup_plan.py`
- `tests/test_ortholog_stronger_source_lookup_plan_schema.py`
- `tests/test_ortholog_stronger_source_lookup_plan_table.py`
- `tests/test_ortholog_stronger_source_lookup_plan_validator.py`
- `tests/fixtures/ortholog_stronger_source_fixture_lookup_results.csv`
- `src/longevity_port_pipelines/stages/ortholog_stronger_source_fixture_lookup.py`
- `tests/test_ortholog_stronger_source_fixture_lookup.py`
- `src/longevity_port_pipelines/stages/ortholog_stronger_source_live_lookup_policy.py`
- `tests/test_ortholog_stronger_source_live_lookup_policy.py`

The stronger-source evidence collection layer has a schema, a table, and a table-only validator. The collection table now contains one G3SX30 metadata-only UniProtKB TrEMBL stronger-source collection row. This row is manual source-evidence collection only: it is not an accepted ortholog, not a reviewed decision, not a Gate 4 / Gate 5 policy update, not Gate 8 or Gate 9 promotion, and not a biological claim.

The stronger-source lookup layer has an API-boundary policy, a lookup plan schema, a header-only lookup plan table scaffold, and a table-only lookup plan validator.

The stronger-source fixture lookup layer adds a local fixture-backed lookup helper and synthetic fixture results under `tests/fixtures`. This layer can join fixture-backed lookup plan rows to committed synthetic fixture result rows. These results remain fixture-only payloads: they are not source evidence rows, not curated target decisions, not reviewed ortholog decisions, and not downstream-gate permissions.

The stronger-source live-lookup opt-in boundary now adds a policy helper for future live metadata lookup. The default decision remains denied. A future live-lookup path can pass this boundary only with explicit runtime opt-in, non-CI context, no sequence fetch request, the allowed raw metadata response output target, preserved Gate 4 / Gate 5 blocker status, preserved `repair_worklist` claim status, and explicit operator acknowledgement that results remain blocked and non-reviewed. This boundary does not implement a real API client and does not perform live external lookup.

The stronger-source live metadata client scaffold now wires future live metadata lookup attempts through this opt-in boundary using only an injected provider interface. Denied policy rows do not call the provider. Authorized policy rows can call an injected provider, but returned values remain raw metadata candidates only, with `sequence_included=false`, `evidence_row_created=false`, `reviewed_decision_created=false`, `blocked_gate4_gate5`, and `repair_worklist`. This scaffold does not implement a real API client, does not import network libraries, does not persist raw metadata tables, does not collect source evidence, does not create reviewed decisions, does not update Gate 4 / Gate 5 policy, does not promote Gate 8 or Gate 9, and does not make biological claims.

The stronger-source live metadata dry-run wrapper now adds an operator/runtime dry-run boundary around this scaffold. It wires lookup plan rows through the explicit live lookup policy decision and then through the scaffold-only metadata client using only injected fake/noop providers. Default-denied, CI-denied, sequence-fetch-requested, and missing-blocker-acknowledgement paths do not call the provider. Authorized context can call only the injected fake/noop provider, and output remains a typed dry-run summary: raw metadata candidate only, no persistence, no source evidence, no reviewed decision, no Gate 4 / Gate 5 policy update, no Gate 8 or Gate 9 promotion, no network lookup, and no biological claims.

The stronger-source raw metadata response layer now defines the future raw metadata response data contract with `data/config/ortholog_stronger_source_raw_metadata_response_schema.yaml`, header-only `data/input/ortholog_stronger_source_raw_metadata_responses.csv`, and `src/longevity_port_pipelines/stages/ortholog_stronger_source_raw_metadata_response.py`.

The raw metadata response builder status is `in_memory_builder_only`. Its input is `live_metadata_dry_run_summary_rows_plus_lookup_plan_provenance`, and its output is `dry_run_derived_raw_metadata_response_rows`. These rows remain fake/noop dry-run artifacts: dry-run-derived raw metadata response rows are not real external database metadata.

The raw metadata response exporter status is `explicit_table_writer_only`. It writes only already-built, already-validated raw metadata response rows to an explicit table path. It does not call the builder, provider, client, or network by itself. Exported dry-run-derived rows must remain explicit through `raw_metadata_source_type`, `raw_metadata_payload_ref`, `raw_metadata_summary`, and `reviewer_note`.

The raw metadata response review checklist is documented in `docs/ortholog_stronger_source_raw_metadata_response_review_checklist.md`. The raw metadata response review checklist status is `docs_only_human_review_protocol`. It defines how a reviewer should inspect raw metadata response rows before any later source evidence intake. The raw metadata response review checklist does not create source evidence, does not create manual review rows, does not create reviewed decisions, does not update Gate 4 / Gate 5, does not promote Gate 8 or Gate 9, and does not make biological claims.

The raw metadata response human review layer is recorded in `data/config/ortholog_stronger_source_raw_metadata_review_schema.yaml`, `data/input/ortholog_stronger_source_raw_metadata_reviews.csv`, and `src/longevity_port_pipelines/stages/ortholog_stronger_source_raw_metadata_review.py`. The table now contains one G3SX30 metadata-only human review row for the UniProtKB metadata-only sandbox row. This scaffold defines how a later reviewer may record metadata-only review of a raw metadata response row while keeping no source evidence, no reviewed decision, no Gate 4 / Gate 5 policy update, no Gate 8 or Gate 9 promotion, no sequence fetch, no embeddings, no Boltz, and no biological claim.

The first committed G3SX30 stronger-source lookup plan row is recorded in `data/input/ortholog_stronger_source_lookup_plan.csv`. It traces to `data/input/ortholog_stronger_source_evidence_requests.csv` row 1 for the MDM2 elephant accession-level evidence candidate `G3SX30`. This row is UniProtKB entry metadata lookup planning only, not a confirmed reviewed UniProt source. It keeps `live_lookup_allowed=false`, `sequence_fetch_allowed=false`, `blocked_gate4_gate5`, `repair_worklist`, and `no_biological_claims_until_validation`. Its planned output target is `data/input/ortholog_stronger_source_raw_metadata_responses.csv`, and its allowed next action is `add_raw_metadata_response_sandbox_row_later`, not source evidence intake, not a reviewed decision, not a Gate 4 / Gate 5 policy update, and not downstream eligibility.\n\nThe committed response table now contains one G3SX30 dry-run-derived raw metadata response row. It is explicitly fake/noop dry-run output, non-evidence, not real external metadata, not source evidence, not a manual review row, not a reviewed decision, not runtime persistence from a live provider, not a Gate 4 / Gate 5 policy update, not Gate 8 or Gate 9 promotion, and not a biological claim.

The first concrete TP53/MDM2 elephant accession-level evidence candidate is the MDM2 `G3SX30` row. It remains an accession-level evidence candidate only.

Current `G3SX30` status:

- evidence source database: `UniProtKB TrEMBL`
- evidence source accession: `G3SX30`
- target species: `Loxodonta africana`
- target taxid: `9785`
- target gene symbol: `MDM2`
- target sequence length: `492`
- second-review status: `second_review_complete_still_blocked`
- second-review decision: `needs_additional_source_evidence`
- reviewed target UniProt after second review: `unresolved`
- stronger-source request status: `pending_source_collection`
- stronger-source request decision: `needs_manual_source_collection`
- stronger-source collection table status: `one_g3sx30_row_still_blocked`
- manually collected stronger-source evidence rows: one G3SX30 metadata-only UniProtKB TrEMBL row
- stronger-source collection decision: collection_decision=`evidence_recorded_for_later_intake_pr`
- collected source evidence intake rows: one G3SX30 collected-source intake row ready for later reviewed-decision PR
- ortholog evidence review decision schema status: `schema_active`
- ortholog evidence review decision table status: `one_g3sx30_row_policy_blocked`
- ortholog evidence Gate 4 / Gate 5 policy update schema status: `schema_active`
- ortholog evidence Gate 4 / Gate 5 policy update table status: `one_g3sx30_row_runtime_blocked`
- ortholog evidence Gate 4 / Gate 5 policy update rows: one G3SX30 planning-policy update row still runtime-blocked
- ortholog evidence Gate 4 / Gate 5 policy update source: reviewed-decision row from `data/input/ortholog_evidence_review_decisions.csv#1`
- ortholog evidence Gate 4 / Gate 5 policy update result: policy_update_decision=`approve_gate45_policy_update_for_planning`, downstream_block_status_after_policy=`gate45_policy_updated_still_runtime_blocked`, allowed_next_action_after_policy=`prepare_later_gate_aware_embedding_fill_plan_pr`
- G3SX30 gate-aware embedding fill plan checkpoint status: `planning_policy_updated_runtime_blocked`
- G3SX30 gate-aware embedding fill plan checkpoint source: `data/input/ortholog_evidence_gate45_policy_updates.csv#1`
- G3SX30 gate-aware embedding fill plan checkpoint result: docs-only planning checkpoint; no sequence fetch, no Biohub call, no embedding generation, no committed embedding artifact, no Gate 8 / Gate 9 promotion, no Boltz/AF3/Chai call, and no biological claim
- controlled embedding fill worklist vocabulary status: `planning_policy_updated_runtime_blocked` is now machine-readable and blocked; recommended next action is `keep_blocked`; no preflight, no single dry-run, no live call, no Gate 8 / Gate 9 promotion, and no biological claim
- controlled embedding fill worklist G3SX30 checkpoint rows: one table-only G3SX30 row in `data/interim/controlled_embedding_fill_worklist_g3sx30_blocked_checkpoint.csv` with fill_status=`planning_policy_updated_runtime_blocked`, allowed_next_action=`keep_blocked`, dry_run_required=`false`, max_live_batch_size=`0`, sequence_length_status=`not_fetched`, embedding_path=`not_applicable_runtime_blocked`, no preflight, no single dry-run, no live call, no sequence fetch, no Biohub, no embedding generation, no Gate 8 / Gate 9 promotion, no Boltz/AF3/Chai call, and no biological claim
- G3SX30 blocked embedding-fill exit criteria status: docs-only review protocol in `docs/g3sx30_blocked_embedding_fill_exit_criteria.md`; current row remains `planning_policy_updated_runtime_blocked`; later exit requires reviewed target sequence provenance, `sequence_length_status=matches`, explicit separate dry-run preflight decision, no live call, no Gate 8 / Gate 9 promotion, and no biological claim
- reviewed target sequence provenance scaffold status: schema/table/helper scaffold in `data/config/reviewed_target_sequence_provenance_schema.yaml`, `data/input/reviewed_target_sequence_provenance.csv`, and `src/longevity_port_pipelines/stages/reviewed_target_sequence_provenance.py`; header-only, no G3SX30 sequence row, no sequence fetch, no Biohub / ESMC, no embeddings, no curated embedding preflight/single, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- reviewed target sequence provenance rows: one G3SX30 deferred pending-review row is preserved and does not record reviewed sequence provenance; one reviewed official UniProt sequence provenance row is added in `data/input/reviewed_target_sequence_provenance.csv` with sequence_source_type=`reviewed_external_database_record`, sequence_source_reference=`https://rest.uniprot.org/uniprotkb/G3SX30.fasta`, reviewed_sequence_length=`492`, reviewed_sequence_sha256=`e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, sequence_length_status=`matches`, sequence_review_status=`reviewed_sequence_provenance`, provenance_review_status=`reviewed`, allowed_next_action_after_sequence_review=`consider_later_dry_run_preflight_decision_pr`; no raw FASTA artifact commit, no target sequence review decision row mutation, no ready_for_preflight, no Biohub / ESMC, no embeddings, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- G3SX30 target sequence review checklist status: docs-only checklist in `docs/g3sx30_target_sequence_review_checklist.md`; requires traceability to `data/input/ortholog_evidence_gate45_policy_updates.csv#1`, identity checks for accession `G3SX30`, database `UniProtKB TrEMBL`, species `Loxodonta africana`, taxid `9785`, gene symbol `MDM2`, explicit sequence artifact/hash checks, reviewed length checking against expected metadata length `492`, mismatch handling, and separate later dry-run preflight decision; no sequence fetch, no reviewed sequence provenance row, no sequence_length_status=`matches`, no Biohub / ESMC, no embeddings, no ready_for_preflight, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- target sequence review decision scaffold status: schema/table/helper scaffold in `data/config/target_sequence_review_decision_schema.yaml`, `data/input/target_sequence_review_decisions.csv`, and `src/longevity_port_pipelines/stages/target_sequence_review_decisions.py`; header-only, no G3SX30 decision row, no mutation of reviewed target sequence provenance rows, no sequence fetch, no sequence_length_status=`matches`, no Biohub / ESMC, no embeddings, no ready_for_preflight, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- target sequence review decision rows: one G3SX30 deferred decision row is preserved in `data/input/target_sequence_review_decisions.csv` with sequence_review_decision=`defer_pending_sequence_review`; one reviewed G3SX30 target sequence approval decision row is added with source_sequence_provenance_row_index=`2`, sequence_review_decision=`approve_reviewed_sequence_provenance_for_planning`, sequence_length_status_after_decision=`matches`, provenance_review_status_after_decision=`reviewed`, reviewed_sequence_length=`492`, reviewed_sequence_sha256=`e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`, decision_status=`reviewed_for_planning_still_preflight_blocked`, downstream_block_status_after_decision=`sequence_reviewed_still_preflight_decision_blocked`, allowed_next_action_after_decision=`consider_later_dry_run_preflight_decision_pr`; no source provenance row mutation, no sequence fetch, no ready_for_preflight, no Biohub / ESMC, no embeddings, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- G3SX30 dry-run preflight decision rows: one G3SX30 dry-run preflight decision row in `data/input/g3sx30_dry_run_preflight_decisions.csv` references `data/input/target_sequence_review_decisions.csv#2` with dry_run_preflight_decision=`approve_dry_run_preflight_for_planning`, dry_run_preflight_status_after_decision=`dry_run_preflight_planning_approved_runtime_blocked`, allowed_next_action_after_decision=`prepare_later_dry_run_preflight_manifest_pr`, max_live_batch_size_after_decision=`0`, ready_for_preflight_after_decision=`false`; no curated_embedding_preflight run, no curated_embedding_single run, no Biohub / ESMC, no embeddings, no .npy, no ready_for_preflight runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- G3SX30 dry-run preflight manifest rows: one G3SX30 dry-run preflight manifest row in `data/input/g3sx30_dry_run_preflight_manifest.csv` references `data/input/g3sx30_dry_run_preflight_decisions.csv#1` with manifest_entry_status=`manifest_scaffold_ready_runtime_blocked`, dry_run_only=`true`, max_live_batch_size=`0`, ready_for_preflight_after_manifest=`false`, sequence_fetch_allowed=`false`, biohub_call_allowed=`false`, esmc_call_allowed=`false`, embedding_generation_allowed=`false`, curated_embedding_preflight_allowed=`false`, curated_embedding_single_allowed=`false`; no curated_embedding_preflight run, no curated_embedding_single run, no Biohub / ESMC, no embeddings, no .npy, no ready_for_preflight runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- G3SX30 dry-run preflight execution checklist status: docs-only checklist in `docs/g3sx30_dry_run_preflight_execution_checklist.md`; source manifest row is `data/input/g3sx30_dry_run_preflight_manifest.csv#1`; includes future dry-run command template, pre-run checks, post-run checks, forbidden artifacts, allowed language, and disallowed language; no curated_embedding_preflight run, no curated_embedding_single run, no Biohub / ESMC, no embeddings, no .npy, no data/output commit, no ready_for_preflight runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- G3SX30 dry-run preflight command discovery note status: docs-only note in `docs/g3sx30_dry_run_preflight_command_discovery_note.md`; source checklist is `docs/g3sx30_dry_run_preflight_execution_checklist.md`; source manifest row remains `data/input/g3sx30_dry_run_preflight_manifest.csv#1`; script names to inspect later are `curated-embedding-preflight` and `curated-embedding-single`; includes non-executed help commands, help-output checks, repository-search checks, no-run proof, and stop conditions; no curated-embedding-preflight run, no curated_embedding_preflight run, no curated-embedding-single run, no curated_embedding_single run, no Biohub / ESMC, no embeddings, no .npy, no data/output commit, no ready_for_preflight runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- G3SX30 dry-run preflight CLI compatibility note status: docs-only note in `docs/g3sx30_dry_run_preflight_cli_compatibility_note.md`; compares checklist/discovery expectations against `pyproject.toml`, `curated_embedding_preflight.py`, and `curated_embedding_single.py`; verdict: current CLI is not ready for direct G3SX30 manifest-row execution because preflight is dry-run-only but not manifest-aware and writes data/output by default, while single is dry-run by default but can call Biohub / ESMC with `--yes-live`; recommends manifest-aware adapter/wrapper, source-level guardrail, or stopping while runtime-blocked; no preflight/single run, no Biohub / ESMC, no embeddings, no .npy, no data/output artifact commit, no ready_for_preflight, no manifest runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, no enrichment/contrast rerun, and no biological claim
- G3SX30 manifest-aware dry-run preflight adapter scaffold status: helper-only module in `src/longevity_port_pipelines/stages/g3sx30_manifest_aware_dry_run_preflight_adapter.py`, schema `data/config/g3sx30_manifest_aware_dry_run_preflight_adapter_schema.yaml`, and scaffold row `data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1`; reads and validates `data/input/g3sx30_dry_run_preflight_manifest.csv#1`, returns adapter_status=`manifest_understood_runtime_blocked`, adapter_decision=`do_not_execute_current_cli_directly`, current_cli_compatibility=`not_directly_executable_manifest_mismatch_output_path_issue`, required_next_action=`add_manifest_aware_wrapper_or_guardrail_before_execution`, output_path_policy=`do_not_write_committed_data_output`; no pyproject script entry point, no preflight/single run, no --help run, no Biohub / ESMC, no embeddings, no .npy, no data/output artifact commit, no ready_for_preflight, no manifest runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, no enrichment/contrast rerun, and no biological claim
- G3SX30 manifest-aware adapter policy contract status: machine-readable policy contract in `src/longevity_port_pipelines/stages/g3sx30_manifest_aware_adapter_policy_contract.py`, schema `data/config/g3sx30_manifest_aware_adapter_policy_contract_schema.yaml`, and one concrete policy row `data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1`; sources `data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1`, keeps the old scaffold row unchanged, rejects current CLI direct execution, allows only future wrapper scaffold preparation, keeps wrapper execution/dry-run/live execution/ready_for_preflight/Biohub/ESMC/embedding/artifact decisions `not_authorized`, and points allowed_next_action_after_policy to `prepare_manifest_aware_wrapper_scaffold_pr`; no pyproject script entry point, no manifest-aware wrapper implementation, no wrapper execution, no dry-run execution, no preflight/single run, no --help run, no Biohub / ESMC, no embeddings, no .npy, no data/output artifact commit, no ready_for_preflight, no manifest runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, no enrichment/contrast rerun, and no biological claim
- G3SX30 manifest-aware dry-run wrapper scaffold status: non-executable helper/table scaffold in `src/longevity_port_pipelines/stages/g3sx30_manifest_aware_dry_run_wrapper_scaffold.py`, schema `data/config/g3sx30_manifest_aware_dry_run_wrapper_scaffold_schema.yaml`, and scaffold row `data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1`; sources `data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1`, `data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1`, and `data/input/g3sx30_dry_run_preflight_manifest.csv#1`; records wrapper_status=`wrapper_scaffold_runtime_blocked`, wrapper_decision=`prepare_wrapper_plan_only`, command_selected=`false`, output_path_selected=`false`, execution_plan_materialized=`false`, runtime_still_blocked=`true`, and allowed_next_action_after_wrapper_scaffold=`add_wrapper_command_contract_pr`; no pyproject script entry point, no Typer executable wrapper, no manifest-aware wrapper implementation, no wrapper execution, no dry-run execution, no live execution, no preflight/single run, no --help run, no command selection, no output path selection, no execution plan materialization, no Biohub / ESMC, no embeddings, no .npy, no data/output artifact commit, no ready_for_preflight, no manifest runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, no enrichment/contrast rerun, and no biological claim
- G3SX30 wrapper command contract scaffold status: non-executable helper/table scaffold in `src/longevity_port_pipelines/stages/g3sx30_wrapper_command_contract_scaffold.py`, schema `data/config/g3sx30_wrapper_command_contract_scaffold_schema.yaml`, and scaffold row `data/interim/g3sx30_wrapper_command_contract_scaffold.csv#1`; sources `data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1`, `data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1`, and `data/input/g3sx30_dry_run_preflight_manifest.csv#1`; records command_contract_status=`command_contract_scaffold_runtime_blocked`, command_contract_decision=`define_future_command_contract_only`, expected_command_family=`curated_embedding_preflight_dry_run_wrapper`, actual_cli_help_observed=`false`, actual_command_verified=`false`, command_selected=`false`, output_path_selected=`false`, execution_plan_materialized=`false`, execution_authorized=`false`, wrapper_execution_authorized=`false`, dry_run_execution_authorized=`false`, live_execution_authorized=`false`, ready_for_preflight_authorized=`false`, biohub_esmc_authorized=`false`, embedding_generation_authorized=`false`, npy_artifact_authorized=`false`, data_output_artifact_commit_authorized=`false`, output_path_policy=`do_not_write_committed_data_output`, allowed_output_location_policy=`future_temp_or_manual_reviews_path_only`, unverified_until_help_or_source_guardrail=`true`, future_command_contract_scaffold_only=`true`, runtime_still_blocked=`true`, and allowed_next_action_after_command_contract=`add_wrapper_source_guardrail_pr`; no pyproject script entry point, no Typer executable wrapper, no wrapper execution, no dry-run execution, no live execution, no actual command run, no --help run, no observed-help claims, no actual CLI flag verification claims, no Biohub / ESMC, no embeddings, no .npy, no data/output artifact commit, no ready_for_preflight, no manifest runtime unlock, no Gate 8 / Gate 9, no Boltz/AF3/Chai, no enrichment/contrast rerun, and no biological claim
- G3SX30 official sequence source review preparation status: docs-only checkpoint in `docs/g3sx30_official_sequence_source_review_preparation.md`; requires future official source record review for accession `G3SX30`, database `UniProtKB TrEMBL`, species `Loxodonta africana`, taxid `9785`, gene symbol `MDM2`, expected metadata length `492`, explicit sequence source traceability, stable `reviewed_sequence_sha256`, direct reviewed amino-acid sequence length calculation, direct length comparison, and mismatch handling; no sequence fetch inside the repository, no raw sequence artifact commit, no source provenance row mutation, no decision row mutation, no reviewed sequence approval, no sequence_length_status=`matches`, no Biohub / ESMC, no embeddings, no ready_for_preflight, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- ortholog evidence Gate 4 / Gate 5 policy update validator status: `table_only_no_runtime_side_effects`
- ortholog evidence review decision rows: one G3SX30 reviewed-for-planning provenance row still policy-blocked
- prior G3SX30 handoff actions preserved: raw_metadata_review allowed_next_action_after_review=`prepare_later_source_evidence_intake_pr`; collection allowed_next_action_after_collection=`prepare_later_source_evidence_intake_pr`; collected-source intake allowed_next_action_after_intake=`prepare_later_reviewed_decision_pr`
- ortholog evidence review decision source: collected-source intake row from `data/input/ortholog_evidence_intake.csv#5`
- ortholog evidence review decision result: review_decision=`accepted_for_planning_after_review`, downstream_block_status_after_review=`reviewed_for_planning_still_policy_blocked`, allowed_next_action_after_review=`consider_later_explicit_gate4_gate5_policy_update`
- ortholog evidence review decision validator status: `table_only_no_runtime_side_effects`
- stronger-source lookup policy status: `policy_only_no_live_lookup`
- stronger-source lookup plan table status: `one_row_lookup_plan_still_blocked`
- stronger-source lookup plan rows: one G3SX30 UniProtKB entry metadata lookup plan row
- fixture-backed source client status: `fixture_only_local_synthetic`
- fixture lookup result status: `synthetic_fixture_only_non_evidence`
- live lookup opt-in boundary status: `policy_helper_only_default_denied`
- live metadata client scaffold status: `scaffold_only_injected_provider_no_network`
- live metadata dry-run wrapper status: `runtime_operator_dry_run_fake_provider_only`
- raw metadata response schema status: `schema_only_unreviewed_non_evidence`
- raw metadata response table status: `two_rows_dry_run_and_real_metadata_still_blocked`
- raw metadata response builder status: `in_memory_builder_only`
- raw metadata response builder input: `live_metadata_dry_run_summary_rows_plus_lookup_plan_provenance`
- raw metadata response builder output: `dry_run_derived_raw_metadata_response_rows`
- raw metadata response exporter status: `explicit_table_writer_only`
- raw metadata response review checklist status: `docs_only_human_review_protocol`
- raw metadata human review schema status: `schema_only_no_rows`
- raw metadata human review table status: `one_g3sx30_row_still_blocked`
- raw metadata human review rows: one G3SX30 metadata-only review row
- raw metadata response rows: one G3SX30 dry-run-derived fake/noop non-evidence row; one G3SX30 UniProtKB metadata-only sandbox row requiring manual review
- metadata-only external probe status: one explicit UniProtKB metadata-only manual probe recorded; no sequence fetched; no source evidence created
- downstream block status: `blocked_gate4_gate5`
- claim status: `repair_worklist`

This ladder does not accept or validate an ortholog. It records one explicit UniProtKB metadata-only manual probe and one metadata-only stronger-source collection row, but it does not create a curated ortholog candidate, does not complete source evidence intake/review, does not create a reviewed ortholog decision, does not update Gate 4 / Gate 5 policy, does not promote Gate 8 or Gate 9, does not fetch sequences, does not call Biohub, does not generate embeddings, does not call Boltz, AF3, or Chai, does not rerun enrichment or contrast, and does not make biological claims.



The first G3SX30 ortholog evidence Gate 4 / Gate 5 policy update row is now recorded from the reviewed-decision row. It records policy_update_decision=`approve_gate45_policy_update_for_planning`, but remains downstream_block_status_after_policy=`gate45_policy_updated_still_runtime_blocked` and only allows allowed_next_action_after_policy=`prepare_later_gate_aware_embedding_fill_plan_pr`. It does not fetch sequences, does not call Biohub, does not generate embeddings, does not call Boltz, does not call AF3, does not call Chai, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

The first G3SX30 ortholog evidence reviewed-decision row is now recorded from the collected-source intake row. It records review_decision=`accepted_for_planning_after_review` as reviewed-for-planning provenance evidence, but remains downstream_block_status_after_review=`reviewed_for_planning_still_policy_blocked` and only allows allowed_next_action_after_review=`consider_later_explicit_gate4_gate5_policy_update`. It does not automatically update Gate 4 / Gate 5 policy, does not fetch sequences, does not call Biohub, does not generate embeddings, does not call Boltz, does not call AF3, does not call Chai, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

The first real metadata ingestion sandbox for G3SX30 is now represented by the committed UniProtKB metadata-only sandbox row. The first G3SX30 collected-source intake row is now recorded from the metadata-only stronger-source evidence collection row with intake_outcome=`evidence_ready_for_review_decision`. The first G3SX30 ortholog evidence reviewed-decision row is now recorded from that collected-source intake row with review_decision=`accepted_for_planning_after_review` and downstream_block_status_after_review=`reviewed_for_planning_still_policy_blocked`. The first G3SX30 Gate 4 / Gate 5 policy update row is now recorded as a planning-policy update, still runtime-blocked. The G3SX30 gate-aware embedding fill plan checkpoint is now recorded as docs-only planning context. The first G3SX30 blocked controlled embedding-fill worklist row is now recorded in `data/interim/controlled_embedding_fill_worklist_g3sx30_blocked_checkpoint.csv` with fill_status=`planning_policy_updated_runtime_blocked` and allowed_next_action=`keep_blocked`. The next safe main-track action is a later explicit reviewed dry-run preflight decision or worklist update, not embedding execution: do not fetch sequence, do not call Biohub, do not generate embeddings, do not call Boltz, do not promote Gate 8 or Gate 9, and do not make biological claims. Any later live client must remain blocker-first and must not collect source evidence automatically, accept orthologs, create reviewed decisions, update Gate 4 / Gate 5 policy, promote Gate 8 or Gate 9, fetch sequences by default, call Biohub, generate embeddings, call Boltz, AF3, or Chai, or make biological claims.
