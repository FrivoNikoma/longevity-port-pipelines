from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

DEFAULT_PDB_IDS = ["8f86", "8bot", "7s68"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a small SIRT6 explicit-only pilot selection from a full selection CSV."
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_dna_repair_explicit_only_selection.csv",
        help="Input SIRT6 explicit-only selection CSV.",
    )
    parser.add_argument(
        "--coverage",
        default="data/output/sirt6_dna_repair_explicit_only_ortholog_coverage.csv",
        help="Input SIRT6 explicit-only ortholog coverage CSV.",
    )
    parser.add_argument(
        "--pdb-ids",
        nargs="+",
        default=DEFAULT_PDB_IDS,
        help="PDB IDs to keep for the mini-pilot.",
    )
    parser.add_argument(
        "--output-selection",
        default="data/output/sirt6_mini_pilot_selection.csv",
        help="Output mini-pilot selection CSV.",
    )
    parser.add_argument(
        "--output-coverage",
        default="data/output/sirt6_mini_pilot_ortholog_coverage.csv",
        help="Output mini-pilot ortholog coverage CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    selection_path = Path(args.selection)
    coverage_path = Path(args.coverage)

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing selection CSV: {selection_path}")
    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing ortholog coverage CSV: {coverage_path}")

    selection = pl.read_csv(selection_path)
    coverage = pl.read_csv(coverage_path)

    pdb_ids = set(args.pdb_ids)
    mini_selection = selection.filter(pl.col("pdb_id").is_in(sorted(pdb_ids)))

    if mini_selection.is_empty():
        raise ValueError(f"No rows matched PDB IDs {sorted(pdb_ids)} in {selection_path}")

    source_uniprots = set()
    for col in ["uniprot_R", "uniprot_L"]:
        source_uniprots.update(
            str(value).strip()
            for value in mini_selection.get_column(col).to_list()
            if value is not None and str(value).strip()
        )

    mini_coverage = coverage.filter(pl.col("source_uniprot").is_in(sorted(source_uniprots)))

    output_selection = Path(args.output_selection)
    output_coverage = Path(args.output_coverage)
    output_selection.parent.mkdir(parents=True, exist_ok=True)
    output_coverage.parent.mkdir(parents=True, exist_ok=True)

    mini_selection.write_csv(output_selection)
    mini_coverage.write_csv(output_coverage)

    print("Mini-pilot PDB IDs:", sorted(pdb_ids))
    print("Selected complexes:", mini_selection.height)
    print("Unique source UniProt IDs:", sorted(source_uniprots))
    print("Ortholog coverage rows:", mini_coverage.height)
    print()
    print("Mini-pilot selection:")
    print(
        mini_selection.select(
            [
                "id",
                "pdb_id",
                "uniprot_R",
                "uniprot_L",
                "intermolecular_contacts",
                "predicted_R",
                "predicted_L",
            ]
        )
    )
    print()
    print(f"Wrote mini-pilot selection -> {output_selection}")
    print(f"Wrote mini-pilot coverage -> {output_coverage}")


if __name__ == "__main__":
    main()
