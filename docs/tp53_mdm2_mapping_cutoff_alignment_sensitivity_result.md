# Scoped MDM2 A2 mapping/cutoff/alignment sensitivity result

## Status

This is a committed technical A2 robustness result for the narrow MDM2 lane.
It tests whether the A1 residue-level interface-depletion direction survives
predeclared coordinate, interface-cutoff, and alignment choices. It does not
perform Gate 8 disposition, does not open Gate 9, and makes no biological
claim.

## Bound artifacts

| Artifact | Rows | Canonical text SHA-256 |
| --- | ---: | --- |
| `data/input/tp53_mdm2_1ycr_q00987_full_chain_mapping.csv` | 85 | `2794c3adabb69ff739e24af6179d587424acab293407d44b536bf0a8111dbb5f` |
| `data/input/tp53_mdm2_mdm2_mapping_cutoff_alignment_sensitivity_results.csv` | 485 | `33ec3211de227cab56367528019f7a17041759e29a8cf16795dd41db5ae26c07` |
| `data/input/tp53_mdm2_mdm2_mapping_cutoff_alignment_sensitivity_summary.csv` | 3 | `db58d84a53b2a891eb80d5e065457355c48d6a198cea7a84b47d44b392895ba4` |

The three CSV hashes use UTF-8 text after an optional BOM is removed and
`CRLF` or bare `CR` line endings are normalized to `LF`. This makes committed
result validation invariant to Git's Windows checkout conversion while still
binding column order, row order, field content, delimiters, and the trailing
newline.

The PDB bytes are bound to SHA-256
`7b4e503dea1fe3a6966b9676a1b98caf511c735cde01029cd0998e2319e75493`.
The complete resolved `1YCR:A` chain contains 85 residues, PDB positions
25–109, which map uniquely and identity-consistently to full-length `Q00987`
zero-based indices 24–108. The committed 8 Å A1 interface is exactly
reproduced from this full-chain map.

## Predeclared grid

The audit uses five heavy-atom interface cutoffs: 6, 7, 8, 9, and 10 Å. The
corresponding MDM2 masks contain 30, 42, 47, 54, and 56 residues and are
nested. Five Biotite BLOSUM62 policies vary terminal penalties, gap opening,
and gap extension. Every optimal alignment trace is retained, identified by
SHA-256, and passed explicitly into the same A1 residue-level L2 metric.

This produces:

- 225 elephant `G3SX30` scenarios;
- 200 mouse `P23804` scenarios;
- 60 hamster `A0ABM2YB85` scenarios;
- 485 scenarios in total.

Every scenario uses 1,000 deterministic, same-size shuffled masks with seed
42 in the identical metric family. The historical geometric shuffled result
and embedding-based NEGATOME ratio are not mixed into this calculation.

## Numerical result

| Target | A1 baseline | A2 min | A2 median | A2 max | Cohen's d range | Direction flips | Lower-tail shuffled pass | Complete mappings |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Elephant `G3SX30` | `0.59271069444374358` | `0.58594152898225094` | `0.59717637154973469` | `0.65347819296783838` | `-0.58204662952195763` to `-0.47769213442143316` | 0 | 225/225 | 225/225 |
| Mouse `P23804` | `0.51464311118804662` | `0.50870249919165011` | `0.516274601027505` | `0.57404154378007133` | `-0.78877882064632165` to `-0.66074558709042586` | 0 | 200/200 | 200/200 |
| Hamster `A0ABM2YB85` | `0.59823664002011123` | `0.55829361372217545` | `0.59388455174971477` | `0.61265994493139697` | `-0.73415503144465233` to `-0.62885322001902544` | 0 | 60/60 | 60/60 |

All 485 ratios remain below 1, all effect sizes remain negative, every source
interface residue maps, every shuffled lower-tail empirical p-value is at most
0.05, and all three canonical A1 rows reproduce exactly. Therefore each target
is classified `stable_under_predeclared_a2_grid`.

In this metric, a ratio below 1 means the aligned ESMC embedding delta is lower
at mapped interface residues than in the non-interface background. The result
is therefore a robust technical interface-depletion pattern, not evidence by
itself for stronger binding, preserved binding, functional TP53/MDM2 change,
or a longevity mechanism.

## Remaining limitations and exact next action

A2 does not compare the elephant row against a robustness-qualified aggregate
of the short-lived controls. A3 leave-one-control-out and residue-block
jackknife remain unrun. NEGATOME metric compatibility remains unresolved, and
the panel still contains only one long-lived lineage.

The exact allowed next action after this result is merged is:

`run_leave_one_control_out_and_residue_block_jackknife`

Only a later, separate A4 disposition may decide whether the accumulated Gate
8 input is directionally usable. Gate 8 is not promoted here. Gate 9 planning
and all structural calls remain forbidden.
