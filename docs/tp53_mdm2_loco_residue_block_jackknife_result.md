# Scoped MDM2 A3 control-identity and residue-block robustness result

## Status

This is a committed technical A3 robustness result for the narrow MDM2 lane.
It separates robustness of the shared mapped-interface depletion pattern from
robustness of the elephant-versus-short-lived contrast. It does not perform
Gate 8 disposition, does not promote Gate 8 or Gate 9, and makes no biological
claim.

## Bound artifacts

| Artifact | Rows | Canonical-text SHA-256 |
| --- | ---: | --- |
| `data/input/tp53_mdm2_mdm2_residue_block_jackknife_species_results.csv` | 15 | `ac27176b72e691e50ca3daf55ec69ee0d386c01242e6a5ad7c50f7326e9bd90b` |
| `data/input/tp53_mdm2_mdm2_contrast_robustness_results.csv` | 8 | `2b83c153f729f19f82cd657af30fb4c9d9f29bddeaa79e4c78e37bcae96b6762` |
| `data/input/tp53_mdm2_mdm2_loco_residue_block_jackknife_summary.csv` | 1 | `90158dd18a67dd509df82f25bd30137979b879809a77fbbc702b8d09b576bcb3` |

Validation normalizes UTF-8 BOM handling and CRLF/CR/LF line endings before
hashing. The numerical CSV content is unchanged by that portability policy.
Every species row is bound to the committed interface mapping, A1 result, and
A2 summary through their canonical-text SHA-256 values.

## Predeclared robustness calculations

The 47 committed `Q00987` zero-based interface positions are sorted and split
deterministically into five ordered blocks of sizes `10/10/9/9/9`. For each
block and each of elephant `G3SX30`, mouse `P23804`, and hamster `A0ABM2YB85`,
the selected residues are removed entirely before the metric is recalculated.
They are not reassigned to the non-interface background. This produces 15
species-level jackknife rows.

The contrast table contains eight scenarios:

- one full elephant-versus-mean-short-lived baseline;
- `leave_mouse_out` and `leave_hamster_out`;
- five residue-block jackknife contrasts.

All scenarios reuse the generic contrast classification and retain the
single-long-lived-lineage limitation.

## Species-level robustness

| Target | Five-block enrichment-ratio range | Cohen's d range | Lower-tail shuffled pass |
| --- | ---: | ---: | ---: |
| Elephant `G3SX30` | `0.50705911319844221`–`0.65409395413968363` | `-0.68459862477234079`–`-0.47780497394425647` | 5/5 |
| Mouse `P23804` | `0.46433412299785343`–`0.56926627985638945` | `-0.86010657206217878`–`-0.68946459056189624` | 5/5 |
| Hamster `A0ABM2YB85` | `0.50198730507439393`–`0.66431997891320882` | `-0.81535611557823784`–`-0.54631644137941826` | 5/5 |

All 15 ratios remain below 1, all effect sizes remain negative, and all 15
metric-compatible shuffled lower-tail checks pass at 0.05. The committed
summary therefore records both `shared_interface_depletion_robustness=robust`
and `block_jackknife_robustness=robust`.

In this metric, a ratio below 1 means that the aligned residue-level ESMC L2
delta is lower at the retained mapped interface than in the non-interface
background. This is a shared technical interface-constraint pattern; it is not
by itself evidence for binding strength, preserved binding, a functional
TP53/MDM2 effect, or a longevity mechanism.

## Contrast robustness

| Scenario | Enrichment delta | Sign | Matches full sign | Generic class |
| --- | ---: | --- | --- | --- |
| `full_short_lived_baseline` | `0.036270818839664654` | positive | true | `shared_interface_constraint` |
| `leave_mouse_out` | `-0.0055259455763676524` | negative | false | `shared_interface_constraint` |
| `leave_hamster_out` | `0.07806758325569696` | positive | true | `shared_interface_constraint` |
| `block_1_short_lived_baseline` | `0.089403321963416382` | positive | true | `shared_interface_constraint` |
| `block_2_short_lived_baseline` | `0.056283161254250702` | positive | true | `shared_interface_constraint` |
| `block_3_short_lived_baseline` | `0.020850990991445051` | positive | true | `shared_interface_constraint` |
| `block_4_short_lived_baseline` | `-0.059953233723955557` | negative | false | `shared_interface_constraint` |
| `block_5_short_lived_baseline` | `0.07669471806943895` | positive | true | `shared_interface_constraint` |

The full contrast is small and positive. Its sign reverses once when control
identity is varied (`leave_mouse_out`) and once across the residue blocks
(`block_4_short_lived_baseline`). Thus the result records
`control_identity_robustness=control_identity_sensitive` and
`block_contrast_sign_robustness=block_sensitive`, while the generic class
remains `shared_interface_constraint` in every scenario.

The exact combined status is:

`shared_interface_constraint_robust_but_longevity_contrast_not_robust`

## Boundaries and exact next action

The shared interface-depletion direction is robust under A1, A2, and the A3
block jackknife. The available data do not support a robust
long-lived-versus-short-lived interpretation because the contrast depends on
both control identity and one residue block. Only one long-lived lineage is
present, and NEGATOME metric compatibility remains separately unresolved.

The exact allowed next action is:

`add_independent_short_lived_controls_or_limit_to_shared_interface_constraint`

This result creates no new embedding, calls no BioHub/ESMC or structural
model, commits no `data/output` artifact, does not perform Gate 8 disposition,
does not promote Gate 8 or Gate 9, and makes no biological claim.
