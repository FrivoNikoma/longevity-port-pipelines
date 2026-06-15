# SIRT6 v2 core3-expanded PCA cluster-map interpretation

## Purpose

This note explains how to interpret the PCA cluster map for the SIRT6 v2 core3-expanded divergence-profile clustering results.

It complements:

- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.csv`

- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.png`

- `data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.md`

- `scripts/plot_core3_expanded_divergence_profile_clusters_2d.py`

The goal is to document what the PCA map supports, what it does not support, and how it should be used in biological discussion.

## Short interpretation

The PCA map supports the large-scale structure of the current cluster interpretation.

It supports:

1. `1nfi` and `8g57` as related long-lived divergence candidates;

2. `4xhu` as a separate shared constrained-interface anchor;

3. `8bhv` R/j as a singleton outlier or artifact-risk benchmark;

4. cluster 0 as a broad mixed regime requiring case-level interpretation.

The PCA map does not prove a biological mechanism by itself.

It is a supporting visualization of the 11-dimensional divergence-profile feature space used for clustering.

## What is being projected

The PCA map projects the curated 11-dimensional divergence-profile feature space into two visual coordinates.

The 11 features are:

1. `log2_enrichment_ratio`

2. `effect_size_cohens_d_computed`

3. `delta_mean_difference`

4. `median_difference`

5. `q75_difference`

6. `q90_difference`

7. `top10_mean_difference`

8. `max_difference`

9. `fraction_interface_above_global_q90`

10. `interface_fraction_above_global_q90`

11. `interface_fraction`

Each point in the PCA plot represents one `complex x chain x target_species` divergence-profile object.

The plot should therefore be read as:

```text

11-dimensional divergence-profile feature vector

-> 2-dimensional PCA projection

```

It should not be read as:

```text

PC1 = longevity

PC2 = binding affinity

```

PC1 and PC2 are visualization axes, not direct biological mechanisms.

## What the PCA supports

### 1. `1nfi` and `8g57` group together

The strongest support from the PCA map is that the main long-lived divergence candidates occupy the same cluster regime.

These are:

- `1nfi` receptor in naked mole-rat;

- `1nfi` receptor in Myotis;

- `8g57` ligand in naked mole-rat;

- `8g57` ligand in Myotis.

All four are assigned to cluster 1.

This supports the interpretation that `1nfi` and `8g57` have related divergence-profile behavior.

Biologically, this is useful because the two cases come from different contexts:

- `1nfi`: NF-kappaB / IkappaBalpha regulatory-interface context;

- `8g57`: SIRT6-nucleosome context.

The PCA map does not say that these mechanisms are the same. It says that their interface-divergence profiles are similar enough to occupy the same clustering regime.

### 2. `4xhu` separates as a constrained-interface anchor

The three `4xhu` receptor cases form cluster 2:

- mouse;

- naked mole-rat;

- Myotis.

This supports the interpretation of `4xhu` as a shared constrained-interface anchor rather than as a long-lived divergence hit.

This is important because it shows that the pipeline is not only finding divergent candidates. It can also distinguish a conserved or constrained interface regime.

### 3. `8bhv` R/j behaves as a singleton outlier

The `8bhv` ligand R/j mouse case appears as cluster 3, a singleton outlier.

This supports the interpretation of this case as an outlier or artifact-risk benchmark.

It should be used to check:

- chain-pair handling;

- residue-numbering assumptions;

- structure-remapping behavior;

- artifact risk;

- sensitivity to unusual interface profiles.

### 4. Cluster 0 is a mixed regime

Cluster 0 contains several types of cases, including:

- `8f86` receptor Myotis;

- `7s68` receptor naked mole-rat;

- one `8bhv` ligand mouse case;

- other background, mixed, constrained, or cautious cases.

This means cluster 0 should not be treated as a single clean biological class.

For `8f86` and `7s68`, the PCA map is not the main evidence. Their interpretation should depend more heavily on:

- residue-level candidate patches;

- structure-remapping QC;

- viewer-ready selections;

- manual 3D review.

## Why cluster 0 and cluster 1 are not perfectly separated in 2D

The blue and orange regions in the PCA map are not perfectly separated. This is expected.

The clustering was performed in the original 11-dimensional feature space, while the plot shows only a two-dimensional projection.

PCA keeps the first two principal components, which capture large directions of variance. However, PCA does not try to maximize visual separation between KMeans clusters.

Therefore, two groups can be meaningfully separated in 11 dimensions but partially overlap in a 2D PCA projection.

A useful analogy is a 3D object casting a shadow. The shadow can preserve some structure, but it cannot show every dimension of the object.

In the same way, the PCA map is a two-dimensional shadow of the 11-dimensional divergence-profile space.

Therefore:

```text

partial overlap in PCA space

does not imply

invalid clustering

```

It only means that the first two principal components do not contain all information used by KMeans.

## What the PCA does not support

The PCA map should not be used to claim that:

1. PC1 or PC2 is a longevity axis;

2. cluster 1 is a validated biological mechanism;

3. all cluster 1 cases have the same molecular mechanism;

4. cluster 0 is unimportant;

5. `8f86` lacks biological interest because it is in cluster 0;

6. interface divergence necessarily changes binding affinity;

7. structure-proximal residues are automatically causal.

These would be over-interpretations.

The PCA map is a visual support layer, not a validation layer.

## Recommended presentation caption

A concise caption for collaborators:

```text

PCA projection of the 11-feature divergence-profile space used for clustering.

The top long-lived divergence candidates 1nfi and 8g57 co-localize in cluster 1,

the shared constrained-interface anchor 4xhu separates into cluster 2, and the

8bhv R/j mouse case appears as a singleton outlier. PCA is used for visualization

only; biological interpretation depends on residue-level and structure-remapping review.

```

## Working conclusion

The PCA map supports the major structure of the current interpretation.

It supports:

- `1nfi` and `8g57` as related long-lived divergence candidates;

- `4xhu` as a separate constrained-interface anchor;

- `8bhv` R/j as a singleton outlier;

- cluster 0 as a broad mixed regime requiring case-level interpretation.

It does not prove a biological mechanism.

The PCA map should be used as a supporting figure that helps communicate the cluster regimes. The primary biological interpretation should still rely on residue-level analysis, structure-remapping QC, viewer-ready selections, and manual 3D review.
