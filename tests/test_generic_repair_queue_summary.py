from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import generic_repair_queue_summary as summary


def sirt6_repair_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "bowhead_whale",
                "target_species_taxid": "27622",
                "group": "long-lived",
                "coverage_gap_status": "missing_ortholog_but_local_rows_present",
                "recommended_coverage_action": (
                    "local_downstream_evidence_without_source_ortholog"
                ),
                "candidate_target_uniprots": "",
                "ortholog_source_dbs": "",
                "ortholog_source_files": "",
                "local_files": "data/output/readiness_audit.csv",
                "repair_decision": "needs_external_manual_sequence_review",
                "repair_priority": "high",
                "claim_policy": "deferred_no_claim",
                "repair_note": (
                    "Local downstream rows exist, but source ortholog provenance "
                    "is missing; defer strict contrast use until manual provenance review."
                ),
            }
        ]
    )


def tp53_mdm2_repair_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_set": "tp53_mdm2_elephant",
                "candidate_id": "tp53_mdm2_elephant_seed_tp53_chain",
                "lane_name": "tp53_mdm2_elephant",
                "pdb_id": "1ycr",
                "chain": "B",
                "source_species": "human",
                "target_species": "elephant",
                "gene_symbol": "TP53",
                "source_uniprot": "P04637",
                "partner_uniprot": "Q00987",
                "target_uniprot": "unresolved",
                "coverage_status": "unresolved_downstream_provenance",
                "provenance_status": "unresolved",
                "recommended_next_action": ("curate_or_fetch_tp53_mdm2_source_ortholog_coverage"),
                "repair_decision": "fetch_or_curate_source_ortholog",
                "repair_status": "pending",
                "repair_priority": "high",
                "claim_policy": "ortholog_repair_only",
                "reviewer_note": (
                    "Generic repair vocabulary alignment only; elephant target UniProt "
                    "remains unresolved and must be fetched or manually curated before "
                    "downstream eligibility."
                ),
            }
        ]
    )


def test_empty_generic_repair_queue_summary_has_schema_columns() -> None:
    empty = summary.empty_generic_repair_queue_summary()

    assert empty.is_empty()
    assert empty.columns == list(summary.SUMMARY_SCHEMA)


def test_validate_required_columns_rejects_missing_sirt6_column() -> None:
    rows = sirt6_repair_rows().drop("repair_note")

    with pytest.raises(ValueError, match="SIRT6 repair table is missing required columns"):
        summary.validate_required_columns(
            rows,
            required_columns=summary.SIRT6_REQUIRED_COLUMNS,
            table_name="SIRT6 repair table",
        )


def test_sirt6_rows_to_generic_summary_maps_manual_review_blocker() -> None:
    generic_rows = summary.sirt6_rows_to_generic_summary(sirt6_repair_rows())

    assert generic_rows.columns == list(summary.SUMMARY_SCHEMA)
    assert generic_rows.height == 1

    row = generic_rows.row(0, named=True)

    assert row["candidate_set"] == "sirt6_dna_repair"
    assert row["lane_name"] == "SIRT6/core3"
    assert row["source_species"] == "human"
    assert row["target_species"] == "bowhead_whale"
    assert row["gene_symbol"] == "unresolved"
    assert row["target_uniprot"] == "unresolved"
    assert row["coverage_status"] == "local_rows_without_source_ortholog"
    assert row["provenance_status"] == "external_review_required"
    assert row["repair_status"] == "needs_manual_review"
    assert row["repair_queue_status"] == "blocked_pending_manual_review"
    assert row["downstream_block_status"] == "blocked_gate4_gate5"
    assert row["allowed_next_action"] == "manual_sequence_provenance_review"
    assert row["claim_status"] == "repair_worklist"


def test_tp53_mdm2_rows_to_generic_summary_keeps_source_ortholog_blocker() -> None:
    generic_rows = summary.tp53_mdm2_rows_to_generic_summary(tp53_mdm2_repair_rows())

    assert generic_rows.columns == list(summary.SUMMARY_SCHEMA)
    assert generic_rows.height == 1

    row = generic_rows.row(0, named=True)

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["lane_name"] == "tp53_mdm2_elephant"
    assert row["source_species"] == "human"
    assert row["target_species"] == "elephant"
    assert row["gene_symbol"] == "TP53"
    assert row["target_uniprot"] == "unresolved"
    assert row["coverage_status"] == "unresolved_downstream_provenance"
    assert row["provenance_status"] == "unresolved"
    assert row["repair_status"] == "pending"
    assert row["repair_queue_status"] == "blocked_pending_source_ortholog_repair"
    assert row["downstream_block_status"] == "blocked_gate4_gate5"
    assert row["allowed_next_action"] == "fetch_or_curate_source_ortholog"
    assert row["claim_status"] == "repair_worklist"


def test_build_generic_repair_queue_summary_combines_lanes() -> None:
    repair_summary = summary.build_generic_repair_queue_summary(
        sirt6_rows=sirt6_repair_rows(),
        tp53_mdm2_rows=tp53_mdm2_repair_rows(),
    )

    assert repair_summary.columns == list(summary.SUMMARY_SCHEMA)
    assert repair_summary.height == 2
    assert set(repair_summary.get_column("candidate_set").to_list()) == {
        "sirt6_dna_repair",
        "tp53_mdm2_elephant",
    }
    assert set(repair_summary.get_column("downstream_block_status").to_list()) == {
        "blocked_gate4_gate5"
    }


def test_committed_repair_tables_build_expected_summary_without_downstream_promotion() -> None:
    repair_summary = summary.build_generic_repair_queue_summary(
        sirt6_rows=summary.read_repair_table(summary.DEFAULT_SIRT6_REPAIR),
        tp53_mdm2_rows=summary.read_repair_table(summary.DEFAULT_TP53_MDM2_REPAIR),
    )

    assert repair_summary.height == 13
    assert set(repair_summary.get_column("candidate_set").to_list()) == {
        "sirt6_dna_repair",
        "tp53_mdm2_elephant",
    }
    assert set(repair_summary.get_column("downstream_block_status").to_list()) == {
        "blocked_gate4_gate5"
    }


def test_repair_queue_status_counts_counts_blocker_types() -> None:
    repair_summary = summary.build_generic_repair_queue_summary(
        sirt6_rows=sirt6_repair_rows(),
        tp53_mdm2_rows=tp53_mdm2_repair_rows(),
    )

    counts = summary.repair_queue_status_counts(repair_summary)
    observed = {row["repair_queue_status"]: row["n_rows"] for row in counts.to_dicts()}

    assert observed == {
        "blocked_pending_manual_review": 1,
        "blocked_pending_source_ortholog_repair": 1,
    }


def test_summary_forbids_runtime_side_effects_and_biological_claims() -> None:
    repair_summary = summary.build_generic_repair_queue_summary(
        sirt6_rows=sirt6_repair_rows(),
        tp53_mdm2_rows=tp53_mdm2_repair_rows(),
    )

    for row in repair_summary.to_dicts():
        assert "sequence fetch" in row["forbidden_actions"]
        assert "manual ortholog curation" in row["forbidden_actions"]
        assert "Biohub call" in row["forbidden_actions"]
        assert "embedding generation" in row["forbidden_actions"]
        assert "Boltz call" in row["forbidden_actions"]
        assert "Gate 8 promotion" in row["forbidden_actions"]
        assert "Gate 9 promotion" in row["forbidden_actions"]
        assert "biological claim" in row["forbidden_actions"]
