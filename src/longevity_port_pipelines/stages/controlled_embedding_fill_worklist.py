from __future__ import annotations

from pathlib import Path
from typing import Literal

import polars as pl
import typer

DEFAULT_PREFLIGHT = Path("data/output/curated_ortholog_embedding_preflight.csv")
DEFAULT_OUTPUT = Path("data/interim/controlled_embedding_fill_worklist.csv")

CLAIM_POLICY = "no_biological_claims_until_validation"
CLAIM_STATUS = "technical_checkpoint"
FORBIDDEN_ACTIONS = (
    "Biohub call; embedding generation; data/output commit; Boltz call; "
    "enrichment rerun; contrast rerun; biological claim"
)

FillStatus = Literal[
    "ready_for_preflight",
    "needs_coverage_repair",
    "needs_source_provenance_review",
    "defer_until_gate8_ready",
    "reviewed_for_single_live_fill",
    "do_not_fill",
]

PREFLIGHT_REQUIRED_FIELDS = [
    "complex_id",
    "chain",
    "target_species",
    "source_uniprot",
    "target_species_taxid",
    "target_accession",
    "target_accession_db",
    "target_sequence_length",
    "actual_sequence_length",
    "sequence_length_status",
    "embedding_path",
    "embedding_exists",
    "embedding_status",
]

WORKLIST_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "complex_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "target_species": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "target_accession": pl.Utf8,
    "target_accession_db": pl.Utf8,
    "target_sequence_length": pl.Int64,
    "actual_sequence_length": pl.Int64,
    "sequence_length_status": pl.Utf8,
    "embedding_path": pl.Utf8,
    "embedding_exists": pl.Boolean,
    "embedding_status": pl.Utf8,
    "fill_status": pl.Utf8,
    "fill_reason": pl.Utf8,
    "gate_dependency": pl.Utf8,
    "source_provenance_status": pl.Utf8,
    "coverage_repair_status": pl.Utf8,
    "dry_run_required": pl.Boolean,
    "live_opt_in_required": pl.Boolean,
    "max_live_batch_size": pl.Int64,
    "allowed_next_action": pl.Utf8,
    "forbidden_actions": pl.Utf8,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "review_note": pl.Utf8,
}

COVERAGE_READY_STATUSES = {
    "not_needed",
    "repaired_for_planning",
    "accepted_for_planning_after_review",
}

app = typer.Typer(add_completion=False)


def empty_controlled_embedding_fill_worklist() -> pl.DataFrame:
    return pl.DataFrame(schema=WORKLIST_SCHEMA)


def validate_preflight_schema(preflight: pl.DataFrame) -> None:
    missing = [column for column in PREFLIGHT_REQUIRED_FIELDS if column not in preflight.columns]
    if missing:
        raise ValueError(f"Missing required preflight columns: {missing}")


