# Generic repair queue summary builder checkpoint

This checkpoint records the first generic Gate 4 / Gate 5 repair queue summary builder.

The builder combines the tracked SIRT6/core3 and TP53/MDM2 elephant repair inputs into one machine-readable repair queue summary.

## Inputs

Tracked inputs:

- `data/input/sirt6_candidate_coverage_repair_decisions.csv`
- `data/input/tp53_mdm2_ortholog_repair_decisions.csv`

Current expected committed-input summary:

- SIRT6/core3: 11 repair rows
- TP53/MDM2 elephant: 2 repair rows
- total: 13 repair queue rows

## Output

Default runtime output:

- `data/interim/generic_repair_queue_summary.csv`

The output is a runtime artifact and is not committed by this checkpoint.

## Safe summary fields

The builder uses explicit blocker-oriented fields:

- `repair_queue_status`
- `downstream_block_status`
- `allowed_next_action`

It intentionally avoids pass-through language.

## Gate decision

This checkpoint does not repair any ortholog row.

All current committed rows remain blocked at Gate 4 / Gate 5 and must not be promoted into Gate 8 contrast, Gate 9 cofolding readiness, live structural compatibility, or decision-package claims.

## Disallowed actions

This checkpoint performs:

- no sequence fetch
- no manual ortholog curation
- no Biohub call
- no embedding generation
- no Boltz call
- no enrichment or contrast rerun
- no Gate 8 promotion
- no Gate 9 promotion
- no biological claim

## Next safe actions

Possible next PRs after this checkpoint:

1. Add a checked-in example summary fixture if useful.
2. Add a generic repair queue docs page.
3. Add a manual provenance review checkpoint for one high-priority row.
4. Keep all downstream gates blocked until explicit ortholog evidence is reviewed.
