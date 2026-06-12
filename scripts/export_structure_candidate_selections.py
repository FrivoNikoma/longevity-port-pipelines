from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import polars as pl

DEFAULT_DIVERGENT = "data/output/sirt6_mini_pilot_top_divergent_interface_residues.csv"
DEFAULT_CONSTRAINED = "data/output/sirt6_mini_pilot_top_constrained_interface_residues.csv"
DEFAULT_OUTPUT_DIR = "data/output/structure_selections"
DEFAULT_FOCUS_CLASSES = [
    "long_lived_specific_interface_divergence",
    "long_lived_enhanced_interface_divergence",
    "shared_nonhuman_interface_divergence",
]


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
        "--residue-deltas",
        default=None,
        help=(
            "Optional full residue-delta parquet. When used with --longevity-contrast, "
            "the script selects top interface residues directly from the full residue-delta layer."
        ),
    )
    parser.add_argument(
        "--longevity-contrast",
        default=None,
        help=(
            "Optional longevity contrast CSV. When provided, residue candidates are filtered "
            "to contrast rows matching complex_id/chain/long_lived_species."
        ),
    )
    parser.add_argument(
        "--focus-classes",
        nargs="+",
        default=DEFAULT_FOCUS_CLASSES,
        help="Contrast classes to export when --longevity-contrast is provided.",
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


def read_longevity_contrast(path: Path, focus_classes: list[str]) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing longevity contrast CSV: {path}")

    df = pl.read_csv(path)
    required = {
        "complex_id",
        "chain",
        "long_lived_species",
        "short_lived_species",
        "contrast_class",
        "contrast_priority",
        "long_enrichment_ratio",
        "short_enrichment_ratio",
        "enrichment_delta",
        "enrichment_log2_ratio",
        "long_effect_size",
        "short_effect_size",
        "effect_size_delta",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

    out = (
        df.filter(pl.col("contrast_class").is_in(focus_classes))
        .select(
            [
                "complex_id",
                "chain",
                "long_lived_species",
                "short_lived_species",
                "contrast_class",
                "contrast_priority",
                "long_enrichment_ratio",
                "short_enrichment_ratio",
                "enrichment_delta",
                "enrichment_log2_ratio",
                "long_effect_size",
                "short_effect_size",
                "effect_size_delta",
            ]
        )
        .rename({"long_lived_species": "target_species"})
    )

    if out.is_empty():
        raise ValueError(
            f"Longevity contrast filtering produced no rows. Check --focus-classes: {focus_classes}"
        )

    return out


def read_residue_deltas(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing residue-delta parquet: {path}")

    df = pl.read_parquet(path)
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
        "is_interface",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

    return df.select(sorted(required))


def candidate_type_for_contrast_class(contrast_class: str) -> str:
    if "constraint" in contrast_class or "constrained" in contrast_class:
        return "constrained"
    return "divergent"


def structure_chain_for_candidate(row: dict[str, object]) -> str:
    complex_id = str(row["complex_id"])
    pdb_id = complex_id.split("__", maxsplit=1)[0]
    chain_role = str(row["chain"])

    mapping = {
        "8bot": {"receptor": "U", "ligand": "T"},
        "1h2k": {"receptor": "A", "ligand": "S"},
        "1nfi": {"receptor": "C", "ligand": "E"},
        "8bhy": {"receptor": "T", "ligand": "M"},
        "7s68": {"receptor": "A", "ligand": "B"},
        "4xhu": {"receptor": "C", "ligand": "D"},
        "8bhv": {"receptor": "j", "ligand": "R"},
        "8f86": {"receptor": "K", "ligand": "A"},
    }

    return mapping.get(pdb_id, {}).get(chain_role, chain_role)


def candidate_label(row: dict[str, object]) -> str:
    label_parts = [
        str(row["candidate_type"]),
        str(row["pdb_id"]),
        str(row["chain"]),
        str(row["target_species"]),
        str(row["source_uniprot"]),
    ]

    if "contrast_class" in row and row["contrast_class"] is not None:
        label_parts.append(str(row["contrast_class"]))

    return "_".join(label_parts)


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


def build_candidates_from_residue_deltas(
    residue_deltas: pl.DataFrame,
    contrast: pl.DataFrame,
) -> pl.DataFrame:
    joined = (
        residue_deltas.filter(pl.col("is_interface"))
        .join(
            contrast,
            on=["complex_id", "chain", "target_species"],
            how="inner",
        )
        .with_columns(
            pl.col("contrast_class")
            .map_elements(candidate_type_for_contrast_class, return_dtype=pl.Utf8)
            .alias("candidate_type")
        )
    )

    if joined.is_empty():
        raise ValueError(
            "No interface residue deltas matched longevity contrast rows. "
            "Check --residue-deltas, --longevity-contrast, species names, and focus classes."
        )

    return joined.drop("is_interface")


def apply_longevity_contrast_filter(
    candidates: pl.DataFrame,
    contrast: pl.DataFrame,
) -> pl.DataFrame:
    filtered = candidates.join(
        contrast,
        on=["complex_id", "chain", "target_species"],
        how="inner",
    )

    if filtered.is_empty():
        raise ValueError(
            "No residue candidates matched longevity contrast rows. "
            "Check top residue candidate paths, species names, and focus classes."
        )

    return filtered


def optional_summary_columns(summary: pl.DataFrame) -> list[str]:
    columns = [
        "short_lived_species",
        "contrast_class",
        "contrast_priority",
        "long_enrichment_ratio",
        "short_enrichment_ratio",
        "enrichment_delta",
        "enrichment_log2_ratio",
        "long_effect_size",
        "short_effect_size",
        "effect_size_delta",
    ]
    return [column for column in columns if column in summary.columns]


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

    base_columns = [
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

    return (
        candidates.filter(pl.col("candidate_rank") <= top_n_per_group)
        .select(base_columns + optional_summary_columns(candidates))
        .sort(
            [
                "candidate_type",
                "pdb_id",
                "chain",
                "target_species",
                "candidate_rank",
            ]
        )
    )


def group_columns_for_scripts(summary: pl.DataFrame) -> list[str]:
    columns = [
        "candidate_type",
        "complex_id",
        "pdb_id",
        "chain",
        "structure_chain",
        "target_species",
        "source_uniprot",
    ]

    for optional in [
        "short_lived_species",
        "contrast_class",
        "contrast_priority",
        "long_enrichment_ratio",
        "short_enrichment_ratio",
        "enrichment_delta",
        "enrichment_log2_ratio",
    ]:
        if optional in summary.columns:
            columns.append(optional)

    return columns


def contrast_comment(row: dict[str, Any]) -> str:
    if "contrast_class" not in row or row["contrast_class"] is None:
        return ""

    return (
        f" | contrast={row['contrast_class']} | "
        f"long={float(row['long_enrichment_ratio']):.4f} | "
        f"short={float(row['short_enrichment_ratio']):.4f} | "
        f"delta={float(row['enrichment_delta']):.4f}"
    )


def grouped_selection_summary(summary: pl.DataFrame) -> pl.DataFrame:
    return summary.group_by(group_columns_for_scripts(summary)).agg(
        [
            pl.col("reference_sequence_residue_number").sort().alias("residues"),
            pl.col("delta").mean().alias("mean_delta"),
        ]
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
        "show cartoon",
        "color gray",
        "",
    ]

    grouped = grouped_selection_summary(summary)

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
                f"mean_delta={float(row['mean_delta']):.4f}"
                f"{contrast_comment(row)}",
                pymol_selection_line(selection_name, str(row["structure_chain"]), residues),
            ]
        )

        if row["candidate_type"] == "divergent":
            lines.extend(
                [
                    f"color red, {selection_name}",
                    f"show sticks, {selection_name}",
                ]
            )
        else:
            lines.extend(
                [
                    f"color blue, {selection_name}",
                    f"show sticks, {selection_name}",
                ]
            )

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

    grouped = grouped_selection_summary(summary)

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
                f"mean_delta={float(row['mean_delta']):.4f}"
                f"{contrast_comment(row)}",
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


def preview_columns(summary: pl.DataFrame) -> list[str]:
    columns = [
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
    columns.extend(optional_summary_columns(summary))
    return columns


def main() -> None:
    args = parse_args()

    divergent_path = Path(args.top_divergent)
    constrained_path = Path(args.top_constrained)
    residue_deltas_path = Path(args.residue_deltas) if args.residue_deltas else None
    longevity_contrast_path = Path(args.longevity_contrast) if args.longevity_contrast else None
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    contrast = None
    if longevity_contrast_path is not None:
        contrast = read_longevity_contrast(longevity_contrast_path, args.focus_classes)

    if residue_deltas_path is not None:
        if contrast is None:
            raise ValueError("--residue-deltas requires --longevity-contrast")
        candidates = build_candidates_from_residue_deltas(
            read_residue_deltas(residue_deltas_path),
            contrast,
        )
    else:
        candidates = load_candidates(divergent_path, constrained_path)
        if candidates.is_empty():
            raise FileNotFoundError(
                "No candidate residue tables were found. "
                "Run scripts.summarize_residue_level_candidates first."
            )

        if contrast is not None:
            candidates = apply_longevity_contrast_filter(candidates, contrast)

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
    print(summary.select(preview_columns(summary)).head(30))


if __name__ == "__main__":
    main()
