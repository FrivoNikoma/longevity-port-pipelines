# G3SX30 blocked embedding-fill exit criteria

## Purpose

This document records the review criteria that must be satisfied before a later PR can
consider moving the G3SX30 controlled embedding-fill row out of its current blocked
state.

This is a docs-only review protocol. It does not change the committed G3SX30 row and
does not run any embedding-fill workflow.

## Current committed state

The current blocked G3SX30 controlled embedding-fill row is recorded in:

- `data/interim/controlled_embedding_fill_worklist_g3sx30_blocked_checkpoint.csv`

The row is sourced from:

- `data/input/ortholog_evidence_gate45_policy_updates.csv#1`

The current row remains:

- `fill_status=planning_policy_updated_runtime_blocked`
- `allowed_next_action=keep_blocked`
- `dry_run_required=false`
- `max_live_batch_size=0`
- `sequence_length_status=not_fetched`
- `embedding_path=not_applicable_runtime_blocked`
- `embedding_status=not_generated_runtime_blocked`
- `claim_status=technical_checkpoint`

This means G3SX30 is machine-readable in the controlled embedding-fill layer but is
still runtime-blocked.

## Non-exit signals

The following are not sufficient to exit the blocked state:

- a metadata-only UniProtKB row
- a raw metadata response row
- a stronger-source collection row
- a reviewed-for-planning provenance decision by itself
- a Gate 4 / Gate 5 planning-policy update by itself
- a blocked controlled embedding-fill worklist row by itself
- `target_sequence_length=492` without a reviewed target sequence artifact
- `sequence_length_status=not_fetched`
- an ordinary preflight row emitted without explicit policy context
- a desire to spend compute credits

None of those signals make G3SX30 embedding-ready, Gate 8 eligible, Gate 9 eligible,
Boltz-ready, or claim-ready.

## Required exit criteria for a later dry-run preflight decision

A later PR may only consider moving G3SX30 toward a dry-run preflight decision if it
records all of the following, explicitly and reviewably:

1. The source link to `data/input/ortholog_evidence_gate45_policy_updates.csv#1`
   remains preserved.
2. The current blocked row in `data/interim/controlled_embedding_fill_worklist_g3sx30_blocked_checkpoint.csv` remains traceable.
3. A reviewed target sequence provenance artifact exists for G3SX30.
4. The reviewed target sequence source, accession, species, taxid, and length are
   recorded.
5. The reviewed sequence length check records `sequence_length_status=matches`.
6. The later PR explicitly states whether it is only a dry-run preflight decision.
7. The later PR keeps live Biohub / ESMC calls disabled by default.
8. The later PR keeps `curated_embedding_single` and any live fill out of scope unless
   a still-later human-approved live-fill PR explicitly allows it.
9. The later PR preserves no Gate 8 promotion, no Gate 9 promotion, no Boltz readiness,
   and no biological claim.

If any of those criteria are missing, the row must remain:

- `fill_status=planning_policy_updated_runtime_blocked`
- `allowed_next_action=keep_blocked`

## Allowed later outcomes

A later reviewed PR may choose one of these outcomes:

- keep G3SX30 blocked with `allowed_next_action=keep_blocked`
- record a reviewed dry-run preflight decision only, while still forbidding live fill
- defer pending more sequence/provenance review
- reject or exclude the row if provenance fails review

A dry-run preflight decision is still not a live embedding fill decision.

## Forbidden in this checkpoint

This checkpoint does not:

- change the G3SX30 worklist row to `ready_for_preflight`
- change the G3SX30 worklist row to `reviewed_for_single_live_fill`
- run `curated_embedding_preflight`
- run `curated_embedding_single`
- fetch sequences
- call Biohub / ESMC
- generate embeddings
- create or commit `.npy` artifacts
- promote Gate 8
- promote Gate 9
- call Boltz, AF3, or Chai
- rerun enrichment or contrast
- make biological claims

## Claim policy

The maximum claim status for this checkpoint is `technical_checkpoint`.

Allowed language:

- blocked embedding-fill row
- exit criteria
- dry-run preflight decision criteria
- reviewed target sequence provenance required
- keep blocked until explicit later review

Disallowed language:

- validated longevity signal
- validated biological hit
- confirmed binding change
- confirmed functional effect
- safe to port
- proven pro-longevity variant
