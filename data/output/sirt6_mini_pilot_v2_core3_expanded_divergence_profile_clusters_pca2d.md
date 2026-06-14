# SIRT6 v2 core3-expanded divergence-profile clusters PCA map

## Purpose

This file summarizes a two-dimensional PCA projection of the SIRT6 v2 core3-expanded divergence-profile clusters.

The PCA coordinates are taken from the existing clustering output `pca1` and `pca2`, rather than recomputed here.

The clustering script uses the curated 11-dimensional divergence-profile feature set listed below, scales those features, and projects them into two principal components for visualization.

## Inputs

- Cluster output: `data\output\sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters.csv`
- Manual-review structure QC: `data\output\sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_qc.csv`

## Outputs

- PCA coordinates: `data\output\sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.csv`
- PCA figure: `data\output\sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.png`
- Summary: `data\output\sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.md`

## Original feature-space dimension

- Original divergence-profile feature-space dimension: 11
- PCA projection dimension: 2

## Feature columns used by the clustering PCA

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

## Cluster counts

- Cluster `0`: 34 rows
- Cluster `1`: 23 rows
- Cluster `2`: 3 rows
- Cluster `3`: 1 rows

## Manual-review cases shown on the PCA map

- `1nfi receptor Myotis` (cluster `1`, PC1=2.549, PC2=0.674, complex `1nfi__A1_Q04206--1nfi__F1_P25963`)
- `1nfi receptor NMR` (cluster `1`, PC1=2.731, PC2=0.802, complex `1nfi__A1_Q04206--1nfi__F1_P25963`)
- `4xhu receptor mouse` (cluster `2`, PC1=-6.496, PC2=1.134, complex `4xhu__A1_P09874--4xhu__B1_Q9UNS1`)
- `4xhu receptor Myotis` (cluster `2`, PC1=-6.481, PC2=1.420, complex `4xhu__A1_P09874--4xhu__B1_Q9UNS1`)
- `4xhu receptor NMR` (cluster `2`, PC1=-6.606, PC2=1.172, complex `4xhu__A1_P09874--4xhu__B1_Q9UNS1`)
- `7s68 receptor NMR` (cluster `0`, PC1=1.520, PC2=-1.735, complex `7s68__D1_P09874--7s68__C1_P09874`)
- `8bhv ligand Q/h mouse` (cluster `0`, PC1=0.524, PC2=-1.780, complex `8bhv__N1_P12956--8bhv__I1_Q9H9Q4`)
- `8bhv ligand R/j mouse` (cluster `3`, PC1=9.324, PC2=-2.997, complex `8bhv__P1_P13010--8bhv__J1_Q9H9Q4`)
- `8f86 receptor Myotis` (cluster `0`, PC1=-2.037, PC2=-1.789, complex `8f86__K1_Q8N6T7--8f86__D1_P02281`)
- `8g57 ligand Myotis` (cluster `1`, PC1=2.638, PC2=1.777, complex `8g57__A1_Q8N6T7--8g57__H1_P04908`)
- `8g57 ligand NMR` (cluster `1`, PC1=3.275, PC2=1.581, complex `8g57__A1_Q8N6T7--8g57__H1_P04908`)

## Interpretation note

This PCA map should be interpreted as a low-dimensional visualization of the 11-dimensional divergence-profile feature space used for clustering. The PCA axes are not biological mechanisms. Biological interpretation still depends on the residue-level packet, structure-remapping QC, viewer-ready selections, and manual 3D review.
