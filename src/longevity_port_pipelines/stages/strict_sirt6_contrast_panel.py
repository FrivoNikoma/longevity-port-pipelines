from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages import candidate_coverage_repair_decisions as repair
from longevity_port_pipelines.stages import candidate_species_coverage_matrix as coverage
from longevity_port_pipelines.stages.coverage_preflight import (
    CONSERVATIVE_CLAIM_POLICY,
    coverage_preflight_for_statuses,
)

DEFAULT_COVERAGE_MATRIX_INPUT = Path("data/interim/sirt6_candidate_species_coverage_matrix.csv")
DEFAULT_REPAIR_DECISIONS_INPUT = repair.DEFAULT_REPAIR_DECISIONS_PATH
DEFAULT_OUTPUT = Path("data/interim/sirt6_strict_contrast_panel.csv")
DEFAULT_SUMMARY_OUTPUT = Path("data/interim/sirt6_strict_contrast_panel_summary.csv")

KEY_COLUMNS = ["candidate_id", "pdb_id", "chain", "source_uniprot", "priority"]
REPAIR_KEY_COLUMNS = ["candidate_id", "source_uniprot", "target_species"]

COVERAGE_REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "target_species",
    "target_species_taxid",
    "group",
    "coverage_gap_status",
    "recommended_coverage_action",
}

STRICT_PANEL_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "target_species": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "group": pl.Utf8,
    "coverage_gap_status": pl.Utf8,
    "recommended_coverage_action": pl.Utf8,
    "repair_decision": pl.Utf8,
    "repair_priority": pl.Utf8,
    "claim_policy": pl.Utf8,
    "strict_panel_include": pl.Boolean,
    "strict_panel_status": pl.Utf8,
    "strict_panel_claim_policy": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "strict_panel_note": pl.Utf8,
    "generic_coverage_status": pl.Utf8,
    "generic_provenance_status": pl.Utf8,
    "generic_repair_status": pl.Utf8,
    "generic_coverage_preflight_status": pl.Utf8,
    "generic_recommended_next_action": pl.Utf8,
    "generic_strict_panel_allowed": pl.Boolean,
    "generic_contrast_dry_run_allowed": pl.Boolean,
    "generic_claim_policy": pl.Utf8,
    "generic_claim_status": pl.Utf8,
    "generic_coverage_preflight_note": pl.Utf8,
}

STRICT_PANEL_SUMMARY_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "n_strict_panel_ready_species": pl.Int64,
    "n_strict_panel_blocked_species": pl.Int64,
    "n_strict_long_lived_ready": pl.Int64,
    "n_strict_short_lived_ready": pl.Int64,
    "strict_long_lived_species": pl.Utf8,
    "strict_short_lived_species": pl.Utf8,
    "blocked_target_species": pl.Utf8,
    "strict_panel_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "strict_panel_note": pl.Utf8,
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


def _as_int(row: dict[str, Any], column: str, default: int = 0) -> int:
    value = row.get(column)
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)

    text = str(value).strip()
    if not text:
        return default
    return int(text)


def _repair_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        _as_str(row, "candidate_id"),
        _as_str(row, "source_uniprot"),
        _as_str(row, "target_species"),
    )


def _key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        _as_str(row, "candidate_id"),
        _as_str(row, "pdb_id"),
        _as_str(row, "chain"),
        _as_str(row, "source_uniprot"),
        _as_str(row, "priority"),
    )


def _joined_unique_values(rows: list[dict[str, Any]], column: str) -> str:
    values = {_as_str(row, column) for row in rows}
    return ",".join(sorted(value for value in values if value))


def generic_coverage_status_for_sirt6_row(
    *,
    coverage_gap_status: str,
    recommended_coverage_action: str,
) -> str:
    if recommended_coverage_action == "coverage_ready":
        return "coverage_ready"
    if recommended_coverage_action == "generate_local_candidate_rows":
        return "source_ortholog_without_local_rows"
    if recommended_coverage_action == "fetch_or_curate_source_ortholog":
        return "missing_source_ortholog"
    if recommended_coverage_action in {
        "review_local_rows_without_source_ortholog",
        "local_downstream_evidence_without_source_ortholog",
    }:
        return "local_rows_without_source_ortholog"
    if coverage_gap_status == "not_audited":
        return "unresolved_downstream_provenance"
    return "unresolved_downstream_provenance"


