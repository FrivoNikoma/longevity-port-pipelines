from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

CLUSTERS_CSV = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters.csv"
)
STRUCTURE_QC_CSV = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_qc.csv"
)

OUT_CSV = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.csv"
)
OUT_PNG = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.png"
)
OUT_MD = Path("data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters_pca2d.md")

PCA_FEATURE_COLUMNS = [
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

IDENTITY_COLUMNS = [
    "complex_id",
    "pdb_id",
    "chain",
    "target_species",
    "source_uniprot",
    "target_uniprot",
    "signal_class",
    "contrast_class",
]

MANUAL_REVIEW_PDB_ORDER = ["1nfi", "8g57", "8f86", "7s68", "4xhu", "8bhv"]


def cluster_sort_key(value: Any) -> tuple[int, str]:
    text = str(value)

    try:
        return (0, f"{int(float(text)):04d}")
    except ValueError:
        return (1, text)


def load_manual_review_cases() -> pd.DataFrame:
    if not STRUCTURE_QC_CSV.exists():
        return pd.DataFrame()

    qc = pd.read_csv(STRUCTURE_QC_CSV)

    keep = [
        column
        for column in [
            "complex_id",
            "pdb_id",
            "chain",
            "target_species",
            "qc_status",
            "structure_chain",
            "partner_structure_chain",
        ]
        if column in qc.columns
    ]

    return qc[keep].drop_duplicates()


def manual_review_label(row: pd.Series) -> str:
    if not bool(row.get("manual_review_case", False)):
        return ""

    pdb_id = str(row.get("pdb_id", "")).lower()
    chain = str(row.get("chain", ""))
    species = str(row.get("target_species", ""))

    if pdb_id not in MANUAL_REVIEW_PDB_ORDER:
        return ""

    species_short = {
        "naked_mole_rat": "NMR",
        "myotis_lucifugus": "Myotis",
        "mouse": "mouse",
    }.get(species, species)

    structure_chain = row.get("structure_chain", "")
    partner_chain = row.get("partner_structure_chain", "")

    if pdb_id == "8bhv" and structure_chain and partner_chain:
        return f"{pdb_id} {chain} {structure_chain}/{partner_chain} {species_short}"

    return f"{pdb_id} {chain} {species_short}"


def add_manual_review_flag(frame: pd.DataFrame, manual_cases: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output["manual_review_case"] = False
    output["manual_review_label"] = ""

    if manual_cases.empty:
        return output

    merge_keys = [
        column
        for column in ["complex_id", "pdb_id", "chain", "target_species"]
        if column in output.columns and column in manual_cases.columns
    ]

    if not merge_keys:
        return output

    marker_columns = merge_keys + [
        column
        for column in ["qc_status", "structure_chain", "partner_structure_chain"]
        if column in manual_cases.columns
    ]
    marker = manual_cases[marker_columns].drop_duplicates(subset=merge_keys)
    marker["manual_review_case_marker"] = True

    output = output.merge(marker, on=merge_keys, how="left")
    output["manual_review_case"] = output["manual_review_case_marker"].fillna(False)
    output = output.drop(columns=["manual_review_case_marker"])

    output["manual_review_label"] = output.apply(manual_review_label, axis=1)

    return output


def validate_cluster_frame(frame: pd.DataFrame) -> None:
    required = {"pca1", "pca2", "kmeans_cluster", "complex_id", "pdb_id", "chain", "target_species"}
    missing = required - set(frame.columns)

    if missing:
        raise ValueError(f"{CLUSTERS_CSV} is missing required columns: {sorted(missing)}")

    missing_features = [column for column in PCA_FEATURE_COLUMNS if column not in frame.columns]
    if missing_features:
        raise ValueError(
            f"Cluster CSV is missing expected PCA/clustering feature columns: {missing_features}"
        )


def plot_pca(frame: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 8.0))

    clusters = sorted(frame["kmeans_cluster"].unique(), key=cluster_sort_key)

    for cluster in clusters:
        subset = frame[frame["kmeans_cluster"] == cluster]
        ax.scatter(
            subset["pca1"],
            subset["pca2"],
            s=48,
            alpha=0.72,
            label=f"Cluster {cluster}",
        )

    manual = frame[frame["manual_review_case"]]
    if not manual.empty:
        ax.scatter(
            manual["pca1"],
            manual["pca2"],
            s=150,
            facecolors="none",
            edgecolors="black",
            linewidths=1.5,
            label="Manual-review case",
        )

        for _, row in manual.iterrows():
            label = str(row["manual_review_label"])
            if not label:
                continue

            ax.annotate(
                label,
                xy=(row["pca1"], row["pca2"]),
                xytext=(6, 6),
                textcoords="offset points",
                fontsize=8,
            )

    ax.set_title("SIRT6 v2 core3-expanded divergence-profile clusters: PCA 2D projection")
    ax.set_xlabel("PC1 from clustering script")
    ax.set_ylabel("PC2 from clustering script")
    ax.axhline(0, linewidth=0.8, alpha=0.35)
    ax.axvline(0, linewidth=0.8, alpha=0.35)
    ax.legend(loc="best", fontsize=8)
    ax.text(
        0.01,
        0.01,
        "PCA of the 11 curated divergence-profile features used for clustering; visualization only.",
        transform=ax.transAxes,
        fontsize=8,
        va="bottom",
    )

    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=220)
    plt.close(fig)


