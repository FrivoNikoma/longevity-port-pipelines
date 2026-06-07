from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.load_pinder import load_pinder_index, select_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate Biohub embedding calls for selected PINDER complexes."
    )
    parser.add_argument(
        "--candidate-set",
        default=None,
        help="Optional candidate set name from data/config/candidate_sets.yaml.",
    )
    parser.add_argument(
        "--selection-mode",
        default="partner_aware",
        choices=["partner_aware", "explicit_only"],
        help="Candidate UniProt selection mode.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Disable unfiltered fallback when no candidate-set complexes are found.",
    )
    parser.add_argument(
        "--selection-count",
        type=int,
        default=10,
        help="Maximum number of selected complexes.",
    )
    parser.add_argument(
        "--selection",
        default="data/output/selection.csv",
        help="Selection CSV path used when --candidate-set is not provided.",
    )
    parser.add_argument(
        "--coverage",
        default="data/output/ortholog_coverage.csv",
        help="Ortholog coverage CSV path.",
    )
    return parser.parse_args()


def load_selection(args: argparse.Namespace) -> pl.DataFrame:
    if args.candidate_set is None:
        selection_path = Path(args.selection)
        if not selection_path.exists():
            raise FileNotFoundError(f"Missing selection CSV: {selection_path}")
        return pl.read_csv(selection_path)

    cfg = PipelineConfig(
        candidate_set=args.candidate_set,
        candidate_selection_mode=args.selection_mode,
        allow_unfiltered_fallback=not args.strict,
        selection_count=args.selection_count,
    )
    lf = load_pinder_index(cfg)
    return select_candidates(lf, cfg).collect()


def main() -> None:
    args = parse_args()

    selection = load_selection(args)

    coverage_path = Path(args.coverage)
    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing ortholog coverage CSV: {coverage_path}")

    coverage = pl.read_csv(coverage_path)

    total_pairs = 0
    api_calls = 0
    rows: list[tuple[str, str, str, int]] = []
    missing_coverage: list[tuple[str, str, str]] = []

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
                rows.append((complex_id, chain, str(uniprot), n))
                total_pairs += n
                api_calls += 2 * n
            else:
                missing_coverage.append((complex_id, chain, str(uniprot)))

    print("candidate set:", args.candidate_set or "<selection file>")
    print("selection mode:", args.selection_mode if args.candidate_set else "<not used>")
    print("strict mode:", args.strict if args.candidate_set else "<not used>")
    print("complexes:", selection.height)
    print("embedding pairs:", total_pairs)
    print("estimated Biohub API calls:", api_calls)
    print()

    print("first selected complexes:")
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
        ).head(20)
    )
    print()

    print("first embedding rows:")
    for item in rows[:30]:
        print(item)

    print()
    print("missing ortholog coverage rows:", len(missing_coverage))
    for item in missing_coverage[:50]:
        print(item)


if __name__ == "__main__":
    main()
