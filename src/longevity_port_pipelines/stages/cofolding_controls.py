"""Audit PINDER rows before using them as Boltz cofolding controls.

This stage is deliberately cheap: it does not call Boltz and does not spend
prediction credits. It annotates high-confidence PINDER pairs with UniProt
metadata so we can choose sensible positive controls for cofolding calibration.

Why this exists
---------------
A PINDER row is a structural chain-pair, not necessarily a biologically
meaningful receptor/ligand pair. High-confidence PINDER rows can include
homomers, capsids, viral assemblies, repeated chains, or non-human proteins.
Before using a pair as a Boltz positive control, we need to know:

- are both UniProt IDs defined?
- is this a homomer/same-UniProt repeated chain?
- is this human-human?
- does it look viral/capsid-like?
- is it a plausible human heterodimer control?

Usage
-----
uv run python -m longevity_port_pipelines.stages.cofolding_controls

Outputs
-------
data/output/pinder_cofolding_control_audit.csv
"""

from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import polars as pl
import typer

app = typer.Typer(help="Audit PINDER rows for Boltz cofolding control selection.")

DEFAULT_PINDER_DATA_DIR = Path("data/interim/pinder/data")
DEFAULT_OUTPUT = Path("data/output/pinder_cofolding_control_audit.csv")
DEFAULT_METADATA_CACHE = Path("data/output/uniprot_metadata_cache.json")

PINDER_DATA_DIR_OPTION = typer.Option(
    DEFAULT_PINDER_DATA_DIR,
    "--pinder-data-dir",
    help="Directory containing PINDER parquet files.",
)
OUTPUT_OPTION = typer.Option(
    DEFAULT_OUTPUT,
    "--output",
    help="CSV output path for the annotated audit.",
)
METADATA_CACHE_OPTION = typer.Option(
    DEFAULT_METADATA_CACHE,
    "--metadata-cache",
    help="Local JSON cache for UniProt metadata.",
)


@dataclass(frozen=True)
class UniProtMetadata:
    """Small subset of UniProt metadata needed for control selection."""

    accession: str
    taxid: int | None
    organism: str | None
    protein_name: str | None


def parse_pinder_uniprots(pinder_id: str) -> tuple[str, str]:
    """Return the two UniProt accessions encoded in a PINDER id.

    Example:
    3lqz__B1_P04440--3lqz__A1_P20036 -> ("P04440", "P20036")

    Note: these are structural pair sides, not necessarily biological
    receptor/ligand roles.
    """
    halves = pinder_id.split("--", 1)
    if len(halves) != 2:
        raise ValueError(f"Invalid PINDER id: {pinder_id}")

    receptor_uniprot = halves[0].rsplit("_", 1)[-1]
    ligand_uniprot = halves[1].rsplit("_", 1)[-1]

    if not receptor_uniprot or not ligand_uniprot:
        raise ValueError(f"Could not parse UniProt IDs from: {pinder_id}")

    return receptor_uniprot, ligand_uniprot


def fetch_uniprot_metadata(accession: str) -> UniProtMetadata:
    """Fetch organism/protein metadata for one UniProt accession."""
    if accession == "UNDEFINED":
        return UniProtMetadata(
            accession=accession,
            taxid=None,
            organism=None,
            protein_name=None,
        )

    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"

    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    organism = data.get("organism", {})
    protein_description = data.get("proteinDescription", {})

    recommended_name = protein_description.get("recommendedName", {})
    full_name = recommended_name.get("fullName", {})
    protein_name = full_name.get("value")

    if protein_name is None:
        submission_names = protein_description.get("submissionNames", [])
        if submission_names:
            protein_name = submission_names[0].get("fullName", {}).get("value")

    taxid = organism.get("taxonId")
    return UniProtMetadata(
        accession=accession,
        taxid=int(taxid) if taxid is not None else None,
        organism=organism.get("scientificName"),
        protein_name=protein_name,
    )


def load_metadata_cache(path: Path) -> dict[str, UniProtMetadata]:
    """Load a local UniProt metadata cache if it exists."""
    if not path.exists():
        return {}

    raw = json.loads(path.read_text(encoding="utf-8"))
    cache: dict[str, UniProtMetadata] = {}

    for accession, item in raw.items():
        cache[accession] = UniProtMetadata(
            accession=str(item["accession"]),
            taxid=item["taxid"],
            organism=item["organism"],
            protein_name=item["protein_name"],
        )

    return cache


