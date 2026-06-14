from pathlib import Path

import pandas as pd

RESIDUE_PATH = Path("data/output/sirt6_mini_pilot_v2_core3_expanded_residue_deltas_mapped.parquet")
CLUSTER_PATH = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_divergence_profile_clusters.csv"
)
OUT_CSV = Path("data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_residue_shortlist.csv")
OUT_MD = Path("data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_residue_shortlist.md")

TOP_N = 12

CASES = [
    {
        "priority": 1,
        "pdb_id": "8g57",
        "chain": "ligand",
        "species": ["naked_mole_rat", "myotis_lucifugus"],
        "review_case": "SIRT6-nucleosome long-lived interface divergence candidate",
        "selection_mode": "top_interface_delta",
        "review_note": "Inspect whether high-delta ligand-side interface residues form a coherent SIRT6/nucleosome contact surface.",
    },
    {
        "priority": 2,
        "pdb_id": "1nfi",
        "chain": "receptor",
        "species": ["naked_mole_rat", "myotis_lucifugus"],
        "review_case": "NF-kappaB regulatory-interface rewiring candidate",
        "selection_mode": "top_interface_delta",
        "review_note": "Inspect whether high-delta receptor-side residues cluster on the NF-kappaB / IkappaBalpha regulatory interface.",
    },
    {
        "priority": 3,
        "pdb_id": "7s68",
        "chain": "receptor",
        "species": ["naked_mole_rat"],
        "review_case": "PARP1-linked cautious long-lived-specific candidate",
        "selection_mode": "top_interface_delta",
        "review_note": "Inspect whether high-delta receptor-side residues map to a meaningful PARP1-linked DNA-damage-recognition or regulatory surface.",
    },
    {
        "priority": 4,
        "pdb_id": "8f86",
        "chain": "receptor",
        "species": ["myotis_lucifugus"],
        "review_case": "SIRT6-nucleosome maintained-interface candidate",
        "selection_mode": "lowest_interface_delta",
        "review_note": "Inspect whether low-delta interface residues form a preserved SIRT6/nucleosome contact surface while the background diverges.",
    },
    {
        "priority": 5,
        "pdb_id": "4xhu",
        "chain": "receptor",
        "species": ["mouse", "naked_mole_rat", "myotis_lucifugus"],
        "review_case": "shared constrained-interface anchor",
        "selection_mode": "lowest_interface_delta",
        "review_note": "Use as an anchor/control case: inspect whether low-delta residues form a shared conserved interface across all species.",
    },
    {
        "priority": 6,
        "pdb_id": "8bhv",
        "chain": "ligand",
        "species": ["mouse"],
        "review_case": "singleton divergent outlier / artifact-risk benchmark",
        "selection_mode": "top_interface_delta",
        "review_note": "Use as an artifact-risk benchmark: inspect whether the extreme mouse signal is caused by real interface residues or mapping/interface-size issues.",
    },
]


def select_residues(case: dict[str, object], residues: pd.DataFrame) -> pd.DataFrame:
    interface_mask = residues["is_interface"].fillna(False).astype(bool)

    subset = residues[
        (residues["pdb_id"] == case["pdb_id"])
        & (residues["chain"] == case["chain"])
        & (residues["target_species"].isin(case["species"]))
        & interface_mask
    ].copy()

    if subset.empty:
        return subset

    if case["selection_mode"] == "top_interface_delta":
        ascending = [True, True, True, False, True]
    elif case["selection_mode"] == "lowest_interface_delta":
        ascending = [True, True, True, True, True]
    else:
        raise ValueError(f"Unknown selection_mode: {case['selection_mode']}")

    subset = subset.sort_values(
        ["complex_id", "pdb_id", "target_species", "delta", "residue_number_1based"],
        ascending=ascending,
    )

    selected = (
        subset.groupby(
            ["complex_id", "pdb_id", "chain", "target_species"],
            as_index=False,
            group_keys=False,
        )
        .head(TOP_N)
        .copy()
    )

    selected["selection_rank"] = (
        selected.groupby(["complex_id", "pdb_id", "chain", "target_species"]).cumcount() + 1
    )

    for key in ["priority", "review_case", "selection_mode", "review_note"]:
        selected[key] = case[key]

    return selected


