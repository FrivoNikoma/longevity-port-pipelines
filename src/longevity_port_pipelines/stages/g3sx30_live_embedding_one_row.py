from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.embed import (
    embed_or_load_sequence,
    embedding_path,
    get_biohub_token,
)

DEFAULT_MANIFEST = Path("data/input/g3sx30_dry_run_preflight_manifest.csv")
DEFAULT_APPROVAL_DOC = Path("docs/current_gate_map.md")
DEFAULT_REVIEWED_SEQUENCE_FASTA = Path(
    "D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta"
)
DEFAULT_OUTPUT_DIR = Path("data/output")

EXPECTED_MANIFEST_ROW_INDEX = 1
EXPECTED_CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
EXPECTED_TARGET_ACCESSION = "G3SX30"
EXPECTED_TARGET_TAXID = 9785
EXPECTED_GENE_SYMBOL = "MDM2"
EXPECTED_SEQUENCE_LENGTH = 492
EXPECTED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
EXPECTED_CHAIN = "mdm2"

APPROVAL_REQUIRED_STRINGS = (
    "next_data_step_decision=approve_one_row_live_embedding_for_next_pr",
    "live_embedding_authorized_for_next_pr=true",
    "max_live_batch_size_for_next_pr=1",
    "allowed_next_action_after_review=execute_one_row_g3sx30_live_embedding_with_strict_guardrails",
    "Execute one-row G3SX30 live embedding with strict guardrails",
)

app = typer.Typer(add_completion=False)


@dataclass(frozen=True)
class ReviewedSequence:
    header: str
    sequence: str
    length: int
    sha256: str


@dataclass(frozen=True)
class G3SX30LiveEmbeddingPlan:
    manifest_path: Path
    manifest_row_index: int
    approval_doc: Path
    reviewed_sequence_fasta: Path
    candidate_id: str
    target_accession: str
    target_taxid: int
    gene_symbol: str
    reviewed_sequence: ReviewedSequence
    model_name: str
    output_dir: Path
    embedding_path: Path


@dataclass(frozen=True)
class G3SX30LiveEmbeddingResult:
    plan: G3SX30LiveEmbeddingPlan
    status: str
    embedding_shape: str | None = None


def _require(row: dict[str, str], column: str) -> str:
    value = row.get(column)
    if value is None or value.strip() == "":
        raise ValueError(f"Missing required manifest column value: {column}")
    return value.strip()


def _read_manifest_row(manifest_path: Path, row_index: int) -> dict[str, str]:
    if row_index != EXPECTED_MANIFEST_ROW_INDEX:
        raise ValueError(
            "G3SX30 live embedding wrapper is one-row only and requires "
            f"manifest_row_index={EXPECTED_MANIFEST_ROW_INDEX}; got {row_index}"
        )
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing G3SX30 manifest: {manifest_path}")
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one G3SX30 manifest row, found {len(rows)}")
    return rows[0]


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Expected boolean string, got {value!r}")


def validate_approval_doc(approval_doc: Path) -> None:
    if not approval_doc.exists():
        raise FileNotFoundError(f"Missing approval document: {approval_doc}")
    text = approval_doc.read_text(encoding="utf-8")
    missing = [required for required in APPROVAL_REQUIRED_STRINGS if required not in text]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(
            f"Approval document is missing required G3SX30 live approval: {missing_text}"
        )


def load_reviewed_sequence_fasta(path: Path) -> ReviewedSequence:
    if not path.exists():
        raise FileNotFoundError(f"Missing external reviewed G3SX30 FASTA artifact: {path}")
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines or not lines[0].startswith(">"):
        raise ValueError(f"Reviewed sequence artifact is not FASTA: {path}")
    header = lines[0]
    sequence = "".join(lines[1:]).replace(" ", "").replace("\t", "").upper()
    sha256 = hashlib.sha256(sequence.encode("utf-8")).hexdigest()
    if EXPECTED_TARGET_ACCESSION not in header:
        raise ValueError(f"FASTA header does not contain {EXPECTED_TARGET_ACCESSION}: {header}")
    if f"OX={EXPECTED_TARGET_TAXID}" not in header:
        raise ValueError(f"FASTA header does not contain OX={EXPECTED_TARGET_TAXID}: {header}")
    if f"GN={EXPECTED_GENE_SYMBOL}" not in header:
        raise ValueError(f"FASTA header does not contain GN={EXPECTED_GENE_SYMBOL}: {header}")
    if len(sequence) != EXPECTED_SEQUENCE_LENGTH:
        raise ValueError(
            "Reviewed G3SX30 sequence length mismatch: "
            f"expected={EXPECTED_SEQUENCE_LENGTH}, actual={len(sequence)}"
        )
    if sha256 != EXPECTED_SEQUENCE_SHA256:
        raise ValueError(
            "Reviewed G3SX30 sequence SHA256 mismatch: "
            f"expected={EXPECTED_SEQUENCE_SHA256}, actual={sha256}"
        )
    return ReviewedSequence(header=header, sequence=sequence, length=len(sequence), sha256=sha256)


