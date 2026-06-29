from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import polars as pl
import typer

from longevity_port_pipelines.stages.cofolding_candidate_baseline import (
    DEFAULT_PINDER_DATA_DIR,
    SHORT_FRAGMENT_WARNING_THRESHOLD,
    prepare_candidate_baseline_input,
)
from longevity_port_pipelines.stages.negatome_curation import CURATED_NEGATIVE_PARTNERS
from longevity_port_pipelines.stages.negatome_inputs import (
    filter_nonempty_negative_control_pairs,
)
from longevity_port_pipelines.stages.negatome_inputs import (
    validate_schema as validate_negatome_schema,
)
from longevity_port_pipelines.stages.species_coverage_audit import (
    DATA_OUTPUT,
    SpeciesCoverageAuditSpec,
    build_species_coverage_audit,
)

DEFAULT_MANIFEST = Path("data/interim/cofolding_candidate_manifest.csv")
DEFAULT_EXISTING_NEGATOME_PAIRS = Path("data/interim/negatome_control_pairs_with_curated.csv")
DEFAULT_OUTPUT = Path("data/output/cofolding_candidate_preflight_scorecard.csv")

REQUIRED_MANIFEST_COLUMNS = {
    "candidate_id",
    "chain",
    "source_uniprot",
}

SCORECARD_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "baseline_input_status": pl.Utf8,
    "receptor_uniprot": pl.Utf8,
    "ligand_uniprot": pl.Utf8,
    "receptor_length": pl.Int64,
    "ligand_length": pl.Int64,
    "short_fragment_warning": pl.Boolean,
    "species_coverage_status": pl.Utf8,
    "missing_source_ortholog_species": pl.Utf8,
    "missing_local_candidate_row_species": pl.Utf8,
    "negatome_status": pl.Utf8,
    "negative_partner_uniprot": pl.Utf8,
    "missing_negatome_species": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "preflight_note": pl.Utf8,
}

app = typer.Typer(add_completion=False)


@dataclass(frozen=True)
class ManifestCandidate:
    candidate_id: str
    chain: str
    source_uniprot: str
    priority: str = ""


@dataclass(frozen=True)
class NegatomeReadiness:
    status: str
    negative_partner_uniprot: str
    missing_species: str


def _as_str(row: dict[str, object], column: str, default: str = "") -> str:
    value = row.get(column)
    if value is None:
        return default
    return str(value).strip()


