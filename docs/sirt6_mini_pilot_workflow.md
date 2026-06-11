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
- preliminary validation plan;
- NEGATOME-style control pair candidate scaffold;
- PyMOL and ChimeraX structure-selection exports.

## Prerequisites

Run commands from the repository root:

```text
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

- interface_constrained;
- interface_divergent;
- low-confidence directional classes;
- weak_or_mixed.

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

## 10. Generate NEGATOME-style control pair candidates

```powershell
uv run python -m scripts.generate_negatome_control_pair_candidates

```

Expected output:

```text
data/output/sirt6_mini_pilot_negatome_control_pair_candidates.csv

```

This step generates a curation scaffold for future NEGATOME-style negative-control pairs from the mini-pilot residue-delta outputs.

The generated table is not a populated NEGATOME input. Candidate rows are marked as:

```text
ready_for_input_contract = false
negative_partner_source = curation_required

```

until the following fields are filled:

```text
negative_partner_uniprot
negative_partner_sequence

```

This output should be treated as a curation aid, not as evidence that NEGATOME-style controls are populated.

The generated candidate scaffold should not change the current negative-control interpretation. Until a valid `data/interim/negatome_control_pairs.csv` file exists and control ratios are computed, enrichment results should continue to be reported as `missing_negatome`.

## 11. Summarize residue-level candidates

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

## 12. Classify interaction outcomes

```powershell
uv run python -m scripts.classify_interaction_outcomes

```

Expected output:

```text
data/output/sirt6_mini_pilot_interaction_outcome_summary.csv

```

This step maps technical signal classes to interaction outcome categories:

- maintained_candidate;
- possible_interface_remodeling_or_incompatibility;
- low-confidence directional classes;
- unresolved.

It also assigns:

- confidence;
- assay priority;
- engineering priority;
- rationale;
- top divergent and constrained residue summaries when available.

## 13. Build candidate scorecard

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

## 14. Export structure candidate selections

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

## 15. Generate mini-pilot validation plan

```powershell
uv run python -m scripts.generate_mini_pilot_validation_plan

```

Expected outputs:

```text
data/output/sirt6_mini_pilot_validation_plan.csv
data/output/sirt6_mini_pilot_validation_plan.md

```

This step generates a preliminary validation plan from the candidate scorecard.

The validation plan includes:

- evidence level;
- validation priority;
- primary validation assay;
- secondary validation assay;
- structural follow-up;
- control requirements;
- interpretation warnings.

Candidates with `missing_negatome` are labeled as preliminary shuffled-control-only evidence rather than fully controlled hits.

## 16. Current control status

Current implemented controls:

- shuffled mask control: implemented in enrichment analysis;
- directional Mann-Whitney tests: implemented;
- NEGATOME-style negative control: field exists in the result model, but the current mini-pilot does not yet populate a full NEGATOME control;
- NEGATOME input contract: documented in `docs/negatome_control_inputs.md`;
- NEGATOME input validator: available as `scripts.validate_negatome_control_inputs`;
- NEGATOME-style control pair candidate scaffold: available as `scripts.generate_negatome_control_pair_candidates`.

The current workflow can explicitly report whether each result has:

- shuffled control only;
- missing NEGATOME control;
- populated negative control;
- passed all required controls.

Until a valid `data/interim/negatome_control_pairs.csv` file exists and control ratios are computed, mini-pilot scorecards should continue to show `missing_negatome`.

The candidate scaffold generated at:

```text
data/output/sirt6_mini_pilot_negatome_control_pair_candidates.csv

```

is not itself a valid NEGATOME input. It is a curation aid for preparing future negative-control partner rows.

## 17. Current mini-pilot status before expansion

The current SIRT6 mini-pilot should be interpreted as a reproducible, control-aware pilot rather than a fully validated NEGATOME-controlled analysis.

Implemented and reproducible layers:

```text
mini-pilot complex selection
mapped interface extraction
interface-vs-background embedding enrichment
shuffled-mask controls
negative-control audit fields
validation plan generation
interaction outcome classification
candidate scorecard generation
NEGATOME-style candidate scaffold generation
NEGATOME input validation
NEGATOME curation rules and evidence notes

```

Current control interpretation:

```text
shuffled mask controls: implemented
NEGATOME-style candidate scaffold: implemented
NEGATOME input validator: implemented
curated NEGATOME input rows: not yet populated
NEGATOME-style control ratios: not yet computed
scorecard/control status: missing_negatome where no curated input exists

```

PARP1/P09874 curation status:

```text
PARP1 NEGATOME curation: attempted
Negatome 2.0 candidates found: P07437/TUBB and O60907/TBL1X
P07437/TUBB: background-only / ambiguous
O60907/TBL1X: reviewed but pathway-adjacent / candidate_under_review
ready PARP1 negative-control input row: not available

```

Therefore, the current correct interpretation remains:

```text
The mini-pilot can support hypothesis generation and prioritization.
The mini-pilot should not be interpreted as fully NEGATOME-controlled.
Candidates with shuffled support but missing NEGATOME controls remain preliminary.
NEGATOME-style controls are now scaffolded and auditable, but not yet populated.

```

Before expanding the pilot, preserve this distinction:

```text
Expansion can proceed with explicit missing_negatome status.
Expansion should not silently treat scaffold rows as curated controls.
Future curated controls should be added row-by-row only after passing the input contract and curation rules.

