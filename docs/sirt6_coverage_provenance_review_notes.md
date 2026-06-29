# SIRT6 coverage provenance review notes

This note records the row-level provenance review worklist produced by the
candidate species coverage matrix for the SIRT6/core3 calibration lane.

This is a review note only. It does not curate new orthologs, does not run
Biohub embeddings, and does not run Boltz predictions.

## Input

The review table is generated locally from:

```bash
uv run candidate-species-coverage-matrix \
  --manifest data/input/sirt6_cofolding_candidate_manifest.csv \
  --output data/interim/sirt6_candidate_species_coverage_matrix.csv \
  --blockers-output data/interim/sirt6_candidate_species_coverage_blockers.csv
```

The blocker CSV is a regenerable local output under `data/interim/` and is not
committed.

## Summary

Total blocker rows: 11

Blocked by target species:

- bowhead_whale: 6
- brandts_bat: 4
- elephant: 1

Blocked by source UniProt:

- P12956: 3
- P09874: 2
- P13010: 2
- Q04206: 2
- Q8N6T7: 2

Recommended actions:

- review_local_rows_without_source_ortholog: 11

## Interpretation

All current blocker rows have local candidate-file rows present, but do not have
confirmed source ortholog coverage in the current coverage inputs.

That means the next step should not blindly add new ortholog records. Each row
needs provenance review first:

1. Check whether the local candidate rows already contain a valid target-species
ortholog sequence for the source UniProt.
2. If the sequence is valid, consolidate or link it into the source ortholog
coverage inputs.
3. If the sequence is not valid or the provenance is ambiguous, mark the row for
manual curation.
4. If the row is a mistaken local candidate row, exclude or correct it in a
separate small PR.

A useful observation from this checkpoint is that all current blockers are in
long-lived target species. Short-lived controls are not the current bottleneck
for this SIRT6/core3 manifest checkpoint.

## Row-level review worklist


| source_uniprot | target_species | candidate_id                     | pdb_id | chain    | local_rows | review_action                             |
| -------------- | -------------- | -------------------------------- | ------ | -------- | ---------- | ----------------------------------------- |
| P09874         | bowhead_whale  | 4xhu__A1_P09874--4xhu__B1_Q9UNS1 | 4xhu   | receptor | 2          | review_local_rows_without_source_ortholog |
| P09874         | bowhead_whale  | 7s68__D1_P09874--7s68__C1_P09874 | 7s68   | receptor | 4          | review_local_rows_without_source_ortholog |
| P12956         | bowhead_whale  | 8bhv__N1_P12956--8bhv__I1_Q9H9Q4 | 8bhv   | receptor | 2          | review_local_rows_without_source_ortholog |
| P12956         | brandts_bat    | 8bhv__N1_P12956--8bhv__I1_Q9H9Q4 | 8bhv   | receptor | 1          | review_local_rows_without_source_ortholog |
| P12956         | elephant       | 8bhv__N1_P12956--8bhv__I1_Q9H9Q4 | 8bhv   | receptor | 3          | review_local_rows_without_source_ortholog |
| P13010         | bowhead_whale  | 8bhv__P1_P13010--8bhv__J1_Q9H9Q4 | 8bhv   | receptor | 2          | review_local_rows_without_source_ortholog |
| P13010         | brandts_bat    | 8bhv__P1_P13010--8bhv__J1_Q9H9Q4 | 8bhv   | receptor | 1          | review_local_rows_without_source_ortholog |
| Q04206         | bowhead_whale  | 1nfi__A1_Q04206--1nfi__F1_P25963 | 1nfi   | receptor | 2          | review_local_rows_without_source_ortholog |
| Q04206         | brandts_bat    | 1nfi__A1_Q04206--1nfi__F1_P25963 | 1nfi   | receptor | 1          | review_local_rows_without_source_ortholog |
| Q8N6T7         | bowhead_whale  | 8f86__K1_Q8N6T7--8f86__D1_P02281 | 8f86   | receptor | 4          | review_local_rows_without_source_ortholog |
| Q8N6T7         | brandts_bat    | 8f86__K1_Q8N6T7--8f86__D1_P02281 | 8f86   | receptor | 2          | review_local_rows_without_source_ortholog |


## Local evidence files to inspect

The blocker export points to prior local audit or result files as local evidence.
The main files to inspect during manual review are:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_readiness_audit.csv`
- `data/output/sirt6_mini_pilot_v2_expanded_embedding_readiness_audit.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_embedding_signal_summary_refreshed.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_mapped_enrichment_refreshed.parquet`

These files are evidence pointers, not automatic proof that a row is
coverage-ready. The provenance check must still confirm that the target species,
source UniProt, sequence identity, and candidate mapping are consistent.

## Review decision categories

Use these categories during the next coverage repair PRs:

- `link_existing_local_row_to_source_ortholog`: local evidence appears valid and
should be consolidated into source ortholog coverage.
- `curate_missing_source_ortholog`: no valid local/provenance evidence was found;
a source ortholog needs manual curation.
- `ambiguous_provenance`: local evidence exists, but the source, species,
sequence, or UniProt mapping is not reliable enough.
- `exclude_or_correct_local_row`: local row appears inconsistent with the
candidate/source/species mapping and should not be treated as coverage-ready.

## Suggested review order

Start with source UniProts that block multiple rows:

1. P12956: 3 blocker rows across bowhead_whale, brandts_bat, and elephant.
2. P09874: 2 blocker rows, both bowhead_whale.
3. P13010: 2 blocker rows across bowhead_whale and brandts_bat.
4. Q04206: 2 blocker rows across bowhead_whale and brandts_bat.
5. Q8N6T7: 2 blocker rows across bowhead_whale and brandts_bat.

This order is only a review convenience. It is not a biological priority ranking.

## Definition of done for the next repair step

A follow-up coverage repair PR should reduce the blocker count only when the
source ortholog provenance is explicit.

After repair, rerun:

```bash
uv run candidate-species-coverage-matrix \
  --manifest data/input/sirt6_cofolding_candidate_manifest.csv \
  --output data/interim/sirt6_candidate_species_coverage_matrix.csv \
  --blockers-output data/interim/sirt6_candidate_species_coverage_blockers.csv
```

The affected rows should move from:

```text
review_local_rows_without_source_ortholog
```

to:

```text
coverage_ready
```

No longevity-specific biological claim should be made from this review note
alone.