def _as_int(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    text = str(value).strip()
    if not text:
        return 0
    return int(text)


def _join(values: list[str]) -> str:
    return ", ".join(sorted({value for value in values if value}))


def _empty_scorecard() -> pl.DataFrame:
    return pl.DataFrame(schema=SCORECARD_SCHEMA)


def _scorecard_from_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    if not rows:
        return _empty_scorecard()

    return pl.DataFrame(rows).select(
        [pl.col(column).cast(dtype).alias(column) for column, dtype in SCORECARD_SCHEMA.items()]
    )


def read_table(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing table: {path}")

    if path.suffix.lower() == ".parquet":
        return pl.read_parquet(path)

    return pl.read_csv(path, infer_schema_length=10000)


def validate_manifest_schema(manifest: pl.DataFrame) -> None:
    missing = REQUIRED_MANIFEST_COLUMNS - set(manifest.columns)
    if missing:
        raise ValueError(f"Candidate manifest is missing required columns: {sorted(missing)}")


def manifest_candidates(manifest: pl.DataFrame) -> list[ManifestCandidate]:
    validate_manifest_schema(manifest)

    rows: list[ManifestCandidate] = []
    seen: set[str] = set()

    for row in manifest.iter_rows(named=True):
        candidate_id = _as_str(row, "candidate_id")
        if not candidate_id:
            raise ValueError("Candidate manifest contains an empty candidate_id.")
        if candidate_id in seen:
            raise ValueError(f"Duplicate candidate_id in manifest: {candidate_id}")
        seen.add(candidate_id)

        rows.append(
            ManifestCandidate(
                candidate_id=candidate_id,
                chain=_as_str(row, "chain"),
                source_uniprot=_as_str(row, "source_uniprot"),
                priority=_as_str(row, "priority"),
            )
        )

    return rows


def load_existing_negatome_pairs(path: Path) -> pl.DataFrame | None:
    if not path.exists():
        return None

    pairs = read_table(path)
    validate_negatome_schema(pairs)
    return filter_nonempty_negative_control_pairs(pairs)


def _species_from_coverage_summary(summary: pl.DataFrame) -> list[str]:
    if summary.is_empty() or "target_species" not in summary.columns:
        return []

    return [str(value) for value in summary["target_species"].drop_nulls().to_list()]


def species_coverage_status(summary: pl.DataFrame) -> tuple[str, str, str]:
    if summary.is_empty():
        return "not_audited", "", ""

    missing_orthologs = [
        str(row["target_species"])
        for row in summary.filter(~pl.col("has_source_ortholog")).iter_rows(named=True)
    ]
    missing_local_rows = [
        str(row["target_species"])
        for row in summary.filter(~pl.col("has_local_candidate_file_rows")).iter_rows(named=True)
    ]

    if missing_orthologs:
        return "missing_source_ortholog", _join(missing_orthologs), _join(missing_local_rows)
    if missing_local_rows:
        return "missing_local_candidate_rows", "", _join(missing_local_rows)

    return "complete_species_coverage", "", ""


def negatome_readiness(
    *,
    candidate: ManifestCandidate,
    expected_species: list[str],
    existing_pairs: pl.DataFrame | None,
) -> NegatomeReadiness:
    partner = CURATED_NEGATIVE_PARTNERS.get(candidate.source_uniprot)
    if partner is None:
        return NegatomeReadiness(
            status="missing_curated_negative_partner",
            negative_partner_uniprot="",
            missing_species=_join(expected_species),
        )

    negative_partner_uniprot = partner["negative_partner_uniprot"]
    if existing_pairs is None or existing_pairs.is_empty():
        return NegatomeReadiness(
            status="missing_export_ready",
            negative_partner_uniprot=negative_partner_uniprot,
            missing_species=_join(expected_species),
        )

    hits = existing_pairs.filter(
        (pl.col("complex_id").cast(pl.Utf8) == candidate.candidate_id)
        & (pl.col("chain").cast(pl.Utf8) == candidate.chain)
        & (pl.col("source_uniprot").cast(pl.Utf8) == candidate.source_uniprot)
        & (pl.col("negative_partner_uniprot").cast(pl.Utf8) == negative_partner_uniprot)
    )

    present_species = (
        {str(value) for value in hits["target_species"].drop_nulls().to_list()}
        if not hits.is_empty()
        else set()
    )

    expected = set(expected_species)
    missing_species = sorted(expected - present_species)

    if not expected:
        return NegatomeReadiness(
            status="not_audited",
            negative_partner_uniprot=negative_partner_uniprot,
            missing_species="",
        )

    if not missing_species:
        return NegatomeReadiness(
            status="present_existing",
            negative_partner_uniprot=negative_partner_uniprot,
            missing_species="",
        )

    if present_species:
        return NegatomeReadiness(
            status="partial_existing",
            negative_partner_uniprot=negative_partner_uniprot,
            missing_species=_join(missing_species),
        )

    return NegatomeReadiness(
        status="missing_export_ready",
        negative_partner_uniprot=negative_partner_uniprot,
        missing_species=_join(missing_species),
    )


def recommended_next_action(
    *,
    baseline_input_status: str,
    species_status: str,
    negatome_status: str,
    short_fragment_warning: bool,
) -> str:
    if baseline_input_status != "input_prepared":
        return "fix_baseline_input"

    if species_status != "complete_species_coverage":
        return "fix_species_coverage"

    if negatome_status in {
        "missing_curated_negative_partner",
        "missing_export_ready",
        "partial_existing",
        "not_audited",
    }:
        return "fix_negatome_controls"

    if short_fragment_warning:
        return "review_short_fragments"

    return "ready_for_human_baseline"


def build_candidate_preflight_scorecard(
    *,
    manifest: pl.DataFrame,
    pinder_data_dir: Path = DEFAULT_PINDER_DATA_DIR,
    data_output: Path = DATA_OUTPUT,
    existing_negatome_pairs: pl.DataFrame | None = None,
    short_fragment_threshold: int = SHORT_FRAGMENT_WARNING_THRESHOLD,
) -> pl.DataFrame:
    rows: list[dict[str, object]] = []

    for candidate in manifest_candidates(manifest):
        try:
            baseline = prepare_candidate_baseline_input(
                pinder_data_dir,
                candidate.candidate_id,
            )
            baseline_input_status = "input_prepared"
            baseline_note = "PINDER baseline input prepared without live Boltz calls."
        except Exception as exc:
            rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "pdb_id": "",
                    "chain": candidate.chain,
                    "source_uniprot": candidate.source_uniprot,
                    "priority": candidate.priority,
                    "baseline_input_status": "missing_baseline_input",
                    "receptor_uniprot": "",
                    "ligand_uniprot": "",
                    "receptor_length": 0,
                    "ligand_length": 0,
                    "short_fragment_warning": False,
                    "species_coverage_status": "not_audited",
                    "missing_source_ortholog_species": "",
                    "missing_local_candidate_row_species": "",
                    "negatome_status": "not_audited",
                    "negative_partner_uniprot": "",
                    "missing_negatome_species": "",
                    "recommended_next_action": "fix_baseline_input",
                    "preflight_note": f"Could not prepare baseline input: {exc}",
                }
            )
            continue

        pdb_id = _as_str(baseline, "pdb_id")
        receptor_length = _as_int(baseline.get("pinder_receptor_len"))
        ligand_length = _as_int(baseline.get("pinder_ligand_len"))
        short_fragment_warning = (
            receptor_length < short_fragment_threshold or ligand_length < short_fragment_threshold
        )

        coverage = build_species_coverage_audit(
            spec=SpeciesCoverageAuditSpec(
                complex_id=candidate.candidate_id,
                pdb_id=pdb_id,
                chain=candidate.chain,
                source_uniprot=candidate.source_uniprot,
            ),
            data_output=data_output,
        )
        species_status, missing_orthologs, missing_local_rows = species_coverage_status(
            coverage.summary
        )

        expected_species = _species_from_coverage_summary(coverage.summary)
        negatome = negatome_readiness(
            candidate=candidate,
            expected_species=expected_species,
            existing_pairs=existing_negatome_pairs,
        )

        action = recommended_next_action(
            baseline_input_status=baseline_input_status,
            species_status=species_status,
            negatome_status=negatome.status,
            short_fragment_warning=short_fragment_warning,
        )

        rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "pdb_id": pdb_id,
                "chain": candidate.chain,
                "source_uniprot": candidate.source_uniprot,
                "priority": candidate.priority,
                "baseline_input_status": baseline_input_status,
                "receptor_uniprot": _as_str(baseline, "receptor_uniprot"),
                "ligand_uniprot": _as_str(baseline, "ligand_uniprot"),
                "receptor_length": receptor_length,
                "ligand_length": ligand_length,
                "short_fragment_warning": short_fragment_warning,
                "species_coverage_status": species_status,
                "missing_source_ortholog_species": missing_orthologs,
                "missing_local_candidate_row_species": missing_local_rows,
                "negatome_status": negatome.status,
                "negative_partner_uniprot": negatome.negative_partner_uniprot,
                "missing_negatome_species": negatome.missing_species,
                "recommended_next_action": action,
                "preflight_note": baseline_note,
            }
        )

    return _scorecard_from_rows(rows).sort(["recommended_next_action", "priority", "candidate_id"])


