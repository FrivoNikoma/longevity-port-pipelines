from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.config import TARGET_SPECIES, PipelineConfig
from longevity_port_pipelines.models import OrthologMapping
from longevity_port_pipelines.stages.fetch_orthologs import fetch_ortholog
from longevity_port_pipelines.stages.load_pinder import load_pinder_index, select_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch ortholog coverage for a candidate-set driven PINDER selection."
    )
    parser.add_argument(
        "--candidate-set",
        default="sirt6_dna_repair",
        help="Candidate set name from data/config/candidate_sets.yaml.",
    )
    parser.add_argument(
        "--selection-mode",
        default="explicit_only",
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
        "--output-coverage",
        default=None,
        help="Output ortholog coverage CSV path.",
    )
    parser.add_argument(
        "--output-selection",
        default=None,
        help="Optional output selected-complexes CSV path.",
    )
    return parser.parse_args()


def default_output_stem(candidate_set: str, selection_mode: str) -> str:
    return f"{candidate_set}_{selection_mode}"


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


def write_coverage(mappings: list[OrthologMapping], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [mapping.model_dump() for mapping in mappings]
    df = pl.DataFrame(rows) if rows else pl.DataFrame()
    df.write_csv(output_path)


def main() -> None:
    args = parse_args()

    cfg = PipelineConfig(
        candidate_set=args.candidate_set,
        candidate_selection_mode=args.selection_mode,
        allow_unfiltered_fallback=not args.strict,
        selection_count=args.selection_count,
    )
    cfg.ensure_dirs()

    stem = default_output_stem(args.candidate_set, args.selection_mode)
    coverage_path = (
        Path(args.output_coverage)
        if args.output_coverage is not None
        else cfg.output_dir / f"{stem}_ortholog_coverage.csv"
    )
    selection_path = (
        Path(args.output_selection)
        if args.output_selection is not None
        else cfg.output_dir / f"{stem}_selection.csv"
    )

    lf = load_pinder_index(cfg)
    selection = select_candidates(lf, cfg).collect()

    selection.write_csv(selection_path)

    uniprots = selected_uniprots(selection)

    mappings: list[OrthologMapping] = []
    missing: list[tuple[str, int, str]] = []

    for uniprot_id in uniprots:
        for target in TARGET_SPECIES:
            mapping = fetch_ortholog(uniprot_id, target)
            if mapping is None:
                missing.append((uniprot_id, target.taxid, target.name))
                continue
            mappings.append(mapping)

    write_coverage(mappings, coverage_path)

    print("candidate set:", args.candidate_set)
    print("selection mode:", args.selection_mode)
    print("strict mode:", args.strict)
    print("selected complexes:", selection.height)
    print("unique source UniProt IDs:", len(uniprots))
    print("target species:", [species.name for species in TARGET_SPECIES])
    print("ortholog mappings:", len(mappings))
    print("missing mappings:", len(missing))
    print()
    print("selected UniProt IDs:")
    for uniprot_id in uniprots:
        print(uniprot_id)

    print()
    print("first mappings:")
    for mapping in mappings[:30]:
        print(
            mapping.source_uniprot,
            "->",
            mapping.target_species_taxid,
            mapping.target_uniprot,
            mapping.source_db,
            "reviewed=",
            mapping.is_reviewed,
        )

    print()
    print("first missing:")
    for item in missing[:30]:
        print(item)

    print()
    print(f"Wrote selection -> {selection_path}")
    print(f"Wrote ortholog coverage -> {coverage_path}")


if __name__ == "__main__":
    main()
