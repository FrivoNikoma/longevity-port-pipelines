# Generic repair queue review checklist

This checklist defines how a human reviewer should inspect rows from the generic Gate 4 / Gate 5 repair queue before any row can be treated as reviewed-for-planning provenance evidence.

The repair queue is a blocker-first worklist. An unreviewed row is not an invalid row and is not a failed candidate. It is a valid blocked repair-queue item that keeps downstream gates blocked until provenance evidence is reviewed.

This checklist is a docs-only governance checkpoint. It does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

## Purpose

The purpose of this checklist is to make Gate 4 / Gate 5 provenance review explicit and reproducible.

A reviewer uses this checklist to decide whether one concrete repair queue row can move from:

```text
unreviewed Gate 4 / Gate 5 blocker
```

to:

```text
reviewed-for-planning provenance evidence
```

A reviewed row may support a later explicit Gate 4 / Gate 5 policy update. It does not automatically authorize downstream analysis.

## Scope

This checklist applies to rows produced from the current generic repair queue inputs:

```text
data/input/sirt6_candidate_coverage_repair_decisions.csv
data/input/tp53_mdm2_ortholog_repair_decisions.csv
```

The current committed repair queue is expected to contain:

```text
11 SIRT6/core3 repair rows
2 TP53/MDM2 elephant repair rows
13 total repair queue rows
```

The checklist can be reused for future lanes, but it should not be interpreted as permission to expand biological lanes, run embeddings, run cofolding, or make claims.

## Required row identifiers

For each reviewed row, the reviewer must record enough identifiers to make the review traceable.

Required identifiers:

```text
candidate_set
candidate_id
lane_name
source_table
source_row_index
gene_symbol
source_species
target_species
target_species_taxid
source_uniprot
target_uniprot_before_review
partner_uniprot
coverage_status_before_review
provenance_status_before_review
repair_queue_status_before_review
downstream_block_status_before_review
allowed_next_action_before_review
claim_policy_before_review
```

If a field is unavailable in the source row, the reviewer must record that it is unavailable rather than silently inferring it.

## Evidence to inspect

For each row, the reviewer should answer:

1. Which candidate lane does this row belong to?
2. Which candidate and source table row does it trace back to?
3. Which source protein, target species, and candidate ortholog are involved?
4. What provenance evidence is missing?
5. What source evidence was inspected?
6. Does the inspected evidence resolve the missing source ortholog or provenance issue?
7. Does the evidence match the expected species and taxid?
8. Does the evidence match the expected gene or protein identity?
9. Does the evidence introduce ambiguity that requires a second reviewer?
10. What downstream gates remain blocked after this review?

## Acceptable evidence sources

Acceptable evidence sources are sources that let a reviewer trace the row to a concrete ortholog or explain why such a trace is still unresolved.

Examples of acceptable sources:

```text
reviewed UniProt entry
UniProt ortholog or taxonomy evidence
NCBI protein or gene record with species and taxid
Ensembl orthology evidence
OMA orthology evidence
OrthoDB orthology evidence
primary literature with accession-level evidence
project-maintained curated table with explicit source accession and reviewer note
```

The reviewer must record the evidence source and accession or stable identifier when available.

## Unacceptable evidence sources

The following are not sufficient by themselves:

```text
model output without accession-level provenance
embedding similarity alone
sequence similarity without species/taxid provenance
LLM-generated assertion without external source evidence
a filename or local cache path without source provenance
a candidate name without accession evidence
a downstream enrichment result
a Boltz, AF3, Chai, or cofolding result
a biological narrative without source accession evidence
```

These sources may be useful context, but they do not resolve a Gate 4 / Gate 5 provenance blocker by themselves.

## Allowed review decisions

A reviewed row should use one of the following decisions:

```text
accepted_for_planning_after_review
rejected_after_review
deferred_pending_source
needs_second_reviewer
```

### accepted_for_planning_after_review

Use this only when the reviewer found enough accession-level and species-level provenance evidence to support later Gate 4 / Gate 5 planning.

This does not mean:

```text
validated ortholog
validated biological signal
Gate 8 eligible
Gate 9 eligible
embedding ready
Boltz ready
```

It means only:

```text
this provenance blocker has reviewed evidence that may support a later explicit Gate 4 / Gate 5 policy update
```

### rejected_after_review

Use this when the inspected evidence shows that the row should not be promoted for planning, for example because the accession, species, taxid, gene identity, or orthology evidence conflicts with the row.

A rejected row remains a valid repair-queue output. It becomes an explicit exclude or do-not-promote item rather than disappearing silently.

### deferred_pending_source

Use this when the available evidence is insufficient to resolve the row.

A deferred row remains blocked at Gate 4 / Gate 5.

### needs_second_reviewer

Use this when evidence exists but is ambiguous enough that one reviewer should not make the decision alone.

A second-reviewer row remains blocked at Gate 4 / Gate 5 until the ambiguity is resolved.

## Downstream blocking policy

A review decision must record what remains blocked.

Even after `accepted_for_planning_after_review`, the row must not automatically enter:

```text
Gate 8 contrast
Gate 9 cofolding readiness
live structural compatibility
decision-package promotion
```

The review may support a later explicit Gate 4 / Gate 5 policy update. That later policy update must be implemented in a separate PR.

## Forbidden claims

This checklist does not authorize claims such as:

```text
validated longevity signal
validated biological hit
confirmed binding change
confirmed functional effect
validated ortholog
safe to port
proven pro-longevity variant
```

Allowed language is limited to:

```text
manual provenance review checklist
repair evidence checklist
review planning
Gate 4 / Gate 5 blocker review
reviewed-for-planning provenance evidence
```

## Reviewer output expectation

A future reviewed-decision artifact should record:

```text
review_decision
reviewed_target_uniprot
reviewed_source_database
reviewed_source_accession
reviewed_sequence_length
reviewed_taxid
review_evidence_uri_or_note
reviewer_note
downstream_block_status_after_review
allowed_next_action_after_review
claim_policy_after_review
claim_status_after_review
forbidden_actions_after_review
```

This checklist defines the human review protocol. A later schema PR should define the exact machine-readable reviewed-decision table.
