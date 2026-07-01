# TP53/MDM2 pilot coverage preflight summary

This document summarizes the current TP53/MDM2 elephant pilot coverage preflight state.

This is a planning-only technical report for the LongevityPort gated pipeline.

It does not make biological validation claims.

## Source inputs

```text
data/input/tp53_mdm2_pilot_manifest.csv
data/input/tp53_mdm2_ortholog_repair_decisions.csv

```

## Generated preflight table

The TP53/MDM2 coverage preflight CLI writes:

```text
data/interim/tp53_mdm2_pilot_coverage_preflight.csv

```

## Command

Run from the repository root:

```powershell
uv run tp53-mdm2-pilot-coverage-preflight

```

This command builds the TP53/MDM2 pilot coverage preflight table from the committed manifest and the committed ortholog repair-decision table.

## Overview

- Candidate set: `tp53_mdm2_elephant`
- Target species: `elephant`
- PDB structure: `1ycr`
- Row count: `2`
- Coverage preflight status: `blocked_pending_coverage_repair`
- Recommended next action: `curate_or_fetch_tp53_mdm2_source_ortholog_coverage`
- Repair decision: `fetch_or_curate_source_ortholog`
- Repair priority: `high`
- Repair claim policy: `ortholog_repair_only`

## Preflight rows


| Candidate ID                         | Chain | Source UniProt | Partner UniProt | Coverage preflight status         | Recommended next action                              | Repair decision                   | Repair priority |
| ------------------------------------ | ----- | -------------- | --------------- | --------------------------------- | ---------------------------------------------------- | --------------------------------- | --------------- |
| `tp53_mdm2_elephant_seed_tp53_chain` | `B`   | `P04637`       | `Q00987`        | `blocked_pending_coverage_repair` | `curate_or_fetch_tp53_mdm2_source_ortholog_coverage` | `fetch_or_curate_source_ortholog` | `high`          |
| `tp53_mdm2_elephant_seed_mdm2_chain` | `A`   | `Q00987`       | `P04637`        | `blocked_pending_coverage_repair` | `curate_or_fetch_tp53_mdm2_source_ortholog_coverage` | `fetch_or_curate_source_ortholog` | `high`          |


## Status interpretation

The TP53/MDM2 elephant pilot lane is still blocked before contrast analysis.

The blocker is source ortholog coverage.

Both manifest rows require source ortholog provenance to be fetched or manually curated before the lane can move toward contrast-gate readiness.

This means cofolding should remain blocked until the coverage preflight and contrast gate are updated from reviewed source ortholog coverage.

## Repair notes

The committed repair-decision rows record that:

- the TP53 elephant pilot row remains blocked until source ortholog provenance is fetched or manually curated
- the MDM2 elephant pilot row remains blocked until source ortholog provenance is fetched or manually curated

These repair decisions are planning-only. They do not assert that the biological contrast is valid.

## Guardrails

This report does not:

- fetch orthologs
- run Biohub
- run Boltz
- generate embeddings
- create cofolding inputs
- submit cofolding jobs
- spend Boltz credits
- change downstream gate decisions
- make biological validation claims

## Recommended next action

Curate or fetch the TP53/MDM2 source ortholog coverage needed for the elephant pilot lane.

After source ortholog provenance is reviewed, re-run the TP53/MDM2 coverage preflight and then re-check the contrast gate before creating any cofolding inputs.