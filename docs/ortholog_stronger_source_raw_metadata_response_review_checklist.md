# Ortholog stronger-source raw metadata response review checklist

This checklist defines how a human reviewer should inspect stronger-source raw metadata response rows before any later source evidence intake.

It is a docs-only governance checkpoint. It does not add a review schema, does not add a review table, does not add source evidence rows, does not create reviewed ortholog decisions, does not update Gate 4 / Gate 5 policy, does not promote Gate 8 or Gate 9, does not call Biohub, does not generate embeddings, does not call Boltz, AF3, or Chai, and does not make biological claims.

## Purpose

The purpose of this checklist is to make raw metadata response review explicit before the first real metadata ingestion sandbox.

A reviewer uses this checklist to decide whether one raw metadata response row is ready to be considered later for source evidence intake.

This checklist does not itself create source evidence. It only defines the human-review protocol that must happen before any later machine-readable source evidence intake PR.

## Scope

This checklist applies to rows matching the stronger-source raw metadata response contract:

- data/config/ortholog_stronger_source_raw_metadata_response_schema.yaml
- data/input/ortholog_stronger_source_raw_metadata_responses.csv
- src/longevity_port_pipelines/stages/ortholog_stronger_source_raw_metadata_response.py

Current raw metadata response rows may be dry-run-derived fake/noop artifacts. Those rows are not real external database metadata.

A future real metadata ingestion sandbox may add metadata-only rows, but those rows must remain unreviewed, non-evidence, blocked, and outside downstream gate promotion until a later reviewed process says otherwise.

## Required row identity fields

For every raw metadata response review note, record the row identity before interpreting the metadata:

- candidate_set
- lane_name
- candidate_id
- request_table
- request_source_row_index
- gene_symbol
- source_species
- target_species
- target_species_taxid
- source_uniprot
- partner_uniprot
- requested_evidence_source_database
- requested_evidence_source_accession
- planned_lookup_source_type
- planned_lookup_source_name
- planned_lookup_query_identifier
- planned_lookup_query_taxid
- live_lookup_policy_decision
- dry_run_status
- dry_run_provider_mode
- raw_metadata_status
- raw_metadata_response_status
- raw_metadata_review_status
- raw_metadata_source_type
- raw_metadata_source_name
- raw_metadata_source_identifier
- raw_metadata_payload_ref

If any field is unavailable, record it as unresolved or unavailable rather than silently inferring it.

## Metadata review questions

For each raw metadata response row, the reviewer should answer:

1. Which candidate lane and source request does this row trace back to?
2. Is this row dry-run-derived fake/noop metadata or real external metadata?
3. Which source type and source name produced the metadata?
4. Does the metadata source match the requested evidence source?
5. Does the metadata identify the expected species and taxid?
6. Does the metadata identify the expected gene or protein?
7. Does the metadata identify the expected accession or stable identifier?
8. Is sequence length reported, unresolved, or conflicting?
9. Does the metadata conflict with the requested target species, taxid, gene, or accession?
10. Does the row require a second reviewer before source evidence intake?
11. Which downstream gates remain blocked after this review?

## Dry-run-derived metadata guardrail

Dry-run-derived raw metadata response rows must remain explicit fake/noop artifacts.

A dry-run-derived row must not be treated as real external database metadata, even if it has a valid raw metadata response shape.

The reviewer must confirm that dry-run-derived rows remain explicit through:

- raw_metadata_source_type
- raw_metadata_payload_ref
- raw_metadata_summary
- reviewer_note

Required interpretation:

- dry-run-derived raw metadata response != real external database metadata
- dry-run-derived raw metadata response != source evidence
- dry-run-derived raw metadata response != reviewed ortholog decision
- dry-run-derived raw metadata response != Gate 4 / Gate 5 policy update
- dry-run-derived raw metadata response != Gate 8 or Gate 9 input
- dry-run-derived raw metadata response != biological claim

## Acceptable metadata sources for later review

Acceptable metadata sources are sources that can potentially support later source evidence intake after review.

Examples:

- reviewed UniProt entry metadata
- NCBI protein or gene record metadata
- Ensembl orthology metadata
- OMA orthology metadata
- OrthoDB orthology metadata
- primary literature metadata with accession-level trace
- other manual source metadata with accession-level trace

These sources are still only raw metadata at this stage. They do not become source evidence until a later source evidence intake artifact records them as such.

## Unacceptable metadata interpretations

The following must not be treated as source evidence by themselves:

- dry-run fake/noop provider output
- model output without accession-level provenance
- embedding similarity alone
- sequence similarity without species or taxid provenance
- LLM-generated assertion without external source evidence
- filename or local cache path without source provenance
- downstream enrichment result
- Boltz, AF3, Chai, or cofolding result
- biological narrative without source accession evidence

These may be useful context, but they cannot resolve a Gate 4 / Gate 5 provenance blocker by themselves.

## Review outcomes

A raw metadata response review should end with one of these conservative human-readable outcomes:

- raw_metadata_ready_for_source_evidence_intake_later
- raw_metadata_insufficient_keep_blocked
- raw_metadata_conflict_keep_blocked_or_exclude_later
- raw_metadata_ambiguous_needs_second_reviewer
- dry_run_metadata_non_evidence_keep_blocked

These are review outcomes only. They are not downstream permissions.

A later PR may define a machine-readable review schema or source evidence intake artifact, but this checklist does not create either one.

## Downstream guardrails

A raw metadata response review does not mean:

- source evidence created
- manual review row created
- reviewed ortholog decision created
- validated ortholog
- accepted ortholog
- Gate 4 / Gate 5 policy updated
- Gate 8 eligible
- Gate 9 eligible
- embedding ready
- Boltz ready
- safe to port
- biological claim

Allowed language is limited to:

- raw metadata response review
- metadata-only review
- source evidence intake candidate
- Gate 4 / Gate 5 blocker remains blocked
- unreviewed non-evidence metadata
- dry-run-derived non-evidence metadata

## Immediate use case

The immediate use case is to prepare the next main-track PR:

Add first real metadata ingestion sandbox for G3SX30.

That future PR should remain:

- one row only
- G3SX30 only
- metadata only
- explicit live opt-in
- no sequence fetch
- no source evidence auto-creation
- no reviewed decision
- no Gate 4 / Gate 5 update
- no Gate 8 / Gate 9
- no embeddings
- no Boltz
- no biological claim

## Explicit guardrail phrase anchors

Raw metadata is not source evidence.

Dry-run-derived raw metadata response rows are not real external database metadata.

Each raw metadata response row remains blocked at Gate 4 / Gate 5 until a later reviewed-decision PR and explicit Gate 4 / Gate 5 policy update say otherwise.

This checklist does not fetch sequences, does not create source evidence, does not create manual review rows, does not create reviewed ortholog decisions, does not update Gate 4 / Gate 5, does not promote Gate 8, does not promote Gate 9, does not call Biohub, does not generate embeddings, does not call Boltz, AF3, or Chai, and does not make biological claims.
