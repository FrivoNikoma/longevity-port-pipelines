# TP53/MDM2 generic repair alignment checkpoint

This checkpoint records the alignment of the TP53/MDM2 elephant ortholog repair decision table with the generic LongevityPort coverage/provenance repair vocabulary.

It is a vocabulary-alignment checkpoint, not an ortholog curation checkpoint.

No elephant TP53 or MDM2 ortholog is claimed as resolved here. No sequence is fetched or manually curated here. No downstream gate is unblocked here.

## Updated repair decision table

Tracked file:

- `data/input/tp53_mdm2_ortholog_repair_decisions.csv`

The table now keeps the TP53/MDM2-specific fields and also exposes generic repair vocabulary fields:

- `lane_name`
- `source_species`
- `gene_symbol`
- `target_uniprot`
- `coverage_status`
- `provenance_status`
- `repair_status`
- `reviewer_note`

The two seed rows remain:

- `tp53_mdm2_elephant_seed_tp53_chain`
- `tp53_mdm2_elephant_seed_mdm2_chain`

Both rows remain unresolved:

- `target_uniprot`: `unresolved`
- `coverage_status`: `unresolved_downstream_provenance`
- `provenance_status`: `unresolved`
- `repair_status`: `pending`

## Validator update

The TP53/MDM2 ortholog repair validator now checks the generic alignment fields alongside the lane-specific fields.

It also exposes:

- `generic_repair_columns`
- `blocked_generic_repair_rows`

These helpers make the TP53/MDM2 lane easier to compare against the generic repair queue without promoting the rows into strict panel, contrast, cofolding, or live structural compatibility gates.

## Gate decision

TP53/MDM2 elephant remains blocked at Gate 4 / Gate 5.

Allowed language:

- generic repair vocabulary alignment
- coverage/provenance repair queue
- source ortholog fetch or curation required
- blocked calibration lane
- technical checkpoint

Disallowed claims and actions:

- no validated ortholog
- no confirmed conserved function
- no validated biological hit
- no validated longevity signal
- no confirmed binding change
- no confirmed functional effect
- no Biohub call
- no embedding generation
- no Boltz call
- no enrichment or contrast rerun
- no cofolding readiness promotion
- no live structural compatibility call
- no decision package promotion

## Next safe actions

Possible next PRs after this checkpoint:

1. Add a generic repair queue summary builder.
2. Build a unified repair queue view across SIRT6 and TP53/MDM2.
3. Record one manual source-ortholog provenance review checkpoint.
4. Keep TP53/MDM2 blocked until explicit ortholog evidence is fetched or manually curated.
