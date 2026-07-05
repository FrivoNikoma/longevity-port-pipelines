# G3SX30 official sequence source review preparation

This checkpoint documents the preparation requirements for a later possible G3SX30 reviewed target sequence provenance PR.

It does not perform the review itself.

It does not fetch sequences inside the repository, does not commit a raw sequence artifact, does not mutate `data/input/reviewed_target_sequence_provenance.csv`, and does not mutate `data/input/target_sequence_review_decisions.csv`.

## Current committed state

The current committed G3SX30 state remains blocked:

- target accession: `G3SX30`
- accession database: `UniProtKB TrEMBL`
- target species: `Loxodonta africana`
- target taxid: `9785`
- gene symbol: `MDM2`
- expected metadata length from the Gate 4 / Gate 5 policy row: `492`
- source sequence provenance row: `data/input/reviewed_target_sequence_provenance.csv#1`
- target sequence review decision row: `data/input/target_sequence_review_decisions.csv#1`
- current sequence source type: `deferred_pending_review`
- current sequence length status: `not_fetched`
- current sequence review status: `deferred_pending_review`
- current provenance review status: `deferred`
- current sequence review decision: `defer_pending_sequence_review`
- current downstream block status after decision: `sequence_review_deferred_still_blocked`

## Official source record preparation

A later reviewed target sequence provenance PR must be based on an explicit official source record.

The future reviewer must check that the official source record is traceable and reproducible, and that it identifies the intended target:

- accession is exactly `G3SX30`
- accession database is exactly `UniProtKB TrEMBL`
- organism is elephant / `Loxodonta africana`
- taxid is exactly `9785`
- gene symbol is exactly `MDM2`
- record describes the intended MDM2 protein target, not a paralog, unrelated isoform, wrong species record, or fragment-only artifact
- the source record can be re-opened by a later reviewer

This preparation checkpoint does not assert that the official source record has already been reviewed.

## Hash and length preparation

A later reviewed target sequence provenance PR must compute length and hash from the reviewed amino-acid sequence itself.

It must not rely on metadata length alone.

Before any later row can use `sequence_length_status=matches`, a reviewer must record:

- an explicit source reference for the reviewed sequence record or reviewed sequence artifact
- a stable `reviewed_sequence_sha256`
- `reviewed_sequence_length` computed directly from the reviewed amino-acid sequence
- a direct length comparison to expected metadata length `492`
- explicit mismatch handling if the reviewed sequence length or identity does not match expectations

The current preparation checkpoint does not compute a hash, does not compute a length, and does not record `sequence_length_status=matches`.

## Mismatch handling preparation

If the future reviewed source record has an identity mismatch or length mismatch, the row must stay blocked.

Allowed blocked outcomes include:

- `sequence_length_status=mismatch`
- `sequence_review_status=deferred_pending_review`
- `sequence_review_status=rejected_sequence_provenance`
- `provenance_review_status=needs_review`
- `provenance_review_status=rejected`
- `allowed_next_action_after_sequence_review=keep_blocked`
- `allowed_next_action_after_sequence_review=reject_or_exclude_sequence_source`
- `sequence_review_decision=keep_blocked_after_mismatch`
- `sequence_review_decision=reject_sequence_provenance`

A mismatch must not become `reviewed_sequence_provenance`, `sequence_length_status=matches`, or `consider_later_dry_run_preflight_decision_pr`.

## Boundary

This PR is a review-preparation checkpoint only.

It does not approve reviewed sequence provenance.

It does not record `reviewed_sequence_provenance`.

It does not record `sequence_length_status=matches`.

It does not fetch sequences inside the repository.

It does not commit a raw sequence artifact.

It does not mutate `data/input/reviewed_target_sequence_provenance.csv`.

It does not mutate `data/input/target_sequence_review_decisions.csv`.

It does not call Biohub / ESMC.

It does not generate embeddings.

It does not run `curated_embedding_preflight`.

It does not run `curated_embedding_single`.

It does not change the G3SX30 controlled embedding-fill worklist row.

It does not mark anything `ready_for_preflight`.

It does not create or commit `.npy` artifacts.

It does not promote Gate 8 or Gate 9.

It does not call Boltz, AF3, or Chai.

It does not rerun enrichment or contrast.

It does not make biological claims.
