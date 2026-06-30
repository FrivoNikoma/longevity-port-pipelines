from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import candidate_contrast_gate as gate


def contrast_ready_rows(status: str = "contrast_ready") -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "n_coverage_ready_species": 5,
                "n_long_lived_ready": 2,
                "n_short_lived_ready": 3,
                "ready_long_lived_species": "myotis_lucifugus,naked_mole_rat",
                "ready_short_lived_species": "hamster,mouse,rat",
                "contrast_readiness_status": status,
                "recommended_next_action": "prepare_long_lived_vs_short_lived_contrast",
            }
        ]
    )


def negatome_readiness_rows(
    *,
    baseline_status: str = "input_prepared",
    species_status: str = "complete_species_coverage",
    negatome_status: str = "present_existing",
) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "baseline_input_status": baseline_status,
                "species_coverage_status": species_status,
                "negatome_status": negatome_status,
                "negative_partner_uniprot": "O60907",
                "missing_negatome_species": "",
                "recommended_next_action": "ready_for_human_baseline",
            }
        ]
    )


def coverage_repair_rows() -> pl.DataFrame:
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
                "group": "long-lived",
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


def test_contrast_gate_marks_candidate_eligible_for_dry_run() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "eligible_for_contrast_dry_run"
    assert row["recommended_next_action"] == "prepare_contrast_dry_run"
    assert "no enrichment statistic" in row["gate_note"]


def test_contrast_gate_blocks_contrast_coverage_first() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(status="insufficient_short_lived_coverage"),
        negatome_readiness=negatome_readiness_rows(),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_contrast_coverage"
    assert row["recommended_next_action"] == "repair_contrast_species_coverage"


def test_contrast_gate_blocks_baseline_input_after_contrast_coverage() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(
            baseline_status="missing_baseline_input",
        ),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_baseline_input"
    assert row["recommended_next_action"] == "fix_baseline_input"


def test_contrast_gate_blocks_species_coverage_before_negatome() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(
            species_status="missing_source_ortholog",
            negatome_status="partial_existing",
        ),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_species_coverage"
    assert row["recommended_next_action"] == "fix_species_coverage"


def test_contrast_gate_blocks_negatome_when_species_is_complete() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(
            species_status="complete_species_coverage",
            negatome_status="partial_existing",
        ),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_negatome_controls"
    assert row["recommended_next_action"] == "fix_negatome_controls"


def test_contrast_gate_validates_required_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        gate.build_candidate_contrast_gate(
            contrast_ready=pl.DataFrame({"candidate_id": ["candidate_a"]}),
            negatome_readiness=negatome_readiness_rows(),
        )


def test_empty_contrast_gate_has_schema() -> None:
    result = gate.empty_contrast_gate()

    assert result.is_empty()
    assert result.columns == list(gate.CONTRAST_GATE_SCHEMA)


def test_contrast_gate_uses_coverage_repair_decisions_for_species_blocker() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(
            species_status="missing_source_ortholog",
            negatome_status="partial_existing",
        ),
        coverage_repair_decisions=coverage_repair_rows(),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_species_coverage"
    assert row["coverage_repair_decision_status"] == "manual_review_required_deferred_no_claim"
    assert row["n_coverage_repair_decision_rows"] == 1
    assert row["coverage_repair_target_species"] == "bowhead_whale"
    assert row["coverage_repair_decisions"] == "needs_external_manual_sequence_review"
    assert row["coverage_repair_priorities"] == "high"
    assert row["coverage_repair_claim_policies"] == "deferred_no_claim"
    assert row["recommended_next_action"] == "review_manual_coverage_repair_decisions"
    assert "deferred_no_claim" in row["gate_note"]


def test_contrast_gate_marks_missing_repair_decision_when_table_is_provided() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(
            species_status="missing_source_ortholog",
            negatome_status="partial_existing",
        ),
        coverage_repair_decisions=coverage_repair_rows().head(0),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_species_coverage"
    assert row["coverage_repair_decision_status"] == "missing_repair_decision"
    assert row["n_coverage_repair_decision_rows"] == 0
    assert row["recommended_next_action"] == "add_coverage_repair_decision"
    assert "no coverage repair decision" in row["gate_note"]


