from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTAKE_TABLE_PATH = ROOT / "data/input/ortholog_evidence_intake.csv"
INTAKE_SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_intake_schema.yaml"
REVIEW_DECISIONS_PATH = ROOT / "data/input/generic_repair_queue_review_decisions.csv"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def intake_rows() -> list[dict[str, str]]:
    rows = read_csv_rows(INTAKE_TABLE_PATH)
    assert len(rows) == 4
    return rows


def test_ortholog_evidence_intake_table_exists_with_scaffold_and_first_candidate_row() -> None:
    rows = intake_rows()

    assert {
        (
            row["source_table"],
            row["source_row_index"],
            row["candidate_id"],
            row["evidence_source_accession"],
        )
        for row in rows
    } == {
        (
            "data/input/sirt6_candidate_coverage_repair_decisions.csv",
            "1",
            "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
            "NCBI Taxonomy:27602; UniProt Taxonomy:27602",
        ),
        (
            "data/input/tp53_mdm2_ortholog_repair_decisions.csv",
            "1",
            "tp53_mdm2_elephant_seed_tp53_chain",
            "data/input/tp53_mdm2_ortholog_repair_decisions.csv#1",
        ),
        (
            "data/input/tp53_mdm2_ortholog_repair_decisions.csv",
            "2",
            "tp53_mdm2_elephant_seed_mdm2_chain",
            "data/input/tp53_mdm2_ortholog_repair_decisions.csv#2",
        ),
        (
            "data/input/tp53_mdm2_ortholog_repair_decisions.csv",
            "2",
            "tp53_mdm2_elephant_seed_mdm2_chain",
            "G3SX30",
        ),
    }

    assert {row["intake_outcome"] for row in rows} == {
        "evidence_insufficient_defer",
        "evidence_ambiguous_needs_second_reviewer",
    }
    assert {row["target_protein_accession"] for row in rows} == {"unresolved", "G3SX30"}
    assert {row["downstream_block_status_after_intake"] for row in rows} == {"blocked_gate4_gate5"}


def test_first_real_mdm2_elephant_evidence_candidate_row_is_accession_level_only() -> None:
    rows = intake_rows()
    matching = [
        row
        for row in rows
        if row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
        and row["evidence_source_accession"] == "G3SX30"
    ]

    assert len(matching) == 1
    row = matching[0]

    assert row["gene_symbol"] == "MDM2"
    assert row["target_species"] == "elephant"
    assert row["target_species_taxid"] == "9785"
    assert row["evidence_source_type"] == "uniprot_ortholog_or_taxonomy_evidence"
    assert row["evidence_source_database"] == "UniProtKB TrEMBL"
    assert row["target_species_name"] == "Loxodonta africana"
    assert row["target_gene_symbol"] == "MDM2"
    assert row["target_protein_accession"] == "G3SX30"
    assert row["target_sequence_length"] == "492"
    assert row["ambiguity_flag"] == "true"
    assert row["second_reviewer_required"] == "true"
    assert row["intake_outcome"] == "evidence_ambiguous_needs_second_reviewer"
    assert row["allowed_next_action_after_intake"] == (
        "perform_second_reviewer_evidence_intake_review"
    )


def test_ortholog_evidence_intake_table_uses_schema_required_fields() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    required_fields = set(schema["required_row_identity_fields"]) | set(
        schema["required_evidence_fields"]
    )

    for row in intake_rows():
        assert required_fields <= set(row)
        assert all(row[field] for field in required_fields)


def test_ortholog_evidence_intake_table_uses_allowed_sources_and_outcomes() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    allowed_sources = set(schema["allowed_evidence_source_types"])
    allowed_outcomes = set(schema["allowed_intake_outcomes"])

    for row in intake_rows():
        assert row["evidence_source_type"] in allowed_sources
        assert row["intake_outcome"] in allowed_outcomes


def test_ortholog_evidence_intake_table_traces_reviewed_provenance_rows() -> None:
    review_rows = read_csv_rows(REVIEW_DECISIONS_PATH)
    review_index = {
        (row["source_table"], row["source_row_index"], row["candidate_id"]): row
        for row in review_rows
    }

    for row in intake_rows():
        key = (row["source_table"], row["source_row_index"], row["candidate_id"])
        reviewed_row = review_index[key]

        assert row["candidate_set"] == reviewed_row["candidate_set"]
        assert row["lane_name"] == reviewed_row["lane_name"]
        assert row["source_species"] == reviewed_row["source_species"]
        assert row["target_species"] == reviewed_row["target_species"]
        assert row["target_species_taxid"] == reviewed_row["target_species_taxid"]
        assert row["source_uniprot"] == reviewed_row["source_uniprot"]
        assert row["partner_uniprot"] == reviewed_row["partner_uniprot"]
        assert row["target_uniprot_before_intake"] == reviewed_row["target_uniprot_before_review"]
        assert row["coverage_status_before_intake"] == reviewed_row["coverage_status_before_review"]
        assert (
            row["provenance_status_before_intake"]
            == reviewed_row["provenance_status_before_review"]
        )
        assert (
            row["repair_queue_status_before_intake"]
            == reviewed_row["repair_queue_status_before_review"]
        )


def test_ortholog_evidence_intake_table_keeps_downstream_blocked_by_schema_rule() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)

    for row in intake_rows():
        rule = schema["intake_outcome_rules"][row["intake_outcome"]]

        assert rule["gate4_gate5_policy_update_allowed"] is False
        assert rule["gate8_eligible"] is False
        assert rule["gate9_eligible"] is False
        assert rule["embedding_ready"] is False
        assert rule["biohub_ready"] is False
        assert rule["boltz_ready"] is False
        assert rule["af3_ready"] is False
        assert rule["chai_ready"] is False
        assert rule["accepted_ortholog_claim_allowed"] is False
        assert rule["validated_ortholog_claim_allowed"] is False
        assert rule["biological_claim_allowed"] is False
        assert rule["does_not_auto_accept_ortholog"] is True
        assert (
            row["downstream_block_status_after_intake"]
            == rule["downstream_block_status_after_intake"]
        )
        assert row["allowed_next_action_after_intake"] == rule["allowed_next_action_after_intake"]
        assert row["claim_status_after_intake"] == rule["claim_status_after_intake"]


def test_ortholog_evidence_intake_table_records_blocker_first_guardrails() -> None:
    for row in intake_rows():
        forbidden_actions = row["forbidden_actions_after_intake"]

        assert row["claim_policy_after_intake"] == "no_biological_claims_until_validation"
        assert row["claim_status_after_intake"] == "repair_worklist"
        assert row["ambiguity_flag"] == "true"
        assert row["second_reviewer_required"] == "true"
        assert "Gate 8 promotion" in forbidden_actions
        assert "Gate 9 promotion" in forbidden_actions
        assert "Biohub call" in forbidden_actions
        assert "embedding generation" in forbidden_actions
        assert "Boltz call" in forbidden_actions
        assert "biological claim" in forbidden_actions


def test_ortholog_evidence_intake_table_does_not_accept_orthologs() -> None:
    forbidden_values = {
        "accepted_for_planning_after_review",
        "validated_ortholog",
        "validated_biological_signal",
        "validated_longevity_signal",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "embedding ready",
        "Boltz ready",
        "safe_to_port",
    }

    observed_values: set[str] = set()
    for row in intake_rows():
        observed_values.update(row.values())

    assert observed_values.isdisjoint(forbidden_values)
