# Boltz baseline calibration results

This note records the first live Boltz baseline-calibration results for the PINDER-fragment cofolding workflow.

The goal is not to make a species-level biological claim yet. The goal is to establish whether the current Boltz PPI setup can recover known human-human structural positive controls before interpreting cross-species cofolding outputs.

## Commands

```bash
uv run cofolding-controls --top-n 200
uv run cofolding-baseline-controls --control-id "3lqz__B1_P04440--3lqz__A1_P20036" --yes-live
uv run cofolding-baseline-controls --control-id "6xcp__B1_O19707--6xcp__A1_Q30069" --yes-live
```

## Results

| PINDER id | Pair | Receptor | Ligand | Receptor length | Ligand length | ipTM | Binding confidence | Classification |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 3lqz__B1_P04440--3lqz__A1_P20036 | HLA class II human-human control | P04440 | P20036 | 198 | 181 | 0.959 | 0.750 | maintained |
| 6xcp__B1_O19707--6xcp__A1_Q30069 | MHC/HLA-DQ human-human control | O19707 | Q30069 | 200 | 182 | 0.973 | 0.769 | maintained |

## Interpretation

Both audited human-human PINDER-fragment positive controls were recovered as maintained interactions by the current Boltz cofolding setup.

This is an important calibration result: the workflow can recover high-confidence human-human structural controls and does not simply classify all PINDER-fragment inputs as incompatible.

However, these controls are MHC/HLA examples. They do not by themselves validate SIRT6/NHEJ cofolding candidates. Future cross-species claims should require a recoverable human or technical positive-control baseline for the same candidate family before interpreting species-level incompatibility biologically.

## Caveats

- Runtime outputs under data/output/ are local and are not committed.
- Signed Boltz structure URLs are not committed.
- The current evidence supports the cofolding calibration gate, not a direct SIRT6/NHEJ species-level biological conclusion.
- The next biological question is whether any SIRT6/NHEJ human PINDER-fragment baseline is recoverable before running cross-species panels.
