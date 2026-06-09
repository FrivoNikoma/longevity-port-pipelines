from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

DEFAULT_DIVERGENT = "data/output/sirt6_mini_pilot_top_divergent_interface_residues.csv"
DEFAULT_CONSTRAINED = "data/output/sirt6_mini_pilot_top_constrained_interface_residues.csv"
DEFAULT_OUTPUT_DIR = "data/output/structure_selections"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export PyMOL and ChimeraX selections for mini-pilot residue candidates."
    )
    parser.add_argument(
        "--top-divergent",
        default=DEFAULT_DIVERGENT,
        help="Top divergent interface residue candidates CSV.",
    )
    parser.add_argument(
        "--top-constrained",
        default=DEFAULT_CONSTRAINED,
        help="Top constrained interface residue candidates CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for structure selection scripts.",
    )
    parser.add_argument(
        "--top-n-per-group",
        type=int,
        default=10,
        help="Maximum residues per complex/chain/species/candidate-type group.",
    )
    return parser.parse_args()


def read_candidate_table(path: Path, candidate_type: str) -> pl.DataFrame:
    if not path.exists():
        return pl.DataFrame()

    df = pl.read_csv(path)
    required = {
        "complex_id",
        "pdb_id",
        "chain",
        "target_species",
        "source_uniprot",
        "target_uniprot",
        "residue_number_1based",
        "residue_aa",
        "delta",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

    return df.select(sorted(required)).with_columns(pl.lit(candidate_type).alias("candidate_type"))


def structure_chain_for_candidate(row: dict[str, object]) -> str:
    complex_id = str(row["complex_id"])
    chain_role = str(row["chain"])

    if "8bot" in complex_id:
        if chain_role == "receptor":
            return "U"
        if chain_role == "ligand":
            return "T"

    if "7s68" in complex_id:
        if chain_role == "receptor":
            return "A"
        if chain_role == "ligand":
            return "B"

    if "8f86" in complex_id:
        if chain_role == "receptor":
            return "K"
        if chain_role == "ligand":
            return "A"

    return chain_role


def candidate_label(row: dict[str, object]) -> str:
    return (
        f"{row['candidate_type']}_{row['pdb_id']}_{row['chain']}_"
        f"{row['target_species']}_{row['source_uniprot']}"
    )


def sanitize_name(value: str) -> str:
    allowed = []
    for char in value:
        if char.isalnum() or char in {"_", "-"}:
            allowed.append(char)
        else:
            allowed.append("_")
    return "".join(allowed)


def pymol_selection_line(name: str, structure_chain: str, residues: list[int]) -> str:
    residue_expr = "+".join(str(residue) for residue in residues)
    return f"select {name}, chain {structure_chain} and resi {residue_expr}"


def chimerax_selection_line(name: str, structure_chain: str, residues: list[int]) -> str:
    residue_expr = ",".join(str(residue) for residue in residues)
    return f"name {name} /{structure_chain}:{residue_expr}"


def load_candidates(divergent_path: Path, constrained_path: Path) -> pl.DataFrame:
    tables = [
        read_candidate_table(divergent_path, "divergent"),
        read_candidate_table(constrained_path, "constrained"),
    ]
    tables = [table for table in tables if not table.is_empty()]

    if not tables:
        return pl.DataFrame()

    return pl.concat(tables, how="vertical")


def build_summary(candidates: pl.DataFrame, top_n_per_group: int) -> pl.DataFrame:
    candidates = candidates.with_columns(
        pl.struct(["complex_id", "chain"])
        .map_elements(structure_chain_for_candidate, return_dtype=pl.Utf8)
        .alias("structure_chain")
    )

    rank_descending = (
        pl.col("delta")
        .rank(method="ordinal", descending=True)
        .over(["candidate_type", "complex_id", "chain", "target_species"])
    )
    rank_ascending = (
        pl.col("delta")
        .rank(method="ordinal", descending=False)
        .over(["candidate_type", "complex_id", "chain", "target_species"])
    )

    candidates = candidates.with_columns(
        [
            pl.when(pl.col("candidate_type") == "divergent")
            .then(rank_descending)
            .otherwise(rank_ascending)
            .alias("candidate_rank"),
            pl.col("residue_number_1based").alias("reference_sequence_residue_number"),
        ]
    )

    return (
        candidates.filter(pl.col("candidate_rank") <= top_n_per_group)
        .select(
            [
                "candidate_type",
                "complex_id",
                "pdb_id",
                "chain",
                "structure_chain",
                "target_species",
                "source_uniprot",
                "target_uniprot",
                "reference_sequence_residue_number",
                "residue_aa",
                "delta",
                "candidate_rank",
            ]
        )
        .sort(
            [
                "candidate_type",
                "complex_id",
                "chain",
                "target_species",
                "candidate_rank",
            ]
        )
    )


def write_pymol_script(summary: pl.DataFrame, output_path: Path) -> None:
    lines = [
        "# SIRT6 mini-pilot candidate residue selections for PyMOL",
        "#",
        "# IMPORTANT:",
        "# These selections use reference-sequence 1-based residue numbers.",
        "# They assume that reference sequence numbering matches structure residue numbering.",
        "# If a structure has missing residues, insertion codes, or renumbered chains,",
        "# inspect and adjust selections manually.",
        "#",
        "hide everything",
        "show cartoon",
        "color gray80",
        "",
    ]

    grouped = summary.group_by(
        [
            "candidate_type",
            "complex_id",
            "pdb_id",
            "chain",
            "structure_chain",
            "target_species",
            "source_uniprot",
        ]
    ).agg(
        [
            pl.col("reference_sequence_residue_number").sort().alias("residues"),
            pl.col("delta").mean().alias("mean_delta"),
        ]
    )

    for row in grouped.sort(["candidate_type", "pdb_id", "chain", "target_species"]).iter_rows(
        named=True
    ):
        selection_name = sanitize_name(candidate_label(row))
        residues = [int(residue) for residue in row["residues"]]
        if not residues:
            continue

        lines.extend(
            [
                "",
                f"# {row['candidate_type']} | {row['complex_id']} | "
                f"{row['chain']} | {row['target_species']} | "
                f"mean_delta={float(row['mean_delta']):.4f}",
                pymol_selection_line(selection_name, str(row["structure_chain"]), residues),
            ]
        )

        if row["candidate_type"] == "divergent":
            lines.extend(
                [
                    f"show sticks, {selection_name}",
                    f"color red, {selection_name}",
                ]
            )
        else:
            lines.extend(
                [
                    f"show sticks, {selection_name}",
                    f"color blue, {selection_name}",
                ]
            )

    lines.extend(
        [
            "",
            "# Convenience combined selections",
            "select all_divergent_candidates, none",
            "select all_constrained_candidates, none",
        ]
    )

    divergent_names = []
    constrained_names = []
    for row in grouped.iter_rows(named=True):
        name = sanitize_name(candidate_label(row))
        if row["candidate_type"] == "divergent":
            divergent_names.append(name)
        else:
            constrained_names.append(name)

    if divergent_names:
        lines.append(f"select all_divergent_candidates, {' or '.join(divergent_names)}")
        lines.append("color red, all_divergent_candidates")
        lines.append("show sticks, all_divergent_candidates")

    if constrained_names:
        lines.append(f"select all_constrained_candidates, {' or '.join(constrained_names)}")
        lines.append("color blue, all_constrained_candidates")
        lines.append("show sticks, all_constrained_candidates")

    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_chimerax_script(summary: pl.DataFrame, output_path: Path) -> None:
    lines = [
        "# SIRT6 mini-pilot candidate residue selections for ChimeraX",
        "#",
        "# IMPORTANT:",
        "# These selections use reference-sequence 1-based residue numbers.",
        "# They assume that reference sequence numbering matches structure residue numbering.",
        "# If a structure has missing residues, insertion codes, or renumbered chains,",
        "# inspect and adjust selections manually.",
        "#",
        "cartoon",
        "color gray",
        "",
    ]

    grouped = summary.group_by(
        [
            "candidate_type",
            "complex_id",
            "pdb_id",
            "chain",
            "structure_chain",
            "target_species",
            "source_uniprot",
        ]
    ).agg(
        [
            pl.col("reference_sequence_residue_number").sort().alias("residues"),
            pl.col("delta").mean().alias("mean_delta"),
        ]
    )

    for row in grouped.sort(["candidate_type", "pdb_id", "chain", "target_species"]).iter_rows(
        named=True
    ):
        selection_name = sanitize_name(candidate_label(row))
        residues = [int(residue) for residue in row["residues"]]
        if not residues:
            continue

        lines.extend(
            [
                "",
                f"# {row['candidate_type']} | {row['complex_id']} | "
                f"{row['chain']} | {row['target_species']} | "
                f"mean_delta={float(row['mean_delta']):.4f}",
                chimerax_selection_line(selection_name, str(row["structure_chain"]), residues),
            ]
        )

        if row["candidate_type"] == "divergent":
            lines.extend(
                [
                    "color sel red",
                    "style sel stick",
                ]
            )
        else:
            lines.extend(
                [
                    "color sel blue",
                    "style sel stick",
                ]
            )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    divergent_path = Path(args.top_divergent)
    constrained_path = Path(args.top_constrained)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates = load_candidates(divergent_path, constrained_path)
    if candidates.is_empty():
        raise FileNotFoundError(
            "No candidate residue tables were found. Run scripts.summarize_residue_level_candidates first."
        )

    summary = build_summary(candidates, args.top_n_per_group)

    summary_path = output_dir / "sirt6_mini_pilot_candidate_selection_summary.csv"
    pymol_path = output_dir / "sirt6_mini_pilot_candidate_selections.pml"
    chimerax_path = output_dir / "sirt6_mini_pilot_candidate_selections.cxc"

    summary.write_csv(summary_path)
    write_pymol_script(summary, pymol_path)
    write_chimerax_script(summary, chimerax_path)

    print(f"Wrote candidate selection summary -> {summary_path}")
    print(f"Wrote PyMOL selections -> {pymol_path}")
    print(f"Wrote ChimeraX selections -> {chimerax_path}")
    print()
    print("Selection summary shape:")
    print(summary.shape)
    print()
    print("Selection summary preview:")
    print(
        summary.select(
            [
                "candidate_type",
                "pdb_id",
                "chain",
                "structure_chain",
                "target_species",
                "source_uniprot",
                "reference_sequence_residue_number",
                "residue_aa",
                "delta",
                "candidate_rank",
            ]
        ).head(30)
    )


if __name__ == "__main__":
    main()
