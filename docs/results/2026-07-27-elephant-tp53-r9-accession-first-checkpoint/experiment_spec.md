# Causal experiment specification: p53-R9 G23W reversion

## Scientific question

Does the retrogene-family `W23G` change contribute causally to
the p53-R9 phenotype by weakening MDM2 regulation, or is the
published mitochondrial Tid1/Bax phenotype driven primarily
by truncation or other retrogene-specific sequence changes?

The experiment is designed to separate four mechanisms:

1. direct MDM2 escape caused by `W23G`;
2. protection of canonical TP53 through a guardian interaction;
3. a generic consequence of truncating elephant TP53 to 180 aa;
4. a p53-R9-specific Tid1/Bax mitochondrial mechanism.

## Why this experiment is needed

The published literature contains an unresolved assay conflict.

- Abegglen et al. reported a band interpreted as MDM2
  co-immunoprecipitating with elephant p53 retrogene 9.
- Sulak et al. argued that the reported band was not at the
  expected MDM2 size, found no MDM2 co-immunoprecipitation
  with TP53RTG12, and linked the loss of binding to `W23G`.
- The Sulak author response reports that Abegglen RTG9 and
  their TP53RTG12 sequence were 100% identical at nucleotide
  and protein level.
- Preston et al. showed that 180-aa p53-R9 can drive
  Tid1/Bax-associated mitochondrial apoptosis.

The same standardized construct panel must therefore measure
MDM2 interaction, protein turnover and mitochondrial apoptosis
in parallel.

## Primary causal contrast

`p53-R9 WT (G23)` versus `p53-R9 G23W`.

The evidence is interpreted in three pre-specified tiers:

1. **Binding-causal:** `G23W` increases direct MDM2
   association in at least two orthogonal assay formats.
2. **Regulatory-causal:** binding rescue is accompanied by an
   MDM2-dependent change in p53-R9 regulation or by a change
   in its guardian effect on canonical TP53.
3. **Phenotype-causal:** the regulatory change alters
   abundance-adjusted apoptosis or TP53 signaling and is not
   reproduced completely by a matched 180-aa truncation of
   canonical elephant TP53.

Restoring MDM2 binding without changing downstream readouts
supports a causal role for `W23G` in loss of binding, but not
a causal role in the mitochondrial phenotype.

## Experimental phases

### Phase A: construct-intrinsic mechanism

Use one p53-null mammalian cell context to compare all
constructs without interference from endogenous p53.

This phase establishes:

- direct MDM2 association;
- protein turnover;
- Tid1 and Bax interaction;
- mitochondrial localization;
- cytochrome-c/caspase/apoptosis response.

A p53-null context comparable to the system used for the
published p53-R9 mitochondrial study is preferred. HEK293
must not be the sole mechanistic system because its viral
transforming proteins alter p53 regulation.

### Phase B: guardian mechanism

Repeat the critical WT-versus-G23W comparisons in a context
containing canonical elephant TP53.

This phase tests whether p53-R9:

- interacts with canonical elephant TP53;
- changes canonical TP53 ubiquitination or stability;
- changes the threshold or amplitude of TP53 signaling.

Elephant fibroblast validation is the preferred biological
context after Phase A establishes interpretable construct
behavior.

## Construct identity requirements

The committed `KF715863.1` 180-aa protein is a hashed working
sequence, not an independently recovered plasmid insert.

Before experimental execution:

- verify the exact expression-insert sequence;
- hash the final WT and G23W amino-acid sequences;
- confirm that the only intended WT-versus-reversion
  difference is residue 23;
- use matched tags and expression architecture across the
  causal pair;
- verify comparable expression before interpreting downstream
  phenotypes.

## Important turnover caveat

The 180-aa p53-R9 protein lacks the canonical C-terminal p53
lysines that are predominant targets of MDM2-mediated
ubiquitination and degradation. It retains potential lysine
targets in the N-terminal/DNA-binding portion, but restored
MDM2 association may therefore occur without canonical
full-length-p53 turnover.

Consequently:

- absence of a ubiquitination or stability change does not
  refute restored MDM2 binding;
- turnover is a secondary mechanistic endpoint for p53-R9;
- the full-length canonical elephant TP53 control is required
  to verify that the MDM2 assay can detect expected turnover;
- binding, localization, guardian behavior and phenotype must
  be interpreted separately.

## Endpoint hierarchy

### Primary proximal endpoint

MDM2 association of p53-R9 WT versus p53-R9 G23W.

The result must be supported by two orthogonal approaches,
rather than a single co-immunoprecipitation band.

### Primary phenotypic endpoint

Apoptosis difference between p53-R9 WT and p53-R9 G23W after
normalization for construct abundance.

### Secondary endpoints

- p53-R9 ubiquitination and stability;
- canonical elephant TP53 ubiquitination and stability;
- p53-R9 interaction with canonical TP53;
- Tid1 interaction;
- mitochondrial localization;
- Bax interaction;
- cytochrome-c release;
- caspase activation;
- TP53 response-element signaling in the guardian phase.

## Statistical and reproducibility requirements

- Pre-register the WT-versus-G23W primary contrast.
- Use independent biological replicates performed on
  different days.
- Determine sample size prospectively from pilot variance
  and a predefined minimum effect of biological interest.
- Randomize sample processing and blind quantitative image
  or band analysis where feasible.
- Normalize interaction and phenotype readouts to verified
  construct abundance.
- Treat MDM2/turnover, guardian and mitochondrial endpoints as
  separate endpoint families and control multiplicity within
  each family.
- Report effect sizes and uncertainty, not only p-values.
- Do not promote a mechanism from one cell context or one
  assay format.

## Stop/go decisions

### Go: binding-causal MDM2 escape

Conclude that `W23G` is causal for loss of MDM2 binding when
`G23W` restores association in orthogonal assays.

Advance to a phenotype-causal claim only when a downstream
regulatory or phenotypic consequence is also demonstrated.

### Go: distinct mitochondrial mechanism

Proceed with Tid1/Bax work when `G23W` changes MDM2
association or turnover but does not change mitochondrial
apoptosis.

### Stop: W23G insufficient

Do not claim W23G-mediated escape when `G23W` fails to change
MDM2 association in orthogonal assays.

### Redirect: truncation-dominant mechanism

Prioritize truncation/domain architecture when matched
180-aa canonical TP53 controls reproduce the p53-R9
phenotype.

## Claim boundary

This package is an experimental decision specification, not
evidence that `W23G` is beneficial, that p53-R9 causes
elephant cancer resistance, or that the phenotype affects
organismal longevity.

All laboratory execution must follow the host institution's
approved cell-culture, genetic-manipulation and chemical
safety procedures.

## Primary sources

- Abegglen et al. 2015:
  `10.1001/jama.2015.13134`
- Sulak et al. 2016:
  `10.7554/eLife.11994`
- Preston et al. 2023:
  `10.1038/s41420-023-01348-7`
