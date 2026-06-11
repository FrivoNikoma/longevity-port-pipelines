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
residue-level inspection
structure-guided follow-up
assay planning
validation-plan generation

```

The current v2 run does not yet support:

```text
claiming fully NEGATOME-controlled hits
treating scaffolded controls as curated controls
removing missing_negatome warnings from scorecards or validation plans

```

## Recommended next steps

Recommended next technical steps:

```text
1. Add or curate NEGATOME-style negative-control rows for selected high-priority v2 candidates.
2. Re-run negative-control audit and scorecard generation after curated controls exist.
3. Generate structure-selection exports for top v2 candidates.
4. Inspect the strongest v2 remodeling candidates structurally, especially 8bhv ligand signals.
5. Use the v2 validation plan as a preliminary assay-planning guide.
```

Recommended next biological review targets:

```text
8bhv ligand / naked_mole_rat
8bhv ligand / mouse
1nfi receptor / naked_mole_rat
1nfi receptor / myotis_lucifugus
8bhv receptor / naked_mole_rat
```