def strict_panel_summary_rows(
    *,
    status: str = "strict_panel_ready",
    candidate_id: str = "candidate_a",
) -> pl.DataFrame:
    blocked = status != "strict_panel_ready"
    return pl.DataFrame(
        [
            {
                "candidate_id": candidate_id,
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "n_strict_panel_ready_species": 2,
                "n_strict_panel_blocked_species": 1 if blocked else 0,
                "n_strict_long_lived_ready": 1,
                "n_strict_short_lived_ready": 1,
                "strict_long_lived_species": "naked_mole_rat",
                "strict_short_lived_species": "mouse",
                "blocked_target_species": "bowhead_whale" if blocked else "",
                "strict_panel_status": status,
                "recommended_next_action": (
                    "resolve_coverage_repair_decisions"
                    if blocked
                    else "prepare_strict_contrast_dry_run"
                ),
                "strict_panel_note": (
                    "Strict panel builder only audits coverage and repair policy."
                ),
            }
        ]
    )


def test_contrast_gate_records_strict_panel_ready_summary() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(),
        strict_panel_summary=strict_panel_summary_rows(),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "eligible_for_contrast_dry_run"
    assert row["strict_panel_status"] == "strict_panel_ready"
    assert row["n_strict_panel_ready_species"] == 2
    assert row["n_strict_panel_blocked_species"] == 0
    assert row["strict_long_lived_species"] == "naked_mole_rat"
    assert row["strict_short_lived_species"] == "mouse"
    assert row["recommended_next_action"] == "prepare_contrast_dry_run"


def test_contrast_gate_blocks_strict_panel_before_negatome_controls() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(negatome_status="partial_existing"),
        strict_panel_summary=strict_panel_summary_rows(
            status="blocked_species_coverage_repair",
        ),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_strict_panel"
    assert row["strict_panel_status"] == "blocked_species_coverage_repair"
    assert row["blocked_target_species"] == "bowhead_whale"
    assert row["recommended_next_action"] == "resolve_strict_panel_coverage_repairs"
    assert "Strict panel summary has unresolved coverage repair rows" in row["gate_note"]


def test_contrast_gate_blocks_missing_strict_panel_summary_row() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(),
        strict_panel_summary=strict_panel_summary_rows(candidate_id="other_candidate"),
    )

    row = result.filter(pl.col("candidate_id") == "candidate_a").row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_strict_panel"
    assert row["strict_panel_status"] == "missing_strict_panel_summary_row"
    assert row["recommended_next_action"] == "build_strict_panel_summary"


def negatome_repair_decision_rows(
    *,
    status: str = "partial_existing",
    claim_policy: str = "deferred_no_claim",
    candidate_id: str = "candidate_a",
) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": candidate_id,
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "negatome_status": status,
                "negative_partner_uniprot": "O60907",
                "missing_negatome_species": "bowhead_whale",
                "repair_decision": "complete_missing_negatome_species",
                "repair_priority": "high",
                "claim_policy": claim_policy,
                "repair_note": (
                    "Complete missing NEGATOME-style controls before controlled claims."
                ),
            }
        ]
    )


def test_contrast_gate_uses_negatome_repair_decisions_for_control_blocker() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(negatome_status="partial_existing"),
        negatome_repair_decisions=negatome_repair_decision_rows(),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_negatome_repair_policy"
    assert row["negatome_repair_decision_status"] == "negatome_repair_required_deferred_no_claim"
    assert row["n_negatome_repair_decision_rows"] == 1
    assert row["negatome_repair_missing_species"] == "bowhead_whale"
    assert row["negatome_repair_decisions"] == "complete_missing_negatome_species"
    assert row["negatome_repair_priorities"] == "high"
    assert row["negatome_repair_claim_policies"] == "deferred_no_claim"
    assert row["recommended_next_action"] == "complete_negatome_repair_before_controlled_claim"
    assert "NEGATOME repair decision remains deferred_no_claim" in row["gate_note"]


def test_contrast_gate_marks_missing_negatome_repair_decision_when_table_is_provided() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(negatome_status="partial_existing"),
        negatome_repair_decisions=negatome_repair_decision_rows(candidate_id="other_candidate"),
    )

    row = result.filter(pl.col("candidate_id") == "candidate_a").row(0, named=True)
    assert row["strict_contrast_gate_status"] == "blocked_negatome_controls"
    assert row["negatome_repair_decision_status"] == "missing_repair_decision"
    assert row["recommended_next_action"] == "add_negatome_repair_decision"
    assert "no NEGATOME repair decision is available yet" in row["gate_note"]


def test_contrast_gate_does_not_require_negatome_repair_when_controls_present() -> None:
    result = gate.build_candidate_contrast_gate(
        contrast_ready=contrast_ready_rows(),
        negatome_readiness=negatome_readiness_rows(negatome_status="present_existing"),
        negatome_repair_decisions=negatome_repair_decision_rows(),
    )

    row = result.row(0, named=True)
    assert row["strict_contrast_gate_status"] == "eligible_for_contrast_dry_run"
    assert row["negatome_repair_decision_status"] == "not_required"
    assert row["n_negatome_repair_decision_rows"] == 1
