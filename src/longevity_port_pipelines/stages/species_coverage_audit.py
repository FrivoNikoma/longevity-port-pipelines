from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.config import SPECIES_REGISTRY
from longevity_port_pipelines.models import LifespanCategory, Species

DATA_OUTPUT = Path("data/output")
DATA_INTERIM = Path("data/interim")

SPECIES_PANEL_SCHEMA = {
    "target_species": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "group": pl.Utf8,
}

ORTHOLOG_RAW_SCHEMA = {
    "target_species": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "target_uniprot": pl.Utf8,
    "target_sequence_length": pl.Int64,
    "is_reviewed": pl.Boolean,
    "source_db": pl.Utf8,
    "source_file": pl.Utf8,
}

LOCAL_FILE_RAW_SCHEMA = {
    "target_species": pl.Utf8,
    "source_file": pl.Utf8,
    "n_rows": pl.Int64,
}

SUMMARY_SCHEMA = {
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
}

app = typer.Typer(add_completion=False)


@dataclass(frozen=True)
class SpeciesCoverageAuditSpec:
    complex_id: str
    pdb_id: str
    chain: str
    source_uniprot: str


@dataclass(frozen=True)
class SpeciesCoverageAuditResult:
    ortholog_raw: pl.DataFrame
    local_file_raw: pl.DataFrame
    summary: pl.DataFrame


@dataclass(frozen=True)
class SpeciesCoverageAuditOutputs:
    ortholog_raw: Path
    local_file_raw: Path
    summary: Path


def _empty_frame(schema: Mapping[str, Any]) -> pl.DataFrame:
    return pl.DataFrame(schema=schema)


def _frame_from_rows(rows: list[dict[str, Any]], schema: Mapping[str, Any]) -> pl.DataFrame:
    if not rows:
        return _empty_frame(schema)

    return pl.DataFrame(rows).select(
        [pl.col(column).cast(dtype).alias(column) for column, dtype in schema.items()]
    )


def target_species_rows(
    species_registry: Mapping[str, Species] | None = None,
) -> list[dict[str, Any]]:
    registry = species_registry or SPECIES_REGISTRY
    rows: list[dict[str, Any]] = []

    for species in registry.values():
        if species.category == LifespanCategory.REFERENCE:
            continue

        rows.append(
            {
                "target_species": species.name,
                "target_species_taxid": species.taxid,
                "group": species.category.value,
            }
        )

    group_order = {
        LifespanCategory.LONG_LIVED.value: 0,
        LifespanCategory.SHORT_LIVED.value: 1,
    }

    return sorted(
        rows,
        key=lambda row: (
            group_order.get(str(row["group"]), 99),
            str(row["target_species"]),
        ),
    )


def read_table(path: Path) -> pl.DataFrame | None:
    try:
        if path.suffix.lower() == ".parquet":
            return pl.read_parquet(path)
        if path.suffix.lower() == ".csv":
            return pl.read_csv(path, infer_schema_length=10000)
    except Exception as exc:
        typer.echo(f"SKIP {path}: {exc}")

    return None


def join_unique(values: list[Any]) -> str:
    clean = sorted({str(value) for value in values if value is not None and str(value)})
    return ", ".join(clean)


def sequence_length(value: Any) -> int | None:
    if value is None:
        return None

    text = str(value)
    if not text or text.lower() == "null":
        return None

    return len(text)


