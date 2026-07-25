# SIRT6 8g57 five-species result

## Result

The historical sequence-mapped `8g57` histone-H2A interface analysis was
reproduced exactly and extended from mouse to rat and hamster controls.
The resolved structure chains are `K/G`, with 38 ligand interface residues
at the 8 Å heavy-atom cutoff.

| Group | Species | Taxid | Accession | Enrichment | Interface substitutions |
|---|---|---:|---|---:|---:|
| long_lived | naked_mole_rat | 10181 | `G5BV53` | 1.412505 | 3 |
| long_lived | myotis_lucifugus | 59463 | `G1P399` | 1.284767 | 6 |
| short_lived_control | hamster | 10036 | `A0ABM2YD99` | 0.845637 | 0 |
| short_lived_control | rat | 10116 | `D3ZVK7` | 0.811451 | 0 |
| short_lived_control | mouse | 10090 | `H2A3_MOUSE` | 0.802751 | 0 |

Both independent long-lived lineages are above all three short-lived
controls. The minimum long-lived enrichment is
`1.284767491209` and the maximum
short-lived enrichment is `0.845637387781`.

## Sequence-divergence limitation

The long-lived species are also the only species in this panel with
substitutions at the 38-residue H2A interface. Simple full-sequence and
interface-divergence adjustments reduce the contrast and do not separate
a longevity-associated effect from ordinary sequence divergence.

The committed classification is
`sequence_divergence_confounding_not_resolved`.
This is not a phylogenetic correction.

The lane is closed as `closed_pending_divergence_decoupling_species`.
It should be reopened only when species break the present correlation
between lifespan group and interface divergence.

## Claim boundaries

This result does not establish altered SIRT6-nucleosome binding affinity,
beneficial or harmful function, a causal longevity mechanism, or readiness
for structural-model promotion.

## Validation

```bash
uv run python -m scripts.record_sirt6_8g57_result
uv run python -m scripts.record_sirt6_8g57_result \
  --validate-runtime-root <path-to-sirt6_8g57_sequence_package>
```
