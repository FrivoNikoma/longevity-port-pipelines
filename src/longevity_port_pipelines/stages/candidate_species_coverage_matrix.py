from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages.cofolding_candidate_baseline import (
    DEFAULT_PINDER_DATA_DIR,
    prepare_candidate_baseline_input,
)
from longevity_port_pipelines.stages.cofolding_candidate_preflight_batch import (
    manifest_candidates,
    read_table,
)
from longevity_port_pipelines.stages.species_coverage_audit import (
    DATA_INTERIM,
    DATA_OUTPUT,
    SpeciesCoverageAuditSpec,
    build_species_coverage_audit,
)

DEFAULT_MANIFEST = Path("data/input/sirt6_cofolding_candidate_manifest.csv")
DEFAULT_OUTPUT = DATA_INTERIM / "candidate_species_coverage_matrix.csv"

MATRIX_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "target_species": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "group": pl.Utf8,
    "has_source_ortholog": pl.Boolean,
    "n_ortholog_candidate_rows": pl.Int64,
    "candidate_target_uniprots": pl.Utf8,
    "candidate_sequence_lengths": pl.Utf8,
    "ortholog_source_dbs": pl.Utf8,
    "ortholog_source_files": pl.Utf8,
    "has_local_candidate_file_rows": pl.Boolean,
    "n_local_candidate_file_rows": pl.Int64,
    "local_files": pl.Utf8,
    "coverage_gap_status": pl.Utf8,
    "recommended_coverage_action": pl.Utf8,
    "coverage_note": pl.Utf8,
}

app = typer.Typer(add_completion=False)


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


def _as_bool(row: dict[str, Any], column: str, default: bool = False) -> bool:
    value = row.get(column)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def _empty_matrix() -> pl.DataFrame:
    return pl.DataFrame(schema=MATRIX_SCHEMA)


def _matrix_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return _empty_matrix()

    return pl.DataFrame(rows).select(
        [pl.col(column).cast(dtype).alias(column) for column, dtype in MATRIX_SCHEMA.items()]
    )


def recommended_coverage_action(coverage_gap_status: str) -> str:
    if coverage_gap_status == "ortholog_and_local_rows_present":
        return "coverage_ready"
    if coverage_gap_status == "ortholog_present_but_missing_local_rows":
        return "generate_local_candidate_rows"
    if coverage_gap_status == "missing_ortholog_but_local_rows_present":
        return "review_local_rows_without_source_ortholog"
    if coverage_gap_status == "missing_ortholog_and_local_rows":
        return "fetch_or_curate_source_ortholog"
    return "review_coverage_status"


def _missing_baseline_row(
    *,
    candidate_id: str,
    chain: str,
    source_uniprot: str,
    priority: str,
    note: str,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "pdb_id": "",
        "chain": chain,
        "source_uniprot": source_uniprot,
        "priority": priority,
        "target_species": "",
        "target_species_taxid": 0,
        "group": "",
        "has_source_ortholog": False,
        "n_ortholog_candidate_rows": 0,
        "candidate_target_uniprots": "",
        "candidate_sequence_lengths": "",
        "ortholog_source_dbs": "",
        "ortholog_source_files": "",
        "has_local_candidate_file_rows": False,
        "n_local_candidate_file_rows": 0,
        "local_files": "",
        "coverage_gap_status": "not_audited",
        "recommended_coverage_action": "fix_baseline_input",
        "coverage_note": note,
    }


