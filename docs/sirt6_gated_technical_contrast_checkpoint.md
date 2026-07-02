# SIRT6 gated technical longevity contrast checkpoint

This document defines the first SIRT6 gated technical contrast checkpoint. It also records the generic Gate 8 dry-run wrapper and the safe SIRT6 Gate 9 dry-run path through the shared generic cofolding readiness and dry-run manifest layers.

It is a reproducible dry-run checkpoint around the `longevity-contrast` stage. It is not a biological result, not a validated longevity signal, and not a wet-lab claim.

## Purpose

The legacy checkpoint connects three layers:

1. mapped SIRT6 enrichment rows,
2. candidate contrast gate policy,
3. the gated `longevity-contrast` stage.

The generic Gate 8 dry-run path connects four layers:

1. mapped SIRT6 enrichment rows,
2. candidate contrast gate policy,
3. the SIRT6 generic gated contrast input bridge,
4. the shared generic gated contrast runtime.

The SIRT6 Gate 9 dry-run path then connects four more table-only layers:

1. SIRT6 generic Gate 8 summary rows,
2. SIRT6 Gate 9 cofolding readiness context rows,
3. the shared generic cofolding readiness runtime,
4. the shared generic cofolding dry-run manifest builder.

The stage should only compute long-lived-vs-short-lived technical contrast rows for candidate/chain rows that passed the candidate contrast gate as:

    eligible_for_contrast_dry_run

All other candidate/chain rows remain blocked and should be treated as a repair or review worklist.

## Legacy SIRT6 command

Run from the repository root:

    uv run longevity-contrast `
      --enrichment-input data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet `
      --gate-input data/interim/sirt6_candidate_contrast_gate.csv `
      --output data/output/sirt6_gated_longevity_contrast.csv `
      --blocked-output data/output/sirt6_gated_longevity_contrast_blocked.csv

## Generic Gate 8 dry-run command

Run from the repository root:

    uv run sirt6-generic-gated-contrast `
      --enrichment-input data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet `
      --gate-input data/interim/sirt6_candidate_contrast_gate.csv `
      --generic-input-output data/interim/sirt6_generic_gated_contrast_input.csv `
      --output data/output/sirt6_generic_gated_contrast_summary.csv

## SIRT6 Gate 9 dry-run path

Run from the repository root after the generic Gate 8 summary exists:

    uv run sirt6-cofolding-readiness-context `
      --gate8-summary data/output/sirt6_generic_gated_contrast_summary.csv `
      --output data/interim/sirt6_generic_cofolding_readiness_context.csv

    uv run cofolding-readiness `
      --gate8-summary data/output/sirt6_generic_gated_contrast_summary.csv `
      --cofolding-context data/interim/sirt6_generic_cofolding_readiness_context.csv `
      --output data/interim/sirt6_generic_cofolding_readiness_summary.csv

    uv run cofolding-dry-run-manifest `
      --readiness-summary data/interim/sirt6_generic_cofolding_readiness_summary.csv `
      --output data/interim/sirt6_generic_cofolding_dry_run_manifest.csv `
      --blocked-output data/interim/sirt6_generic_cofolding_dry_run_blocked_manifest.csv

By default, the SIRT6 context builder records:

    cofolding_input_review_status = dry_run_inputs_unreviewed
    live_opt_in_status = live_not_requested

This means the first Gate 9 pass is expected to produce a blocked/review worklist until dry-run inputs are explicitly reviewed.

## Expected outputs

The legacy checkpoint writes two tables:

    data/output/sirt6_gated_longevity_contrast.csv
    data/output/sirt6_gated_longevity_contrast_blocked.csv

The generic Gate 8 dry-run wrapper writes two tables:

    data/interim/sirt6_generic_gated_contrast_input.csv
    data/output/sirt6_generic_gated_contrast_summary.csv

The SIRT6 Gate 9 dry-run path writes three additional planning tables:

    data/interim/sirt6_generic_cofolding_readiness_context.csv
    data/interim/sirt6_generic_cofolding_readiness_summary.csv
    data/interim/sirt6_generic_cofolding_dry_run_manifest.csv

It also writes a blocked/review worklist:

    data/interim/sirt6_generic_cofolding_dry_run_blocked_manifest.csv

### `sirt6_gated_longevity_contrast.csv`

This table contains only candidate/chain rows that passed the candidate contrast gate.

Every row is still a technical checkpoint row only. It should include:

    strict_contrast_gate_status = eligible_for_contrast_dry_run
    contrast_checkpoint_policy = technical_checkpoint_no_claim

### `sirt6_gated_longevity_contrast_blocked.csv`

This table contains candidate/chain rows that did not pass the candidate contrast gate.

Blocked rows are not negative biological results. They are a worklist for coverage repair, strict panel repair, NEGATOME control repair, or NEGATOME repair-policy review.

### `sirt6_generic_gated_contrast_input.csv`

This table adapts SIRT6 enrichment rows and candidate contrast gate rows into the generic Gate 8 input contract.

It is an adoption bridge only. It should not be interpreted as a new biological result.

### `sirt6_generic_gated_contrast_summary.csv`

This table is produced by the shared generic gated contrast runtime.

Every row remains a technical Gate 8 checkpoint row only. Generic robustness annotations are review aids, not biological validation.

### `sirt6_generic_cofolding_readiness_context.csv`

This table records SIRT6-specific partner/provenance/review context for the generic Gate 9 cofolding readiness runtime.

It is a context bridge only. It does not generate cofolding inputs and does not imply that live cofolding is allowed.

### `sirt6_generic_cofolding_readiness_summary.csv`

This table is produced by the shared generic Gate 9 cofolding readiness runtime.

Rows can be ready, blocked, or routed to review. A ready row is still only eligible for dry-run manifest planning, not live structural submission.

### `sirt6_generic_cofolding_dry_run_manifest.csv`

This table contains rows that passed generic Gate 9 dry-run manifest eligibility.

It is not a Boltz input file and does not submit a Boltz job.

### `sirt6_generic_cofolding_dry_run_blocked_manifest.csv`

This table contains blocked or review rows from the generic Gate 9 dry-run manifest builder.

These rows are a worklist for missing context, unreviewed inputs, Gate 8 blockers, claim-policy issues, or manual review.

## Interpretation policy

Allowed language:

    This is a gated technical contrast checkpoint.
    This candidate/chain is eligible for contrast dry-run planning.
    This row remains blocked by the candidate contrast gate.

Not allowed language:

    SIRT6 longevity signal is validated.
    This proves a long-lived species mechanism.
    This proves functional protection or functional damage.
    This is ready for biological interpretation without additional validation.

## No-live-action guarantees

This checkpoint does not make live calls or generate new biological evidence.

It does not:

- call the Biohub API,
- call the Boltz API,
- generate embeddings,
- compute new enrichment statistics,
- submit cofolding jobs,
- make wet-lab or biological validation claims.

## Biological caution

A long-lived-vs-short-lived contrast can be useful as a prioritization signal, but it is not by itself evidence for a validated SIRT6 longevity mechanism.

At this stage, the output means only:

    The candidate passed the configured technical gates and can be reviewed as a technical contrast checkpoint.

Further interpretation would require additional controls, structural review, and eventually experimental or orthogonal validation.

## Next step

After the generic Gate 8 dry-run summary is reviewed, the next roadmap step is a contrast-gated cofolding run plan. That plan should use gated technical contrast rows as inputs, while keeping blocked rows out of live Boltz planning by default.