def _as_str(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        raise ValueError(f"Missing value for {column}")
    return str(value).strip()


def _as_int(row: dict[str, object], column: str) -> int:
    value = row[column]
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        return int(value.strip())
    raise ValueError(f"Cannot interpret integer value for {column}: {value!r}")


def _as_bool(row: dict[str, object], column: str) -> bool:
    value = row[column]
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    raise ValueError(f"Cannot interpret boolean value for {column}: {value!r}")


def _candidate_id(
    *,
    candidate_set: str,
    complex_id: str,
    chain: str,
    target_species_taxid: int,
) -> str:
    return f"{candidate_set}__{complex_id}__{chain}__{target_species_taxid}"


def classify_fill_row(
    *,
    sequence_length_status: str,
    embedding_exists: bool,
    embedding_status: str,
    source_provenance_status: str,
    coverage_repair_status: str,
    gate8_ready: bool,
) -> tuple[FillStatus, str]:
    if embedding_exists or embedding_status == "present":
        return "do_not_fill", "Embedding already exists; no fill is needed."

    if coverage_repair_status == "excluded":
        return "do_not_fill", "Coverage repair status excludes this row from filling."

    if coverage_repair_status == "deferred":
        return "defer_until_gate8_ready", "Coverage repair status is deferred."

    if coverage_repair_status not in COVERAGE_READY_STATUSES:
        return "needs_coverage_repair", "Coverage/provenance repair is not complete."

    if source_provenance_status == "rejected":
        return "do_not_fill", "Source provenance was rejected."

    if source_provenance_status != "reviewed":
        return "needs_source_provenance_review", "Source provenance requires review."

    if sequence_length_status != "matches":
        return (
            "needs_source_provenance_review",
            "Recorded target sequence length does not match the actual sequence length.",
        )

    if not gate8_ready:
        return "defer_until_gate8_ready", "Upstream Gate 8 status is not ready."

    return (
        "ready_for_preflight",
        "Missing reviewed embedding may enter controlled dry-run preflight.",
    )


def _next_action(fill_status: FillStatus) -> str:
    if fill_status == "ready_for_preflight":
        return "run_curated_embedding_preflight"
    if fill_status == "needs_coverage_repair":
        return "repair_coverage_before_fill"
    if fill_status == "needs_source_provenance_review":
        return "request_source_provenance_review"
    if fill_status == "defer_until_gate8_ready":
        return "defer_until_gate8_ready"
    if fill_status == "reviewed_for_single_live_fill":
        return "consider_single_live_fill_after_human_approval"
    return "do_not_fill"


def _dry_run_required(fill_status: FillStatus) -> bool:
    return fill_status in {"ready_for_preflight", "reviewed_for_single_live_fill"}


def _max_live_batch_size(fill_status: FillStatus) -> int:
    if fill_status == "reviewed_for_single_live_fill":
        return 1
    return 0


def build_controlled_embedding_fill_worklist(
    preflight: pl.DataFrame,
    *,
    candidate_set: str,
    lane_name: str,
    source_provenance_status: str = "needs_review",
    coverage_repair_status: str = "not_needed",
    gate_dependency: str = "manual_review",
    gate8_ready: bool = True,
    review_note: str = "Generated by controlled embedding fill worklist builder.",
) -> pl.DataFrame:
    """Build a table-only controlled embedding fill worklist.

    This stage does not call Biohub, does not generate embeddings, does not rerun
    enrichment or contrast, and does not call Boltz.
    """
    validate_preflight_schema(preflight)
    if preflight.is_empty():
        return empty_controlled_embedding_fill_worklist()

    rows: list[dict[str, object]] = []
    for row in preflight.iter_rows(named=True):
        complex_id = _as_str(row, "complex_id")
        chain = _as_str(row, "chain")
        target_species_taxid = _as_int(row, "target_species_taxid")
        sequence_length_status = _as_str(row, "sequence_length_status")
        embedding_exists = _as_bool(row, "embedding_exists")
        embedding_status = _as_str(row, "embedding_status")

        fill_status, fill_reason = classify_fill_row(
            sequence_length_status=sequence_length_status,
            embedding_exists=embedding_exists,
            embedding_status=embedding_status,
            source_provenance_status=source_provenance_status,
            coverage_repair_status=coverage_repair_status,
            gate8_ready=gate8_ready,
        )

        rows.append(
            {
                "candidate_set": candidate_set,
                "lane_name": lane_name,
                "candidate_id": _candidate_id(
                    candidate_set=candidate_set,
                    complex_id=complex_id,
                    chain=chain,
                    target_species_taxid=target_species_taxid,
                ),
                "complex_id": complex_id,
                "chain": chain,
                "source_uniprot": _as_str(row, "source_uniprot"),
                "target_species": _as_str(row, "target_species"),
                "target_species_taxid": target_species_taxid,
                "target_accession": _as_str(row, "target_accession"),
                "target_accession_db": _as_str(row, "target_accession_db"),
                "target_sequence_length": _as_int(row, "target_sequence_length"),
                "actual_sequence_length": _as_int(row, "actual_sequence_length"),
                "sequence_length_status": sequence_length_status,
                "embedding_path": _as_str(row, "embedding_path"),
                "embedding_exists": embedding_exists,
                "embedding_status": embedding_status,
                "fill_status": fill_status,
                "fill_reason": fill_reason,
                "gate_dependency": gate_dependency,
                "source_provenance_status": source_provenance_status,
                "coverage_repair_status": coverage_repair_status,
                "dry_run_required": _dry_run_required(fill_status),
                "live_opt_in_required": True,
                "max_live_batch_size": _max_live_batch_size(fill_status),
                "allowed_next_action": _next_action(fill_status),
                "forbidden_actions": FORBIDDEN_ACTIONS,
                "claim_policy": CLAIM_POLICY,
                "claim_status": CLAIM_STATUS,
                "review_note": review_note,
            }
        )

    return (
        pl.DataFrame(rows, schema=WORKLIST_SCHEMA)
        .select(list(WORKLIST_SCHEMA))
        .sort(["fill_status", "complex_id", "chain", "target_species_taxid"])
    )


def fill_status_counts(worklist: pl.DataFrame) -> dict[str, int]:
    if worklist.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in worklist.group_by("fill_status").len().iter_rows(named=True):
        counts[_as_str(row, "fill_status")] = _as_int(row, "len")
    return counts


@app.command()
def main(
    preflight: Path = DEFAULT_PREFLIGHT,
    output: Path = DEFAULT_OUTPUT,
    candidate_set: str = "unknown_candidate_set",
    lane_name: str = "unknown_lane",
    source_provenance_status: str = "needs_review",
    coverage_repair_status: str = "not_needed",
    gate_dependency: str = "manual_review",
    gate8_ready: bool = True,
    review_note: str = "Generated by controlled embedding fill worklist builder.",
) -> None:
    """Build a table-only controlled embedding fill worklist from preflight rows."""
    if not preflight.exists():
        raise FileNotFoundError(f"Missing curated embedding preflight table: {preflight}")

    preflight_df = pl.read_csv(preflight)
    worklist = build_controlled_embedding_fill_worklist(
        preflight_df,
        candidate_set=candidate_set,
        lane_name=lane_name,
        source_provenance_status=source_provenance_status,
        coverage_repair_status=coverage_repair_status,
        gate_dependency=gate_dependency,
        gate8_ready=gate8_ready,
        review_note=review_note,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    worklist.write_csv(output)

    typer.echo(f"controlled embedding fill rows: {worklist.height}")
    for status, count in sorted(fill_status_counts(worklist).items()):
        typer.echo(f"{status}: {count}")
    typer.echo(f"Wrote controlled embedding fill worklist -> {output}")


if __name__ == "__main__":
    app()
