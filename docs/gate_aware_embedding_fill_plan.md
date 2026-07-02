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

## Gate-aware fill statuses

Use these statuses in embedding-fill review notes and future worklists:

| Status | Meaning |
| --- | --- |
| `ready_for_preflight` | Candidate may enter dry-run embedding preflight. |
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

TP53/MDM2 remains a blocked calibration lane.

Allowed next step:

- use embedding-fill planning to identify what remains blocked;
- connect missing embeddings to coverage repair decisions.

Not allowed:

- live embedding fill while coverage remains unresolved;
- real Gate 8 contrast attempt;
- cofolding eligibility;
- biological claim.

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
