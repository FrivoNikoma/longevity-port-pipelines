# SIRT6 mini-pilot v2 local results

This document records the current local v2 mini-pilot result package.

The generated v2 artifacts live under `data/output/` and are not committed by default.

## Scope

The v2 local run used the conservative v2 selection described in:
```text
docs/sirt6_mini_pilot_v2_candidate_selection.md
docs/sirt6_mini_pilot_v2_expansion_plan.md
docs/sirt6_mini_pilot_workflow.md
```

The local v2 run covers:
```text
v2 selection
v2 ortholog coverage
v2 Biohub saved embeddings
v2 missing embedding audit
v2 mapped enrichment
v2 embedding signal summary
v2 longevity contrast
v2 structure-inspection selections
v2 residue-level deltas
v2 residue-level candidate summaries
v2 interaction outcome summary
v2 negative-control audit
v2 candidate scorecard
v2 validation plan
```

## Local generated artifacts

The current local v2 decision package consists of generated artifacts under `data/output/`:
```text
data/output/sirt6_mini_pilot_v2_selection.csv
data/output/sirt6_mini_pilot_v2_ortholog_coverage.csv
data/output/sirt6_mini_pilot_v2_missing_embeddings.csv
data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet
data/output/sirt6_mini_pilot_v2_embedding_signal_summary.csv
data/output/sirt6_mini_pilot_v2_embedding_signal_summary.md
data/output/sirt6_mini_pilot_v2_longevity_contrast.csv
data/output/sirt6_mini_pilot_v2_longevity_contrast.md
data/output/sirt6_mini_pilot_v2_structure_selections/
data/output/sirt6_mini_pilot_v2_residue_deltas_mapped.parquet
data/output/sirt6_mini_pilot_v2_residue_candidates/
data/output/sirt6_mini_pilot_v2_interaction_outcome_summary.csv
data/output/sirt6_mini_pilot_v2_negative_control_audit.csv
data/output/sirt6_mini_pilot_v2_candidate_scorecard.csv
data/output/sirt6_mini_pilot_v2_validation_plan.csv
data/output/sirt6_mini_pilot_v2_validation_plan.md
```

These files are generated outputs and should not be committed by default.

## Embedding readiness and generation

The v2 dry-run estimated:
```text
complexes: 8
embedding pairs: 43
estimated Biohub API calls: 86
missing ortholog coverage rows: 1
```

The missing ortholog coverage row is:
```text
8f86 ligand P84233
```

After the controlled Biohub embedding run, the missing embedding audit reported:
```text
ok: 43
missing_embedding: 0
missing_ortholog_coverage: 1
```

Interpretation:
```text
All embeddable v2 rows have saved embeddings.
The remaining incomplete row is an ortholog coverage gap, not an embedding failure.
```

## Mapped enrichment

The v2 mapped enrichment run wrote:
```text
data/output/sirt6_mini_pilot_v2_enrichment_mapped.parquet
```

Summary:
```text
rows: 43
complexes: 8
chains: receptor, ligand
species: mouse, myotis_lucifugus, naked_mole_rat
skipped no interface: 0
skipped missing embedding: 0
skipped no mapping: 1
```

The one no-mapping skip is the expected `8f86` ligand `P84233` ortholog coverage gap.

## Embedding signal summary

The v2 embedding signal summary produced:
```text
data/output/sirt6_mini_pilot_v2_embedding_signal_summary.csv
data/output/sirt6_mini_pilot_v2_embedding_signal_summary.md
```

Signal class counts:
```text
weak_or_mixed: 17
interface_constrained: 12
interface_divergent: 12
interface_divergent_not_significant: 1
interface_constrained_not_significant: 1
```

The strongest preliminary divergent signal is:
```text
8bhv__P1_P13010--8bhv__J1_Q9H9Q4 / ligand / naked_mole_rat
enrichment_ratio: 2.592572
p_two_sided: 4.553e-12
effect_size_cohens_d: 4.291875
signal_class: interface_divergent
```

The second strongest preliminary divergent signal is:
```text
8bhv__P1_P13010--8bhv__J1_Q9H9Q4 / ligand / mouse
enrichment_ratio: 2.336554
p_two_sided: 4.553e-12
effect_size_cohens_d: 3.796028
signal_class: interface_divergent
```

## Longevity contrast

The v2 longevity contrast analysis compares long-lived species rows against a short-lived mouse baseline within each `complex_id + chain` group.

The v2 longevity contrast outputs were written to:
```text
data/output/sirt6_mini_pilot_v2_longevity_contrast.csv
data/output/sirt6_mini_pilot_v2_longevity_contrast.md
```

Contrast class counts:
```text
weak_or_unresolved_contrast: 14
shared_interface_constraint: 7
long_lived_enhanced_interface_divergence: 4
short_lived_baseline_stronger_signal: 2
shared_nonhuman_interface_divergence: 1
```

Key contrast result:
```text
8bhv ligand / naked_mole_rat vs mouse
contrast_class: shared_nonhuman_interface_divergence
```

