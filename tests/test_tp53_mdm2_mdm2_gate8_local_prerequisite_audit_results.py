from pathlib import Path

import pytest
import yaml

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_gate8_local_prerequisite_audit_results as audit,
)

ROOT = Path(__file__).resolve().parents[1]
RESULT_TABLE = ROOT / audit.DEFAULT_RESULT_TABLE
SCHEMA_PATH = ROOT / "data/config/tp53_mdm2_mdm2_gate8_local_prerequisite_audit_result_schema.yaml"


def test_gate8_local_prerequisite_audit_has_exact_panel_rows() -> None:
    rows = audit.load_and_validate_result(ROOT)

    assert [row["target_species"] for row in rows] == [
        "elephant",
        "mouse",
        "hamster",
    ]
    assert [row["target_accession"] for row in rows] == [
        "G3SX30",
        "P23804",
        "A0ABM2YB85",
    ]
    assert {row["target_species_taxid"] for row in rows} == {
        "9785",
        "10090",
        "10036",
    }


def test_gate8_local_prerequisite_audit_records_one_valid_two_missing() -> None:
    rows = audit.load_and_validate_result(ROOT)
    by_species = {row["target_species"]: row for row in rows}

    elephant = by_species["elephant"]
    assert elephant["local_embedding_status"] == "present_valid"
    assert elephant["runtime_blocker_code"] == "none"
    assert elephant["embedding_shape"] == "492x960"
    assert elephant["embedding_dtype"] == "float32"
    assert elephant["embedding_numeric"] == "true"
    assert elephant["embedding_finite"] == "true"
    assert elephant["embedding_sequence_length_matches"] == "true"
    assert (
        elephant["embedding_accession_provenance_status"]
        == "confirmed_by_existing_g3sx30_one_row_preflight_result"
    )

    for species in ["mouse", "hamster"]:
        row = by_species[species]
        assert row["local_embedding_status"] == "missing"
        assert row["runtime_blocker_code"] == "missing_exact_local_embedding"
        assert row["local_runtime_embedding_exists"] == "false"
        assert row["embedding_load_status"] == "not_attempted_missing"


def test_gate8_local_prerequisite_audit_records_panel_blocker() -> None:
    rows = audit.load_and_validate_result(ROOT)

    for row in rows:
        assert row["panel_valid_accessions"] == "G3SX30"
        assert row["panel_missing_accessions"] == "P23804|A0ABM2YB85"
        assert row["panel_local_prerequisites_status"] == "blocked_missing_exact_local_embeddings"
        assert (
            row["panel_runtime_blocker_code"]
            == "missing_exact_local_embeddings_for_ready_mdm2_controls"
        )
        assert row["later_mdm2_dry_run_manifest_allowed"] == "false"
        assert row["allowed_next_action"] == "prepare_separate_scoped_missing_embedding_fill"


def test_gate8_local_prerequisite_audit_preserves_gate_boundaries() -> None:
    rows = audit.load_and_validate_result(ROOT)

    for row in rows:
        assert row["mdm2_gate7_strict_panel_status"] == "strict_panel_ready"
        assert row["mdm2_gate7_contrast_dry_run_allowed"] == "true"
        assert row["tp53_status"] == "deferred_pending_source"
        assert row["aggregate_gate7_blocker_code"] == ("tp53_deferred_pending_source")
        for field in audit.FALSE_FIELDS:
            assert row[field] == "false"


def test_gate8_local_prerequisite_audit_excludes_deferred_rat() -> None:
    rows = audit.load_and_validate_result(ROOT)

    assert "rat" not in {row["target_species"] for row in rows}
    assert "NP_001426446.1" not in {row["target_accession"] for row in rows}


def test_gate8_local_prerequisite_audit_rebuilds_from_sources() -> None:
    actual = audit.read_csv_rows(RESULT_TABLE)
    expected = audit.build_expected_rows(
        audit.read_csv_rows(ROOT / audit.DEFAULT_ELEPHANT_SOURCE_TABLE),
        audit.read_csv_rows(ROOT / audit.DEFAULT_SHORT_LIVED_SOURCE_TABLE),
        audit.read_csv_rows(ROOT / audit.DEFAULT_G3SX30_PREFLIGHT_RESULT_TABLE),
    )

    assert actual == expected


def test_gate8_local_prerequisite_audit_rejects_missing_row_as_present() -> None:
    rows = audit.read_csv_rows(RESULT_TABLE)
    bad_rows = [dict(row) for row in rows]
    bad_rows[1]["local_embedding_status"] = "present_valid"

    with pytest.raises(ValueError, match="local_embedding_status"):
        audit.validate_result_rows(
            bad_rows,
            elephant_rows=audit.read_csv_rows(ROOT / audit.DEFAULT_ELEPHANT_SOURCE_TABLE),
            short_lived_rows=audit.read_csv_rows(ROOT / audit.DEFAULT_SHORT_LIVED_SOURCE_TABLE),
            g3sx30_preflight_rows=audit.read_csv_rows(
                ROOT / audit.DEFAULT_G3SX30_PREFLIGHT_RESULT_TABLE
            ),
        )


def test_gate8_local_prerequisite_audit_rejects_gate8_unlock() -> None:
    rows = audit.read_csv_rows(RESULT_TABLE)
    bad_rows = [dict(row) for row in rows]
    bad_rows[0]["aggregate_gate8_entry_allowed"] = "true"

    with pytest.raises(ValueError, match="aggregate_gate8_entry_allowed"):
        audit.validate_result_rows(
            bad_rows,
            elephant_rows=audit.read_csv_rows(ROOT / audit.DEFAULT_ELEPHANT_SOURCE_TABLE),
            short_lived_rows=audit.read_csv_rows(ROOT / audit.DEFAULT_SHORT_LIVED_SOURCE_TABLE),
            g3sx30_preflight_rows=audit.read_csv_rows(
                ROOT / audit.DEFAULT_G3SX30_PREFLIGHT_RESULT_TABLE
            ),
        )


def test_gate8_local_prerequisite_audit_schema_contract() -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["version"] == 1
    assert schema["model_name"] == "esmc-300m-2024-12"
    assert schema["expected_row_count"] == 3
    assert schema["panel_contract"]["valid_accessions"] == ["G3SX30"]
    assert schema["panel_contract"]["missing_accessions"] == [
        "P23804",
        "A0ABM2YB85",
    ]
    assert (
        schema["panel_contract"]["panel_local_prerequisites_status"]
        == "blocked_missing_exact_local_embeddings"
    )
    assert schema["panel_contract"]["later_mdm2_dry_run_manifest_allowed"] is False
    assert schema["boundaries"]["aggregate_gate8_entry_allowed"] is False
    assert schema["boundaries"]["gate9_promoted"] is False
    assert schema["boundaries"]["biological_claim_made"] is False
