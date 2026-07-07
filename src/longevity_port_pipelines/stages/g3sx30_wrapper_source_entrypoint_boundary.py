from __future__ import annotations

import csv
import json
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
REVIEWED_MANIFEST_ROW_INDEX = 1
REVIEWED_EXTERNAL_OUTPUT_PATH = Path(
    "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
)

FORBIDDEN_SUBSTITUTE_COMMANDS = (
    "curated-embedding-preflight",
    "curated_embedding_preflight",
    "curated-embedding-single",
    "curated_embedding_single",
)

REVIEWED_DRY_RUN_OPTIONS = (
    "--manifest",
    "--manifest-row-index",
    "--output-path",
)

FORBIDDEN_NON_DRY_RUN_ACTIONS = (
    "live execution",
    "Biohub / ESMC call",
    "embedding generation",
    ".npy artifact creation",
    "data/output artifact commit",
    "ready_for_preflight promotion",
    "Gate 8 promotion",
    "Gate 9 promotion",
    "Boltz call",
    "AF3 call",
    "Chai call",
    "enrichment rerun",
    "contrast rerun",
    "biological claim",
)

app = typer.Typer(
    add_completion=False,
    help=(
        "Reviewed G3SX30 external-output dry-run writer. This command executes only "
        "the reviewed dry-run path, writes a small JSON observation to the reviewed "
        "external output path, and never calls Biohub / ESMC or generates embeddings."
    ),
)


def reviewed_output_path_text() -> str:
    return REVIEWED_EXTERNAL_OUTPUT_PATH.as_posix()


def reviewed_command_form(output_path: Path | None = None) -> str:
    selected_output_path = output_path or REVIEWED_EXTERNAL_OUTPUT_PATH
    return (
        f"uv run {SCRIPT_ENTRY_POINT} "
        f"--manifest {DEFAULT_MANIFEST.as_posix()} "
        f"--manifest-row-index {REVIEWED_MANIFEST_ROW_INDEX} "
        f"--output-path {selected_output_path.as_posix()}"
    )


def build_boundary_status() -> dict[str, Any]:
    return {
        "entrypoint_boundary_status": "reviewed_external_output_dry_run_enabled",
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
        "manifest_row_index": REVIEWED_MANIFEST_ROW_INDEX,
        "reviewed_external_output_path": reviewed_output_path_text(),
        "reviewed_command_form": reviewed_command_form(),
        "actual_command_verified": True,
        "command_selected_for_execution": True,
        "output_path_selected_for_execution": True,
        "execution_plan_materialized": True,
        "wrapper_execution_authorized": True,
        "dry_run_execution_authorized": True,
        "live_execution_authorized": False,
        "manifest_execution_authorized": False,
        "ready_for_preflight_authorized": False,
        "biohub_esmc_authorized": False,
        "embedding_generation_authorized": False,
        "npy_artifact_authorized": False,
        "data_output_artifact_commit_authorized": False,
        "gate8_promotion_authorized": False,
        "gate9_promotion_authorized": False,
        "biological_claim_authorized": False,
        "runtime_still_blocked": False,
        "runtime_client_path_still_blocked": True,
        "ordinary_scripts_valid_as_substitutes": False,
        "dry_run_output_external_only": True,
    }


def dry_run_success_message(output_path: Path) -> str:
    return (
        f"{SCRIPT_ENTRY_POINT} wrote reviewed external dry-run observation to "
        f"{output_path.as_posix()}. No Biohub / ESMC call, no embedding generation, "
        "no .npy artifact, no data/output artifact, no ready_for_preflight, "
        "no Gate 8 / Gate 9, and no biological claim."
    )


def read_manifest_row(manifest: Path, row_index: int) -> dict[str, str]:
    with manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    if row_index < 1:
        raise ValueError("manifest row index is 1-based and must be positive")
    if row_index > len(rows):
        raise ValueError(f"missing manifest row index {row_index}; table has {len(rows)} rows")

    return {column: value or "" for column, value in rows[row_index - 1].items()}


def validate_reviewed_request(
    manifest: Path,
    manifest_row_index: int,
    output_path: Path,
) -> list[str]:
    errors: list[str] = []

    if manifest.as_posix() != DEFAULT_MANIFEST.as_posix():
        errors.append(
            f"manifest must be {DEFAULT_MANIFEST.as_posix()}, observed {manifest.as_posix()}"
        )

    if manifest_row_index != REVIEWED_MANIFEST_ROW_INDEX:
        errors.append(
            "manifest row index must be "
            f"{REVIEWED_MANIFEST_ROW_INDEX}, observed {manifest_row_index}"
        )

    if output_path.as_posix() != reviewed_output_path_text():
        errors.append(
            "output path must be the reviewed external path "
            f"{reviewed_output_path_text()}, observed {output_path.as_posix()}"
        )

    if "data/output" in output_path.as_posix().replace("\\", "/"):
        errors.append("output path must not be under data/output")

    if output_path.suffix == ".npy":
        errors.append("output path must not be an .npy artifact")

    return errors


