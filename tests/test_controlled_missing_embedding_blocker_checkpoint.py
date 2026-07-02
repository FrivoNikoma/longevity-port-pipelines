from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_DOC = ROOT / "docs/controlled_missing_embedding_blocker_checkpoint.md"
LOCAL_RESULTS_DOC = ROOT / "docs/sirt6_mini_pilot_v2_local_results.md"
WORKFLOW_DOC = ROOT / "docs/sirt6_mini_pilot_workflow.md"
BASELINE_DOC = ROOT / "docs/sirt6_human_cofolding_baseline_shortlist.md"
REPAIR_DECISIONS = ROOT / "data/input/sirt6_candidate_coverage_repair_decisions.csv"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_repair_rows() -> list[dict[str, str]]:
    with REPAIR_DECISIONS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_controlled_missing_embedding_blocker_checkpoint_doc_exists() -> None:
    assert CHECKPOINT_DOC.exists()


def test_controlled_missing_embedding_blocker_checkpoint_records_p84233_as_blocked() -> None:
    text = read_text(CHECKPOINT_DOC)

    assert "8f86" in text
    assert "P84233" in text
    assert "missing ortholog coverage" in text
    assert "must not be promoted to a controlled dry-run or live-fill candidate" in text
    assert "No reviewed missing embedding row is selected" in text


def test_legacy_docs_record_p84233_missing_ortholog_coverage() -> None:
    local_results = read_text(LOCAL_RESULTS_DOC)
    workflow = read_text(WORKFLOW_DOC)

    assert "8f86 ligand P84233" in local_results
    assert "missing ortholog coverage row" in local_results
    assert "missing coverage row: 8f86 ligand P84233" in workflow


def test_baseline_doc_records_8f86_mapping_concerns() -> None:
    baseline = read_text(BASELINE_DOC)

    assert "older 8f86 rows included ligand-mapping and partner-mismatch concerns" in baseline
    assert "not a good first live baseline target" in baseline


def test_tracked_8f86_q8n6t7_expanded_species_rows_remain_deferred() -> None:
    rows = [
        row
        for row in read_repair_rows()
        if row["candidate_id"] == "8f86__K1_Q8N6T7--8f86__D1_P02281"
        and row["source_uniprot"] == "Q8N6T7"
    ]

    assert {row["target_species"] for row in rows} == {"bowhead_whale", "brandts_bat"}

    for row in rows:
        assert row["coverage_gap_status"] == "missing_ortholog_but_local_rows_present"
        assert (
            row["recommended_coverage_action"]
            == "local_downstream_evidence_without_source_ortholog"
        )
        assert row["repair_decision"] == "needs_external_manual_sequence_review"
        assert row["claim_policy"] == "deferred_no_claim"


def test_controlled_missing_embedding_blocker_checkpoint_forbids_live_actions() -> None:
    text = read_text(CHECKPOINT_DOC)

    assert "no Biohub call" in text
    assert "no embedding generation" in text
    assert "no `curated_embedding_single --yes-live`" in text
    assert "no committed `data/output/` embedding artifact" in text
    assert "no Boltz call" in text
    assert "no enrichment or contrast rerun" in text
    assert "no biological claim" in text
