# Poster corrections for longevity_port.png

The poster image (`docs/images/longevity_port.png`) was AI-generated and contains
fabricated 3D structure images, incorrect chain labels, wrong protein names, a
misleading color legend, and several data-level inconsistencies with the actual
pipeline results. This document lists every error found and the authoritative
source for each correction.

**Corrected poster assets:**
- Full HTML poster with real ChimeraX renders: `docs/poster/poster.html`
- SVG summary (embeddable in README): `docs/poster/poster_summary.svg`
- Labeled ChimeraX scripts: `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/panel*.cxc`

---

## A. Panel 4 — "3D VIEW — 1NFI: NF-KAPPA B / IKAPPBALPHA INTERFACE"

### A1. Wrong chain letters

| Poster label | Correct label | Source |
|---|---|---|
| RelA/p65 **(chain A)** | RelA/p65 **(chain C)** — target (gray cartoon) | `viewer_structure_selections.csv` row for 1nfi: `structure_chain=C` |
| NF-kappB **(chain B)** | IkappaBAlpha **(chain E)** — partner (blue surface) | `viewer_structure_selections.csv` row for 1nfi: `partner_structure_chain=E` |

### A2. Wrong partner protein name

The poster labels the partner as **"NF-kappB"**. RelA/p65 already IS the NF-kappaB
subunit (UniProt Q04206). The partner chain E is **IkappaBAlpha** (UniProt P25963,
mouse ortholog IKBA_MOUSE).

Correct panel title: **"1NFI: RelA/p65 — IkappaBAlpha interface"**

Source: `divergence_profile_clusters_pca2d.csv`, row `1nfi, ligand, mouse` →
`source_uniprot=P25963`, mouse ortholog name `IKBA_MOUSE`.

### A3. Fabricated 3D image — must be replaced

The poster shows a multi-colored structure (red, yellow, blue, green residues on
both chains). The actual ChimeraX renders use only three visual elements:

| Element | Color | Meaning |
|---|---|---|
| Target chain C cartoon | **Gray** | RelA/p65 backbone |
| Partner chain E surface | **Semi-transparent blue** | IkappaBAlpha |
| Candidate residue spheres | **Orange** | Top-12 divergent residues by embedding delta |

There is no red, no green, no multi-color residue coding in the real renders.

**Replacement images** (pick one species + view, or show both species):

| Species | View | File |
|---|---|---|
| Naked mole-rat | Closeup | `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/1nfi_receptor_c_e_naked_mole_rat_long_lived_enhanced_interface_divergence_closeup.png` |
| Naked mole-rat | Overview | `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/1nfi_receptor_c_e_naked_mole_rat_long_lived_enhanced_interface_divergence_overview.png` |
| Myotis lucifugus | Closeup | `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/1nfi_receptor_c_e_myotis_lucifugus_long_lived_enhanced_interface_divergence_closeup.png` |
| Myotis lucifugus | Overview | `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/1nfi_receptor_c_e_myotis_lucifugus_long_lived_enhanced_interface_divergence_overview.png` |

### A4. Wrong color legend

Replace the three-color legend (red / blue / gray) with:

- **Orange spheres** — candidate divergent residues (top-12 by embedding delta)
- **Blue surface** — partner chain (IkappaBAlpha, chain E)
- **Gray cartoon** — target chain backbone (RelA/p65, chain C)

Source: ChimeraX script `1nfi_receptor_c_e_*.cxc` — `color ... orange`,
`color /E blue surfaces`, `color /C gray`.

### A5. Interpretation text correction

The poster's red box below panel 4 says:
> "Divergence concentrated at regulatory interface.
> Potential impact on NF-kappaB / kappaBAlpha binding and signaling regulation."

