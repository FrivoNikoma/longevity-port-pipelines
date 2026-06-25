# SIRT6/core3-expanded human cofolding baseline shortlist

This note defines a small human-baseline shortlist for the next Boltz
cofolding step after the initial MHC/HLA calibration.

The goal is not to make a cross-species biological claim yet. The goal is
to choose SIRT6/core3-expanded candidate pairs where a human or technical baseline
should be tested before spending Boltz calls on species panels.

## Background

The first live baseline calibration recovered two audited human-human
MHC/HLA PINDER-fragment controls as maintained interactions.

That result shows that the current Boltz cofolding setup can recover
known structural positive controls. However, those controls do not directly
validate SIRT6/core3-expanded biology.

The next biological gate is therefore:

Can Boltz recover a relevant human PINDER-fragment baseline?

Only candidates with a recoverable human baseline should move to
cross-species interpretation.

## Selection criteria

Prioritize candidates that satisfy most of the following:

- candidate comes from the existing SIRT6 core3-expanded workflow
- human or technical baseline is available
- receptor and ligand fragments are not extremely short
- candidate does not have known missing-chain or partner-mismatch issues
- candidate has prior interface/enrichment signal worth following up
- live Boltz run can be done one candidate at a time with explicit id

Avoid interpreting species-level incompatibility unless the matching human
or technical baseline is first recovered.

## Shortlist

### Priority 1: 1nfi A/F

Reason to test:

- NF-kappaB / IkappaBalpha regulatory-interface candidate
- moderate fragment sizes in the current workflow
- previously appeared in the manual-review / controlled follow-up context
- useful first test for whether a regulatory-interface human baseline is recoverable

Recommended next action:

- audit the exact generated cofolding id
- run a dry-run first
- if inputs look correct, run one explicit live baseline only

### Priority 1: 4xhu A/B

Reason to test:

- strong follow-up candidate from the existing controlled cases
- appeared as a controlled-pass signal in the previous validation context
- useful as an early bridge from calibration controls to SIRT6/core3-expanded biology

Recommended next action:

- verify chain annotations and generated id
- prefer this as a second live baseline after 1nfi if the input looks clean

### Priority 2: 7s68 D/C

Reason to test:

- appeared in the SIRT6/core3-expanded candidate workflow
- potentially useful as a compact interface-level probe

Caution:

- shorter fragments make interpretation more fragile
- should not be the first live biological baseline unless higher-priority
  candidates fail preflight

### Priority 3: 8bhv N/I and P/J

Reason to test:

- appeared in previous controlled-fail / interesting-divergence context
- may be useful as a stress test after stronger baselines

Caution:

- very short ligand-side fragment in the current workflow
- lower priority for live spending
- do not use as the first biological baseline

### Deprioritized for first live baseline: 8f86 K/D

Reason:

- older 8f86 rows included ligand-mapping and partner-mismatch concerns
- useful to track, but not a good first live baseline target

## Candidate baseline preflight CLI

Before any live Boltz call, inspect the exact PINDER-fragment baseline input
with the dry-run-only candidate baseline CLI:

```bash
uv run cofolding-candidate-baseline --candidate-id "1nfi__A1_Q04206--1nfi__F1_P25963"
uv run cofolding-candidate-baseline --candidate-id "4xhu__A1_P09874--4xhu__B1_Q9UNS1"
```

This command prepares receptor/ligand fragment sequences and prints their
PDB id, UniProt ids, chain ids, and fragment lengths. It does not create a
Boltz client, does not submit predictions, and does not write runtime output
files.

## Proposed live-run order

1. audit generated ids for 1nfi and 4xhu
2. dry-run 1nfi only
3. if the generated input is clean, run one explicit 1nfi live baseline
4. if 1nfi is maintained or otherwise recoverable, dry-run 4xhu
5. run 4xhu live only if the dry-run input is clean
6. move to species panels only after at least one relevant human baseline is
   recovered

## Interpretation gate

A future species-level cofolding result should be interpreted biologically
only if the matching human or technical baseline is recoverable.

If the human baseline is not recoverable, an incompatible species result is
not strong evidence for biological loss of interaction. It may simply reflect
a poor fragment choice, missing structural context, or an unsuitable Boltz
cofolding setup for that candidate.

## Notes

- Do not commit runtime outputs under data/output/.
- Do not commit signed Boltz structure URLs.
- Spend live Boltz calls one candidate at a time.
- Prefer explicit --control-id or candidate-id style execution over broad
  live panels.

## Candidate ids to audit

- 1nfi__A1_Q04206--1nfi__F1_P25963
- 4xhu__A1_P09874--4xhu__B1_Q9UNS1
- 7s68__D1_P09874--7s68__C1_P09874
- 8f86__K1_Q8N6T7--8f86__D1_P02281
- 8bhv__N1_P12956--8bhv__I1_Q9H9Q4
- 8bhv__P1_P13010--8bhv__J1_Q9H9Q4
