from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import polars as pl

from longevity_port_pipelines.config import TARGET_SPECIES
from longevity_port_pipelines.models import OrthologMapping, Species
from longevity_port_pipelines.stages.fetch_orthologs import fetch_ortholog

DEFAULT_SELECTION = "data/output/sirt6_mini_pilot_v2_expanded_selection.csv"
DEFAULT_OUTPUT_COVERAGE = "data/output/sirt6_mini_pilot_v2_expanded_ortholog_coverage.csv"
DEFAULT_OUTPUT_MISSING = "data/output/sirt6_mini_pilot_v2_expanded_missing_orthologs.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Refresh SIRT6 mini-pilot v2 expanded ortholog coverage from an "
            "existing expanded selection CSV using the current TARGET_SPECIES registry."
        )
    )
    parser.add_argument(
        "--selection",
        default=DEFAULT_SELECTION,
        help="Input SIRT6 mini-pilot v2 expanded selection CSV.",
    )
    parser.add_argument(
        "--output-coverage",
        default=DEFAULT_OUTPUT_COVERAGE,
        help="Output refreshed ortholog coverage CSV.",
    )
    parser.add_argument(
        "--output-missing",
        default=DEFAULT_OUTPUT_MISSING,
        help="Output missing ortholog audit CSV.",
    )
    return parser.parse_args()


def require_columns(frame: pl.DataFrame, required: set[str], path: Path) -> None:
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")


def selected_uniprots(selection: pl.DataFrame) -> list[str]:
    values: set[str] = set()

    for col in ["uniprot_R", "uniprot_L"]:
        if col in selection.columns:
            values.update(
                str(value).strip()
                for value in selection.get_column(col).to_list()
                if value is not None and str(value).strip()
            )

    return sorted(values)


def fetch_ortholog_coverage(
    uniprots: Sequence[str],
    target_species: Sequence[Species],
) -> tuple[list[OrthologMapping], list[dict[str, Any]]]:
    mappings: list[OrthologMapping] = []
    missing: list[dict[str, Any]] = []

    for uniprot_id in uniprots:
        for target in target_species:
            mapping = fetch_ortholog(uniprot_id, target)
            if mapping is None:
                missing.append(
                    {
                        "source_uniprot": uniprot_id,
                        "target_species_taxid": target.taxid,
                        "target_species": target.name,
                        "reason": "no_ortholog_mapping",
                    }
                )
                continue
            mappings.append(mapping)

    return mappings, missing


def write_coverage(mappings: list[OrthologMapping], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [mapping.model_dump() for mapping in mappings]
    df = pl.DataFrame(rows) if rows else pl.DataFrame()
    df.write_csv(output_path)


def write_missing(missing: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = (
        pl.DataFrame(missing)
        if missing
        else pl.DataFrame(
            schema={
                "source_uniprot": pl.Utf8,
                "target_species_taxid": pl.Int64,
                "target_species": pl.Utf8,
                "reason": pl.Utf8,
            }
        )
    )
    df.write_csv(output_path)


def coverage_summary(mappings: list[OrthologMapping]) -> pl.DataFrame:
    if not mappings:
        return pl.DataFrame(
            schema={
                "target_species_taxid": pl.Int64,
                "target_species": pl.Utf8,
                "row_count": pl.Int64,
            }
        )

    rows = [
        {
            "target_species_taxid": mapping.target_species_taxid,
            "target_species": next(
                (
                    species.name
                    for species in TARGET_SPECIES
                    if species.taxid == mapping.target_species_taxid
                ),
                "unknown",
            ),
        }
        for mapping in mappings
    ]
    return (
        pl.DataFrame(rows)
        .group_by(["target_species_taxid", "target_species"])
        .len()
        .rename({"len": "row_count"})
        .sort("target_species_taxid")
    )


def missing_summary(missing: list[dict[str, Any]]) -> pl.DataFrame:
    if not missing:
        return pl.DataFrame(
            schema={
                "target_species_taxid": pl.Int64,
                "target_species": pl.Utf8,
                "missing_count": pl.Int64,
            }
        )

    return (
        pl.DataFrame(missing)
        .group_by(["target_species_taxid", "target_species"])
        .len()
        .rename({"len": "missing_count"})
        .sort("target_species_taxid")
    )


def main() -> None:
    args = parse_args()

    selection_path = Path(args.selection)
    output_coverage = Path(args.output_coverage)
    output_missing = Path(args.output_missing)

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing expanded selection CSV: {selection_path}")

    selection = pl.read_csv(selection_path)
    require_columns(selection, {"uniprot_R", "uniprot_L"}, selection_path)

    uniprots = selected_uniprots(selection)
    mappings, missing = fetch_ortholog_coverage(uniprots, TARGET_SPECIES)

    write_coverage(mappings, output_coverage)
    write_missing(missing, output_missing)

    print("selection:", selection_path)
    print("selected complexes:", selection.height)
    print("unique source UniProt IDs:", len(uniprots))
    print("target species:", [species.name for species in TARGET_SPECIES])
    print("ortholog mappings:", len(mappings))
    print("missing mappings:", len(missing))
    print()
    print("Coverage by target species:")
    print(coverage_summary(mappings))
    print()
    print("Missing by target species:")
    print(missing_summary(missing))
    print()
    print(f"Wrote refreshed ortholog coverage -> {output_coverage}")
    print(f"Wrote missing ortholog audit -> {output_missing}")


if __name__ == "__main__":
    main()
