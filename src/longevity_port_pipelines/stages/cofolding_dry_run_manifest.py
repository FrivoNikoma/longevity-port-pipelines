from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages.cofolding_readiness import (
    CONSERVATIVE_CLAIM_POLICY,
    MAXIMUM_CLAIM_STATUS,
)
from longevity_port_pipelines.stages.cofolding_readiness_runtime import (
    COFOLDING_READINESS_SCHEMA,
)

DEFAULT_READINESS_SUMMARY = Path("data/interim/generic_cofolding_readiness_summary.csv")
DEFAULT_OUTPUT = Path("data/interim/generic_cofolding_dry_run_manifest.csv")
DEFAULT_BLOCKED_OUTPUT = Path("data/interim/generic_cofolding_dry_run_blocked_manifest.csv")

ELIGIBLE_READINESS_STATUS = "cofolding_dry_run_ready"
REVIEWED_INPUT_STATUS = "dry_run_inputs_reviewed"

ELIGIBLE_PLAN_STATUS = "eligible_for_generic_cofolding_dry_run_manifest"
BLOCKED_GATE8_NOT_READY = "blocked_gate8_not_ready"
BLOCKED_GATE8_REVIEW = "blocked_gate8_review"
BLOCKED_MISSING_CONTEXT = "blocked_missing_context"
BLOCKED_UNREVIEWED_INPUTS = "blocked_unreviewed_dry_run_inputs"
BLOCKED_CLAIM_POLICY = "blocked_claim_policy"
REVIEW_LIMITED_CONTEXT = "review_limited_cofolding_context"
REVIEW_MANUAL_CONTEXT = "review_manual_cofolding_context"
EXCLUDED_FROM_COFOLDING = "excluded_from_cofolding"
BLOCKED_COFOLDING_READINESS = "blocked_cofolding_readiness"

READINESS_REQUIRED_COLUMNS = set(COFOLDING_READINESS_SCHEMA)

COFOLDING_DRY_RUN_MANIFEST_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "target_species": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "contrast_class": pl.Utf8,
    "contrast_status": pl.Utf8,
    "robustness_status": pl.Utf8,
    "cofolding_input_review_status": pl.Utf8,
    "cofolding_readiness_status": pl.Utf8,
    "cofolding_plan_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "cofolding_dry_run_allowed": pl.Boolean,
    "live_cofolding_allowed": pl.Boolean,
    "controlled_claim_allowed": pl.Boolean,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "cofolding_readiness_note": pl.Utf8,
    "cofolding_plan_note": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def read_table(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing table: {path}")

    if path.suffix.lower() == ".parquet":
        return pl.read_parquet(path)

    return pl.read_csv(path, infer_schema_length=10000)


def validate_required_columns(df: pl.DataFrame, required: set[str], label: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {sorted(missing)}")


def _as_str(row: dict[str, Any], column: str, default: str = "") -> str:
    value = row.get(column)
    if value is None:
        return default
    return str(value).strip()


def _as_bool(row: dict[str, Any], column: str, default: bool = False) -> bool:
    value = row.get(column)
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False

    return default


def empty_cofolding_dry_run_manifest() -> pl.DataFrame:
    return pl.DataFrame(schema=COFOLDING_DRY_RUN_MANIFEST_SCHEMA)


def _manifest_from_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    if not rows:
        return empty_cofolding_dry_run_manifest()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in COFOLDING_DRY_RUN_MANIFEST_SCHEMA.items()
        ]
    )


def _eligible_for_dry_run_manifest(row: dict[str, Any]) -> bool:
    return (
        _as_str(row, "cofolding_readiness_status") == ELIGIBLE_READINESS_STATUS
        and _as_bool(row, "cofolding_dry_run_allowed")
        and not _as_bool(row, "live_cofolding_allowed")
        and not _as_bool(row, "controlled_claim_allowed")
        and _as_str(row, "claim_policy") == CONSERVATIVE_CLAIM_POLICY
        and _as_str(row, "claim_status") == MAXIMUM_CLAIM_STATUS
        and _as_str(row, "cofolding_input_review_status") == REVIEWED_INPUT_STATUS
        and bool(_as_str(row, "target_species"))
        and bool(_as_str(row, "partner_uniprot"))
    )


def _blocked_plan_status(row: dict[str, Any]) -> str:
    readiness_status = _as_str(row, "cofolding_readiness_status")

    if readiness_status == "cofolding_limited_dry_run_review":
        return REVIEW_LIMITED_CONTEXT
    if readiness_status == "blocked_contrast_not_ready":
        return BLOCKED_GATE8_NOT_READY
    if readiness_status == "blocked_contrast_requires_review":
        return BLOCKED_GATE8_REVIEW
    if readiness_status == "blocked_unreviewed_dry_run_inputs":
        return BLOCKED_UNREVIEWED_INPUTS
    if readiness_status == "blocked_claim_policy":
        return BLOCKED_CLAIM_POLICY
    if readiness_status == "excluded_from_cofolding":
        return EXCLUDED_FROM_COFOLDING
    if readiness_status == "needs_manual_review":
        return REVIEW_MANUAL_CONTEXT
    if readiness_status.startswith("blocked_missing"):
        return BLOCKED_MISSING_CONTEXT

    return BLOCKED_COFOLDING_READINESS


def _plan_note(row: dict[str, Any], *, eligible: bool) -> str:
    if eligible:
        return (
            "Eligible for generic cofolding dry-run manifest planning only; this is "
            "not a Boltz input, not a live structural call, and not a biological claim."
        )

    readiness_status = _as_str(row, "cofolding_readiness_status", "unknown")
    next_action = _as_str(row, "recommended_next_action", "manual_review_required")
    return (
        "Excluded from generic cofolding dry-run manifest eligibility; "
        f"cofolding_readiness_status={readiness_status}; "
        f"recommended_next_action={next_action}."
    )


