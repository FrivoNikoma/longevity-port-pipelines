# Coverage/provenance repair queue checkpoint

This checkpoint records the current Gate 4 / Gate 5 coverage and provenance repair frontier after the controlled embedding fill governance series.

It is a queue checkpoint, not a biological repair PR.

No ortholog rows are changed here. No sequences are fetched or curated here. No embeddings, contrast, cofolding, Boltz, or biological claims are produced here.

## Current tracked repair queues

### SIRT6/core3

Tracked file:

- `data/input/sirt6_candidate_coverage_repair_decisions.csv`

Current status:

- rows: 11
- `coverage_gap_status`: `missing_ortholog_but_local_rows_present`
- `recommended_coverage_action`: `local_downstream_evidence_without_source_ortholog`
- `repair_decision`: `needs_external_manual_sequence_review`
- `claim_policy`: `deferred_no_claim`

Interpretation:

SIRT6/core3 has local downstream evidence rows for these cases, but source ortholog provenance is missing. These rows require external/manual sequence provenance review before they can be treated as repaired for planning.

Affected source UniProt IDs:

- `P09874`
- `P12956`
- `P13010`
- `Q04206`
- `Q8N6T7`

Affected species include:

- `bowhead_whale`
- `brandts_bat`
- `elephant`

### TP53/MDM2 elephant

Tracked file:

- `data/input/tp53_mdm2_ortholog_repair_decisions.csv`

Current status:

- rows: 2
- `coverage_preflight_status`: `blocked_pending_coverage_repair`
- `source_ortholog_status`: `not_checked`
- `local_candidate_row_status`: `not_checked`
- `recommended_next_action`: `curate_or_fetch_tp53_mdm2_source_ortholog_coverage`
- `repair_decision`: `fetch_or_curate_source_ortholog`
- `repair_priority`: `high`
- `claim_policy`: `ortholog_repair_only`

Interpretation:

TP53/MDM2 elephant is a blocked calibration lane. The TP53 and MDM2 seed rows must not enter real contrast or cofolding eligibility until source ortholog provenance is fetched or manually curated.

## Queue alignment

These two repair queues represent different blocker types:

- SIRT6/core3: local downstream rows exist, but source ortholog provenance is missing.
- TP53/MDM2 elephant: source ortholog coverage has not yet been checked or curated for the seed rows.

Both remain Gate 4 / Gate 5 blockers. They should not be bypassed by embedding fill, contrast, cofolding, or live structural calls.

## Decision

This checkpoint does not select a repaired row.

Allowed language:

- coverage/provenance repair queue
- source ortholog provenance review
- blocked calibration lane
- technical checkpoint
- repair worklist

Disallowed claims and actions:

- no validated longevity signal
- no validated biological hit
- no confirmed binding change
- no confirmed functional effect
- no Biohub call
- no embedding generation
- no Boltz call
- no enrichment or contrast rerun
- no live structural compatibility call
- no decision package promotion

## Next safe actions

Possible next PRs after this checkpoint:

1. Add a generic coverage/provenance repair queue summary builder.
2. Align TP53/MDM2 repair decisions with the generic repair queue vocabulary.
3. Record one manual provenance review checkpoint for a single high-priority row.
4. Keep all downstream gates blocked until repair evidence is explicit.
