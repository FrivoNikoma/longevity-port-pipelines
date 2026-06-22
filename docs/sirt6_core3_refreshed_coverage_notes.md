# SIRT6 core3 refreshed ortholog coverage notes

## Status

This note summarizes the refreshed ortholog coverage state for the SIRT6 mini-pilot v2 core3 expanded workflow.

This is a dataset-readiness checkpoint, not a biological interpretation of the longevity signal.

## Inputs

The refreshed expanded ortholog coverage was generated from:

- `data/output/sirt6_mini_pilot_v2_expanded_selection.csv`
- current `TARGET_SPECIES` registry
- `scripts/refresh_sirt6_expanded_ortholog_coverage.py`

The full refresh was run in bounded chunks and then merged locally into:

- `data/output/sirt6_mini_pilot_v2_expanded_ortholog_coverage_refreshed_all.csv`
- `data/output/sirt6_mini_pilot_v2_expanded_missing_orthologs_refreshed_all.csv`

These CSV files are local generated artifacts and are not committed.

## Expanded refreshed coverage summary

The refreshed expanded coverage attempted:

- 25 source UniProt IDs
- 8 registered target species
- 200 source-UniProt × target-species attempts

Observed local result:

| Status | Count |
|---|---:|
| Ortholog mappings found | 106 |
| Missing mappings | 94 |
| Total attempts | 200 |

Coverage by target species in the refreshed expanded coverage:

| Target species | Taxid | Found mappings | Missing mappings |
|---|---:|---:|---:|
| elephant | 9785 | 16 | 9 |
| hamster | 10036 | 16 | 9 |
| mouse | 10090 | 20 | 5 |
| rat | 10116 | 20 | 5 |
| naked mole-rat | 10181 | 17 | 8 |
| bowhead whale | 27622 | 0 | 25 |
| Myotis lucifugus | 59463 | 17 | 8 |
| Brandt's bat | 109478 | 0 | 25 |

Two source UniProt IDs had zero mappings across all target species in the refreshed expanded audit:

- `P03296`
- `P62799`

## Core3 refreshed result

Using the refreshed expanded coverage as input, `make_sirt6_mini_pilot_v2_core3_expanded.py` produced:

| Metric | Value |
|---|---:|
| Core3 selection rows | 11 |
| Unique PDB IDs | 8 |
| Source UniProt IDs | 12 |
| Retained ortholog coverage rows | 69 |
| Embedding pairs | 125 |
| Estimated Biohub API calls | 250 |
| Missing embedding pairs | 51 |

Coverage retained in the refreshed core3 output:

| Target species | Taxid | Retained rows |
|---|---:|---:|
| elephant | 9785 | 10 |
| hamster | 10036 | 11 |
| mouse | 10090 | 12 |
| rat | 10116 | 12 |
| naked mole-rat | 10181 | 12 |
| Myotis lucifugus | 59463 | 12 |

The core3-required species are fully retained for the 12 core3 source UniProt IDs:

- mouse
- naked mole-rat
- Myotis lucifugus

Additional usable species now retained in the core3 output:

- rat
- hamster
- elephant

Species audited but not retained due to missing ortholog coverage in this refreshed run:

- bowhead whale
- Brandt's bat

## Interpretation boundary

This result should not yet be interpreted as a biological longevity signal.

It only establishes that the SIRT6 core3 workflow can now support a broader comparative basis than the earlier three-species setup.

Allowed conclusion:

> The refreshed ortholog coverage expands the usable SIRT6 core3 comparison from a narrow mouse / naked mole-rat / Myotis setup to a six-species basis including elephant, rat, and hamster. This enables a more credible long-lived vs short-lived embedding/enrichment analysis in the next stage.

Not yet supported:

- long-lived species have stronger interface conservation
- elephant shows a specific SIRT6 longevity signal
- short-lived species differ in embedding geometry
- any specific interface is a validated longevity candidate
- any mechanism is confirmed

Those claims require the downstream embedding, enrichment, control, and manual-review stages.
