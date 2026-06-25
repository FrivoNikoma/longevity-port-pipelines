"""Dry-run preflight for explicit PINDER candidate cofolding baselines.

This stage prepares receptor/ligand PINDER-fragment sequences for one exact
biologically selected candidate id. It is deliberately dry-run only: it does
not create a Boltz client, does not submit predictions, and does not write
runtime output files.

The goal is to inspect whether a candidate human/technical baseline input is
well-formed before any live Boltz spending happens in a later, explicit PR.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import typer

from longevity_port_pipelines.stages.cofolding_baseline_controls import (
    load_pinder_fragment_sequences,
)

app = typer.Typer(help="Dry-run explicit PINDER candidate baseline inputs.")

DEFAULT_PINDER_DATA_DIR = Path("data/interim/pinder/data")
SHORT_FRAGMENT_WARNING_THRESHOLD = 30

PINDER_DATA_DIR_OPTION = typer.Option(
    DEFAULT_PINDER_DATA_DIR,
    "--pinder-data-dir",
    help="Directory containing PINDER parquet files.",
)

CANDIDATE_ID_OPTION = typer.Option(
    ...,
    "--candidate-id",
    help="Exact PINDER candidate id to prepare, e.g. 1nfi__A1_Q04206--1nfi__F1_P25963.",
)

SHORT_FRAGMENT_THRESHOLD_OPTION = typer.Option(
    SHORT_FRAGMENT_WARNING_THRESHOLD,
    "--short-fragment-threshold",
    help="Warn when either PINDER fragment is shorter than this many residues.",
)


def parse_pinder_candidate_id(candidate_id: str) -> dict[str, str]:
    """Parse a PINDER candidate id into PDB, chain, and UniProt fields."""
    halves = candidate_id.split("--", 1)
    if len(halves) != 2:
        raise ValueError(f"Invalid PINDER candidate id: {candidate_id}")

    left = parse_pinder_side(halves[0], side_name="receptor")
    right = parse_pinder_side(halves[1], side_name="ligand")

    return {
        "pdb_id": left["pdb_id"],
        "receptor_chain": left["chain_id"],
        "receptor_uniprot": left["uniprot"],
        "ligand_chain": right["chain_id"],
        "ligand_uniprot": right["uniprot"],
    }


def parse_pinder_side(side: str, *, side_name: str) -> dict[str, str]:
    """Parse one side of a PINDER id, e.g. 1nfi__A1_Q04206."""
    match = re.fullmatch(
        r"(?P<pdb_id>[A-Za-z0-9]+)__(?P<chain_id>[^_]+)_(?P<uniprot>[A-Z0-9]{6,10})",
        side,
    )
    if match is None:
        raise ValueError(f"Invalid {side_name} side in PINDER candidate id: {side}")

    return {
        "pdb_id": match.group("pdb_id").lower(),
        "chain_id": match.group("chain_id"),
        "uniprot": match.group("uniprot"),
    }


def prepare_candidate_baseline_input(
    pinder_data_dir: Path,
    candidate_id: str,
) -> dict[str, Any]:
    """Prepare one explicit PINDER candidate baseline input."""
    parsed = parse_pinder_candidate_id(candidate_id)
    sequences_by_id = load_pinder_fragment_sequences(pinder_data_dir, [candidate_id])

    if candidate_id not in sequences_by_id:
        raise RuntimeError(f"Missing PINDER sequences for candidate id: {candidate_id}")

    return {
        "id": candidate_id,
        **parsed,
        **sequences_by_id[candidate_id],
    }


def print_dry_run(row: dict[str, Any], *, short_fragment_threshold: int) -> None:
    """Print a dry-run summary without calling Boltz or writing output files."""
    typer.echo("[DRY RUN] Prepared 1 PINDER candidate baseline.")
    typer.echo("")
    typer.echo(f"id: {row['id']}")
    typer.echo(f"pdb: {row['pdb_id']}")
    typer.echo(f"receptor: {row['receptor_uniprot']} chain={row['receptor_chain']}")
    typer.echo(f"ligand: {row['ligand_uniprot']} chain={row['ligand_chain']}")
    typer.echo(f"receptor_length: {row['pinder_receptor_len']}")
    typer.echo(f"ligand_length: {row['pinder_ligand_len']}")

    if int(row["pinder_receptor_len"]) < short_fragment_threshold:
        typer.echo(
            f"WARNING: receptor fragment is short "
            f"(<{short_fragment_threshold} residues); live interpretation may be fragile."
        )

    if int(row["pinder_ligand_len"]) < short_fragment_threshold:
        typer.echo(
            f"WARNING: ligand fragment is short "
            f"(<{short_fragment_threshold} residues); live interpretation may be fragile."
        )

    typer.echo("")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No runtime output files were written.")


@app.command()
def main(
    candidate_id: str = CANDIDATE_ID_OPTION,
    pinder_data_dir: Path = PINDER_DATA_DIR_OPTION,
    short_fragment_threshold: int = SHORT_FRAGMENT_THRESHOLD_OPTION,
) -> None:
    """Dry-run one explicit biologically selected PINDER candidate baseline."""
    row = prepare_candidate_baseline_input(pinder_data_dir, candidate_id)
    print_dry_run(row, short_fragment_threshold=short_fragment_threshold)


if __name__ == "__main__":
    app()
