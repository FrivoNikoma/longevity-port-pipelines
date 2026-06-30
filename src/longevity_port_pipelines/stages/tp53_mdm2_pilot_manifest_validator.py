from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

EXPECTED_CANDIDATE_SET = "tp53_mdm2_elephant"
EXPECTED_BIOLOGICAL_MODE = "beneficial_breakage"
EXPECTED_BREAKAGE_INTERPRETATION_POLICY = "do_not_auto_classify_breakage_as_incompatibility"
EXPECTED_CLAIM_POLICY = "technical_checkpoint_no_claim"

DEFAULT_INPUT = Path("data/input/tp53_mdm2_pilot_manifest.csv")

REQUIRED_COLUMNS = (
    "candidate_set",
    "biological_mode",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "partner_uniprot",
    "target_species",
    "strict_contrast_gate_status",
    "contrast_checkpoint_policy",
    "cofolding_plan_status",
    "breakage_interpretation_policy",
    "claim_policy",
)

ALLOWED_STRICT_CONTRAST_GATE_STATUSES = frozenset(
    {
        "eligible_for_contrast_dry_run",
        "blocked_contrast_coverage",
        "blocked_baseline_input",
        "blocked_species_coverage",
        "blocked_strict_panel",
        "blocked_negatome_repair_policy",
        "blocked_negatome_controls",
    }
)

ALLOWED_COFOLDING_PLAN_STATUSES = frozenset(
    {
        "eligible_for_cofolding_dry_run",
        "blocked_by_contrast_gate",
        "blocked_pending_manual_review",
        "blocked_pending_negatome_repair",
        "blocked_pending_species_coverage_repair",
    }
)


app = typer.Typer(
    help=(
        "Validate TP53/MDM2 pilot manifest policy fields without live API calls "
        "or biological claims."
    )
)


def _missing_columns(frame: pl.DataFrame, required_columns: tuple[str, ...]) -> list[str]:
    return [column for column in required_columns if column not in frame.columns]


def _nonempty_string_mask(column: str) -> pl.Expr:
    return pl.col(column).cast(pl.String).str.strip_chars().ne("")


def _invalid_values(
    frame: pl.DataFrame,
    column: str,
    allowed_values: frozenset[str],
) -> list[str]:
    if column not in frame.columns:
        return []

    values = (
        frame.select(pl.col(column).cast(pl.String).str.strip_chars().alias(column))
        .filter(pl.col(column).is_not_null() & pl.col(column).ne(""))
        .unique()
        .sort(column)
        .get_column(column)
        .to_list()
    )

    return [value for value in values if value not in allowed_values]


def validate_tp53_mdm2_pilot_manifest(frame: pl.DataFrame) -> None:
    """Validate a TP53/MDM2 pilot manifest without interpreting it as biology."""

    missing = _missing_columns(frame, REQUIRED_COLUMNS)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    if frame.is_empty():
        return

    required_nonempty = (
        "candidate_set",
        "biological_mode",
        "candidate_id",
        "source_uniprot",
        "partner_uniprot",
        "target_species",
        "breakage_interpretation_policy",
        "claim_policy",
    )

    blank_columns = [
        column
        for column in required_nonempty
        if frame.filter(~_nonempty_string_mask(column)).height > 0
    ]
    if blank_columns:
        raise ValueError(f"Blank required fields: {', '.join(blank_columns)}")

    duplicate_keys = (
        frame.group_by(["candidate_id", "target_species", "chain"]).len().filter(pl.col("len") > 1)
    )
    if duplicate_keys.height:
        raise ValueError(
            "Duplicate TP53/MDM2 manifest keys found for candidate_id, target_species, chain"
        )

    candidate_sets = _invalid_values(
        frame,
        "candidate_set",
        frozenset({EXPECTED_CANDIDATE_SET}),
    )
    if candidate_sets:
        raise ValueError(
            "Invalid candidate_set values for TP53/MDM2 pilot manifest: "
            + ", ".join(candidate_sets)
        )

    biological_modes = _invalid_values(
        frame,
        "biological_mode",
        frozenset({EXPECTED_BIOLOGICAL_MODE}),
    )
    if biological_modes:
        raise ValueError(
            "Invalid biological_mode values for TP53/MDM2 pilot manifest: "
            + ", ".join(biological_modes)
        )

    breakage_policies = _invalid_values(
        frame,
        "breakage_interpretation_policy",
        frozenset({EXPECTED_BREAKAGE_INTERPRETATION_POLICY}),
    )
    if breakage_policies:
        raise ValueError(
            "Invalid breakage_interpretation_policy values: " + ", ".join(breakage_policies)
        )

    claim_policies = _invalid_values(
        frame,
        "claim_policy",
        frozenset({EXPECTED_CLAIM_POLICY}),
    )
    if claim_policies:
        raise ValueError("Invalid claim_policy values: " + ", ".join(claim_policies))

    contrast_policies = _invalid_values(
        frame,
        "contrast_checkpoint_policy",
        frozenset({EXPECTED_CLAIM_POLICY}),
    )
    if contrast_policies:
        raise ValueError(
            "Invalid contrast_checkpoint_policy values: " + ", ".join(contrast_policies)
        )

    gate_statuses = _invalid_values(
        frame,
        "strict_contrast_gate_status",
        ALLOWED_STRICT_CONTRAST_GATE_STATUSES,
    )
    if gate_statuses:
        raise ValueError("Invalid strict_contrast_gate_status values: " + ", ".join(gate_statuses))

    cofolding_statuses = _invalid_values(
        frame,
        "cofolding_plan_status",
        ALLOWED_COFOLDING_PLAN_STATUSES,
    )
    if cofolding_statuses:
        raise ValueError("Invalid cofolding_plan_status values: " + ", ".join(cofolding_statuses))


@app.command()
def main(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            help="TP53/MDM2 pilot manifest CSV to validate.",
        ),
    ] = DEFAULT_INPUT,
) -> dict[str, Any]:
    """Validate a TP53/MDM2 pilot manifest policy CSV."""

    frame = pl.read_csv(input_path)
    validate_tp53_mdm2_pilot_manifest(frame)

    result = {
        "input": str(input_path),
        "rows": frame.height,
        "candidate_set": EXPECTED_CANDIDATE_SET,
        "biological_mode": EXPECTED_BIOLOGICAL_MODE,
        "claim_policy": EXPECTED_CLAIM_POLICY,
        "no_live_actions": True,
    }

    typer.echo(f"Validated TP53/MDM2 pilot manifest rows: {frame.height}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No embeddings were generated.")
    typer.echo("No cofolding jobs were submitted.")
    typer.echo("No Boltz credits were spent.")
    typer.echo("No biological validation claim was made.")

    return result


if __name__ == "__main__":
    app()
