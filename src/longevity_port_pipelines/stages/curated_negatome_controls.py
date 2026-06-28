from __future__ import annotations

from pathlib import Path

import polars as pl
import typer

from longevity_port_pipelines.stages.negatome_curation import (
    CURATED_NEGATIVE_PARTNERS,
    NEGATOME_PAIR_COLUMNS,
    build_curated_ortholog_negatome_control_pairs,
)
from longevity_port_pipelines.stages.negatome_inputs import (
    duplicate_key_columns,
    filter_nonempty_negative_control_pairs,
)
from longevity_port_pipelines.stages.negatome_inputs import (
    validate_schema as validate_negatome_schema,
)
from longevity_port_pipelines.stages.ortholog_inputs import (
    filter_primary_curated_ortholog_candidates,
)
from longevity_port_pipelines.stages.ortholog_inputs import (
    validate_schema as validate_ortholog_schema,
)

DEFAULT_CURATED_ORTHOLOGS = Path("data/input/curated_ortholog_candidates.csv")
DEFAULT_EXISTING_NEGATOME_PAIRS = Path("data/interim/negatome_control_pairs.csv")
DEFAULT_CACHE_DIR = Path("data/interim/uniprot_sequences")
DEFAULT_PREFLIGHT_OUTPUT = Path("data/output/curated_negatome_control_preflight.csv")
DEFAULT_MERGED_OUTPUT = Path("data/interim/negatome_control_pairs_with_curated.csv")

