from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.models import OrthologMapping
from longevity_port_pipelines.pipeline import run_stage_5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run guarded Biohub embeddings for a saved selection + ortholog coverage."
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_mini_pilot_selection.csv",
        help="Selection CSV path.",
    )
    parser.add_argument(
        "--coverage",
        default="data/output/sirt6_mini_pilot_ortholog_coverage.csv",
        help="Ortholog coverage CSV path.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/output",
        help="Pipeline output directory where embeddings will be written.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Actually call Biohub. Without this flag, only a dry-run estimate is printed.",
    )
    return parser.parse_args()


def estimate_calls(
    selection: pl.DataFrame, coverage: pl.DataFrame
) -> tuple[int, int, list[tuple[str, str, str]]]:
    embedding_pairs = 0
    missing: list[tuple[str, str, str]] = []

    for row in selection.iter_rows(named=True):
        complex_id = str(row["id"])

        for chain, uniprot in [
            ("receptor", row["uniprot_R"]),
            ("ligand", row["uniprot_L"]),
        ]:
            n = (
                coverage.filter(pl.col("source_uniprot") == uniprot)
                .select(["source_uniprot", "target_uniprot", "target_species_taxid"])
                .unique()
                .height
            )

            if n:
                embedding_pairs += n
            else:
                missing.append((complex_id, chain, str(uniprot)))

    return embedding_pairs, 2 * embedding_pairs, missing


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

    embedding_pairs, api_calls, missing = estimate_calls(selection, coverage)

    print("selection:", selection_path)
    print("coverage:", coverage_path)
    print("output dir:", args.output_dir)
    print("complexes:", selection.height)
    print("embedding pairs:", embedding_pairs)
    print("estimated Biohub API calls:", api_calls)
    print("missing ortholog coverage rows:", len(missing))
    for item in missing[:30]:
        print(item)

    print()
    print("selected complexes:")
    print(
        selection.select(
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

    if not args.run:
        print()
        print("DRY RUN ONLY. Re-run with --run to call Biohub and write embeddings.")
        return

    cfg = PipelineConfig(output_dir=Path(args.output_dir))
    cfg.ensure_dirs()

    mappings = [OrthologMapping(**row) for row in coverage.to_dicts()]

    print()
    print("Running Biohub embeddings now...")
    embedding_pairs_out = run_stage_5(selection.lazy(), mappings, cfg)
    print(f"Finished. Embedded pairs: {len(embedding_pairs_out)}")
    print(f"Embeddings written under: {cfg.output_dir / 'embeddings'}")


if __name__ == "__main__":
    main()
