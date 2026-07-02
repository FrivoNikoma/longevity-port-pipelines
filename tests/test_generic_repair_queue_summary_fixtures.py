from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

FIXTURE_DIR = Path("tests/fixtures")
BASE_FIXTURE = FIXTURE_DIR / "generic_repair_queue_summary_base.csv"
REVIEWED_FIXTURE = FIXTURE_DIR / "generic_repair_queue_summary_reviewed_overlay.csv"
REVIEWED_CANDIDATE_ID = "4xhu__A1_P09874--4xhu__B1_Q9UNS1"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def fixture_key(row: dict[str, str]) -> tuple[str, str, str, str, str, str]:
    return (
        row["candidate_set"],
        row["candidate_id"],
        row["source_table"].replace("\\\\", "/"),
        row["source_row_index"],
        row["target_species"],
        row["source_uniprot"],
    )


def test_summary_checkpoint_fixtures_exist_under_tests_fixtures() -> None:
    assert BASE_FIXTURE.exists()
    assert REVIEWED_FIXTURE.exists()
    assert "data/interim" not in BASE_FIXTURE.as_posix()
    assert "data/interim" not in REVIEWED_FIXTURE.as_posix()


def test_base_summary_fixture_records_expected_gate4_gate5_queue() -> None:
    rows = read_rows(BASE_FIXTURE)
    assert len(rows) == 13
    assert Counter(row["candidate_set"] for row in rows) == {
        "sirt6_dna_repair": 11,
        "tp53_mdm2_elephant": 2,
    }
    assert {row["downstream_block_status"] for row in rows} == {"blocked_gate4_gate5"}
    assert {row["claim_status"] for row in rows} == {"repair_worklist"}


def test_base_summary_fixture_keeps_unreviewed_repair_statuses() -> None:
    rows = read_rows(BASE_FIXTURE)
    assert Counter(row["repair_queue_status"] for row in rows) == {
        "blocked_pending_manual_review": 11,
        "blocked_pending_source_ortholog_repair": 2,
    }
    assert Counter(row["allowed_next_action"] for row in rows) == {
        "manual_sequence_provenance_review": 11,
        "fetch_or_curate_source_ortholog": 2,
    }


def test_reviewed_overlay_fixture_preserves_queue_size_and_candidate_counts() -> None:
    rows = read_rows(REVIEWED_FIXTURE)
    assert len(rows) == 13
    assert Counter(row["candidate_set"] for row in rows) == {
        "sirt6_dna_repair": 11,
        "tp53_mdm2_elephant": 2,
    }


def test_reviewed_overlay_fixture_records_deferred_sirt6_review_without_unblocking() -> None:
    rows = read_rows(REVIEWED_FIXTURE)
    reviewed_rows = [
        row
        for row in rows
        if row["candidate_id"] == REVIEWED_CANDIDATE_ID
        and row["candidate_set"] == "sirt6_dna_repair"
        and row["target_species"] == "bowhead_whale"
        and row["source_uniprot"] == "P09874"
    ]
    assert len(reviewed_rows) == 1
    reviewed = reviewed_rows[0]
    assert reviewed["repair_decision"] == "deferred_pending_source"
    assert reviewed["repair_status"] == "deferred_pending_source"
    assert reviewed["repair_queue_status"] == "blocked_deferred_pending_source"
    assert reviewed["downstream_block_status"] == "blocked_gate4_gate5"
    assert reviewed["claim_status"] == "repair_worklist"
    assert "Reviewed provenance decision" in reviewed["reviewer_note"]


def test_reviewed_overlay_fixture_changes_only_one_summary_row() -> None:
    base_rows = {fixture_key(row): row for row in read_rows(BASE_FIXTURE)}
    reviewed_rows = {fixture_key(row): row for row in read_rows(REVIEWED_FIXTURE)}
    assert set(base_rows) == set(reviewed_rows)

    changed_keys = [key for key, base_row in base_rows.items() if reviewed_rows[key] != base_row]
    assert len(changed_keys) == 1
    changed = reviewed_rows[changed_keys[0]]
    assert changed["candidate_id"] == REVIEWED_CANDIDATE_ID
    assert changed["repair_queue_status"] == "blocked_deferred_pending_source"


def test_summary_fixtures_do_not_encode_downstream_permission_or_biological_claims() -> None:
    forbidden_claims = (
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "validated ortholog",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "embedding ready",
        "Boltz ready",
    )
    for path in (BASE_FIXTURE, REVIEWED_FIXTURE):
        text = path.read_text(encoding="utf-8")
        for claim in forbidden_claims:
            assert claim not in text
        rows = read_rows(path)
        assert {row["downstream_block_status"] for row in rows} == {"blocked_gate4_gate5"}