Interpretation:
```text
The previous strongest interface-localized signal, 8bhv ligand, remains biologically interesting.
However, it is not currently classified as long-lived-specific because mouse also shows strong interface enrichment.
This makes it a shared non-human-vs-human interface-divergence signal rather than a clean longevity-specific signal.
```

The strongest long-lived-enhanced interface-divergence candidates are:
```text
1nfi receptor / naked_mole_rat vs mouse
1nfi receptor / myotis_lucifugus vs mouse
8bhv receptor / naked_mole_rat vs mouse
8bhv receptor / myotis_lucifugus vs mouse
```

Representative contrast rows:
```text
1nfi receptor / naked_mole_rat vs mouse
long_enrichment_ratio: 1.32632
short_enrichment_ratio: 1.18642
enrichment_delta: 0.139906
enrichment_log2_ratio: 0.160821
long_effect_size: 0.702370
short_effect_size: 0.410381
effect_size_delta: 0.291989
contrast_class: long_lived_enhanced_interface_divergence

1nfi receptor / myotis_lucifugus vs mouse
long_enrichment_ratio: 1.30246
short_enrichment_ratio: 1.18642
enrichment_delta: 0.116043
enrichment_log2_ratio: 0.134628
long_effect_size: 0.658241
short_effect_size: 0.410381
effect_size_delta: 0.247861
contrast_class: long_lived_enhanced_interface_divergence

8bhv receptor / naked_mole_rat vs mouse
long_enrichment_ratio: 1.25418
short_enrichment_ratio: 1.17543
enrichment_delta: 0.078751
enrichment_log2_ratio: 0.093556
long_effect_size: 0.559559
short_effect_size: 0.401666
effect_size_delta: 0.157892
contrast_class: long_lived_enhanced_interface_divergence

8bhv receptor / myotis_lucifugus vs mouse
long_enrichment_ratio: 1.24132
short_enrichment_ratio: 1.17543
enrichment_delta: 0.065886
enrichment_log2_ratio: 0.078682
long_effect_size: 0.517247
short_effect_size: 0.401666
effect_size_delta: 0.115581
contrast_class: long_lived_enhanced_interface_divergence
```

This addresses the main biological caveat in the proposal draft: separating generic non-human-vs-human interface divergence from candidate longevity-associated contrast.

Interpretation:
```text
The v2 package now distinguishes interface-localized divergence from candidate longevity-enhanced divergence.
The strongest original 8bhv ligand signal is better described as shared non-human interface divergence.
The current long-lived-enhanced candidates shift attention toward 1nfi receptor and 8bhv receptor contrasts.
```

## Structure inspection selections

The v2 structure-inspection selection package was generated with the contrast-aware structure selection export:
```text
uv run python -m scripts.export_structure_candidate_selections `
  --residue-deltas data/output/sirt6_mini_pilot_v2_residue_deltas_mapped.parquet `
  --longevity-contrast data/output/sirt6_mini_pilot_v2_longevity_contrast.csv `
  --output-dir data/output/sirt6_mini_pilot_v2_structure_selections
```

The generated local structure-selection artifacts are:
```text
data/output/sirt6_mini_pilot_v2_structure_selections/sirt6_mini_pilot_candidate_selection_summary.csv
data/output/sirt6_mini_pilot_v2_structure_selections/sirt6_mini_pilot_candidate_selections.pml
data/output/sirt6_mini_pilot_v2_structure_selections/sirt6_mini_pilot_candidate_selections.cxc
```

These files are generated outputs and should not be committed by default.

Current structure-selection summary:
```text
rows: 47
columns: 22
```

Exported contrast-informed groups:
```text
1nfi receptor / myotis_lucifugus: 10 residues
1nfi receptor / naked_mole_rat: 10 residues
8bhv receptor / myotis_lucifugus: 10 residues
8bhv receptor / naked_mole_rat: 10 residues
8bhv ligand / naked_mole_rat: 7 residues
```

Structure-chain mapping used in the generated selections:
```text
1nfi receptor -> structure chain C
8bhv receptor -> structure chain j
8bhv ligand -> structure chain R
```

Interpretation:
```text
The structure-selection package focuses structural inspection on long-lived-enhanced interface-divergence candidates: 1nfi receptor and 8bhv receptor.
The 8bhv ligand selection is retained as a strong shared non-human interface-divergence benchmark, not as a clean longevity-specific hit.
```

Important caveat:
```text
The generated selections use reference-sequence 1-based residue numbers.
They assume that reference sequence numbering matches structure residue numbering.
Structures with missing residues, insertion codes, or renumbered chains require manual inspection and adjustment.
```

## Residue-level outputs

The v2 residue-level delta export wrote:
```text
data/output/sirt6_mini_pilot_v2_residue_deltas_mapped.parquet
```

Summary:
```text
residue-level delta rows: 13415
complexes: 8
chains: receptor, ligand
species: mouse, myotis_lucifugus, naked_mole_rat
skipped no interface: 0
skipped missing embedding: 0
skipped no mapping: 1
```

The v2 residue candidate summaries were written under:
```text
data/output/sirt6_mini_pilot_v2_residue_candidates/
```

with:
```text
sirt6_mini_pilot_top_divergent_interface_residues.csv
sirt6_mini_pilot_top_constrained_interface_residues.csv
sirt6_mini_pilot_recurrent_interface_residues.csv
```

Current residue candidate summary:
```text
top divergent interface residues: 30 rows
top constrained interface residues: 30 rows
recurrent interface residues: 438 rows
```

Notable top divergent residue-level examples:
```text
4xhu / receptor / P09874 / residue 104 L
naked_mole_rat delta: 1.763986
mouse delta: 1.735460
myotis_lucifugus delta: 1.731910