def generic_provenance_status_for_sirt6_row(
    *,
    recommended_coverage_action: str,
) -> str:
    if recommended_coverage_action == "coverage_ready":
        return "standard_source_present"
    if recommended_coverage_action == "generate_local_candidate_rows":
        return "standard_source_present"
    if recommended_coverage_action in {
        "review_local_rows_without_source_ortholog",
        "local_downstream_evidence_without_source_ortholog",
    }:
        return "local_row_present_without_source"
    return "unresolved"


def generic_repair_status_for_sirt6_decision(
    *,
    recommended_coverage_action: str,
    repair_decision: str,
) -> str:
    if recommended_coverage_action == "coverage_ready":
        return "not_needed"
    if repair_decision == "exclude_from_strict_panel":
        return "excluded_from_strict_panel"
    if repair_decision == "defer_until_stronger_source":
        return "deferred_pending_source"
    if repair_decision == "needs_external_manual_sequence_review":
        return "needs_manual_review"
    if repair_decision == "curate_source_ortholog":
        return "pending"
    if repair_decision == "accept_existing_local_row_after_provenance_review":
        return "in_review"
    return ""


def generic_preflight_trace_for_sirt6_row(
    *,
    coverage_row: dict[str, Any],
    repair_row: dict[str, Any] | None,
) -> dict[str, Any]:
    recommended_action = _as_str(coverage_row, "recommended_coverage_action")
    coverage_gap_status = _as_str(coverage_row, "coverage_gap_status")
    repair_decision = ""
    if repair_row is not None:
        repair_decision = _as_str(repair_row, "repair_decision")

    generic_coverage_status = generic_coverage_status_for_sirt6_row(
        coverage_gap_status=coverage_gap_status,
        recommended_coverage_action=recommended_action,
    )
    generic_provenance_status = generic_provenance_status_for_sirt6_row(
        recommended_coverage_action=recommended_action,
    )
    generic_repair_status = generic_repair_status_for_sirt6_decision(
        recommended_coverage_action=recommended_action,
        repair_decision=repair_decision,
    )
    generic_preflight = coverage_preflight_for_statuses(
        coverage_status=generic_coverage_status,
        provenance_status=generic_provenance_status,
        repair_status=generic_repair_status,
        claim_policy=CONSERVATIVE_CLAIM_POLICY,
    )

    return {
        "generic_coverage_status": generic_coverage_status,
        "generic_provenance_status": generic_provenance_status,
        "generic_repair_status": generic_repair_status,
        "generic_coverage_preflight_status": generic_preflight.coverage_preflight_status,
        "generic_recommended_next_action": generic_preflight.recommended_next_action,
        "generic_strict_panel_allowed": generic_preflight.strict_panel_allowed,
        "generic_contrast_dry_run_allowed": generic_preflight.contrast_dry_run_allowed,
        "generic_claim_policy": generic_preflight.claim_policy,
        "generic_claim_status": generic_preflight.claim_status,
        "generic_coverage_preflight_note": generic_preflight.notes,
    }


def _empty_panel() -> pl.DataFrame:
    return pl.DataFrame(schema=STRICT_PANEL_SCHEMA)


def _empty_summary() -> pl.DataFrame:
    return pl.DataFrame(schema=STRICT_PANEL_SUMMARY_SCHEMA)


def _panel_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return _empty_panel()

    return pl.DataFrame(rows).select(
        [pl.col(column).cast(dtype).alias(column) for column, dtype in STRICT_PANEL_SCHEMA.items()]
    )


def _summary_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return _empty_summary()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in STRICT_PANEL_SUMMARY_SCHEMA.items()
        ]
    )


def _repair_rows_by_key(
    repair_decisions: pl.DataFrame,
) -> dict[tuple[str, str, str], dict[str, Any]]:
    repair.validate_repair_decisions(repair_decisions)
    return {_repair_key(row): row for row in repair_decisions.iter_rows(named=True)}


