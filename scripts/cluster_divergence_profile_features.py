from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path

import polars as pl
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import RobustScaler, StandardScaler

DEFAULT_FEATURES = [
    "log2_enrichment_ratio",
    "effect_size_cohens_d_computed",
    "delta_mean_difference",
    "median_difference",
    "q75_difference",
    "q90_difference",
    "top10_mean_difference",
    "max_difference",
    "fraction_interface_above_global_q90",
    "interface_fraction_above_global_q90",
    "interface_fraction",
]

ANNOTATION_COLUMNS = [
    "complex_id",
    "pdb_id",
    "chain",
    "target_species",
    "source_uniprot",
    "target_uniprot",
    "signal_class",
    "contrast_class",
    "contrast_priority",
    "feature_qc_status",
    "is_clustering_ready",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Cluster divergence-profile feature vectors using numeric "
            "residue-delta profile features. Signal and contrast classes are "
            "kept only as post hoc annotations."
        )
    )
    parser.add_argument(
        "--input-features",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_features.csv",
        help="Input divergence-profile feature CSV.",
    )
    parser.add_argument(
        "--output-csv",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters.csv",
        help="Output row-level cluster assignment CSV.",
    )
    parser.add_argument(
        "--output-centroids",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_cluster_centroids.csv",
        help="Output cluster centroid CSV.",
    )
    parser.add_argument(
        "--output-md",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters.md",
        help="Output Markdown cluster summary.",
    )
    parser.add_argument(
        "--features",
        default=None,
        help=(
            "Optional comma-separated numeric feature list. "
            "Defaults to the curated divergence-profile feature set."
        ),
    )
    parser.add_argument(
        "--k",
        default="auto",
        help="Number of KMeans clusters, or 'auto' to choose by silhouette.",
    )
    parser.add_argument(
        "--max-k",
        type=int,
        default=8,
        help="Maximum k considered when --k auto.",
    )
    parser.add_argument(
        "--scaler",
        choices=["standard", "robust"],
        default="standard",
        help="Feature scaling strategy.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=0,
        help="Random seed for KMeans and PCA.",
    )
    return parser.parse_args()


def parse_feature_list(features_arg: str | None) -> list[str]:
    if features_arg is None:
        return list(DEFAULT_FEATURES)
    return [feature.strip() for feature in features_arg.split(",") if feature.strip()]


def markdown_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value).replace("|", "\\|")


def markdown_table(frame: pl.DataFrame) -> str:
    if frame.height == 0:
        return "_No rows._"

    columns = frame.columns
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]

    for row in frame.to_dicts():
        lines.append(
            "| " + " | ".join(markdown_value(row.get(column)) for column in columns) + " |"
        )

    return "\n".join(lines)


def make_scaler(kind: str) -> StandardScaler | RobustScaler:
    if kind == "robust":
        return RobustScaler()
    return StandardScaler()


def choose_k(
    scaled_features: object,
    *,
    requested_k: str,
    max_k: int,
    random_state: int,
) -> tuple[int, pl.DataFrame, dict[int, object]]:
    n_rows = len(scaled_features)

    if requested_k != "auto":
        k = int(requested_k)
        if k < 2:
            raise ValueError("--k must be at least 2")
        if k >= n_rows:
            raise ValueError(f"--k must be less than the number of rows ({n_rows})")

        labels = KMeans(n_clusters=k, n_init=50, random_state=random_state).fit_predict(
            scaled_features
        )
        score = silhouette_score(scaled_features, labels)
        return k, pl.DataFrame([{"k": k, "silhouette": float(score)}]), {k: labels}

    upper_k = min(max_k, n_rows - 1)
    if upper_k < 2:
        raise ValueError("Need at least 3 rows to choose k automatically")

    rows = []
    labels_by_k = {}

    for k in range(2, upper_k + 1):
        labels = KMeans(n_clusters=k, n_init=50, random_state=random_state).fit_predict(
            scaled_features
        )
        score = silhouette_score(scaled_features, labels)
        rows.append({"k": k, "silhouette": float(score)})
        labels_by_k[k] = labels

    summary = pl.DataFrame(rows).sort("silhouette", descending=True)
    return int(summary[0, "k"]), summary, labels_by_k


def build_centroids(clustered: pl.DataFrame, features: Iterable[str]) -> pl.DataFrame:
    feature_list = list(features)

    mean_exprs = [pl.col(feature).mean().alias(f"{feature}_mean") for feature in feature_list]
    median_exprs = [pl.col(feature).median().alias(f"{feature}_median") for feature in feature_list]

    return (
        clustered.group_by("kmeans_cluster")
        .agg([pl.len().alias("n"), *mean_exprs, *median_exprs])
        .sort("kmeans_cluster")
    )


