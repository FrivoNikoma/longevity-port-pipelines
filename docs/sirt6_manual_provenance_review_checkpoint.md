# SIRT6 manual provenance review checkpoint

This checkpoint records the first manual provenance review fixture for one SIRT6/core3 Gate 4 / Gate 5 repair queue row.

The reviewed decision is recorded in:

```text
data/input/generic_repair_queue_review_decisions.csv
```

## Scope

This is a Level 1 biological provenance data checkpoint. It records reviewed provenance evidence for one existing blocked repair queue row. It does not fetch sequences, does not curate orthologs, does not call Biohub, does not generate embeddings, does not call Boltz, does not rerun enrichment or contrast, does not promote Gate 8 or Gate 9, and does not make biological claims.

The checkpoint preserves blocker-first semantics. The selected row already exists as a valid blocked repair-queue worklist item. This review does not decide whether the row has the right to exist. It asks whether one concrete SIRT6 repair row can move from:

```text
unreviewed Gate 4 / Gate 5 blocker
```

to:

```text
reviewed-for-planning provenance evidence
```

## Reviewed row

Selected row:

```text
candidate_set: sirt6_dna_repair
lane_name: SIRT6/core3
candidate_id: 4xhu__A1_P09874--4xhu__B1_Q9UNS1
source_table: data/input/sirt6_candidate_coverage_repair_decisions.csv
source_row_index: 1
source_uniprot: P09874
target_species: bowhead_whale
target_species_taxid: 27622
```

The source repair row is a Gate 4 / Gate 5 blocker:

```text
coverage_status_before_review: local_rows_without_source_ortholog
provenance_status_before_review: external_review_required
repair_queue_status_before_review: blocked_pending_manual_review
downstream_block_status_before_review: blocked_gate4_gate5
allowed_next_action_before_review: manual_sequence_provenance_review
claim_policy_before_review: deferred_no_claim
```

## Evidence inspected

The review inspected taxonomy-level evidence for the target species label `bowhead_whale`.

Evidence note:

```text
NCBI and UniProt taxonomy evidence identify Balaena mysticetus / bowhead whale as taxid 27602 while the source repair row records 27622.
```

Recorded evidence sources:

```text
reviewed_source_database: NCBI Taxonomy; UniProt Taxonomy
reviewed_source_accession: NCBI Taxonomy:27602; UniProt Taxonomy:27602
reviewed_taxid: 27602
```

This evidence is sufficient to flag a source row provenance mismatch. It is not sufficient to accept a target ortholog accession for planning, because the fixture does not record accession-level target ortholog evidence.

## Review decision

The review decision is:

```text
review_decision: deferred_pending_source
```

Reason:

```text
The selected SIRT6 repair queue row remains blocked because the target species/taxid provenance requires source correction or stronger accession-level ortholog evidence before the row can be accepted for planning.
```

The row remains a valid repair-queue output. It is not deleted, silently corrected, or promoted downstream.

## Downstream policy

After review, the row remains blocked:

```text
downstream_block_status_after_review: blocked_gate4_gate5
allowed_next_action_after_review: defer_until_stronger_source_evidence_exists
claim_policy_after_review: no_biological_claims_until_validation
claim_status_after_review: repair_worklist
```

This checkpoint does not authorize:

```text
Gate 8 eligibility
Gate 9 eligibility
embedding generation
Boltz readiness
validated ortholog claims
validated biological signal claims
```

## Forbidden actions

This checkpoint does not perform or authorize:

```text
sequence fetch
manual ortholog curation
Biohub call
embedding generation
Boltz call
enrichment rerun
contrast rerun
Gate 8 promotion
Gate 9 promotion
biological claim
```

## Interpretation

This checkpoint is useful because it demonstrates that biological provenance review can keep a row blocked. Biological data review is not a shortcut to downstream analysis. It is a way to make the evidence state of a blocker explicit, reproducible, and machine-readable.
