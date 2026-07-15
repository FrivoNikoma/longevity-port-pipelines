from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_gate6_blocker_disposition_result as disposition,
)
from longevity_port_pipelines.stages.control_readiness import (
    BLOCKED_CONTROL_READINESS_STATUSES,
    BLOCKED_CONTROL_REPAIR_STATUSES,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/tp53_mdm2_first_gate6_blocker_disposition_result_schema.yaml"
RESULT_PATH = ROOT / "data/input/tp53_mdm2_first_gate6_blocker_disposition_results.csv"


def read_raw_rows() -> list[dict[str, str]]:
    with RESULT_PATH.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_committed_gate6_blocker_disposition_result_is_valid() -> None:
    row = disposition.load_and_validate_gate6_blocker_disposition_result()
    assert row["disposition_result_created"] == "true"


def test_gate6_blocker_disposition_table_has_one_row() -> None:
    rows = read_raw_rows()
    assert len(rows) == 1


def test_gate6_blocker_disposition_schema_matches_header() -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    row = disposition.load_and_validate_gate6_blocker_disposition_result()
    assert list(row) == schema["required_fields"]


def test_gate6_blocker_disposition_selects_embedding_based_repair() -> None:
    row = disposition.load_and_validate_gate6_blocker_disposition_result()
    assert row["disposition_class"] == "repair"
    assert row["disposition_action"] == "require_embedding_based_control"
    assert row["repair_selected"] == "true"
    assert row["defer_selected"] == "false"
    assert row["exclude_selected"] == "false"
    assert row["require_embedding_based_control_selected"] == "true"


def test_gate6_blocker_disposition_matches_generic_blocked_vocabulary() -> None:
    row = disposition.load_and_validate_gate6_blocker_disposition_result()
    assert row["generic_control_repair_status"] == "pending"
    assert row["generic_control_repair_status"] in BLOCKED_CONTROL_REPAIR_STATUSES
    assert row["generic_control_readiness_status"] == ("blocked_pending_control_repair")
    assert row["generic_control_readiness_status"] in BLOCKED_CONTROL_READINESS_STATUSES


def test_gate6_blocker_disposition_keeps_gate7_closed() -> None:
    row = disposition.load_and_validate_gate6_blocker_disposition_result()
    assert row["gate6_control_readiness_status_after_disposition"] == "blocked"
    assert row["gate6_control_readiness_resolved_after_disposition"] == "false"
    assert row["gate6_control_closure_blocked_after_disposition"] == "true"
    assert row["gate7_entry_allowed_after_disposition"] == "false"
    assert row["gate7_strict_panel_promoted"] == "false"
    assert row["biological_approval_granted"] == "false"


def test_gate6_blocker_disposition_has_no_runtime_side_effects() -> None:
    row = disposition.load_and_validate_gate6_blocker_disposition_result()
    for field in (
        "runtime_execution_authorized",
        "evidence_recomputed",
        "interface_scoring_performed",
        "comparative_elephant_interface_scoring_performed",
        "new_embeddings_generated",
        "biohub_esmc_called",
        "npy_artifact_read",
        "npy_artifact_written",
        "data_output_artifact_committed",
        "boltz_called",
        "af3_called",
        "chai_called",
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
    ):
        assert row[field] == "false"


def test_gate6_blocker_disposition_metadata_digest_recomputes() -> None:
    row = disposition.load_and_validate_gate6_blocker_disposition_result()
    assert row["disposition_metadata_canonical"] == (disposition.canonical_disposition_metadata())
    assert row["disposition_metadata_sha256"] == (
        "1ef15df255929ca89e248fabec6eba6456d89a972b230389dd7135f24b13b4e4"
    )
    assert row["disposition_metadata_sha256"] == (disposition.disposition_metadata_sha256())


def test_gate6_blocker_disposition_rejects_mutated_action(
    tmp_path: Path,
) -> None:
    row = disposition.load_and_validate_gate6_blocker_disposition_result().copy()
    row["disposition_action"] = "defer"
    path = tmp_path / "mutated.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)

    with pytest.raises(ValueError, match="disposition_action"):
        disposition.load_and_validate_gate6_blocker_disposition_result(path)


def test_gate6_blocker_disposition_rejects_gate7_promotion(
    tmp_path: Path,
) -> None:
    row = disposition.load_and_validate_gate6_blocker_disposition_result().copy()
    row["gate7_entry_allowed_after_disposition"] = "true"
    path = tmp_path / "mutated.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)

    with pytest.raises(ValueError, match="gate7_entry_allowed_after_disposition"):
        disposition.load_and_validate_gate6_blocker_disposition_result(path)
