# Boltz live smoke summary: 3-complex cross-species mini-panel

## Context

This note summarizes the first live Boltz cofolding mini-panel after adding two safety layers to the cofolding stage:

- `--yes-live` prevents accidental live Boltz API prediction starts.
- `--dry-run-inputs` builds real cross-species Boltz inputs without creating a Boltz client, calling the Boltz API, or writing result files.

The goal of this smoke panel was to verify the full live path:

candidate selection -> ortholog lookup -> UniProt partner sequence -> Boltz API submit -> polling/retrieve -> metrics -> CSV/parquet output -> CIF download.

## Panel design

We tested 3 complexes across 3 species:

- `naked_mole_rat` — long-lived species
- `myotis_lucifugus` — long-lived bat species
- `mouse` — short-lived control

All runs used:

- `--top-n 1`
- `--num-samples 1`
- explicit `--complex`
- explicit `--species`
- explicit `--output`
- explicit `--yes-live`

## Results

| complex_id | chain | target_species | enrichment_ratio | classification | ipTM | binding_confidence | complex_ipLDDT | prediction_id |
|---|---|---:|---:|---|---:|---:|---:|---|
| `4rer__A1_Q13131--4rer__B1_O43741` | ligand | mouse | 1.4823 | uncertain | 0.7049 | 0.2562 | 0.6089 | `sab_pred_HFkqtIJMrjvyjAVu15wo` |
| `4rer__A1_Q13131--4rer__B1_O43741` | ligand | myotis_lucifugus | 1.5720 | uncertain | 0.7042 | 0.4081 | 0.6779 | `sab_pred_yCuXxsOSPw6Lhnmlr1Ld` |
| `4rer__A1_Q13131--4rer__B1_O43741` | ligand | naked_mole_rat | 1.9410 | uncertain | 0.4957 | 0.1763 | 0.5965 | `sab_pred_hlUhAkKj3NXOCjBLCTWR` |
| `5iso__A1_P54646--5iso__B1_Q9Y478` | receptor | mouse | 1.5745 | uncertain | 0.6922 | 0.3705 | 0.6948 | `sab_pred_A3tCHRCHIJcppyfsfdcj` |
| `5iso__A1_P54646--5iso__B1_Q9Y478` | receptor | myotis_lucifugus | 1.6236 | uncertain | 0.6829 | 0.3197 | 0.6868 | `sab_pred_un5M7hDPig2Hdasw7CzA` |
| `5iso__A1_P54646--5iso__B1_Q9Y478` | receptor | naked_mole_rat | 1.5844 | uncertain | 0.7041 | 0.2935 | 0.6628 | `sab_pred_h3L8AxxW0G7XfdUiZFVX` |
| `6b2e__A1_P54646--6b2e__B1_O43741` | ligand | mouse | 1.8096 | uncertain | 0.6802 | 0.2880 | 0.6374 | `sab_pred_CwOUSrgRCDhnLj2R4J5W` |
| `6b2e__A1_P54646--6b2e__B1_O43741` | ligand | myotis_lucifugus | 1.9361 | uncertain | 0.7028 | 0.4154 | 0.6990 | `sab_pred_PSxWzmepfPWs6yVJJ2FB` |
| `6b2e__A1_P54646--6b2e__B1_O43741` | ligand | naked_mole_rat | 1.9564 | uncertain | 0.6406 | 0.2744 | 0.6209 | `sab_pred_6gP9uQ1r8RWYxww2ipDm` |

## Interpretation

All 9 live predictions remained in the `uncertain` classification range.

No prediction reached the current maintained threshold:

- maintained: `ipTM >= 0.75`
- functionally broken / incompatible: lower-confidence range, especially with low binding confidence
- uncertain: intermediate region

The strongest repeated pattern is that `myotis_lucifugus` looks comparatively stable in the ligand-chain cases:

- `6b2e / ligand / myotis_lucifugus`: ipTM 0.7028, binding confidence 0.4154, complex ipLDDT 0.6990
- `4rer / ligand / myotis_lucifugus`: ipTM 0.7042, binding confidence 0.4081, complex ipLDDT 0.6779

The mouse control had similar ipTM in `4rer`, but lower binding confidence and complex ipLDDT.

The `5iso / receptor` panel did not reproduce the same myotis-leading pattern. In that case:

- mouse had the highest binding confidence
- naked mole rat had the highest ipTM
- all three remained uncertain

Overall, this is not yet a strong maintained-interaction signal. The result is best interpreted as a successful live technical smoke test plus a preliminary hint that `myotis_lucifugus` may deserve follow-up in ligand-chain cases.

## Connection error note

One live run for `5iso / receptor / naked_mole_rat` initially wrote a local error row due to a connection error during polling/retrieve.

The prediction was later recovered from the Boltz API:

- recovered prediction ID: `sab_pred_h3L8AxxW0G7XfdUiZFVX`
- recovered ipTM: 0.7041
- recovered binding confidence: 0.2935
- recovered complex ipLDDT: 0.6628
- recovered CIF was saved locally

This suggests the prediction was successfully created and completed on the Boltz side, while the local script lost connection during retrieval.

## Local artifacts

The live CSV/parquet/CIF outputs were kept as local experimental artifacts under `data/output/`.

They are not committed in this PR.

## Recommended next steps

1. Do not continue large live runs immediately.
2. Add retry/recovery hardening around Boltz polling/retrieve.
3. Add a helper mode to retrieve an existing Boltz prediction by `prediction_id`.
4. After hardening, run a slightly broader panel or rerun top candidates with `num_samples > 1`.
5. Treat ipTM together with binding confidence, complex ipLDDT, and cross-complex consistency rather than as a standalone binding-affinity metric.