def main() -> None:
    args = parse_args()

    input_path = Path(args.input_features)
    output_csv = Path(args.output_csv)
    output_centroids = Path(args.output_centroids)
    output_md = Path(args.output_md)

    features = parse_feature_list(args.features)

    df = pl.read_csv(input_path)

    if "is_clustering_ready" in df.columns:
        ready = df.filter(pl.col("is_clustering_ready"))
    elif "feature_qc_status" in df.columns:
        ready = df.filter(pl.col("feature_qc_status") == "ok")
    else:
        ready = df

    available_features = [feature for feature in features if feature in ready.columns]
    missing_features = [feature for feature in features if feature not in ready.columns]

    if not available_features:
        raise ValueError("None of the requested numeric features are present")

    ready = ready.drop_nulls(available_features)

    if ready.height < 10:
        raise ValueError(f"Too few clustering-ready rows after null filtering: {ready.height}")

    raw_features = ready.select(available_features).to_numpy()
    scaled_features = make_scaler(args.scaler).fit_transform(raw_features)

    pca = PCA(n_components=2, random_state=args.random_state)
    pcs = pca.fit_transform(scaled_features)

    best_k, k_summary, labels_by_k = choose_k(
        scaled_features,
        requested_k=args.k,
        max_k=args.max_k,
        random_state=args.random_state,
    )

    kmeans_labels = labels_by_k[best_k]
    agglomerative_labels = AgglomerativeClustering(n_clusters=best_k).fit_predict(scaled_features)

    clustered = ready.with_columns(
        [
            pl.Series("pca1", pcs[:, 0]),
            pl.Series("pca2", pcs[:, 1]),
            pl.Series("kmeans_cluster", kmeans_labels),
            pl.Series("agglomerative_cluster", agglomerative_labels),
        ]
    )

    centroids = build_centroids(clustered, available_features)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_centroids.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    clustered.write_csv(output_csv)
    centroids.write_csv(output_centroids)

    cluster_sizes = clustered.group_by("kmeans_cluster").len().sort("kmeans_cluster")

    if "signal_class" in clustered.columns:
        by_signal = (
            clustered.group_by(["kmeans_cluster", "signal_class"])
            .len()
            .sort(["kmeans_cluster", "len"], descending=[False, True])
        )
    else:
        by_signal = pl.DataFrame()

    if "contrast_class" in clustered.columns:
        by_contrast = (
            clustered.group_by(["kmeans_cluster", "contrast_class"])
            .len()
            .sort(["kmeans_cluster", "len"], descending=[False, True])
        )
    else:
        by_contrast = pl.DataFrame()

    outlier_columns = [
        "complex_id",
        "pdb_id",
        "chain",
        "target_species",
        "kmeans_cluster",
        "agglomerative_cluster",
        "pca1",
        "pca2",
        "log2_enrichment_ratio",
        "effect_size_cohens_d_computed",
        "fraction_interface_above_global_q90",
        "signal_class",
        "contrast_class",
    ]
    outlier_columns = [column for column in outlier_columns if column in clustered.columns]

    pca_outliers = (
        clustered.with_columns((pl.col("pca1").abs() + pl.col("pca2").abs()).alias("pca_radius"))
        .sort("pca_radius", descending=True)
        .select(outlier_columns)
        .head(30)
    )

    lines = [
        "# Divergence-profile clustering",
        "",
        f"Input features: `{input_path}`",
        f"Output clusters: `{output_csv}`",
        f"Output centroids: `{output_centroids}`",
        "",
        f"- Total feature rows: {df.height}",
        f"- Clustering-ready rows used: {ready.height}",
        f"- Features used: {len(available_features)}",
        f"- Scaling: `{args.scaler}`",
        f"- KMeans k: {best_k}",
        f"- PCA explained variance ratio: {pca.explained_variance_ratio_[0]:.4f}, "
        f"{pca.explained_variance_ratio_[1]:.4f}",
        "",
        "## Features used",
        "",
    ]

    for feature in available_features:
        lines.append(f"- `{feature}`")

    if missing_features:
        lines.extend(["", "## Requested features not found", ""])
        for feature in missing_features:
            lines.append(f"- `{feature}`")

    lines.extend(
        [
            "",
            "## KMeans silhouette by k",
            "",
            markdown_table(k_summary),
            "",
            "## KMeans cluster sizes",
            "",
            markdown_table(cluster_sizes),
            "",
            "## Cluster centroids",
            "",
            markdown_table(centroids),
            "",
            "## KMeans clusters by signal class",
            "",
            markdown_table(by_signal),
            "",
            "## KMeans clusters by contrast class",
            "",
            markdown_table(by_contrast),
            "",
            "## PCA outlier / extreme rows",
            "",
            markdown_table(pca_outliers),
            "",
            "## Notes",
            "",
            "- This is exploratory clustering, not biological validation.",
            "- `signal_class` and `contrast_class` are post hoc annotations, not clustering coordinates.",
            "- Small clusters and singleton clusters should be interpreted as outlier modes, not robust biological classes.",
        ]
    )

    output_md.write_text("\n".join(lines), encoding="utf-8")

    print("Input:", input_path)
    print("Rows total:", df.height)
    print("Rows clustering-ready:", ready.height)
    print("Features used:", available_features)
    print()
    print("KMeans silhouette by k:")
    print(k_summary)
    print()
    print("Best k:", best_k)
    print()
    print("KMeans cluster sizes:")
    print(cluster_sizes)
    print()
    print("KMeans clusters by signal_class:")
    print(by_signal)
    print()
    print("KMeans clusters by contrast_class:")
    print(by_contrast)
    print()
    print("Wrote cluster CSV ->", output_csv)
    print("Wrote centroid CSV ->", output_centroids)
    print("Wrote cluster Markdown ->", output_md)


if __name__ == "__main__":
    main()
