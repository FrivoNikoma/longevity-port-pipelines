# Refreshed SIRT6 core3 signal notes

## Status

The refreshed SIRT6 core3 run is technically complete through:

- saved Biohub embeddings
- mapped interface enrichment
- embedding signal summary
- first long-lived vs short-lived contrast
- shortlist species-level review

Embedding coverage is complete:

- target ortholog embeddings: 125 / 125 ok
- planned embedding files including human references: 147 / 147 present
- ortholog files: 125
- human/reference files: 22

Mapped enrichment analysis completed with:

- 125 enrichment rows
- skipped no interface: 0
- skipped no mapping: 0
- skipped missing embedding: 0

## Signal summary

The refreshed mapped enrichment summary contains 125 rows.

Signal class counts:

- interface divergent: 37
- interface constrained: 35
- weak or mixed: 44
- interface divergent, not significant: 4
- interface constrained, not significant: 5

The enrichment distribution is heterogeneous rather than globally shifted:

- min enrichment ratio: 0.649
- median enrichment ratio: 1.006
- mean enrichment ratio: 1.058
- max enrichment ratio: 2.681

Effect sizes are also mixed:

- min Cohen's d: -1.254
- median Cohen's d: 0.011
- mean Cohen's d: 0.122
- max Cohen's d: 4.292

This argues against a simple global pattern such as "all long-lived species are more divergent" or "all long-lived species are more constrained".

## Predicted-structure sanity check

The signal does not appear to be driven solely by predicted structures.

Experimental rows:

- n = 51
- mean enrichment = 1.065
- median enrichment = 1.016
- mean effect size = 0.165
- median effect size = 0.031

Predicted rows:

- n = 74
- mean enrichment = 1.052
- median enrichment = 1.003
- mean effect size = 0.092
- median effect size = 0.005

Predicted rows are not inflated relative to experimental rows in this run.

## Long-lived vs short-lived contrast shortlist

The first strict contrast shortlist used the filter:

`abs(delta_effect) >= 0.5 OR abs(delta_enrichment) >= 0.25`

This produced four candidate complex/chain cases.

### 1. 8bhv__P1_P13010--8bhv__J1_Q9H9Q4, ligand

Direction:

- long-lived more constrained relative to short-lived controls

Group-level values:

- mean ER long-lived: 1.796
- mean ER short-lived: 2.179
- delta ER: -0.382
- mean effect long-lived: 2.146
- mean effect short-lived: 3.539
- delta effect: -1.393

Species-level caution:

- naked mole-rat is strongly interface-divergent
- Myotis lucifugus is flat / weak
- short-lived controls are all strongly interface-divergent

Interpretation:

This is not a clean "all long-lived constrained" case. It is better described as short-lived controls being even more interface-divergent than the long-lived group average.

### 2. 7sgl__C1_P13010--7sgl__D1_Q96SD1, ligand

Direction:

- long-lived more constrained relative to short-lived controls

Group-level values:

- mean ER long-lived: 1.153
- mean ER short-lived: 1.807
- delta ER: -0.653
- mean effect long-lived: 0.248
- mean effect short-lived: 1.575
- delta effect: -1.327

Species-level pattern:

- rat, hamster, and mouse are strongly interface-divergent
- elephant and naked mole-rat are weak or mixed
- Myotis lucifugus is moderately divergent

Interpretation:

This is a stronger candidate for short-lived-enriched interface divergence, or equivalently relative long-lived interface constraint.

### 3. 7sgl__B1_P12956--7sgl__D1_Q96SD1, ligand

Direction:

- long-lived more divergent relative to short-lived controls

Group-level values:

- mean ER long-lived: 1.551
- mean ER short-lived: 1.027
- delta ER: +0.524
- mean effect long-lived: 0.817
- mean effect short-lived: 0.048
- delta effect: +0.768

Species-level caution:

- elephant is strongly interface-divergent
- naked mole-rat and Myotis lucifugus are weak or mixed
- short-lived controls are weak or mixed

Interpretation:

This is a candidate long-lived-enriched divergence case, but it may be driven mainly by elephant rather than by the full long-lived group.

### 4. 8bhy__B1_P12956--8bhy__G1_P49917, receptor

Direction:

- long-lived more constrained relative to short-lived controls

Group-level values:

- mean ER long-lived: 0.800
- mean ER short-lived: 1.042
- delta ER: -0.242
- mean effect long-lived: -0.426
- mean effect short-lived: 0.081
- delta effect: -0.507

Species-level pattern:

- naked mole-rat is interface-constrained
- Myotis lucifugus is constrained but not significant
- short-lived controls are weak or mixed

Interpretation:

This is a candidate long-lived interface-constraint case, but elephant is absent from the long-lived side for this complex/chain.

## Interim interpretation

The refreshed SIRT6 core3 signal is interaction-specific and heterogeneous.

The current result should be described as:

- a technically complete refreshed embedding and mapped-interface analysis
- a first candidate contrast shortlist
- not yet a validated longevity mechanism
- not yet a universal long-lived-vs-short-lived pattern

The strongest next filters are:

1. separate single-species-driven cases from multi-species-consistent cases
2. distinguish experimental and predicted structure support at species level
3. check whether the candidate interfaces map to known functional surfaces
4. apply or extend negative/shuffled controls where available
5. produce a manual residue-level review shortlist for the four contrast cases
