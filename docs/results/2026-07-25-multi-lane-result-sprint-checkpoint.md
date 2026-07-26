# Multi-lane result sprint checkpoint

- **Analysis root label:** `analysis_20260725`
- **Checkpoint created:** `2026-07-26T12:33:36+04:00`
- **Repository commit:** `50f0eca060ec0f6e20bb9d488438834ba146d789`
- **Branch:** `record-multi-lane-result-sprint-checkpoint`

## Purpose

This checkpoint records scientific outcomes before opening the next elephant TP53-retrogene stage. It is a results and provenance checkpoint, not a claim that the tested mechanisms are validated longevity interventions.

## Main result

Across the completed multi-lane sprint, no direct regulatory-site change repeated across two or more tested long-lived lineages. The strongest positive computational result remains the HAS2 reciprocal multi-site rescue. TSC1 M771V remains a moderate two-lineage regional candidate. Three direct regulatory changes are lineage-specific: NMR ULK1 S467G, Myotis ACACB S222G and Myotis PARP1 K521R.

## Lane scorecard

| Lane | Mechanism | Result class | Decision |
|---|---|---|---|
| tp53_mdm2_elephant \| MDM2 mapped-interface enrichment \| negative_for_longevity_contrast \| Do not promote MDM2 interface enrichment as a longevity adaptation. |
| sirt6_dna_repair \| SIRT6 interface embedding contrast \| confounded_negative \| Do not expand the embedding-only SIRT6 contrast without stronger independent controls. |
| igf_rheb_mtor \| RHEB-MTOR interface contrast \| closed_shared_negative \| Lane closed. |
| ampk_pilot \| AMPK interface embedding contrast \| closed_shared_negative \| Stop interface-level AMPK expansion. |
| has2_cd44_nmr \| HAS2 functional-axis sequence rescue \| positive_computational_candidate \| Retain as the strongest positive computational lane. |
| igf_rheb_mtor \| IGF1-IGF1R direct interface \| closed_shared_negative \| Direct-interface lane closed. |
| igf_rheb_mtor \| TSC2-RHEB catalytic switch \| closed_conserved_core \| Do not promote the nonlocal variant without additional mechanism. |
| igf_rheb_mtor \| TSC1-TSC2 assembly interface \| moderate_two_lineage_candidate \| Retain as a regional two-lineage interface candidate. |
| igf_rheb_mtor \| AKT1-to-FOXO3 phosphosite motifs \| closed_shared_negative \| Motif lane closed. |
| igf_rheb_mtor \| AKT-to-TSC2 phosphosite motifs \| closed_shared_negative \| Motif lane closed. |
| sirt6_dna_repair \| Stress SIRT6-to-PARP1 regulation \| closed_no_repeated_signal_with_lineage_specific_candidate \| No shared longevity signal; preserve Myotis K521R as a species-specific candidate. |
| ampk_pilot \| AMPK/mTOR-to-ULK1 phosphoregulation \| lineage_specific_direct_site_loss_with_missing_lineage \| Preserve as an NMR-specific candidate, not a repeated longevity signal. |
| ampk_pilot \| AMPK-to-RPTOR energy checkpoint \| closed_shared_negative \| Lane closed. |
| ampk_pilot \| AMPK-to-ACC1/ACC2 metabolic checkpoint \| closed_no_repeated_signal_with_lineage_specific_candidate \| No shared longevity signal; preserve the bat-specific ACC2 candidate. |

The complete machine-readable table is stored in `docs/results/2026-07-25-multi-lane-result-sprint/lane_scorecard.csv`.

## Candidate shortlist

| Priority | Candidate | Evidence class | Scope | Next validation |
|---:|---|---|---|---|
| 1 \| HAS2 multi-site reciprocal rescue \| positive_computational_multi_site \| human/NMR reciprocal backgrounds \| Multi-site HAS2 wet-lab panel with single-site, cluster and reciprocal controls. |
| 2 \| TSC1 M771V regional interface candidate \| moderate_two_lineage_interface \| 2 long-lived lineages \| Human TSC1 WT, M771V, M806V, M845V and V772M; measure TSC stability, assembly, RHEB-GTP, p-S6K/4E-BP1 and autophagic flux. |
| 3 \| ULK1 S467G \| single_lineage_direct_phosphoacceptor_loss \| NMR only; Myotis unresolved \| Direct S467G phosphosite and autophagy assay. |
| 4 \| ACACB S222G \| single_lineage_direct_phosphoacceptor_loss \| Myotis only \| ACC2 phosphorylation, catalytic activity and malonyl-CoA assay. |
| 5 \| PARP1 K521R \| single_lineage_direct_regulatory_lysine_loss \| Myotis only \| PARP1 recruitment, activity and site-specific regulatory-modification assay. |

## Decisions

1. **Preserve HAS2 as the strongest positive computational lane.** The reciprocal local rescue is substantial and directionally consistent, but remains an embedding-level observation.
2. **Preserve TSC1 M771V as a moderate regional two-lineage candidate.** It is not uniquely position-specific after nearby interface controls.
3. **Stop broad AMPK regulatory-motif scanning.** The tested architecture is predominantly conserved, with different lineage-specific exceptions rather than a shared rewiring pattern.
4. **Do not expand conserved-site questions with ESMC or cofolding.** Site presence or loss is already a direct sequence observation.
5. **Open elephant TP53 retrogenes as a separate stage.** Claims must be copy-specific and distinguish BOX-I disruption, expression evidence and functional evidence.

## Claim boundaries

- Sequence substitutions do not establish phosphorylation, binding, enzyme activity, pathway output or lifespan effects.
- Embedding rescue is model-level evidence of local sequence-context compatibility, not direct biochemical rescue.
- A change seen in one long-lived lineage is a species-specific candidate, not a general longevity-associated adaptation.
- Missing sequence or annotation is recorded as unresolved rather than interpreted as biological absence.

## Provenance

- `docs/results/2026-07-25-multi-lane-result-sprint/result_manifest.json` records repository state and hashes.
- `docs/results/2026-07-25-multi-lane-result-sprint/source_artifact_inventory.csv` inventories CSV and JSON outputs under the external result root and records which summary-level artifacts were copied.
- Local absolute paths are replaced with `<external-result-root>` or `<repository-root>` in committed copies.
- FASTA files, embeddings, structures, caches, scripts and large intermediate files are intentionally excluded.

## Validation scope

- All committed JSON files parse successfully.
- All committed CSV files have consistent row width.
- Only the checkpoint document and curated artifacts under `docs/results/2026-07-25-multi-lane-result-sprint` are included.
- No Biohub, Boltz or new embedding execution is part of this PR.

## Repository placement

The pipeline-wide `data/output/*` path is intentionally ignored as regenerable output. This PR therefore commits only curated scientific checkpoint artifacts under `docs/results/`. Empty candidate CSV files encountered in the generated source checkpoint were accepted as valid zero-row negative results rather than treated as corruption.
