# SIRT6 v2 core3-expanded viewer-ready structure selections

## Purpose

This file exports viewer-ready selections for manual 3D review of the SIRT6 v2 core3-expanded manual-review residue patches.

Selections are based on `remapped_reference_to_structure_residue` from the structure-QC output, not on raw `residue_number_1based` values.

## Important caveat

These selections are review aids. They should be visually inspected before being used for final figures or biological claims.

## Selection summary

### 8g57 / ligand / myotis_lucifugus

- Candidate type: priority_1: SIRT6-nucleosome long-lived interface divergence candidate
- Complex: `8g57__A1_Q8N6T7--8g57__H1_P04908`
- Contrast class: `long_lived_specific_interface_divergence`
- QC status: `remapped_interface_supported`
- Structure chain: `G`
- Partner chain: `K`
- Reference residues: `116;115;114;113;112;117;111;110;12;53;61;46`
- Remapped structure residues: `22;56;63;71;120;121;122;123;124;125;126;127`

PyMOL:

```text
select 8g57_ligand_g_k_myotis_lucifugus_long_lived_specific_interface_divergence_patch, chain G and resi 22+56+63+71+120+121+122+123+124+125+126+127
select 8g57_ligand_g_k_myotis_lucifugus_partner, chain K
show sticks, 8g57_ligand_g_k_myotis_lucifugus_long_lived_specific_interface_divergence_patch; show surface, chain K; color yellow, 8g57_ligand_g_k_myotis_lucifugus_long_lived_specific_interface_divergence_patch; color cyan, 8g57_ligand_g_k_myotis_lucifugus_partner
```

ChimeraX:

```text
select /G:22,56,63,71,120,121,122,123,124,125,126,127
select /K
style /G:22,56,63,71,120,121,122,123,124,125,126,127 stick; surface /K
```

### 8g57 / ligand / naked_mole_rat

- Candidate type: priority_1: SIRT6-nucleosome long-lived interface divergence candidate
- Complex: `8g57__A1_Q8N6T7--8g57__H1_P04908`
- Contrast class: `long_lived_specific_interface_divergence`
- QC status: `remapped_interface_supported`
- Structure chain: `G`
- Partner chain: `K`
- Reference residues: `47;46;48;49;45;50;51;117;42;14;54;52`
- Remapped structure residues: `24;52;55;56;57;58;59;60;61;62;64;127`

PyMOL:

```text
select 8g57_ligand_g_k_naked_mole_rat_long_lived_specific_interface_divergence_patch, chain G and resi 24+52+55+56+57+58+59+60+61+62+64+127
select 8g57_ligand_g_k_naked_mole_rat_partner, chain K
show sticks, 8g57_ligand_g_k_naked_mole_rat_long_lived_specific_interface_divergence_patch; show surface, chain K; color yellow, 8g57_ligand_g_k_naked_mole_rat_long_lived_specific_interface_divergence_patch; color cyan, 8g57_ligand_g_k_naked_mole_rat_partner
```

ChimeraX:

```text
select /G:24,52,55,56,57,58,59,60,61,62,64,127
select /K
style /G:24,52,55,56,57,58,59,60,61,62,64,127 stick; surface /K
```

### 1nfi / receptor / myotis_lucifugus

- Candidate type: priority_2: NF-kappaB regulatory-interface rewiring candidate
- Complex: `1nfi__A1_Q04206--1nfi__F1_P25963`
- Contrast class: `long_lived_enhanced_interface_divergence`
- QC status: `remapped_interface_supported`
- Structure chain: `C`
- Partner chain: `E`
- Reference residues: `162;4;291;290;295;287;288;3;294;292;285;293`
- Remapped structure residues: `22;23;181;304;306;307;309;310;311;312;313;314`

PyMOL:

```text
select 1nfi_receptor_c_e_myotis_lucifugus_long_lived_enhanced_interface_divergence_patch, chain C and resi 22+23+181+304+306+307+309+310+311+312+313+314
select 1nfi_receptor_c_e_myotis_lucifugus_partner, chain E
show sticks, 1nfi_receptor_c_e_myotis_lucifugus_long_lived_enhanced_interface_divergence_patch; show surface, chain E; color yellow, 1nfi_receptor_c_e_myotis_lucifugus_long_lived_enhanced_interface_divergence_patch; color cyan, 1nfi_receptor_c_e_myotis_lucifugus_partner
```

ChimeraX:

```text
select /C:22,23,181,304,306,307,309,310,311,312,313,314
select /E
style /C:22,23,181,304,306,307,309,310,311,312,313,314 stick; surface /E
```

### 1nfi / receptor / naked_mole_rat

