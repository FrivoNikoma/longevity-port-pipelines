# Hamster MDM2 complete sequence source review

## Scope

This checkpoint records a bounded read-only source inspection for
`Mesocricetus auratus` MDM2, taxid `10036`.

The source set includes UniProtKB, NCBI Gene and Protein/RefSeq, accession
history, legacy GenBank evidence, and an Ensembl translation identifier. Raw
amino-acid sequences are not committed.

## Main locus

NCBI Gene identifies `GeneID:101833011` as the main hamster `Mdm2` locus.
Other discovered records resolve to retired, `Mdm2-like`, MDM2-binding-protein,
`Mdm4`, SWI/SNF, or unrelated loci and are excluded explicitly in the review
table.

## Accepted complete sequence group

One complete identity-valid sequence group is represented by:

- UniProtKB TrEMBL `A0ABM2YB85`;
- NCBI model RefSeq `XP_040610761.1`;
- `GeneID:101833011`;
- length `510`;
- sequence SHA-256 `77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5`.

The two accessions have identical sequences. `A0ABM2YB85` is selected as the
project accession and `XP_040610761.1` is retained as a corroborating RefSeq
accession.

## Legacy reviewed fragment

Reviewed Swiss-Prot `Q60524` and GenBank `AAC52425.1` share the 466-amino-acid
sequence SHA-256 `f5e0b35c24cf9ce7c11d9290214930b3787da380112024a37b9ce41909ba5d35`.

`Q60524` remains explicitly marked as a fragment. The selected 510-amino-acid
sequence is neither an exact match to `Q60524` nor a sequence containing the
complete `Q60524` fragment as an exact subsequence. The old fragment therefore
remains separate evidence provenance and is not reinterpreted as a full
sequence.

## Decision

- `review_decision=accept_complete_hamster_mdm2_uniprot_refseq_sequence_group_for_gate7_technical_planning`
- `selection_outcome=ready_for_gate7_strict_panel_planning`
- `target_protein_accession=A0ABM2YB85`
- `blocker_code=none`
- `strict_panel_row_allowed=true`

This decision accepts a project accession for Gate 7 technical planning. It
does not claim that the genome-derived model is a validated canonical
biological isoform.

## Gate effect

The MDM2 strict panel now contains:

- long-lived: `elephant`;
- short-lived: `hamster,mouse`;
- `n_strict_long_lived_ready=1`;
- `n_strict_short_lived_ready=2`;
- `strict_panel_status=strict_panel_ready`;
- `contrast_dry_run_allowed=true`;
- `controlled_claim_allowed=false`.

No contrast is executed. Aggregate Gate 7 remains closed because the TP53 chain
is still `deferred_pending_source`. Gate 8 and Gate 9 remain closed.

## Boundaries

No raw sequence is committed. No repository-runtime sequence fetch, Biohub or
ESMC call, embedding generation, `.npy` or `data/output` commit, contrast,
Boltz/AF3/Chai call, canonical-biological-isoform claim, gate promotion, or
biological claim is introduced.