def audit_ortholog_coverage(
    *,
    species_rows: list[dict[str, Any]],
    data_output: Path,
    source_uniprot: str,
) -> pl.DataFrame:
    taxid_to_species = {
        int(row["target_species_taxid"]): str(row["target_species"]) for row in species_rows
    }

    raw_rows: list[dict[str, Any]] = []

    for path in sorted(data_output.glob("*ortholog_coverage*.csv")):
        df = read_table(path)
        if df is None:
            continue

        required = {"source_uniprot", "target_species_taxid", "target_sequence"}
        if not required.issubset(set(df.columns)):
            continue

        hits = df.filter(pl.col("source_uniprot") == source_uniprot)

        for row in hits.iter_rows(named=True):
            taxid = row.get("target_species_taxid")
            if taxid is None:
                continue

            species_name = taxid_to_species.get(int(taxid))
            if species_name is None:
                continue

            raw_rows.append(
                {
                    "target_species": species_name,
                    "target_species_taxid": int(taxid),
                    "target_uniprot": row.get("target_uniprot"),
                    "target_sequence_length": sequence_length(row.get("target_sequence")),
                    "is_reviewed": row.get("is_reviewed"),
                    "source_db": row.get("source_db"),
                    "source_file": str(path),
                }
            )

    return _frame_from_rows(raw_rows, ORTHOLOG_RAW_SCHEMA).sort(["target_species", "source_file"])


def row_matches_candidate(df: pl.DataFrame, spec: SpeciesCoverageAuditSpec) -> pl.Expr | None:
    masks: list[pl.Expr] = []

    if "complex_id" in df.columns:
        complex_col = pl.col("complex_id").cast(pl.Utf8)
        masks.append(
            complex_col.str.contains(spec.complex_id, literal=True)
            | complex_col.str.contains(spec.pdb_id, literal=True)
        )

    if "id" in df.columns:
        id_col = pl.col("id").cast(pl.Utf8)
        masks.append(
            id_col.str.contains(spec.complex_id, literal=True)
            | id_col.str.contains(spec.pdb_id, literal=True)
        )

    if "pdb_id" in df.columns:
        masks.append(pl.col("pdb_id").cast(pl.Utf8) == spec.pdb_id)

    if not masks:
        return None

    mask = masks[0]
    for extra in masks[1:]:
        mask = mask | extra

    if "chain" in df.columns:
        mask = mask & (pl.col("chain").cast(pl.Utf8) == spec.chain)

    if "source_uniprot" in df.columns:
        mask = mask & (pl.col("source_uniprot").cast(pl.Utf8) == spec.source_uniprot)

    return mask


def audit_local_candidate_file_rows(
    *,
    species_rows: list[dict[str, Any]],
    data_output: Path,
    spec: SpeciesCoverageAuditSpec,
) -> pl.DataFrame:
    target_species = {str(row["target_species"]) for row in species_rows}
    raw_rows: list[dict[str, Any]] = []

    files = sorted(
        path
        for path in data_output.rglob("*")
        if path.is_file() and path.suffix.lower() in {".csv", ".parquet"}
    )

    for path in files:
        if "ortholog_coverage" in path.name:
            continue

        df = read_table(path)
        if df is None:
            continue

        if "target_species" not in df.columns:
            continue

        mask = row_matches_candidate(df, spec)
        if mask is None:
            continue

        hits = df.filter(mask)
        if hits.is_empty():
            continue

        for species in sorted(set(hits["target_species"].drop_nulls().to_list())):
            species_text = str(species)
            if species_text not in target_species:
                continue

            species_hits = hits.filter(pl.col("target_species").cast(pl.Utf8) == species_text)

            raw_rows.append(
                {
                    "target_species": species_text,
                    "source_file": str(path),
                    "n_rows": species_hits.height,
                }
            )

    return _frame_from_rows(raw_rows, LOCAL_FILE_RAW_SCHEMA).sort(["target_species", "source_file"])


def coverage_gap_status(
    *,
    has_source_ortholog: bool,
    has_local_candidate_file_rows: bool,
) -> str:
    if has_source_ortholog and has_local_candidate_file_rows:
        return "ortholog_and_local_rows_present"
    if not has_source_ortholog and has_local_candidate_file_rows:
        return "missing_ortholog_but_local_rows_present"
    if has_source_ortholog and not has_local_candidate_file_rows:
        return "ortholog_present_but_missing_local_rows"
    return "missing_ortholog_and_local_rows"


