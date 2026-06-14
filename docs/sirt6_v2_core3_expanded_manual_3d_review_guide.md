# SIRT6 v2 core3-expanded manual 3D review guide

## Purpose

This guide defines the manual 3D structure-review procedure for the SIRT6 v2 core3-expanded manual-review candidates.

It complements:

- `docs/sirt6_v2_core3_expanded_preliminary_results_summary.md`
- `docs/sirt6_v2_core3_expanded_residue_review_interpretation.md`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_qc.md`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.md`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.csv`

The goal is to turn structure-QC-supported residue patches into visual, manually reviewed biological interpretations.

This document does not claim validated mechanisms. It defines what should be checked before any candidate is used in figures, collaborator updates, proposals, or downstream biological prioritization.

## Core rule

Use remapped structure residues, not raw sequence-level residue numbers.

The viewer-ready selection packet is based on:

- `remapped_reference_to_structure_residue`
- `structure_chain`
- `partner_structure_chain`

from the structure-QC output.

Do not generate final PyMOL, ChimeraX, or Mol* figures directly from `residue_number_1based`.

Reason: some cases show weak exact residue-number support but complete remapped support. This means the biological signal can be real while direct PDB numbering is shifted or otherwise mismatched.

## Files to use during review

Primary viewer-selection file:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.md`

Primary table file:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.csv`

Primary structure-QC file:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_qc.csv`

Recommended review order:

1. Open the viewer-selection Markdown.
2. Copy the relevant PyMOL or ChimeraX selection block.
3. Load the corresponding PDB/mmCIF structure.
4. Apply the patch selection and partner-chain selection.
5. Inspect whether the patch is a coherent physical surface.
6. Record the review outcome using the outcome categories below.

## Review outcome categories

Each case should be assigned one of the following manual outcomes.

### A. Strong structural candidate

Use this when:

- remapped residues form a compact or interpretable 3D surface patch;
- the patch is close to the expected partner chain;
- the chain identity is correct;
- the interface context matches the biological interpretation;
- no obvious numbering, chain, or missing-residue artifact explains the signal.

This category is suitable for figure preparation and collaborator discussion.

### B. Partial structural candidate

Use this when:

- some remapped residues form a plausible interface patch;
- other residues are scattered, ambiguous, or structurally distant;
- the case may still be biologically meaningful but needs a more careful figure or narrower residue subset.

This category is suitable for cautious discussion but not for strong claims.

### C. Mapping or numbering risk

Use this when:

- the selected residues depend heavily on remapping;
- exact numbering is poor;
- the structure has missing residues, construct boundaries, insertion issues, or chain ambiguity;
- the patch is hard to interpret visually.

This category should remain in the audit trail but should not be promoted as a main biological hit without additional checks.

### D. Non-interface or weak visual support

Use this when:

- the remapped residues do not form a coherent interface-proximal patch;
- the selected residues are scattered across unrelated surfaces;
- the biological interpretation is not supported by the inspected structure.

This category should be treated as a negative or deprioritized case.

### E. Control or benchmark case

Use this for shared anchors and outliers that are not intended as longevity-specific hits.

This category includes:

- shared constrained-interface anchors;
- mouse-only outliers;
- artifact-risk benchmarks;
- chain-mapping stress tests.

## General inspection checklist

For each case, inspect:

1. Chain identity:
   - Does the selected structure chain correspond to the intended receptor or ligand?
   - Does the partner chain correspond to the intended interaction partner?
   - Are there multiple similar chains in the same PDB entry?

2. Residue localization:
   - Do the remapped residues lie near the partner chain?
   - Are they exposed on a plausible binding surface?
   - Are they buried, disordered, or visually inaccessible?

3. Patch coherence:
   - Do the residues form one compact patch?
   - Do they form multiple interpretable subpatches?
   - Are they scattered across unrelated regions?

4. Interface type:
   - Is the surface protein-protein?
   - Is it protein-DNA?
   - Is it protein-nucleosome or mixed protein-DNA?
   - Does this match the biological interpretation?

5. Species contrast:
   - Does the long-lived species patch look distinct from mouse or shared-control cases?
   - Does the same region recur in naked mole-rat and Myotis?
   - Is the apparent difference driven by a small number of residues?

