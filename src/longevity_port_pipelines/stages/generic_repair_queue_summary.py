from __future__ import annotations

from pathlib import Path
from typing import Annotated

import polars as pl
import typer

DEFAULT_SIRT6_REPAIR = Path("data/input/sirt6_candidate_coverage_repair_decisions.csv")
DEFAULT_TP53_MDM2_REPAIR = Path("data/input/tp53_mdm2_ortholog_repair_decisions.csv")
DEFAULT_REVIEW_DECISIONS = Path("data/input/generic_repair_queue_review_decisions.csv")
DEFAULT_OUTPUT = Path("data/interim/generic_repair_queue_summary.csv")

CLAIM_STATUS = "repair_worklist"
FORBIDDEN_ACTIONS = (
    "sequence fetch; manual ortholog curation; Biohub call; embedding generation; "
    "Boltz call; enrichment rerun; contrast rerun; Gate 8 promotion; "
    "Gate 9 promotion; biological claim"
)

SIRT6_REQUIRED_COLUMNS = (
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "target_species",
    "coverage_gap_status",
    "recommended_coverage_action",
    "candidate_target_uniprots",
    "repair_decision",
    "repair_priority",
    "claim_policy",
    "repair_note",
)

TP53_MDM2_REQUIRED_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "lane_name",
    "pdb_id",
    "chain",
    "source_species",
    "target_species",
    "gene_symbol",
    "source_uniprot",
    "partner_uniprot",
    "target_uniprot",
    "coverage_status",
    "provenance_status",
    "recommended_next_action",
    "repair_decision",
    "repair_status",
    "repair_priority",
    "claim_policy",
    "reviewer_note",
)

REVIEW_DECISION_REQUIRED_COLUMNS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "source_table",
    "source_row_index",
    "gene_symbol",
    "source_species",
    "target_species",
    "target_species_taxid",
    "source_uniprot",
    "partner_uniprot",
    "target_uniprot_before_review",
    "coverage_status_before_review",
    "provenance_status_before_review",
    "repair_queue_status_before_review",
    "downstream_block_status_before_review",
    "allowed_next_action_before_review",
    "claim_policy_before_review",
    "review_decision",
    "reviewed_target_uniprot",
    "reviewed_source_database",
    "reviewed_source_accession",
    "reviewed_sequence_length",
    "reviewed_taxid",
    "review_evidence_uri_or_note",
    "reviewer_note",
    "downstream_block_status_after_review",
    "allowed_next_action_after_review",
    "claim_policy_after_review",
    "claim_status_after_review",
    "forbidden_actions_after_review",
)

REVIEW_MATCH_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "source_table",
    "source_row_index",
    "target_species",
    "source_uniprot",
)

SUMMARY_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "source_table": pl.Utf8,
    "source_row_index": pl.Int64,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_species": pl.Utf8,
    "target_species": pl.Utf8,
    "gene_symbol": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "target_uniprot": pl.Utf8,
    "coverage_status": pl.Utf8,
    "provenance_status": pl.Utf8,
    "repair_decision": pl.Utf8,
    "repair_status": pl.Utf8,
    "repair_priority": pl.Utf8,
    "repair_queue_status": pl.Utf8,
    "downstream_block_status": pl.Utf8,
    "allowed_next_action": pl.Utf8,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "forbidden_actions": pl.Utf8,
    "reviewer_note": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def empty_generic_repair_queue_summary() -> pl.DataFrame:
    return pl.DataFrame(schema=SUMMARY_SCHEMA)


def read_repair_table(path: Path) -> pl.DataFrame:
    return pl.read_csv(path, infer_schema_length=0)


def validate_required_columns(
    rows: pl.DataFrame,
    *,
    required_columns: tuple[str, ...],
    table_name: str,
) -> None:
    missing = [column for column in required_columns if column not in rows.columns]
    if missing:
        raise ValueError(f"{table_name} is missing required columns: {missing}")


def _row_value(row: dict[str, object], column: str, default: str = "unresolved") -> str:
    value = row.get(column, default)
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    return text


