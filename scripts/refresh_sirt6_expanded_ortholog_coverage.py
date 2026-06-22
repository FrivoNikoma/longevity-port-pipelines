from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from time import perf_counter
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
    parser.add_argument(
        "--only-uniprot",
        action="append",
        default=None,
        help=(
            "Restrict refresh to one or more source UniProt IDs. "
            "May be repeated or passed as a comma-separated list."
        ),
    )
    parser.add_argument(
        "--max-uniprots",
        type=int,
        default=None,
        help="Limit refresh to the first N selected source UniProt IDs.",
    )
    parser.add_argument(
        "--checkpoint-every-uniprots",
        type=int,
        default=1,
        help=(
            "Write partial coverage/missing outputs after every N source UniProt IDs. "
            "Use 0 to disable checkpoint writes."
        ),
    )
    parser.add_argument(
        "--quiet-progress",
        action="store_true",
        help="Suppress per-request progress logging.",
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


def parse_requested_uniprots(values: Sequence[str] | None) -> set[str]:
    if not values:
        return set()

    requested: set[str] = set()
    for value in values:
        requested.update(part.strip() for part in value.split(",") if part.strip())
    return requested


def restrict_uniprots(
    uniprots: Sequence[str],
    only_uniprots: Sequence[str] | None,
    max_uniprots: int | None,
) -> list[str]:
    selected = list(uniprots)
    requested = parse_requested_uniprots(only_uniprots)

    if requested:
        available = set(selected)
        missing = sorted(requested - available)
        if missing:
            raise ValueError(
                f"Requested UniProt IDs are not present in the selection CSV: {missing}"
            )
        selected = [uniprot_id for uniprot_id in selected if uniprot_id in requested]

    if max_uniprots is not None:
        if max_uniprots < 1:
            raise ValueError("--max-uniprots must be >= 1")
        selected = selected[:max_uniprots]

    return selected


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


def write_checkpoint(
    mappings: list[OrthologMapping],
    missing: list[dict[str, Any]],
    coverage_path: Path | None,
    missing_path: Path | None,
    *,
    progress: bool,
) -> None:
    if coverage_path is not None:
        write_coverage(mappings, coverage_path)
    if missing_path is not None:
        write_missing(missing, missing_path)
    if progress and (coverage_path is not None or missing_path is not None):
        print(
            f"  checkpoint written: {len(mappings)} mappings, {len(missing)} missing",
            flush=True,
        )


def fetch_ortholog_coverage(
    uniprots: Sequence[str],
    target_species: Sequence[Species],
    *,
    progress: bool = True,
    checkpoint_coverage_path: Path | None = None,
    checkpoint_missing_path: Path | None = None,
    checkpoint_every_uniprots: int = 0,
) -> tuple[list[OrthologMapping], list[dict[str, Any]]]:
    mappings: list[OrthologMapping] = []
    missing: list[dict[str, Any]] = []

    total_requests = len(uniprots) * len(target_species)
    request_index = 0

    for uniprot_index, uniprot_id in enumerate(uniprots, start=1):
        if progress:
            print(
                f"Source UniProt {uniprot_index}/{len(uniprots)}: {uniprot_id}",
                flush=True,
            )

        for target in target_species:
            request_index += 1
            started = perf_counter()

            if progress:
                print(
                    f"  [{request_index}/{total_requests}] "
                    f"{uniprot_id} -> {target.name} ({target.taxid}) ...",
                    flush=True,
                )

            mapping = fetch_ortholog(uniprot_id, target)
            seconds = perf_counter() - started

            if mapping is None:
                missing.append(
                    {
                        "source_uniprot": uniprot_id,
                        "target_species_taxid": target.taxid,
                        "target_species": target.name,
                        "reason": "no_ortholog_mapping",
                    }
                )
            else:
                mappings.append(mapping)

            if progress:
                status = "found" if mapping is not None else "missing"
                source_db = f", source_db={mapping.source_db}" if mapping else ""
                print(
                    f"    {status}{source_db}, seconds={seconds:.2f}",
                    flush=True,
                )

        if checkpoint_every_uniprots > 0 and uniprot_index % checkpoint_every_uniprots == 0:
            write_checkpoint(
                mappings,
                missing,
                checkpoint_coverage_path,
                checkpoint_missing_path,
                progress=progress,
            )

    return mappings, missing


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

    uniprots = restrict_uniprots(
        selected_uniprots(selection),
        args.only_uniprot,
        args.max_uniprots,
    )
    if not uniprots:
        raise ValueError("No source UniProt IDs selected for refresh")

    progress = not args.quiet_progress
    mappings, missing = fetch_ortholog_coverage(
        uniprots,
        TARGET_SPECIES,
        progress=progress,
        checkpoint_coverage_path=output_coverage,
        checkpoint_missing_path=output_missing,
        checkpoint_every_uniprots=args.checkpoint_every_uniprots,
    )

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