This is acceptable, but should note that 1nfi is the **only statistically
significant** divergent candidate (signal_class = `interface_divergent`,
Cohen's d = 0.66–0.70). Consider emphasizing this.

Source: `manual_review_structure_selection_summary.csv`, 1nfi rows.

---

## B. Panel 5 — "3D VIEW — 8G57: SIRT6-NUCLEOSOME INTERFACE"

### B1. Wrong chain letters

| Poster label | Correct label | Source |
|---|---|---|
| SIRT6 **(chain A)** | SIRT6 **(chain K)** — partner (blue surface) | `viewer_structure_selections.csv`: `partner_structure_chain=K` |
| Nucleosome **(chain B)** | Histone H2A **(chain G)** — target (gray cartoon) | `viewer_structure_selections.csv`: `structure_chain=G` |

### B2. Wrong protein name and swapped roles

Two errors compounded:

1. **"Nucleosome"** is the whole complex. The specific protein analyzed is
   **Histone H2A** (UniProt P04908, mouse ortholog H2A3_MOUSE). Use
   "Histone H2A" in the label.

2. **Roles are swapped.** The poster presents SIRT6 as the target chain ("chain A",
   left/prominent position). In reality SIRT6 (Q8N6T7, chain K) is the **partner**
   shown as a blue surface. The **target being analyzed** for divergence is the
   histone H2A chain G (gray cartoon with orange residues).

Correct panel title: **"8G57: Histone H2A (chain G) — SIRT6 (chain K) interface"**

Correct layout labels:
- Gray cartoon chain = **Histone H2A (chain G)** — the chain analyzed for divergence
- Blue surface = **SIRT6 (chain K)** — the interaction partner

Source: CXC script `8g57_ligand_g_k_*.cxc` — `cartoon /G`, `surface /K`.

### B3. Fabricated 3D image — must be replaced

The poster shows a purple/green protein. The actual render shows a small helical
histone H2A chain (gray) with orange candidate residues, pressed against a large
globular SIRT6 surface (blue).

**Replacement images:**

| Species | View | File |
|---|---|---|
| Naked mole-rat | Closeup | `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/8g57_ligand_g_k_naked_mole_rat_long_lived_specific_interface_divergence_closeup.png` |
| Naked mole-rat | Overview | `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/8g57_ligand_g_k_naked_mole_rat_long_lived_specific_interface_divergence_overview.png` |
| Myotis lucifugus | Closeup | `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/8g57_ligand_g_k_myotis_lucifugus_long_lived_specific_interface_divergence_closeup.png` |
| Myotis lucifugus | Overview | `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/8g57_ligand_g_k_myotis_lucifugus_long_lived_specific_interface_divergence_overview.png` |

### B4. Wrong color legend

Same fix as panel 4 (section A4). Replace red/blue/gray with orange/blue/gray.

### B5. Missing "not significant" qualifier

The poster presents 8g57 as the priority-1 candidate without noting that its
signal is `interface_divergent_not_significant` (enrichment ratio 1.28–1.41,
Cohen's d 0.35–0.50 — small effect, below significance threshold).

The red interpretation box below panel 5 says:
> "Divergence at SIRT6-nucleosome interface.
> Potential relevance to chromatin regulation and DNA repair."

This should include a caveat, e.g.:
> "Trend-level divergence at SIRT6-nucleosome interface (not statistically
> significant; Cohen's d = 0.35–0.50). Requires validation with larger sample."

Source: `manual_review_structure_selection_summary.csv`, 8g57 rows:
`signal_class=interface_divergent_not_significant`.

---

## C. Panel 6 — "DIVERGENCE VS CONSTRAINT: TWO SIDES OF THE SAME COIN"

### C1. Fabricated thumbnail images

All small structure thumbnails under "DIVERGENCE (Rewiring / Incompatibility Risk)"
and "CONSTRAINT (Preserved Compatibility)" are AI-generated and do not match any
actual ChimeraX renders. The real renders all use a consistent gray/blue/orange
color scheme on a white background.

**Replacement source:** Use crops or thumbnails from the contact sheet at
`data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_contact_sheet.png`,
or from individual render files below.

Suggested divergence examples:
- 1nfi (NMR): `1nfi_receptor_c_e_naked_mole_rat_long_lived_enhanced_interface_divergence_closeup.png`
- 8g57 (NMR): `8g57_ligand_g_k_naked_mole_rat_long_lived_specific_interface_divergence_closeup.png`
- 7s68 (NMR): `7s68_receptor_a_b_naked_mole_rat_long_lived_specific_interface_divergence_closeup.png`

Suggested constraint examples:
- 4xhu (bat): `4xhu_receptor_c_d_myotis_lucifugus_shared_interface_constraint_closeup.png`
- 4xhu (NMR): `4xhu_receptor_c_d_naked_mole_rat_shared_interface_constraint_closeup.png`
- 8f86 (bat): `8f86_receptor_k_d_myotis_lucifugus_long_lived_specific_interface_constraint_closeup.png`

All files are in `data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/`.

---

## D. Panel 3 — "SIRT6 V2 CORE3 EXPANDED: CANDIDATE SUMMARY"

### D1. Missing candidate: 7s68 (PARP1 homodimer)

The summary table shows 5 PDB entries (1nfi, 8g57, 8f86, 4xhu, 8bhv) but omits
**7s68** (priority 3: PARP1-linked cautious long-lived-specific candidate).

Add a row for 7s68:

| PDB | Biological context | Signal type | Notes |
|---|---|---|---|
| 7s68 | PARP1 homodimer (P09874 self-interaction) | Long-lived specific interface divergence | Naked mole-rat only; not significant (Cohen's d = 0.38) |

Source: `manual_review_structure_selection_summary.csv`, 7s68 row;
`viewer_structure_selections.csv`, row 5.

The 3D render exists:
- `7s68_receptor_a_b_naked_mole_rat_long_lived_specific_interface_divergence_closeup.png`
- `7s68_receptor_a_b_naked_mole_rat_long_lived_specific_interface_divergence_overview.png`

### D2. Candidate table — signal type accuracy

Verify the signal type column in the table matches the actual signal_class from
the data. The correct values are:

| PDB | Correct signal_class | Correct contrast_class | Significant? |
|---|---|---|---|
| 1nfi | `interface_divergent` | `long_lived_enhanced_interface_divergence` | **Yes** |
| 8g57 | `interface_divergent_not_significant` | `long_lived_specific_interface_divergence` | No |
| 7s68 | `interface_divergent_not_significant` | `long_lived_specific_interface_divergence` | No |
| 8f86 | `interface_constrained_not_significant` | `long_lived_specific_interface_constraint` | No |
| 4xhu | `interface_constrained` | `shared_interface_constraint` | **Yes** (constraint) |
| 8bhv | `interface_divergent` | `not_applicable` (control) | N/A |

Source: `manual_review_structure_selection_summary.csv`.

### D3. Priority ordering vs statistical strength

The data ranks 8g57 as priority 1 and 1nfi as priority 2. But 1nfi is the only
candidate with statistically significant interface divergence (Cohen's d 0.66–0.70
vs 8g57's 0.35–0.50). The poster should either:

- (a) Reorder to put 1nfi first, or
- (b) Clearly explain the priority criteria (e.g. biological relevance of the
  SIRT6 target may justify promoting it despite weaker statistics)

---

## E. Panel 2 — "EVIDENCE LADDER" and bottom banner

### E1. "11/11" framing is misleading

The poster states in two places:
- "11 / 11 groups show remapped interface support"
- "11/11 candidates are well-supported with strong structural support"

Issues:
1. "11" counts **(PDB x species) QC groups**, not independent candidates. There
   are only **6 complexes** (8g57, 1nfi, 7s68, 8f86, 4xhu, 8bhv).
2. 3 of the 11 groups are **controls** with `not_applicable` contrast class
   (4xhu-mouse, 8bhv-mouse Q/h, 8bhv-mouse R/j).
3. "Strong structural support" refers to remapped residue proximity QC, not to
   statistical significance of the biological signal.

Suggested fix:
> "11/11 structure-species groups pass remapped-residue interface proximity QC.
> Covers 6 complexes across 3 species (including 3 control groups)."

Source: `manual_review_structure_qc.md`, table at line 17–18.

### E2. Bottom banner "Top candidates: 1nfi, 8g57"

This is acceptable but should note:
- 1nfi: statistically significant divergence (Cohen's d = 0.66–0.70)
- 8g57: trend-level only, not significant (Cohen's d = 0.35–0.50)

---

## F. Panel 1 — "LONGEVITY PORT PIPELINE" flowchart

### F1. Species icons/labels

Verify the flowchart's species list matches the actual pipeline species. The
pipeline analyzes orthologs for:
- **Naked mole-rat** (Heterocephalus glaber)
- **Myotis lucifugus** (little brown bat)
- **Mouse** (Mus musculus) — as short-lived reference

Source: `divergence_profile_clusters_pca2d.csv`, `target_species` column.

The poster mentions "naked mole-rat, bowhead whale, bats" in panel 1, but the
actual data contains **no bowhead whale** entries. Either remove bowhead whale
from the flowchart or note it as a planned future species.

---

## G. Protein name reference table

For all panels, use these authoritative protein names:

| UniProt | Gene | Protein name | PDB | Chain | Role in poster |
|---|---|---|---|---|---|
| Q04206 | RELA | NF-kappaB p65 (RelA) | 1nfi | C (target) | Gray cartoon |
| P25963 | NFKBIA | IkappaBAlpha | 1nfi | E (partner) | Blue surface |
| Q8N6T7 | SIRT6 | Sirtuin-6 | 8g57 | K (partner) | Blue surface |
| P04908 | H2AFZ | Histone H2A | 8g57 | G (target) | Gray cartoon |
| Q8N6T7 | SIRT6 | Sirtuin-6 | 8f86 | K (target) | Gray cartoon |
| P02281 | HIST1H2BN | Histone H2B type 1 | 8f86 | D (partner) | Blue surface |
| P09874 | PARP1 | Poly(ADP-ribose) polymerase 1 | 7s68 | A (target) | Gray cartoon |
| P09874 | PARP1 | Poly(ADP-ribose) polymerase 1 | 7s68 | B (partner) | Blue surface (homodimer) |
| P09874 | PARP1 | Poly(ADP-ribose) polymerase 1 | 4xhu | C (target) | Gray cartoon |
| Q9UNS1 | TIMELESS | Timeless | 4xhu | D (partner) | Blue surface |
| P12956 | XRCC6 | Ku70 | 8bhv | N (receptor) | — |
| Q9H9Q4 | NHEJ1 | XLF / Cernunnos | 8bhv | Q,R (target) | Gray cartoon |
| P13010 | XRCC5 | Ku80 | 8bhv | P (receptor) | — |

Source: `divergence_profile_clusters_pca2d.csv` mouse ortholog names;
`viewer_structure_selections.csv` chain assignments.

---

## H. Global color scheme fix

The poster uses a fabricated multi-color scheme across panels 4, 5, and 6. All
actual ChimeraX renders use a uniform scheme:

| Visual element | Color | Meaning |
|---|---|---|
| Target chain backbone | **Gray** cartoon | The chain analyzed for embedding divergence |
| Partner chain | **Semi-transparent blue** surface | The interaction partner |
| Candidate residues | **Orange** ball-and-stick | Top residues by embedding delta (remapped to structure) |
| Background | **White** | — |

There is **no** red/green/multi-color residue classification in the actual renders.
All candidate residues are orange regardless of divergence subtype.

Source: every `.cxc` script in
`data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts/`.

---

## I. 8bhv classification note

The poster labels 8bhv as "Singleton divergent outlier / artifact-risk benchmark."
However, the full PCA cluster data shows that 8bhv's ligand (XLF/NHEJ1, Q9H9Q4)
has `contrast_class = long_lived_enhanced_interface_divergence` for both Myotis and
naked mole-rat — the **same classification as 1nfi**, the top divergent candidate.

This is not necessarily an error to fix in the poster, but warrants a footnote or
discussion point: either 8bhv's ligand-side signal is real (and shouldn't be
dismissed as artifact), or this classification can produce false positives (which
casts doubt on 1nfi's classification too).

Source: `divergence_profile_clusters_pca2d.csv`, rows for
`8bhv__N1_P12956--8bhv__I1_Q9H9Q4, ligand, myotis_lucifugus` and
`ligand, naked_mole_rat`.

---

## Quick checklist

- [ ] Panel 4: fix chain labels A→C, B→E
- [ ] Panel 4: fix partner name "NF-kappB" → "IkappaBAlpha"
- [ ] Panel 4: replace AI image with real ChimeraX render
- [ ] Panel 4: fix color legend to orange/blue/gray
- [ ] Panel 5: fix chain labels A→K, B→G
- [ ] Panel 5: fix protein name "Nucleosome" → "Histone H2A"
- [ ] Panel 5: fix role swap (SIRT6 = partner surface, H2A = target cartoon)
- [ ] Panel 5: replace AI image with real ChimeraX render
- [ ] Panel 5: add "not significant" caveat to interpretation box
- [ ] Panel 5: fix color legend to orange/blue/gray
- [ ] Panel 6: replace AI thumbnails with real ChimeraX render crops
- [ ] Panel 3: add missing 7s68 row
- [ ] Panel 3: verify signal types match data
- [ ] Panel 3: address priority ordering vs statistical strength
- [ ] Panel 2 / banner: fix "11/11" framing (6 complexes, 3 are controls)
- [ ] Panel 1: remove bowhead whale if not in data
- [ ] All panels: apply correct protein names from reference table (section G)