def build_species_coverage_summary(
    *,
    species_rows: list[dict[str, Any]],
    ortholog_raw: pl.DataFrame,
    local_file_raw: pl.DataFrame,
) -> pl.DataFrame:
    rows: list[dict[str, Any]] = []

    for species_row in species_rows:
        species = str(species_row["target_species"])

        ortholog_hits = ortholog_raw.filter(pl.col("target_species") == species)
        local_file_hits = local_file_raw.filter(pl.col("target_species") == species)

        has_source_ortholog = not ortholog_hits.is_empty()
        has_local_candidate_file_rows = not local_file_hits.is_empty()

        n_local_rows = (
            int(local_file_hits.select(pl.col("n_rows").sum()).item())
            if has_local_candidate_file_rows
            else 0
        )

        rows.append(
            {
                **species_row,
                "has_source_ortholog": has_source_ortholog,
                "n_ortholog_candidate_rows": ortholog_hits.height,
                "candidate_target_uniprots": join_unique(
                    ortholog_hits["target_uniprot"].drop_nulls().to_list()
                )
                if has_source_ortholog
                else "",
                "candidate_sequence_lengths": join_unique(
                    ortholog_hits["target_sequence_length"].drop_nulls().to_list()
                )
                if has_source_ortholog
                else "",
                "ortholog_source_dbs": join_unique(
                    ortholog_hits["source_db"].drop_nulls().to_list()
                )
                if has_source_ortholog
                else "",
                "ortholog_source_files": join_unique(ortholog_hits["source_file"].to_list())
                if has_source_ortholog
                else "",
                "has_local_candidate_file_rows": has_local_candidate_file_rows,
                "n_local_candidate_file_rows": n_local_rows,
                "local_files": join_unique(local_file_hits["source_file"].to_list())
                if has_local_candidate_file_rows
                else "",
                "coverage_gap_status": coverage_gap_status(
                    has_source_ortholog=has_source_ortholog,
                    has_local_candidate_file_rows=has_local_candidate_file_rows,
                ),
            }
        )

    return _frame_from_rows(rows, SUMMARY_SCHEMA)


def build_species_coverage_audit(
    *,
    spec: SpeciesCoverageAuditSpec,
    data_output: Path = DATA_OUTPUT,
    species_rows: list[dict[str, Any]] | None = None,
) -> SpeciesCoverageAuditResult:
    panel_rows = species_rows or target_species_rows()

    ortholog_raw = audit_ortholog_coverage(
        species_rows=panel_rows,
        data_output=data_output,
        source_uniprot=spec.source_uniprot,
    )
    local_file_raw = audit_local_candidate_file_rows(
        species_rows=panel_rows,
        data_output=data_output,
        spec=spec,
    )
    summary = build_species_coverage_summary(
        species_rows=panel_rows,
        ortholog_raw=ortholog_raw,
        local_file_raw=local_file_raw,
    )

    return SpeciesCoverageAuditResult(
        ortholog_raw=ortholog_raw,
        local_file_raw=local_file_raw,
        summary=summary,
    )


def output_prefix_for(spec: SpeciesCoverageAuditSpec) -> str:
    return (
        f"{spec.pdb_id}_{spec.source_uniprot}".lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )


def write_species_coverage_audit_outputs(
    *,
    result: SpeciesCoverageAuditResult,
    output_dir: Path = DATA_INTERIM,
    output_prefix: str,
) -> SpeciesCoverageAuditOutputs:
    output_dir.mkdir(parents=True, exist_ok=True)

    ortholog_raw_path = output_dir / f"{output_prefix}_ortholog_coverage_raw_hits.csv"
    local_file_raw_path = output_dir / f"{output_prefix}_local_file_rows_raw_hits.csv"
    summary_path = output_dir / f"{output_prefix}_species_coverage_audit.csv"

    result.ortholog_raw.write_csv(ortholog_raw_path)
    result.local_file_raw.write_csv(local_file_raw_path)
    result.summary.write_csv(summary_path)

    return SpeciesCoverageAuditOutputs(
        ortholog_raw=ortholog_raw_path,
        local_file_raw=local_file_raw_path,
        summary=summary_path,
    )


