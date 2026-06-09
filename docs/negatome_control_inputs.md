# NEGATOME-style control inputs

This document defines the input contract for future NEGATOME-style negative controls.

The current mini-pilot already reports:

- shuffled mask control ratios;
- NEGATOME-style control ratio field;
- negative-control audit status;
- control status in the candidate scorecard.

However, the current mini-pilot does not yet populate `negatome_control_ratio`. Until a valid negative-control input table is provided, enrichment results should remain marked as `missing_negatome`.

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

```
uv run python -m scripts.validate_negatome_control_inputs

```

Expected output:

```
data/output/sirt6_mini_pilot_negatome_control_input_validation.csv

```

The validation output reports whether each mini-pilot complex/chain/species row has at least one negative-control input candidate.

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

A later pipeline step should use this input contract to compute `negatome_control_ratio`.

That future step should:

1. embed the negative-control partner sequence;
2. compute a comparable interface/non-interface or partner-control statistic;
3. write `negatome_control_ratio` into enrichment outputs;
4. rerun the negative-control audit;
5. propagate the updated control status into the candidate scorecard.

## Important interpretation note

This document defines the input contract only. It does not claim that NEGATOME-style controls are currently populated.

The current correct interpretation is:

```
shuffled mask control: implemented
NEGATOME-style control: input contract defined, ratios not yet populated
candidate scorecard: should continue to show missing_negatome until a valid control table exists

```