def action_counts(scorecard: pl.DataFrame) -> dict[str, int]:
    if scorecard.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in scorecard.group_by("recommended_next_action").len().iter_rows(named=True):
        counts[str(row["recommended_next_action"])] = int(row["len"])

    return counts


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
    existing_negatome_pairs: Annotated[
        Path,
        typer.Option(help="Existing NEGATOME control-pair CSV/parquet file."),
    ] = DEFAULT_EXISTING_NEGATOME_PAIRS,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the candidate preflight scorecard."),
    ] = DEFAULT_OUTPUT,
    short_fragment_threshold: Annotated[
        int,
        typer.Option(help="Warn when either PINDER fragment is shorter than this threshold."),
    ] = SHORT_FRAGMENT_WARNING_THRESHOLD,
) -> None:
    """Build a manifest-driven preflight scorecard without Boltz calls."""
    manifest_df = read_table(manifest)
    existing_pairs = load_existing_negatome_pairs(existing_negatome_pairs)

    scorecard = build_candidate_preflight_scorecard(
        manifest=manifest_df,
        pinder_data_dir=pinder_data_dir,
        data_output=data_output,
        existing_negatome_pairs=existing_pairs,
        short_fragment_threshold=short_fragment_threshold,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    scorecard.write_csv(output)

    typer.echo(f"candidate rows audited: {scorecard.height}")
    for action, count in sorted(action_counts(scorecard).items()):
        typer.echo(f"{action}: {count}")

    for row in scorecard.iter_rows(named=True):
        typer.echo(
            "  "
            f"{row['candidate_id']} "
            f"baseline={row['baseline_input_status']} "
            f"species={row['species_coverage_status']} "
            f"negatome={row['negatome_status']} "
            f"next={row['recommended_next_action']}"
        )

    typer.echo(f"Wrote candidate preflight scorecard -> {output}")
    typer.echo("No Boltz API calls were made.")


if __name__ == "__main__":
    app()
