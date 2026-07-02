# Brandt's bat P09874 controlled embedding fill no-op checkpoint

This checkpoint records the first real controlled embedding fill worklist run after the controlled fill protocol, schema, and builder were added.

Input:

- `data/output/curated_ortholog_embedding_preflight.csv`

Output:

- `data/interim/controlled_embedding_fill_worklist_brandts_bat_p09874_checkpoint.csv`

This is a table-only checkpoint. It does not call Biohub, does not generate embeddings, does not commit `data/output/` artifacts, does not call Boltz, does not rerun enrichment/contrast, and does not make biological claims.

## Result

The input preflight table contains one Brandt's bat P09874 row:

- `candidate_set`: `sirt6_dna_repair`
- `lane_name`: `SIRT6/core3`
- `source_uniprot`: `P09874`
- `target_species`: `brandts_bat`
- `target_species_taxid`: `109478`
- `target_accession`: `EPQ16369.1`
- `sequence_length_status`: `matches`
- `embedding_exists`: `true`
- `embedding_status`: `present`

The controlled worklist therefore assigns:

- `fill_status`: `do_not_fill`
- `allowed_next_action`: `do_not_fill`
- `claim_policy`: `no_biological_claims_until_validation`
- `claim_status`: `technical_checkpoint`

## Interpretation

This is a no-op fill checkpoint.

It confirms that the controlled embedding fill worklist builder treats the already-filled Brandt's bat P09874 embedding as a completed technical artifact and does not promote it to a new live-fill candidate.

This checkpoint does not select a missing embedding for fill. A future PR must use a reviewed missing row before any controlled dry-run candidate selection or live-fill review.
