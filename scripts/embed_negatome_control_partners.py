from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.embed import get_biohub_token
from longevity_port_pipelines.stages.negatome_controls import (
    embed_negatome_control_partners,
    load_negatome_control_pairs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embed curated NEGATOME-style negative-control partner sequences."
    )
    parser.add_argument(
        "--negatome-pairs",
        default="data/interim/negatome_control_pairs.csv",
        help="Curated negative-control partner CSV.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    cfg = PipelineConfig()
    cfg.ensure_dirs()

    pairs = load_negatome_control_pairs(Path(args.negatome_pairs))
    if pairs is None:
        raise FileNotFoundError(
            f"Missing NEGATOME control pairs file: {args.negatome_pairs}. "
            "See docs/negatome_control_inputs.md and data/input/negatome_control_pairs.example.csv."
        )

    token = get_biohub_token()
    embedded_count = embed_negatome_control_partners(pairs, cfg, token)

    print(f"Embedded {embedded_count} new negative partner sequences")
    print(f"Cache directory: {cfg.interim_dir / 'negatome_embeddings' / cfg.esmc_model}")


if __name__ == "__main__":
    main()