```

Recommended next directions:

```text
Option A: continue curation on another first-pass target such as SIRT6 receptor / mouse or Ku70 receptor / mouse.
Option B: expand to a v2 pilot while keeping NEGATOME-style controls as an explicit missing/curation layer.
Option C: implement the computation step for NEGATOME-style ratios only after at least one curated input row is accepted.

```

## 18. v2 conservative preflight workflow

The v2 conservative preflight is a local, non-committed workflow for testing the first controlled expansion before changing default mini-pilot behavior.

It uses the conservative v2 PDB set described in `docs/sirt6_mini_pilot_v2_candidate_selection.md`:

```text
8f86
8bot
7s68
4xhu
1h2k
1nfi
8bhy
8bhv

```

Generate the v2 selection and ortholog coverage files with explicit output paths:

```powershell
uv run python -m scripts.make_sirt6_mini_pilot `
  --pdb-ids 8f86 8bot 7s68 4xhu 1h2k 1nfi 8bhy 8bhv `
  --output-selection data/output/sirt6_mini_pilot_v2_selection.csv `
  --output-coverage data/output/sirt6_mini_pilot_v2_ortholog_coverage.csv

```

Expected local outputs:

```text
data/output/sirt6_mini_pilot_v2_selection.csv
data/output/sirt6_mini_pilot_v2_ortholog_coverage.csv

```

Run mapped interface chain-pair QC against the v2 selection:

```powershell
uv run python -m scripts.audit_mapped_interface_selection `
  --selection data/output/sirt6_mini_pilot_v2_selection.csv `
  --output data/output/sirt6_mini_pilot_v2_chain_pair_qc.csv

```

Expected local output:

```text
data/output/sirt6_mini_pilot_v2_chain_pair_qc.csv

```

Current local preflight result:

```text
selected v2 contexts: 8
ortholog coverage rows: 31
mapped interface QC: 8/8 rows status = ok

```

The v2 preflight outputs are generated artifacts under `data/output/` and should not be committed by default.

This preflight does not populate NEGATOME-style controls and does not compute v2 enrichment results. It only verifies that the conservative v2 selection can be generated and that the selected chain pairs pass mapped interface QC.

## 19. Optional biological report

The current biology-facing report is stored at:

```text
docs/sirt6_mini_pilot_biology_report.md

```

It summarizes the current biological interpretation of the mini-pilot.

## 20. Recommended full command sequence

For a full mini-pilot rerun after embeddings are available:

```powershell
uv run python -m scripts.audit_mapped_interface_selection
uv run python -m scripts.analyze_saved_embeddings_mapped
uv run python -m scripts.summarize_embedding_signals
uv run python -m scripts.export_mapped_residue_deltas
uv run python -m scripts.generate_negatome_control_pair_candidates
uv run python -m scripts.summarize_residue_level_candidates
uv run python -m scripts.classify_interaction_outcomes
uv run python -m scripts.audit_negative_controls
uv run python -m scripts.make_mini_pilot_candidate_scorecard
uv run python -m scripts.generate_mini_pilot_validation_plan
uv run python -m scripts.validate_negatome_control_inputs
uv run python -m scripts.export_structure_candidate_selections

```

If embeddings need to be regenerated, run before the sequence above:

```powershell
uv run python -m scripts.embed_saved_selection

```

## 21. Quality checks before committing code changes

Run:

```powershell
uv run ruff format src scripts tests
uv run ruff check src scripts tests
uv run mypy src/
uv run pytest

```

Expected result:

```text
All checks passed
Success: no issues found
pytest passes

```

## 22. Main output files

The most important mini-pilot outputs are:

```text
data/output/sirt6_mini_pilot_chain_pair_qc.csv
data/output/sirt6_mini_pilot_enrichment_mapped.parquet
data/output/sirt6_mini_pilot_embedding_signal_summary.csv
data/output/sirt6_mini_pilot_residue_deltas_mapped.parquet
data/output/sirt6_mini_pilot_negatome_control_pair_candidates.csv
data/output/sirt6_mini_pilot_top_divergent_interface_residues.csv
data/output/sirt6_mini_pilot_top_constrained_interface_residues.csv
data/output/sirt6_mini_pilot_recurrent_interface_residues.csv
data/output/sirt6_mini_pilot_interaction_outcome_summary.csv
data/output/sirt6_mini_pilot_negative_control_audit.csv
data/output/sirt6_mini_pilot_negatome_control_input_validation.csv
data/output/sirt6_mini_pilot_candidate_scorecard.csv
data/output/sirt6_mini_pilot_validation_plan.csv
data/output/sirt6_mini_pilot_validation_plan.md
data/output/structure_selections/sirt6_mini_pilot_candidate_selection_summary.csv
data/output/structure_selections/sirt6_mini_pilot_candidate_selections.pml
data/output/structure_selections/sirt6_mini_pilot_candidate_selections.cxc

```

Most `data/output` files are generated artifacts and should generally not be committed unless explicitly needed.

## 23. Workflow interpretation

The workflow supports a progression from raw structural complexes to candidate prioritization and structural inspection:

```text
structure selection
→ mapped interface extraction
→ embedding delta analysis
→ signal classification
→ residue-level deltas
→ NEGATOME-style control pair candidate scaffold
→ residue-level candidates
→ interaction outcome classes
→ negative-control audit
→ candidate scorecard
→ preliminary validation plan
→ structure selection export

```

This makes the mini-pilot reproducible and provides a compact basis for downstream structural inspection, assay planning, curation of negative controls, and engineering decisions.