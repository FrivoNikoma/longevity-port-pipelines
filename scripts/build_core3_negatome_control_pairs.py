from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.negatome_curation import (
    build_core3_negatome_control_pairs,
    validate_curated_sequences,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build curated core3-expanded NEGATOME control pairs for viewer cases."
    )
    parser.add_argument(
        "--viewer-selections",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.csv",
        help="Viewer-ready structure selections CSV.",
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_mini_pilot_v2_core3_expanded_selection.csv",
        help="Core3-expanded selection CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/interim/negatome_control_pairs.csv",
        help="Output curated NEGATOME control pairs CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    viewer_path = Path(args.viewer_selections)
    selection_path = Path(args.selection)
    output_path = Path(args.output)

    if not viewer_path.exists():
        raise FileNotFoundError(f"Missing viewer selections CSV: {viewer_path}")
    if not selection_path.exists():
        raise FileNotFoundError(f"Missing selection CSV: {selection_path}")

    cfg = PipelineConfig()
    cfg.ensure_dirs()
    cache_dir = cfg.interim_dir / "uniprot_sequences"

    pairs = build_core3_negatome_control_pairs(
        viewer_selections=pl.read_csv(viewer_path),
        selection=pl.read_csv(selection_path),
        cache_dir=cache_dir,
    )
    validate_curated_sequences(pairs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pairs.write_csv(output_path)

    print(f"Wrote {pairs.height} curated NEGATOME control pairs -> {output_path}")
    for row in pairs.select(
        [
            "complex_id",
            "chain",
            "target_species",
            "source_uniprot",
            "negative_partner_uniprot",
        ]
    ).iter_rows(named=True):
        print(
            f"  {row['complex_id']} / {row['chain']} / {row['target_species']} "
            f"-> {row['source_uniprot']} x {row['negative_partner_uniprot']}"
        )


if __name__ == "__main__":
    main()
