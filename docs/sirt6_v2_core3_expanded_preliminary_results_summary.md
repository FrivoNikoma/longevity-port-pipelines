# SIRT6 v2 core3-expanded preliminary results summary

## Purpose

This note summarizes the preliminary results from the SIRT6 v2 core3-expanded analysis.

It is intended as a human-readable synthesis of the current computational evidence, not as a validation claim.

The analysis has now progressed through:

1. core3-expanded complex selection;
2. ortholog coverage for mouse, naked mole-rat, and Myotis lucifugus;
3. saved ESMC embeddings;
4. mapped interface enrichment;
5. embedding signal summary;
6. long-lived-vs-mouse contrast;
7. mapped residue-level deltas;
8. divergence-profile feature export;
9. unsupervised clustering of divergence profiles;
10. manual-review case shortlist;
11. residue-level manual-review packet;
12. residue-patch interpretation;
13. structure-remapping QC.

The main result is that the pipeline now produces concrete, structure-supported residue-level candidate patches for manual biological review.

## Result status

The core3-expanded run has moved beyond a complex-level signal.

The current result stack supports the following interpretation:

- there are long-lived-enriched interface-divergence candidates;
- there are maintained-interface candidates;
- there are shared constrained-interface anchors;
- there are short-lived or singleton outliers useful as artifact-risk controls;
- the selected residue patches are not just sequence-level hits, because structure QC shows remapped interface support.

The result remains preliminary because final 3D interpretation still requires manual structure inspection, residue-numbering confirmation, and biological review of each interface context.

## Main result files

