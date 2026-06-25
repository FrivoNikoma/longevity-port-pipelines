"""Dry-run and controlled live preflight for explicit PINDER candidate baselines.

This stage prepares receptor/ligand PINDER-fragment sequences for one exact
biologically selected candidate id. The default mode is deliberately dry-run
only: it does not create a Boltz client, does not submit predictions, and does
not write runtime output files.

Live execution is available only through an explicit `--yes-live` safety gate
and processes one exact candidate id per command.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import polars as pl
import typer

from longevity_port_pipelines.stages import cofolding
from longevity_port_pipelines.stages.cofolding_baseline_controls import (
    load_pinder_fragment_sequences,
    require_columns,
)

app = typer.Typer(help="Dry-run or live explicit PINDER candidate baseline inputs.")

DEFAULT_PINDER_DATA_DIR = Path("data/interim/pinder/data")
DEFAULT_OUTPUT = Path("data/output/cofolding_candidate_baseline_results.parquet")
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

OUTPUT_OPTION = typer.Option(
    DEFAULT_OUTPUT,
    "--output",
    help="Parquet output path for live candidate baseline results.",
)

NUM_SAMPLES_OPTION = typer.Option(
    1,
    "--num-samples",
    help="Boltz samples per prediction. Keep small for candidate baseline gates.",
)

YES_LIVE_OPTION = typer.Option(
    False,
    "--yes-live",
    help="Actually submit the selected candidate baseline to Boltz. Omit for dry-run mode.",
)

SKIP_EXISTING_OPTION = typer.Option(
    False,
    "--skip-existing",
    help="Skip candidate ids already present in the output CSV or parquet.",
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


def load_existing_candidate_results(output: Path) -> pl.DataFrame | None:
    """Load existing candidate baseline results from CSV or parquet output."""
    csv_output = output.with_suffix(".csv")

    if csv_output.exists():
        df = pl.read_csv(csv_output)
        source = csv_output
    elif output.exists():
        df = pl.read_parquet(output)
        source = output
    else:
        return None

    require_columns(df, {"id"}, source=str(source))
    return df


def load_existing_candidate_ids(output: Path) -> set[str]:
    """Load candidate baseline ids already present in prior outputs."""
    existing_results = load_existing_candidate_results(output)
    if existing_results is None:
        return set()

    return {str(value) for value in existing_results["id"].drop_nulls().to_list()}


def merge_candidate_baseline_results(
    new_results: pl.DataFrame,
    output: Path,
) -> pl.DataFrame:
    """Append live candidate baseline results while keeping one latest row per id."""
    existing_results = load_existing_candidate_results(output)

    if existing_results is None or existing_results.is_empty():
        return new_results

    return pl.concat(
        [existing_results, new_results],
        how="diagonal_relaxed",
    ).unique(subset=["id"], keep="last")


def run_live_candidate_baseline(
    row: dict[str, Any],
    *,
    output: Path,
    num_samples: int,
) -> pl.DataFrame:
    """Submit one explicit PINDER candidate baseline to Boltz and save results."""
    client = cofolding.get_boltz_client()

    typer.echo("\n" + "=" * 100)
    typer.echo(f"PINDER candidate baseline: {row['id']}")
    typer.echo(
        f"receptor={row['receptor_uniprot']} len={row['pinder_receptor_len']}  "
        f"ligand={row['ligand_uniprot']} len={row['pinder_ligand_len']}"
    )
    typer.echo(f"Submitting to Boltz: num_samples={num_samples}")

    api_result = cofolding.submit_ppi_prediction(
        client,
        str(row["receptor_sequence"]),
        str(row["ligand_sequence"]),
        num_samples=num_samples,
    )

    iptm = float(api_result["iptm"])
    binding_confidence_raw = api_result.get("binding_confidence")
    binding_confidence = (
        float(binding_confidence_raw) if binding_confidence_raw is not None else None
    )
    classification = cofolding.classify_interaction(iptm, binding_confidence)

    result_row = {
        "id": row["id"],
        "baseline_type": "pinder_fragment_candidate_human_baseline",
        "pdb_id": row["pdb_id"],
        "receptor_chain": row["receptor_chain"],
        "receptor_uniprot": row["receptor_uniprot"],
        "ligand_chain": row["ligand_chain"],
        "ligand_uniprot": row["ligand_uniprot"],
        "pinder_receptor_len": row["pinder_receptor_len"],
        "pinder_ligand_len": row["pinder_ligand_len"],
        "num_samples": num_samples,
        "boltz_classification": classification,
        **api_result,
    }

    new_df = pl.DataFrame([result_row])
    output.parent.mkdir(parents=True, exist_ok=True)
    out_df = merge_candidate_baseline_results(new_df, output)
    out_df.write_parquet(output)
    out_df.write_csv(output.with_suffix(".csv"))

    typer.echo(
        f"iptm={iptm:.3f}  "
        + (f"binding_conf={binding_confidence:.3f}  " if binding_confidence is not None else "")
        + f"-> {classification}"
    )
    typer.echo("\nSaved candidate baseline result to:")
    typer.echo(str(output))
    typer.echo(str(output.with_suffix(".csv")))

    return out_df


@app.command()
def main(
    candidate_id: str = CANDIDATE_ID_OPTION,
    pinder_data_dir: Path = PINDER_DATA_DIR_OPTION,
    output: Path = OUTPUT_OPTION,
    short_fragment_threshold: int = SHORT_FRAGMENT_THRESHOLD_OPTION,
    num_samples: int = NUM_SAMPLES_OPTION,
    yes_live: bool = YES_LIVE_OPTION,
    skip_existing: bool = SKIP_EXISTING_OPTION,
) -> None:
    """Dry-run or live-run one explicit biologically selected candidate baseline."""
    row = prepare_candidate_baseline_input(pinder_data_dir, candidate_id)

    if skip_existing and candidate_id in load_existing_candidate_ids(output):
        typer.echo(f"Skipped existing candidate baseline result: {candidate_id}")
        typer.echo("No Boltz API calls were made.")
        raise typer.Exit(0)

    if not yes_live:
        print_dry_run(row, short_fragment_threshold=short_fragment_threshold)
        raise typer.Exit(0)

    run_live_candidate_baseline(row, output=output, num_samples=num_samples)


if __name__ == "__main__":
    app()
