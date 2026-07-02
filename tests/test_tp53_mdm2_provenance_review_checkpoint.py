from __future__ import annotations

import csv
from pathlib import Path

from longevity_port_pipelines.stages import gate_repair_policy as policy

REVIEW_DECISIONS = Path("data/input/generic_repair_queue_review_decisions.csv")
REVIEWED_OVERLAY = Path("tests/fixtures/generic_repair_queue_summary_reviewed_overlay.csv")


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _tp53_mdm2_review_rows() -> list[dict[str, str]]:
    rows = _read_rows(REVIEW_DECISIONS)
    return [
        row
        for row in rows
        if row["candidate_set"] == "tp53_mdm2_elephant"
        and row["source_table"] == "data/input/tp53_mdm2_ortholog_repair_decisions.csv"
    ]


def _tp53_mdm2_overlay_rows() -> list[dict[str, str]]:
    rows = _read_rows(REVIEWED_OVERLAY)
    return [
        row
        for row in rows
        if row["candidate_set"] == "tp53_mdm2_elephant"
        and row["source_table"].replace("\\", "/")
        == "data/input/tp53_mdm2_ortholog_repair_decisions.csv"
    ]


def test_tp53_mdm2_review_checkpoint_records_both_seed_rows() -> None:
    rows = _tp53_mdm2_review_rows()

    assert len(rows) == 2
    assert {row["gene_symbol"] for row in rows} == {"TP53", "MDM2"}
    assert {row["candidate_id"] for row in rows} == {
        "tp53_mdm2_elephant_seed_tp53_chain",
        "tp53_mdm2_elephant_seed_mdm2_chain",
    }
    assert {row["source_row_index"] for row in rows} == {"1", "2"}


def test_tp53_mdm2_review_checkpoint_remains_deferred_and_blocked() -> None:
    rows = _tp53_mdm2_review_rows()

    for row in rows:
        assert row["review_decision"] == "deferred_pending_source"
        assert row["reviewed_target_uniprot"] == "unresolved"
        assert row["reviewed_source_database"] == "project_repair_queue"
        assert row["reviewed_source_accession"] == "unresolved"
        assert row["reviewed_sequence_length"] == "unresolved"
        assert row["reviewed_taxid"] == "9785"
        assert row["downstream_block_status_after_review"] == "blocked_gate4_gate5"
        assert (
            row["allowed_next_action_after_review"] == "defer_until_stronger_source_evidence_exists"
        )
        assert row["claim_policy_after_review"] == "no_biological_claims_until_validation"
        assert row["claim_status_after_review"] == "repair_worklist"
        assert "no accession-level elephant target ortholog" in row["reviewer_note"]


def test_tp53_mdm2_review_checkpoint_forbids_runtime_downstream_actions() -> None:
    rows = _tp53_mdm2_review_rows()

    expected_forbidden_actions = [
        "sequence fetch",
        "manual ortholog curation",
        "Biohub call",
        "embedding generation",
        "Boltz call",
        "enrichment rerun",
        "contrast rerun",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "biological claim",
    ]

    for row in rows:
        forbidden_actions = row["forbidden_actions_after_review"]
        for action in expected_forbidden_actions:
            assert action in forbidden_actions


def test_tp53_mdm2_review_overlay_marks_both_rows_as_deferred() -> None:
    rows = _tp53_mdm2_overlay_rows()

    assert len(rows) == 2
    assert {row["gene_symbol"] for row in rows} == {"TP53", "MDM2"}

    for row in rows:
        assert row["repair_decision"] == "deferred_pending_source"
        assert row["repair_status"] == "deferred_pending_source"
        assert row["repair_queue_status"] == "blocked_deferred_pending_source"
        assert row["downstream_block_status"] == "blocked_gate4_gate5"
        assert row["allowed_next_action"] == "defer_until_stronger_source_evidence_exists"
        assert row["claim_policy"] == "no_biological_claims_until_validation"
        assert row["claim_status"] == "repair_worklist"
        assert "Reviewed provenance decision: deferred_pending_source" in row["reviewer_note"]


def test_tp53_mdm2_review_overlay_policy_helper_keeps_rows_blocked() -> None:
    rows = _tp53_mdm2_overlay_rows()

    assert len(rows) == 2

    for row in rows:
        decision = policy.classify_gate_repair_policy(row)
        assert decision.can_leave_gate4_gate5_now is False
        assert decision.gate4_gate5_policy_update_allowed is False
        assert decision.gate8_eligible is False
        assert decision.gate9_eligible is False
        assert decision.embedding_ready is False
        assert decision.boltz_ready is False
        assert decision.biological_claim_allowed is False
        assert decision.reason == "deferred_pending_source remains a Gate 4 / Gate 5 blocker"
