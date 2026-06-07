from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.load_pinder import (
    load_candidate_set_uniprots,
    load_partner_aware_uniprots,
    load_pinder_index,
    select_candidates,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit why PINDER complexes were selected for a candidate set."
    )
    parser.add_argument(
        "--candidate-set",
        default="ampk_pilot",
        help="Candidate set name from data/config/candidate_sets.yaml.",
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
        "--output",
        default=None,
        help="Optional output CSV path. Defaults to data/output/<candidate_set>_selection_audit.csv.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    cfg = PipelineConfig(
        candidate_set=args.candidate_set,
        candidate_selection_mode=args.selection_mode,
        allow_unfiltered_fallback=not args.strict,
        selection_count=args.selection_count,
    )
    cfg.ensure_dirs()

    explicit_uniprots = load_candidate_set_uniprots(cfg)
    expanded_uniprots = load_partner_aware_uniprots(cfg)

    lf = load_pinder_index(cfg)
    selected = select_candidates(lf, cfg).collect()

    output_path = (
        Path(args.output)
        if args.output is not None
        else cfg.output_dir / f"{args.candidate_set}_selection_audit.csv"
    )

    if selected.is_empty():
        print(f"No complexes selected for candidate set: {args.candidate_set}")
        print(f"selection mode: {args.selection_mode}")
        print(f"strict mode: {args.strict}")
        print(f"explicit UniProt IDs: {sorted(explicit_uniprots)}")
        print(f"expanded UniProt IDs: {sorted(expanded_uniprots)}")
        selected.write_csv(output_path)
        print(f"Wrote empty audit table -> {output_path}")
        return

    explicit_sorted = sorted(explicit_uniprots)
    expanded_sorted = sorted(expanded_uniprots)

    audit = selected.with_columns(
        pl.col("uniprot_R").is_in(explicit_sorted).alias("R_is_explicit_uniprot"),
        pl.col("uniprot_L").is_in(explicit_sorted).alias("L_is_explicit_uniprot"),
        pl.col("uniprot_R").is_in(expanded_sorted).alias("R_is_expanded_uniprot"),
        pl.col("uniprot_L").is_in(expanded_sorted).alias("L_is_expanded_uniprot"),
    ).with_columns(
        (pl.col("R_is_explicit_uniprot") | pl.col("L_is_explicit_uniprot")).alias(
            "matches_explicit_candidate_set"
        ),
        (pl.col("R_is_expanded_uniprot") | pl.col("L_is_expanded_uniprot")).alias(
            "matches_expanded_partner_aware_set"
        ),
    )

    audit = audit.select(
        [
            "id",
            "pdb_id",
            "chain_R",
            "uniprot_R",
            "chain_L",
            "uniprot_L",
            "intermolecular_contacts",
            "predicted_R",
            "predicted_L",
            "R_is_explicit_uniprot",
            "L_is_explicit_uniprot",
            "R_is_expanded_uniprot",
            "L_is_expanded_uniprot",
            "matches_explicit_candidate_set",
            "matches_expanded_partner_aware_set",
        ]
    )

    audit.write_csv(output_path)

    print(f"Candidate set: {args.candidate_set}")
    print(f"selection mode: {args.selection_mode}")
    print(f"strict mode: {args.strict}")
    print(f"selected complexes: {audit.height}")
    print(f"explicit UniProt IDs: {sorted(explicit_uniprots)}")
    print(f"expanded UniProt IDs: {sorted(expanded_uniprots)}")
    print()
    print(audit)
    print()
    print(f"Wrote audit table -> {output_path}")


if __name__ == "__main__":
    main()
