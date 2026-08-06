# The proximal 3' UTR indel deficit is cell-cycle specific

Every layer of the regulatory arc has been measured on cell-cycle / tumour-suppressor genes, and
the working claim is framed accordingly — tighter cell-cycle control in long-lived, cancer-
resistant mammals (Peto's paradox). **That framing had never been tested.** If housekeeping genes
showed the same proximal indel deficit
([constraint nature](../2026-08-07-utr-constraint-nature/RESULT.md)), the finding would not be
about the cell cycle at all but about 3' UTRs of long-lived mammals in general — a different,
arguably larger, claim, and one that would have invalidated the Peto framing carried since the
[extended panel](../2026-08-05-extended-panel/RESULT.md).

It survives.

## Design

Control modules (`data/config/control_modules.tsv`), 24 genes in three blocks: ribosomal
proteins, core glycolysis, and cytoskeleton / TCA enzymes. They are broadly expressed and
strongly constrained at the protein level — comparable to the cell-cycle set in overall
constraint — while having no established link to lifespan. Proteostasis and nuclear-pore genes
were deliberately excluded despite being convenient housekeeping sets: both are recognised
hallmarks of ageing and cannot serve as negative controls.

The primary statistic is a **within-species contrast**, the device that kept the structure and
embedding layers interpretable:

    delta = proximal indel rate (cell-cycle) - proximal indel rate (control)

Both terms come from the same species through the same machinery, so every species-level
nuisance — mutation rate, generation time, genome and annotation quality, alignment behaviour —
cancels in the difference.

## Results

Proximal 3' UTR, **indel** metric, 57 species, PGLS on lifespan + mass:

| gene set | n genes | slope | 95 % CI | p |
|---|---|---|---|---|
| **cell-cycle** | 25 | **−0.0465** | [−0.0709, −0.0221] | **0.0003** |
| **control, all** | 24 | **−0.0016** | **[−0.0316, +0.0285]** | **0.92** |
| control: ribosome | 8 | −0.0077 | [−0.0715, +0.0561] | 0.81 |
| control: glycolysis | 8 | −0.0138 | [−0.0477, +0.0200] | 0.42 |
| control: cytoskeleton / TCA | 8 | +0.0119 | [−0.0364, +0.0603] | 0.62 |
| **delta (cell-cycle − control)** | — | **−0.0449** | [−0.0756, −0.0142] | **0.0049** |

**This is a real null in the controls, not a power failure.** The control interval **excludes**
the cell-cycle slope (−0.0465 lies below −0.0316); the effect differs by a factor of 29; and all
three blocks are independently flat, one of them with a positive point estimate. Nor is the null
caused by lack of variation: control genes carry *more* proximal indels than cell-cycle genes on
average (0.352 vs 0.216), so there was more room to detect a deficit, not less.

The within-species contrast is significant at p = 0.0049, which is the cleanest statement
available: in the same animal, the cell-cycle module's proximal 3' UTR is indel-constrained
relative to its own housekeeping genes, and that gap widens with lifespan.

## What we are *not* claiming

The substitution metric produces a tempting mirror image: cell-cycle p = 0.15 (the familiar
null), while the controls reach p = 0.0048 (ribosome 0.020, glycolysis 0.024, cytoskeleton/TCA
0.090). Read carelessly this is a double dissociation — "cell-cycle genes conserve length,
housekeeping genes conserve sequence."

**That claim is not supported and is not made here.** The substitution contrast between modules
is not significant (delta p = 0.16), the two intervals overlap heavily
([−0.0150, +0.0023] vs [−0.0208, −0.0040]), and power is comparable in both sets. There is no
statistical basis for separating the substitution slopes. Both point the same way as the neutral
intronic substitution trend measured in the
[intron control](../2026-08-08-intron-neutral-control/RESULT.md) (−0.0088, p = 0.087), so the
parsimonious reading is a single weak lineage-level substitution-rate effect surfacing wherever
power allows — not two mechanisms.

**Module specificity belongs to the indel component alone.** That is what this layer establishes.

## A data-integrity guard, added here

Building this panel surfaced a failure mode worth recording. NCBI gene resolution returned a
*genomic* record instead of an mRNA for one pair — GAPDH in rabbit came back as chromosome
`NC_091435.1`, a 144 Mb "3' UTR", reproducibly across two independent fetches. Nothing would have
crashed: the analysis truncates to 3 kb, so the first 3 000 nt of a rabbit chromosome would have
entered the statistics as a UTR. `MAX_PLAUSIBLE_UTR = 20 000` now drops such records and names
each one on stdout. Real mammalian 3' UTRs in this panel reach ~13 kb (CDK6 ~10 kb, MDM4 ~13 kb),
so the threshold discards resolution failures without touching biology: across 3 231 records it
drops exactly two (GAPDH/rabbit and FH/squirrel-monkey at 28 kb). **The cell-cycle panel contains
no such records**, so the previously merged results are unaffected.

## Bounds

- **Housekeeping is not the same as unconstrained.** These genes are strongly conserved; the
  control shows that lifespan-linked *indel* constraint is absent there, not that their 3' UTRs
  are free.
- **Coverage is uneven across control genes.** All 24 are included; 23 carry 49–61 species, but
  TUBA1B carries only 37. Its failures are scattered across clades rather than blocked in time,
  so this is genuine absence of an annotated ortholog — tubulin paralogues resolve poorly by
  symbol — rather than a fetch problem. It is one gene of 24 inside a block that is flat on its
  own (cytoskeleton / TCA, p = 0.62), so it cannot be driving the control null.
- Three control blocks were chosen a priori, but "no established link to lifespan" is a judgement
  about a literature, not a measurement. A different housekeeping set could behave differently.
- Human-anchored pairwise alignment throughout, inherited from the whole arc; indel calls remain
  alignment calls under one gap-penalty regime.
- The contrast tests cell-cycle against *these* controls. It does not establish that the
  cell-cycle module is unique among all functional modules — only that it differs from broadly
  expressed housekeeping genes.

## Reproducing

```
uv run python scripts/fetch_panel_utr.py --genes RPL5,RPL11,RPL13A,RPS3,RPS6,RPS14,RPS19,RPLP0,\
GAPDH,ALDOA,ENO1,PKM,PGK1,TPI1,LDHA,HK1,ACTB,ACTG1,TUBB,TUBA1B,SDHA,CS,MDH1,FH
uv run python scripts/analyze_utr_constraint_geometry.py --gene-set all --cache-only
uv run python scripts/analyze_module_specificity.py --metric indel \
    --out-dir docs/results/2026-08-09-module-specificity
uv run python scripts/analyze_module_specificity.py --metric substitution \
    --out-dir docs/results/2026-08-09-module-specificity
```

Alignments are cached in `data/interim/utr_panel/aln_cache/`; UTR fastas and caches are
gitignored and regenerable.
