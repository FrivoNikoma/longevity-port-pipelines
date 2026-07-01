from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import strict_sirt6_contrast_panel as strict


def coverage_matrix_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "mouse",
                "target_species_taxid": 10090,
                "group": "short_lived_control",
                "coverage_gap_status": "ortholog_and_local_rows_present",
                "recommended_coverage_action": "coverage_ready",
            },
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "naked_mole_rat",
                "target_species_taxid": 10181,
                "group": "long_lived_small_body",
                "coverage_gap_status": "ortholog_and_local_rows_present",
                "recommended_coverage_action": "coverage_ready",
            },
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "bowhead_whale",
                "target_species_taxid": 27622,
                "group": "long_lived_large_body",
                "coverage_gap_status": "missing_ortholog_but_local_rows_present",
                "recommended_coverage_action": "local_downstream_evidence_without_source_ortholog",
            },
        ]
    )


def repair_decision_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "bowhead_whale",
                "target_species_taxid": "27622",
                "group": "long_lived_large_body",
                "coverage_gap_status": "missing_ortholog_but_local_rows_present",
                "recommended_coverage_action": "local_downstream_evidence_without_source_ortholog",
                "candidate_target_uniprots": "",
                "ortholog_source_dbs": "",
                "ortholog_source_files": "",
                "local_files": "data/output/example.csv",
                "repair_decision": "needs_external_manual_sequence_review",
                "repair_priority": "high",
                "claim_policy": "deferred_no_claim",
                "repair_note": "Manual provenance review is required before strict contrast use.",
            }
        ]
    )


def ready_only_coverage_rows() -> pl.DataFrame:
    return coverage_matrix_rows().filter(pl.col("target_species") != "bowhead_whale")


def test_strict_panel_marks_coverage_ready_rows_as_panel_ready() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=ready_only_coverage_rows(),
        repair_decisions=repair_decision_rows(),
    )

    assert panel.height == 2
    assert set(panel.get_column("strict_panel_status").to_list()) == {"strict_panel_ready"}
    assert set(panel.get_column("strict_panel_include").to_list()) == {True}
    assert set(panel.get_column("strict_panel_claim_policy").to_list()) == {
        "allowed_for_strict_panel_planning_no_claim"
    }


def test_strict_panel_blocks_deferred_repair_decision_rows() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=coverage_matrix_rows(),
        repair_decisions=repair_decision_rows(),
    )

    row = panel.filter(pl.col("target_species") == "bowhead_whale").row(0, named=True)
    assert row["strict_panel_include"] is False
    assert row["strict_panel_status"] == "blocked_deferred_no_claim"
    assert row["repair_decision"] == "needs_external_manual_sequence_review"
    assert row["repair_priority"] == "high"
    assert row["claim_policy"] == "deferred_no_claim"
    assert row["recommended_next_action"] == "review_manual_coverage_repair_decision"
    assert "manual sequence/provenance review" in row["strict_panel_note"]


def test_strict_panel_blocks_missing_repair_decisions() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=coverage_matrix_rows(),
        repair_decisions=repair_decision_rows().head(0),
    )

    row = panel.filter(pl.col("target_species") == "bowhead_whale").row(0, named=True)
    assert row["strict_panel_include"] is False
    assert row["strict_panel_status"] == "blocked_missing_repair_decision"
    assert row["recommended_next_action"] == "add_coverage_repair_decision"


def test_strict_panel_candidate_summary_blocks_candidates_with_deferred_rows() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=coverage_matrix_rows(),
        repair_decisions=repair_decision_rows(),
    )

    summary = strict.strict_panel_candidate_summary(panel)

    row = summary.row(0, named=True)
    assert row["strict_panel_status"] == "blocked_species_coverage_repair"
    assert row["recommended_next_action"] == "resolve_coverage_repair_decisions"
    assert row["n_strict_panel_ready_species"] == 2
    assert row["n_strict_panel_blocked_species"] == 1
    assert row["strict_long_lived_species"] == "naked_mole_rat"
    assert row["strict_short_lived_species"] == "mouse"
    assert row["blocked_target_species"] == "bowhead_whale"