def build_g3sx30_live_embedding_plan(
    *,
    manifest_path: Path,
    manifest_row_index: int,
    approval_doc: Path,
    reviewed_sequence_fasta: Path,
    output_dir: Path,
    model_name: str,
) -> G3SX30LiveEmbeddingPlan:
    validate_approval_doc(approval_doc)
    row = _read_manifest_row(manifest_path=manifest_path, row_index=manifest_row_index)
    candidate_id = _require(row, "candidate_id")
    target_accession = _require(row, "target_accession")
    target_taxid = int(_require(row, "target_taxid"))
    gene_symbol = _require(row, "gene_symbol")
    reviewed_length = int(_require(row, "reviewed_sequence_length"))
    reviewed_sha256 = _require(row, "reviewed_sequence_sha256")
    expected_pairs: tuple[tuple[str, object, object], ...] = (
        ("candidate_id", candidate_id, EXPECTED_CANDIDATE_ID),
        ("target_accession", target_accession, EXPECTED_TARGET_ACCESSION),
        ("target_taxid", target_taxid, EXPECTED_TARGET_TAXID),
        ("gene_symbol", gene_symbol, EXPECTED_GENE_SYMBOL),
        ("reviewed_sequence_length", reviewed_length, EXPECTED_SEQUENCE_LENGTH),
        ("reviewed_sequence_sha256", reviewed_sha256, EXPECTED_SEQUENCE_SHA256),
    )
    for label, actual, expected in expected_pairs:
        if actual != expected:
            raise ValueError(f"Unexpected {label} for G3SX30 live run: {actual}")
    if not _parse_bool(_require(row, "dry_run_only")):
        raise ValueError("Expected source manifest dry_run_only=true as identity-only source row")
    if int(_require(row, "max_live_batch_size")) != 0:
        raise ValueError("Expected source manifest max_live_batch_size=0 before wrapper override")
    if _parse_bool(_require(row, "ready_for_preflight_after_manifest")):
        raise ValueError("Source manifest must not mark ready_for_preflight")
    for column in (
        "sequence_fetch_allowed",
        "biohub_call_allowed",
        "esmc_call_allowed",
        "embedding_generation_allowed",
        "curated_embedding_preflight_allowed",
        "curated_embedding_single_allowed",
    ):
        if _parse_bool(_require(row, column)):
            raise ValueError(f"Source manifest must keep {column}=false")
    reviewed_sequence = load_reviewed_sequence_fasta(reviewed_sequence_fasta)
    path = embedding_path(
        output_dir=output_dir,
        model_name=model_name,
        complex_id=candidate_id,
        chain=EXPECTED_CHAIN,
        species_taxid=target_taxid,
    )
    return G3SX30LiveEmbeddingPlan(
        manifest_path=manifest_path,
        manifest_row_index=manifest_row_index,
        approval_doc=approval_doc,
        reviewed_sequence_fasta=reviewed_sequence_fasta,
        candidate_id=candidate_id,
        target_accession=target_accession,
        target_taxid=target_taxid,
        gene_symbol=gene_symbol,
        reviewed_sequence=reviewed_sequence,
        model_name=model_name,
        output_dir=output_dir,
        embedding_path=path,
    )


def run_g3sx30_live_embedding(
    plan: G3SX30LiveEmbeddingPlan,
    *,
    api_url: str,
    yes_live: bool,
    max_live_batch_size: int,
    skip_existing: bool = True,
) -> G3SX30LiveEmbeddingResult:
    if max_live_batch_size != 1:
        raise ValueError(
            f"G3SX30 live wrapper requires max_live_batch_size=1; got {max_live_batch_size}"
        )
    if not yes_live:
        status = "dry_run_present" if plan.embedding_path.exists() else "dry_run_missing"
        return G3SX30LiveEmbeddingResult(plan=plan, status=status)
    if skip_existing and plan.embedding_path.exists():
        return G3SX30LiveEmbeddingResult(plan=plan, status="skipped_existing")
    load_dotenv(dotenv_path=Path(".env"))
    token = get_biohub_token()
    embedding = embed_or_load_sequence(
        complex_id=plan.candidate_id,
        chain=EXPECTED_CHAIN,
        sequence=plan.reviewed_sequence.sequence,
        species_taxid=plan.target_taxid,
        model=plan.model_name,
        api_url=api_url,
        token=token,
        output_dir=plan.output_dir,
        is_predicted_structure=True,
    )
    shape = f"{embedding.embeddings.shape[0]}x{embedding.embeddings.shape[1]}"
    return G3SX30LiveEmbeddingResult(plan=plan, status="live_completed", embedding_shape=shape)