def markdown_summary(frame: pd.DataFrame) -> str:
    lines: list[str] = []

    lines.append("# SIRT6 v2 core3-expanded divergence-profile clusters PCA map")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This file summarizes a two-dimensional PCA projection of the "
        "SIRT6 v2 core3-expanded divergence-profile clusters."
    )
    lines.append("")
    lines.append(
        "The PCA coordinates are taken from the existing clustering output "
        "`pca1` and `pca2`, rather than recomputed here."
    )
    lines.append("")
    lines.append(
        "The clustering script uses the curated 11-dimensional divergence-profile "
        "feature set listed below, scales those features, and projects them into "
        "two principal components for visualization."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Cluster output: `{CLUSTERS_CSV}`")
    lines.append(f"- Manual-review structure QC: `{STRUCTURE_QC_CSV}`")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- PCA coordinates: `{OUT_CSV}`")
    lines.append(f"- PCA figure: `{OUT_PNG}`")
    lines.append(f"- Summary: `{OUT_MD}`")
    lines.append("")
    lines.append("## Original feature-space dimension")
    lines.append("")
    lines.append(
        f"- Original divergence-profile feature-space dimension: {len(PCA_FEATURE_COLUMNS)}"
    )
    lines.append("- PCA projection dimension: 2")
    lines.append("")
    lines.append("## Feature columns used by the clustering PCA")
    lines.append("")

    for column in PCA_FEATURE_COLUMNS:
        lines.append(f"- `{column}`")

    lines.append("")
    lines.append("## Cluster counts")
    lines.append("")

    counts = frame["kmeans_cluster"].value_counts().sort_index()

    for cluster, count in counts.items():
        lines.append(f"- Cluster `{cluster}`: {count} rows")

    lines.append("")
    lines.append("## Manual-review cases shown on the PCA map")
    lines.append("")

    manual = frame[frame["manual_review_case"]].copy()

    if manual.empty:
        lines.append("No manual-review cases were matched to the PCA rows.")
    else:
        columns = [
            "manual_review_label",
            "kmeans_cluster",
            "complex_id",
            "pdb_id",
            "chain",
            "target_species",
            "pca1",
            "pca2",
        ]

        for _, row in manual[columns].iterrows():
            lines.append(
                "- "
                f"`{row['manual_review_label']}` "
                f"(cluster `{row['kmeans_cluster']}`, "
                f"PC1={row['pca1']:.3f}, PC2={row['pca2']:.3f}, "
                f"complex `{row['complex_id']}`)"
            )

    lines.append("")
    lines.append("## Interpretation note")
    lines.append("")
    lines.append(
        "This PCA map should be interpreted as a low-dimensional visualization "
        "of the 11-dimensional divergence-profile feature space used for clustering. "
        "The PCA axes are not biological mechanisms. Biological interpretation "
        "still depends on the residue-level packet, structure-remapping QC, "
        "viewer-ready selections, and manual 3D review."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    clusters = pd.read_csv(CLUSTERS_CSV)
    validate_cluster_frame(clusters)

    manual_cases = load_manual_review_cases()
    clusters = add_manual_review_flag(clusters, manual_cases)

    output_columns = [column for column in IDENTITY_COLUMNS if column in clusters.columns] + [
        "kmeans_cluster",
        "agglomerative_cluster",
        "pca1",
        "pca2",
        "manual_review_case",
        "manual_review_label",
    ]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    clusters[output_columns].to_csv(OUT_CSV, index=False)

    plot_pca(clusters)

    OUT_MD.write_text(markdown_summary(clusters), encoding="utf-8")

    print(f"Wrote {OUT_CSV} with {len(clusters)} rows")
    print(f"Wrote {OUT_PNG}")
    print(f"Wrote {OUT_MD}")
    print("")
    print(f"Original feature-space dimension: {len(PCA_FEATURE_COLUMNS)}")
    print("PCA projection dimension: 2")
    print("")
    print(
        clusters[
            [
                "pdb_id",
                "chain",
                "target_species",
                "kmeans_cluster",
                "pca1",
                "pca2",
                "manual_review_case",
                "manual_review_label",
            ]
        ]
        .sort_values(["manual_review_case", "pdb_id", "chain", "target_species"])
        .tail(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
