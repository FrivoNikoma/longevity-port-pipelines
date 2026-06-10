# PARP1 NEGATOME-style curation evidence notes

This document records first-pass curation evidence for candidate NEGATOME-style negative-control partners for PARP1 rows in the SIRT6 mini-pilot.

This is an evidence note, not a final input table.

Do not treat any row in this document as a populated NEGATOME-style control until it has been promoted into:

```text
data/interim/negatome_control_pairs.csv

```

and a later computation step has populated:

```text
negatome_control_ratio

```

## 1. Current mini-pilot PARP1 rows

Current scaffold rows involving PARP1:

```text
7s68__D1_P09874--7s68__C1_P09874,ligand,mouse,P09874,P11103
7s68__D1_P09874--7s68__C1_P09874,ligand,myotis_lucifugus,P09874,G1PK82
7s68__D1_P09874--7s68__C1_P09874,ligand,naked_mole_rat,P09874,A0A0A7HSK2
7s68__D1_P09874--7s68__C1_P09874,receptor,mouse,P09874,P11103
7s68__D1_P09874--7s68__C1_P09874,receptor,myotis_lucifugus,P09874,G1PK82
7s68__D1_P09874--7s68__C1_P09874,receptor,naked_mole_rat,P09874,A0A0A7HSK2

```

For first-pass curation, focus on the mouse receptor row:

```text
complex_id: 7s68__D1_P09874--7s68__C1_P09874
chain: receptor
target_species: mouse
source_uniprot: P09874
true_partner_uniprot: P11103

```

## 2. Source and true partner interpretation

`P09874` is the human PARP1 reference protein used in the source complex.

`P11103` is mouse PARP1 and appears as the target ortholog for the mouse row.

This means that a candidate negative partner must not be:

- PARP1 itself;
- mouse PARP1;
- an ortholog of PARP1;
- a close PARP-family homolog used as a substitute for PARP1;
- a known direct PARP1 interactor in the same relevant biological context;
- a known component of the same complex or repair machinery context being evaluated.

## 3. Why PARP1 is a good first-pass curation target

PARP1 is a useful first target because:

- it is central to DNA damage sensing and repair biology;
- the scaffold contains both ligand and receptor PARP1 rows;
- mouse has a clear target ortholog row;
- PARP1 has many known interactors, making exclusion rules important;
- the row is good for testing curation logic before expanding to all species.

## 4. Evidence sources to check

For each candidate negative partner, record evidence from one or more of the following:

```text
Negatome manual table
Negatome stringent table
Negatome PDB-derived table
IntAct search
BioGRID search
UniProt sequence and protein-family check
Manual literature review

```

Priority order:

1. database-supported non-interactor from Negatome;
2. literature-supported non-interactor;
3. no known interaction after database screen;
4. orthogonal-pathway control;
5. background-protein control.

Only the first two are strong NEGATOME-style evidence.

## 5. Known exclusion examples

Do not use the following as PARP1 negative partners without strong contrary evidence:

```text
PARP1
PARP2
HPF1
XRCC1
BRCA1
ERG
DNA repair complex partners
PARP-family close homologs

```

Rationale:

- PARP2 is functionally and biologically close to PARP1;
- HPF1 is a known PARP1 cofactor in serine ADP-ribosylation contexts;
- XRCC1 and BRCA1 are DNA repair-associated interactors or pathway-adjacent proteins;
- ERG has reported interaction evidence with PARP1;
- close PARP-family homologs are poor negative controls because homology and pathway similarity confound interpretation.

This exclusion list is not complete. It is a starting point for avoiding obvious false negative controls.

## 6. First-pass evidence table


| complex_id                       | chain    | target_species | source_uniprot | true_partner_uniprot | candidate_negative_partner_uniprot | candidate_negative_partner_name               | candidate_negative_partner_species | candidate_negative_partner_sequence_status | evidence_source         | evidence_source_record                                                                                                                          | evidence_type                     | interaction_database_screen                                                     | known_interaction_exclusion_status | homology_exclusion_status         | same_complex_exclusion_status  | curation_status           | curation_note                                                                                                                                                                                               |
| -------------------------------- | -------- | -------------- | -------------- | -------------------- | ---------------------------------- | --------------------------------------------- | ---------------------------------- | ------------------------------------------ | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------- | --------------------------------- | ------------------------------ | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 7s68__D1_P09874--7s68__C1_P09874 | receptor | mouse          | P09874         | P11103               | TBD                                | TBD                                           | mouse                              | sequence_not_checked                       | Negatome_check_required | TBD                                                                                                                                             | TBD                               | not_checked                                                                     | not_checked                        | not_checked                       | not_checked                    | candidate_unreviewed      | First-pass PARP1 mouse receptor row. Search Negatome for P09874-supported non-interactor candidates before promoting anything to input.                                                                     |
| 7s68__D1_P09874--7s68__C1_P09874 | receptor | mouse          | P09874         | P11103               | P07437                             | Tubulin beta chain / TUBB                     | human                              | sequence_not_checked                       | negatome_database       | Negatome manual table row 1577; PMID 15607978; MI:0007 anti tag coimmunoprecipitation                                                           | database_supported_non_interactor | Negatome_checked; IntAct_quick_screen_has_PARP1_TUBB_result                     | ambiguous_manual_review_needed     | not_close_homolog_of_true_partner | ambiguous_manual_review_needed | candidate_background_only | Manual Negatome hit for PARP1/P09874, but quick IntAct search surfaces a PARP1/P09874 and P07437/TUBB result. Treat as lower-priority/background-only until the interaction context is manually resolved.   |
| 7s68__D1_P09874--7s68__C1_P09874 | receptor | mouse          | P09874         | P11103               | O60907                             | F-box-like/WD repeat-containing protein TBL1X | human                              | sequence_available                         | negatome_database       | Negatome manual table row 1671; PMID 15607978; MI:0007 anti tag coimmunoprecipitation; UniProt O60907 reviewed canonical sequence length 577 aa | database_supported_non_interactor | Negatome_checked; UniProt_sequence_checked; targeted_PARP1_TBL1X_screen_pending | ambiguous_manual_review_needed     | not_close_homolog_of_true_partner | ambiguous_manual_review_needed | candidate_under_review    | Manual Negatome hit for PARP1/P09874. O60907 has a reviewed UniProt canonical sequence, but targeted PARP1/TBL1X interaction-database and same-complex/pathway screens are still required before promotion. |
| 7s68__D1_P09874--7s68__C1_P09874 | ligand   | mouse          | P09874         | P11103               | TBD                                | TBD                                           | mouse                              | sequence_not_checked                       | Negatome_check_required | TBD                                                                                                                                             | TBD                               | not_checked                                                                     | not_checked                        | not_checked                       | not_checked                    | candidate_unreviewed      | Optional second PARP1 mouse row. Do not curate until receptor row procedure is validated.                                                                                                                   |


