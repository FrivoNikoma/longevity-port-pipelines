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
