# Core3 validation closure

This document explains the validation-closure workflow for the SIRT6 v2 core3-expanded run.

The goal of the closure step is to connect curated NEGATOME-style negative-control inputs to downstream candidate interpretation artifacts.

Pipeline shape:

```text
curated NEGATOME control pairs
-> NEGATOME input validation
-> optional NEGATOME partner embedding
-> optional NEGATOME ratio patching
-> negative-control audit
-> interaction outcome summary
-> candidate scorecard
-> validation plan
-> validation closure summary

```

This workflow does not create biological validation by itself. It makes the evidence tier explicit and prevents shuffled-control-only rows from being interpreted as fully controlled hits.

## Main entrypoint

Run the end-to-end closure workflow with:

```bash
uv run python -m scripts.run_core3_validation_closure

```

The main script is:

```text
scripts/run_core3_validation_closure.py

```

Use this as the preferred entrypoint when regenerating the validation-closure artifact set for the core3-expanded run.

## Safe local mode

If you do not want to run Biohub embedding or re-patch NEGATOME ratios, use:

```bash
uv run python -m scripts.run_core3_validation_closure --skip-embed --skip-analyze

```

This mode is useful when you only want to verify that existing output tables can still feed the audit, scorecard, validation plan, and closure summary.

## Important inputs

The closure workflow expects the core3-expanded artifacts to already exist.

Key input files include:

```text
data/output/sirt6_mini_pilot_v2_core3_expanded_embedding_signal_summary.csv
data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.csv
data/output/sirt6_mini_pilot_v2_core3_expanded_selection.csv
data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage.csv
data/output/embeddings/

```

The curated NEGATOME-style pair table is written to:

```text
data/interim/negatome_control_pairs.csv

```

Do not treat a scaffold or candidate curation table as populated NEGATOME control evidence. The strict controlled gate only applies when valid NEGATOME control ratios are actually populated in enrichment and audit tables.

## Generated outputs

The closure workflow writes or refreshes the following main outputs:

```text
data/output/sirt6_mini_pilot_v2_core3_expanded_enrichment_mapped.parquet
data/output/sirt6_mini_pilot_v2_core3_expanded_negatome_control_input_validation.csv
data/output/sirt6_mini_pilot_v2_core3_expanded_negative_control_audit.csv
data/output/sirt6_mini_pilot_v2_core3_expanded_interaction_outcome_summary.csv
data/output/sirt6_mini_pilot_v2_core3_expanded_candidate_scorecard.csv
data/output/sirt6_mini_pilot_v2_core3_expanded_validation_plan.csv
data/output/sirt6_mini_pilot_v2_core3_expanded_validation_plan.md
data/output/sirt6_mini_pilot_v2_core3_expanded_validation_closure_summary.md

```

The most convenient final human-readable summary is:

```text
data/output/sirt6_mini_pilot_v2_core3_expanded_validation_closure_summary.md

```

## Component scripts

The closure workflow orchestrates several smaller scripts:

```text
scripts.build_core3_negatome_control_pairs
scripts.validate_negatome_control_inputs
scripts.embed_negatome_control_partners
scripts.patch_core3_negatome_controls
scripts.audit_negative_controls
scripts.classify_interaction_outcomes
scripts.make_mini_pilot_candidate_scorecard
scripts.generate_mini_pilot_validation_plan

```

Use the end-to-end closure script first. Use component scripts only when debugging one specific stage.

## Evidence tiers

The negative-control audit and scorecard distinguish several evidence states.

### controlled_pass

Both shuffled-mask and NEGATOME-style controls are populated, and the row passes the strict control gate.

For divergence-style evidence, the primary enrichment must exceed both controls by the configured margin and pass the directional interface-greater p-value gate.

For constraint-style evidence, the primary enrichment must fall below both controls by the configured margin and pass the directional interface-less p-value gate.

### controlled_fail

Both shuffled-mask and NEGATOME-style controls are populated, but the row does not pass the strict ratio and/or directional p-value gate.

This is not a pipeline failure. It means the signal does not survive the strict controlled interpretation layer.

### preliminary_shuffled_only

The shuffled-mask control is populated, but the NEGATOME-style control is missing.

These rows may still be useful as preliminary candidates, but they should not be described as fully NEGATOME-controlled hits.

### incomplete or missing controls

Rows with missing shuffled controls, missing all controls, invalid zero controls, or other incomplete control states should be treated as incomplete evidence and inspected before interpretation.

## Interpretation rule

Use this conservative rule when communicating results:

```text
controlled_pass
    -> strict controlled candidate

controlled_fail
    -> controlled but rejected / not supported by strict gate

preliminary_shuffled_only
    -> preliminary signal only; do not claim full NEGATOME-controlled evidence

missing or incomplete controls
    -> infrastructure/debugging or curation issue; do not interpret as a validated candidate

```

## Common mistake to avoid

Do not confuse these three states:

```text
NEGATOME-style scaffold exists
curated NEGATOME input table exists
NEGATOME control ratios are populated

```

Only the last state supports strict controlled interpretation.

## Recommended validation commands

Before opening a PR that changes this workflow, run:

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
uv run pytest tests/ -v

```

If you changed only documentation, at minimum run:

```bash
uv run pytest tests/test_negative_controls.py tests/test_negatome_curation.py tests/test_scorecard.py tests/test_validation_plan.py -v

```

## Minimal smoke run

For a local smoke check that avoids remote embedding work:

```bash
uv run python -m scripts.run_core3_validation_closure --skip-embed --skip-analyze

```

Then inspect:

```text
data/output/sirt6_mini_pilot_v2_core3_expanded_validation_closure_summary.md

```

The expected result is not necessarily that many candidates pass. The expected result is that every candidate is assigned an explicit control-aware interpretation tier.
