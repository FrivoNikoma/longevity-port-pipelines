from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer

EXPECTED_COMMAND_FAMILY = "curated_embedding_preflight_dry_run_wrapper"
SCRIPT_ENTRY_POINT = "g3sx30-wrapper-dry-run"
CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
TARGET_ACCESSION = "G3SX30"
TARGET_ACCESSION_DB = "UniProtKB TrEMBL"
TARGET_SPECIES = "Loxodonta africana"
TARGET_TAXID = 9785
GENE_SYMBOL = "MDM2"
REVIEWED_SEQUENCE_LENGTH = 492
REVIEWED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"

DEFAULT_MANIFEST = Path("data/input/g3sx30_dry_run_preflight_manifest.csv")

FORBIDDEN_SUBSTITUTE_COMMANDS = (
    "curated-embedding-preflight",
    "curated_embedding_preflight",
    "curated-embedding-single",
    "curated_embedding_single",
)

FUTURE_HELP_ONLY_OPTIONS = (
    "--manifest",
    "--manifest-row-index",
    "--output-path",
)

FORBIDDEN_RUNTIME_ACTIONS = (
    "wrapper execution",
    "dry-run execution",
    "live execution",
    "Biohub / ESMC call",
    "embedding generation",
    ".npy artifact creation",
    "data/output artifact commit",
    "ready_for_preflight promotion",
    "Gate 8 promotion",
    "Gate 9 promotion",
    "biological claim",
)

app = typer.Typer(
    add_completion=False,
    help=(
        "Runtime-blocked G3SX30 manifest-aware wrapper entry-point boundary. "
        "Use only for future help observation; this command does not execute "
        "the wrapper or generate embeddings."
    ),
)


def build_boundary_status() -> dict[str, Any]:
    return {
        "entrypoint_boundary_status": "source_entrypoint_boundary_runtime_blocked",
        "script_entry_point": SCRIPT_ENTRY_POINT,
        "expected_command_family": EXPECTED_COMMAND_FAMILY,
        "candidate_id": CANDIDATE_ID,
        "target_accession": TARGET_ACCESSION,
        "target_accession_db": TARGET_ACCESSION_DB,
        "target_species": TARGET_SPECIES,
        "target_taxid": TARGET_TAXID,
        "gene_symbol": GENE_SYMBOL,
        "reviewed_sequence_length": REVIEWED_SEQUENCE_LENGTH,
        "reviewed_sequence_sha256": REVIEWED_SEQUENCE_SHA256,
        "manifest": DEFAULT_MANIFEST.as_posix(),
        "manifest_row_index": 1,
        "actual_cli_help_observed": False,
        "actual_command_verified": False,
        "command_selected_for_execution": False,
        "output_path_selected_for_execution": False,
        "execution_plan_materialized": False,
        "wrapper_execution_authorized": False,
        "dry_run_execution_authorized": False,
        "live_execution_authorized": False,
        "ready_for_preflight_authorized": False,
        "biohub_esmc_authorized": False,
        "embedding_generation_authorized": False,
        "npy_artifact_authorized": False,
        "data_output_artifact_commit_authorized": False,
        "gate8_promotion_authorized": False,
        "gate9_promotion_authorized": False,
        "biological_claim_authorized": False,
        "runtime_still_blocked": True,
        "ordinary_scripts_valid_as_substitutes": False,
        "future_safe_observation": f"uv run {SCRIPT_ENTRY_POINT} --help",
    }


def blocked_runtime_message() -> str:
    return (
        f"{SCRIPT_ENTRY_POINT} is a runtime-blocked source entry-point boundary. "
        "Only future help observation is allowed. Do not execute the wrapper, "
        "do not run a dry-run, do not call Biohub / ESMC, and do not generate "
        "embeddings."
    )


@app.command()
def main(
    manifest: Annotated[
        Path,
        typer.Option(
            "--manifest",
            help=(
                "Future G3SX30 manifest path for interface documentation only. "
                "This boundary does not read or execute the manifest."
            ),
        ),
    ] = DEFAULT_MANIFEST,
    manifest_row_index: Annotated[
        int,
        typer.Option(
            "--manifest-row-index",
            min=1,
            help=(
                "Future manifest row index for interface documentation only. "
                "This boundary does not execute any manifest row."
            ),
        ),
    ] = 1,
    output_path: Annotated[
        Path | None,
        typer.Option(
            "--output-path",
            help=(
                "Future non-committed output path for interface documentation only. "
                "This boundary does not write outputs."
            ),
        ),
    ] = None,
) -> None:
    _ = (manifest, manifest_row_index, output_path)
    typer.echo(blocked_runtime_message())
    raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
