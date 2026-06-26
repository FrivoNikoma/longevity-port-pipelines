# Brandt's bat P09874 ortholog candidate evidence

This note records candidate evidence for a potential `brandts_bat` / `Myotis brandtii`
ortholog mapping for human `P09874` in the `4xhu` receptor-chain follow-up.

This is an evidence note, not a populated ortholog-coverage input.

## Context

The `4xhu` / `P09874` follow-up currently aims to extend a recovered human-baseline
candidate toward a long-lived vs short-lived species contrast.

The local `4xhu` / `P09874` coverage audit showed that `brandts_bat` and
`bowhead_whale` still lacked usable `P09874` ortholog coverage through the existing
local artifacts.

A follow-up probe through the repository's standard `fetch_ortholog()` path returned
missing for both species. That standard path tries OMA first and falls back to UniProt.

A broader UniProt / NCBI Protein probe found strict `brandts_bat` candidates, but did
not yield a safe `bowhead_whale` candidate.

## Candidate evidence

| Target species | Candidate | Source | Length | Description |
|---|---|---|---:|---|
| `brandts_bat` | `EPQ16369.1` | NCBI Protein | 1024 | `Poly [ADP-ribose] polymerase 1 [Myotis brandtii]` |
| `brandts_bat` | `S7NG06` | UniProt | 1024 | `Poly [ADP-ribose] polymerase`, organism `Myotis brandtii` |
| `brandts_bat` | `XP_005880205.1` | NCBI Protein | 969 | predicted `poly [ADP-ribose] polymerase 1 [Myotis brandtii]`; secondary isoform-like candidate |

The strongest current candidate is `EPQ16369.1` because it has:

- the expected organism label, `Myotis brandtii`;
- a PARP1-specific description;
- a full-length-like sequence length of 1024 amino acids.

`S7NG06` is useful as a same-length UniProt cross-check, but its description is less
specific than the NCBI Protein `EPQ16369.1` record.

`XP_005880205.1` should remain secondary because it is predicted and shorter.

## Rejected broad-probe hits

The broad probe also returned hits that should not be promoted as `P09874` ortholog
candidates:

| Candidate | Reason |
|---|---|
| `S7MYH2` | annotated as CHD1L / ATP-dependent chromatin remodeler, not PARP1 |
| `S7P457` | annotated as DNA polymerase, not PARP1 |
| short PARP-family-like hits | not full-length-like for this use case |

## Bowhead whale status

The `bowhead_whale` / `Balaena mysticetus` status remains unresolved.

Exact-taxid NCBI probing returned PARP1-like records:

| Candidate | Length | Rejection reason |
|---|---:|---|
| `XP_036133328.1` | 1014 | FASTA header identifies `Molossus molossus`, not `Balaena mysticetus` |
| `XP_036133329.1` | 975 | FASTA header identifies `Molossus molossus`, not `Balaena mysticetus` |

These should not be used as safe `bowhead_whale` curated mappings.

## Interpretation guard

This note records candidate evidence only.

It does not mean that:

- `brandts_bat` `P09874` ortholog coverage is populated in the pipeline;
- a curated ortholog override mechanism exists yet;
- the `4xhu` / `P09874` species panel is complete;
- the full 5-vs-3 long-lived/short-lived contrast is ready for live Boltz runs.

A future PR should decide whether to add a formal curated-ortholog input contract,
analogous to the NEGATOME curation workflow's separation between evidence notes,
curated input tables, and populated downstream control ratios.

No Boltz API calls were made during these probes.
