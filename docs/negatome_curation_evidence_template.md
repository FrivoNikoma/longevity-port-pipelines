# NEGATOME-style curation evidence template

This document defines an evidence template for curating candidate NEGATOME-style negative-control partners before they are promoted into:

```text
data/interim/negatome_control_pairs.csv

```

It complements:

- `docs/negatome_control_inputs.md`
- `docs/negatome_curation_guide.md`
- `scripts.generate_negatome_control_pair_candidates`
- `scripts.validate_negatome_control_inputs`

The goal is to keep curation evidence separate from the final input contract, so that tentative or weak candidate controls are not accidentally treated as populated NEGATOME-style controls.

## 1. Why this evidence layer exists

The current mini-pilot has a candidate scaffold:

```text
data/output/sirt6_mini_pilot_negatome_control_pair_candidates.csv

```

That scaffold identifies rows that could receive future negative-control partners, but it does not provide real negative partners.

A curated input row should only be created after a candidate negative partner has been reviewed for:

- non-interaction evidence;
- absence of known direct interaction in the relevant context;
- non-homology to the true partner;
- not being part of the same complex;
- sequence availability;
- clear provenance.

This document provides a place to record that evidence before creating the strict input file.

## 2. Three separate states

The NEGATOME-style workflow should keep these states distinct:

```text
candidate scaffold exists
curation evidence exists
curated input table exists
computed NEGATOME-style control ratios exist

```

Only the final state should populate `negatome_control_ratio`.

The existence of this evidence document does not mean NEGATOME-style controls are populated.

## 3. Recommended evidence table columns

Use the following columns when recording curation evidence:

```text
complex_id
chain
target_species
source_uniprot
true_partner_uniprot
candidate_negative_partner_uniprot
candidate_negative_partner_name
candidate_negative_partner_species
candidate_negative_partner_sequence_status
evidence_source
evidence_source_record
evidence_type
interaction_database_screen
known_interaction_exclusion_status
homology_exclusion_status
same_complex_exclusion_status
curation_status
curation_note

```

These columns are intentionally broader than the final input contract.

The final input contract requires only:

```text
complex_id
chain
target_species
source_uniprot
negative_partner_uniprot
negative_partner_source
negative_partner_sequence
control_type

```

## 4. Column meanings

### `complex_id`

The mini-pilot complex identifier.

Example:

```text
8f86__K1_Q8N6T7--8f86__A1_P84233

```

### `chain`

The mini-pilot chain role being evaluated.

Allowed values should match the pipeline outputs, usually:

```text
receptor
ligand

```

### `target_species`

The species row from the mini-pilot comparison.

Examples:

```text
mouse
myotis_lucifugus
naked_mole_rat

```

### `source_uniprot`

The source/reference UniProt identifier for the tested protein.

Examples from the current mini-pilot:

```text
Q8N6T7
P13010
P12956
P09874

```

### `true_partner_uniprot`

The known or intended interaction partner for the source complex row.

This field is used to ensure the candidate negative partner is not simply the true partner, an ortholog of the true partner, or a close homolog.

### `candidate_negative_partner_uniprot`

The proposed negative-control partner UniProt identifier.

This field must not be copied into `data/interim/negatome_control_pairs.csv` until the evidence fields below have been reviewed.

### `candidate_negative_partner_name`

Human-readable protein name.

### `candidate_negative_partner_species`

Species for the candidate negative partner.

For the first pass, prefer species consistency with the mini-pilot row when possible.

### `candidate_negative_partner_sequence_status`

Suggested values:

```text
sequence_available
sequence_missing
sequence_ambiguous
sequence_fragment_only
sequence_not_checked

```

Only `sequence_available` should be allowed into the final input file.

### `evidence_source`

Where the negative-partner claim came from.

Suggested values:

```text
negatome_database
literature_curation
manual_curation
intact_or_biogrid_absence_screen
orthogonal_pathway_selection
background_control_only

```

### `evidence_source_record`

A stable identifier, URL, citation note, database row identifier, or short source description.

Examples:

```text
Negatome manual table entry
Negatome stringent table entry
Manual review: no known direct interaction found in checked sources

```

### `evidence_type`

Suggested values:

```text
database_supported_non_interactor
literature_supported_non_interactor
no_known_interaction_after_database_screen
orthogonal_pathway_control
background_protein_control

```

Use `background_protein_control` only for weak background controls. Do not treat it as strong NEGATOME evidence.

### `interaction_database_screen`

Record what was checked.

Suggested values:

```text
not_checked
IntAct_checked
BioGRID_checked
IntAct_and_BioGRID_checked
Negatome_checked

```

If interaction databases are checked but no interaction is found, this should still be interpreted cautiously. Absence from an interaction database is not proof of non-interaction.

### `known_interaction_exclusion_status`

Suggested values:

```text
not_checked
no_known_direct_interaction_found
known_interaction_found_reject
ambiguous_manual_review_needed

```

### `homology_exclusion_status`

Suggested values:

```text
not_checked
not_close_homolog_of_true_partner
close_homolog_reject
ambiguous_manual_review_needed

```

A candidate negative partner should not be a close homolog, ortholog, or paralog of the true partner.

