# RELA / NF-κB lead — targeted follow-up

Date: 2026-07-28
Status: **technical checkpoint — the lead does not hold up; not a validated claim.**

## Motivation

In the SIRT6 panel, RELA/p65 (1nfi receptor) was the single interface that (a) diverged (enrichment
> 1), (b) leaned long-lived-ward, and (c) appeared interface-specific under NEGATOME in the early
4-complex run. NF-κB is central to "inflammaging", and naked mole-rats have altered NF-κB/inflammatory
signaling — so this was the natural lead to drill into. It was examined with existing embeddings (no
new API calls) using three tests.

## Per-species record (both chains)

| Chain | Species | Group | enrichment | enr/neg | Cohen's d | p (within-species) |
|---|---|---|---|---|---|---|
| RELA (receptor) | elephant | long | 1.354 | 0.876 | 0.78 | 1.0e-7 |
| RELA (receptor) | naked_mole_rat | long | 1.298 | 0.835 | 0.67 | 9.1e-7 |
| RELA (receptor) | myotis_lucifugus | long | 1.276 | 0.766 | 0.62 | 1.0e-6 |
| RELA (receptor) | mouse | short | 1.165 | 0.712 | 0.38 | 7.1e-4 |
| RELA (receptor) | rat | short | 1.284 | 0.758 | 0.65 | 2.0e-6 |
| RELA (receptor) | hamster | short | 1.283 | 0.800 | 0.66 | 2.0e-6 |
| IκBα (ligand) | naked_mole_rat | long | 0.978 | 1.047 | −0.04 | 0.28 |
| IκBα (ligand) | (others) | — | 1.08–1.15 | 0.86–1.05 | 0.24–0.48 | — |

## Three tests, three failures

1. **Significance.** Contrast Mann-Whitney (3 long vs 3 short) p = 0.40, Benjamini-Hochberg q = 0.71.
   Not significant (3v3 is underpowered by design).

2. **Convergence across long-lived lineages — FAIL.** A real longevity signal requires the long-lived
   species to consistently exceed the short-lived. They do not: the minimum long-lived value (myotis
   1.276) is **below** the maximum short-lived value (rat 1.284). Rat — a short-lived rodent — diverges
   as much as the long-lived species. The +0.065 group mean difference is driven by elephant being high
   and mouse being low (a single-species pattern), not a coherent long-lived signature. On the IκBα side
   the only outlier is naked mole-rat being uniquely *conserved* — again a single-species effect, not
   convergence.

3. **Interface-specificity under the corrected NEGATOME — FAIL.** After fixing the ortholog-indexing
   bug, RELA's `enr/neg < 1` in **all six species** (0.71–0.88): the interface diverges *less* than the
   generic non-partner (tubulin) coupling baseline. In other words this is a broadly variable surface,
   not a change specific to the RELA–IκBα interaction. The earlier `enr/neg ≈ 1.20` that made RELA look
   interface-specific was an artifact of the indexing bug (`negatome_analyze.py`), now fixed and covered
   by a regression test.

## Conclusion

The RELA/NF-κB interface is genuinely divergent and biologically variable (strong within-species
localization, Cohen's d up to 0.78), but its divergence is **not longevity-specific**: it is not
significant, not convergent across long-lived lineages, and not specific beyond the non-partner
baseline once the NEGATOME control is computed correctly. The single apparent lead in the panel was
partly inflated by the NEGATOME bug; correcting it dissolves the lead. This strengthens, rather than
qualifies, the panel-wide negative result.

A properly powered revisit (≥5 long vs ≥5 short species, per-protein NEGATOME-verified non-interactors,
and per-residue convergence analysis) could re-examine RELA, but the current evidence does not support
it as a longevity-portability candidate.
