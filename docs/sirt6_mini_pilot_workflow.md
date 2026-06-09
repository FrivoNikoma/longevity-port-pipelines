# SIRT6 mini-pilot workflow

This document describes the reproducible command sequence for the SIRT6 mini-pilot pipeline.

The mini-pilot starts from a small curated set of longevity-relevant protein complexes and produces:

- mapped interface extraction;
- chain-pair quality control;
- interface-vs-background embedding enrichment;
- directional Mann-Whitney statistics;
- embedding signal classification;
- residue-level delta export;
- residue-level candidate summaries;
- interaction outcome classification;
- final candidate scorecard;
- PyMOL and ChimeraX structure-selection exports.

## Prerequisites

Run commands from the repository root:

```powershell
D:\biohub_projects\longevity-port-pipelines

```

Use the project environment:

```powershell
uv run python -m <module>

```

Before starting a new analysis run, check the repository state:

```powershell
git status

```

## 1. Build or refresh the mini-pilot selection

```powershell
uv run python -m scripts.make_sirt6_mini_pilot

```

Expected output:

```text
data/output/sirt6_mini_pilot_selection.csv

```

This file contains the selected mini-pilot complexes, chain roles, UniProt identifiers, and reference sequences.

## 2. Fetch ortholog coverage

```powershell
uv run python -m scripts.fetch_candidate_set_orthologs

```

Expected output:

```text
data/output/sirt6_mini_pilot_ortholog_coverage.csv

```

This file contains reference-to-target ortholog mappings and target sequences.

## 3. Estimate embedding calls

Optional preflight step:

```powershell
uv run python -m scripts.estimate_embed_calls

```

Use this to check how many embeddings are expected before running embedding generation.

## 4. Generate or reuse saved embeddings

```powershell
uv run python -m scripts.embed_saved_selection

```

Expected output directory:

```text
data/output/embeddings/

```

The embedding files are stored as NumPy arrays under model-specific subdirectories.

## 5. Audit saved selection interfaces

Optional quality-control step:

```powershell
uv run python -m scripts.audit_saved_selection_interfaces

```

This checks whether selected complexes have extractable interface residues.

## 6. Audit mapped interface chain-pair selection

```powershell
uv run python -m scripts.audit_mapped_interface_selection

```

Expected output:

```text
data/output/sirt6_mini_pilot_chain_pair_qc.csv

```

This verifies that sequence-compatible chains are also spatially contacting in the structure.

## 7. Run mapped embedding enrichment analysis

```powershell
uv run python -m scripts.analyze_saved_embeddings_mapped

```

Expected output:

```text
data/output/sirt6_mini_pilot_enrichment_mapped.parquet

```

This step computes interface-vs-noninterface embedding delta enrichment for each complex, chain, and target species.

The output includes:

- interface mean delta;
- non-interface mean delta;
- enrichment ratio;
- shuffled mask control ratio;
- directional Mann-Whitney p-values;
- Cohen's d effect size.

## 8. Summarize embedding signals

```powershell
uv run python -m scripts.summarize_embedding_signals

```

Expected outputs:

```text
data/output/sirt6_mini_pilot_embedding_signal_summary.csv
data/output/sirt6_mini_pilot_embedding_signal_summary.md

```

This step classifies interface signals as:

- `interface_constrained`;
- `interface_divergent`;
- low-confidence directional classes;
- `weak_or_mixed`.

## 9. Export residue-level mapped deltas

```powershell
uv run python -m scripts.export_mapped_residue_deltas

```

Expected output:

```text
data/output/sirt6_mini_pilot_residue_deltas_mapped.parquet

```

This file contains one row per aligned reference residue per comparison.

Key columns:

```text
complex_id
pdb_id
chain
source_species
target_species
source_uniprot
target_uniprot
residue_index
residue_number_1based
residue_aa
delta
is_interface
model_name
is_predicted_structure

```

## 10. Summarize residue-level candidates

```powershell
uv run python -m scripts.summarize_residue_level_candidates

```

Expected outputs:

```text
data/output/sirt6_mini_pilot_top_divergent_interface_residues.csv
data/output/sirt6_mini_pilot_top_constrained_interface_residues.csv
data/output/sirt6_mini_pilot_recurrent_interface_residues.csv

```

This step produces:

- top divergent interface residues;
- top constrained interface residues;
- recurrent interface residues across target species.

## 11. Classify interaction outcomes

```powershell
uv run python -m scripts.classify_interaction_outcomes

```

Expected output:

```text
data/output/sirt6_mini_pilot_interaction_outcome_summary.csv

```

This step maps technical signal classes to interaction outcome categories:

- `maintained_candidate`;
- `possible_interface_remodeling_or_incompatibility`;
- low-confidence directional classes;
- `unresolved`.

It also assigns:

- confidence;
- assay priority;
- engineering priority;
- rationale;
- top divergent and constrained residue summaries when available.

