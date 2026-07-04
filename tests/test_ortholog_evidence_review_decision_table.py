from __future__ import annotations

import csv
from pathlib import Path

import yaml

from longevity_port_pipelines.stages import ortholog_evidence_review_decision as review

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = ROOT / "data/input/ortholog_evidence_review_decisions.csv"
INTAKE_PATH = ROOT / "data/input/ortholog_evidence_intake.csv"
SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_review_decision_schema.yaml"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def review_rows() -> list[dict[str, str]]:
    rows = read_csv_rows(TABLE_PATH)
    assert len(rows) == 1
    return rows


def g3sx30_review_row() -> dict[str, str]:
    rows = [
        row
        for row in review_rows()
        if row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
        and row["evidence_source_accession"] == "G3SX30"
    ]
    assert len(rows) == 1
    return rows[0]


def test_ortholog_evidence_review_decision_table_has_one_g3sx30_row() -> None:
    row = g3sx30_review_row()

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["lane_name"] == "tp53_mdm2_elephant"
    assert row["gene_symbol"] == "MDM2"
    assert row["target_species"] == "elephant"
    assert row["target_species_taxid"] == "9785"
    assert row["target_species_name"] == "Loxodonta africana"
    assert row["target_taxid"] == "9785"
    assert row["target_gene_symbol"] == "MDM2"
    assert row["target_protein_accession"] == "G3SX30"
    assert row["target_sequence_length"] == "492"


def test_ortholog_evidence_review_decision_row_traces_collected_source_intake() -> None:
    row = g3sx30_review_row()
    intake_rows = read_csv_rows(INTAKE_PATH)

    assert row["review_source_table"] == "data/input/ortholog_evidence_intake.csv"
    assert row["intake_table"] == "data/input/ortholog_evidence_intake.csv"
    assert row["intake_source_table"] == (
        "data/input/ortholog_stronger_source_evidence_collection.csv"
    )
    assert row["intake_source_table"] != "data/input/tp53_mdm2_ortholog_repair_decisions.csv"
    assert row["intake_source_row_index"] == "1"

    intake_row = intake_rows[int(row["review_source_row_index"]) - 1]
    assert intake_row["candidate_id"] == row["candidate_id"]
    assert intake_row["source_table"] == row["intake_source_table"]
    assert intake_row["source_row_index"] == row["intake_source_row_index"]
    assert intake_row["intake_outcome"] == "evidence_ready_for_review_decision"
    assert intake_row["allowed_next_action_after_intake"] == ("prepare_later_reviewed_decision_pr")


def test_ortholog_evidence_review_decision_row_uses_schema_allowed_decision() -> None:
    schema = load_yaml(SCHEMA_PATH)
    row = g3sx30_review_row()
    rule = schema["review_decision_rules"][row["review_decision"]]

    assert row["review_decision"] in schema["allowed_review_decisions"]
    assert row["review_decision"] == "accepted_for_planning_after_review"
    assert rule["automatic_gate4_gate5_policy_update_allowed"] is False
    assert rule["gate8_eligible"] is False
    assert rule["gate9_eligible"] is False
    assert rule["embedding_ready"] is False
    assert rule["biohub_ready"] is False
    assert rule["boltz_ready"] is False
    assert rule["af3_ready"] is False
    assert rule["chai_ready"] is False
    assert rule["validated_ortholog_claim_allowed"] is False
    assert rule["biological_claim_allowed"] is False


def test_ortholog_evidence_review_decision_row_remains_policy_blocked() -> None:
    row = g3sx30_review_row()

    assert row["downstream_block_status_after_review"] == (
        "reviewed_for_planning_still_policy_blocked"
    )
    assert row["allowed_next_action_after_review"] == (
        "consider_later_explicit_gate4_gate5_policy_update"
    )
    assert row["claim_policy_after_review"] == "no_biological_claims_until_validation"
    assert row["claim_status_after_review"] == "repair_worklist"
    assert "does not automatically update Gate 4 / Gate 5 policy" in row["reviewer_note"]
    assert "does not promote Gate 8 or Gate 9" in row["reviewer_note"]
    assert "does not make biological claims" in row["reviewer_note"]


def test_ortholog_evidence_review_decision_row_forbids_runtime_side_effects() -> None:
    row = g3sx30_review_row()
    forbidden = row["forbidden_actions_after_review"]

    for action in review.RUNTIME_SIDE_EFFECTS:
        assert action in forbidden

    assert "automatic Gate 4 or Gate 5 policy update" in forbidden
    assert "sequence fetch" in forbidden
    assert "Biohub call" in forbidden
    assert "embedding generation" in forbidden
    assert "Boltz call" in forbidden
    assert "AF3 call" in forbidden
    assert "Chai call" in forbidden
    assert "Gate 8 promotion" in forbidden
    assert "Gate 9 promotion" in forbidden
    assert "biological claim" in forbidden


def test_ortholog_evidence_review_decision_table_uses_module_columns() -> None:
    header = TABLE_PATH.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert tuple(header) == review.REQUIRED_COLUMNS


def test_ortholog_evidence_review_decision_table_uses_schema_required_fields() -> None:
    schema = load_yaml(SCHEMA_PATH)
    header = set(TABLE_PATH.read_text(encoding="utf-8").splitlines()[0].split(","))
    required = set(schema["required_row_identity_fields"]) | set(schema["required_review_fields"])
    assert required <= header
