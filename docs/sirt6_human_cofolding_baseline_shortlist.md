# SIRT6/core3-expanded human cofolding baseline shortlist

This note defines a small human-baseline shortlist for the next Boltz
cofolding step after the initial MHC/HLA calibration.

The goal is not to make a cross-species biological claim yet. The goal is
to choose SIRT6/core3-expanded candidate pairs where a human or technical baseline
should be tested before spending Boltz calls on species panels.

## Background

The first live baseline calibration recovered two audited human-human
MHC/HLA PINDER-fragment controls as maintained interactions.

That result shows that the current Boltz cofolding setup can recover
known structural positive controls. However, those controls do not directly
validate SIRT6/core3-expanded biology.

The next biological gate is therefore:

Can Boltz recover a relevant human PINDER-fragment baseline?

Only candidates with a recoverable human baseline should move to
cross-species interpretation.

## Selection criteria

Prioritize candidates that satisfy most of the following:

- candidate comes from the existing SIRT6 core3-expanded workflow
- human or technical baseline is available
- receptor and ligand fragments are not extremely short
- candidate does not have known missing-chain or partner-mismatch issues
- candidate has prior interface/enrichment signal worth following up
- live Boltz run can be done one candidate at a time with explicit id

Avoid interpreting species-level incompatibility unless the matching human
or technical baseline is first recovered.

## Shortlist

### Priority 1: 1nfi A/F

Reason to test:

- NF-kappaB / IkappaBalpha regulatory-interface candidate
- moderate fragment sizes in the current workflow
- previously appeared in the manual-review / controlled follow-up context
- useful first test for whether a regulatory-interface human baseline is recoverable

Recommended next action:

- audit the exact generated cofolding id
- run a dry-run first
- if inputs look correct, run one explicit live baseline only

### Priority 1: 4xhu A/B

Reason to test:

- strong follow-up candidate from the existing controlled cases
- appeared as a controlled-pass signal in the previous validation context
- useful as an early bridge from calibration controls to SIRT6/core3-expanded biology

Recommended next action:

- verify chain annotations and generated id
- prefer this as a second live baseline after 1nfi if the input looks clean

### Priority 2: 7s68 D/C

Reason to test:

- appeared in the SIRT6/core3-expanded candidate workflow
- potentially useful as a compact interface-level probe

Caution:

- shorter fragments make interpretation more fragile
- should not be the first live biological baseline unless higher-priority
  candidates fail preflight

### Priority 3: 8bhv N/I and P/J

Reason to test:

- appeared in previous controlled-fail / interesting-divergence context
- may be useful as a stress test after stronger baselines

Caution:

- very short ligand-side fragment in the current workflow
- lower priority for live spending
- do not use as the first biological baseline

### Deprioritized for first live baseline: 8f86 K/D

Reason:

- older 8f86 rows included ligand-mapping and partner-mismatch concerns
- useful to track, but not a good first live baseline target

## Candidate baseline preflight CLI

Before any live Boltz call, inspect the exact PINDER-fragment baseline input
with the dry-run-only candidate baseline CLI:

```bash
uv run cofolding-candidate-baseline --candidate-id "1nfi__A1_Q04206--1nfi__F1_P25963"
uv run cofolding-candidate-baseline --candidate-id "4xhu__A1_P09874--4xhu__B1_Q9UNS1"
```

This command prepares receptor/ligand fragment sequences and prints their
PDB id, UniProt ids, chain ids, and fragment lengths. It does not create a
Boltz client, does not submit predictions, and does not write runtime output
files.

## Local dry-run preflight results

The first dry-run preflight checks for the Priority 1 candidates resolved
successfully from local PINDER data:

| Candidate id | PDB | Receptor | Ligand | Receptor length | Ligand length | Dry-run status |
|---|---|---:|---:|---:|---:|---|
| `1nfi__A1_Q04206--1nfi__F1_P25963` | 1nfi | Q04206 / A1 | P25963 / F1 | 295 | 213 | input prepared |
| `4xhu__A1_P09874--4xhu__B1_Q9UNS1` | 4xhu | P09874 / A1 | Q9UNS1 / B1 | 333 | 83 | input prepared |

Both dry-runs reported:

```text
No Boltz API calls were made.
No runtime output files were written.
```

Interpretation: these Priority 1 candidates pass the input-preflight gate.
This does not yet imply that Boltz can recover the interaction as maintained;
it only shows that the exact PINDER-fragment baseline inputs can be prepared
and inspected safely before any live baseline run.

## Local live candidate baseline results

The first controlled live candidate baseline runs were executed with `--yes-live --num-samples 1` after dry-run preflight.

