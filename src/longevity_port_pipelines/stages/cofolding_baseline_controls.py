"""Run Boltz baselines for audited PINDER cofolding controls.

This stage consumes the local CSV produced by `cofolding-controls`, extracts the
corresponding PINDER receptor/ligand fragment sequences, and either prints a
dry-run plan or submits a small number of human-human/technical control
baselines to Boltz.

The default mode is safe: no Boltz calls are made unless `--yes-live` is passed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl
import typer

from longevity_port_pipelines.stages import cofolding

app = typer.Typer(help="Run PINDER-fragment Boltz baselines for audited controls.")

DEFAULT_AUDIT_INPUT = Path("data/output/pinder_cofolding_control_audit.csv")
DEFAULT_PINDER_DATA_DIR = Path("data/interim/pinder/data")
DEFAULT_OUTPUT = Path("data/output/cofolding_control_baseline_results.parquet")

AUDIT_INPUT_OPTION = typer.Option(
    DEFAULT_AUDIT_INPUT,
    "--audit-input",
    help="CSV produced by `uv run cofolding-controls`.",
)
PINDER_DATA_DIR_OPTION = typer.Option(
    DEFAULT_PINDER_DATA_DIR,
    "--pinder-data-dir",
    help="Directory containing PINDER parquet files.",
)
OUTPUT_OPTION = typer.Option(
    DEFAULT_OUTPUT,
    "--output",
    help="Parquet output path for live Boltz baseline results.",
)
CONTROL_KIND_OPTION = typer.Option(
    "human_heterodimer",
    "--control-kind",
    help="Control kind: human_heterodimer, technical_homomer, or all.",
)
TOP_N_OPTION = typer.Option(
    2,
    "--top-n",
    help="Number of audited controls to prepare/run.",
)
NUM_SAMPLES_OPTION = typer.Option(
    3,
    "--num-samples",
    help="Boltz samples per prediction.",
)
YES_LIVE_OPTION = typer.Option(
    False,
    "--yes-live",
    help="Actually submit selected controls to Boltz. Omit for dry-run mode.",
)

CONTROL_KIND_TO_FLAG: dict[str, str | None] = {
    "human_heterodimer": "human_heterodimer_control",
    "technical_homomer": "technical_homomer_control",
    "all": None,
}


def require_columns(df: pl.DataFrame, columns: set[str], *, source: str) -> None:
    """Raise if a dataframe is missing required columns."""
    missing = sorted(columns - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def load_audit(path: Path) -> pl.DataFrame:
    """Load the cofolding-control audit CSV."""
    if not path.exists():
        raise FileNotFoundError(
            f"Audit file not found: {path}. Run `uv run cofolding-controls` first."
        )

    df = pl.read_csv(path)
    require_columns(
        df,
        {
            "id",
            "probability",
            "buried_sasa",
            "intermolecular_contacts",
            "receptor_len",
            "ligand_len",
            "receptor_uniprot",
            "ligand_uniprot",
            "human_heterodimer_control",
            "technical_homomer_control",
        },
        source=str(path),
    )
    return df


def filter_control_candidates(audit: pl.DataFrame, *, control_kind: str) -> pl.DataFrame:
    """Filter audited rows to the requested control kind."""
    if control_kind not in CONTROL_KIND_TO_FLAG:
        allowed = ", ".join(sorted(CONTROL_KIND_TO_FLAG))
        raise ValueError(f"Unknown control kind: {control_kind}. Allowed: {allowed}")

    flag_column = CONTROL_KIND_TO_FLAG[control_kind]
    candidates = audit

    if flag_column is not None:
        candidates = candidates.filter(pl.col(flag_column))

    return candidates.sort(["probability", "buried_sasa"], descending=True)


def load_pinder_fragment_sequences(
    pinder_data_dir: Path,
    ids: list[str],
) -> dict[str, dict[str, Any]]:
    """Load PINDER receptor/ligand fragment sequences for selected ids."""
    wanted = set(ids)
    found: dict[str, dict[str, Any]] = {}

    for path in pinder_data_dir.glob("*.parquet"):
        if not wanted:
            break

        df = pl.read_parquet(path)
        require_columns(
            df,
            {"id", "receptor_sequence", "ligand_sequence"},
            source=str(path),
        )

        hits = df.filter(pl.col("id").is_in(sorted(wanted)))

        for row in hits.iter_rows(named=True):
            pinder_id = str(row["id"])
            receptor_sequence = str(row["receptor_sequence"])
            ligand_sequence = str(row["ligand_sequence"])

            found[pinder_id] = {
                "receptor_sequence": receptor_sequence,
                "ligand_sequence": ligand_sequence,
                "pinder_receptor_len": len(receptor_sequence),
                "pinder_ligand_len": len(ligand_sequence),
            }
            wanted.remove(pinder_id)

    return found


def prepare_baseline_inputs(
    audit_input: Path,
    pinder_data_dir: Path,
    *,
    control_kind: str,
    top_n: int,
) -> list[dict[str, Any]]:
    """Prepare PINDER-fragment baseline inputs from audited controls."""
    audit = load_audit(audit_input)
    candidates = filter_control_candidates(audit, control_kind=control_kind).head(top_n)

    if candidates.is_empty():
        return []

    candidate_rows = [dict(row) for row in candidates.iter_rows(named=True)]
    ids = [str(row["id"]) for row in candidate_rows]
    sequences_by_id = load_pinder_fragment_sequences(pinder_data_dir, ids)

    missing = sorted(set(ids) - set(sequences_by_id))
    if missing:
        raise RuntimeError(f"Missing PINDER sequences for selected ids: {missing}")

    prepared: list[dict[str, Any]] = []
    for row in candidate_rows:
        pinder_id = str(row["id"])
        sequence_record = sequences_by_id[pinder_id]

        prepared.append(
            {
                **row,
                **sequence_record,
                "control_kind": control_kind,
                "baseline_type": f"pinder_fragment_{control_kind}",
            }
        )

    return prepared


def print_dry_run(inputs: list[dict[str, Any]], *, num_samples: int) -> None:
    """Print selected baseline controls without calling Boltz."""
    typer.echo(f"[DRY RUN] Prepared {len(inputs)} baseline control(s).")
    for row in inputs:
        typer.echo(
            "  -> "
            f"{row['id']} "
            f"({row['control_kind']}; "
            f"probability={float(row['probability']):.3f}; "
            f"buried_sasa={float(row['buried_sasa']):.1f})"
        )
        typer.echo(
            "     "
            f"receptor={row['receptor_uniprot']} len={row['pinder_receptor_len']}  "
            f"ligand={row['ligand_uniprot']} len={row['pinder_ligand_len']}  "
            f"num_samples={num_samples}"
        )

    typer.echo("No Boltz API calls were made.")


def run_live_baselines(
    inputs: list[dict[str, Any]],
    *,
    output: Path,
    num_samples: int,
) -> pl.DataFrame:
    """Submit selected PINDER-fragment baseline controls to Boltz."""
    client = cofolding.get_boltz_client()
    result_rows: list[dict[str, Any]] = []

    for row in inputs:
        typer.echo("\n" + "=" * 100)
        typer.echo(f"PINDER-fragment baseline control: {row['id']}")
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
        binding_confidence = api_result["binding_confidence"]
        classification = cofolding.classify_interaction(iptm, binding_confidence)

        result_row = {
            "id": row["id"],
            "control_kind": row["control_kind"],
            "baseline_type": row["baseline_type"],
            "receptor_uniprot": row["receptor_uniprot"],
            "ligand_uniprot": row["ligand_uniprot"],
            "pinder_receptor_len": row["pinder_receptor_len"],
            "pinder_ligand_len": row["pinder_ligand_len"],
            "probability": row["probability"],
            "buried_sasa": row["buried_sasa"],
            "intermolecular_contacts": row["intermolecular_contacts"],
            "num_samples": num_samples,
            "boltz_classification": classification,
            **api_result,
        }
        result_rows.append(result_row)

        typer.echo(
            f"iptm={iptm:.3f}  "
            + (
                f"binding_conf={float(binding_confidence):.3f}  "
                if binding_confidence is not None
                else ""
            )
            + f"-> {classification}"
        )

    out_df = pl.DataFrame(result_rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    out_df.write_parquet(output)
    out_df.write_csv(output.with_suffix(".csv"))

    typer.echo("\nSaved baseline results to:")
    typer.echo(str(output))
    typer.echo(str(output.with_suffix(".csv")))

    return out_df


@app.command()
def main(
    audit_input: Path = AUDIT_INPUT_OPTION,
    pinder_data_dir: Path = PINDER_DATA_DIR_OPTION,
    output: Path = OUTPUT_OPTION,
    control_kind: str = CONTROL_KIND_OPTION,
    top_n: int = TOP_N_OPTION,
    num_samples: int = NUM_SAMPLES_OPTION,
    yes_live: bool = YES_LIVE_OPTION,
) -> None:
    """Prepare or run PINDER-fragment Boltz baselines for audited controls."""
    inputs = prepare_baseline_inputs(
        audit_input,
        pinder_data_dir,
        control_kind=control_kind,
        top_n=top_n,
    )

    if not inputs:
        typer.echo(f"No controls found for control_kind={control_kind!r}.")
        raise typer.Exit(0)

    if not yes_live:
        print_dry_run(inputs, num_samples=num_samples)
        raise typer.Exit(0)

    run_live_baselines(inputs, output=output, num_samples=num_samples)


if __name__ == "__main__":
    app()