def _sirt6_coverage_status(coverage_gap_status: str) -> str:
    if coverage_gap_status == "missing_ortholog_but_local_rows_present":
        return "local_rows_without_source_ortholog"
    if coverage_gap_status == "ortholog_and_local_rows_present":
        return "coverage_ready"
    return "unresolved_downstream_provenance"


def _sirt6_repair_status(repair_decision: str) -> str:
    if repair_decision == "needs_external_manual_sequence_review":
        return "needs_manual_review"
    if repair_decision == "no_repair_needed":
        return "not_needed"
    return "pending"


def _repair_queue_status(repair_status: str) -> str:
    if repair_status in {
        "not_needed",
        "repaired_for_planning",
        "accepted_for_planning_after_review",
    }:
        return "not_needed_or_repaired_for_planning"
    if repair_status == "needs_manual_review":
        return "blocked_pending_manual_review"
    if repair_status == "pending":
        return "blocked_pending_source_ortholog_repair"
    if repair_status == "deferred_pending_source":
        return "blocked_deferred_pending_source"
    if repair_status == "excluded_from_strict_panel":
        return "excluded_from_downstream_gates"
    return "blocked_pending_repair_review"


def _review_repair_queue_status(review_decision: str) -> str:
    if review_decision == "accepted_for_planning_after_review":
        return "reviewed_for_planning_still_policy_blocked"
    if review_decision == "rejected_after_review":
        return "excluded_from_downstream_gates"
    if review_decision == "deferred_pending_source":
        return "blocked_deferred_pending_source"
    if review_decision == "needs_second_reviewer":
        return "blocked_pending_second_reviewer"
    return "blocked_pending_repair_review"


def _downstream_block_status(repair_status: str) -> str:
    if repair_status in {
        "not_needed",
        "repaired_for_planning",
        "accepted_for_planning_after_review",
    }:
        return "not_blocked_by_repair_queue"
    return "blocked_gate4_gate5"


def _allowed_next_action(repair_queue_status: str, fallback_action: str) -> str:
    if repair_queue_status == "blocked_pending_manual_review":
        return "manual_sequence_provenance_review"
    if repair_queue_status == "blocked_pending_source_ortholog_repair":
        return "fetch_or_curate_source_ortholog"
    if repair_queue_status == "blocked_deferred_pending_source":
        return "defer_until_stronger_source"
    if repair_queue_status == "excluded_from_downstream_gates":
        return "do_not_promote_downstream"
    if repair_queue_status == "not_needed_or_repaired_for_planning":
        return "no_repair_queue_action_needed"
    return fallback_action


def _match_value(row: dict[str, object], column: str) -> str:
    value = _row_value(row, column)
    if column == "source_table":
        return value.replace("\\", "/")
    return value


def _match_key(row: dict[str, object]) -> tuple[str, ...]:
    return tuple(_match_value(row, column) for column in REVIEW_MATCH_COLUMNS)


def sirt6_rows_to_generic_summary(rows: pl.DataFrame) -> pl.DataFrame:
    validate_required_columns(
        rows,
        required_columns=SIRT6_REQUIRED_COLUMNS,
        table_name="SIRT6 repair table",
    )
    summary_rows = []
    for index, row in enumerate(rows.to_dicts(), start=1):
        coverage_status = _sirt6_coverage_status(_row_value(row, "coverage_gap_status"))
        repair_status = _sirt6_repair_status(_row_value(row, "repair_decision"))
        repair_queue_status = _repair_queue_status(repair_status)
        allowed_next_action = _allowed_next_action(
            repair_queue_status,
            _row_value(row, "recommended_coverage_action"),
        )
        summary_rows.append(
            {
                "candidate_set": "sirt6_dna_repair",
                "lane_name": "SIRT6/core3",
                "candidate_id": _row_value(row, "candidate_id"),
                "source_table": str(DEFAULT_SIRT6_REPAIR),
                "source_row_index": index,
                "pdb_id": _row_value(row, "pdb_id"),
                "chain": _row_value(row, "chain"),
                "source_species": "human",
                "target_species": _row_value(row, "target_species"),
                "gene_symbol": "unresolved",
                "source_uniprot": _row_value(row, "source_uniprot"),
                "partner_uniprot": "unresolved",
                "target_uniprot": _row_value(row, "candidate_target_uniprots"),
                "coverage_status": coverage_status,
                "provenance_status": "external_review_required",
                "repair_decision": _row_value(row, "repair_decision"),
                "repair_status": repair_status,
                "repair_priority": _row_value(row, "repair_priority"),
                "repair_queue_status": repair_queue_status,
                "downstream_block_status": _downstream_block_status(repair_status),
                "allowed_next_action": allowed_next_action,
                "claim_policy": _row_value(row, "claim_policy"),
                "claim_status": CLAIM_STATUS,
                "forbidden_actions": FORBIDDEN_ACTIONS,
                "reviewer_note": _row_value(row, "repair_note"),
            }
        )
    return pl.DataFrame(summary_rows, schema=SUMMARY_SCHEMA)