def _strict_row_decision(
    *,
    coverage_row: dict[str, Any],
    repair_row: dict[str, Any] | None,
) -> dict[str, Any]:
    recommended_action = _as_str(coverage_row, "recommended_coverage_action")
    coverage_gap_status = _as_str(coverage_row, "coverage_gap_status")
    generic_trace = generic_preflight_trace_for_sirt6_row(
        coverage_row=coverage_row,
        repair_row=repair_row,
    )

    if recommended_action == "coverage_ready":
        return {
            "repair_decision": "",
            "repair_priority": "",
            "claim_policy": "coverage_ready_no_claim",
            "strict_panel_include": True,
            "strict_panel_status": "strict_panel_ready",
            "strict_panel_claim_policy": "allowed_for_strict_panel_planning_no_claim",
            "recommended_next_action": "allow_for_strict_panel_planning",
            "strict_panel_note": (
                "Source ortholog and local candidate rows are present. This only "
                "allows strict panel planning; no enrichment statistic or biological "
                "claim is computed here."
            ),
            **generic_trace,
        }

    if repair_row is None:
        return {
            "repair_decision": "",
            "repair_priority": "",
            "claim_policy": "",
            "strict_panel_include": False,
            "strict_panel_status": "blocked_missing_repair_decision",
            "strict_panel_claim_policy": "no_claim",
            "recommended_next_action": "add_coverage_repair_decision",
            "strict_panel_note": (
                "Species coverage is not ready and no repair decision is available."
            ),
            **generic_trace,
        }

    repair_decision = _as_str(repair_row, "repair_decision")
    repair_priority = _as_str(repair_row, "repair_priority")
    claim_policy = _as_str(repair_row, "claim_policy")

    if claim_policy == "deferred_no_claim":
        status = "blocked_deferred_no_claim"
        next_action = "review_manual_coverage_repair_decision"
        note = (
            "Coverage repair decision remains deferred_no_claim; manual "
            "sequence/provenance review is required before strict panel use."
        )
    elif (
        claim_policy == "excluded_from_strict_claim"
        or repair_decision == "exclude_from_strict_panel"
    ):
        status = "excluded_from_strict_panel"
        next_action = "do_not_use_in_strict_panel"
        note = "Coverage repair policy excludes this row from strict panel use."
    elif claim_policy == "allowed_for_limited_dry_run_only":
        status = "blocked_limited_dry_run_only"
        next_action = "keep_as_dry_run_only"
        note = "Coverage repair policy allows only limited dry-run planning, not strict claims."
    else:
        status = "blocked_repair_policy_review_required"
        next_action = "resolve_coverage_repair_policy"
        note = (
            "Coverage repair policy is not sufficient for strict panel inclusion; "
            "review before use."
        )

    return {
        "repair_decision": repair_decision,
        "repair_priority": repair_priority,
        "claim_policy": claim_policy,
        "strict_panel_include": False,
        "strict_panel_status": status,
        "strict_panel_claim_policy": "no_claim",
        "recommended_next_action": next_action,
        "strict_panel_note": f"{note} coverage_gap_status={coverage_gap_status}.",
        **generic_trace,
    }


def build_strict_sirt6_contrast_panel(
    *,
    coverage_matrix: pl.DataFrame,
    repair_decisions: pl.DataFrame,
) -> pl.DataFrame:
    validate_required_columns(coverage_matrix, COVERAGE_REQUIRED_COLUMNS, "coverage_matrix")
    repair_by_key = _repair_rows_by_key(repair_decisions)

    rows: list[dict[str, Any]] = []
    for coverage_row in coverage_matrix.iter_rows(named=True):
        row_decision = _strict_row_decision(
            coverage_row=coverage_row,
            repair_row=repair_by_key.get(_repair_key(coverage_row)),
        )
        rows.append(
            {
                "candidate_id": _as_str(coverage_row, "candidate_id"),
                "pdb_id": _as_str(coverage_row, "pdb_id"),
                "chain": _as_str(coverage_row, "chain"),
                "source_uniprot": _as_str(coverage_row, "source_uniprot"),
                "priority": _as_str(coverage_row, "priority"),
                "target_species": _as_str(coverage_row, "target_species"),
                "target_species_taxid": _as_int(coverage_row, "target_species_taxid"),
                "group": _as_str(coverage_row, "group"),
                "coverage_gap_status": _as_str(coverage_row, "coverage_gap_status"),
                "recommended_coverage_action": _as_str(
                    coverage_row,
                    "recommended_coverage_action",
                ),
                **row_decision,
            }
        )

    return _panel_from_rows(rows).sort(
        ["candidate_id", "strict_panel_include", "target_species"],
        descending=[False, True, False],
    )


def _summary_status(
    *,
    n_blocked: int,
    n_long_lived_ready: int,
    n_short_lived_ready: int,
) -> str:
    if n_blocked > 0:
        return "blocked_species_coverage_repair"
    if n_long_lived_ready > 0 and n_short_lived_ready > 0:
        return "strict_panel_ready"
    if n_long_lived_ready == 0 and n_short_lived_ready == 0:
        return "insufficient_strict_coverage"
    if n_long_lived_ready == 0:
        return "insufficient_strict_long_lived_coverage"
    return "insufficient_strict_short_lived_coverage"