- Candidate type: priority_2: NF-kappaB regulatory-interface rewiring candidate
- Complex: `1nfi__A1_Q04206--1nfi__F1_P25963`
- Contrast class: `long_lived_enhanced_interface_divergence`
- QC status: `remapped_interface_supported`
- Structure chain: `C`
- Partner chain: `E`
- Reference residues: `162;291;290;295;288;292;287;294;3;285;283;289`
- Remapped structure residues: `22;181;302;304;306;307;308;309;310;311;313;314`

PyMOL:

```text
select 1nfi_receptor_c_e_naked_mole_rat_long_lived_enhanced_interface_divergence_patch, chain C and resi 22+181+302+304+306+307+308+309+310+311+313+314
select 1nfi_receptor_c_e_naked_mole_rat_partner, chain E
show sticks, 1nfi_receptor_c_e_naked_mole_rat_long_lived_enhanced_interface_divergence_patch; show surface, chain E; color yellow, 1nfi_receptor_c_e_naked_mole_rat_long_lived_enhanced_interface_divergence_patch; color cyan, 1nfi_receptor_c_e_naked_mole_rat_partner
```

ChimeraX:

```text
select /C:22,181,302,304,306,307,308,309,310,311,313,314
select /E
style /C:22,181,302,304,306,307,308,309,310,311,313,314 stick; surface /E
```

### 7s68 / receptor / naked_mole_rat

- Candidate type: priority_3: PARP1-linked cautious long-lived-specific candidate
- Complex: `7s68__D1_P09874--7s68__C1_P09874`
- Contrast class: `long_lived_specific_interface_divergence`
- QC status: `remapped_interface_supported`
- Structure chain: `A`
- Partner chain: `B`
- Reference residues: `1;36;38;37;40;41;2;39;43;42;177;175`
- Remapped structure residues: `5;6;40;41;42;43;44;45;46;47;311;313`

PyMOL:

```text
select 7s68_receptor_a_b_naked_mole_rat_long_lived_specific_interface_divergence_patch, chain A and resi 5+6+40+41+42+43+44+45+46+47+311+313
select 7s68_receptor_a_b_naked_mole_rat_partner, chain B
show sticks, 7s68_receptor_a_b_naked_mole_rat_long_lived_specific_interface_divergence_patch; show surface, chain B; color yellow, 7s68_receptor_a_b_naked_mole_rat_long_lived_specific_interface_divergence_patch; color cyan, 7s68_receptor_a_b_naked_mole_rat_partner
```

ChimeraX:

```text
select /A:5,6,40,41,42,43,44,45,46,47,311,313
select /B
style /A:5,6,40,41,42,43,44,45,46,47,311,313 stick; surface /B
```

### 8f86 / receptor / myotis_lucifugus

- Candidate type: priority_4: SIRT6-nucleosome maintained-interface candidate
- Complex: `8f86__K1_Q8N6T7--8f86__D1_P02281`
- Contrast class: `long_lived_specific_interface_constraint`
- QC status: `remapped_interface_supported`
- Structure chain: `K`
- Partner chain: `D`
- Reference residues: `173;174;175;177;169;171;170;172`
- Remapped structure residues: `170;171;172;173;174;175;176;178`

PyMOL:

```text
select 8f86_receptor_k_d_myotis_lucifugus_long_lived_specific_interface_constraint_patch, chain K and resi 170+171+172+173+174+175+176+178
select 8f86_receptor_k_d_myotis_lucifugus_partner, chain D
show sticks, 8f86_receptor_k_d_myotis_lucifugus_long_lived_specific_interface_constraint_patch; show surface, chain D; color yellow, 8f86_receptor_k_d_myotis_lucifugus_long_lived_specific_interface_constraint_patch; color cyan, 8f86_receptor_k_d_myotis_lucifugus_partner
```

ChimeraX:

```text
select /K:170,171,172,173,174,175,176,178
select /D
style /K:170,171,172,173,174,175,176,178 stick; surface /D
```

### 4xhu / receptor / mouse

- Candidate type: priority_5: shared constrained-interface anchor
- Complex: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Contrast class: `not_applicable`
- QC status: `remapped_interface_supported`
- Structure chain: `C`
- Partner chain: `D`
- Reference residues: `207;220;204;219;218;203;201;252;202;315;317;208`
- Remapped structure residues: `876;877;878;879;882;883;893;894;895;927;991;993`

PyMOL:

```text
select 4xhu_receptor_c_d_mouse_not_applicable_patch, chain C and resi 876+877+878+879+882+883+893+894+895+927+991+993
select 4xhu_receptor_c_d_mouse_partner, chain D
show sticks, 4xhu_receptor_c_d_mouse_not_applicable_patch; show surface, chain D; color yellow, 4xhu_receptor_c_d_mouse_not_applicable_patch; color cyan, 4xhu_receptor_c_d_mouse_partner
```

ChimeraX:

