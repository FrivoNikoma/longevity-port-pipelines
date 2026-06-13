from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

DEFAULT_SELECTION = "data/output/sirt6_mini_pilot_v2_expanded_selection.csv"
DEFAULT_ORTHOLOG_COVERAGE = "data/output/sirt6_mini_pilot_v2_expanded_ortholog_coverage.csv"
DEFAULT_OUTPUT_SELECTION = "data/output/sirt6_mini_pilot_v2_core3_expanded_selection.csv"
DEFAULT_OUTPUT_COVERAGE = "data/output/sirt6_mini_pilot_v2_core3_expanded_ortholog_coverage.csv"
DEFAULT_OUTPUT_AUDIT = "data/output/sirt6_mini_pilot_v2_core3_expanded_readiness_audit.csv"

CORE_TARGET_SPECIES = {
    10181: "naked_mole_rat",
    59463: "myotis_lucifugus",
    10090: "mouse",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a conservative SIRT6 v2 core3 expanded selection. "
            "Core3 keeps only complex rows where receptor and ligand both have "
            "ortholog mappings for mouse, naked mole rat, and Myotis lucifugus."
        )
    )
    parser.add_argument(
        "--selection",
        default=DEFAULT_SELECTION,
        help="Input expanded selection CSV.",
    )
    parser.add_argument(
        "--ortholog-coverage",
        default=DEFAULT_ORTHOLOG_COVERAGE,
        help="Input expanded ortholog coverage CSV.",
    )
    parser.add_argument(
        "--output-selection",
        default=DEFAULT_OUTPUT_SELECTION,
        help="Output core3 expanded selection CSV.",
    )
    parser.add_argument(
        "--output-coverage",
        default=DEFAULT_OUTPUT_COVERAGE,
        help="Output core3 expanded ortholog coverage CSV.",
    )
    parser.add_argument(
        "--output-audit",
        default=DEFAULT_OUTPUT_AUDIT,
        help="Output core3 readiness audit CSV.",
    )
    return parser.parse_args()


def require_columns(frame: pl.DataFrame, required: set[str], path: Path) -> None:
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")


def build_readiness_audit(selection: pl.DataFrame, coverage: pl.DataFrame) -> pl.DataFrame:
    covered = {
        (row["source_uniprot"], int(row["target_species_taxid"])): row["target_uniprot"]
        for row in coverage.select(
            ["source_uniprot", "target_species_taxid", "target_uniprot"]
        ).iter_rows(named=True)
    }

    rows = []
    for row in selection.iter_rows(named=True):
        for chain_role, uniprot_col in [
            ("receptor", "uniprot_R"),
            ("ligand", "uniprot_L"),
        ]:
            source_uniprot = row[uniprot_col]
            for taxid, species_name in CORE_TARGET_SPECIES.items():
                target_uniprot = covered.get((source_uniprot, taxid))
                rows.append(
                    {
                        "id": row["id"],
                        "pdb_id": row["pdb_id"],
                        "chain_role": chain_role,
                        "source_uniprot": source_uniprot,
                        "target_species_taxid": taxid,
                        "target_species": species_name,
                        "target_uniprot": target_uniprot,
                        "has_ortholog_mapping": target_uniprot is not None,
                        "intermolecular_contacts": row["intermolecular_contacts"],
                        "predicted_R": row["predicted_R"],
                        "predicted_L": row["predicted_L"],
                    }
                )

    return pl.DataFrame(rows)


def core3_ready_ids(readiness_audit: pl.DataFrame) -> list[str]:
    pair = readiness_audit.group_by(["id", "pdb_id", "target_species"]).agg(
        pl.col("has_ortholog_mapping").all().alias("both_chains_mapped")
    )

    all3 = pair.group_by(["id", "pdb_id"]).agg(
        pl.col("both_chains_mapped").all().alias("all_three_species_both_chains"),
        pl.col("both_chains_mapped").sum().alias("n_species_both_chains"),
    )

    return all3.filter(pl.col("all_three_species_both_chains"))["id"].to_list()


