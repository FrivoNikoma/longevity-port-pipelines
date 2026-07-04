from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_raw_metadata_review as review,
)


def valid_review_row() -> dict[str, str]:
    return {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2_elephant",
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "raw_metadata_response_table": "data/input/ortholog_stronger_source_raw_metadata_responses.csv",
        "raw_metadata_response_source_row_index": "2",
        "gene_symbol": "MDM2",
        "source_species": "human",
        "target_species": "elephant",
        "target_species_taxid": "9785",
        "source_uniprot": "Q00987",
        "partner_uniprot": "P04637",
        "requested_evidence_source_database": "UniProtKB TrEMBL",
        "requested_evidence_source_accession": "G3SX30",
        "target_taxid": "9785",
        "target_species_name": "Loxodonta africana",
        "target_gene_symbol": "MDM2",
        "target_protein_accession": "G3SX30",
        "target_sequence_length": "492",
        "planned_lookup_source_type": "uniprot_entry_metadata",
        "planned_lookup_query_identifier": "G3SX30",
        "raw_metadata_source_type": "uniprot_entry_metadata",
        "raw_metadata_source_name": "UniProtKB REST metadata-only TSV",
        "raw_metadata_source_identifier": "UniProtKB:G3SX30",
        "raw_metadata_status_before_review": "raw_metadata_received_unreviewed",
        "raw_metadata_response_status_before_review": (
            "raw_metadata_received_unreviewed_still_blocked"
        ),
        "raw_metadata_review_status_before_review": "raw_metadata_requires_manual_review",
        "raw_metadata_human_review_status": ("raw_metadata_human_review_complete_still_blocked"),
        "raw_metadata_human_review_decision": (
            "metadata_consistent_prepare_source_evidence_intake_later"
        ),
        "reviewed_metadata_source_type": "uniprot_entry_metadata",
        "reviewed_metadata_source_name": "UniProtKB REST metadata-only TSV",
        "reviewed_metadata_source_identifier": "UniProtKB:G3SX30",
        "reviewed_accession": "G3SX30",
        "reviewed_entry_name": "G3SX30_LOXAF",
        "reviewed_reviewed_status": "unreviewed",
        "reviewed_gene_symbol": "MDM2",
        "reviewed_organism_name": "Loxodonta africana (African elephant)",
        "reviewed_taxid": "9785",
        "reviewed_sequence_length": "492",
        "sequence_review_scope": "metadata_only_no_sequence_reviewed",
        "sequence_fetched": "false",
        "source_evidence_created": "false",
        "source_evidence_creation_status": "not_created_metadata_review_only",
        "reviewed_decision_created": "false",
        "reviewed_decision_creation_status": "not_created_metadata_review_only",
        "gate4_gate5_policy_updated": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "downstream_block_status_after_review": "blocked_gate4_gate5",
        "allowed_next_action_after_review": "prepare_later_source_evidence_intake_pr",
        "claim_policy_after_review": "no_biological_claims_until_validation",
        "claim_status_after_review": "repair_worklist",
        "biological_claim_status": "no_biological_claim",
        "forbidden_actions_after_review": "; ".join(sorted(review.RUNTIME_SIDE_EFFECTS)),
        "reviewer_note": (
            "Synthetic validator row: metadata-only human review remains blocked and "
            "does not create source evidence or downstream permission."
        ),
    }


def test_raw_metadata_review_reader_loads_header_only_committed_table() -> None:
    rows = review.read_raw_metadata_review_rows()

    assert rows.height == 0
    assert rows.columns == list(review.REQUIRED_COLUMNS)
    review.validate_raw_metadata_review_rows(rows)


def test_raw_metadata_review_validator_accepts_synthetic_metadata_only_review_row() -> None:
    rows = pl.DataFrame([valid_review_row()]).select(list(review.REQUIRED_COLUMNS))

    review.validate_raw_metadata_review_rows(rows)


def test_raw_metadata_review_validator_rejects_missing_columns() -> None:
    rows = pl.DataFrame([valid_review_row()]).drop("reviewer_note")

    with pytest.raises(ValueError, match="missing required columns"):
        review.validate_raw_metadata_review_rows(rows)


def test_raw_metadata_review_validator_rejects_duplicate_keys() -> None:
    row = valid_review_row()
    rows = pl.DataFrame([row, dict(row)]).select(list(review.REQUIRED_COLUMNS))

    with pytest.raises(ValueError, match="duplicate review keys"):
        review.validate_raw_metadata_review_rows(rows)


def test_raw_metadata_review_validator_rejects_side_effect_flags() -> None:
    row = valid_review_row()
    row["source_evidence_created"] = "true"
    rows = pl.DataFrame([row]).select(list(review.REQUIRED_COLUMNS))

    with pytest.raises(ValueError, match="side-effect flags"):
        review.validate_raw_metadata_review_rows(rows)


def test_raw_metadata_review_validator_rejects_decision_rule_mismatch() -> None:
    row = valid_review_row()
    row["allowed_next_action_after_review"] = "promote_gate8"
    rows = pl.DataFrame([row]).select(list(review.REQUIRED_COLUMNS))

    with pytest.raises(ValueError, match="decision-rule mismatches"):
        review.validate_raw_metadata_review_rows(rows)


def test_raw_metadata_review_validator_rejects_disallowed_claim_values() -> None:
    row = valid_review_row()
    row["reviewer_note"] = "Gate 8 eligible"
    rows = pl.DataFrame([row]).select(list(review.REQUIRED_COLUMNS))

    with pytest.raises(ValueError, match="disallowed claim values"):
        review.validate_raw_metadata_review_rows(rows)


def test_raw_metadata_review_candidate_helpers_return_expected_subsets() -> None:
    row = valid_review_row()
    pending = valid_review_row()
    pending["raw_metadata_response_source_row_index"] = "3"
    pending["raw_metadata_source_identifier"] = "dry_run:G3SX30"
    pending["raw_metadata_human_review_status"] = "pending_raw_metadata_human_review"
    pending["raw_metadata_human_review_decision"] = "pending"
    pending["reviewed_metadata_source_type"] = "unresolved"
    pending["reviewed_reviewed_status"] = "unresolved"
    pending["reviewed_sequence_length"] = "unresolved"
    pending["sequence_review_scope"] = "not_reviewed_pending"
    pending["allowed_next_action_after_review"] = "perform_raw_metadata_human_review"

    rows = pl.DataFrame([row, pending]).select(list(review.REQUIRED_COLUMNS))

    review.validate_raw_metadata_review_rows(rows)
    assert review.pending_raw_metadata_review_rows(rows).height == 1
    assert review.completed_still_blocked_raw_metadata_review_rows(rows).height == 1