1h2k / ligand / Q16665 / residue 24 D
myotis_lucifugus delta: 1.648620
mouse delta: 1.643813
```

Notable top constrained residue-level example:
```text
1h2k / receptor / Q9NWT6 / residue 188 E
naked_mole_rat delta: 0.053646
mouse delta: 0.057056
```

## Interaction outcomes

The v2 interaction outcome summary was written to:
```text
data/output/sirt6_mini_pilot_v2_interaction_outcome_summary.csv
```

Outcome class counts:
```text
unresolved / very_low: 17
maintained_candidate / high: 10
possible_interface_remodeling_or_incompatibility / high: 6
possible_interface_remodeling_or_incompatibility / medium: 6
maintained_candidate / medium: 2
possible_interface_remodeling_or_incompatibility / low: 1
possible_maintained_low_confidence / low: 1
```

## Negative-control status

The v2 negative-control audit was written to:
```text
data/output/sirt6_mini_pilot_v2_negative_control_audit.csv
```

Current control status:
```text
missing_negatome: 43
```

Interpretation:
```text
Shuffled-mask controls are populated.
NEGATOME-style controls are not populated.
All v2 scorecard rows remain preliminary shuffled-control-only evidence.
```

## Candidate scorecard

The v2 candidate scorecard was written to:
```text
data/output/sirt6_mini_pilot_v2_candidate_scorecard.csv
```

Summary:
```text
rows: 43
columns: 31
control_status: missing_negatome
control_interpretation: shuffled_only_missing_negatome
```

Top preliminary scorecard candidates include:
```text
8bhv ligand / naked_mole_rat
8bhv ligand / mouse
1nfi receptor / naked_mole_rat
1nfi receptor / myotis_lucifugus
8bhv receptor / naked_mole_rat
```

These should be interpreted as prioritization candidates, not fully controlled hits.

After longevity contrast, the most relevant biological-review targets become:
```text
1nfi receptor / naked_mole_rat vs mouse
1nfi receptor / myotis_lucifugus vs mouse
8bhv receptor / naked_mole_rat vs mouse
8bhv receptor / myotis_lucifugus vs mouse
8bhv ligand / naked_mole_rat vs mouse as shared non-human interface divergence
```

After structure-selection export, these biological-review targets now have generated PyMOL/ChimeraX residue selections for structure-guided inspection.

## Validation plan

The v2 validation plan was written to:
```text
data/output/sirt6_mini_pilot_v2_validation_plan.csv
data/output/sirt6_mini_pilot_v2_validation_plan.md
```

Validation priority counts:
```text
medium_preliminary / preliminary_shuffled_only: 22
defer / low_confidence_shuffled_only: 19
low_preliminary / preliminary_shuffled_only: 2
```

Interpretation:
```text
The v2 run now supports preliminary prioritization and assay planning.
The evidence remains preliminary because NEGATOME-style controls are missing.
```

## Current interpretation

The current v2 run supports:
```text
candidate prioritization
long-lived-vs-short-lived contrast analysis
contrast-informed structure-inspection selection export
residue-level inspection
structure-guided follow-up
assay planning
validation-plan generation
```

The current v2 run does not yet support:
```text
claiming fully NEGATOME-controlled hits
claiming fully longevity-specific biological hits
treating scaffolded controls as curated controls
removing missing_negatome warnings from scorecards or validation plans
```

## Recommended next steps

Recommended next technical steps:
```text
1. Inspect the generated PyMOL/ChimeraX selections for the top long-lived-enhanced candidates.
2. Check whether the selected reference-sequence residue numbers match structure residue numbering.
3. Generate screenshots or short structural notes for 1nfi receptor and 8bhv receptor contrast candidates.
4. Keep 8bhv ligand as a strong shared non-human interface-divergence benchmark, not as a clean longevity-specific hit.
5. Add or curate NEGATOME-style negative-control rows for selected high-priority contrast candidates.
6. Re-run negative-control audit and scorecard generation after curated controls exist.
7. Use the v2 validation plan as a preliminary assay-planning guide.
```

Recommended next biological review targets:
```text
1nfi receptor / naked_mole_rat vs mouse
1nfi receptor / myotis_lucifugus vs mouse
8bhv receptor / naked_mole_rat vs mouse
8bhv receptor / myotis_lucifugus vs mouse
8bhv ligand / naked_mole_rat vs mouse as shared non-human interface divergence benchmark
```