def _summary_next_action(status: str) -> str:
    if status == "strict_panel_ready":
        return "prepare_strict_contrast_dry_run"
    if status == "blocked_species_coverage_repair":
        return "resolve_coverage_repair_decisions"
    return "repair_species_coverage_before_strict_contrast"


def strict_panel_candidate_summary(panel: pl.DataFrame) -> pl.DataFrame:
    if panel.is_empty():
        return _empty_summary()

    rows: list[dict[str, Any]] = []
    for key_row in panel.select(KEY_COLUMNS).unique().sort(KEY_COLUMNS).iter_rows(named=True):
        candidate_rows = panel
        for column in KEY_COLUMNS:
            candidate_rows = candidate_rows.filter(pl.col(column) == key_row[column])

        ready_rows = candidate_rows.filter(pl.col("strict_panel_include"))

        ready_long_lived = sorted(
            {
                _as_str(row, "target_species")
                for row in ready_rows.filter(
                    pl.col("group").is_in(coverage.LONG_LIVED_GROUPS)
                ).iter_rows(named=True)
                if _as_str(row, "target_species")
            }
        )
        ready_short_lived = sorted(
            {
                _as_str(row, "target_species")
                for row in ready_rows.filter(
                    pl.col("group").is_in(coverage.SHORT_LIVED_GROUPS)
                ).iter_rows(named=True)
                if _as_str(row, "target_species")
            }
        )
        blocked_species = sorted(
            {
                _as_str(row, "target_species")
                for row in candidate_rows.filter(~pl.col("strict_panel_include")).iter_rows(
                    named=True
                )
                if _as_str(row, "target_species")
            }
        )

        status = _summary_status(
            n_blocked=len(blocked_species),
            n_long_lived_ready=len(ready_long_lived),
            n_short_lived_ready=len(ready_short_lived),
        )

        rows.append(
            {
                **key_row,
                "n_strict_panel_ready_species": ready_rows.height,
                "n_strict_panel_blocked_species": len(blocked_species),
                "n_strict_long_lived_ready": len(ready_long_lived),
                "n_strict_short_lived_ready": len(ready_short_lived),
                "strict_long_lived_species": ",".join(ready_long_lived),
                "strict_short_lived_species": ",".join(ready_short_lived),
                "blocked_target_species": ",".join(blocked_species),
                "strict_panel_status": status,
                "recommended_next_action": _summary_next_action(status),
                "strict_panel_note": (
                    "Strict panel builder only audits coverage and repair policy; "
                    "it does not compute enrichment statistics or biological claims."
                ),
            }
        )

    return _summary_from_rows(rows).sort(["strict_panel_status", "priority", "candidate_id"])


def strict_panel_status_counts(panel: pl.DataFrame) -> dict[str, int]:
    if panel.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in panel.group_by("strict_panel_status").len().iter_rows(named=True):
        counts[str(row["strict_panel_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    coverage_matrix_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet SIRT6 candidate x species coverage matrix."),
    ] = DEFAULT_COVERAGE_MATRIX_INPUT,
    repair_decisions_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet coverage repair decision table."),
    ] = DEFAULT_REPAIR_DECISIONS_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the strict SIRT6 contrast panel."),
    ] = DEFAULT_OUTPUT,
    summary_output: Annotated[
        Path | None,
        typer.Option(help="Optional output CSV path for candidate-level strict panel summary."),
    ] = DEFAULT_SUMMARY_OUTPUT,
) -> None:
    """Build a strict SIRT6 contrast panel without Biohub, Boltz, or claims."""
    coverage_matrix = read_table(coverage_matrix_input)
    repair_decisions = read_table(repair_decisions_input)

    panel = build_strict_sirt6_contrast_panel(
        coverage_matrix=coverage_matrix,
        repair_decisions=repair_decisions,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    panel.write_csv(output)

    if summary_output is not None:
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        strict_panel_candidate_summary(panel).write_csv(summary_output)

    typer.echo(f"strict SIRT6 contrast panel rows: {panel.height}")
    for status, count in sorted(strict_panel_status_counts(panel).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote strict SIRT6 contrast panel -> {output}")
    if summary_output is not None:
        typer.echo(f"Wrote strict SIRT6 contrast panel summary -> {summary_output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No embeddings, enrichment statistics, or biological claims were computed.")


if __name__ == "__main__":
    app()