def build_candidate_species_coverage_matrix(
    *,
    manifest: pl.DataFrame,
    pinder_data_dir: Path = DEFAULT_PINDER_DATA_DIR,
    data_output: Path = DATA_OUTPUT,
) -> pl.DataFrame:
    rows: list[dict[str, Any]] = []

    for candidate in manifest_candidates(manifest):
        try:
            baseline = prepare_candidate_baseline_input(
                pinder_data_dir,
                candidate.candidate_id,
            )
        except Exception as exc:
            rows.append(
                _missing_baseline_row(
                    candidate_id=candidate.candidate_id,
                    chain=candidate.chain,
                    source_uniprot=candidate.source_uniprot,
                    priority=candidate.priority,
                    note=f"Could not prepare baseline input: {exc}",
                )
            )
            continue

        pdb_id = _as_str(baseline, "pdb_id")
        coverage = build_species_coverage_audit(
            spec=SpeciesCoverageAuditSpec(
                complex_id=candidate.candidate_id,
                pdb_id=pdb_id,
                chain=candidate.chain,
                source_uniprot=candidate.source_uniprot,
            ),
            data_output=data_output,
        )

        for summary_row in coverage.summary.iter_rows(named=True):
            status = _as_str(summary_row, "coverage_gap_status")
            rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "pdb_id": pdb_id,
                    "chain": candidate.chain,
                    "source_uniprot": candidate.source_uniprot,
                    "priority": candidate.priority,
                    "target_species": _as_str(summary_row, "target_species"),
                    "target_species_taxid": _as_int(summary_row, "target_species_taxid"),
                    "group": _as_str(summary_row, "group"),
                    "has_source_ortholog": _as_bool(summary_row, "has_source_ortholog"),
                    "n_ortholog_candidate_rows": _as_int(summary_row, "n_ortholog_candidate_rows"),
                    "candidate_target_uniprots": _as_str(summary_row, "candidate_target_uniprots"),
                    "candidate_sequence_lengths": _as_str(
                        summary_row, "candidate_sequence_lengths"
                    ),
                    "ortholog_source_dbs": _as_str(summary_row, "ortholog_source_dbs"),
                    "ortholog_source_files": _as_str(summary_row, "ortholog_source_files"),
                    "has_local_candidate_file_rows": _as_bool(
                        summary_row, "has_local_candidate_file_rows"
                    ),
                    "n_local_candidate_file_rows": _as_int(
                        summary_row, "n_local_candidate_file_rows"
                    ),
                    "local_files": _as_str(summary_row, "local_files"),
                    "coverage_gap_status": status,
                    "recommended_coverage_action": recommended_coverage_action(status),
                    "coverage_note": "Species coverage audited without Biohub or Boltz calls.",
                }
            )

    return _matrix_from_rows(rows).sort(["candidate_id", "target_species"])


def action_counts(matrix: pl.DataFrame) -> dict[str, int]:
    if matrix.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in matrix.group_by("recommended_coverage_action").len().iter_rows(named=True):
        counts[str(row["recommended_coverage_action"])] = int(row["len"])

    return counts


def print_matrix_summary(matrix: pl.DataFrame) -> None:
    typer.echo(f"coverage matrix rows: {matrix.height}")

    for action, count in sorted(action_counts(matrix).items()):
        typer.echo(f"{action}: {count}")


@app.command()
def main(
    manifest: Annotated[
        Path,
        typer.Option(help="CSV/parquet manifest with candidate_id, chain, and source_uniprot."),
    ] = DEFAULT_MANIFEST,
    pinder_data_dir: Annotated[
        Path,
        typer.Option(help="Directory containing PINDER parquet files."),
    ] = DEFAULT_PINDER_DATA_DIR,
    data_output: Annotated[
        Path,
        typer.Option(help="Directory containing local runtime outputs to audit."),
    ] = DATA_OUTPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the candidate × species coverage matrix."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Build a manifest-level species coverage matrix without Biohub or Boltz calls."""
    manifest_df = read_table(manifest)
    matrix = build_candidate_species_coverage_matrix(
        manifest=manifest_df,
        pinder_data_dir=pinder_data_dir,
        data_output=data_output,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    matrix.write_csv(output)

    print_matrix_summary(matrix)
    typer.echo(f"Wrote candidate species coverage matrix -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")


if __name__ == "__main__":
    app()
