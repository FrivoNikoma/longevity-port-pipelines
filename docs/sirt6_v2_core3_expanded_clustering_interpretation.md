# SIRT6 v2 core3-expanded divergence-profile clustering interpretation

## Purpose

This note summarizes the exploratory divergence-profile clustering results for the SIRT6 v2 core3-expanded run.

The goal is to interpret residue-level divergence-profile features after the pipeline has produced:

1. core3-expanded complex selection;
2. ortholog coverage for mouse, naked mole rat, and *Myotis lucifugus*;
3. saved ESMC embeddings;
4. mapped interface-vs-background enrichment;
5. signal summary;
6. longevity contrast;
7. residue-level mapped deltas;
8. divergence-profile feature vectors;
9. annotation-blind clustering of numeric profile features.

The clustering analysis is exploratory. It is intended to identify interpretable regimes of interface behavior, not to establish validated biological classes.

## Inputs

The clustering was run on:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_features.csv`

The clustering script produced:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_cluster_centroids.csv`
- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters.md`

The feature table contained 66 feature rows, of which 61 were clustering-ready.

## Clustering method

Clustering used only numeric divergence-profile features derived from residue-level delta distributions. The features included:

- `log2_enrichment_ratio`
- `effect_size_cohens_d_computed`
- `delta_mean_difference`
- `median_difference`
- `q75_difference`
- `q90_difference`
- `top10_mean_difference`
- `max_difference`
- `fraction_interface_above_global_q90`
- `interface_fraction_above_global_q90`
- `interface_fraction`

The categorical fields `signal_class` and `contrast_class` were not used as clustering coordinates. They were retained only as post hoc annotations for biological interpretation.

KMeans clustering was run with automatic selection of `k` by silhouette score. Standard feature scaling was used.

## Summary of clustering result

The best KMeans solution selected:

- `k = 4`
- silhouette approximately `0.388`

The cluster sizes were:

- cluster 0: `n = 34`
- cluster 1: `n = 23`
- cluster 2: `n = 3`
- cluster 3: `n = 1`

The resulting structure should be interpreted as a set of divergence-profile regimes rather than as four equally robust biological classes.

## Cluster 0: mild constrained / mixed background mode

Cluster 0 is the largest cluster.

Centroid-level summary:

- `n = 34`
- mean log2 enrichment approximately `-0.17`
- mean effect size approximately `-0.20`
- mean `fraction_interface_above_global_q90` approximately `0.05`

This cluster is enriched for interface-constrained and weak/mixed signals. Its profile suggests that, for many entries in this group, interface residues are not preferentially concentrated in the high-divergence tail relative to non-interface residues.

Biological interpretation:

Cluster 0 appears to represent a mild constrained or mixed background regime.

This regime is not biologically uninteresting. Some long-lived-specific constraint cases fall into this cluster, for example SIRT6/histone-related receptor cases with relatively low interface tail enrichment.

## Cluster 1: divergent / high-tail-enriched mode

Cluster 1 is the main divergent-profile cluster.

Centroid-level summary:

- `n = 23`
- mean log2 enrichment approximately `+0.20`
- mean effect size approximately `+0.26`
- mean `fraction_interface_above_global_q90` approximately `0.42`

This cluster contains many `interface_divergent` and `interface_divergent_not_significant` rows. It also contains several post hoc longevity-contrast annotations such as long-lived-enhanced or long-lived-specific interface divergence.

Biological interpretation:

Cluster 1 appears to represent an interface-divergent or high-tail-enriched mode.

This is the most relevant cluster for the Longevity Port hypothesis. It suggests that some long-lived species orthologs show divergence profiles where interface residues are preferentially shifted toward higher residue-level delta values.

Examples include:

- 8g57 ligand in naked mole rat and *Myotis lucifugus*
- 8g57 receptor in mouse, naked mole rat, and *Myotis lucifugus*
- 1nfi receptor in naked mole rat and *Myotis lucifugus*

These should be treated as candidate cases for manual biological review, not as validated causal findings.

## Cluster 2: extreme shared interface constraint

Cluster 2 is a compact three-row cluster.

It contains:

- 4xhu receptor mouse
- 4xhu receptor naked mole rat
- 4xhu receptor *Myotis lucifugus*

Centroid-level summary:

- `n = 3`
- mean log2 enrichment approximately `-1.31`
- mean effect size approximately `-0.95`
- mean `fraction_interface_above_global_q90` approximately `0.03`

Biological interpretation:

Cluster 2 appears to represent extreme shared interface constraint.

This is not a longevity-specific signal. Instead, it is a useful anchor mode: a case where the same interface appears strongly protected across all three species. This provides a contrast to the more divergent or long-lived-specific cases.

## Cluster 3: singleton extreme divergent outlier

Cluster 3 contains a single row:

- 8bhv ligand mouse

Its profile is extreme:

- log2 enrichment approximately `+1.22`
- effect size approximately `+3.78`
- `interface_fraction_above_global_q90 = 1.0`

Biological interpretation:

Cluster 3 is not a robust cluster; it is a singleton divergent outlier.

This case should be inspected manually. It may represent a real extreme interface-divergence pattern, but it could also reflect chain-specific, mapping-specific, or structural-context effects.

## Overall interpretation

The core3-expanded run produced an interpretable divergence-profile feature space.

The main regimes are:

1. a mild constrained / mixed background mode;
2. a divergent / high-tail-enriched mode;
3. an extreme shared interface-constraint mode;
4. a singleton extreme divergent outlier.

The most important conceptual result is that the pipeline moves beyond individual p-values or enrichment ratios. It produces a profile space in which interface behavior can be grouped into interpretable regimes.

For the Longevity Port hypothesis, the most interesting region is cluster 1, because it contains several long-lived-specific or long-lived-enhanced interface divergence cases. Cluster 2 is also important as an internal negative/anchor regime: strong shared constraint across all species.

## Limitations

These results are exploratory.

Important limitations:

- the sample size is small;
- cluster 3 is a singleton and should not be interpreted as a stable biological class;
- cluster labels depend on the selected numeric features and scaling method;
- KMeans imposes a partition even when biological regimes may be continuous;
- signal and contrast labels were used only for post hoc interpretation;
- candidate cases require manual inspection of structure mapping, residue-level deltas, and biological context.

## Working conclusion

The SIRT6 v2 core3-expanded analysis supports the usefulness of the pipeline as a hypothesis-generation tool. It identifies interpretable residue-level interface-divergence regimes and highlights candidate complexes/chains where long-lived orthologs may show distinctive interface behavior relative to the mouse baseline.

The next step is manual biological review of high-priority cases from the divergent and long-lived-specific/enhanced regimes, especially:

- 8g57 ligand naked_mole_rat / *Myotis lucifugus*
- 1nfi receptor naked_mole_rat / *Myotis lucifugus*
- 7s68 receptor naked_mole_rat
- 8f86 receptor *Myotis lucifugus*

These candidates should be treated as preliminary leads for further structural and biological validation.