The main result files are:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_selection.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_enrichment_mapped.parquet`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_embedding_signal_summary.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_longevity_contrast.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_residue_deltas_mapped.parquet`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_features.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_residue_shortlist.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_selection_summary.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_qc.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_qc.md`

The main interpretation documents are:

- `docs/sirt6_v2_core3_expanded_clustering_interpretation.md`
- `docs/sirt6_v2_core3_expanded_manual_review_shortlist.md`
- `docs/sirt6_v2_core3_expanded_residue_review_interpretation.md`

This document summarizes the current biological story across those outputs.

## Key preliminary observations

### 1. SIRT6-nucleosome long-lived interface divergence candidate: 8g57 ligand

The strongest SIRT6-nucleosome divergence candidate is:

- Complex: `8g57__A1_Q8N6T7--8g57__H1_P04908`
- Chain: ligand
- Species: `naked_mole_rat`, `myotis_lucifugus`
- Contrast class: `long_lived_specific_interface_divergence`
- Structure QC: `remapped_interface_supported`

The residue-level packet identifies compact or near-compact high-delta interface regions.

For naked mole-rat, the main selected patch includes L45, E46, Y47, L48, T49, A50, E51, I52, and E54, with additional selected residues A42, Q14, and K117.

For Myotis lucifugus, the main selected patch includes T110, E111, S112, H113, H114, K115, A116, and K117, with additional selected residues G12, E46, L53, and R61.

Biological interpretation:

This is a high-priority candidate because SIRT6 is linked to chromatin regulation, DNA repair, genome maintenance, and aging-associated biology. A long-lived-specific divergence pattern in a SIRT6-nucleosome context could point to altered chromatin engagement, altered nucleosome-surface recognition, or species-specific remodeling of SIRT6-associated chromatin interactions.

The long-lived species do not highlight exactly the same sequence region. Naked mole-rat emphasizes an approximate L45-E54 patch, while Myotis emphasizes an approximate T110-K117 patch. This could mean that different long-lived species remodel different parts of a broader nucleosome-associated interaction context.

Manual review priority: high.

### 2. NF-kappaB / IkappaBalpha regulatory-interface candidate: 1nfi receptor

The strongest regulatory-interface divergence candidate is:

- Complex: `1nfi__A1_Q04206--1nfi__F1_P25963`
- Chain: receptor
- Species: `naked_mole_rat`, `myotis_lucifugus`
- Contrast class: `long_lived_enhanced_interface_divergence`
- Structure QC: `remapped_interface_supported`

The residue-level packet shows a repeated long-lived signal around the approximate R283-K295 region.

For naked mole-rat, selected residues include R283, R285, Y287, E288, T289, F290, K291, S292, M294, and K295, with additional selected residues E3 and H162.

For Myotis lucifugus, selected residues include R285, Y287, E288, F290, K291, S292, I293, M294, and K295, with additional selected residues E3, I4, and H162.

Biological interpretation:

This is one of the most compelling regulatory candidates because the long-lived species converge on a similar receptor-side region.

NF-kappaB signaling is involved in inflammatory regulation, stress response, immune activation, survival signaling, and senescence-associated transcriptional programs. Interface divergence in the NF-kappaB / IkappaBalpha regulatory context could indicate altered inhibitory binding, altered release threshold, or altered stress/inflammatory responsiveness.

Manual review priority: high.

### 3. PARP1-linked cautious candidate: 7s68 receptor

The PARP1-linked cautious candidate is:

- Complex: `7s68__D1_P09874--7s68__C1_P09874`
- Chain: receptor
- Species: `naked_mole_rat`
- Contrast class: `long_lived_specific_interface_divergence`
- Structure QC: `remapped_interface_supported`

The selected residues include S1 and D2, an approximate local region Q36, S37, P38, M39, F40, D41, G42, and K43, plus C175 and G177.

Biological interpretation:

This case is biologically relevant because PARP1 is involved in DNA damage recognition and DNA repair signaling.

However, it remains cautious because the selected set includes N-terminal residues such as S1 and D2. N-terminal positions can be sensitive to construct boundaries, missing residues, disorder, sequence trimming, or remapping ambiguity.

Structure QC supports remapped interface proximity, which is encouraging, but this case still needs stricter manual inspection than 8g57 or 1nfi.

Manual review priority: medium.

### 4. Maintained SIRT6-nucleosome interface candidate: 8f86 receptor

The maintained-interface SIRT6 candidate is:

- Complex: `8f86__K1_Q8N6T7--8f86__D1_P02281`
- Chain: receptor
- Species: `myotis_lucifugus`
- Contrast class: `long_lived_specific_interface_constraint`
- Structure QC: `remapped_interface_supported`

The selected low-delta interface residues are K169, A170, R171, G172, L173, R174, A175, and R177.

Biological interpretation:

This case is important because it is not a divergent-interface candidate. It is a maintained-interface candidate.

That distinction matters for portability. A long-lived ortholog may be useful not only when it remodels an interface, but also when it preserves a critical interaction surface while allowing other regions to diverge.

Manual review priority: high.

### 5. Shared constrained-interface anchor: 4xhu receptor

The shared constrained-interface anchor is:

- Complex: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Chain: receptor
- Species: `mouse`, `naked_mole_rat`, `myotis_lucifugus`
- Contrast class: `shared_interface_constraint` for long-lived species; `not_applicable` for mouse baseline
- Structure QC: `remapped_interface_supported`

Across species, several low-delta residues recur in the selected interface sets, including P207, K218, G219, I220, R203, L202, G201, and E208.

Biological interpretation:

This is not a longevity-specific hit. Its value is as an internal anchor/control case.

It shows that the pipeline can distinguish shared interface constraint from long-lived-specific divergence.

The exact-numbering fields are weak for this case, but remapped support is complete. That is an important technical observation: sequence-level residue numbers should not be treated as direct PDB residue numbers without remapping.

Manual review priority: control / anchor.

### 6. Mouse outlier and artifact-risk benchmark: 8bhv ligand

The mouse outlier case is:

- PDB: `8bhv`
- Chain: ligand
- Species: `mouse`
- Contrast class: `not_applicable`
- Structure QC: `remapped_interface_supported`

The residue packet and structure-selection summary split this case into two chain-pair-specific complex IDs:

- `8bhv__N1_P12956--8bhv__I1_Q9H9Q4`, with ligand Q / partner h
- `8bhv__P1_P13010--8bhv__J1_Q9H9Q4`, with ligand R / partner j

Biological interpretation:

This is not a longevity candidate. It is an artifact-risk benchmark and mouse-only outlier.

Its value is methodological: it demonstrates why chain-pair-specific structure mapping matters. A single PDB ID can contain multiple relevant chain-pair contexts, and collapsing them can obscure interpretation.

Manual review priority: control / outlier.

## Structure-QC conclusion

The manual-review structure QC reports:

- `11 / 11 manual-review groups: remapped_interface_supported`

This means that every selected review group can be sequence-alignment-remapped to the relevant structural chain and that the remapped residues are interface-proximal under the configured cutoff.

This is a major improvement over a sequence-only interpretation.

However, exact residue-number support varies across cases. In particular, some cases show weak exact support but strong remapped support. This indicates residue-numbering mismatch rather than failure of the biological signal.

The practical conclusion is:

- do not generate final PyMOL or ChimeraX selections directly from `residue_number_1based`;
- use remapped structure residue numbers from the QC output;
- still perform manual visual inspection before making structural figures or biological claims.

## Biological summary

The current core3-expanded run supports three main biological hypotheses for follow-up review.

### Hypothesis 1: long-lived species may remodel SIRT6-nucleosome interfaces

The 8g57 ligand case shows long-lived-specific interface divergence in a SIRT6-nucleosome context.

This suggests possible species-specific remodeling of chromatin engagement, histone/nucleosome recognition, or SIRT6 substrate positioning.

### Hypothesis 2: long-lived species may alter stress/inflammatory regulatory interfaces

The 1nfi receptor case shows a repeated long-lived signal in the NF-kappaB / IkappaBalpha regulatory context.

This suggests a possible interface-level route for altered inflammatory or stress-response regulation.

### Hypothesis 3: portability may require both divergence and preservation

The 8f86 and 4xhu cases show that constrained interfaces are biologically useful, not uninteresting.

A long-lived-species protein may be attractive when important functional surfaces are preserved while other regions diverge.

## Remaining caveats

The current results are still computational and preliminary.

Important caveats:

1. Structure QC confirms remapped interface proximity, not functional effect.
2. Interface-proximal residues do not automatically imply altered binding affinity.
3. The residue patches need manual inspection in 3D.
4. The pipeline does not yet include curated NEGATOME-style negative controls.
5. Some cases involve nucleosome, histone, DNA, or multi-chain contexts where biological interpretation is not purely protein-protein.
6. Mouse-only outliers show that strong divergence can occur outside the long-lived species contrast.

## Recommended next steps

### Manual 3D review

Open the top cases in a structure viewer and inspect:

1. 8g57 ligand in naked mole-rat and Myotis;
2. 1nfi receptor in naked mole-rat and Myotis;
3. 8f86 receptor in Myotis;
4. 7s68 receptor in naked mole-rat;
5. 4xhu receptor across all species;
6. 8bhv ligand mouse outlier cases.

For each case, check:

- chain identity;
- remapped residue numbering;
- whether selected residues form a compact surface patch;
- distance to partner chain;
- whether the surface is protein-protein, protein-DNA, or mixed;
- whether the pattern is biologically plausible.

### Structure-selection export

Generate viewer-ready selections only after using remapped structure residue numbers, not raw `residue_number_1based`.

The safest next technical output would be a structure-viewer selection packet based on the QC remapping output.

### Biological prioritization

Prioritize cases in this order:

1. 1nfi receptor long-lived species, because of repeated long-lived regulatory-interface signal;
2. 8g57 ligand long-lived species, because of SIRT6-nucleosome relevance;
3. 8f86 receptor Myotis, because of maintained-interface portability relevance;
4. 7s68 receptor naked mole-rat, as a cautious DNA-repair-linked candidate;
5. 4xhu as a shared constraint anchor;
6. 8bhv as an outlier/artifact-risk benchmark.

## Working conclusion

The SIRT6 v2 core3-expanded run now provides a coherent preliminary result:

- long-lived-vs-mouse contrast;
- residue-level interface patches;
- unsupervised divergence-profile regimes;
- manual-review prioritization;
- sequence-to-structure remapping support.

The strongest immediate claims are not mechanistic claims.

The strongest current claims are:

1. the pipeline identifies interpretable long-lived-enriched interface-divergence candidates;
2. the pipeline also identifies maintained-interface and shared-constraint cases;
3. the selected residue patches can be remapped onto relevant structures;
4. all 11 manual-review groups are interface-proximal after remapping;
5. the next step is manual 3D inspection and viewer-ready remapped residue selections.

This is a suitable preliminary result layer for guiding structure review, collaborator discussion, and downstream biological prioritization.