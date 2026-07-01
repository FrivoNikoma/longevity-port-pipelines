# Current LongevityPort gate map

This document tracks the current state of the LongevityPort gated decision pipeline.

It is intentionally conservative. A gate can be useful even when it blocks a candidate, because blocked rows become an explicit repair, exclude, or defer worklist.

## Gate summary

| Gate | Purpose | Current status |
| --- | --- | --- |
| Gate 0 - candidate sets configured | Candidate modules exist with biological modes. | Partly done. SIRT6, TP53/MDM2, HAS2/CD44, IGF/RHEB/mTOR, and AMPK are represented as candidate sets. |
| Gate 1 - candidate lane contract | Define what every biological lane must provide. | Not done. Next roadmap PR should document the generic lane contract. |
| Gate 2 - lane registry | Register all lanes in one machine-readable format. | Not done. Needed before broad generalization. |
| Gate 3 - manifest | Explicit candidate rows exist for a lane. | Done for SIRT6; started for TP53/MDM2; pending for HAS2/CD44, IGF/RHEB/mTOR, and AMPK in the new architecture. |
| Gate 4 - coverage/provenance | Ortholog and local downstream evidence are explicit. | Advanced for SIRT6; started for TP53/MDM2; pending for other lanes. |
| Gate 5 - repair decisions | Coverage/provenance blockers are classified as repair/exclude/defer. | Advanced for SIRT6; started for TP53/MDM2; pending for other lanes. |
| Gate 6 - control readiness | Shuffled and NEGATOME/control status are explicit. | Advanced for SIRT6; not yet generic. |
| Gate 7 - strict panel / contrast gate | Decide whether a candidate may enter technical contrast. | Advanced for SIRT6; not yet generic. |
| Gate 8 - long-lived vs short-lived contrast | Compute technical contrast under gate policy. | Implemented as a SIRT6 technical checkpoint; generic calculator still pending. |
| Gate 9 - cofolding readiness | Produce contrast-gated cofolding planning rows. | Implemented for SIRT6 planning; generic readiness checklist pending. |
| Gate 10 - live structural compatibility | Submit live structural calls only after explicit opt-in and review. | Not part of default pipeline. Must remain opt-in. |
| Gate 11 - decision package | Summarize candidate status, allowed claims, forbidden claims, and next action. | Not done. |
| Gate 12 - additional biological lanes | Add HAS2/CD44, IGF/RHEB/mTOR, AMPK, and future modules with real biological data. | Pending. |

## Current interpretation

The project has moved from a SIRT6-only coverage-repair phase into a multi-lane gate architecture phase.

Current calibration lanes:

- SIRT6/core3:
  - first calibration lane
  - most advanced gate stack
  - technical contrast checkpoint exists
  - not a validated biological claim

- TP53/MDM2 elephant:
  - second calibration lane
  - useful because biological_mode = beneficial_breakage
  - coverage/provenance repair lane has started
  - not yet at SIRT6-level gate maturity

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

Boltz is a downstream compatibility classifier.

It should not be used as a discovery shortcut.

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
