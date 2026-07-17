# TP53/MDM2 MDM2-side short-lived control evaluation

## Mouse

Mouse `P23804` remains the only ready short-lived MDM2 control:

- `selection_outcome=ready_for_gate7_strict_panel_planning`
- `blocker_code=none`
- `strict_panel_row_allowed=true`

## Rat

The committed comparison table
`data/input/tp53_mdm2_rat_mdm2_accession_review_results.csv` records:

- `A6IGT1` as `excluded_inactive_accession`;
- active TrEMBL `A0A0G2JVC1` as 49 amino acids longer than
  `NP_001426446.1`, containing it as an exact subsequence, but not an exact
  accession-level match;
- active TrEMBL `D3ZVH5` as a distinct 458-amino-acid non-match;
- validated RefSeq `NP_001426446.1` as the evidence anchor, not an accepted
  canonical project accession or isoform.

The decision-bearing result is:

- `review_decision=defer_rat_pending_unambiguous_canonical_sequence_source`
- `selection_outcome=deferred_pending_source`
- `blocker_code=no_unambiguous_canonical_rat_mdm2_sequence`
- `strict_panel_row_allowed=false`

This is a completed review decision for the current source set, not a claim
that rat lacks an MDM2 ortholog.

## Hamster

Hamster `Q60524` remains `deferred_pending_source` because the reviewed
sequence is marked as a fragment.

## Panel effect

Only mouse enters the strict panel. MDM2 therefore remains:

- `n_strict_long_lived_ready=1`
- `n_strict_short_lived_ready=1`
- `strict_long_lived_species=elephant`
- `strict_short_lived_species=mouse`
- `strict_panel_status=strict_panel_ready`

No contrast is run. TP53 remains `deferred_pending_source`; aggregate Gate 7
remains false, and Gate 8 and Gate 9 remain closed.

## Boundaries

No raw sequence is committed. No sequence fetch occurs inside repository
runtime. No contrast, Biohub/ESMC call, embedding generation, `.npy` or
`data/output` commit, Boltz/AF3/Chai call, gate promotion, biological
approval, or biological claim is introduced.