| Candidate id | PDB | Receptor | Ligand | ipTM | Binding confidence | complex ipLDDT | Boltz classification | Prediction id |
|---|---|---:|---:|---:|---:|---:|---|---|
| `1nfi__A1_Q04206--1nfi__F1_P25963` | 1nfi | Q04206 / A1 | P25963 / F1 | 0.742 | 0.376 | 0.893 | uncertain | `sab_pred_apj3d6YLoGb4ErSaJUDH` |
| `4xhu__A1_P09874--4xhu__B1_Q9UNS1` | 4xhu | P09874 / A1 | Q9UNS1 / B1 | 0.920 | 0.798 | 0.931 | maintained | `sab_pred_7cUCBAVPrtD5UzhkHa0P` |

Interpretation:

- `1nfi` is a borderline/uncertain human baseline: high structural confidence but low binding confidence.
- `4xhu` is the first cleanly recovered SIRT6/core3-expanded human-baseline candidate in this workflow.
- Species-panel interpretation should prioritize `4xhu` first, because its matching human/technical baseline is recoverable.
- Full temporary structure URLs are intentionally not recorded in docs.


## 4xhu P09874 species coverage gap

The intended biological contrast is long-lived species versus short-lived controls, not old versus newly added species. However, the current local coverage for the `4xhu` receptor chain (`P09874`) is fragmented across historical ortholog coverage outputs.

The expanded species registry contains five long-lived species and three short-lived controls:

| Group | Species |
|---|---|
| long-lived | `naked_mole_rat`, `myotis_lucifugus`, `brandts_bat`, `elephant`, `bowhead_whale` |
| short-lived controls | `mouse`, `rat`, `hamster` |

Local audit of existing `*ortholog_coverage*.csv` files found partial `P09874` coverage:

| Coverage source pattern | P09874 species present | Missing registry species |
|---|---|---|
| earlier mini-pilot / explicit-only files | `mouse`, `myotis_lucifugus`, `naked_mole_rat` | `brandts_bat`, `elephant`, `bowhead_whale`, `rat`, `hamster` |
| refreshed / part2 files | `elephant`, `hamster`, `myotis_lucifugus`, `naked_mole_rat`, `rat` | `brandts_bat`, `bowhead_whale`, `mouse` |

This means the current local outputs are not uniformly consolidated across the full intended 5-vs-3 long-lived/short-lived panel for `P09874`.

Interpretation guard:

- `4xhu` remains the first clean human-baseline candidate for follow-up because its live baseline was classified as `maintained`.
- A full species-level interpretation should wait until `P09874` ortholog coverage is refreshed or explicitly consolidated across all intended target species.
- Existing SIRT6/core3-expanded outputs should not be described as a complete expanded long-lived-vs-short-lived contrast for `4xhu`.
- A smaller technical pilot may be possible, but it must be labeled as incomplete coverage rather than a full species panel.

Next recommended step before live Boltz species-panel runs:

1. consolidate or refresh `P09874` ortholog coverage for all intended target species;
2. audit whether corresponding embeddings / mapped residue outputs exist;
3. run `cofolding --dry-run-inputs` only after the input species panel is explicit and reproducible;
4. start live Boltz calls only after the dry-run input audit is clean.


## 4xhu P09874 missing-ortholog probe

After the local coverage audit, two long-lived species still lacked usable `P09874` ortholog coverage for the `4xhu` receptor chain:

- `bowhead_whale` / taxid `27622`
- `brandts_bat` / taxid `109478`

A targeted local probe was run through the repository's standard `fetch_ortholog()` path, which tries OMA first and falls back to UniProt. Both species returned missing through that standard path.

A broader local probe was then run across UniProt and NCBI Protein. This found strict `brandts_bat` candidates, but did not yield a safe `bowhead_whale` candidate.

Summary:

| Species | Standard OMA/UniProt path | Broad probe result | Current interpretation |
|---|---|---|---|
| `brandts_bat` | missing | strict PARP1 candidates found: `EPQ16369.1` / `S7NG06`, length 1024 | candidate mapping can be considered in a separate curated-input PR |
| `bowhead_whale` | missing | PARP1-like hits found, but full headers identify `Molossus molossus`, not `Balaena mysticetus` | no safe curated mapping yet |

The best current `brandts_bat` candidate is:

| Species | Candidate | Source | Length | Header / description |
|---|---|---|---:|---|
| `brandts_bat` | `EPQ16369.1` | NCBI Protein | 1024 | `Poly [ADP-ribose] polymerase 1 [Myotis brandtii]` |
| `brandts_bat` | `S7NG06` | UniProt | 1024 | `Poly [ADP-ribose] polymerase`, organism `Myotis brandtii` |

The `bowhead_whale` PARP1-like hits were rejected for curated use at this stage:

| Candidate | Length | Rejection reason |
|---|---:|---|
| `XP_036133328.1` | 1014 | FASTA header identifies `Molossus molossus`, not `Balaena mysticetus` |
| `XP_036133329.1` | 975 | FASTA header identifies `Molossus molossus`, not `Balaena mysticetus` |

Interpretation guard:

