# Rat MDM2 canonical-accession review result

The comparison table is
`data/input/tp53_mdm2_rat_mdm2_accession_review_results.csv`.

Raw amino-acid sequences are not committed. The table records lengths,
SHA-256 digests, exact-match and subsequence relationships, source statuses,
and candidate dispositions from an external public primary-source review
performed on 2026-07-17.

| Accession | Source status | Length | Disposition |
|---|---|---:|---|
| `NP_001426446.1` | validated RefSeq | 434 | evidence anchor, not accepted as canonical project accession or isoform |
| `A0A0G2JVC1` | active unreviewed TrEMBL | 483 | non-exact match containing the RefSeq as an exact subsequence |
| `A6IGT1` | inactive | 0 | `excluded_inactive_accession` |
| `D3ZVH5` | active unreviewed TrEMBL | 458 | distinct non-exact sequence |

No active UniProt candidate exactly matches the validated RefSeq evidence
anchor. The decision is:

- `review_decision=defer_rat_pending_unambiguous_canonical_sequence_source`
- `selection_outcome=deferred_pending_source`
- `blocker_code=no_unambiguous_canonical_rat_mdm2_sequence`
- `strict_panel_row_allowed=false`

Mouse remains the only ready short-lived control. No contrast, Biohub/ESMC
call, embedding generation, runtime artifact commit, Gate 8/9 opening, or
biological claim is introduced.
