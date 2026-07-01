# Generic lane manifest summary CLI

This document describes the generic lane manifest summary CLI.

The CLI validates a generic lane manifest CSV and writes a planning-only Markdown status summary.

It is intended as a local reporting command for the manifest layer of the LongevityPort gated pipeline.

## Command

Run from the repository root:

```powershell
uv run python -m longevity_port_pipelines.stages.lane_manifest `
  data/interim/generic_lane_manifest_seed.csv `
  --output-path reports/lane_manifest_status_summary.md

```

The command performs the following steps:

1. Reads the lane manifest CSV.
2. Loads the generic lane manifest schema.
3. Loads the candidate lane registry.
4. Validates the manifest against the schema and registry.
5. Writes a Markdown status summary.

## Optional paths

By default, the CLI uses the committed generic lane manifest schema and candidate lane registry.

You can override them explicitly:

```powershell
uv run python -m longevity_port_pipelines.stages.lane_manifest `
  data/interim/generic_lane_manifest_seed.csv `
  --output-path reports/lane_manifest_status_summary.md `
  --schema-path data/config/lane_manifest_schema.yaml `
  --candidate-lanes-path data/config/candidate_lanes.yaml

```

## Output

The Markdown report includes:

- row count
- lane names
- candidate sets
- manifest status counts
- claim status counts
- lane-name counts
- candidate-set counts
- planning-only row count
- validation-required row count

The report is a technical planning artifact. It does not make biological validation claims.

## Guardrails

This CLI is a local reporting command only.

It does not:

- fetch orthologs
- run Biohub
- run Boltz
- generate embeddings
- create cofolding inputs
- change downstream gate decisions
- make biological validation claims

## Pipeline position

This CLI sits after the generic lane manifest schema and validator.

The intended flow is:

```text
manifest CSV
→ generic lane manifest validator
→ status summary
→ Markdown report

```

This keeps manifest reporting reproducible before connecting the manifest layer to concrete lane workflows or downstream gates.