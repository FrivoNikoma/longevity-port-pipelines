# NEGATOME-style control inputs

This document defines the input contract for future NEGATOME-style negative controls.

The current mini-pilot already reports:

- shuffled mask control ratios;
- NEGATOME-style control ratio field;
- negative-control audit status;
- control status in the candidate scorecard.

However, the current mini-pilot does not yet populate `negatome_control_ratio` until curated
negative-control inputs are provided **and** partner embeddings are computed. Until then,
enrichment results should remain marked as `missing_negatome`.

## Input file

Expected path:

```
data/interim/negatome_control_pairs.csv

```

This file should not be treated as a generated output. It is an input table describing negative-control partner candidates.

## Required columns

```
complex_id
chain
target_species
source_uniprot
negative_partner_uniprot
negative_partner_source
negative_partner_sequence
control_type

```

## Column meanings

### complex_id

The mini-pilot complex identifier.

Example:

```
8bot__U1_P13010--8bot__T1_P12956

```

### chain

The chain role used in the mini-pilot.

Allowed values:

```
receptor
ligand

```

### target_species

The target species label used in mini-pilot outputs.

Examples:

```
mouse
naked_mole_rat
myotis_lucifugus

```

### source_uniprot

The UniProt identifier of the reference protein being analyzed.

### negative_partner_uniprot

The UniProt identifier of a protein expected not to interact with the analyzed protein.

### negative_partner_source

The source of the negative-control pair.

Examples:

```
NEGATOME
curated_manual
decoy_library

```

### negative_partner_sequence

The sequence of the negative-control partner. This is required for future embedding-based control calculations.

### control_type

The type of negative control.

Suggested values:

```
negatome
curated_negative
decoy

```

## Validation script

Run:

```powershell
uv run python -m scripts.validate_negatome_control_inputs
```

Expected output:

```
data/output/sirt6_mini_pilot_negatome_control_input_validation.csv
```

The validation output reports whether each mini-pilot complex/chain/species row has at least one negative-control input candidate.

## Compute NEGATOME control ratios

After curating `data/interim/negatome_control_pairs.csv` (see `data/input/negatome_control_pairs.example.csv`):

```powershell
uv run python -m scripts.embed_negatome_control_partners
uv run python -m scripts.analyze_saved_embeddings_mapped --negatome-pairs data/interim/negatome_control_pairs.csv
uv run python -m scripts.audit_negative_controls
```

The main 7-stage pipeline also embeds negative partners during stage 5 and writes
`negatome_control_ratio` during stage 6 when the curated input file exists.

### Metric

`negatome_control_ratio` uses the same structural interface mask as the primary enrichment
analysis, but measures cross-species change in embedding coupling to the curated
non-interacting partner. A candidate should ideally satisfy:

```text
enrichment_ratio > shuffled_control_ratio
enrichment_ratio > negatome_control_ratio
```

## Current expected status

Until `data/interim/negatome_control_pairs.csv` exists, the validation output should report:

```
missing_input_file

```

or:

```
missing_negative_control_input

```

This is expected and should not be treated as a failed analysis. It means the mini-pilot should continue to report `missing_negatome`.

## Future use

The pipeline step that computes `negatome_control_ratio` is implemented in:

- `src/longevity_port_pipelines/stages/negatome_analyze.py`
- `src/longevity_port_pipelines/stages/negatome_controls.py`
- `src/longevity_port_pipelines/pipeline.py` (stages 5–6)
- `scripts/embed_negatome_control_partners.py`
- `scripts/analyze_saved_embeddings_mapped.py`

That step:

1. embeds the negative-control partner sequence;
2. computes coupling-shift enrichment at the structural interface mask;
3. writes `negatome_control_ratio` into enrichment outputs;
4. reruns the negative-control audit;
5. propagates the updated control status into the candidate scorecard.

## Important interpretation note

This document defines the input contract only. It does not claim that NEGATOME-style controls
are populated for every row until curated inputs and partner embeddings exist.

The current interpretation is:

```text
shuffled mask control: implemented
NEGATOME-style control: implemented when data/interim/negatome_control_pairs.csv is curated
candidate scorecard: missing_negatome until negatome_control_ratio is populated per row
```

