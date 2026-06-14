# SIRT6 mini-pilot v2 structure selection QC

This report audits contrast-informed structure selections against local PDB/mmCIF structures.

It reports both exact residue-number matches and sequence-alignment-remapped matches.

Important caveat: this is a structural QC screen, not a replacement for final manual structure review.

## Cutoffs

- near cutoff: 5.0 A
- interface-proximal cutoff: 8.0 A

## QC status counts

| qc_status | len |
| --- | --- |
| remapped_interface_supported | 11 |

## Overview

| pdb_id | chain | structure_chain | partner_structure_chain | target_species | contrast_class | n_selected_residues | exact_n_found | exact_fraction_within_interface_cutoff | remapped_n_found | remapped_fraction_within_interface_cutoff | qc_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8g57 | ligand | G | K | myotis_lucifugus | long_lived_specific_interface_divergence | 12 | 12 | 0.1667 | 12 | 1 | remapped_interface_supported |
| 8g57 | ligand | G | K | naked_mole_rat | long_lived_specific_interface_divergence | 12 | 12 | 0.08333 | 12 | 1 | remapped_interface_supported |
| 1nfi | receptor | C | E | myotis_lucifugus | long_lived_enhanced_interface_divergence | 12 | 10 | 0.4 | 12 | 1 | remapped_interface_supported |
| 1nfi | receptor | C | E | naked_mole_rat | long_lived_enhanced_interface_divergence | 12 | 11 | 0.2727 | 12 | 1 | remapped_interface_supported |
| 7s68 | receptor | A | B | naked_mole_rat | long_lived_specific_interface_divergence | 12 | 8 | 0.5 | 12 | 1 | remapped_interface_supported |
| 8f86 | receptor | K | D | myotis_lucifugus | long_lived_specific_interface_constraint | 8 | 8 | 0.75 | 8 | 1 | remapped_interface_supported |
| 4xhu | receptor | C | D | mouse | not_applicable | 12 | 0 | 0 | 12 | 1 | remapped_interface_supported |
| 4xhu | receptor | C | D | myotis_lucifugus | shared_interface_constraint | 12 | 0 | 0 | 12 | 1 | remapped_interface_supported |
| 4xhu | receptor | C | D | naked_mole_rat | shared_interface_constraint | 12 | 0 | 0 | 12 | 1 | remapped_interface_supported |
| 8bhv | ligand | Q | h | mouse | not_applicable | 7 | 7 | 0.1429 | 7 | 1 | remapped_interface_supported |
| 8bhv | ligand | R | j | mouse | not_applicable | 7 | 6 | 0 | 7 | 1 | remapped_interface_supported |

## Interpretation notes

- `exact_*` fields assume reference residue numbering equals structure residue numbering.
- `remapped_*` fields align the residue-delta reference sequence to the structure chain sequence.
- Low exact support with better remapped support indicates residue-numbering mismatch rather than necessarily a biological failure.
- Low remapped proximity suggests that selections need manual review or that the candidate is not interface-proximal in the inspected structure.
