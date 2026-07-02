# Controlled missing embedding blocker checkpoint

This checkpoint records the first controlled inspection for a reviewed missing embedding fill candidate after the controlled embedding fill protocol, worklist schema, worklist builder, and Brandt's bat P09874 no-op checkpoint.

It is a blocker checkpoint, not a fill-candidate checkpoint.

## Inspection result

The current tracked evidence does not support selecting a reviewed missing embedding row for controlled dry-run or live fill.

The legacy SIRT6 mini-pilot missing-embedding artifacts identify the `8f86` ligand-side `P84233` row as the remaining technical missing case, but that row is blocked by missing ortholog coverage rather than ready for embedding fill.

The relevant legacy case is:

- complex: `8f86`
- chain role: ligand
- source UniProt: `P84233`
- interpretation: missing ortholog coverage / no reviewed target-species embedding path

Because this row lacks reviewed target species, target taxid, target accession, and embedding path evidence, it must not be promoted to a controlled dry-run or live-fill candidate.

## Tracked blocker context

The tracked SIRT6 coverage repair decision table records current `8f86` / `Q8N6T7` expanded-species blockers for:

- `bowhead_whale`
- `brandts_bat`

Both rows are recorded as:

- `coverage_gap_status`: `missing_ortholog_but_local_rows_present`
- `recommended_coverage_action`: `local_downstream_evidence_without_source_ortholog`
- `repair_decision`: `needs_external_manual_sequence_review`
- `claim_policy`: `deferred_no_claim`

This reinforces that the next safe action is manual sequence/provenance review, not embedding generation.

## Decision

No reviewed missing embedding row is selected in this checkpoint.

Allowed status:

- blocked embedding fill row
- source provenance review
- coverage repair dependency
- technical checkpoint

Disallowed next actions:

- no Biohub call
- no embedding generation
- no `curated_embedding_single --yes-live`
- no committed `data/output/` embedding artifact
- no Boltz call
- no enrichment or contrast rerun
- no biological claim

## Next safe action

Create or repair explicit ortholog/provenance rows before considering any controlled embedding dry-run candidate.

A future controlled fill candidate must have:

- explicit candidate id
- explicit target species
- explicit target species taxid
- explicit target accession
- reviewed source provenance
- no unresolved coverage blocker
- `sequence_length_status == matches`
- dry-run evidence before any live opt-in
