from __future__ import annotations

import csv
from pathlib import Path

import yaml

from longevity_port_pipelines.stages import ortholog_evidence_gate45_policy_update as policy

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = ROOT / "data/input/ortholog_evidence_gate45_policy_updates.csv"
REVIEW_TABLE_PATH = ROOT / "data/input/ortholog_evidence_review_decisions.csv"
SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_gate45_policy_update_schema.yaml"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def policy_rows() -> list[dict[str, str]]:
    rows = read_csv_rows(TABLE_PATH)
    assert len(rows) == 1
    return rows


def g3sx30_policy_row() -> dict[str, str]:
    rows = [
        row
        for row in policy_rows()
        if row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
        and row["reviewed_source_accession"] == "G3SX30"
    ]
    assert len(rows) == 1
    return rows[0]


def test_gate45_policy_update_table_has_one_g3sx30_row() -> None:
    row = g3sx30_policy_row()

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["lane_name"] == "tp53_mdm2_elephant"
    assert row["reviewed_target_uniprot"] == "G3SX30"
    assert row["reviewed_source_database"] == "UniProtKB TrEMBL"
    assert row["reviewed_source_accession"] == "G3SX30"
    assert row["reviewed_taxid"] == "9785"
    assert row["reviewed_sequence_length"] == "492"


def test_gate45_policy_update_row_traces_review_decision_source() -> None:
    row = g3sx30_policy_row()
    review_rows = read_csv_rows(REVIEW_TABLE_PATH)

    assert row["policy_source_table"] == "data/input/ortholog_evidence_review_decisions.csv"
    assert row["policy_source_row_index"] == "1"

    review_row = review_rows[int(row["policy_source_row_index"]) - 1]
    assert review_row["candidate_id"] == row["candidate_id"]
    assert review_row["reviewed_source_accession"] == row["reviewed_source_accession"]
    assert review_row["review_decision"] == row["review_decision_before_policy"]
    assert (
        review_row["downstream_block_status_after_review"]
        == row["downstream_block_status_before_policy"]
    )
    assert (
        review_row["allowed_next_action_after_review"] == row["allowed_next_action_before_policy"]
    )


def test_gate45_policy_update_row_is_schema_allowed_and_runtime_blocked() -> None:
    schema = load_yaml(SCHEMA_PATH)
    row = g3sx30_policy_row()
    rule = schema["policy_update_decision_rules"][row["policy_update_decision"]]

    assert row["policy_update_decision"] in schema["allowed_policy_update_decisions"]
    assert row["policy_update_decision"] == "approve_gate45_policy_update_for_planning"
    assert row["gate4_status_after_policy"] == "gate4_policy_updated_for_planning"
    assert row["gate5_status_after_policy"] == "gate5_policy_updated_for_planning"
    assert (
        row["downstream_block_status_after_policy"] == "gate45_policy_updated_still_runtime_blocked"
    )
    assert row["allowed_next_action_after_policy"] == (
        "prepare_later_gate_aware_embedding_fill_plan_pr"
    )
    assert rule["gate8_eligible"] is False
    assert rule["gate9_eligible"] is False
    assert rule["embedding_ready"] is False
    assert rule["biohub_ready"] is False
    assert rule["boltz_ready"] is False
    assert rule["af3_ready"] is False
    assert rule["chai_ready"] is False
    assert rule["biological_claim_allowed"] is False


def test_gate45_policy_update_row_keeps_claim_boundary() -> None:
    row = g3sx30_policy_row()

    assert row["claim_policy_after_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status_after_policy"] == "repair_worklist"
    assert "does not promote Gate 8 or Gate 9" in row["policy_update_note"]
    assert "does not make biological claims" in row["policy_update_note"]


def test_gate45_policy_update_row_forbids_runtime_side_effects() -> None:
    row = g3sx30_policy_row()
    forbidden = row["forbidden_actions_after_policy"]

    for action in policy.RUNTIME_SIDE_EFFECTS:
        assert action in forbidden

    assert "sequence fetch" in forbidden
    assert "Biohub call" in forbidden
    assert "embedding generation" in forbidden
    assert "Boltz call" in forbidden
    assert "AF3 call" in forbidden
    assert "Chai call" in forbidden
    assert "Gate 8 promotion" in forbidden
    assert "Gate 9 promotion" in forbidden
    assert "biological claim" in forbidden


def test_gate45_policy_update_table_uses_module_columns() -> None:
    header = TABLE_PATH.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert tuple(header) == policy.REQUIRED_COLUMNS


def test_gate45_policy_update_table_uses_schema_required_fields() -> None:
    schema = load_yaml(SCHEMA_PATH)
    header = set(TABLE_PATH.read_text(encoding="utf-8").splitlines()[0].split(","))
    required = set(schema["required_source_fields"]) | set(schema["required_policy_fields"])
    assert required <= header