## 12. Build candidate scorecard

```powershell
uv run python -m scripts.make_mini_pilot_candidate_scorecard

```

Expected output:

```text
data/output/sirt6_mini_pilot_candidate_scorecard.csv

```

This is the main compact decision table for the mini-pilot.

It combines:

- protein label;
- biological process;
- target species;
- interaction outcome class;
- confidence;
- numerical score;
- assay priority;
- engineering priority;
- recurrent residue summaries;
- current negative-control status;
- recommended next action.

## 13. Export structure candidate selections

```powershell
uv run python -m scripts.export_structure_candidate_selections

```

Expected outputs:

```text
data/output/structure_selections/sirt6_mini_pilot_candidate_selection_summary.csv
data/output/structure_selections/sirt6_mini_pilot_candidate_selections.pml
data/output/structure_selections/sirt6_mini_pilot_candidate_selections.cxc

```

This step exports residue selections for downstream structural visualization in PyMOL and ChimeraX.

The exported selections distinguish:

- divergent candidate interface residues;
- constrained candidate interface residues.

Important note: the current selections use reference-sequence 1-based residue numbers. If structure residue numbering differs from reference sequence numbering, inspect and adjust the selections manually.

## 14. Current control status

Current implemented controls:

- shuffled mask control: implemented in enrichment analysis;
- directional Mann-Whitney tests: implemented;
- NEGATOME-style negative control: field exists in the result model, but the current mini-pilot does not yet populate a full NEGATOME control;
- NEGATOME input contract: documented in `docs/negatome_control_inputs.md`;
- NEGATOME input validator: available as `scripts.validate_negatome_control_inputs`.

The current workflow can explicitly report whether each result has:

- shuffled control only;
- missing NEGATOME control;
- populated negative control;
- passed all required controls.

Until a valid `data/interim/negatome_control_pairs.csv` file exists and control ratios are computed, mini-pilot scorecards should continue to show `missing_negatome`.

## 15. Optional biological report

The current biology-facing report is stored at:

```text
docs/sirt6_mini_pilot_biology_report.md

```

It summarizes the current biological interpretation of the mini-pilot.

## 16. Recommended full command sequence

For a full mini-pilot rerun after embeddings are available:

```powershell
uv run python -m scripts.audit_mapped_interface_selection
uv run python -m scripts.analyze_saved_embeddings_mapped
uv run python -m scripts.summarize_embedding_signals
uv run python -m scripts.export_mapped_residue_deltas
uv run python -m scripts.summarize_residue_level_candidates
uv run python -m scripts.classify_interaction_outcomes
uv run python -m scripts.audit_negative_controls
uv run python -m scripts.make_mini_pilot_candidate_scorecard
uv run python -m scripts.validate_negatome_control_inputs
uv run python -m scripts.export_structure_candidate_selections

```

If embeddings need to be regenerated, run before the sequence above:

```powershell
uv run python -m scripts.embed_saved_selection

```

## 17. Quality checks before committing code changes

Run:

```powershell
uv run ruff format src scripts tests
uv run ruff check src scripts tests
uv run pytest

```

Expected result:

```text
All checks passed
44 passed

```

## 18. Main output files

The most important mini-pilot outputs are:

```text
data/output/sirt6_mini_pilot_chain_pair_qc.csv
data/output/sirt6_mini_pilot_enrichment_mapped.parquet
data/output/sirt6_mini_pilot_embedding_signal_summary.csv
data/output/sirt6_mini_pilot_residue_deltas_mapped.parquet
data/output/sirt6_mini_pilot_top_divergent_interface_residues.csv
data/output/sirt6_mini_pilot_top_constrained_interface_residues.csv
data/output/sirt6_mini_pilot_recurrent_interface_residues.csv
data/output/sirt6_mini_pilot_interaction_outcome_summary.csv
data/output/sirt6_mini_pilot_negative_control_audit.csv
data/output/sirt6_mini_pilot_negatome_control_input_validation.csv
data/output/sirt6_mini_pilot_candidate_scorecard.csv
data/output/structure_selections/sirt6_mini_pilot_candidate_selection_summary.csv
data/output/structure_selections/sirt6_mini_pilot_candidate_selections.pml
data/output/structure_selections/sirt6_mini_pilot_candidate_selections.cxc

```

Most `data/output` files are generated artifacts and should generally not be committed unless explicitly needed.

## 19. Workflow interpretation

The workflow supports a progression from raw structural complexes to candidate prioritization and structural inspection:

```text
structure selection
→ mapped interface extraction
→ embedding delta analysis
→ signal classification
→ residue-level candidates
→ interaction outcome classes
→ negative-control audit
→ candidate scorecard
→ structure selection export

```

This makes the mini-pilot reproducible and provides a compact basis for downstream structural inspection, assay planning, and engineering decisions.