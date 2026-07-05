# G3SX30 target sequence review checklist

This checklist defines the human-review requirements that must be satisfied before any later PR can consider moving the G3SX30 target sequence provenance row from `deferred_pending_review` to `reviewed_sequence_provenance`.

The current committed state remains blocked:

- `sequence_source_type=deferred_pending_review`
- `reviewed_sequence_length=0`
- `sequence_length_status=not_fetched`
- `sequence_review_status=deferred_pending_review`
- `provenance_review_status=deferred`
- `allowed_next_action_after_sequence_review=defer_pending_sequence_review`
- `claim_status=repair_worklist`

This document is a checklist only. It does not fetch sequences, does not add or replace the G3SX30 sequence provenance row, does not record `sequence_length_status=matches`, does not call Biohub / ESMC, does not generate embeddings, does not run `curated_embedding_preflight`, does not run `curated_embedding_single`, does not promote Gate 8 or Gate 9, does not call Boltz, AF3, or Chai, and does not make biological claims.

## Source row that must remain traceable

Any later reviewed sequence provenance PR must remain traceable to:

- source table: `data/input/ortholog_evidence_gate45_policy_updates.csv`
- source row index: `1`
- candidate set: `tp53_mdm2_elephant`
- lane name: `tp53_mdm2_elephant`
- candidate id: `tp53_mdm2_elephant_seed_mdm2_chain`

The source policy row records G3SX30 as a Gate 4 / Gate 5 planning-policy update that is still runtime-blocked. A reviewed target sequence provenance row may support a later dry-run preflight decision PR, but it must not itself run preflight, generate embeddings, or promote Gate 8 / Gate 9.

## Required identity checks

Before any later PR can mark the G3SX30 target sequence provenance row as reviewed, a human reviewer must check all identity fields:

- target accession is exactly `G3SX30`
- accession database is exactly `UniProtKB TrEMBL`
- target species is elephant / `Loxodonta africana`
- target taxid is exactly `9785`
- gene symbol is exactly `MDM2`
- source sequence record describes the intended elephant MDM2 target, not a paralog, fragment-only artifact, unrelated isoform, or wrong species record

If any identity field does not match, the later row must not use `reviewed_sequence_provenance`.

## Required sequence artifact checks

A later reviewed row must not rely on metadata length alone. It must point to a concrete reviewed sequence artifact or reviewed external sequence record.

Before setting `sequence_review_status=reviewed_sequence_provenance`, a human reviewer must check:

- the sequence source reference is explicit and reproducible
- the reviewed sequence artifact or external record can be re-opened
- the sequence is amino-acid/protein sequence data for the target record
- the reviewed sequence has a stable hash recorded in `reviewed_sequence_sha256`
- `reviewed_sequence_length` is computed from the reviewed sequence itself
- `reviewed_sequence_length` matches the expected metadata length
- `sequence_length_status=matches` is only used after the sequence artifact length has been checked directly

The currently known expected metadata length from the Gate 4 / Gate 5 policy row is `492`, but that value alone is not a reviewed sequence artifact.

## Required mismatch handling

If a future reviewed sequence artifact does not match the expected target identity or expected length, the row must stay blocked.

Allowed blocked outcomes include:

- `sequence_length_status=mismatch`
- `sequence_review_status=deferred_pending_review`
- `sequence_review_status=rejected_sequence_provenance`
- `provenance_review_status=needs_review`
- `provenance_review_status=rejected`
- `allowed_next_action_after_sequence_review=keep_blocked`
- `allowed_next_action_after_sequence_review=reject_or_exclude_sequence_source`

A mismatch must not be converted into `consider_later_dry_run_preflight_decision_pr`.

## Required next-action boundary

Even if a later PR records reviewed target sequence provenance with `sequence_length_status=matches`, that PR must still remain separate from dry-run embedding preflight.

The strongest allowed next action after a valid reviewed sequence provenance row is:

- `allowed_next_action_after_sequence_review=consider_later_dry_run_preflight_decision_pr`

That next action means only that a later PR may consider a dry-run preflight decision. It does not authorize live calls or embedding generation.

## Forbidden actions for this checklist layer

This checklist does not authorize:

- sequence fetch
- Biohub calls
- ESMC calls
- embedding generation
- `curated_embedding_preflight`
- `curated_embedding_single`
- data/output commits
- `.npy` artifacts
- Gate 8 eligibility
- Gate 9 eligibility
- Boltz calls
- AF3 calls
- Chai calls
- enrichment rerun
- contrast rerun
- biological claims

## Allowed language

Use these phrases for this layer:

- target sequence review checklist
- human-review requirements
- sequence provenance pending review
- sequence not fetched
- sequence length not checked
- deferred pending review
- still blocked pending explicit later sequence review
- dry-run preflight remains a separate later decision

## Disallowed language

Do not describe this checklist as:

- reviewed sequence provenance
- sequence fetched
- sequence length matched
- embedding ready
- Biohub ready
- ESMC ready
- ready for preflight
- Gate 8 eligible
- Gate 9 eligible
- Boltz ready
- AF3 ready
- Chai ready
- validated longevity signal
- validated biological hit
- confirmed binding change
- confirmed functional effect
- safe to port
- proven pro-longevity variant