```text
select /C:876,877,878,879,882,883,893,894,895,927,991,993
select /D
style /C:876,877,878,879,882,883,893,894,895,927,991,993 stick; surface /D
```

### 4xhu / receptor / myotis_lucifugus

- Candidate type: priority_5: shared constrained-interface anchor
- Complex: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Contrast class: `shared_interface_constraint`
- QC status: `remapped_interface_supported`
- Structure chain: `C`
- Partner chain: `D`
- Reference residues: `207;218;201;203;219;251;220;208;202;200;206;252`
- Remapped structure residues: `875;876;877;878;881;882;883;893;894;895;926;927`

PyMOL:

```text
select 4xhu_receptor_c_d_myotis_lucifugus_shared_interface_constraint_patch, chain C and resi 875+876+877+878+881+882+883+893+894+895+926+927
select 4xhu_receptor_c_d_myotis_lucifugus_partner, chain D
show sticks, 4xhu_receptor_c_d_myotis_lucifugus_shared_interface_constraint_patch; show surface, chain D; color yellow, 4xhu_receptor_c_d_myotis_lucifugus_shared_interface_constraint_patch; color cyan, 4xhu_receptor_c_d_myotis_lucifugus_partner
```

ChimeraX:

```text
select /C:875,876,877,878,881,882,883,893,894,895,926,927
select /D
style /C:875,876,877,878,881,882,883,893,894,895,926,927 stick; surface /D
```

### 4xhu / receptor / naked_mole_rat

- Candidate type: priority_5: shared constrained-interface anchor
- Complex: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Contrast class: `shared_interface_constraint`
- QC status: `remapped_interface_supported`
- Structure chain: `C`
- Partner chain: `D`
- Reference residues: `207;218;220;204;203;202;219;317;201;315;253;208`
- Remapped structure residues: `876;877;878;879;882;883;893;894;895;928;991;993`

PyMOL:

```text
select 4xhu_receptor_c_d_naked_mole_rat_shared_interface_constraint_patch, chain C and resi 876+877+878+879+882+883+893+894+895+928+991+993
select 4xhu_receptor_c_d_naked_mole_rat_partner, chain D
show sticks, 4xhu_receptor_c_d_naked_mole_rat_shared_interface_constraint_patch; show surface, chain D; color yellow, 4xhu_receptor_c_d_naked_mole_rat_shared_interface_constraint_patch; color cyan, 4xhu_receptor_c_d_naked_mole_rat_partner
```

ChimeraX:

```text
select /C:876,877,878,879,882,883,893,894,895,928,991,993
select /D
style /C:876,877,878,879,882,883,893,894,895,928,991,993 stick; surface /D
```

### 8bhv / ligand / mouse

- Candidate type: priority_6: singleton divergent outlier / artifact-risk benchmark
- Complex: `8bhv__N1_P12956--8bhv__I1_Q9H9Q4`
- Contrast class: `not_applicable`
- QC status: `remapped_interface_supported`
- Structure chain: `Q`
- Partner chain: `h`
- Reference residues: `170;171;172;168;173;169;167`
- Remapped structure residues: `173;174;175;176;177;178;179`

PyMOL:

```text
select 8bhv_ligand_q_h_mouse_not_applicable_patch, chain Q and resi 173+174+175+176+177+178+179
select 8bhv_ligand_q_h_mouse_partner, chain h
show sticks, 8bhv_ligand_q_h_mouse_not_applicable_patch; show surface, chain h; color yellow, 8bhv_ligand_q_h_mouse_not_applicable_patch; color cyan, 8bhv_ligand_q_h_mouse_partner
```

ChimeraX:

```text
select /Q:173,174,175,176,177,178,179
select /h
style /Q:173,174,175,176,177,178,179 stick; surface /h
```

### 8bhv / ligand / mouse

- Candidate type: priority_6: singleton divergent outlier / artifact-risk benchmark
- Complex: `8bhv__P1_P13010--8bhv__J1_Q9H9Q4`
- Contrast class: `not_applicable`
- QC status: `remapped_interface_supported`
- Structure chain: `R`
- Partner chain: `j`
- Reference residues: `221;220;224;225;222;223;219`
- Remapped structure residues: `293;294;295;296;297;298;299`

PyMOL:

```text
select 8bhv_ligand_r_j_mouse_not_applicable_patch, chain R and resi 293+294+295+296+297+298+299
select 8bhv_ligand_r_j_mouse_partner, chain j
show sticks, 8bhv_ligand_r_j_mouse_not_applicable_patch; show surface, chain j; color yellow, 8bhv_ligand_r_j_mouse_not_applicable_patch; color cyan, 8bhv_ligand_r_j_mouse_partner
```

ChimeraX:

```text
select /R:293,294,295,296,297,298,299
select /j
style /R:293,294,295,296,297,298,299 stick; surface /j
```