def _manifest_record(
    row: dict[str, Any],
    *,
    cofolding_plan_status: str,
    cofolding_plan_note: str,
) -> dict[str, object]:
    return {
        "candidate_set": _as_str(row, "candidate_set"),
        "lane_name": _as_str(row, "lane_name"),
        "candidate_id": _as_str(row, "candidate_id"),
        "pdb_id": _as_str(row, "pdb_id"),
        "chain": _as_str(row, "chain"),
        "source_uniprot": _as_str(row, "source_uniprot"),
        "priority": _as_str(row, "priority"),
        "target_species": _as_str(row, "target_species"),
        "partner_uniprot": _as_str(row, "partner_uniprot"),
        "contrast_class": _as_str(row, "contrast_class"),
        "contrast_status": _as_str(row, "contrast_status"),
        "robustness_status": _as_str(row, "robustness_status"),
        "cofolding_input_review_status": _as_str(row, "cofolding_input_review_status"),
        "cofolding_readiness_status": _as_str(row, "cofolding_readiness_status"),
        "cofolding_plan_status": cofolding_plan_status,
        "recommended_next_action": _as_str(row, "recommended_next_action"),
        "cofolding_dry_run_allowed": _as_bool(row, "cofolding_dry_run_allowed"),
        "live_cofolding_allowed": _as_bool(row, "live_cofolding_allowed"),
        "controlled_claim_allowed": _as_bool(row, "controlled_claim_allowed"),
        "claim_policy": _as_str(row, "claim_policy"),
        "claim_status": _as_str(row, "claim_status"),
        "cofolding_readiness_note": _as_str(row, "cofolding_readiness_note"),
        "cofolding_plan_note": cofolding_plan_note,
    }


def build_generic_cofolding_dry_run_manifest(
    readiness_summary: pl.DataFrame,
) -> pl.DataFrame:
    """Build eligible generic cofolding dry-run manifest rows from Gate 9 output.

    This does not build Boltz inputs, does not call Boltz, does not call Biohub,
    does not generate embeddings, does not submit cofolding jobs, and does not
    make biological claims.
    """
    validate_required_columns(
        readiness_summary,
        READINESS_REQUIRED_COLUMNS,
        "readiness_summary",
    )

    rows: list[dict[str, object]] = []
    for row in readiness_summary.iter_rows(named=True):
        if not _eligible_for_dry_run_manifest(row):
            continue

        rows.append(
            _manifest_record(
                row,
                cofolding_plan_status=ELIGIBLE_PLAN_STATUS,
                cofolding_plan_note=_plan_note(row, eligible=True),
            )
        )

    return _manifest_from_rows(rows).sort(
        [
            "priority",
            "candidate_id",
            "target_species",
        ]
    )


def build_blocked_generic_cofolding_dry_run_manifest(
    readiness_summary: pl.DataFrame,
) -> pl.DataFrame:
    """Build blocked/review worklist rows from Gate 9 output."""
    validate_required_columns(
        readiness_summary,
        READINESS_REQUIRED_COLUMNS,
        "readiness_summary",
    )

    rows: list[dict[str, object]] = []
    for row in readiness_summary.iter_rows(named=True):
        if _eligible_for_dry_run_manifest(row):
            continue

        rows.append(
            _manifest_record(
                row,
                cofolding_plan_status=_blocked_plan_status(row),
                cofolding_plan_note=_plan_note(row, eligible=False),
            )
        )

    return _manifest_from_rows(rows).sort(
        [
            "cofolding_plan_status",
            "priority",
            "candidate_id",
            "target_species",
        ]
    )


def cofolding_plan_status_counts(manifest: pl.DataFrame) -> dict[str, int]:
    if manifest.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in manifest.group_by("cofolding_plan_status").len().iter_rows(named=True):
        counts[str(row["cofolding_plan_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    readiness_summary: Annotated[
        Path,
        typer.Option(help="CSV/parquet generic Gate 9 cofolding readiness summary table."),
    ] = DEFAULT_READINESS_SUMMARY,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for eligible generic cofolding dry-run manifest rows."),
    ] = DEFAULT_OUTPUT,
    blocked_output: Annotated[
        Path,
        typer.Option(help="Output CSV path for blocked/review generic cofolding manifest rows."),
    ] = DEFAULT_BLOCKED_OUTPUT,
) -> None:
    """Build a generic cofolding dry-run manifest without live actions."""
    readiness = read_table(readiness_summary)

    manifest = build_generic_cofolding_dry_run_manifest(readiness)
    blocked_manifest = build_blocked_generic_cofolding_dry_run_manifest(readiness)

    output.parent.mkdir(parents=True, exist_ok=True)
    blocked_output.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_csv(output)
    blocked_manifest.write_csv(blocked_output)

    typer.echo(
        f"Wrote eligible generic cofolding dry-run manifest rows: {manifest.height} -> {output}"
    )
    for status, count in sorted(cofolding_plan_status_counts(manifest).items()):
        typer.echo(f"eligible {status}: {count}")

    typer.echo(
        f"Wrote blocked/review generic cofolding manifest rows: "
        f"{blocked_manifest.height} -> {blocked_output}"
    )
    for status, count in sorted(cofolding_plan_status_counts(blocked_manifest).items()):
        typer.echo(f"blocked {status}: {count}")

    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No embeddings were generated.")
    typer.echo("No cofolding inputs were generated.")
    typer.echo("No cofolding jobs were submitted.")
    typer.echo("No Boltz credits were spent.")
    typer.echo("No signed structure URLs were written.")
    typer.echo("No biological validation claim was made.")


if __name__ == "__main__":
    app()