6. Artifact risk:
   - Are there missing residues?
   - Are there construct boundaries?
   - Are N-terminal residues involved?
   - Is the interface very small?
   - Is chain-pair assignment unambiguous?
   - Is the signal dependent on exact numbering rather than remapped numbering?

## Priority 1: 1nfi receptor / NF-kappaB regulatory-interface candidate

### Cases

- `1nfi__A1_Q04206--1nfi__F1_P25963`
- Chain role: receptor
- Structure chain: `C`
- Partner chain: `E`
- Species: `naked_mole_rat`, `myotis_lucifugus`
- Biological class: long-lived-enhanced regulatory-interface divergence

### Why it is high priority

This is one of the strongest biological-story candidates.

Both long-lived species highlight a similar receptor-side region around the approximate R283-K295 sequence-level region, and structure QC supports the remapped residues as interface-proximal.

NF-kappaB / IkappaBalpha biology is relevant to inflammatory regulation, stress response, immune activation, survival signaling, and senescence-associated programs.

### What to inspect

Inspect whether the remapped residues:

- form a coherent surface on structure chain `C`;
- lie near partner chain `E`;
- map to the expected NF-kappaB / IkappaBalpha regulatory interface;
- show a repeated visual pattern between naked mole-rat and Myotis;
- include one main surface or separate subpatches.

### Desired review outcome

Strong structural candidate if the remapped residues form a coherent partner-facing regulatory patch.

Partial candidate if the R283-K295-linked region is coherent but E3, I4, or H162 behave as separate features.

## Priority 2: 8g57 ligand / SIRT6-nucleosome long-lived interface divergence

### Cases

- `8g57__A1_Q8N6T7--8g57__H1_P04908`
- Chain role: ligand
- Structure chain: `G`
- Partner chain: `K`
- Species: `naked_mole_rat`, `myotis_lucifugus`
- Biological class: long-lived-specific SIRT6-nucleosome interface divergence

### Why it is high priority

This is the strongest SIRT6-nucleosome divergence candidate.

SIRT6 is relevant to chromatin regulation, DNA repair, genome maintenance, and aging-associated biology. A long-lived-specific divergence pattern in a nucleosome-associated interface could indicate altered chromatin engagement, altered histone or nucleosome recognition, or altered substrate positioning.

### What to inspect

For naked mole-rat, inspect whether the L45-E54-linked sequence-level patch remaps to a coherent physical surface.

For Myotis, inspect whether the T110-K117-linked sequence-level patch remaps to a coherent physical surface.

For both species, check whether the selected residues contact:

- SIRT6;
- histone surface;
- nucleosomal DNA;
- mixed protein-DNA interface context.

### Desired review outcome

Strong structural candidate if one or both long-lived species show coherent nucleosome-facing or SIRT6-facing remapped patches.

Partial candidate if the patches are interface-proximal but split across different subregions.

## Priority 3: 8f86 receptor / maintained SIRT6-nucleosome interface

### Case

- `8f86__K1_Q8N6T7--8f86__D1_P02281`
- Chain role: receptor
- Structure chain: `K`
- Partner chain: `D`
- Species: `myotis_lucifugus`
- Biological class: long-lived-specific interface constraint

### Why it is high priority

This case is important because it is a maintained-interface candidate, not a divergent-interface candidate.

For portability, preserved interaction surfaces can be as important as remodeled ones. A long-lived ortholog may be attractive if it preserves a critical interface while allowing divergence elsewhere.

### What to inspect

Inspect whether the K169-R177-linked low-delta patch:

- forms a compact surface;
- faces partner chain `D`;
- appears compatible with a maintained SIRT6-nucleosome interaction;
- is visually distinct from high-divergence candidate patches.

### Desired review outcome

Strong maintained-interface candidate if the remapped residues form a coherent preserved contact patch.

## Priority 4: 7s68 receptor / PARP1-linked cautious candidate

### Case

- `7s68__D1_P09874--7s68__C1_P09874`
- Chain role: receptor
- Structure chain: `A`
- Partner chain: `B`
- Species: `naked_mole_rat`
- Biological class: PARP1-linked long-lived-specific interface divergence