- This does not prove that bowhead whale lacks PARP1 biologically.
- It means the current standard and broad local probes did not produce a safe `bowhead_whale` `P09874` curated mapping.
- The `4xhu` / `P09874` follow-up should still not be described as a complete 5-vs-3 long-lived/short-lived species panel.
- A separate curated-input PR may add `brandts_bat`, but `bowhead_whale` needs a stronger source or manual sequence curation before inclusion.
- No Boltz API calls were made during these probes.


## Reusable species coverage audit CLI

The earlier `scripts/audit_4xhu_p09874_coverage.py` script captured the first hard-coded `4xhu` / `P09874` coverage audit. The reusable `species-coverage-audit` command generalizes the same safety check for explicit future candidates.

Example:

```bash
uv run species-coverage-audit --complex-id "4xhu__A1_P09874--4xhu__B1_Q9UNS1" --pdb-id 4xhu --chain receptor --source-uniprot P09874 --output-prefix 4xhu_p09874_reusable
```

Local smoke-test result for the historical `4xhu` / `P09874` case:

```text
Missing source ortholog coverage: ['bowhead_whale']
Missing local candidate file rows: []
```

Interpretation guard: this still should not be described as a complete expanded 5-vs-3 species panel while `bowhead_whale` source ortholog coverage is missing. No Boltz API calls are made by the audit command.

## Proposed live-run order

1. audit generated ids for 1nfi and 4xhu
2. dry-run 1nfi only
3. if the generated input is clean, run one explicit 1nfi live baseline
4. if 1nfi is maintained or otherwise recoverable, dry-run 4xhu
5. run 4xhu live only if the dry-run input is clean
6. move to species panels only after at least one relevant human baseline is
   recovered

## Interpretation gate

A future species-level cofolding result should be interpreted biologically
only if the matching human or technical baseline is recoverable.

If the human baseline is not recoverable, an incompatible species result is
not strong evidence for biological loss of interaction. It may simply reflect
a poor fragment choice, missing structural context, or an unsuitable Boltz
cofolding setup for that candidate.

## Notes

- Do not commit runtime outputs under data/output/.
- Do not commit signed Boltz structure URLs.
- Spend live Boltz calls one candidate at a time.
- Prefer explicit --control-id or candidate-id style execution over broad
  live panels.

## Candidate ids to audit

- 1nfi__A1_Q04206--1nfi__F1_P25963
- 4xhu__A1_P09874--4xhu__B1_Q9UNS1
- 7s68__D1_P09874--7s68__C1_P09874
- 8f86__K1_Q8N6T7--8f86__D1_P02281
- 8bhv__N1_P12956--8bhv__I1_Q9H9Q4
- 8bhv__P1_P13010--8bhv__J1_Q9H9Q4

## Manifest-driven candidate preflight

The reusable species coverage audit can be composed with candidate baseline and
NEGATOME-readiness checks through a manifest-driven dry-run CLI:

```bash
uv run cofolding-candidate-preflight-batch \
  --manifest data/interim/cofolding_candidate_manifest_smoke.csv \
  --output data/interim/cofolding_candidate_preflight_scorecard_smoke.csv
```

The manifest must include:

```text
candidate_id,chain,source_uniprot,priority
4xhu__A1_P09874--4xhu__B1_Q9UNS1,receptor,P09874,1
```

The command does not make Boltz API calls. It prepares the PINDER baseline input,
runs the species coverage audit, checks NEGATOME control readiness, and writes a
candidate-level scorecard with a recommended next action.

Current `4xhu` / `P09874` smoke result:

```text
baseline=input_prepared
species=missing_source_ortholog
negatome=partial_existing
next=fix_species_coverage
```

This means the human PINDER-fragment baseline input is available, but the
candidate should not be sent into a larger live batch yet because the expanded
species panel still has a source-ortholog coverage gap.

## Canonical SIRT6 candidate manifest

The committed candidate manifest defines the current SIRT6/core3-expanded
cofolding batch input:

```text
data/input/sirt6_cofolding_candidate_manifest.csv
```

It contains six explicit PINDER candidate ids from this shortlist, with the
chain/source-UniProt pair to audit and lightweight priority/context metadata.
This turns the previous manually typed smoke manifest into a reproducible
tracked input for the batch preflight stage.

Local preflight command:

```bash
uv run cofolding-candidate-preflight-batch \
  --manifest data/input/sirt6_cofolding_candidate_manifest.csv \
  --output data/interim/sirt6_cofolding_candidate_preflight_scorecard.csv
```

Local preflight result:

```text
candidate rows audited: 6
fix_species_coverage: 6
No Boltz API calls were made.
```

Interpretation:

- all six candidate baseline inputs can be prepared from local PINDER data;
- none should be promoted to a live species-panel batch yet;
- the current shared blocker is incomplete source-ortholog/species coverage;
- the generated scorecard is a local regenerable output under `data/interim/`,
  while the manifest itself is committed under `data/input/`.

This keeps the workflow moving toward automation without weakening the
interpretation gate before live Boltz spending.
