# Boltz follow-up panel plan

## Goal

Define a small, controlled Boltz follow-up panel before running additional live API predictions.

The goal is not to perform a broad sweep. The goal is to test whether the cofolding stage can produce reproducible, interpretable structural compatibility signals for a small number of high-priority cross-species protein-protein complexes.

## Background

The first Boltz live smoke panel was technically successful, but the structural classifications remained uncertain across the tested predictions. That suggests the next step should be a controlled follow-up panel rather than a large live run.

The cofolding stage has since been hardened with:

- explicit `--yes-live` protection for live prediction starts
- dry-run input inspection via `--dry-run-inputs`
- prediction retrieval recovery via `--retrieve-prediction`
- retry logic around Boltz prediction retrieval
- tests for species mapping, cross-species pair construction, retry behavior, and live-run safety

## Biological rationale

The cofolding stage asks whether a human protein partner can still form a plausible complex with an orthologous chain from another species.

For each candidate interaction:

- one chain remains human
- the analyzed chain is replaced by an ortholog from the target species
- Boltz evaluates whether the resulting cross-species complex remains structurally compatible

This is useful for longevity-oriented comparison because long-lived species may preserve, weaken, or remodel specific protein-protein interfaces relative to short-lived controls.

## Priority module: SIRT6 DNA repair

The first follow-up panel should focus on `sirt6_dna_repair`.

Reasons:

- It already has the richest local evidence base in this repository.
- It has prior SIRT6/core3 analysis, NEGATOME closure, scorecard outputs, and manual-review notes.
- It already reached the Boltz smoke-test stage, so the follow-up is a continuation of an existing analysis rather than a new biological branch.
- DNA repair is biologically central to longevity, genome stability, and stress-response hypotheses.

## Candidate selection principles

Select a small number of cases that satisfy most of the following:

- present in the SIRT6/core3 expanded analysis
- has usable ortholog coverage for the target species
- has prior interface enrichment or residue-level signal
- has interpretable receptor/ligand chain assignment
- has no obvious sequence-length or partner-mapping issue
- has biological relevance to DNA repair or chromatin-associated repair

Avoid cases where the dry-run shows missing ortholog sequence, ambiguous complex parsing, or severe input mismatch.

## Initial target species

Use a small species panel:

- `myotis_lucifugus` — long-lived small-bodied mammal
- `naked_mole_rat` — long-lived small-bodied mammal
- `mouse` — short-lived control

This gives a minimal long-lived vs short-lived contrast without expanding the live run too much.

## Proposed live-run size

Start with:

- 2-3 complexes
- 2-3 target species per complex
- `num_samples=3`

This gives enough repeated samples to check whether the signal is stable, while keeping credit usage bounded.

The first objective is reproducibility, not discovery volume.

## Preflight before live API calls

Before any live run, run dry-run input inspection:

```bash
uv run cofolding --dry-run-inputs --top-n 10

```

For selected cases, use more specific filters:

```bash
uv run cofolding --dry-run-inputs --complex <complex_id> --species <target_species> --top-n 1

```

Only promote cases to live Boltz calls if the dry-run confirms that:

- the complex ID parses successfully
- the target species is known through `SPECIES_REGISTRY`
- the ortholog sequence is available
- the human partner sequence can be fetched
- sequence lengths look plausible
- no Boltz API call is made during dry-run

## Live-run command pattern

For each approved case:

```bash
uv run cofolding --complex <complex_id> --species <target_species> --top-n 1 --num-samples 3 --yes-live

```

Do not run broad live sweeps until the focused panel produces interpretable and reproducible results.

## Interpretation categories

Interpret Boltz outputs conservatively.

Possible follow-up categories:

### Preserved interface

The cross-species complex remains structurally compatible.

This may indicate that the interface is conserved despite sequence divergence.

### Rewired but viable interface

The sequence/interface signal differs, but the complex still appears structurally plausible.

This is the most interesting class for longevity-oriented follow-up because it may indicate functional remodeling rather than simple breakage.

### Broken or incompatible interface

The cross-species complex appears structurally weak or incompatible.

This can be biologically interesting, but interpretation depends on the interaction. In some systems, weakening an interaction may be beneficial rather than harmful.

### Uncertain

Metrics are not strong enough for interpretation.

Uncertain cases should not be overinterpreted. They may require reruns, more samples, better complex selection, or a different structural question.

## Success criteria

This follow-up panel is successful if it produces:

- a small table of completed Boltz predictions
- reproducible metrics across samples
- clear dry-run and live-run provenance
- at least one interpretable preserved, rewired, broken, or consistently uncertain case
- a decision about whether to expand to HAS2/CD44 or another candidate set

## Next candidate set after SIRT6

If the SIRT6 follow-up panel is technically clean and biologically interpretable, the next candidate set should be `has2_cd44_nmr`.

Rationale:

- strong naked mole-rat relevance
- connection to hyaluronan biology and extracellular matrix
- phenotype-level relevance to longevity and cancer resistance hypotheses

Caution:

HAS2/CD44 biology may produce indirect interface signals because the core phenotype is tied to extracellular matrix structure and hyaluronan metabolism, not only to a simple binary protein-protein interface.

## What not to do yet

Do not run:

- all candidate sets
- all species
- high `num_samples`
- live API calls without dry-run inspection
- threshold tuning based on one or two predictions
- biological claims from single uncertain predictions

The next step should remain a small controlled structural follow-up panel.

## Cofolding control-selection gate

Before running additional live Boltz panels, run:

```bash
uv run cofolding-controls
```

Rationale:

- PINDER rows are structural chain-pairs, not automatically biological
  receptor/ligand pairs.
- High-confidence PINDER rows can include homomers, capsids, viral assemblies,
  repeated chains, or non-human proteins.
- Cross-species incompatibility should not be interpreted biologically unless
  the corresponding human-human or technical positive-control baseline is
  recoverable.

The audit stage is cheap: it fetches/caches UniProt metadata and writes a local
CSV under `data/output/`, but it does not call Boltz or spend prediction credits.
