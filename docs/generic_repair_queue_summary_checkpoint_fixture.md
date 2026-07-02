# Generic repair queue summary checkpoint fixtures

This checkpoint records regression fixtures for the generic Gate 4 / Gate 5 repair queue summary.

The fixtures live under `tests/fixtures/` rather than `data/interim/` because they are test checkpoints, not ordinary runtime outputs.

## Fixtures

```text
tests/fixtures/generic_repair_queue_summary_base.csv
tests/fixtures/generic_repair_queue_summary_reviewed_overlay.csv
```

The base fixture records the default generic repair queue summary without reviewed decisions. It is expected to contain 13 rows: 11 SIRT6/core3 repair rows and 2 TP53/MDM2 elephant repair rows.

The reviewed-overlay fixture records the same 13-row queue with reviewed decisions from `data/input/generic_repair_queue_review_decisions.csv` applied through the optional `--review-decisions` overlay.

## Gate / claim policy

These fixtures are regression checkpoints. They do not fetch sequences, do not curate orthologs, do not call Biohub, do not generate embeddings, do not call Boltz, do not rerun enrichment or contrast, do not promote Gate 8 or Gate 9, and do not make biological claims.

The current reviewed overlay fixture keeps the reviewed SIRT6 row blocked at Gate 4 / Gate 5 with `repair_queue_status = blocked_deferred_pending_source`. It records the reviewed decision without converting reviewed-for-planning provenance evidence into downstream eligibility.

The fixtures are intended to protect blocker-first semantics before later Gate 4 / Gate 5 policy-helper work.