def test_strict_panel_candidate_summary_marks_clean_panel_ready() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=ready_only_coverage_rows(),
        repair_decisions=repair_decision_rows(),
    )

    summary = strict.strict_panel_candidate_summary(panel)

    row = summary.row(0, named=True)
    assert row["strict_panel_status"] == "strict_panel_ready"
    assert row["recommended_next_action"] == "prepare_strict_contrast_dry_run"
    assert row["n_strict_panel_ready_species"] == 2
    assert row["n_strict_panel_blocked_species"] == 0


def test_strict_panel_validates_required_coverage_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        strict.build_strict_sirt6_contrast_panel(
            coverage_matrix=pl.DataFrame({"candidate_id": ["candidate_a"]}),
            repair_decisions=repair_decision_rows(),
        )


def test_empty_strict_panel_summary_has_schema() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=coverage_matrix_rows().head(0),
        repair_decisions=repair_decision_rows(),
    )
    summary = strict.strict_panel_candidate_summary(panel)

    assert panel.is_empty()
    assert panel.columns == list(strict.STRICT_PANEL_SCHEMA)
    assert summary.is_empty()
    assert summary.columns == list(strict.STRICT_PANEL_SUMMARY_SCHEMA)


def test_strict_panel_records_generic_helper_trace_for_ready_rows() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=ready_only_coverage_rows(),
        repair_decisions=repair_decision_rows(),
    )

    assert set(panel.get_column("generic_coverage_status").to_list()) == {"coverage_ready"}
    assert set(panel.get_column("generic_provenance_status").to_list()) == {
        "standard_source_present"
    }
    assert set(panel.get_column("generic_repair_status").to_list()) == {"not_needed"}
    assert set(panel.get_column("generic_coverage_preflight_status").to_list()) == {
        "coverage_preflight_ready"
    }
    assert set(panel.get_column("generic_recommended_next_action").to_list()) == {
        "run_strict_panel_or_contrast_gate"
    }
    assert set(panel.get_column("generic_strict_panel_allowed").to_list()) == {True}
    assert set(panel.get_column("generic_contrast_dry_run_allowed").to_list()) == {True}
    assert set(panel.get_column("generic_claim_policy").to_list()) == {
        "no_biological_claims_until_validation"
    }
    assert set(panel.get_column("generic_claim_status").to_list()) == {"repair_worklist"}


def test_strict_panel_records_generic_helper_trace_for_blocked_repair_rows() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=coverage_matrix_rows(),
        repair_decisions=repair_decision_rows(),
    )

    row = panel.filter(pl.col("target_species") == "bowhead_whale").row(0, named=True)

    assert row["generic_coverage_status"] == "local_rows_without_source_ortholog"
    assert row["generic_provenance_status"] == "local_row_present_without_source"
    assert row["generic_repair_status"] == "needs_manual_review"
    assert row["generic_coverage_preflight_status"] == "blocked_needs_manual_review"
    assert row["generic_recommended_next_action"] == ("request_external_manual_sequence_review")
    assert row["generic_strict_panel_allowed"] is False
    assert row["generic_contrast_dry_run_allowed"] is False
    assert row["generic_claim_policy"] == "no_biological_claims_until_validation"
    assert row["generic_claim_status"] == "repair_worklist"


def test_strict_panel_records_generic_helper_trace_without_repair_decision() -> None:
    panel = strict.build_strict_sirt6_contrast_panel(
        coverage_matrix=coverage_matrix_rows(),
        repair_decisions=repair_decision_rows().head(0),
    )

    row = panel.filter(pl.col("target_species") == "bowhead_whale").row(0, named=True)

    assert row["generic_coverage_status"] == "local_rows_without_source_ortholog"
    assert row["generic_provenance_status"] == "local_row_present_without_source"
    assert row["generic_repair_status"] == ""
    assert row["generic_coverage_preflight_status"] == "blocked_pending_repair_review"
    assert row["generic_recommended_next_action"] == ("complete_ortholog_repair_decision_review")
    assert row["generic_strict_panel_allowed"] is False
    assert row["generic_contrast_dry_run_allowed"] is False
