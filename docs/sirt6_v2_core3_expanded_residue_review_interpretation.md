# SIRT6 v2 core3-expanded residue-review interpretation

## Purpose

This note interprets the residue-level manual-review packet for the SIRT6 v2 core3-expanded run.

It complements:

- `docs/sirt6_v2_core3_expanded_manual_review_shortlist.md`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_residue_shortlist.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_residue_shortlist.md`
- `scripts/export_core3_expanded_manual_review_residue_shortlist.py`

The goal is to move from complex-level and cluster-level signals to concrete residue-level observations that can be checked on 3D structures.

This note is interpretive. It does not validate any biological mechanism by itself. Each candidate residue set still requires manual structural inspection, chain verification, and residue-mapping verification.

## Important residue-numbering caveat

The residue labels in the manual-review packet come from the mapped residue-delta output:

- `residue_index`
- `residue_number_1based`
- `residue_aa`
- `residue_label`

These labels should be treated as mapped sequence-level positions unless verified otherwise.

They should not yet be assumed to be direct PDB residue numbers.

Before generating PyMOL, ChimeraX, or Mol* selections, each case needs residue-numbering validation against the corresponding structure, chain mapping, missing residues, and any sequence truncation.

This is especially important for:

- histone/nucleosome complexes;
- N-terminal residues;
- structures with missing loops;
- protein-DNA or protein-nucleosome contexts;
- cases with multiple candidate chain pairs under the same PDB ID.

## What the residue packet adds

The previous manual-review shortlist identified six priority review regimes:

1. SIRT6-nucleosome long-lived interface divergence candidates;
2. NF-kappaB regulatory-interface rewiring candidates;
3. PARP1-linked cautious long-lived-specific candidates;
4. SIRT6-nucleosome maintained-interface candidates;
5. shared constrained-interface anchors;
6. singleton divergent outliers or artifact-risk benchmarks.

The residue packet adds exact candidate residues for each regime.

For divergent candidates, the packet selects high-delta interface residues. These are positions where the target-species ortholog differs strongly from the human reference at the mapped interface.

For constrained candidates, the packet selects low-delta interface residues. These are positions where the interface appears preserved relative to the background.

Biologically, both patterns matter:

- interface divergence can indicate altered partner recognition, altered binding strength, altered substrate engagement, or species-specific remodeling;
- interface constraint can indicate preservation of a critical interaction surface, which may be important for portability.

## Priority 1: 8g57 ligand / SIRT6-nucleosome long-lived interface divergence

### Case

- Complex: `8g57__A1_Q8N6T7--8g57__H1_P04908`
- Chain: ligand
- Species: `naked_mole_rat`, `myotis_lucifugus`
- Review class: SIRT6-nucleosome long-lived interface divergence candidate
- Contrast class: `long_lived_specific_interface_divergence`

### Residue-level observation

For naked mole-rat, the selected high-delta interface residues include a compact local block:

```text

L45, E46, Y47, L48, T49, A50, E51, I52, E54

```

with additional selected residues:

```text

A42, Q14, K117

```

For Myotis lucifugus, the selected residues include another compact local block:

```text

T110, E111, S112, H113, H114, K115, A116, K117

```

with additional selected residues:

```text

G12, E46, L53, R61

```

### Biological interpretation

This is one of the most interesting outputs because the high-delta residues are not only isolated single positions. They appear to include contiguous or near-contiguous residue blocks.

That pattern is consistent with a candidate surface patch rather than random distributed noise.

Because 8g57 is a SIRT6-nucleosome context, possible biological interpretations include:

- altered SIRT6-nucleosome engagement;
- altered recognition of histone or nucleosomal surface features;
- altered chromatin-substrate positioning;
- species-specific remodeling of the SIRT6-associated chromatin interface.

The naked mole-rat and Myotis signals do not appear identical. Naked mole-rat highlights the approximate L45-E54 region, while Myotis highlights the approximate T110-K117 region. This could mean that different long-lived species remodel different parts of the same broad interface context.

### Manual structure-review questions

Check whether the selected residues:

1. map to the same physical nucleosome-facing or SIRT6-facing surface;
2. contact SIRT6, histone, DNA, or a mixed protein-DNA surface;
3. form one or more coherent patches in 3D;
4. are affected by histone numbering conventions or missing residues;
5. are weaker or absent in the mouse baseline.

### Current interpretation

High-priority candidate.

Use cautious language until residue numbering and 3D localization are verified.

## Priority 2: 1nfi receptor / NF-kappaB regulatory-interface rewiring

### Case

- Complex: `1nfi__A1_Q04206--1nfi__F1_P25963`
- Chain: receptor
- Species: `naked_mole_rat`, `myotis_lucifugus`
- Review class: NF-kappaB regulatory-interface rewiring candidate
- Contrast class: `long_lived_enhanced_interface_divergence`

### Residue-level observation

Both long-lived species highlight a similar receptor-side region.

For naked mole-rat, selected residues include:

```text

R283, R285, Y287, E288, T289, F290, K291, S292, M294, K295

```

with additional selected residues:

```text

E3, H162

```

For Myotis lucifugus, selected residues include:

```text

