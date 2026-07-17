# TP53/MDM2 MDM2-side short-lived control evaluation

## Mouse

Mouse `P23804` remains ready:

- `selection_outcome=ready_for_gate7_strict_panel_planning`
- `blocker_code=none`
- `strict_panel_row_allowed=true`

## Rat

The committed comparison table
`data/input/tp53_mdm2_rat_mdm2_accession_review_results.csv`
records a terminal source deferral:

- `review_decision=defer_rat_pending_unambiguous_canonical_sequence_source`
- `selection_outcome=deferred_pending_source`
- `blocker_code=no_unambiguous_canonical_rat_mdm2_sequence`
- `strict_panel_row_allowed=false`

Validated RefSeq `NP_001426446.1` remains an evidence anchor and is not
accepted as a canonical project accession or isoform.

## Hamster

The committed bounded review table
`data/input/tp53_mdm2_hamster_mdm2_complete_sequence_review_results.csv`
resolves the complete sequence source.

One complete 510-amino-acid sequence group is represented by:

- primary project accession `A0ABM2YB85`;
- corroborating model RefSeq `XP_040610761.1`;
- main hamster `Mdm2` locus `GeneID:101833011`;
- sequence SHA-256
  `77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5`.

The two accessions have the same sequence. No competing complete sequence for
the main `Mdm2` locus was identified in the bounded source set.

Reviewed Swiss-Prot `Q60524` and GenBank `AAC52425.1` remain a distinct
466-amino-acid legacy fragment sequence group. The accepted 510-amino-acid
sequence is not an exact match to the fragment and does not contain it as an
exact subsequence. The fragment is retained as evidence provenance; it is not
reinterpreted as a complete protein.

The decision-bearing hamster result is:

- `review_decision=accept_complete_hamster_mdm2_uniprot_refseq_sequence_group_for_gate7_technical_planning`
- `selection_outcome=ready_for_gate7_strict_panel_planning`
- `blocker_code=none`
- `strict_panel_row_allowed=true`

This is project accession acceptance for technical planning only. It is not a
claim that `A0ABM2YB85` is a validated canonical biological isoform.

## Panel effect

Mouse and hamster enter the strict panel. MDM2 becomes:

- `n_strict_long_lived_ready=1`
- `n_strict_short_lived_ready=2`
- `strict_long_lived_species=elephant`
- `strict_short_lived_species=hamster,mouse`
- `strict_panel_status=strict_panel_ready`
- `contrast_dry_run_allowed=true`
- `controlled_claim_allowed=false`

The earlier single-species short-lived baseline limitation is removed for MDM2
technical planning. This still does not establish a general
long-lived-versus-short-lived biological effect.

No contrast is run. TP53 remains `deferred_pending_source`; aggregate Gate 7
remains false, and Gate 8 and Gate 9 remain closed.

## Boundaries

No raw sequence is committed. No sequence fetch occurs inside repository
runtime. No contrast, Biohub/ESMC call, embedding generation, `.npy` or
`data/output` commit, Boltz/AF3/Chai call, gate promotion, biological approval,
canonical-isoform claim, or biological claim is introduced.
