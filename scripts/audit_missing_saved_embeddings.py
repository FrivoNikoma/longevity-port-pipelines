from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

DEFAULT_MODEL_NAME = "esmc-300m-2024-12"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit missing saved per-residue embedding files for a selection and coverage table."
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_mini_pilot_selection.csv",
        help="Input selection CSV.",
    )
    parser.add_argument(
        "--coverage",
        default="data/output/sirt6_mini_pilot_ortholog_coverage.csv",
        help="Input ortholog coverage CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/output",
        help="Pipeline output directory containing the embeddings/ subdirectory.",
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL_NAME,
        help="Embedding model subdirectory name.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_missing_embeddings.csv",
        help="Output CSV with expected embedding paths and missing/existing status.",
    )
    return parser.parse_args()


def expected_embedding_path(
    output_dir: Path,
    model_name: str,
    complex_id: str,
    chain: str,
    taxid: int,
) -> Path:
    return output_dir / "embeddings" / model_name / f"{complex_id}_{chain}_{taxid}.npy"


def build_embedding_audit(
    selection: pl.DataFrame,
    coverage: pl.DataFrame,
    output_dir: Path,
    model_name: str,
) -> pl.DataFrame:
    rows: list[dict[str, object]] = []

    coverage_columns = [
        "source_uniprot",
        "target_uniprot",
        "target_species_taxid",
    ]

    if "target_species" in coverage.columns:
        coverage_columns.append("target_species")

    for selection_row in selection.iter_rows(named=True):
        complex_id = str(selection_row["id"])
        pdb_id = str(selection_row["pdb_id"])

        for chain, source_uniprot in [
            ("receptor", selection_row["uniprot_R"]),
            ("ligand", selection_row["uniprot_L"]),
        ]:
            source_uniprot_str = str(source_uniprot)

            coverage_rows = (
                coverage.filter(pl.col("source_uniprot") == source_uniprot_str)
                .select(coverage_columns)
                .unique()
                .sort(["target_species_taxid", "target_uniprot"])
                .to_dicts()
            )

            if not coverage_rows:
                rows.append(
                    {
                        "complex_id": complex_id,
                        "pdb_id": pdb_id,
                        "chain": chain,
                        "source_uniprot": source_uniprot_str,
                        "target_uniprot": None,
                        "target_species": None,
                        "target_species_taxid": None,
                        "model_name": model_name,
                        "embedding_path": None,
                        "embedding_exists": False,
                        "audit_status": "missing_ortholog_coverage",
                    }
                )
                continue

            for coverage_row in coverage_rows:
                taxid = int(coverage_row["target_species_taxid"])
                path = expected_embedding_path(
                    output_dir=output_dir,
                    model_name=model_name,
                    complex_id=complex_id,
                    chain=chain,
                    taxid=taxid,
                )

                exists = path.exists()

                rows.append(
                    {
                        "complex_id": complex_id,
                        "pdb_id": pdb_id,
                        "chain": chain,
                        "source_uniprot": source_uniprot_str,
                        "target_uniprot": coverage_row["target_uniprot"],
                        "target_species": coverage_row.get("target_species"),
                        "target_species_taxid": taxid,
                        "model_name": model_name,
                        "embedding_path": str(path),
                        "embedding_exists": exists,
                        "audit_status": "ok" if exists else "missing_embedding",
                    }
                )

    return pl.DataFrame(rows)


def main() -> None:
    args = parse_args()

    selection_path = Path(args.selection)
    coverage_path = Path(args.coverage)
    output_dir = Path(args.output_dir)
    output_path = Path(args.output)

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing selection CSV: {selection_path}")
    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing ortholog coverage CSV: {coverage_path}")

    selection = pl.read_csv(selection_path)
    coverage = pl.read_csv(coverage_path)

    audit = build_embedding_audit(
        selection=selection,
        coverage=coverage,
        output_dir=output_dir,
        model_name=args.model_name,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit.write_csv(output_path)

    print(f"Wrote missing embedding audit -> {output_path}")
    print()
    print("selection:", selection_path)
    print("coverage:", coverage_path)
    print("output dir:", output_dir)
    print("model name:", args.model_name)
    print("selection rows:", selection.height)
    print("audit rows:", audit.height)
    print()
    print("Audit status counts:")
    print(audit.group_by("audit_status").len().sort("audit_status"))

    missing = audit.filter(pl.col("audit_status") != "ok")

    if missing.is_empty():
        print()
        print("All expected embeddings are present.")
        return

    print()
    print("Missing / incomplete preview:")
    print(
        missing.select(
            [
                "complex_id",
                "pdb_id",
                "chain",
                "source_uniprot",
                "target_uniprot",
                "target_species",
                "target_species_taxid",
                "audit_status",
                "embedding_path",
            ]
        )
    )


if __name__ == "__main__":
    main()