R285, Y287, E288, F290, K291, S292, I293, M294, K295

```

with additional selected residues:

```text

E3, I4, H162

```

### Biological interpretation

This is a strong regulatory-interface candidate because the long-lived species show a repeated residue region around approximately R283-K295.

NF-kappaB regulation is relevant because the NF-kappaB / IkappaBalpha system controls inflammatory signaling, stress responses, immune activation, survival, and senescence-associated programs.

A long-lived-enhanced interface divergence pattern in this complex could indicate altered regulatory sequestration, altered release threshold, or altered inhibitor interaction.

The repeated region across naked mole-rat and Myotis makes this more compelling than a single-species-only signal.

### Manual structure-review questions

Check whether the selected residues:

1. lie on the NF-kappaB / IkappaBalpha contact surface;
2. cluster on one exposed structural face;
3. are close to known regulatory or inhibitor-binding regions;
4. are consistent across naked mole-rat and Myotis after residue remapping;
5. could be affected by truncation or chain-role assignment.

### Current interpretation

High-priority regulatory-interface candidate.

This should be framed as possible stress/inflammation regulatory rewiring, not as direct evidence of lifespan extension.

## Priority 3: 7s68 receptor / PARP1-linked cautious long-lived-specific candidate

### Case

- Complex: `7s68__D1_P09874--7s68__C1_P09874`
- Chain: receptor
- Species: `naked_mole_rat`
- Review class: PARP1-linked cautious long-lived-specific candidate
- Contrast class: `long_lived_specific_interface_divergence`

### Residue-level observation

The selected high-delta interface residues include:

```text

S1, D2

```

and a local region:

```text

Q36, S37, P38, M39, F40, D41, G42, K43

```

with additional selected residues:

```text

C175, G177

```

### Biological interpretation

This case has strong residue-level delta values, but it should remain cautious.

PARP1-linked contexts are biologically relevant because PARP1 participates in DNA damage detection and repair signaling. However, the selected residues include very N-terminal positions such as S1 and D2.

N-terminal positions can be risky in structural interpretation because they may involve:

- flexible or disordered regions;
- construct boundaries;
- sequence trimming;
- alignment or remapping ambiguity;
- missing residues in experimental structures.

The approximate Q36-K43 region may still be biologically interesting if it maps to a real interface-proximal surface.

### Manual structure-review questions

Check whether the selected residues:

1. are actually present in the experimental structure;
2. map cleanly to the receptor chain;
3. contact the partner chain or DNA-associated region;
4. form a coherent physical patch;
5. remain meaningful after excluding possible N-terminal mapping artifacts.

### Current interpretation

Secondary candidate.

Do not promote as a top hit unless structural review confirms that the residues map to a real interface surface.

## Priority 4: 8f86 receptor / Myotis maintained SIRT6-nucleosome interface

### Case

- Complex: `8f86__K1_Q8N6T7--8f86__D1_P02281`
- Chain: receptor
- Species: `myotis_lucifugus`
- Review class: SIRT6-nucleosome maintained-interface candidate
- Contrast class: `long_lived_specific_interface_constraint`

### Residue-level observation

The selected low-delta interface residues are:

```text

K169, A170, R171, G172, L173, R174, A175, R177

```

### Biological interpretation

This is a maintained-interface candidate rather than a divergent-interface candidate.

That distinction matters. A long-lived ortholog does not need to change every important interface to be biologically interesting. In some cases, portability may depend on preserving a critical interaction surface while allowing divergence elsewhere.

The selected residues form a compact approximate K169-R177 region, which is consistent with a potentially preserved surface patch.

### Manual structure-review questions

Check whether the selected residues:

1. form a compact SIRT6-nucleosome contact surface;
2. are conserved at the physical interface;
3. sit near histone, DNA, or mixed nucleosome-contact features;
4. remain low-delta relative to the surrounding background;
5. are correctly mapped between sequence and structure.

### Current interpretation

High-value counterexample to a purely divergence-focused view.

This case supports the idea that the pipeline can identify preserved interaction surfaces as well as remodeled ones.

## Priority 5: 4xhu receptor / shared constrained-interface anchor

### Case

- Complex: `4xhu__A1_P09874--4xhu__B1_Q9UNS1`
- Chain: receptor
- Species: `mouse`, `naked_mole_rat`, `myotis_lucifugus`
- Review class: shared constrained-interface anchor
- Contrast class: `shared_interface_constraint` for long-lived species; `not_applicable` for mouse baseline

### Residue-level observation

Across species, several low-delta residues recur in the selected interface sets, including:

```text

P207, K218, G219, I220, R203, L202, G201, E208

```

Additional species-specific selected residues include:

```text

mouse: I204, G252, V315, D317

naked_mole_rat: I204, V315, D317, N253

myotis_lucifugus: Q200, P206, L251, G252

