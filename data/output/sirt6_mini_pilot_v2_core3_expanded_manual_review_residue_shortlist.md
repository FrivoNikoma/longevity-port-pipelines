# SIRT6 v2 core3-expanded manual review residue shortlist

## Purpose

This file summarizes residue-level candidates for manual structural review from the SIRT6 v2 core3-expanded run.

Divergent cases are represented by the highest-delta interface residues. Constrained-anchor cases are represented by the lowest-delta interface residues.

## Summary by review case

### Priority 1: 8g57 / ligand / myotis_lucifugus

- Complex: `8g57__A1_Q8N6T7--8g57__H1_P04908`
- Review case: SIRT6-nucleosome long-lived interface divergence candidate
- Selection mode: `top_interface_delta`
- Signal class: `interface_divergent_not_significant`
- Contrast class: `long_lived_specific_interface_divergence`
- Number of residues: 12
- Delta range: 0.3098 to 1.3913
- Mean delta: 0.8192
- Residues: A116, K115, H114, H113, S112, K117, E111, T110, G12, L53, R61, E46

### Priority 1: 8g57 / ligand / naked_mole_rat

- Complex: `8g57__A1_Q8N6T7--8g57__H1_P04908`
- Review case: SIRT6-nucleosome long-lived interface divergence candidate
- Selection mode: `top_interface_delta`
- Signal class: `interface_divergent_not_significant`
- Contrast class: `long_lived_specific_interface_divergence`
- Number of residues: 12
- Delta range: 0.4174 to 1.5196
- Mean delta: 0.8172
- Residues: Y47, E46, L48, T49, L45, A50, E51, K117, A42, Q14, E54, I52

### Priority 2: 1nfi / receptor / myotis_lucifugus

- Complex: `1nfi__A1_Q04206--1nfi__F1_P25963`
- Review case: NF-kappaB regulatory-interface rewiring candidate
- Selection mode: `top_interface_delta`
- Signal class: `interface_divergent`
- Contrast class: `long_lived_enhanced_interface_divergence`
- Number of residues: 12
- Delta range: 0.4223 to 0.8879
- Mean delta: 0.5530
- Residues: H162, I4, K291, F290, K295, Y287, E288, E3, M294, S292, R285, I293

### Priority 2: 1nfi / receptor / naked_mole_rat

- Complex: `1nfi__A1_Q04206--1nfi__F1_P25963`
- Review case: NF-kappaB regulatory-interface rewiring candidate
- Selection mode: `top_interface_delta`
- Signal class: `interface_divergent`
- Contrast class: `long_lived_enhanced_interface_divergence`
- Number of residues: 12
- Delta range: 0.4440 to 0.9289
- Mean delta: 0.5632
- Residues: H162, K291, F290, K295, E288, S292, Y287, M294, E3, R285, R283, T289

### Priority 3: 7s68 / receptor / naked_mole_rat

- Complex: `7s68__D1_P09874--7s68__C1_P09874`
- Review case: PARP1-linked cautious long-lived-specific candidate
- Selection mode: `top_interface_delta`
- Signal class: `interface_divergent_not_significant`
- Contrast class: `long_lived_specific_interface_divergence`
- Number of residues: 12
- Delta range: 0.4880 to 1.8175
- Mean delta: 1.3959
- Residues: S1, Q36, P38, S37, F40, D41, D2, M39, K43, G42, G177, C175

### Priority 4: 8f86 / receptor / myotis_lucifugus

- Complex: `8f86__K1_Q8N6T7--8f86__D1_P02281`
- Review case: SIRT6-nucleosome maintained-interface candidate
- Selection mode: `lowest_interface_delta`
- Signal class: `interface_constrained_not_significant`
- Contrast class: `long_lived_specific_interface_constraint`
- Number of residues: 8
- Delta range: 0.1616 to 0.2614
- Mean delta: 0.2106
- Residues: L173, R174, A175, R177, K169, R171, A170, G172

### Priority 5: 4xhu / receptor / mouse

- Complex: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Review case: shared constrained-interface anchor
- Selection mode: `lowest_interface_delta`
- Signal class: `interface_constrained`
- Contrast class: `not_applicable`
- Number of residues: 12
- Delta range: 0.1505 to 0.2008
- Mean delta: 0.1830
- Residues: P207, I220, I204, G219, K218, R203, G201, G252, L202, V315, D317, E208

### Priority 5: 4xhu / receptor / myotis_lucifugus

- Complex: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Review case: shared constrained-interface anchor
- Selection mode: `lowest_interface_delta`
- Signal class: `interface_constrained`
- Contrast class: `shared_interface_constraint`
- Number of residues: 12
- Delta range: 0.1620 to 0.2603
- Mean delta: 0.2162
- Residues: P207, K218, G201, R203, G219, L251, I220, E208, L202, Q200, P206, G252

### Priority 5: 4xhu / receptor / naked_mole_rat

- Complex: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Review case: shared constrained-interface anchor
- Selection mode: `lowest_interface_delta`
- Signal class: `interface_constrained`
- Contrast class: `shared_interface_constraint`
- Number of residues: 12
- Delta range: 0.1608 to 0.2138
- Mean delta: 0.1871
- Residues: P207, K218, I220, I204, R203, L202, G219, D317, G201, V315, N253, E208

### Priority 6: 8bhv / ligand / mouse

- Complex: `8bhv__N1_P12956--8bhv__I1_Q9H9Q4`
- Review case: singleton divergent outlier / artifact-risk benchmark
- Selection mode: `top_interface_delta`
- Signal class: `interface_divergent`
- Contrast class: `not_applicable`
- Number of residues: 7
- Delta range: 0.3780 to 0.6287
- Mean delta: 0.5019
- Residues: R170, D171, R172, L168, L173, I169, T167

### Priority 6: 8bhv / ligand / mouse

- Complex: `8bhv__P1_P13010--8bhv__J1_Q9H9Q4`
- Review case: singleton divergent outlier / artifact-risk benchmark
- Selection mode: `top_interface_delta`
- Signal class: `interface_divergent`
- Contrast class: `not_applicable`
- Number of residues: 7
- Delta range: 0.7783 to 1.0492
- Mean delta: 0.9118
- Residues: R221, P220, F224, S225, G222, L223, K219

## Caveat

This shortlist is a review aid, not a validation result. Each residue set still needs manual inspection on the corresponding 3D structure to confirm interface localization, chain identity, and residue remapping.