### Why it is cautious

This case is biologically interesting because PARP1-linked contexts relate to DNA damage recognition and repair signaling.

However, it includes N-terminal sequence-level residues such as S1 and D2. N-terminal positions can be sensitive to construct boundaries, disorder, missing residues, and remapping ambiguity.

### What to inspect

Inspect whether:

- the S1/D2-linked residues are actually resolved and meaningful after remapping;
- the Q36-K43-linked region forms a real surface patch;
- the C175/G177-linked residues are part of the same interface context or a separate feature;
- the patch is close to partner chain `B`;
- the interpretation is protein-protein, DNA-associated, or mixed.

### Desired review outcome

Partial or cautious candidate unless the remapped residues form a clear, coherent interface patch and the N-terminal residues are structurally meaningful.

## Priority 5: 4xhu receptor / shared constrained-interface anchor

### Cases

- `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Chain role: receptor
- Structure chain: `C`
- Partner chain: `D`
- Species: `mouse`, `naked_mole_rat`, `myotis_lucifugus`
- Biological class: shared constrained-interface anchor

### Why it matters

This is not a longevity-specific hit.

Its value is methodological and interpretive: it shows a shared constrained interface across species, and it demonstrates that remapping is necessary because exact numbering can be weak while remapped interface support is complete.

### What to inspect

Inspect whether the recurring low-delta residues:

- form a conserved surface across species;
- lie near partner chain `D`;
- are visually similar across mouse, naked mole-rat, and Myotis;
- can serve as an internal visual anchor for interpreting divergent cases.

### Desired review outcome

Control or benchmark case.

Use it to calibrate interpretation of conserved interface surfaces.

## Priority 6: 8bhv ligand / mouse outlier and artifact-risk benchmark

### Cases

- `8bhv__N1_P12956--8bhv__I1_Q9H9Q4`
- Structure chain: `Q`
- Partner chain: `h`

and:

- `8bhv__P1_P13010--8bhv__J1_Q9H9Q4`
- Structure chain: `R`
- Partner chain: `j`

### Why it matters

This is not a longevity candidate.

Its value is as a mouse-only outlier and chain-pair ambiguity benchmark. The viewer-selection export intentionally includes structure and partner chain IDs in selection names so the two 8bhv cases do not overwrite each other in PyMOL.

### What to inspect

Inspect whether each 8bhv chain-pair case:

- maps to the correct ligand chain;
- lies close to the correct partner chain;
- forms a compact patch or scattered residues;
- looks like a real mouse-specific divergence event or a structure/mapping artifact.

### Desired review outcome

Control or artifact-risk benchmark.

Do not promote as a longevity-specific biological hit.

## Suggested manual review table

For each case, record:

- reviewer;
- date;
- PDB ID;
- complex ID;
- chain role;
- structure chain;
- partner chain;
- target species;
- selection source;
- visual patch coherence: strong, partial, weak, none;
- interface proximity: strong, partial, weak, none;
- artifact risk: low, medium, high;
- biological plausibility: high, medium, low;
- outcome category: A, B, C, D, or E;
- notes;
- screenshot path if available.

## Figure-candidate criteria

A case is suitable for a preliminary figure if:

1. the remapped residues form a coherent visible patch;
2. the patch is close to the expected partner chain;
3. the chain and partner-chain mapping are unambiguous;
4. the biological interpretation is clear;
5. the figure caption can honestly describe the result as computational and preliminary.

Recommended first figure candidates:

1. `1nfi` receptor long-lived species, if the R283-K295-linked region is visually coherent;
2. `8g57` ligand long-lived species, if the SIRT6-nucleosome patches are visually coherent;
3. `8f86` receptor Myotis, if the maintained-interface patch is compact;
4. `4xhu` receptor as a conserved-interface control.

## Working conclusion

The current pipeline has reached the point where manual 3D review is meaningful.

The strongest current computational claim is:

- the core3-expanded run identifies interpretable residue-level interface patches;
- these patches are supported by sequence-to-structure remapping;
- viewer-ready selections now allow direct manual inspection in PyMOL, ChimeraX, or Mol*.

The next step is not more numerical summarization. The next step is visual structure review and recording case-level outcomes.