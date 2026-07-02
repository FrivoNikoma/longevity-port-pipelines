from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_DOC = ROOT / "docs/coverage_provenance_repair_queue_checkpoint.md"
SIRT6_REPAIR = ROOT / "data/input/sirt6_candidate_coverage_repair_decisions.csv"
TP53_MDM2_REPAIR = ROOT / "data/input/tp53_mdm2_ortholog_repair_decisions.csv"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_coverage_provenance_repair_queue_checkpoint_doc_exists() -> None:
    assert CHECKPOINT_DOC.exists()


def test_coverage_provenance_repair_queue_checkpoint_records_current_files() -> None:
    text = read_text(CHECKPOINT_DOC)

    assert "data/input/sirt6_candidate_coverage_repair_decisions.csv" in text
    assert "data/input/tp53_mdm2_ortholog_repair_decisions.csv" in text
    assert "Gate 4 / Gate 5" in text
    assert "queue checkpoint, not a biological repair PR" in text


def test_sirt6_repair_queue_has_eleven_deferred_manual_review_rows() -> None:
    rows = read_csv_rows(SIRT6_REPAIR)

    assert len(rows) == 11
    assert {row["coverage_gap_status"] for row in rows} == {
        "missing_ortholog_but_local_rows_present"
    }
    assert {row["recommended_coverage_action"] for row in rows} == {
        "local_downstream_evidence_without_source_ortholog"
    }
    assert {row["repair_decision"] for row in rows} == {"needs_external_manual_sequence_review"}
    assert {row["claim_policy"] for row in rows} == {"deferred_no_claim"}
    assert {row["source_uniprot"] for row in rows} == {
        "P09874",
        "P12956",
        "P13010",
        "Q04206",
        "Q8N6T7",
    }
    assert {"bowhead_whale", "brandts_bat", "elephant"}.issubset(
        {row["target_species"] for row in rows}
    )


def test_tp53_mdm2_repair_queue_has_two_blocked_seed_rows() -> None:
    rows = read_csv_rows(TP53_MDM2_REPAIR)

    assert len(rows) == 2
    assert {row["candidate_set"] for row in rows} == {"tp53_mdm2_elephant"}
    assert {row["source_uniprot"] for row in rows} == {"P04637", "Q00987"}
    assert {row["partner_uniprot"] for row in rows} == {"P04637", "Q00987"}
    assert {row["target_species"] for row in rows} == {"elephant"}
    assert {row["coverage_preflight_status"] for row in rows} == {"blocked_pending_coverage_repair"}
    assert {row["source_ortholog_status"] for row in rows} == {"not_checked"}
    assert {row["local_candidate_row_status"] for row in rows} == {"not_checked"}
    assert {row["recommended_next_action"] for row in rows} == {
        "curate_or_fetch_tp53_mdm2_source_ortholog_coverage"
    }
    assert {row["repair_decision"] for row in rows} == {"fetch_or_curate_source_ortholog"}
    assert {row["repair_priority"] for row in rows} == {"high"}
    assert {row["claim_policy"] for row in rows} == {"ortholog_repair_only"}


def test_coverage_provenance_repair_queue_checkpoint_aligns_blocker_types() -> None:
    text = read_text(CHECKPOINT_DOC)

    assert "SIRT6/core3: local downstream rows exist" in text
    assert "TP53/MDM2 elephant: source ortholog coverage has not yet been checked" in text
    assert "Both remain Gate 4 / Gate 5 blockers" in text
    assert (
        "should not be bypassed by embedding fill, contrast, cofolding, or live structural calls"
        in text
    )


def test_coverage_provenance_repair_queue_checkpoint_forbids_downstream_claims() -> None:
    text = read_text(CHECKPOINT_DOC)

    assert "no validated longevity signal" in text
    assert "no validated biological hit" in text
    assert "no confirmed binding change" in text
    assert "no confirmed functional effect" in text
    assert "no Biohub call" in text
    assert "no embedding generation" in text
    assert "no Boltz call" in text
    assert "no enrichment or contrast rerun" in text
    assert "no live structural compatibility call" in text
    assert "no decision package promotion" in text
