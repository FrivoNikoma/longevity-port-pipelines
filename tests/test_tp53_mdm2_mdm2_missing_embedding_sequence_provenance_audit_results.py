from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_missing_embedding_sequence_provenance_audit_results as audit,
)

ROOT = Path(__file__).resolve().parents[1]
RESULT_TABLE = ROOT / audit.DEFAULT_RESULT_TABLE
SHORT_LIVED_TABLE = ROOT / audit.DEFAULT_SHORT_LIVED_SOURCE_TABLE
HAMSTER_REVIEW_TABLE = ROOT / audit.DEFAULT_HAMSTER_REVIEW_TABLE
GATE8_AUDIT_TABLE = ROOT / audit.DEFAULT_GATE8_LOCAL_AUDIT_TABLE
DATA_INPUT_DIR = ROOT / audit.DEFAULT_DATA_INPUT_DIR


def load_rows() -> list[dict[str, str]]:
    return audit.load_and_validate_result(
        RESULT_TABLE,
        SHORT_LIVED_TABLE,
        HAMSTER_REVIEW_TABLE,
        GATE8_AUDIT_TABLE,
        data_input_dir=DATA_INPUT_DIR,
    )


def by_accession() -> dict[str, dict[str, str]]:
    return {row["target_accession"]: row for row in load_rows()}


def test_sequence_provenance_audit_has_exactly_two_missing_embedding_rows() -> None:
    rows = load_rows()

    assert [row["target_accession"] for row in rows] == [
        "P23804",
        "A0ABM2YB85",
    ]
    assert {row["source_gate8_local_embedding_status"] for row in rows} == {"missing"}


def test_mouse_identity_is_ready_but_exact_hash_and_bytes_are_not_bound() -> None:
    mouse = by_accession()["P23804"]

    assert mouse["source_identity_provenance_ready"] == "true"
    assert (
        mouse["source_identity_provenance"]
        == "reviewed_swissprot_accession_identity_confirmed_for_gate7_technical_planning"
    )
    assert mouse["expected_sequence_length"] == "489"
    assert mouse["committed_exact_sequence_sha256"] == "not_committed"
    assert mouse["committed_exact_sequence_sha256_status"] == "missing_not_committed"
    assert mouse["external_exact_sequence_bytes_bindable"] == "true"
    assert mouse["external_exact_sequence_bytes_bound"] == "false"
    assert (
        mouse["controlled_fill_sequence_input_status"]
        == "blocked_missing_committed_sha256_and_non_committed_exact_sequence_binding"
    )


def test_hamster_has_committed_hash_but_exact_bytes_are_not_bound() -> None:
    hamster = by_accession()["A0ABM2YB85"]

    assert hamster["source_identity_provenance_ready"] == "true"
    assert hamster["expected_sequence_length"] == "510"
    assert hamster["committed_exact_sequence_sha256"] == audit.EXPECTED_HAMSTER_SHA256
    assert hamster["committed_exact_sequence_sha256_status"] == "present_committed"
    assert hamster["external_exact_sequence_bytes_bindable"] == "true"
    assert hamster["external_exact_sequence_bytes_bound"] == "false"
    assert (
        hamster["controlled_fill_sequence_input_status"]
        == "blocked_pending_non_committed_exact_sequence_binding"
    )


def test_panel_remains_blocked_before_missing_embedding_fill_manifest() -> None:
    for row in load_rows():
        assert (
            row["panel_sequence_provenance_status"]
            == "blocked_pending_exact_sequence_bindings_and_mouse_hash"
        )
        assert row["panel_sha256_ready_accessions"] == "A0ABM2YB85"
        assert row["panel_sha256_missing_accessions"] == "P23804"
        assert row["panel_exact_sequence_bytes_bound_accessions"] == "none"
        assert row["later_missing_embedding_fill_manifest_allowed"] == "false"
        assert row["later_controlled_embedding_fill_input_allowed"] == "false"


def test_sequence_provenance_audit_records_no_runtime_side_effects() -> None:
    for row in load_rows():
        for field in audit.NO_SIDE_EFFECT_FIELDS:
            assert row[field] == "false"


def test_committed_result_rebuilds_from_current_sources() -> None:
    actual = load_rows()
    expected = audit.build_expected_rows(
        audit.read_csv_rows(SHORT_LIVED_TABLE),
        audit.read_csv_rows(HAMSTER_REVIEW_TABLE),
        audit.read_csv_rows(GATE8_AUDIT_TABLE),
        data_input_dir=DATA_INPUT_DIR,
    )

    assert actual == expected


def test_validator_rejects_fill_or_gate_promotion() -> None:
    rows = load_rows()
    bad_rows = [dict(row) for row in rows]
    bad_rows[0]["later_missing_embedding_fill_manifest_allowed"] = "true"

    with pytest.raises(ValueError, match="differ"):
        audit.validate_result_rows(
            bad_rows,
            audit.read_csv_rows(SHORT_LIVED_TABLE),
            audit.read_csv_rows(HAMSTER_REVIEW_TABLE),
            audit.read_csv_rows(GATE8_AUDIT_TABLE),
            data_input_dir=DATA_INPUT_DIR,
        )


def test_validator_rejects_biological_claim() -> None:
    rows = load_rows()
    bad_rows = [dict(row) for row in rows]
    bad_rows[1]["biological_claim_made"] = "true"

    with pytest.raises(ValueError, match="biological_claim_made"):
        audit.validate_result_rows(
            bad_rows,
            audit.read_csv_rows(SHORT_LIVED_TABLE),
            audit.read_csv_rows(HAMSTER_REVIEW_TABLE),
            audit.read_csv_rows(GATE8_AUDIT_TABLE),
            data_input_dir=DATA_INPUT_DIR,
        )


def test_hash_discovery_uses_repo_relative_references(
    tmp_path: Path,
) -> None:
    data_input_dir = tmp_path / "alternate_checkout" / "data" / "input"
    data_input_dir.mkdir(parents=True)

    source = data_input_dir / "sequence_review.csv"
    source.write_text(
        f"candidate_accession,sequence_sha256\nA0ABM2YB85,{audit.EXPECTED_HAMSTER_SHA256}\n",
        encoding="utf-8",
    )

    findings = audit.discover_committed_accession_hashes(
        data_input_dir,
        "A0ABM2YB85",
    )

    assert findings == [
        (
            "data/input/sequence_review.csv",
            1,
            "sequence_sha256",
            audit.EXPECTED_HAMSTER_SHA256,
        )
    ]