def tp53_mdm2_rows_to_generic_summary(rows: pl.DataFrame) -> pl.DataFrame:
    validate_required_columns(
        rows,
        required_columns=TP53_MDM2_REQUIRED_COLUMNS,
        table_name="TP53/MDM2 repair table",
    )
    summary_rows = []
    for index, row in enumerate(rows.to_dicts(), start=1):
        repair_status = _row_value(row, "repair_status")
        repair_queue_status = _repair_queue_status(repair_status)
        allowed_next_action = _allowed_next_action(
            repair_queue_status,
            _row_value(row, "recommended_next_action"),
        )
        summary_rows.append(
            {
                "candidate_set": _row_value(row, "candidate_set"),
                "lane_name": _row_value(row, "lane_name"),
                "candidate_id": _row_value(row, "candidate_id"),
                "source_table": str(DEFAULT_TP53_MDM2_REPAIR),
                "source_row_index": index,
                "pdb_id": _row_value(row, "pdb_id"),
                "chain": _row_value(row, "chain"),
                "source_species": _row_value(row, "source_species"),
                "target_species": _row_value(row, "target_species"),
                "gene_symbol": _row_value(row, "gene_symbol"),
                "source_uniprot": _row_value(row, "source_uniprot"),
                "partner_uniprot": _row_value(row, "partner_uniprot"),
                "target_uniprot": _row_value(row, "target_uniprot"),
                "coverage_status": _row_value(row, "coverage_status"),
                "provenance_status": _row_value(row, "provenance_status"),
                "repair_decision": _row_value(row, "repair_decision"),
                "repair_status": repair_status,
                "repair_priority": _row_value(row, "repair_priority"),
                "repair_queue_status": repair_queue_status,
                "downstream_block_status": _downstream_block_status(repair_status),
                "allowed_next_action": allowed_next_action,
                "claim_policy": _row_value(row, "claim_policy"),
                "claim_status": CLAIM_STATUS,
                "forbidden_actions": FORBIDDEN_ACTIONS,
                "reviewer_note": _row_value(row, "reviewer_note"),
            }
        )
    return pl.DataFrame(summary_rows, schema=SUMMARY_SCHEMA)


def _review_decision_lookup(
    review_decision_rows: pl.DataFrame,
) -> dict[tuple[str, ...], dict[str, object]]:
    validate_required_columns(
        review_decision_rows,
        required_columns=REVIEW_DECISION_REQUIRED_COLUMNS,
        table_name="review decision table",
    )
    lookup: dict[tuple[str, ...], dict[str, object]] = {}
    for row in review_decision_rows.to_dicts():
        key = _match_key(row)
        if key in lookup:
            raise ValueError(f"Duplicate review decision for repair queue row: {key}")
        lookup[key] = row
    return lookup


