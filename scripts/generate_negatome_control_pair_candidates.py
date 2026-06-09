from __future__ import annotations

import argparse
from pathlib import Path

from longevity_port_pipelines.stages.negatome_seed import (
    build_negatome_control_pair_candidates,
    read_table,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a curation scaffold for future NEGATOME-style negative-control pairs "
            "from mini-pilot residue-delta outputs."
        )
    )
    parser.add_argument(
        "--residue-deltas",
        default="data/output/sirt6_mini_pilot_residue_deltas_mapped.parquet",
        help="Input mapped residue-delta parquet or CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_negatome_control_pair_candidates.csv",
        help="Output candidate negative-control pair scaffold CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    residue_delta_path = Path(args.residue_deltas)
    output_path = Path(args.output)

    residue_deltas = read_table(residue_delta_path)
    candidates = build_negatome_control_pair_candidates(residue_deltas)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    candidates.write_csv(output_path)

    print(f"Wrote NEGATOME-style control pair candidates -> {output_path}")
    print()
    print("Candidate table shape:")
    print(candidates.shape)

    print()
    print("Readiness counts:")
    print(
        candidates.group_by(["ready_for_input_contract", "negative_partner_source"])
        .len()
        .sort("len", descending=True)
    )

    print()
    print("Candidate preview:")
    print(candidates)


if __name__ == "__main__":
    main()