def build_core3_outputs(
    selection: pl.DataFrame,
    coverage: pl.DataFrame,
    readiness_audit: pl.DataFrame,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    ready_ids = core3_ready_ids(readiness_audit)

    core_selection = selection.filter(pl.col("id").is_in(ready_ids)).sort(
        ["intermolecular_contacts", "pdb_id"],
        descending=[True, False],
    )

    source_uniprots = set(core_selection["uniprot_R"].to_list()) | set(
        core_selection["uniprot_L"].to_list()
    )

    core_coverage = coverage.filter(
        pl.col("source_uniprot").is_in(sorted(source_uniprots))
        & pl.col("target_species_taxid").is_in(sorted(CORE_TARGET_SPECIES))
    ).sort(["source_uniprot", "target_species_taxid"])

    return core_selection, core_coverage


def estimate_embedding_pairs(selection: pl.DataFrame, coverage: pl.DataFrame) -> tuple[int, int]:
    covered = {
        (row["source_uniprot"], int(row["target_species_taxid"]))
        for row in coverage.select(["source_uniprot", "target_species_taxid"]).iter_rows(named=True)
    }

    embedding_pairs = 0
    missing = 0
    for row in selection.iter_rows(named=True):
        for uniprot_col in ["uniprot_R", "uniprot_L"]:
            for taxid in CORE_TARGET_SPECIES:
                if (row[uniprot_col], taxid) in covered:
                    embedding_pairs += 1
                else:
                    missing += 1

    return embedding_pairs, missing


def main() -> None:
    args = parse_args()

    selection_path = Path(args.selection)
    coverage_path = Path(args.ortholog_coverage)
    output_selection = Path(args.output_selection)
    output_coverage = Path(args.output_coverage)
    output_audit = Path(args.output_audit)

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing expanded selection: {selection_path}")
    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing expanded ortholog coverage: {coverage_path}")

    selection = pl.read_csv(selection_path)
    coverage = pl.read_csv(coverage_path)

    require_columns(
        selection,
        {
            "id",
            "pdb_id",
            "uniprot_R",
            "uniprot_L",
            "intermolecular_contacts",
            "predicted_R",
            "predicted_L",
        },
        selection_path,
    )
    require_columns(
        coverage,
        {
            "source_uniprot",
            "target_species_taxid",
            "target_uniprot",
        },
        coverage_path,
    )

    readiness_audit = build_readiness_audit(selection, coverage)
    core_selection, core_coverage = build_core3_outputs(
        selection,
        coverage,
        readiness_audit,
    )

    output_selection.parent.mkdir(parents=True, exist_ok=True)
    output_coverage.parent.mkdir(parents=True, exist_ok=True)
    output_audit.parent.mkdir(parents=True, exist_ok=True)

    readiness_audit.write_csv(output_audit)
    core_selection.write_csv(output_selection)
    core_coverage.write_csv(output_coverage)

    embedding_pairs, missing_pairs = estimate_embedding_pairs(core_selection, core_coverage)

    source_uniprots = set(core_selection["uniprot_R"].to_list()) | set(
        core_selection["uniprot_L"].to_list()
    )

    print(f"Wrote readiness audit -> {output_audit}")
    print(f"Wrote core3 expanded selection -> {output_selection}")
    print(f"Wrote core3 expanded ortholog coverage -> {output_coverage}")
    print()
    print("Core3 target species:")
    for taxid, species_name in CORE_TARGET_SPECIES.items():
        print(f"- {species_name}: {taxid}")
    print()
    print("Core3 summary:")
    print(f"- selection rows: {core_selection.height}")
    print(f"- unique PDB IDs: {core_selection['pdb_id'].n_unique()}")
    print(f"- source UniProt IDs: {len(source_uniprots)}")
    print(f"- ortholog coverage rows: {core_coverage.height}")
    print(f"- embedding pairs: {embedding_pairs}")
    print(f"- estimated Biohub API calls: {embedding_pairs * 2}")
    print(f"- missing embedding pairs: {missing_pairs}")
    print()
    print("Coverage by target species:")
    print(core_coverage.group_by("target_species_taxid").len().sort("target_species_taxid"))
    print()
    print("Core3 selection preview:")
    print(
        core_selection.select(
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


if __name__ == "__main__":
    main()
