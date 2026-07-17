# TP53/MDM2 MDM2-side short-lived control evaluation

## Policy panel

The project-policy MDM2 short-lived-control panel contains mouse, rat, and
hamster. The committed result table now contains one decision-bearing row for
each species. Absence of an earlier committed row is not treated as absence of
an ortholog.

## Mouse: ready

Reviewed UniProtKB Swiss-Prot `P23804` remains accepted for mouse Gate 7
technical planning:

- `selection_outcome=ready_for_gate7_strict_panel_planning`
- `strict_panel_row_allowed=true`

Mouse remains the only ready short-lived MDM2 control.

## Rat: manual review required

NCBI Gene `314856` records rat `Mdm2` with validated RefSeq protein
`NP_001426446.1`. The maintained RefSeq product links to three UniProtKB
TrEMBL accessions: `A0A0G2JVC1`, `A6IGT1`, and `D3ZVH5`.

This confirms accession-level source evidence but does not provide one
unambiguous project-selected canonical UniProt accession:

- `review_decision=needs_manual_review_choose_canonical_uniprot_accession`
- `selection_outcome=needs_manual_review`
- `strict_panel_row_allowed=false`

The result does not claim that rat lacks an MDM2 ortholog.

## Hamster: deferred pending a complete source

Reviewed UniProtKB Swiss-Prot `Q60524` records hamster MDM2, taxid `10036`,
length 466 amino acids, and evidence at transcript level. UniProt marks the
sequence as `Fragment`.

The committed outcome is:

- `review_decision=defer_reviewed_swissprot_fragment_pending_complete_sequence`
- `selection_outcome=deferred_pending_source`
- `strict_panel_row_allowed=false`

A reviewed entry is not automatically accepted when its sequence is
explicitly incomplete.

## Gate 7 and robustness state

Only rows with `strict_panel_row_allowed=true` are passed into the generic
strict-panel builder. Rat and hamster are excluded from panel counts at this
checkpoint.

The MDM2 chain remains:

- `n_strict_long_lived_ready=1`
- `n_strict_short_lived_ready=1`
- `strict_long_lived_species=elephant`
- `strict_short_lived_species=mouse`
- `strict_panel_status=strict_panel_ready`
- `contrast_dry_run_allowed=true`

The short-lived baseline is still single-species and remains subject to
single-baseline robustness review. TP53 remains `deferred_pending_source`;
aggregate Gate 7 remains false, and Gate 8 and Gate 9 remain closed.

## Boundaries

No sequence fetch, Biohub/ESMC call, embedding generation, `.npy` or
`data/output` commit, Boltz/AF3/Chai call, automatic gate promotion,
biological approval, or biological claim is introduced.
