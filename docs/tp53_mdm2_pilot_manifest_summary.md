# TP53/MDM2 pilot manifest summary

This document summarizes the current TP53/MDM2 elephant pilot manifest.

This is a planning-only technical report for the LongevityPort gated pipeline.

It does not make biological validation claims.

## Source manifest

```text
data/input/tp53_mdm2_pilot_manifest.csv

```

## Overview

- Candidate set: `tp53_mdm2_elephant`
- Biological mode: `beneficial_breakage`
- Target species: `elephant`
- PDB structure: `1ycr`
- Row count: `2`
- Current strict contrast gate status: `blocked_contrast_coverage`
- Current cofolding plan status: `blocked_by_contrast_gate`

## Manifest rows


| Candidate ID                         | Chain | Source UniProt | Partner UniProt | Target species | Strict contrast gate status | Cofolding plan status      |
| ------------------------------------ | ----- | -------------- | --------------- | -------------- | --------------------------- | -------------------------- |
| `tp53_mdm2_elephant_seed_tp53_chain` | `B`   | `P04637`       | `Q00987`        | `elephant`     | `blocked_contrast_coverage` | `blocked_by_contrast_gate` |
| `tp53_mdm2_elephant_seed_mdm2_chain` | `A`   | `Q00987`       | `P04637`        | `elephant`     | `blocked_contrast_coverage` | `blocked_by_contrast_gate` |


## Status interpretation

The TP53/MDM2 pilot lane is present as a committed manifest seed, but it is not ready for contrast analysis or cofolding.

The current blocker is contrast coverage.

This means the next technical work should focus on resolving source ortholog coverage and manifest gate readiness before any downstream structural prediction work.

## Policy fields

The current manifest records conservative policy values:

- `contrast_checkpoint_policy`: `technical_checkpoint_no_claim`
- `breakage_interpretation_policy`: `do_not_auto_classify_breakage_as_incompatibility`
- `claim_policy`: `technical_checkpoint_no_claim`

These fields keep the lane in a planning-only status.

## Guardrails

This report does not:

- fetch orthologs
- run Biohub
- run Boltz
- generate embeddings
- create cofolding inputs
- change downstream gate decisions
- make biological validation claims

## Recommended next action

Resolve the TP53/MDM2 contrast coverage blocker before attempting cofolding.

The next safe step is to curate or fetch the source ortholog coverage needed for the TP53/MDM2 elephant pilot lane, then re-run the appropriate coverage preflight and contrast gate checks.