## 7. Current screening interpretation

Current interpretation of the two PARP1/P09874 Negatome manual candidates:

### P07437 / TUBB

`P07437` is a reviewed UniProt entry for human tubulin beta chain / TUBB.

It is not a PARP-family homolog, but it is a broad cytoskeletal/background protein and is therefore a weak biological match for a nuclear DNA-repair/chromatin PARP1 control.

A quick IntAct screen surfaced a PARP1/P09874 and P07437/TUBB result. Because of this, TUBB should not be promoted to `candidate_ready_for_input` without manual resolution of the interaction context.

Current status:

```text
curation_status = candidate_background_only
known_interaction_exclusion_status = ambiguous_manual_review_needed
same_complex_exclusion_status = ambiguous_manual_review_needed

```

### O60907 / TBL1X

`O60907` is a reviewed UniProt entry for human TBL1X.

TBL1X is not a PARP-family homolog and has a nuclear/transcriptional functional context, making it a better review candidate than TUBB for a PARP1 negative-control row.

O60907 sequence availability is now considered confirmed at the UniProt canonical-sequence level. However, BioGRID contains a TBL1X interaction page with many interaction records, so the next step must be targeted pair-level screening rather than assuming that no direct PARP1 interaction exists.

Current status:

```text
candidate_negative_partner_sequence_status = sequence_available
curation_status = candidate_under_review
known_interaction_exclusion_status = ambiguous_manual_review_needed
same_complex_exclusion_status = ambiguous_manual_review_needed

```

TBL1X should remain under review until:

- a targeted PARP1/TBL1X interaction-database screen is documented;
- same-complex and chromatin-remodeling/pathway confounders are reviewed;
- the curation status can be justified without relying only on broad database absence.

## 8. Candidate screening checklist

Before marking a candidate as `candidate_ready_for_input`, check:

```text
candidate_negative_partner_uniprot is non-empty
candidate_negative_partner_name is non-empty
candidate_negative_partner_sequence_status = sequence_available
evidence_source is not TBD
evidence_source_record is traceable
evidence_type is not TBD
interaction_database_screen is not not_checked
known_interaction_exclusion_status = no_known_direct_interaction_found
homology_exclusion_status = not_close_homolog_of_true_partner
same_complex_exclusion_status = not_known_same_complex
curation_status = candidate_ready_for_input

```

## 9. Promotion mapping

If a PARP1 candidate passes curation, map fields into the strict input contract as follows:

```text
complex_id -> complex_id
chain -> chain
target_species -> target_species
source_uniprot -> source_uniprot
candidate_negative_partner_uniprot -> negative_partner_uniprot
evidence_source -> negative_partner_source
candidate negative partner sequence -> negative_partner_sequence
evidence_type -> control_type

```

The final promoted row should go into:

```text
data/interim/negatome_control_pairs.csv

```

only after review.

## 10. Important caution

This document does not populate NEGATOME controls.

The current correct interpretation remains:

```text
PARP1 evidence notes: started
curated PARP1 input row: not yet created
negatome_control_ratio: not yet computed
scorecard status: missing_negatome

```

A candidate row in this document is only a curation candidate. It should not be interpreted as evidence that PARP1 has a populated negative-control ratio.

## 11. Next action

Next research step:

```text
Run a targeted pair-level PARP1/P09874 ↔ O60907/TBL1X interaction-database screen and same-complex/pathway review. O60907 sequence availability is confirmed from UniProt, but the candidate should remain candidate_under_review until direct-interaction exclusion is documented.

```

For the prioritized O60907/TBL1X candidate:

1. run targeted PARP1/TBL1X screen in interaction databases;
2. check whether TBL1X appears in the same protein complex or pathway context as PARP1;
3. decide whether `known_interaction_exclusion_status` can move to `no_known_direct_interaction_found`;
4. decide whether `same_complex_exclusion_status` can move to `not_known_same_complex`;
5. only then consider whether `curation_status` can move from `candidate_under_review` to `candidate_ready_for_input`.

