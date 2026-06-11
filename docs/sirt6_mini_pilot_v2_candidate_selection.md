# SIRT6 mini-pilot v2 candidate selection design

This document defines the first candidate-selection step for the SIRT6 mini-pilot v2 expansion.

It complements:

- `docs/sirt6_mini_pilot_workflow.md`
- `docs/sirt6_mini_pilot_v2_expansion_plan.md`
- `scripts.make_sirt6_mini_pilot`

The goal is to expand the current mini-pilot within the already available explicit-only candidate universe before searching for new external complexes.

## 1. Current selection architecture

The current mini-pilot selection script is:

```text
scripts/make_sirt6_mini_pilot.py

```

It does not build the full explicit-only candidate universe from scratch. Instead, it reads:

```text
data/output/sirt6_dna_repair_explicit_only_selection.csv
data/output/sirt6_dna_repair_explicit_only_ortholog_coverage.csv

```

and filters the selection table by `pdb_id`.

The current default mini-pilot PDB IDs are:

```text
8f86
8bot
7s68

```

This means that v2 can start by expanding the default PDB ID set within the already available explicit-only selection universe.

## 2. Available explicit-only candidate universe

The current explicit-only selection table contains 10 complex contexts:


| pdb_id | uniprot_R | uniprot_L | intermolecular_contacts | predicted_R | predicted_L | current_status          |
| ------ | --------- | --------- | ----------------------- | ----------- | ----------- | ----------------------- |
| 1h2k   | Q9NWT6    | Q16665    | 93                      | true        | true        | available_for_v2_review |
| 1nfi   | Q04206    | P25963    | 83                      | true        | true        | available_for_v2_review |
| 2a93   | P01106    | P28574    | 40                      | true        | true        | available_for_v2_review |
| 4xhu   | P09874    | Q9UNS1    | 47                      | true        | true        | available_for_v2_review |
| 7s68   | P09874    | P09874    | 50                      | true        | true        | v1_selected             |
| 8ag5   | P13010    | P03296    | 51                      | true        | false       | available_for_v2_review |
| 8bhv   | P13010    | Q9H9Q4    | 40                      | true        | true        | available_for_v2_review |
| 8bhy   | P12956    | Q9BUH6    | 72                      | true        | true        | available_for_v2_review |
| 8bot   | P13010    | P12956    | 732                     | true        | true        | v1_selected             |
| 8f86   | Q8N6T7    | P84233    | 40                      | true        | true        | v1_selected             |


## 3. v1 selected contexts

The current v1 mini-pilot uses:

```text
8f86
8bot
7s68

```

These should remain in the default set unless there is a strong reason to split v1 and v2 scripts.

Current v1 interpretation remains unchanged:

```text
v1 is reproducible and control-aware
shuffled-mask controls are implemented
NEGATOME-style scaffold and validation are implemented
curated NEGATOME rows are not yet populated
NEGATOME-style ratios are not yet computed
missing_negatome remains an explicit row-level status

```

## 4. v2 candidate pool

The first v2 candidate pool should be the remaining explicit-only contexts:

```text
1h2k
1nfi
2a93
4xhu
8ag5
8bhv
8bhy

```

These candidates are already present in the explicit-only selection table, which makes them a safer first expansion target than new external structures.

They should still be reviewed before being added to the default v2 set.

## 5. First-pass v2 selection rule

For the first implementation pass, prefer candidates that satisfy:

- already present in `sirt6_dna_repair_explicit_only_selection.csv`;
- has both `predicted_R` and `predicted_L` set to `true`, unless there is a specific reason to test mixed predicted/experimental contexts;
- has non-trivial `intermolecular_contacts`;
- can pass mapped interface chain-pair QC;
- has ortholog coverage in `sirt6_dna_repair_explicit_only_ortholog_coverage.csv`;
- does not require a new output schema;
- does not silently change the interpretation of scorecard fields.

## 6. Candidate prioritization

Recommended first-pass v2 candidates:


| priority | pdb_id | rationale                                                                                         |
| -------- | ------ | ------------------------------------------------------------------------------------------------- |
| 1        | 4xhu   | PARP1-linked context already close to v1 biology, but distinct from the PARP1/PARP1 7s68 context. |
| 2        | 1h2k   | High-contact explicit-only context already present in the source universe.                        |
| 3        | 1nfi   | High-contact explicit-only context already present in the source universe.                        |
| 4        | 8bhy   | Ku70-linked context through P12956, complementary to v1 Ku70/Ku80 coverage.                       |
| 5        | 8bhv   | Ku80-linked context through P13010, complementary to v1 Ku70/Ku80 coverage.                       |


Candidates to treat cautiously:


| pdb_id | reason                                                                            |
| ------ | --------------------------------------------------------------------------------- |
| 8ag5   | `predicted_L = false`, so it may need separate interpretation before inclusion.   |
| 2a93   | lower contact count and biological rationale should be reviewed before inclusion. |


This prioritization is provisional. It should be validated by running chain/interface QC and inspecting downstream scorecard behavior.

## 7. Proposed first v2 default set

A conservative first v2 default set could be:

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

This keeps all v1 contexts and adds five new explicit-only contexts.

A more aggressive first v2 set could include all 10 available contexts:

```text
8f86
8bot
7s68
4xhu
1h2k
1nfi
8bhy
8bhv
8ag5
2a93

```

The conservative set is preferred for the first implementation PR.

## 8. Implementation options

Option A: update `DEFAULT_PDB_IDS` in `scripts/make_sirt6_mini_pilot.py`.

Example conservative set:

```python
DEFAULT_PDB_IDS = ["8f86", "8bot", "7s68", "4xhu", "1h2k", "1nfi", "8bhy", "8bhv"]

```

Option B: keep the v1 default unchanged and add a named v2 command in documentation:

```powershell
uv run python -m scripts.make_sirt6_mini_pilot --pdb-ids 8f86 8bot 7s68 4xhu 1h2k 1nfi 8bhy 8bhv

```

Option C: later refactor the script to support named presets:

```text
v1
v2_conservative
v2_all_explicit_only

```

For the next small implementation PR, Option B is lowest risk because it preserves the existing v1 default behavior while allowing v2 generation explicitly.

## 9. Recommended next implementation PR

The next implementation PR should not immediately alter biological interpretation logic.

Recommended scope:

1. document the v2 command using `--pdb-ids`;
2. optionally add a v2 workflow section;
3. run the v2 selection generation locally;
4. inspect selected complexes and ortholog coverage;
5. do not commit generated `data/output` files by default;
6. only then decide whether to change `DEFAULT_PDB_IDS` or add named presets.

## 10. Control interpretation during v2 selection

Adding more PDB IDs does not populate NEGATOME-style controls.

For all new v2 rows:

```text
shuffled mask control: computed only after enrichment rerun
NEGATOME-style candidate scaffold: generated only after residue-delta outputs exist
curated NEGATOME input: absent unless manually curated
NEGATOME-style ratio: absent until computation step exists
missing_negatome: expected status for rows without curated input

```

Do not treat any v2 scaffold row as a curated negative-control row.

## 11. Decision

The first v2 expansion should proceed within the already available explicit-only selection universe before searching for external complexes.

Preferred next action:

```text
Use the conservative v2 PDB set through an explicit --pdb-ids command.
Do not change DEFAULT_PDB_IDS until the v2 selection, interface QC, scorecard, and validation-plan behavior are inspected.
Do not commit generated output artifacts by default.
Preserve explicit missing_negatome status.

```

This keeps v1 stable while allowing v2 to be tested as a controlled expansion.