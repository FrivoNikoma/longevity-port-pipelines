# Generic candidate lane contract

This document defines what a biological candidate lane must provide in the LongevityPort pipeline.

A candidate lane is a reusable unit of analysis for one biological module, such as SIRT6/DNA repair, TP53/MDM2, HAS2/CD44, IGF/RHEB/mTOR, or AMPK.

The goal is to prevent the repository from becoming a collection of incompatible lane-specific scripts. Each lane may have a different biological interpretation, but it should still pass through the same gated architecture.

## Required lane identity

Every lane must define:

- candidate_set

- biological_mode

- focus genes

- partner genes

- interpretation note

- claim policy

The candidate_set should match the corresponding entry in `data/config/candidate_sets.yaml`.

The biological_mode describes how interface signals should be interpreted. The same numerical result can mean different things in different biological contexts.

Allowed biological modes are:

- maintained_or_enhanced_repair

- beneficial_breakage

- transferable_function

- signaling_rewiring

- hub_risk_review

## Required manifest fields

A lane manifest should identify exact candidate rows before downstream analysis.

Required manifest-level concepts:

- candidate_set

- candidate_id

- pdb_id or structure identifier

- chain

- source_uniprot

- partner_uniprot

- target_species

- biological_mode

- expected_interaction_mode

- desired_interaction_state

- strict_contrast_gate_status

- cofolding_readiness_status

- claim_policy

- notes

The manifest is not a biological claim. It is a structured starting point for coverage, provenance, controls, contrast, and cofolding readiness.

## Coverage and provenance

Every lane must make ortholog and downstream evidence explicit.

Coverage/provenance stages should answer:

- Is the source ortholog available?

- Is the target species represented?

- Is the source database or manual provenance recorded?

- Are local downstream rows present?

- Are missing rows true biological absence or unresolved provenance gaps?

- Should the row be repaired, excluded, or deferred?

Coverage blockers should not be silently ignored. They should become explicit worklist rows.

## Repair decisions

Repair decisions must be explicit and reviewable.

Allowed repair directions include:

- curate_source_ortholog

- fetch_or_curate_source_ortholog

- accept_existing_local_row_after_provenance_review

- exclude_from_strict_panel

- defer_until_stronger_source

- needs_external_manual_sequence_review

A repair decision must not upgrade a row into a biological claim. It only describes how the row should be handled before later gates.

## Control readiness

Every lane should record control readiness before contrast or cofolding interpretation.

Control status should include:

- shuffled control status

- NEGATOME or negative-partner status

- missing control species

- repair decision status

- control claim policy

Rows without adequate controls may still be useful for technical planning, but they should not be promoted to validated biological claims.

## Contrast gate

A candidate may enter long-lived vs short-lived technical contrast only after the relevant gates permit it.

The contrast gate should consider:

- manifest validity

- coverage/provenance status

- strict panel status

- control readiness

- repair decisions

- claim policy

Possible gate outcomes include:

- blocked_contrast_coverage

- blocked_baseline_input

- blocked_species_coverage

- blocked_strict_panel

- blocked_negatome_controls

- eligible_for_contrast_dry_run

A dry-run contrast checkpoint is not a validated longevity signal.

## Cofolding readiness

Cofolding is downstream compatibility planning.

A lane should not use Boltz, AF3, Chai, MD, or chimera design as a discovery shortcut.

Before cofolding readiness, a row should have:

- explicit candidate id

- explicit species context

- source ortholog provenance

- human partner context

- reviewed dry-run inputs

- contrast gate status

- claim policy

Live structural calls must remain opt-in and should be treated as technical compatibility checkpoints.

## Biological-mode-specific interpretation

Architecture should be shared, but interpretation must remain biology-aware.

Examples:

- SIRT6/DNA repair uses maintained_or_enhanced_repair. Interface constraint or compatibility may be promising.

- TP53/MDM2 elephant uses beneficial_breakage. Interface divergence or weakening may be desired regulatory escape.

- HAS2/CD44 uses transferable_function. Extracellular matrix and hyaluronan context are central caveats.

- IGF/RHEB/mTOR uses signaling_rewiring. Hub-risk and network effects are central.

- AMPK uses signaling_rewiring. It is useful for checking that earlier pilot data can be aligned with the generic lane architecture.

## Claim policy

Allowed language before validation:

- technical checkpoint

- dry-run gate

- coverage-aware planning

- repair worklist

- contrast readiness

- cofolding readiness

- candidate for review

Disallowed language before validation:

- validated longevity signal

- validated biological hit

- confirmed binding change

- confirmed functional effect

- safe to port

- proven pro-longevity variant

## Minimal lane lifecycle

A mature lane should eventually pass through:

1. candidate set configuration

2. manifest

3. coverage/provenance preflight

4. repair decisions

5. control readiness

6. strict panel / contrast gate

7. long-lived vs short-lived technical contrast

8. cofolding readiness

9. decision package

## One-sentence contract

A candidate lane may have its own biological interpretation, but it must expose the same gated evidence trail before the project treats it as contrast-ready or cofolding-ready.