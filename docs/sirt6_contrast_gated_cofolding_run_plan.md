# SIRT6 contrast-gated cofolding run plan

This document defines the first contrast-gated cofolding run plan for the SIRT6 workflow.

It is a dry-run planning document only. It does not submit Boltz jobs, does not call the Boltz API, and does not make a biological claim.

## Purpose

The goal is to connect the gated technical contrast checkpoint to future cofolding planning.

The cofolding plan must start from the gated contrast outputs:

    data/output/sirt6_gated_longevity_contrast.csv
    data/output/sirt6_gated_longevity_contrast_blocked.csv

Only rows from the gated contrast table may be considered for cofolding dry-run planning.

Rows from the blocked table are excluded from live cofolding planning by default.

## Required upstream checkpoint

Before any cofolding planning, run the SIRT6 gated technical contrast checkpoint:

    uv run longevity-contrast `
      --enrichment-input data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet `
      --gate-input data/interim/sirt6_candidate_contrast_gate.csv `
      --output data/output/sirt6_gated_longevity_contrast.csv `
      --blocked-output data/output/sirt6_gated_longevity_contrast_blocked.csv

The cofolding run plan should only consume the gated output after this checkpoint has been reviewed.

## Inclusion rule

A candidate/chain row can enter cofolding dry-run planning only if it comes from:

    data/output/sirt6_gated_longevity_contrast.csv

and retains the policy markers:

    strict_contrast_gate_status = eligible_for_contrast_dry_run
    contrast_checkpoint_policy = technical_checkpoint_no_claim

This means the row passed the configured technical gates.

It does not mean the row is biologically validated.

## Exclusion rule

Rows from:

    data/output/sirt6_gated_longevity_contrast_blocked.csv

must not be used for live Boltz planning by default.

Blocked rows are a worklist, not a negative biological result. They may require:

- coverage repair,
- strict panel repair,
- NEGATOME control repair,
- NEGATOME repair-policy review,
- manual structural review.

## Dry-run manifest fields

A future contrast-gated cofolding manifest should preserve the gate and checkpoint context.

Recommended columns:

    candidate_id
    pdb_id
    chain
    source_uniprot
    target_species
    contrast_class
    strict_contrast_gate_status
    contrast_checkpoint_policy
    gate_recommended_next_action
    gate_note
    cofolding_plan_status
    cofolding_plan_note

Allowed planning statuses:

    eligible_for_cofolding_dry_run
    blocked_by_contrast_gate
    blocked_pending_manual_review
    blocked_pending_negatome_repair
    blocked_pending_species_coverage_repair

## Live-action rule

This run plan is not permission to submit live jobs.

Live Boltz submission requires a separate explicit PR or command using an explicit live flag.

Allowed language:

    This candidate is eligible for cofolding dry-run planning.
    This row passed the contrast gate as a technical checkpoint.
    This blocked row remains excluded from live Boltz planning by default.

Not allowed language:

    This candidate should be submitted to Boltz immediately.
    This proves a SIRT6 longevity mechanism.
    This proves a functional species-specific interaction.
    This is a validated biological result.

## No-live-action guarantees

This run plan does not:

- call the Biohub API,
- call the Boltz API,
- generate embeddings,
- compute new enrichment statistics,
- submit cofolding jobs,
- spend Boltz credits,
- make wet-lab or biological validation claims.

## Biological caution

Cofolding can help prioritize structural hypotheses, but it is still not a functional assay.

Even a strong predicted structure would need additional review and validation before making claims about SIRT6 biology, longevity mechanisms, or species-specific functional protection.

At this stage, the cofolding plan means only:

    The candidate passed the configured contrast gates and can be considered for dry-run cofolding planning.

## Next step

After this run plan is reviewed, the next safe implementation step would be a dry-run manifest builder that reads the gated contrast output and writes a cofolding planning manifest without submitting Boltz jobs by default.
