from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_embedding_based_negatome_control_result as result,
)
from longevity_port_pipelines.stages.control_readiness import (
    BLOCKED_CONTROL_READINESS_STATUSES,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / (
    "data/config/tp53_mdm2_first_embedding_based_negatome_control_result_schema.yaml"
)
RESULT_PATH = ROOT / ("data/input/tp53_mdm2_first_embedding_based_negatome_control_results.csv")


def test_committed_result_is_valid() -> None:
    row = result.load_and_validate_embedding_based_negatome_result()
    assert row["result_created"] == "true"


def test_table_has_one_row_and_schema_matches() -> None:
    with RESULT_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert len(rows) == 1
    assert list(rows[0]) == schema["required_fields"]


def test_records_two_concrete_blockers() -> None:
    row = result.load_and_validate_embedding_based_negatome_result()
    assert row["checked_blocker_count"] == "2"
    assert row["primary_missing_input_kind"] == (
        "chain_local_to_full_length_interface_mapping_not_verified"
    )
    assert row["secondary_missing_input_kind"] == ("exact_negatome_pair_lookup_key_missing")


def test_records_available_ignored_embeddings() -> None:
    row = result.load_and_validate_embedding_based_negatome_result()
    assert row["human_embedding_shape"] == "491x960"
    assert row["human_embedding_ignored"] == "true"
    assert row["elephant_embedding_shape"] == "492x960"
    assert row["elephant_embedding_ignored"] == "true"


def test_does_not_invent_ratio_or_open_gate7() -> None:
    row = result.load_and_validate_embedding_based_negatome_result()
    assert row["embedding_based_negatome_control_computed"] == "false"
    assert row["negatome_control_ratio"] == "not_computed"
    assert row["gate6_control_readiness_status_after"] == ("blocked_pending_control_repair")
    assert row["gate6_control_readiness_status_after"] in BLOCKED_CONTROL_READINESS_STATUSES
    assert row["gate7_entry_allowed_after"] == "false"
    assert row["biological_approval_granted"] == "false"


def test_records_honest_npy_boundary() -> None:
    row = result.load_and_validate_embedding_based_negatome_result()
    assert row["npy_artifact_read_during_local_audit"] == "true"
    assert row["npy_artifact_written"] == "false"
    assert row["npy_artifact_committed"] == "false"
    assert row["data_output_artifact_committed"] == "false"
    assert row["biohub_esmc_called"] == "false"


def test_digest_recomputes() -> None:
    row = result.load_and_validate_embedding_based_negatome_result()
    assert row["result_metadata_sha256"] == (
        "e92c045e44db2800fe2cb643bab281d875a1de6e0ce2413a2fed9b23bc3a49c2"
    )
    assert row["result_metadata_sha256"] == result.result_metadata_sha256()


def write_mutated(path: Path, field: str, value: str) -> None:
    row = result.load_and_validate_embedding_based_negatome_result().copy()
    row[field] = value
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


def test_rejects_fake_ratio(tmp_path: Path) -> None:
    path = tmp_path / "mutated.csv"
    write_mutated(path, "negatome_control_ratio", "1.25")
    with pytest.raises(ValueError, match="negatome_control_ratio"):
        result.load_and_validate_embedding_based_negatome_result(path)


def test_rejects_gate7_entry(tmp_path: Path) -> None:
    path = tmp_path / "mutated.csv"
    write_mutated(path, "gate7_entry_allowed_after", "true")
    with pytest.raises(ValueError, match="gate7_entry_allowed_after"):
        result.load_and_validate_embedding_based_negatome_result(path)
