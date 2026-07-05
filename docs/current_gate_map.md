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
- reviewed target sequence provenance rows: one G3SX30 deferred pending-review row in `data/input/reviewed_target_sequence_provenance.csv` with sequence_source_type=`deferred_pending_review`, sequence_length_status=`not_fetched`, sequence_review_status=`deferred_pending_review`, provenance_review_status=`deferred`, allowed_next_action_after_sequence_review=`defer_pending_sequence_review`, no reviewed sequence provenance, no sequence fetch, no Biohub / ESMC, no embeddings, no ready_for_preflight, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
- G3SX30 target sequence review checklist status: docs-only checklist in `docs/g3sx30_target_sequence_review_checklist.md`; requires traceability to `data/input/ortholog_evidence_gate45_policy_updates.csv#1`, identity checks for accession `G3SX30`, database `UniProtKB TrEMBL`, species `Loxodonta africana`, taxid `9785`, gene symbol `MDM2`, explicit sequence artifact/hash checks, reviewed length checking against expected metadata length `492`, mismatch handling, and separate later dry-run preflight decision; no sequence fetch, no reviewed sequence provenance row, no sequence_length_status=`matches`, no Biohub / ESMC, no embeddings, no ready_for_preflight, no Gate 8 / Gate 9, no Boltz/AF3/Chai, and no biological claim
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
