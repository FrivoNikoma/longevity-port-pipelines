from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_external_exact_sequence_binding_results as bindings,
)

ROOT = Path(__file__).resolve().parents[1]
RESULT_TABLE = ROOT / bindings.DEFAULT_RESULT_TABLE
SOURCE_TABLE = ROOT / bindings.DEFAULT_SOURCE_PROVENANCE_TABLE


def load_rows() -> list[dict[str, str]]:
    return bindings.load_and_validate_result(
        RESULT_TABLE,
        SOURCE_TABLE,
    )


def by_accession() -> dict[str, dict[str, str]]:
    return {row["target_accession"]: row for row in load_rows()}


def test_binding_result_has_exactly_two_rows() -> None:
    rows = load_rows()
    assert [row["target_accession"] for row in rows] == [
        "P23804",
        "A0ABM2YB85",
    ]


def test_mouse_binding_establishes_exact_hash() -> None:
    mouse = by_accession()["P23804"]
    assert mouse["expected_sequence_length"] == "489"
    assert mouse["source_previous_sha256_status"] == "missing_not_committed"
    assert mouse["external_normalized_sequence_sha256"] == bindings.P23804_SHA256
    assert mouse["external_accession_verified"] == "true"
    assert mouse["external_taxid_verified"] == "true"
    assert mouse["external_length_verified"] == "true"
    assert mouse["external_sha256_verified"] == "true"


def test_hamster_binding_matches_committed_hash() -> None:
    hamster = by_accession()["A0ABM2YB85"]
    assert hamster["expected_sequence_length"] == "510"
    assert hamster["source_previous_sha256"] == bindings.A0ABM2YB85_SHA256
    assert hamster["external_normalized_sequence_sha256"] == bindings.A0ABM2YB85_SHA256


def test_binding_references_are_portable() -> None:
    for row in load_rows():
        assert row["external_binding_root_env"] == bindings.BINDING_ROOT_ENV
        for field in (
            "external_binding_manifest_relative_path",
            "external_raw_fasta_relative_path",
            "external_normalized_sequence_relative_path",
        ):
            value = row[field]
            assert not Path(value).is_absolute()
            assert "\\" not in value
            assert "D:/" not in value
            assert "/home/" not in value


def test_fill_manifest_permission_is_scoped_only() -> None:
    for row in load_rows():
        assert row["later_missing_embedding_fill_manifest_allowed"] == "true"
        assert (
            row["allowed_next_action"] == "prepare_scoped_missing_embedding_fill_manifest_dry_run"
        )
        assert row["panel_binding_status"] == "ready_for_scoped_missing_embedding_fill_manifest"
        assert row["gate8_entry_allowed"] == "false"
        assert row["gate8_promoted"] == "false"
        assert row["gate9_promoted"] == "false"


def test_binding_result_records_no_runtime_side_effects() -> None:
    for row in load_rows():
        for field in bindings.NO_SIDE_EFFECT_FIELDS:
            assert row[field] == "false"


def test_validator_rejects_gate_promotion() -> None:
    rows = load_rows()
    source_rows = bindings.read_csv_rows(SOURCE_TABLE)
    bad_rows = [dict(row) for row in rows]
    bad_rows[0]["gate8_promoted"] = "true"

    with pytest.raises(ValueError, match="gate8_promoted"):
        bindings.validate_result_rows(
            bad_rows,
            source_rows,
        )


def test_validator_rejects_absolute_binding_path() -> None:
    rows = load_rows()
    source_rows = bindings.read_csv_rows(SOURCE_TABLE)
    bad_rows = [dict(row) for row in rows]
    bad_rows[0]["external_raw_fasta_relative_path"] = "D:/external/P23804.fasta"

    with pytest.raises(ValueError, match="safe relative filename"):
        bindings.validate_result_rows(
            bad_rows,
            source_rows,
        )
