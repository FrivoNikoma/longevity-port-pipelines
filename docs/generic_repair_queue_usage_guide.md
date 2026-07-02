# Generic repair queue usage guide

This guide explains how to run and interpret the generic Gate 4 / Gate 5 repair queue summary.

The summary is a repair worklist. It is not a biological result, not a validation result, and not a downstream modeling decision.

## Command

Run the summary builder with:

uv run generic-repair-queue-summary --output data/interim/generic_repair_queue_summary.csv

The default output path is:

data/interim/generic_repair_queue_summary.csv

This output is a runtime artifact. It should not be committed unless a later PR explicitly adds a reviewed fixture.

## Inputs

The current builder reads two tracked input tables:

data/input/sirt6_candidate_coverage_repair_decisions.csv
data/input/tp53_mdm2_ortholog_repair_decisions.csv

Current committed inputs produce:

11 SIRT6/core3 repair rows
2 TP53/MDM2 elephant repair rows
13 total repair queue rows

## How to read the summary

The summary is centered on three blocker-oriented fields.

### repair_queue_status

This field describes the repair queue state of a row.

Current expected statuses include:

- `blocked_pending_manual_review`
- `blocked_pending_source_ortholog_repair`

Interpretation:

- `blocked_pending_manual_review` means the row needs manual sequence/provenance review before downstream use.
- `blocked_pending_source_ortholog_repair` means the row needs source ortholog fetch or curation before downstream use.

### downstream_block_status

This field describes whether the row is blocked from downstream gates.

Current committed rows are expected to have:

blocked_gate4_gate5

This means the row must not enter Gate 8 contrast, Gate 9 cofolding readiness, live structural compatibility, or decision-package promotion.

### allowed_next_action

This field gives the next safe queue action.

Current expected actions include:

- `manual_sequence_provenance_review`
- `fetch_or_curate_source_ortholog`

These are repair-planning actions only. They do not automatically perform repair.

## Disallowed interpretations

The repair queue summary must not be interpreted as:

- a validated longevity signal
- a validated biological hit
- a confirmed binding change
- a confirmed functional effect
- a validated ortholog table
- permission to run Gate 8 contrast
- permission to run Gate 9 cofolding readiness
- permission to run live structural compatibility calls

## Disallowed runtime actions

The usage guide does not authorize:

- sequence fetch
- manual ortholog curation
- Biohub calls
- embedding generation
- Boltz calls
- enrichment reruns
- contrast reruns
- Gate 8 promotion
- Gate 9 promotion
- biological claims

## Safe workflow

A safe workflow is:

1. Run `generic-repair-queue-summary`.
2. Inspect `repair_queue_status`.
3. Inspect `downstream_block_status`.
4. Use `allowed_next_action` only as a repair-planning hint.
5. Keep downstream gates blocked until explicit ortholog/provenance evidence is reviewed.

The summary is useful because it makes blockers visible. It does not remove those blockers.

## Reviewed-decision overlay

A later checkpoint may provide reviewed repair queue decisions in:

```text
data/input/generic_repair_queue_review_decisions.csv
```

To apply those reviewed decisions as an overlay on the base repair queue summary, run:

```powershell
uv run generic-repair-queue-summary `
  --review-decisions data/input/generic_repair_queue_review_decisions.csv `
  --output data/interim/generic_repair_queue_summary.csv
```

The overlay only consumes already-reviewed decision rows. It does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

For deferred_pending_source review decisions, the row remains blocked at Gate 4 / Gate 5. The overlay records the reviewed decision in the summary without converting reviewed-for-planning provenance evidence into downstream eligibility.
