# Controlled embedding fill protocol

This document defines the reusable protocol for controlled curated embedding fills after the Gate 8 / Gate 9 calibration checkpoint.

This is a governance checkpoint only. It does not call Biohub, generate embeddings, submit Boltz jobs, commit runtime artifacts, rerun enrichment or contrast, or make biological claims.

## Purpose

The repository already has live-capable curated embedding tools. The goal of this protocol is not to add another live runner.

The goal is to formalize how the existing tools may be used safely:

- start from `docs/gate_aware_embedding_fill_plan.md`;
- use `curated_embedding_preflight` before any row-level live consideration;
- use `curated_embedding_single` in dry-run mode before any live call;
- require explicit review and explicit `--yes-live` before any Biohub / ESMC call;
- keep generated `.npy` files as local runtime artifacts under `data/output/`;
- keep embedding fill separate from enrichment, contrast, Boltz, and biological claims.

## Existing tools

### `curated_embedding_preflight`

`curated_embedding_preflight` is the lane-level dry preflight.

It checks curated primary ortholog rows and records:

- canonical embedding path;
- `embedding_exists`;
- `embedding_status`;
- `target_sequence_length`;
- `actual_sequence_length`;
- `sequence_length_status`.

It must be run before selecting any reviewed live-fill candidate.

It does not call Biohub, does not generate embeddings, and does not modify ortholog coverage.

### `curated_embedding_single`

`curated_embedding_single` is the single-row runner.

Its default behavior is dry-run only:

- `yes_live=False` reports `dry_run_missing` or `dry_run_present`;
- dry-run mode does not call Biohub / ESMC;
- dry-run mode does not create an embedding file.

Live behavior is opt-in only:

- a live call requires explicit `--yes-live`;
- live mode must refuse rows where `sequence_length_status != matches`;
- `skip_existing=True` should avoid rewriting existing embeddings unless explicitly overridden.

## Reference precedent: Brandt's bat P09874

The current precedent is recorded in `docs/brandts_bat_p09874_live_embedding_generation.md`.

That checkpoint used:

- `complex_id`: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`;
- `chain`: `receptor`;
- `target_species`: `brandts_bat`;
- `target_species_taxid`: `109478`;
- `target_accession`: `EPQ16369.1`;
- `source_uniprot`: `P09874`;
- `model_name`: `esmc-300m-2024-12`.

Before the live call, dry-run evidence showed:

- `sequence_length_status: matches`;
- `embedding_exists: False`;
- `status: dry_run_missing`.

The live call used explicit `--yes-live`.

After live completion, the local `.npy` artifact was validated directly and a follow-up dry-run confirmed:

- `embedding_exists: True`;
- `status: dry_run_present`.

The precedent did not commit the `.npy` artifact, did not modify curated ortholog inputs, did not modify coverage, did not rerun enrichment, and did not call Boltz.

## Controlled protocol

Every future controlled embedding fill must follow this sequence.

1. Start from `docs/gate_aware_embedding_fill_plan.md`.
2. Run `curated_embedding_preflight` first.
3. Select only 1-3 reviewed rows for consideration.
4. For each selected row, run `curated_embedding_single` in dry-run mode first.
5. Require `sequence_length_status == matches`.
6. Require `embedding_exists == False`, unless intentionally checking skip-existing behavior.
7. Record the explicit candidate id, species, taxid, protein / UniProt identifier, target accession, and fill reason.
8. Require explicit human approval before using `--yes-live`.
9. Run at most one live row at a time.
10. After live completion, validate the local `.npy` artifact directly.
11. Run a follow-up dry-run confirming `embedding_exists: True`.
12. Never commit `data/output/` artifacts.
13. Do not rerun enrichment or contrast automatically.
14. Do not call Boltz automatically.
15. Do not make biological claims.

## Minimum reviewed-row requirements

Before any row can be considered for `reviewed_for_single_live_fill`, it must have:

- explicit candidate id;
- explicit species;
- explicit target species taxid;
- explicit protein / UniProt identifier;
- explicit target accession;
- reviewed target sequence;
- reviewed source provenance;
- no unresolved coverage blocker;
- clear reason why this embedding is needed;
- explicit dry-run preflight output;
- explicit `curated_embedding_single` dry-run output;
- explicit human approval to use `--yes-live`.

## Lane policy

### SIRT6/core3

SIRT6/core3 is the advanced calibration lane.

It may provide the first small reviewed worklist for controlled dry-run preflight and later single-row live embedding checkpoints.

Filled embeddings must still be treated as technical artifacts only. They do not imply biological validation, contrast readiness, cofolding readiness, or decision-package completion.

### TP53/MDM2 elephant

TP53/MDM2 elephant remains a blocked calibration lane while coverage/provenance is unresolved.

Its biological mode is `beneficial_breakage`, so divergence can be interesting, but that also makes claim discipline especially important.

TP53/MDM2 must not receive live embedding fills while unresolved coverage blockers remain. Its expected safe output is still a blocked worklist, not an eligible live-fill or cofolding manifest.

## Artifact policy

Generated embeddings are runtime artifacts.

Do not commit:

- `data/output/`;
- `.npy` embedding files;
- runtime Biohub outputs;
- runtime Boltz outputs;
- signed structure URLs;
- generated structure artifacts.

A controlled live-fill checkpoint may record a text summary of local validation, but not the generated embedding artifact itself.

## Downstream policy

Embedding fill does not automatically permit downstream analysis.

After a fill:

- do not rerun enrichment automatically;
- do not rerun long-lived-vs-short-lived contrast automatically;
- do not generate a cofolding manifest automatically;
- do not call Boltz automatically;
- do not produce a candidate decision package automatically.

Those steps remain behind their own gates.

## Claim policy

Allowed language:

- controlled embedding fill protocol;
- technical checkpoint;
- dry-run preflight;
- reviewed worklist;
- source provenance review;
- coverage repair dependency;
- live embedding opt-in;
- local runtime artifact validation.

Disallowed language:

- validated longevity signal;
- validated biological hit;
- confirmed binding change;
- confirmed functional effect;
- safe to port;
- proven pro-longevity variant.
