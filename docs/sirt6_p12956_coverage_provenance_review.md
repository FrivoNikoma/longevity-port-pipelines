# SIRT6 P12956 coverage provenance review

This note records the P12956-specific provenance review for the SIRT6/core3
coverage blocker worklist.

This is a review note only. It does not curate new orthologs, does not generate
new embeddings, and does not run Boltz predictions.

## Context

The candidate species coverage matrix reports P12956 as coverage-ready for five
species:

- hamster
- mouse
- myotis_lucifugus
- naked_mole_rat
- rat

The same matrix reports three unresolved long-lived species blockers:

- bowhead_whale
- brandts_bat
- elephant

For these three species, local candidate-file rows are present, but source
ortholog provenance is not confirmed.

## P12956 blocker summary


| candidate_id                     | target_species | status  | local evidence | source ortholog provenance |
| -------------------------------- | -------------- | ------- | -------------- | -------------------------- |
| 8bhv__N1_P12956--8bhv__I1_Q9H9Q4 | bowhead_whale  | blocked | present        | missing                    |
| 8bhv__N1_P12956--8bhv__I1_Q9H9Q4 | brandts_bat    | blocked | present        | missing                    |
| 8bhv__N1_P12956--8bhv__I1_Q9H9Q4 | elephant       | blocked | present        | missing                    |


Current coverage action for all three rows:

```text
review_local_rows_without_source_ortholog
```

## Local evidence reviewed

The local evidence probe inspected these files:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_readiness_audit.csv`
- `data/output/sirt6_mini_pilot_v2_expanded_embedding_readiness_audit.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_embedding_signal_summary_refreshed.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_mapped_enrichment_refreshed.parquet`

The readiness audit rows confirm that P12956 appears for the blocked species, but
the `target_uniprot` field is empty for the P12956 rows in:

- bowhead_whale
- brandts_bat
- elephant

The embedding signal and mapped enrichment outputs contain downstream elephant
rows, including a receptor row, but they do not provide enough source ortholog
provenance to mark P12956 elephant coverage as ready.

## Interpretation

These rows should not be promoted to `coverage_ready` based only on downstream
local evidence.

The local evidence confirms that the P12956 candidate has appeared in previous
audit or downstream result files. It does not confirm the missing source
ortholog provenance for bowhead_whale, brandts_bat, or elephant.

Therefore, the correct classification is:

```text
local downstream evidence exists, but source ortholog provenance remains unresolved
```

This distinction matters because the coverage matrix is supposed to protect the
pipeline from treating incomplete provenance as complete biological coverage.

## Recommended next action

Do not blindly add new P12956 ortholog records in this PR.

A follow-up repair PR should either:

1. Curate explicit P12956 source ortholog records for bowhead_whale, brandts_bat,
and/or elephant with documented provenance; or
2. Improve the coverage matrix action labels so these rows are distinguished
from cases where local evidence contains a usable target sequence identifier.

The refined action label for this unresolved provenance case is:

```text
local_downstream_evidence_without_source_ortholog
```

This makes the blocker more precise than the previous generic action:

```text
review_local_rows_without_source_ortholog
```

## Definition of done for future repair

A future P12956 repair PR should only move one of these rows to `coverage_ready`
when the source ortholog provenance is explicit.

At minimum, the repaired row should have:

- target species
- target species taxid
- source UniProt: `P12956`
- target UniProt or stable target protein identifier
- sequence length
- source database or provenance file
- review note explaining why the row is accepted

No longevity-specific biological claim should be made from this review note
alone.
