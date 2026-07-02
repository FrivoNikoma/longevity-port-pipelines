# Ortholog evidence intake checklist

This checklist defines a conservative intake protocol for accession-level ortholog evidence.

It also records how to intake accession-level
ortholog evidence before a Gate 4 / Gate 5 repair-queue row can be considered
for a later reviewed-for-planning provenance decision.

The checklist is an intake checkpoint only. It does not add new reviewed
decisions, does not accept new target orthologs, and does not change downstream
eligibility.

## Purpose

The purpose of this checklist is to make future ortholog evidence intake
traceable before adding or updating machine-readable reviewed provenance
decisions.

The checklist applies after a row has been identified as a Gate 4 / Gate 5
repair-queue worklist item and before any later PR records stronger
accession-level evidence.

This checklist supports later review decisions such as:

- `accepted_for_planning_after_review`
- `rejected_after_review`
- `deferred_pending_source`
- `needs_second_reviewer`

A reviewer may use the checklist to decide whether a row has enough evidence to
support a later explicit Gate 4 / Gate 5 policy update. It does not itself
authorize that update.

## Required row identity fields

For every evidence intake note, record the row identity before reviewing any
external evidence:

- `candidate_set`
- `lane_name`
- `candidate_id`
- `source_table`
- `source_row_index`
- `gene_symbol`
- `source_species`
- `target_species`
- `target_species_taxid`
- `source_uniprot`
- `partner_uniprot`
- `target_uniprot_before_review`
- `coverage_status_before_review`
- `provenance_status_before_review`
- `repair_queue_status_before_review`
- `downstream_block_status_before_review`
- `allowed_next_action_before_review`
- `claim_policy_before_review`

If any field is unavailable, record it as unresolved or unavailable rather than
silently inferring it.

## Minimum accession-level evidence fields

For each candidate ortholog evidence item, record:

- evidence source type
- source database
- source accession or stable identifier
- target taxid
- target species name
- target gene or protein symbol
- target protein accession, when available
- sequence length, when available
- evidence URI or reproducible lookup note
- reviewer note
- ambiguity flag
- whether a second reviewer is required

The key requirement is accession-level traceability. A species name alone, a
gene symbol alone, or a local filename alone is not sufficient.

## Acceptable evidence source types

Acceptable sources are sources that let a reviewer trace a proposed target
ortholog to a concrete accession, stable identifier, species, and taxid.

Examples:

- reviewed UniProt entry
- UniProt ortholog or taxonomy evidence
- NCBI protein or gene record
- Ensembl orthology evidence
- OMA orthology evidence
- OrthoDB orthology evidence
- primary literature with accession-level evidence
- project curated table with source accession and reviewer note

A project curated table is acceptable only when it includes explicit source
accession-level evidence and a reviewer note. It is not acceptable as a vague
local cache or filename.

## Unacceptable evidence source types

The following evidence types are not sufficient by themselves:

- model output without accession-level provenance
- embedding similarity alone
- sequence similarity without species or taxid provenance
- LLM generated assertion without external source evidence
- filename or local cache path without source provenance
- candidate name without accession evidence
- downstream enrichment result
- Boltz, AF3, Chai, or cofolding result
- biological narrative without source accession evidence

These may be useful context, but they cannot resolve a Gate 4 / Gate 5
provenance blocker by themselves.

## Intake outcomes

Evidence intake should end in one of four conservative outcomes:

- `evidence_ready_for_review_decision`
- `evidence_insufficient_defer`
- `evidence_conflict_reject_or_exclude`
- `evidence_ambiguous_needs_second_reviewer`

These are intake outcomes, not downstream permissions.

Mapping to reviewed-decision language should be done in a later reviewed
decision PR:

- `evidence_ready_for_review_decision` may support
  `accepted_for_planning_after_review`
- `evidence_insufficient_defer` may support `deferred_pending_source`
- `evidence_conflict_reject_or_exclude` may support `rejected_after_review`
- `evidence_ambiguous_needs_second_reviewer` may support
  `needs_second_reviewer`

## Downstream guardrails

This checklist does not fetch sequences, does not curate orthologs automatically
automatically, does not call Biohub, does not generate embeddings, does not call
Boltz, does not rerun enrichment or contrast, does not promote Gate 8, does not
promote Gate 9, and does not make biological claims.

Even evidence that appears ready for a later reviewed decision does not mean:

- validated ortholog
- validated longevity signal
- validated biological hit
- confirmed binding change
- confirmed functional effect
- Gate 8 eligible
- Gate 9 eligible
- embedding ready
- Boltz ready
- safe to port
- proven pro-longevity variant

Allowed language is limited to:

- ortholog evidence intake
- accession-level evidence review
- reviewed-for-planning provenance evidence
- Gate 4 / Gate 5 blocker review
- later explicit Gate 4 / Gate 5 policy update

## Current lane use

The immediate use case is to prepare future manual evidence review for:

- SIRT6/core3 repair rows
- TP53/MDM2 elephant repair rows

For TP53/MDM2, this checklist is especially important because the lane may later
test beneficial-breakage logic. This checklist does not evaluate that hypothesis.
It only defines how accession-level elephant TP53 or MDM2 ortholog evidence
should be recorded before a future reviewed-decision PR.

## Explicit guardrail phrase anchors

Each intake row remains a Gate 4 / Gate 5 repair-queue worklist item until a later reviewed-decision PR and explicit Gate 4 / Gate 5 policy update say otherwise.

This checklist does not fetch sequences, does not curate orthologs automatically, does not call Biohub, does not generate embeddings, does not call Boltz, does not rerun enrichment or contrast, does not promote Gate 8, does not promote Gate 9, and does not make biological claims.
