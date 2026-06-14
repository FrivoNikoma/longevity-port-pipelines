from pathlib import Path

import pandas as pd

MANUAL_REVIEW_PATH = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_residue_shortlist.csv"
)
MAPPED_INTERFACE_QC_PATH = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_mapped_interface_qc.csv"
)
OUT_CSV = Path(
    "data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_selection_summary.csv"
)


def structure_chains_for_role(row: pd.Series) -> tuple[str, str]:
    chain_role = str(row["chain"])

    if chain_role == "receptor":
        return str(row["selected_chain_R"]), str(row["selected_chain_L"])

    if chain_role == "ligand":
        return str(row["selected_chain_L"]), str(row["selected_chain_R"])

    raise ValueError(f"Unexpected chain role: {chain_role}")


def main() -> None:
    manual = pd.read_csv(MANUAL_REVIEW_PATH)
    mapped_qc = pd.read_csv(MAPPED_INTERFACE_QC_PATH)

    mapped_qc_cols = [
        "complex_id",
        "pdb_id",
        "selected_chain_R",
        "selected_chain_L",
        "sequence_score_R",
        "sequence_score_L",
        "interface_R",
        "interface_L",
        "atom_contacts",
        "status",
    ]

    merged = manual.merge(
        mapped_qc[mapped_qc_cols],
        on=["complex_id", "pdb_id"],
        how="left",
        validate="many_to_one",
    )

    missing_chain_rows = merged[
        merged["selected_chain_R"].isna() | merged["selected_chain_L"].isna()
    ]

    if not missing_chain_rows.empty:
        missing = (
            missing_chain_rows[["complex_id", "pdb_id", "chain", "target_species"]]
            .drop_duplicates()
            .to_string(index=False)
        )
        raise RuntimeError(f"Missing mapped chain QC rows:\n{missing}")

    chain_pairs = merged.apply(structure_chains_for_role, axis=1, result_type="expand")
    merged["structure_chain"] = chain_pairs[0]
    merged["partner_structure_chain"] = chain_pairs[1]

    output = pd.DataFrame(
        {
            "candidate_type": (
                "priority_"
                + merged["priority"].astype(int).astype(str)
                + ": "
                + merged["review_case"].astype(str)
            ),
            "complex_id": merged["complex_id"],
            "pdb_id": merged["pdb_id"],
            "chain": merged["chain"],
            "structure_chain": merged["structure_chain"],
            "partner_structure_chain": merged["partner_structure_chain"],
            "target_species": merged["target_species"],
            "source_uniprot": merged["source_uniprot"],
            "target_uniprot": merged["target_uniprot"],
            "reference_sequence_residue_number": merged["residue_number_1based"].astype(int),
            "residue_aa": merged["residue_aa"],
            "delta": merged["delta"],
            "candidate_rank": merged["selection_rank"].astype(int),
            "contrast_class": merged["contrast_class"],
            "contrast_priority": merged["contrast_priority"],
            "review_case": merged["review_case"],
            "selection_mode": merged["selection_mode"],
            "signal_class": merged["signal_class"],
            "enrichment_ratio": merged["enrichment_ratio"],
            "effect_size_cohens_d": merged["effect_size_cohens_d"],
            "mapped_sequence_score_R": merged["sequence_score_R"],
            "mapped_sequence_score_L": merged["sequence_score_L"],
            "mapped_interface_R": merged["interface_R"],
            "mapped_interface_L": merged["interface_L"],
            "mapped_atom_contacts": merged["atom_contacts"],
            "mapped_interface_qc_status": merged["status"],
        }
    )

    output = output.sort_values(
        [
            "candidate_type",
            "complex_id",
            "chain",
            "target_species",
            "candidate_rank",
        ]
    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUT_CSV, index=False)

    groups = (
        output.groupby(
            [
                "candidate_type",
                "complex_id",
                "pdb_id",
                "chain",
                "structure_chain",
                "partner_structure_chain",
                "target_species",
            ],
            dropna=False,
        )
        .size()
        .reset_index(name="n_residues")
    )

    print(f"Wrote {OUT_CSV} with {len(output)} rows")
    print("")
    print(groups.to_string(index=False))


if __name__ == "__main__":
    main()
