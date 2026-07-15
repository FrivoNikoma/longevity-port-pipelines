# First TP53/MDM2 MDM2-side shuffled-interface control result

## Result

This result tests the real human `1YCR` MDM2 chain-`A` geometric interface
mask against deterministic same-size masks drawn from the same observed
`85`-residue MDM2 chain.

The true mask contains `47` chain-local positions. TP53 chain `B` is not shuffled because all `13` parsed TP53 residues are already inside its
interface mask, making a size-preserving within-chain TP53 shuffle
degenerate.

## Deterministic control contract

- RNG: `numpy.random.default_rng`;
- seed: `42`;
- control masks: `1000`;
- each control mask: `47` distinct positions sampled without replacement
  from chain-local indices `0..84`;
- each sampled mask is sorted before metric calculation;
- serialized control-mask stream SHA256:
  `6ebc3aea77388a9929d945acdb1962fe8eed148feecac7326fcbeceefbe2015c`;
- unique sampled masks: `1000`.

The existing generic `analyze.py::shuffled_control` also uses deterministic
NumPy RNG with seed `42`, but it operates on embedding deltas. This
result-specific control does not call that function because this PR reads no
embedding arrays and computes no embedding enrichment score.

## Numerical metrics

| Metric | True MDM2 mask | Shuffled mean | Shuffled population SD | Range | Null-tail count | Add-one empirical p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Adjacent residue pairs | `38` | `25.4239999999999995` | `2.3315711441000468` | `18..33` | `0 / 1000` controls had at least the true value | `0.0009990009990010` |
| Contiguous runs | `9` | `21.5760000000000005` | `2.3315711441000468` | `14..29` | `0 / 1000` controls had at most the true value | `0.0009990009990010` |
| Longest contiguous run | `16` | `6.6260000000000003` | `1.8243146658402984` | `3..18` | `1 / 1000` controls had at least the true value | `0.0019980019980020` |

The real mask is therefore more sequence-contiguous than the deterministic
same-size null masks under the three committed compactness summaries. This
is a statement about the chain-local organization of the previously
extracted geometric contact mask only.

## Interpretation boundary

This result does not establish binding, binding energetics, binding
hotspots, functional significance, orthology, elephant compatibility,
beneficial breakage, or longevity evidence. It is not a biological claim.

This PR performs no curated NEGATOME control, no Biohub / ESMC call, no
embedding generation, no `.npy` read or commit, no `data/output` commit, no Boltz / AF3 / Chai call, no Gate 8 or Gate 9 promotion, and no comparative
elephant interface scoring.

The result adds no generic shuffle framework. The deterministic computation
is local to this result-bearing TP53/MDM2 checkpoint.

## Next result-bearing action

`add_first_tp53_mdm2_curated_negatome_interface_control_result`

No inventory-only, preflight-only, plan-only, approval-only, review-only,
runtime-preparation-only, scaffold-only, generic-shuffle-framework-only, or
other non-result PR should precede that curated NEGATOME control result.
