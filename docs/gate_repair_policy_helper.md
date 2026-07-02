# Gate 4 / Gate 5 repair policy helper

This document records the conservative Gate 4 / Gate 5 repair-to-next-gate
policy helper.

The helper is implemented in
`src/longevity_port_pipelines/stages/gate_repair_policy.py`.

## Purpose

The helper interprets one generic repair queue summary row and returns a
policy decision for whether the row can leave Gate 4 / Gate 5.

The initial policy is blocker-first and conservative:

- blocked rows remain blocked;
- deferred reviewed rows remain blocked;
- rejected reviewed rows remain blocked;
- rows needing a second reviewer remain blocked;
- accepted-for-planning rows still require a later explicit Gate 4 / Gate 5
  policy update before any downstream step can treat them as leaving Gate 4 /
  Gate 5.

## Current downstream policy

The helper never grants automatic downstream eligibility.

It always returns:

- `can_leave_gate4_gate5_now = False`
- `gate8_eligible = False`
- `gate9_eligible = False`
- `embedding_ready = False`
- `boltz_ready = False`
- `biological_claim_allowed = False`

For `accepted_for_planning_after_review`, the helper may return
`gate4_gate5_policy_update_allowed = True`, but this only means a later explicit
Gate 4 / Gate 5 policy update can be considered. It does not mean automatic
Gate 8 / Gate 9 promotion.

## Guardrails

This helper is pure and table-only.

It does not fetch sequences, does not curate orthologs, does not call Biohub,
does not generate embeddings, does not call Boltz, does not rerun enrichment or
contrast, does not promote Gate 8 or Gate 9, and does not make biological
claims.