def apply_review_decision_overlay(
    summary: pl.DataFrame,
    review_decision_rows: pl.DataFrame,
) -> pl.DataFrame:
    """Overlay reviewed provenance decisions onto an existing repair queue summary.

    This function consumes already-reviewed decision rows only. It does not fetch
    sequences, curate orthologs, call Biohub, generate embeddings, call Boltz,
    promote Gate 8 or Gate 9, or make biological claims.
    """
    if review_decision_rows.is_empty():
        return summary

    lookup = _review_decision_lookup(review_decision_rows)
    updated_rows = []
    matched_keys: set[tuple[str, ...]] = set()

    for row in summary.to_dicts():
        key = _match_key(row)
        review = lookup.get(key)
        if review is None:
            updated_rows.append(row)
            continue

        matched_keys.add(key)
        review_decision = _row_value(review, "review_decision")
        reviewer_note = _row_value(review, "reviewer_note")
        row.update(
            {
                "repair_decision": review_decision,
                "repair_status": review_decision,
                "repair_queue_status": _review_repair_queue_status(review_decision),
                "downstream_block_status": _row_value(
                    review,
                    "downstream_block_status_after_review",
                ),
                "allowed_next_action": _row_value(
                    review,
                    "allowed_next_action_after_review",
                ),
                "claim_policy": _row_value(review, "claim_policy_after_review"),
                "claim_status": _row_value(
                    review,
                    "claim_status_after_review",
                    CLAIM_STATUS,
                ),
                "forbidden_actions": _row_value(
                    review,
                    "forbidden_actions_after_review",
                    FORBIDDEN_ACTIONS,
                ),
                "reviewer_note": (
                    f"Reviewed provenance decision: {review_decision}. {reviewer_note}"
                ),
            }
        )
        updated_rows.append(row)

    unmatched_keys = sorted(set(lookup) - matched_keys)
    if unmatched_keys:
        raise ValueError(f"Review decisions do not match summary rows: {unmatched_keys}")

    return pl.DataFrame(updated_rows, schema=SUMMARY_SCHEMA)


def build_generic_repair_queue_summary(
    *,
    sirt6_rows: pl.DataFrame,
    tp53_mdm2_rows: pl.DataFrame,
    review_decision_rows: pl.DataFrame | None = None,
) -> pl.DataFrame:
    """Build a table-only Gate 4 / Gate 5 generic repair queue summary.

    This stage does not fetch sequences, does not curate orthologs, does not call
    Biohub, does not generate embeddings, does not call Boltz, and does not make
    biological claims.
    """
    parts = [
        sirt6_rows_to_generic_summary(sirt6_rows),
        tp53_mdm2_rows_to_generic_summary(tp53_mdm2_rows),
    ]
    non_empty_parts = [part for part in parts if not part.is_empty()]
    if not non_empty_parts:
        summary = empty_generic_repair_queue_summary()
    else:
        summary = pl.concat(non_empty_parts).select(list(SUMMARY_SCHEMA))

    if review_decision_rows is None:
        return summary
    return apply_review_decision_overlay(summary, review_decision_rows)


def repair_queue_status_counts(summary: pl.DataFrame) -> pl.DataFrame:
    if summary.is_empty():
        return pl.DataFrame({"repair_queue_status": [], "n_rows": []})
    return summary.group_by("repair_queue_status").len(name="n_rows").sort(["repair_queue_status"])


@app.command()
def main(
    sirt6_repair: Annotated[Path, typer.Option()] = DEFAULT_SIRT6_REPAIR,
    tp53_mdm2_repair: Annotated[Path, typer.Option()] = DEFAULT_TP53_MDM2_REPAIR,
    review_decisions: Annotated[Path | None, typer.Option()] = None,
    output: Annotated[Path, typer.Option()] = DEFAULT_OUTPUT,
) -> None:
    """Write the generic repair queue summary CSV."""
    review_decision_rows = None
    if review_decisions is not None:
        review_decision_rows = read_repair_table(review_decisions)
    summary = build_generic_repair_queue_summary(
        sirt6_rows=read_repair_table(sirt6_repair),
        tp53_mdm2_rows=read_repair_table(tp53_mdm2_repair),
        review_decision_rows=review_decision_rows,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    summary.write_csv(output)
    typer.echo(f"Wrote {summary.height} rows to {output}")