def save_metadata_cache(path: Path, cache: dict[str, UniProtMetadata]) -> None:
    """Write UniProt metadata cache as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {accession: asdict(meta) for accession, meta in cache.items()}
    path.write_text(json.dumps(serializable, indent=2, sort_keys=True), encoding="utf-8")


def load_high_confidence_pinder_candidates(
    pinder_data_dir: Path,
    *,
    min_probability: float,
    min_buried_sasa: float,
    min_contacts: int,
    max_chain_length: int,
    top_n: int,
) -> pl.DataFrame:
    """Load and rank high-confidence PINDER rows for possible controls."""
    frames: list[pl.DataFrame] = []

    for path in pinder_data_dir.glob("*.parquet"):
        df = pl.read_parquet(path)

        required = {
            "id",
            "receptor_sequence",
            "ligand_sequence",
            "probability",
            "buried_sasa",
            "intermolecular_contacts",
            "n_residue_pairs",
            "link_density",
            "planarity",
        }
        missing = sorted(required - set(df.columns))
        if missing:
            raise ValueError(f"{path} is missing required columns: {missing}")

        part = (
            df.with_columns(
                pl.col("receptor_sequence").str.len_chars().alias("receptor_len"),
                pl.col("ligand_sequence").str.len_chars().alias("ligand_len"),
            )
            .filter(
                (pl.col("probability") >= min_probability)
                & (pl.col("buried_sasa") >= min_buried_sasa)
                & (pl.col("intermolecular_contacts") >= min_contacts)
                & (pl.col("receptor_len") <= max_chain_length)
                & (pl.col("ligand_len") <= max_chain_length)
            )
            .select(
                [
                    "id",
                    "probability",
                    "buried_sasa",
                    "intermolecular_contacts",
                    "n_residue_pairs",
                    "receptor_len",
                    "ligand_len",
                    "link_density",
                    "planarity",
                ]
            )
        )

        if not part.is_empty():
            frames.append(part)

    if not frames:
        return pl.DataFrame(
            schema={
                "id": pl.String,
                "probability": pl.Float64,
                "buried_sasa": pl.Float64,
                "intermolecular_contacts": pl.Int64,
                "n_residue_pairs": pl.Int64,
                "receptor_len": pl.Int64,
                "ligand_len": pl.Int64,
                "link_density": pl.Float64,
                "planarity": pl.Float64,
            }
        )

    return (
        pl.concat(frames)
        .unique(subset=["id"])
        .sort(["probability", "buried_sasa"], descending=True)
        .head(top_n)
    )


def add_parsed_uniprot_columns(candidates: pl.DataFrame) -> pl.DataFrame:
    """Add parsed UniProt IDs and simple structural-pair flags."""
    rows: list[dict[str, Any]] = []

    for row in candidates.iter_rows(named=True):
        receptor_uniprot, ligand_uniprot = parse_pinder_uniprots(str(row["id"]))

        rows.append(
            {
                **row,
                "receptor_uniprot": receptor_uniprot,
                "ligand_uniprot": ligand_uniprot,
                "same_uniprot": receptor_uniprot == ligand_uniprot,
                "has_undefined": receptor_uniprot == "UNDEFINED" or ligand_uniprot == "UNDEFINED",
            }
        )

    return pl.DataFrame(rows) if rows else candidates


def unique_defined_accessions(parsed: pl.DataFrame) -> list[str]:
    """Return sorted UniProt accessions to annotate."""
    accessions: set[str] = set()

    if parsed.is_empty():
        return []

    for row in parsed.iter_rows(named=True):
        for column in ("receptor_uniprot", "ligand_uniprot"):
            accession = str(row[column])
            if accession != "UNDEFINED":
                accessions.add(accession)

    return sorted(accessions)


def fetch_metadata_for_accessions(
    accessions: list[str],
    *,
    cache_path: Path,
    sleep_seconds: float,
) -> dict[str, UniProtMetadata]:
    """Fetch UniProt metadata, reusing a local JSON cache."""
    cache = load_metadata_cache(cache_path)

    for index, accession in enumerate(accessions, start=1):
        if accession in cache:
            typer.echo(f"[{index}/{len(accessions)}] {accession}: cached")
            continue

        try:
            cache[accession] = fetch_uniprot_metadata(accession)
            typer.echo(f"[{index}/{len(accessions)}] {accession}: fetched")
            time.sleep(sleep_seconds)
        except Exception as exc:
            typer.echo(f"[{index}/{len(accessions)}] {accession}: FAILED: {exc}", err=True)
            cache[accession] = UniProtMetadata(
                accession=accession,
                taxid=None,
                organism=None,
                protein_name=None,
            )

    save_metadata_cache(cache_path, cache)
    return cache


def looks_viral_or_capsid(
    receptor_organism: str | None,
    ligand_organism: str | None,
    receptor_protein_name: str | None,
    ligand_protein_name: str | None,
) -> bool:
    """Heuristic flag for viral/capsid-like technical assemblies."""
    text = " ".join(
        item or ""
        for item in [
            receptor_organism,
            ligand_organism,
            receptor_protein_name,
            ligand_protein_name,
        ]
    ).lower()

    markers = [
        "virus",
        "viral",
        "phage",
        "capsid",
        "coat protein",
        "syncytial",
    ]
    return any(marker in text for marker in markers)


def annotate_candidates(
    parsed: pl.DataFrame,
    metadata_by_accession: dict[str, UniProtMetadata],
) -> pl.DataFrame:
    """Add UniProt metadata and control-selection flags."""
    rows: list[dict[str, Any]] = []

    for row in parsed.iter_rows(named=True):
        receptor_uniprot = str(row["receptor_uniprot"])
        ligand_uniprot = str(row["ligand_uniprot"])

        receptor_meta = metadata_by_accession.get(
            receptor_uniprot,
            UniProtMetadata(receptor_uniprot, None, None, None),
        )
        ligand_meta = metadata_by_accession.get(
            ligand_uniprot,
            UniProtMetadata(ligand_uniprot, None, None, None),
        )

        human_human = receptor_meta.taxid == 9606 and ligand_meta.taxid == 9606
        same_uniprot = bool(row["same_uniprot"])
        has_undefined = bool(row["has_undefined"])
        likely_viral_or_capsid = looks_viral_or_capsid(
            receptor_meta.organism,
            ligand_meta.organism,
            receptor_meta.protein_name,
            ligand_meta.protein_name,
        )

        rows.append(
            {
                **row,
                "receptor_taxid": receptor_meta.taxid,
                "ligand_taxid": ligand_meta.taxid,
                "receptor_organism": receptor_meta.organism,
                "ligand_organism": ligand_meta.organism,
                "receptor_protein_name": receptor_meta.protein_name,
                "ligand_protein_name": ligand_meta.protein_name,
                "same_taxid": receptor_meta.taxid == ligand_meta.taxid
                and receptor_meta.taxid is not None,
                "human_human": human_human,
                "likely_viral_or_capsid": likely_viral_or_capsid,
                "human_heterodimer_control": human_human
                and not same_uniprot
                and not has_undefined
                and not likely_viral_or_capsid,
                "technical_homomer_control": same_uniprot
                and not has_undefined
                and not likely_viral_or_capsid,
            }
        )

    return pl.DataFrame(rows) if rows else parsed


def human_heterodimer_controls(annotated: pl.DataFrame) -> pl.DataFrame:
    """Return plausible human-human heterodimer controls."""
    if annotated.is_empty():
        return annotated

    return annotated.filter(pl.col("human_heterodimer_control")).sort(
        ["probability", "buried_sasa"], descending=True
    )


@app.command()
def main(
    pinder_data_dir: Path = PINDER_DATA_DIR_OPTION,
    output: Path = OUTPUT_OPTION,
    metadata_cache: Path = METADATA_CACHE_OPTION,
    top_n: int = typer.Option(
        200,
        "--top-n",
        help="Number of high-confidence PINDER rows to annotate.",
    ),
    min_probability: float = typer.Option(
        0.75,
        "--min-probability",
        help="Minimum PINDER probability for candidate controls.",
    ),
    min_buried_sasa: float = typer.Option(
        1200.0,
        "--min-buried-sasa",
        help="Minimum buried SASA for candidate controls.",
    ),
    min_contacts: int = typer.Option(
        50,
        "--min-contacts",
        help="Minimum intermolecular contacts for candidate controls.",
    ),
    max_chain_length: int = typer.Option(
        800,
        "--max-chain-length",
        help="Maximum receptor/ligand sequence length.",
    ),
    sleep_seconds: float = typer.Option(
        0.1,
        "--sleep-seconds",
        help="Pause between UniProt API calls.",
    ),
) -> None:
    """Annotate high-confidence PINDER rows for cofolding-control selection."""
    candidates = load_high_confidence_pinder_candidates(
        pinder_data_dir,
        min_probability=min_probability,
        min_buried_sasa=min_buried_sasa,
        min_contacts=min_contacts,
        max_chain_length=max_chain_length,
        top_n=top_n,
    )

    if candidates.is_empty():
        typer.echo("No high-confidence PINDER candidates found.")
        raise typer.Exit(0)

    parsed = add_parsed_uniprot_columns(candidates)
    accessions = unique_defined_accessions(parsed)

    typer.echo(f"Annotating {len(parsed)} PINDER rows.")
    typer.echo(f"Fetching/checking metadata for {len(accessions)} UniProt accessions.")

    metadata = fetch_metadata_for_accessions(
        accessions,
        cache_path=metadata_cache,
        sleep_seconds=sleep_seconds,
    )
    annotated = annotate_candidates(parsed, metadata)

    output.parent.mkdir(parents=True, exist_ok=True)
    annotated.write_csv(output)

    typer.echo(f"\nSaved audit to: {output}")

    typer.echo("\nTop plausible human-human heterodimer controls:")
    controls = human_heterodimer_controls(annotated)
    if controls.is_empty():
        typer.echo("  none found with current thresholds")
    else:
        display_cols = [
            "id",
            "probability",
            "buried_sasa",
            "intermolecular_contacts",
            "receptor_len",
            "ligand_len",
            "receptor_uniprot",
            "ligand_uniprot",
            "receptor_protein_name",
            "ligand_protein_name",
        ]
        with pl.Config(tbl_cols=-1, tbl_width_chars=240):
            print(controls.select(display_cols).head(30))


if __name__ == "__main__":
    app()