def validate_manifest_row(row: dict[str, str]) -> list[str]:
    expected_values = {
        "candidate_id": CANDIDATE_ID,
        "target_accession": TARGET_ACCESSION,
        "target_accession_db": TARGET_ACCESSION_DB,
        "target_species": TARGET_SPECIES,
        "target_taxid": str(TARGET_TAXID),
        "gene_symbol": GENE_SYMBOL,
        "reviewed_sequence_length": str(REVIEWED_SEQUENCE_LENGTH),
        "reviewed_sequence_sha256": REVIEWED_SEQUENCE_SHA256,
        "dry_run_only": "true",
        "max_live_batch_size": "0",
        "ready_for_preflight_after_manifest": "false",
        "sequence_fetch_allowed": "false",
        "biohub_call_allowed": "false",
        "esmc_call_allowed": "false",
        "embedding_generation_allowed": "false",
        "curated_embedding_preflight_allowed": "false",
        "curated_embedding_single_allowed": "false",
        "claim_status": "technical_checkpoint",
    }

    errors: list[str] = []
    for column, expected_value in expected_values.items():
        observed_value = row.get(column, "").strip()
        if observed_value != expected_value:
            errors.append(
                f"expected manifest {column}={expected_value!r}, observed {observed_value!r}"
            )

    return errors


def build_dry_run_observation(
    manifest_row: dict[str, str],
    manifest: Path,
    manifest_row_index: int,
    output_path: Path,
) -> dict[str, Any]:
    return {
        "dry_run_executed": True,
        "script_entry_point": SCRIPT_ENTRY_POINT,
        "reviewed_command_form": reviewed_command_form(output_path),
        "manifest_path": manifest.as_posix(),
        "manifest_row_index": manifest_row_index,
        "candidate_id": manifest_row["candidate_id"],
        "target_accession": manifest_row["target_accession"],
        "target_accession_db": manifest_row["target_accession_db"],
        "target_species": manifest_row["target_species"],
        "target_taxid": int(manifest_row["target_taxid"]),
        "gene_symbol": manifest_row["gene_symbol"],
        "reviewed_sequence_length": int(manifest_row["reviewed_sequence_length"]),
        "reviewed_sequence_sha256": manifest_row["reviewed_sequence_sha256"],
        "dry_run_only": True,
        "max_live_batch_size": int(manifest_row["max_live_batch_size"]),
        "manifest_row_read": True,
        "manifest_row_validated": True,
        "manifest_execution_performed": False,
        "live_execution_performed": False,
        "sequence_fetch_performed": False,
        "biohub_esmc_called": False,
        "embedding_generation_performed": False,
        "curated_embedding_preflight_run": False,
        "curated_embedding_single_run": False,
        "npy_artifact_created": False,
        "data_output_artifact_created": False,
        "ready_for_preflight_promoted": False,
        "gate8_promoted": False,
        "gate9_promoted": False,
        "boltz_called": False,
        "af3_called": False,
        "chai_called": False,
        "enrichment_rerun": False,
        "contrast_rerun": False,
        "biological_claim_made": False,
        "output_path": output_path.as_posix(),
        "output_location": "external_non_committed_observation_path",
        "claim_status": "technical_checkpoint",
    }


def write_dry_run_observation(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


@app.command()
def main(
    manifest: Annotated[
        Path,
        typer.Option(
            "--manifest",
            help="Reviewed G3SX30 dry-run manifest path. Only the reviewed manifest is accepted.",
        ),
    ] = DEFAULT_MANIFEST,
    manifest_row_index: Annotated[
        int,
        typer.Option(
            "--manifest-row-index",
            min=1,
            help="Reviewed manifest row index. Only row 1 is accepted.",
        ),
    ] = REVIEWED_MANIFEST_ROW_INDEX,
    output_path: Annotated[
        Path,
        typer.Option(
            "--output-path",
            help=(
                "Reviewed external non-committed output path. Only the reviewed "
                "D:/biohub_projects/_chatgpt_observations path is accepted."
            ),
        ),
    ] = REVIEWED_EXTERNAL_OUTPUT_PATH,
) -> None:
    request_errors = validate_reviewed_request(manifest, manifest_row_index, output_path)
    if request_errors:
        for error in request_errors:
            typer.echo(f"ERROR: {error}", err=True)
        raise typer.Exit(code=2)

    manifest_row = read_manifest_row(manifest, manifest_row_index)
    manifest_errors = validate_manifest_row(manifest_row)
    if manifest_errors:
        for error in manifest_errors:
            typer.echo(f"ERROR: {error}", err=True)
        raise typer.Exit(code=2)

    payload = build_dry_run_observation(
        manifest_row=manifest_row,
        manifest=manifest,
        manifest_row_index=manifest_row_index,
        output_path=output_path,
    )
    write_dry_run_observation(payload, output_path)
    typer.echo(dry_run_success_message(output_path))


if __name__ == "__main__":
    app()