PREFLIGHT_SCHEMA = {
    "complex_id": pl.Utf8,
    "chain": pl.Utf8,
    "target_species": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "negative_partner_uniprot": pl.Utf8,
    "negative_partner_source": pl.Utf8,
    "control_type": pl.Utf8,
    "existing_negative_control_row": pl.Boolean,
    "export_status": pl.Utf8,
    "export_note": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def empty_curated_negatome_control_preflight() -> pl.DataFrame:
    return pl.DataFrame(schema=PREFLIGHT_SCHEMA)


def empty_negatome_pairs() -> pl.DataFrame:
    return pl.DataFrame(schema={column: pl.Utf8 for column in NEGATOME_PAIR_COLUMNS})


def _as_str(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        return ""
    return str(value).strip()


def _negative_control_key(
    *,
    complex_id: str,
    chain: str,
    target_species: str,
    negative_partner_uniprot: str,
    control_type: str,
) -> tuple[str, ...]:
    values = {
        "complex_id": complex_id,
        "chain": chain,
        "target_species": target_species,
        "negative_partner_uniprot": negative_partner_uniprot,
        "control_type": control_type,
    }

    return tuple(values[column] for column in duplicate_key_columns())


def _existing_negative_control_keys(
    existing_pairs: pl.DataFrame | None,
) -> set[tuple[str, ...]]:
    if existing_pairs is None:
        return set()

    validate_negatome_schema(existing_pairs)
    nonempty_pairs = filter_nonempty_negative_control_pairs(existing_pairs)

    return {
        _negative_control_key(
            complex_id=_as_str(row, "complex_id"),
            chain=_as_str(row, "chain"),
            target_species=_as_str(row, "target_species"),
            negative_partner_uniprot=_as_str(row, "negative_partner_uniprot"),
            control_type=_as_str(row, "control_type"),
        )
        for row in nonempty_pairs.iter_rows(named=True)
    }


def build_curated_negatome_control_preflight(
    curated_candidates: pl.DataFrame,
    existing_pairs: pl.DataFrame | None,
) -> pl.DataFrame:
    """Report curated ortholog candidates that can receive NEGATOME rows.

    This preflight does not fetch UniProt sequences and does not write merged
    NEGATOME inputs. It only reports whether rows are already present or ready
    to export.
    """
    validate_ortholog_schema(curated_candidates)

    primary_candidates = filter_primary_curated_ortholog_candidates(curated_candidates)
    if primary_candidates.is_empty():
        return empty_curated_negatome_control_preflight()

    existing_keys = _existing_negative_control_keys(existing_pairs)

    rows: list[dict[str, object]] = []
    for candidate_row in primary_candidates.iter_rows(named=True):
        complex_id = _as_str(candidate_row, "complex_id")
        chain = _as_str(candidate_row, "chain")
        target_species = _as_str(candidate_row, "target_species")
        source_uniprot = _as_str(candidate_row, "source_uniprot")

        partner_spec = CURATED_NEGATIVE_PARTNERS.get(source_uniprot)
        if partner_spec is None:
            rows.append(
                {
                    "complex_id": complex_id,
                    "chain": chain,
                    "target_species": target_species,
                    "source_uniprot": source_uniprot,
                    "negative_partner_uniprot": "",
                    "negative_partner_source": "",
                    "control_type": "",
                    "existing_negative_control_row": False,
                    "export_status": "missing_curated_negative_partner",
                    "export_note": (
                        "No curated negative partner is configured for this source UniProt. "
                        "Manual NEGATOME-style curation is required before export."
                    ),
                }
            )
            continue

        negative_partner_uniprot = partner_spec["negative_partner_uniprot"]
        control_type = partner_spec["control_type"]

        key = _negative_control_key(
            complex_id=complex_id,
            chain=chain,
            target_species=target_species,
            negative_partner_uniprot=negative_partner_uniprot,
            control_type=control_type,
        )
        existing = key in existing_keys

        rows.append(
            {
                "complex_id": complex_id,
                "chain": chain,
                "target_species": target_species,
                "source_uniprot": source_uniprot,
                "negative_partner_uniprot": negative_partner_uniprot,
                "negative_partner_source": partner_spec["negative_partner_source"],
                "control_type": control_type,
                "existing_negative_control_row": existing,
                "export_status": "present_existing" if existing else "missing_export_ready",
                "export_note": (
                    "Negative-control row already exists."
                    if existing
                    else "Curated negative partner exists; row is ready for export."
                ),
            }
        )

    return (
        pl.DataFrame(rows)
        .select(list(PREFLIGHT_SCHEMA))
        .sort(["export_status", "complex_id", "chain", "target_species", "source_uniprot"])
    )


def merge_curated_negatome_control_pairs(
    existing_pairs: pl.DataFrame | None,
    curated_pairs: pl.DataFrame,
) -> pl.DataFrame:
    validate_negatome_schema(curated_pairs)

    if existing_pairs is None:
        existing_pairs = empty_negatome_pairs()

    validate_negatome_schema(existing_pairs)

    if curated_pairs.is_empty():
        return existing_pairs.select(NEGATOME_PAIR_COLUMNS)

    return (
        pl.concat(
            [
                existing_pairs.select(NEGATOME_PAIR_COLUMNS),
                curated_pairs.select(NEGATOME_PAIR_COLUMNS),
            ],
            how="vertical",
        )
        .unique(subset=duplicate_key_columns(), keep="first")
        .sort(["complex_id", "chain", "target_species", "negative_partner_uniprot"])
    )


def export_status_counts(preflight: pl.DataFrame) -> dict[str, int]:
    if preflight.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in preflight.group_by("export_status").len().iter_rows(named=True):
        counts[_as_str(row, "export_status")] = int(row["len"])

    return counts


@app.command()
def main(
    curated_orthologs: Path = DEFAULT_CURATED_ORTHOLOGS,
    existing_pairs: Path = DEFAULT_EXISTING_NEGATOME_PAIRS,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    preflight_output: Path = DEFAULT_PREFLIGHT_OUTPUT,
    merged_output: Path = DEFAULT_MERGED_OUTPUT,
    yes_write: bool = False,
) -> None:
    """Preflight/export NEGATOME rows for curated ortholog candidates."""
    if not curated_orthologs.exists():
        raise FileNotFoundError(f"Missing curated ortholog input: {curated_orthologs}")

    candidates = pl.read_csv(curated_orthologs)
    existing = pl.read_csv(existing_pairs) if existing_pairs.exists() else None

    preflight = build_curated_negatome_control_preflight(
        curated_candidates=candidates,
        existing_pairs=existing,
    )

    preflight_output.parent.mkdir(parents=True, exist_ok=True)
    preflight.write_csv(preflight_output)

    typer.echo(f"primary curated candidates audited: {preflight.height}")
    for status, count in sorted(export_status_counts(preflight).items()):
        typer.echo(f"{status}: {count}")

    missing = preflight.filter(pl.col("export_status") != "present_existing")
    if missing.height > 0:
        typer.echo("Curated NEGATOME rows needing action:")
        for row in missing.iter_rows(named=True):
            typer.echo(
                "  "
                f"{row['complex_id']} "
                f"{row['chain']} "
                f"{row['target_species']} "
                f"source={row['source_uniprot']} "
                f"status={row['export_status']}"
            )

    typer.echo(f"Wrote curated NEGATOME preflight -> {preflight_output}")

    if not yes_write:
        typer.echo("Dry run only. Pass --yes-write to write merged NEGATOME control pairs.")
        return

    curated_pairs = build_curated_ortholog_negatome_control_pairs(
        curated_candidates=candidates,
        cache_dir=cache_dir,
    )
    merged = merge_curated_negatome_control_pairs(
        existing_pairs=existing,
        curated_pairs=curated_pairs,
    )

    merged_output.parent.mkdir(parents=True, exist_ok=True)
    merged.write_csv(merged_output)
    typer.echo(f"Wrote merged NEGATOME control pairs -> {merged_output}")


if __name__ == "__main__":
    app()