def _echo_plan(plan: G3SX30LiveEmbeddingPlan) -> None:
    typer.echo(f"manifest_path: {plan.manifest_path}")
    typer.echo(f"manifest_row_index: {plan.manifest_row_index}")
    typer.echo(f"approval_doc: {plan.approval_doc}")
    typer.echo(f"reviewed_sequence_fasta: {plan.reviewed_sequence_fasta}")
    typer.echo(f"candidate_id: {plan.candidate_id}")
    typer.echo(f"chain: {EXPECTED_CHAIN}")
    typer.echo(f"target_accession: {plan.target_accession}")
    typer.echo(f"target_taxid: {plan.target_taxid}")
    typer.echo(f"gene_symbol: {plan.gene_symbol}")
    typer.echo(f"model_name: {plan.model_name}")
    typer.echo(f"sequence_length: {plan.reviewed_sequence.length}")
    typer.echo(f"sequence_sha256: {plan.reviewed_sequence.sha256}")
    typer.echo(f"embedding_path: {plan.embedding_path}")
    typer.echo(f"embedding_exists: {plan.embedding_path.exists()}")


@app.command()
def main(
    manifest: Annotated[
        Path, typer.Option(help="G3SX30 dry-run preflight manifest CSV")
    ] = DEFAULT_MANIFEST,
    manifest_row_index: Annotated[
        int, typer.Option(help="One-based G3SX30 manifest row index")
    ] = EXPECTED_MANIFEST_ROW_INDEX,
    approval_doc: Annotated[
        Path,
        typer.Option(help="Approval doc containing one-row G3SX30 live embedding authorization"),
    ] = DEFAULT_APPROVAL_DOC,
    reviewed_sequence_fasta: Annotated[
        Path,
        typer.Option(help="External non-committed reviewed G3SX30 FASTA artifact"),
    ] = DEFAULT_REVIEWED_SEQUENCE_FASTA,
    output_dir: Annotated[
        Path, typer.Option(help="Pipeline output directory")
    ] = DEFAULT_OUTPUT_DIR,
    model_name: Annotated[str | None, typer.Option(help="ESMC model name override")] = None,
    biohub_api_url: Annotated[str | None, typer.Option(help="Biohub API URL override")] = None,
    max_live_batch_size: Annotated[
        int,
        typer.Option(help="Required one-row live batch-size guardrail"),
    ] = 1,
    yes_live: Annotated[
        bool,
        typer.Option(
            "--yes-live", help="Actually call Biohub/ESMC for the one reviewed G3SX30 row."
        ),
    ] = False,
    skip_existing: Annotated[
        bool,
        typer.Option(
            "--skip-existing/--no-skip-existing", help="Do not rewrite existing embedding."
        ),
    ] = True,
) -> None:
    """Execute or dry-run exactly one guarded G3SX30 live embedding."""
    cfg = PipelineConfig(output_dir=output_dir)
    resolved_model_name = model_name or cfg.esmc_model
    resolved_api_url = biohub_api_url or cfg.biohub_api_url
    plan = build_g3sx30_live_embedding_plan(
        manifest_path=manifest,
        manifest_row_index=manifest_row_index,
        approval_doc=approval_doc,
        reviewed_sequence_fasta=reviewed_sequence_fasta,
        output_dir=output_dir,
        model_name=resolved_model_name,
    )
    typer.echo("G3SX30 one-row live embedding plan:")
    _echo_plan(plan)
    if yes_live:
        typer.echo("mode: live")
    else:
        typer.echo("mode: dry-run; add --yes-live to call Biohub/ESMC")
    result = run_g3sx30_live_embedding(
        plan,
        api_url=resolved_api_url,
        yes_live=yes_live,
        max_live_batch_size=max_live_batch_size,
        skip_existing=skip_existing,
    )
    typer.echo(f"status: {result.status}")
    if result.embedding_shape is not None:
        typer.echo(f"embedding_shape: {result.embedding_shape}")


if __name__ == "__main__":
    app()