### `same_complex_exclusion_status`

Suggested values:

```text
not_checked
not_known_same_complex
same_complex_reject
ambiguous_manual_review_needed

```

### `curation_status`

Suggested values:

```text
candidate_unreviewed
candidate_under_review
candidate_rejected
candidate_ready_for_input
candidate_background_only

```

Only `candidate_ready_for_input` should be promoted into the strict input file.

### `curation_note`

Short human-readable rationale.

This can include caveats, uncertainty, or rejection reasons.

## 5. Markdown table template

Use this table for small manual curation batches:


| complex_id                       | chain    | target_species | source_uniprot | true_partner_uniprot | candidate_negative_partner_uniprot | candidate_negative_partner_name | candidate_negative_partner_species | candidate_negative_partner_sequence_status | evidence_source | evidence_source_record | evidence_type | interaction_database_screen | known_interaction_exclusion_status | homology_exclusion_status | same_complex_exclusion_status | curation_status      | curation_note               |
| -------------------------------- | -------- | -------------- | -------------- | -------------------- | ---------------------------------- | ------------------------------- | ---------------------------------- | ------------------------------------------ | --------------- | ---------------------- | ------------- | --------------------------- | ---------------------------------- | ------------------------- | ----------------------------- | -------------------- | --------------------------- |
| 8f86__K1_Q8N6T7--8f86__A1_P84233 | receptor | mouse          | Q8N6T7         | P59941               | TBD                                | TBD                             | mouse                              | sequence_not_checked                       | TBD             | TBD                    | TBD           | not_checked                 | not_checked                        | not_checked               | not_checked                   | candidate_unreviewed | First-pass SIRT6 mouse row. |
| 8bot__U1_P13010--8bot__T1_P12956 | receptor | mouse          | P13010         | P27641               | TBD                                | TBD                             | mouse                              | sequence_not_checked                       | TBD             | TBD                    | TBD           | not_checked                 | not_checked                        | not_checked               | not_checked                   | candidate_unreviewed | First-pass Ku70 mouse row.  |
| 7s68__D1_P09874--7s68__C1_P09874 | receptor | mouse          | P09874         | P11103               | TBD                                | TBD                             | mouse                              | sequence_not_checked                       | TBD             | TBD                    | TBD           | not_checked                 | not_checked                        | not_checked               | not_checked                   | candidate_unreviewed | First-pass PARP1 mouse row. |


## 6. CSV header template

For larger curation batches, use this CSV header:

```csv
complex_id,chain,target_species,source_uniprot,true_partner_uniprot,candidate_negative_partner_uniprot,candidate_negative_partner_name,candidate_negative_partner_species,candidate_negative_partner_sequence_status,evidence_source,evidence_source_record,evidence_type,interaction_database_screen,known_interaction_exclusion_status,homology_exclusion_status,same_complex_exclusion_status,curation_status,curation_note

```

## 7. First-pass curation targets

Start with a very small subset:

```text
SIRT6 receptor / mouse
Ku70 receptor / mouse
PARP1 receptor / mouse

```

Current scaffold rows:

```text
8f86__K1_Q8N6T7--8f86__A1_P84233,receptor,mouse,Q8N6T7,P59941
8bot__U1_P13010--8bot__T1_P12956,receptor,mouse,P13010,P27641
7s68__D1_P09874--7s68__C1_P09874,receptor,mouse,P09874,P11103

```

These are good first-pass rows because:

- they are central to the mini-pilot;
- mouse is experimentally interpretable;
- the validator already handles partial curation;
- a small subset reduces the risk of propagating weak controls.

## 8. Promotion criteria

A candidate evidence row may be promoted to `data/interim/negatome_control_pairs.csv` only if:

```text
curation_status = candidate_ready_for_input
candidate_negative_partner_sequence_status = sequence_available
known_interaction_exclusion_status = no_known_direct_interaction_found
homology_exclusion_status = not_close_homolog_of_true_partner
same_complex_exclusion_status = not_known_same_complex

```

The final input row should then map fields as follows:

```text
complex_id -> complex_id
chain -> chain
target_species -> target_species
source_uniprot -> source_uniprot
candidate_negative_partner_uniprot -> negative_partner_uniprot
evidence_source -> negative_partner_source
negative partner sequence -> negative_partner_sequence
evidence_type -> control_type

```

## 9. Rejection criteria

Reject a candidate if:

- it is the true partner;
- it is an ortholog, paralog, or close homolog of the true partner;
- it is a known direct interactor in the relevant context;
- it is part of the same complex;
- the sequence is missing or ambiguous;
- the only rationale is that the protein is random;
- the evidence source cannot be traced.

Rejected rows should remain in curation notes and should not be copied into the final input contract.

## 10. Important caution

A curated negative-control input row does not itself compute `negatome_control_ratio`.

The pipeline still needs a later computation step that:

1. embeds the negative-control partner sequence;
2. computes the comparable negative-control statistic;
3. writes `negatome_control_ratio`;
4. reruns the negative-control audit;
5. propagates updated control status into the scorecard and validation plan.

Until that computation exists, downstream enrichment results should remain cautious even if curated input rows are present.