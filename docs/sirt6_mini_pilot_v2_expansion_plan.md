# SIRT6 mini-pilot v2 expansion plan

This document defines the proposed next expansion step after the current SIRT6 mini-pilot v1.

The goal is to expand the pilot while preserving the current interpretation discipline:

- the pipeline is reproducible and control-aware;
- shuffled-mask controls are implemented;
- NEGATOME-style scaffolding and validation are implemented;
- curated NEGATOME input rows are not yet populated;
- NEGATOME-style control ratios are not yet computed;
- `missing_negatome` remains an explicit status, not a bug.

## 1. Current v1 locked status

The current mini-pilot v1 is considered a reproducible, control-aware pilot.

Locked v1 capabilities:

```text
mini-pilot complex selection
mapped interface extraction
chain-pair quality control
interface-vs-background embedding enrichment
shuffled-mask controls
directional Mann-Whitney statistics
embedding signal classification
residue-level delta export
residue-level candidate summaries
interaction outcome classification
candidate scorecard generation
validation plan generation
NEGATOME-style candidate scaffold generation
NEGATOME input validation
NEGATOME curation guide and evidence notes
structure-selection exports for PyMOL and ChimeraX

```

Current v1 control status:

```text
shuffled mask controls: implemented
NEGATOME-style candidate scaffold: implemented
NEGATOME input validator: implemented
curated NEGATOME input rows: not yet populated
NEGATOME-style control ratios: not yet computed
scorecard/control status: missing_negatome where no curated input exists

```

## 2. Why expand now?

The v1 pilot is sufficient to test the pipeline mechanics and interpretation discipline.

The next goal is to test whether the same signal-extraction workflow remains useful when applied to a broader but still defensible set of longevity-relevant protein interactions.

The expansion should not aim to curate a complete interaction database from scratch. It should remain a focused preliminary-data generator.

## 3. Expansion principle

The v2 pilot should expand by adding biologically motivated complexes, not arbitrary proteins.

Each added row should have:

- a clear longevity, DNA repair, chromatin, stress-response, metabolism, or genome-maintenance rationale;
- a known or structurally modeled interaction context;
- identifiable source and partner chains;
- source and target UniProt identifiers;
- extractable or mappable interface residues;
- sequence coverage for selected target species;
- compatibility with the existing output schema.

## 4. Candidate biological themes

Preferred v2 themes:

```text
SIRT6-centered chromatin and DNA repair interactions
PARP-family and ADP-ribosylation context
Ku70/Ku80 and non-homologous end joining
DNA damage sensing and repair complexes
chromatin remodeling and histone-associated complexes
longevity-associated stress-response proteins
species-divergent genome-maintenance proteins

```

## 5. Candidate species

Keep the first v2 species set close to v1 unless there is a strong reason to expand.

Recommended initial species:

```text
mouse
naked_mole_rat
myotis_lucifugus

```

Optional later additions:

```text
human reference variants
bowhead whale
elephant
long-lived bats beyond myotis_lucifugus
additional rodent longevity models

```

Do not add many species at once until the v2 complex expansion is stable.

## 6. Inclusion criteria for v2 complexes

A complex can be considered for v2 if it satisfies most of the following:

- relevant to longevity, DNA repair, chromatin biology, stress resistance, or genome maintenance;
- has a known PDB structure or a defensible predicted structure path;
- has clear chain roles;
- has extractable or inferable interface residues;
- has source UniProt mappings;
- has target ortholog coverage for at least one initial target species;
- can be represented in the current mini-pilot output schema;
- does not require a new biological interpretation category before the current pipeline is validated.

## 7. Exclusion criteria

Do not add a candidate to v2 if:

- the biological rationale is weak or generic;
- the structure/chain mapping is ambiguous;
- the interface cannot be extracted or interpreted;
- the source or target UniProt mapping is unclear;
- the candidate requires large new infrastructure before the current pipeline is expanded;
- the candidate would silently change the meaning of existing scorecard fields;
- the candidate is included only because data are easy to obtain.

## 8. NEGATOME interpretation during expansion

NEGATOME-style controls should remain an explicit curation layer.

Expansion should not be blocked by missing NEGATOME rows, but missing rows must remain visible.

Correct interpretation during v2:

```text
candidate scaffold exists: yes
curated NEGATOME input exists: only if manually accepted row is present
NEGATOME-style ratio exists: only after computation step is implemented and run
missing_negatome: valid explicit status, not a pipeline failure

```

Do not treat generated scaffold rows as curated controls.

Do not populate `data/interim/negatome_control_pairs.csv` from scaffold rows unless the row has passed the curation guide and input contract.

## 9. Required pipeline invariants

The v2 expansion should preserve:

- existing output column names where possible;
- row-level control status;
- compatibility with current scorecard generation;
- compatibility with current validation plan generation;
- compatibility with current structure-selection export;
- test coverage for new selection or mapping logic;
- no committed generated `data/output` artifacts by default.

## 10. Proposed first implementation sequence

Recommended v2 implementation path:

1. add a small candidate-selection design note;
2. update or extend the mini-pilot selection logic with a small number of new complexes;
3. run chain/interface QC;
4. inspect failures before adding more complexes;
5. regenerate mapped enrichment outputs locally;
6. verify that scorecard and validation plan still run;
7. preserve explicit `missing_negatome` status for rows without curated input;
8. only then consider expanding species or adding more complexes.

## 11. First v2 size target

The first v2 expansion should be modest.

Recommended target:

```text
v1: current small mini-pilot
v2 first pass: add approximately 5-10 carefully selected complex/chain contexts
v2 later pass: expand only after QC and scorecard interpretation remain stable

```

This keeps the expansion interpretable and prevents the pilot from becoming an uncontrolled database-building task.

## 12. Decision

The next development step should be a controlled v2 expansion, not further deep manual curation of PARP1 NEGATOME controls.

Rationale:

```text
PARP1 NEGATOME curation has been attempted.
Negatome 2.0 provides only P07437/TUBB and O60907/TBL1X for P09874.
Neither is ready for strict input promotion.
The pipeline already records this honestly as missing_negatome.
The most useful next step is to test whether the pipeline generalizes to a broader candidate set while preserving explicit control status.

```

