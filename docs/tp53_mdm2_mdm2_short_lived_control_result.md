# TP53/MDM2 MDM2-side short-lived control result

## Selected control

The selected project-policy short-lived control species is `mouse`
(`Mus musculus`, taxid `10090`).

The selected MDM2 accession is reviewed UniProtKB Swiss-Prot `P23804`.
The reviewed entry records Mdm2 for mouse, a complete canonical sequence
of 489 amino acids, and evidence at protein level.

## Decision-bearing outcome

- `review_decision=accept_reviewed_swissprot_for_gate7_technical_planning`
- `selection_outcome=ready_for_gate7_strict_panel_planning`
- `coverage_preflight_status_after_selection=coverage_preflight_ready`
- `control_readiness_status_after_selection=controls_ready`

The control row is attached to the existing MDM2 candidate key
`tp53_mdm2_elephant_seed_mdm2_chain`, structure/chain `1ycr:A`.

## Gate 7 recomputation

The MDM2 chain now has one ready long-lived species (`elephant`) and one
ready short-lived species (`mouse`), so its recomputed result is:

- `strict_panel_status=strict_panel_ready`
- `contrast_dry_run_allowed=true`

This is technical Gate 7 readiness for the MDM2 chain only.

Aggregate TP53/MDM2 Gate 7 entry remains false because the TP53 chain is
still `deferred_pending_source`. Gate 8 and Gate 9 remain closed.

## Embedding boundary

No exact local P23804 embedding is asserted. Embedding presence is not
evaluated and is not required for this Gate 7 source-selection decision.
No embedding is generated or committed.

## Other boundaries

No sequence fetch, Biohub/ESMC call, `.npy` or `data/output` commit,
Boltz/AF3/Chai call, Gate 8/9 promotion, biological approval, or
biological claim is introduced.