```

### Biological interpretation

This is not a longevity-specific hit. It is an anchor/control case.

Its value is methodological: the pipeline can identify a strongly constrained interface across mouse, naked mole-rat, and Myotis.

That helps distinguish true candidate divergence from generally conserved interaction surfaces.

Biologically, a shared constrained PARP1-linked interface may represent a conserved DNA repair or replication-associated interaction that should not be disrupted.

### Manual structure-review questions

Check whether the shared residues:

1. form a common conserved surface across all species;
2. map to the expected receptor-side interface;
3. remain low-delta relative to non-interface background;
4. are not simply an artifact of identical or near-identical sequence segments;
5. can serve as a visual anchor for interpreting divergent cases.

### Current interpretation

Useful anchor/control.

Do not present as a longevity-specific candidate.

## Priority 6: 8bhv ligand / mouse singleton divergent outlier split into two complexes

### Case

- Complexes:
  - `8bhv__N1_P12956--8bhv__I1_Q9H9Q4`
  - `8bhv__P1_P13010--8bhv__J1_Q9H9Q4`
- Chain: ligand
- Species: `mouse`
- Review class: singleton divergent outlier / artifact-risk benchmark
- Contrast class: `not_applicable`

### Residue-level observation

The residue packet separates the 8bhv mouse outlier into two complex IDs.

For `8bhv__N1_P12956--8bhv__I1_Q9H9Q4`, selected residues are:

```text

L168, I169, R170, D171, R172, L173, T167

```

For `8bhv__P1_P13010--8bhv__J1_Q9H9Q4`, selected residues are:

```text

K219, P220, R221, G222, L223, F224, S225

```

### Biological interpretation

This is an artifact-risk benchmark rather than a longevity candidate.

The fact that the outlier splits into two distinct complex IDs is important. It means the previous combined view could obscure chain-pair-specific behavior.

Because this is a mouse-only divergent signal, it warns that the pipeline can detect strong interface divergence that is not longevity-specific.

Possible explanations include:

- genuine mouse-specific interface divergence;
- chain-pair-specific effects;
- residue remapping issues;
- small-interface effects;
- structure or numbering artifacts.

### Manual structure-review questions

Check whether each 8bhv residue group:

1. maps to the correct ligand chain;
2. lies on a true partner-contacting surface;
3. is affected by chain-pair selection;
4. reflects a compact physical patch or a mapping artifact;
5. should be used as a negative/outlier example in downstream interpretation.

### Current interpretation

Useful stress test and cautionary control.

Do not use as a longevity-specific candidate.

## Cross-case observations

### Compact residue patches are more interesting than isolated positions

The strongest candidates are those where selected residues form compact or repeated regions:

- 8g57 naked mole-rat: approximate L45-E54 region;
- 8g57 Myotis: approximate T110-K117 region;
- 1nfi long-lived species: approximate R283-K295 region;
- 8f86 Myotis: approximate K169-R177 region.

These patterns are more plausible as structural interface patches than isolated high-delta residues.

### Repeated long-lived patterns increase priority

The 1nfi receptor case is strengthened by similarity between naked mole-rat and Myotis.

The 8g57 case is strengthened by long-lived-specific contrast, but the two long-lived species appear to highlight different residue regions. This may still be biologically meaningful, but it requires careful 3D inspection.

### N-terminal residues require caution

The 7s68 case includes S1 and D2. These may be real, but N-terminal positions often have higher mapping and structural-availability risk.

Manual review should explicitly check whether those residues are resolved in the structure and whether they participate in a real interface.

### Constrained interfaces are useful, not boring

The 8f86 and 4xhu cases show why interface constraint matters.

A useful long-lived-species variant may preserve some interaction surfaces while changing other parts of the protein. This is directly relevant to portability: conserved surfaces may indicate compatibility-preserving regions.

## Manual structure-review checklist

For each review case, inspect:

1. Chain identity:
   - Does the chain in the packet correspond to the intended receptor or ligand?
   - Is the selected biological interpretation consistent with the selected chain?
2. Residue mapping:
   - Do `residue_number_1based` labels correspond to the intended structural residues?
   - Are there missing residues, insertion codes, truncations, or construct boundaries?
3. Interface localization:
   - Are selected residues physically near the partner chain, nucleosome surface, DNA, or relevant ligand?
   - Are they exposed on a plausible binding surface?
4. Patch coherence:
   - Do selected residues form one or more compact 3D patches?
   - Or are they scattered across unrelated surfaces?
5. Species contrast:
   - Is the pattern stronger in long-lived species than in mouse?
   - Is the mouse signal near-neutral, shared, or divergent?
6. Artifact risk:
   - Is the signal driven by very few residues?
   - Is the interface very small?
   - Is the case affected by chain-pair ambiguity or structure-specific numbering?

## Working conclusion

The residue packet provides a useful intermediate result between numerical clustering and manual 3D structure inspection.

The most promising candidates for immediate structural review are:

1. 8g57 ligand in naked mole-rat and Myotis;
2. 1nfi receptor in naked mole-rat and Myotis;
3. 8f86 receptor in Myotis as a maintained-interface case.

The 7s68 case remains biologically interesting but requires stricter mapping checks.

The 4xhu case should be used as a shared constraint anchor.

The 8bhv mouse case should be used as an outlier and artifact-risk benchmark.

The next step is to validate whether these sequence-level residue patches correspond to coherent physical surfaces in the relevant 3D structures.
