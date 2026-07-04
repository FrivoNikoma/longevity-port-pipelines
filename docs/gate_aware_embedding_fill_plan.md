# Gate-aware embedding fill plan

This document records the safe plan for filling missing curated embeddings after the Gate 8 / Gate 9 calibration checkpoint.

The goal is to create a reviewed embedding-fill worklist before any additional live Biohub / ESMC calls.

This is a planning checkpoint only. It does not call Biohub, generate embeddings, submit Boltz jobs, or make biological claims.

## Why this plan exists

The repository already has live-capable embedding tools:

- `curated_embedding_preflight`
- `curated_embedding_single`

Those tools are useful, but live embedding generation must stay behind explicit review and `--yes-live`.

After the Gate 8 / Gate 9 calibration checkpoint, the next safe step is not to generate more embeddings immediately. The next safe step is to decide which missing embeddings are eligible for review, which are blocked, and which should be deferred.

## Controlled fill protocol

The reusable controlled embedding fill protocol is recorded in `docs/controlled_embedding_fill_protocol.md`.

That protocol formalizes the Brandt's bat `P09874` live embedding precedent. It keeps live embedding generation behind `curated_embedding_preflight`, `curated_embedding_single` dry-run evidence, `sequence_length_status == matches`, explicit human approval for `--yes-live`, local `.npy` artifact validation, no committed `data/output/` artifacts, no Boltz calls, no enrichment/contrast rerun by default, and no biological claims.

## Gate-aware fill statuses

Use these statuses in embedding-fill review notes and future worklists:

| Status | Meaning |
| --- | --- |
| `ready_for_preflight` | Candidate may enter dry-run embedding preflight. |
| `planning_policy_updated_runtime_blocked` | Candidate has a Gate 4 / Gate 5 planning-policy update, but may not enter embedding dry-run or live fill until a later reviewed worklist/checkpoint explicitly allows it. |
| `needs_coverage_repair` | Ortholog or local coverage evidence is incomplete. |
| `needs_source_provenance_review` | Source sequence/protein identity must be reviewed before any embedding fill. |
| `defer_until_gate8_ready` | Upstream Gate 8 contrast status is not ready. |
| `reviewed_for_single_live_fill` | A single explicit embedding fill may be considered with `--yes-live`. |
| `do_not_fill` | Candidate should not be embedded under current evidence. |

## Minimum review requirements

Before any live embedding fill, a row must have:

- explicit candidate id;
- explicit species;
- explicit protein / UniProt identifier;
- reviewed target sequence;
- reviewed source provenance;
- no unresolved coverage blocker;
- clear reason why this embedding is needed;
- explicit dry-run preflight output;
- explicit human approval to use `--yes-live`.

## Lane-specific interpretation

### SIRT6/core3

SIRT6 is the advanced calibration lane.

Allowed next step:

- build a small reviewed worklist of missing or stale curated embeddings;
- run dry-run preflight first;
- consider only one or a few explicit live fills after review.

Not allowed:

- large batch live embedding generation;
- treating filled embeddings as biological validation;
- using filled embeddings to justify live Boltz calls automatically.

### TP53/MDM2 elephant

TP53/MDM2 remains runtime-blocked for embedding execution.

G3SX30 now has a recorded Gate 4 / Gate 5 planning-policy update in `data/input/ortholog_evidence_gate45_policy_updates.csv#1`:

- `policy_update_decision=approve_gate45_policy_update_for_planning`;
- `downstream_block_status_after_policy=gate45_policy_updated_still_runtime_blocked`;
- `allowed_next_action_after_policy=prepare_later_gate_aware_embedding_fill_plan_pr`;
- `claim_status_after_policy=repair_worklist`.

Allowed next step:

- record a gate-aware embedding-fill planning checkpoint;
- identify that G3SX30 is planning-policy-updated but still runtime-blocked;
- prepare a later reviewed embedding-fill worklist or dry-run preflight plan if needed.

Not allowed:

- sequence fetch;
- live Biohub / ESMC call;
- embedding generation;
- committed `.npy` embedding artifact;
- real Gate 8 contrast attempt;
- Gate 9 or cofolding eligibility;
- Boltz, AF3, or Chai call;
- biological claim.

Recommended status for G3SX30 at this checkpoint:

- `planning_policy_updated_runtime_blocked`.

## G3SX30 checkpoint

The first G3SX30 Gate 4 / Gate 5 planning-policy update is now recorded upstream of this plan.

Source row:

- `data/input/ortholog_evidence_gate45_policy_updates.csv#1`

This checkpoint does not make G3SX30 embedding-ready. It only records that a later gate-aware embedding-fill planning layer may be prepared.

Current G3SX30 embedding-fill interpretation:

- `planning_policy_updated_runtime_blocked`;
- no sequence fetch;
- no Biohub / ESMC call;
- no embedding generation;
- no committed embedding artifact;
- no Gate 8 or Gate 9 promotion;
- no Boltz, AF3, or Chai call;
- no biological claim.

## Biohub / ESMC policy

Live Biohub / ESMC calls are never default behavior.

Any live embedding call must require an explicit opt-in flag such as `--yes-live`, a reviewed row, and a recorded reason.

## Boltz policy

Embedding fill does not imply Boltz readiness.

Boltz remains downstream of:

1. coverage/provenance review;
2. repair decisions;
3. control readiness;
4. strict panel / contrast readiness;
5. Gate 8 contrast policy;
6. Gate 9 cofolding readiness;
7. dry-run manifest review;
8. explicit live opt-in.

## Claim policy

Allowed language:

- embedding-fill plan;
- reviewed worklist;
- dry-run preflight;
- source provenance review;
- coverage repair dependency;
- live embedding opt-in.

Disallowed language:

- validated longevity signal;
- biological hit;
- confirmed functional effect;
- confirmed binding change;
- safe to port;
- proven pro-longevity variant.