def print_species_coverage_summary(
    *,
    spec: SpeciesCoverageAuditSpec,
    summary: pl.DataFrame,
) -> None:
    typer.echo()
    typer.echo("Species coverage audit")
    typer.echo("=" * 80)
    typer.echo(f"complex_id:     {spec.complex_id}")
    typer.echo(f"pdb_id:         {spec.pdb_id}")
    typer.echo(f"chain:          {spec.chain}")
    typer.echo(f"source_uniprot: {spec.source_uniprot}")
    typer.echo()

    for row in summary.iter_rows(named=True):
        species = str(row["target_species"])
        group = str(row["group"])
        has_ortholog = "yes" if row["has_source_ortholog"] else "no"
        has_results = "yes" if row["has_local_candidate_file_rows"] else "no"

        typer.echo(
            f"{species:18s} {group:12s} "
            f"ortholog={has_ortholog:3s} "
            f"ortholog_rows={row['n_ortholog_candidate_rows']:<2} "
            f"local_files={has_results:3s} "
            f"file_rows={row['n_local_candidate_file_rows']}"
        )

    missing_orthologs = summary.filter(~pl.col("has_source_ortholog"))["target_species"].to_list()
    missing_results = summary.filter(~pl.col("has_local_candidate_file_rows"))[
        "target_species"
    ].to_list()

    typer.echo()
    typer.echo(f"Missing source ortholog coverage: {missing_orthologs}")
    typer.echo(f"Missing local candidate file rows: {missing_results}")

    if missing_orthologs or missing_results:
        typer.echo()
        typer.echo("Interpretation guard:")
        typer.echo("- Do not describe this as a complete expanded species panel.")
        typer.echo("- Refresh/consolidate ortholog coverage before species-panel interpretation.")
    else:
        typer.echo()
        typer.echo("Ortholog coverage and local candidate rows are present for all target species.")


@app.command()
def main(
    complex_id: Annotated[str, typer.Option(help="Exact candidate complex id to audit.")],
    pdb_id: Annotated[str, typer.Option(help="PDB id used to identify candidate rows.")],
    chain: Annotated[str, typer.Option(help="Chain role to audit, for example receptor.")],
    source_uniprot: Annotated[str, typer.Option(help="Human/source UniProt id to audit.")],
    data_output: Annotated[
        Path,
        typer.Option(help="Directory containing runtime outputs."),
    ] = DATA_OUTPUT,
    output_dir: Annotated[
        Path,
        typer.Option(help="Directory for ignored audit outputs."),
    ] = DATA_INTERIM,
    output_prefix: Annotated[
        str | None,
        typer.Option(help="Optional output filename prefix."),
    ] = None,
) -> None:
    """Audit species coverage for one explicit candidate before species-panel interpretation."""
    spec = SpeciesCoverageAuditSpec(
        complex_id=complex_id,
        pdb_id=pdb_id,
        chain=chain,
        source_uniprot=source_uniprot,
    )
    result = build_species_coverage_audit(spec=spec, data_output=data_output)

    prefix = output_prefix or output_prefix_for(spec)
    outputs = write_species_coverage_audit_outputs(
        result=result,
        output_dir=output_dir,
        output_prefix=prefix,
    )

    print_species_coverage_summary(spec=spec, summary=result.summary)

    typer.echo()
    typer.echo("Wrote:")
    typer.echo(f"- {outputs.ortholog_raw}")
    typer.echo(f"- {outputs.local_file_raw}")
    typer.echo(f"- {outputs.summary}")
    typer.echo()
    typer.echo("No Boltz API calls were made.")


if __name__ == "__main__":
    app()
