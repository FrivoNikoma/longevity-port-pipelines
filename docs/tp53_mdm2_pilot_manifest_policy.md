# TP53/MDM2 pilot manifest policy

This document defines the first TP53/MDM2 pilot manifest policy.

It generalizes the SIRT6 gate-stack template to the `tp53_mdm2_elephant` candidate set without running the pipeline, fetching orthologs, generating embeddings, submitting Boltz jobs, or making biological claims.

## Candidate set

Configured candidate set:

    tp53_mdm2_elephant

Primary biological mode:

    beneficial_breakage

Core module:

    TP53 / MDM2

Associated candidate-set interpretation:

    Useful interaction weakening or escape may be adaptive.
    Interface shifts should not automatically be treated as incompatibility.

## Purpose

The purpose of this policy is to define how TP53/MDM2 should enter the existing gated workflow.

This PR does not create a new result.

It documents how a future TP53/MDM2 pilot should reuse the SIRT6 gate-stack template:

    candidate coverage decisions
    NEGATOME repair decisions
    strict panel construction
    candidate contrast gate
    gated longevity contrast
    contrast-gated cofolding run plan
    contrast-gated cofolding dry-run manifest

## Biological interpretation policy

TP53/MDM2 differs from the SIRT6 DNA-repair pilot because interaction weakening may be the expected biological direction.

For TP53/MDM2, apparent interface divergence or weakened regulatory binding must not be automatically classified as incompatibility.

Allowed interpretation categories:

    functional_breakage_candidate
    maintained_interaction_candidate
    incompatible_or_unresolved_candidate

The key caution is:

    breakage can be beneficial, neutral, or harmful depending on the partner and context.

For the elephant TP53/MDM2 module, a future dry-run result may prioritize rows where regulatory escape is plausible, but it still cannot validate a biological mechanism.

## Required gate-stack reuse

A future TP53/MDM2 manifest should not bypass the SIRT6 gate-stack template.

Before cofolding dry-run planning, future rows should pass through:

1. Candidate species coverage matrix
2. Candidate coverage repair decision table
3. NEGATOME readiness matrix
4. NEGATOME repair decision table
5. Strict contrast panel builder
6. Candidate contrast gate
7. Gated longevity contrast
8. Contrast-gated cofolding manifest builder

The required gate language should remain:

    eligible_for_contrast_dry_run
    technical_checkpoint_no_claim
    eligible_for_cofolding_dry_run

## Dry-run manifest expectations

A future TP53/MDM2 pilot manifest should preserve:

    candidate_set
    biological_mode
    candidate_id
    pdb_id
    chain
    source_uniprot
    partner_uniprot
    target_species
    strict_contrast_gate_status
    contrast_checkpoint_policy
    cofolding_plan_status
    breakage_interpretation_policy
    claim_policy

The recommended policy values are:

    candidate_set = tp53_mdm2_elephant
    biological_mode = beneficial_breakage
    breakage_interpretation_policy = do_not_auto_classify_breakage_as_incompatibility
    claim_policy = technical_checkpoint_no_claim

## Allowed language

Allowed:

    TP53/MDM2 is a beneficial-breakage pilot candidate set.
    Regulatory escape may be an adaptive hypothesis.
    Interface weakening should not automatically be interpreted as incompatibility.
    This row is eligible for dry-run planning only.
    This is a technical checkpoint, not a validated biological mechanism.

Not allowed:

    Elephant TP53 is validated as a longevity mechanism by this pipeline.
    MDM2 escape is proven by this manifest policy.
    Interface breakage is always beneficial.
    Interface breakage is always incompatibility.
    This candidate is ready for wet-lab claims without additional controls.

## No-live-action guarantees

This policy does not:

- call the Biohub API,
- call the Boltz API,
- fetch orthologs,
- generate embeddings,
- compute enrichment statistics,
- submit cofolding jobs,
- spend Boltz credits,
- create wet-lab claims,
- create biological validation claims.

## Next step

After this policy is reviewed, the next safe implementation step would be a committed TP53/MDM2 pilot manifest or manifest validator that records the candidate-set policy without running live stages by default.