def main() -> None:
    residues = pd.read_parquet(RESIDUE_PATH)
    clusters = pd.read_csv(CLUSTER_PATH)

    selected_frames = [select_residues(case, residues) for case in CASES]
    nonempty_frames = [frame for frame in selected_frames if not frame.empty]

    if not nonempty_frames:
        raise RuntimeError("No manual-review residues were selected.")

    selected = pd.concat(nonempty_frames, ignore_index=True)

    cluster_cols = [
        "complex_id",
        "pdb_id",
        "chain",
        "target_species",
        "signal_class",
        "contrast_class",
        "contrast_priority",
        "enrichment_ratio",
        "effect_size_cohens_d",
        "kmeans_cluster",
        "agglomerative_cluster",
        "feature_qc_status",
        "is_clustering_ready",
    ]

    selected = selected.merge(
        clusters[cluster_cols],
        on=["complex_id", "pdb_id", "chain", "target_species"],
        how="left",
    )

    selected["contrast_class"] = selected["contrast_class"].fillna("not_applicable")
    selected["signal_class"] = selected["signal_class"].fillna("not_available")

    selected["residue_label"] = selected["residue_aa"].astype(str) + selected[
        "residue_number_1based"
    ].astype(str)

    output_cols = [
        "priority",
        "review_case",
        "selection_mode",
        "selection_rank",
        "pdb_id",
        "complex_id",
        "chain",
        "target_species",
        "residue_label",
        "residue_index",
        "residue_number_1based",
        "residue_aa",
        "delta",
        "is_interface",
        "signal_class",
        "contrast_class",
        "contrast_priority",
        "enrichment_ratio",
        "effect_size_cohens_d",
        "kmeans_cluster",
        "agglomerative_cluster",
        "feature_qc_status",
        "is_clustering_ready",
        "source_uniprot",
        "target_uniprot",
        "review_note",
    ]

    selected = selected[output_cols].sort_values(
        ["priority", "complex_id", "chain", "target_species", "selection_rank"]
    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(OUT_CSV, index=False)

    summary = (
        selected.groupby(
            [
                "priority",
                "review_case",
                "selection_mode",
                "pdb_id",
                "complex_id",
                "chain",
                "target_species",
                "signal_class",
                "contrast_class",
            ],
            dropna=False,
        )
        .agg(
            n_residues=("residue_label", "count"),
            min_delta=("delta", "min"),
            mean_delta=("delta", "mean"),
            max_delta=("delta", "max"),
            residues=("residue_label", lambda x: ", ".join(map(str, x))),
        )
        .reset_index()
        .sort_values(["priority", "complex_id", "chain", "target_species"])
    )

    lines = []
    lines.append("# SIRT6 v2 core3-expanded manual review residue shortlist")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This file summarizes residue-level candidates for manual structural review from the SIRT6 v2 core3-expanded run."
    )
    lines.append("")
    lines.append(
        "Divergent cases are represented by the highest-delta interface residues. Constrained-anchor cases are represented by the lowest-delta interface residues."
    )
    lines.append("")
    lines.append("## Summary by review case")
    lines.append("")

    for _, row in summary.iterrows():
        lines.append(
            f"### Priority {int(row['priority'])}: {row['pdb_id']} / {row['chain']} / {row['target_species']}"
        )
        lines.append("")
        lines.append(f"- Complex: `{row['complex_id']}`")
        lines.append(f"- Review case: {row['review_case']}")
        lines.append(f"- Selection mode: `{row['selection_mode']}`")
        lines.append(f"- Signal class: `{row['signal_class']}`")
        lines.append(f"- Contrast class: `{row['contrast_class']}`")
        lines.append(f"- Number of residues: {int(row['n_residues'])}")
        lines.append(f"- Delta range: {row['min_delta']:.4f} to {row['max_delta']:.4f}")
        lines.append(f"- Mean delta: {row['mean_delta']:.4f}")
        lines.append(f"- Residues: {row['residues']}")
        lines.append("")

    lines.append("## Caveat")
    lines.append("")
    lines.append(
        "This shortlist is a review aid, not a validation result. Each residue set still needs manual inspection on the corresponding 3D structure to confirm interface localization, chain identity, and residue remapping."
    )
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_CSV} with {len(selected)} rows")
    print(f"Wrote {OUT_MD}")
    print("")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
