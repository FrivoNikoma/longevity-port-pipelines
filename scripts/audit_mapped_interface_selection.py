from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl
from scripts.analyze_saved_embeddings_mapped import (
    best_spatial_chain_pair,
    chain_match_candidates,
    chain_sequences,
    download_structure,
)

from longevity_port_pipelines.config import PipelineConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit mapped interface chain-pair selection for a mini-pilot selection CSV."
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_mini_pilot_selection.csv",
        help="Input mini-pilot selection CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_chain_pair_qc.csv",
        help="Output chain-pair QC CSV.",
    )
    parser.add_argument(
        "--distance-cutoff",
        type=float,
        default=8.0,
        help="Atom distance cutoff in Angstrom for interface/contact detection.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.8,
        help="Minimum sequence-match score for candidate chain matching.",
    )
    return parser.parse_args()


def audit_row(
    row: dict[str, object],
    cfg: PipelineConfig,
    distance_cutoff: float,
    min_score: float,
) -> dict[str, object]:
    pdb_id = str(row["pdb_id"])
    complex_id = str(row["id"])

    structure_path, fmt = download_structure(pdb_id, cfg.interim_dir / "pdb")
    chains = chain_sequences(structure_path, fmt)

    receptor_candidates = chain_match_candidates(
        str(row["receptor_sequence"]),
        chains,
        min_score=min_score,
    )
    ligand_candidates = chain_match_candidates(
        str(row["ligand_sequence"]),
        chains,
        min_score=min_score,
    )

    base = {
        "complex_id": complex_id,
        "pdb_id": pdb_id,
        "structure_format": fmt,
        "pinder_chain_R": row["chain_R"],
        "pinder_chain_L": row["chain_L"],
        "uniprot_R": row["uniprot_R"],
        "uniprot_L": row["uniprot_L"],
        "n_receptor_candidates": len(receptor_candidates),
        "n_ligand_candidates": len(ligand_candidates),
        "receptor_candidates": ";".join(
            f"{chain}:{score:.3f}" for chain, score in receptor_candidates
        ),
        "ligand_candidates": ";".join(f"{chain}:{score:.3f}" for chain, score in ligand_candidates),
    }

    if not receptor_candidates or not ligand_candidates:
        return {
            **base,
            "selected_chain_R": None,
            "selected_chain_L": None,
            "sequence_score_R": None,
            "sequence_score_L": None,
            "interface_R": 0,
            "interface_L": 0,
            "atom_contacts": 0,
            "status": "no_sequence_candidates",
            "error": None,
        }

    try:
        (
            selected_r,
            selected_l,
            score_r,
            score_l,
            interface_r,
            interface_l,
            atom_contacts,
        ) = best_spatial_chain_pair(
            structure_path=structure_path,
            fmt=fmt,
            chains=chains,
            receptor_sequence=str(row["receptor_sequence"]),
            ligand_sequence=str(row["ligand_sequence"]),
            distance_cutoff=distance_cutoff,
            min_score=min_score,
        )
    except Exception as exc:
        return {
            **base,
            "selected_chain_R": None,
            "selected_chain_L": None,
            "sequence_score_R": None,
            "sequence_score_L": None,
            "interface_R": 0,
            "interface_L": 0,
            "atom_contacts": 0,
            "status": "error",
            "error": str(exc),
        }

    status = "ok" if atom_contacts > 0 else "no_spatial_contacts"

    return {
        **base,
        "selected_chain_R": selected_r,
        "selected_chain_L": selected_l,
        "sequence_score_R": score_r,
        "sequence_score_L": score_l,
        "interface_R": interface_r,
        "interface_L": interface_l,
        "atom_contacts": atom_contacts,
        "status": status,
        "error": None,
    }


def main() -> None:
    args = parse_args()

    cfg = PipelineConfig()
    cfg.ensure_dirs()

    selection_path = Path(args.selection)
    out_path = Path(args.output)

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing selection CSV: {selection_path}")

    selection = pl.read_csv(selection_path)

    rows = [
        audit_row(
            row=row,
            cfg=cfg,
            distance_cutoff=args.distance_cutoff,
            min_score=args.min_score,
        )
        for row in selection.iter_rows(named=True)
    ]

    df = pl.DataFrame(rows).sort(
        ["status", "atom_contacts"],
        descending=[False, True],
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(out_path)

    print(f"Wrote chain-pair QC -> {out_path}")
    print()
    print(
        df.select(
            [
                "complex_id",
                "pdb_id",
                "pinder_chain_R",
                "pinder_chain_L",
                "selected_chain_R",
                "selected_chain_L",
                "sequence_score_R",
                "sequence_score_L",
                "interface_R",
                "interface_L",
                "atom_contacts",
                "status",
            ]
        )
    )


if __name__ == "__main__":
    main()
