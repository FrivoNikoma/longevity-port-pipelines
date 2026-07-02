from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import gated_contrast
from longevity_port_pipelines.stages import tp53_mdm2_generic_gated_contrast as stage
from longevity_port_pipelines.stages.cofolding_readiness_runtime import (
    build_generic_cofolding_readiness,
)

REPAIR_SCHEMA = {
    "candidate_set": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "target_species": pl.Utf8,
    "coverage_preflight_status": pl.Utf8,
    "source_ortholog_status": pl.Utf8,
    "local_candidate_row_status": pl.Utf8,
    "recommended_next_acction": pl.Utf8,
    "repair_decision": pl.Utf8,
    "repair_priority": pl.Utf8,
    "claim_policy": pl.Utf8,
    "repair_note": pl.Utf8,
}

CONTEXT_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "target_species": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "partner_context_status": pl.Utf8,
    "source_provenance_status": pl.Utf8,
    "cofolding_input_review_status": pl.Utf8,
    "live_opt_in_status": pl.Utf8,
}


def repair_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=REPAIR_SCHEMA)


def repair_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_set": "tp53_mdm2_elephant",
        "candidate_id": "tp53_mdm2_elephant_seed_tp53_chain",
        "pdb_id": "1ycr",
        "chain": "B",
        "source_uniprot": "P04637",
        "partner_uniprot": "Q00987",
        "target_species": "elephant",
        "coverage_preflight_status": "blocked_pending_coverage_repair",
        "source_ortholog_status": "not_checked",
        "local_candidate_row_status": "not_checked",
        "recommended_next_acction": "curate_or_fetch_tp53_mdm2_source_ortholog_rows",
        "repair_decision": "repair_before_claim",
        "repair_priority": "1",
        "claim_policy": "no_biological_claims_until_validation",
        "repair_note": "TP53/MDM2 coverage remains unresolved.",
    }
    row.update(overrides)
    return row


def context_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=CONTEXT_SCHEMA)


def context_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2_elephant",
        "candidate_id": "tp53_mdm2_elephant_seed_tp53_chain",
        "pdb_id": "1ycr",
        "chain": "B",
        "source_uniprot": "P04637",
        "target_species": "elephant",
        "partner_uniprot": "Q00987",
        "partner_context_status": "partner_context_ready",
        "source_provenance_status": "source_provenance_ready",
        "cofolding_input_review_status": "dry_run_inputs_reviewed",
        "live_opt_in_status": "live_not_requested",
    }
    row.update(overrides)
    return row


def test_tp53_mdm2_generic_gate8_blocked_summary_schema_matches_generic_gate8() -> None:
    summary = stage.build_tp53_mdm2_generic_gated_contrast_blocked_summary(
        repair_rows([repair_row()]),
    )

    assert summary.columns == list(gated_contrast.GATED_CONTRAST_SCHEMA)


def test_tp53_mdm2_generic_gate8_blocked_summary_records_blocked_state() -> None:
    summary = stage.build_tp53_mdm2_generic_gated_contrast_blocked_summary(
        repair_rows([repair_row()]),
    )

    assert summary.height == 1
    row = summary.row(0, named=True)

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["lane_name"] == "tp53_mdm2_elephant"
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_tp53_chain"
    assert row["pdb_id"] == "1ycr"
    assert row["chain"] == "B"
    assert row["source_uniprot"] == "P04637"
    assert row["priority"] == "1"
    assert row["long_lived_species"] == "elephant"
    assert row["short_lived_species"] == ""
    assert row["short_lived_control_count"] == 0
    assert row["contrast_status"] == "blocked_strict_panel_not_ready"
    assert (
        row["recommended_next_action"] == "resolve_tp53_mdm2_coverage_repair_before_gate8_contrast"
    )
    assert row["contrast_dry_run_allowed"] is False
    assert row["controlled_claim_allowed"] is False
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "blocked_before_gate8_contrast"
    assert row["contrast_requires_review"] is True
    assert row["robustness_status"] == "blocked_before_robustness_review"
    assert "blocked technical checkpoint" in row["contrast_note"]


def test_tp53_mdm2_generic_gate8_blocked_summary_can_feed_gate9_as_blocked() -> None:
    summary = stage.build_tp53_mdm2_generic_gated_contrast_blocked_summary(
        repair_rows([repair_row()]),
    )
    context = context_rows([context_row()])

    readiness = build_generic_cofolding_readiness(summary, context)

    assert readiness.height == 1
    row = readiness.row(0, named=True)

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["target_species"] == "elephant"
    assert row["partner_uniprot"] == "Q00987"
    assert row["cofolding_readiness_status"] == "blocked_contrast_not_ready"
    assert row["recommended_next_action"] == "resolve_gate8_contrast_status_before_cofolding"
    assert row["cofolding_dry_run_allowed"] is False
    assert row["live_cofolding_allowed"] is False
    assert row["controlled_claim_allowed"] is False


def test_tp53_mdm2_generic_gate8_blocked_summary_status_counts() -> None:
    summary = stage.build_tp53_mdm2_generic_gated_contrast_blocked_summary(
        repair_rows(
            [
                repair_row(candidate_id="candidate_a"),
                repair_row(candidate_id="candidate_b"),
            ]
        ),
    )

    assert stage.tp53_mdm2_generic_gate8_status_counts(summary) == {
        "blocked_strict_panel_not_ready": 2,
    }


def test_tp53_mdm2_generic_gate8_blocked_summary_validates_required_columns() -> None:
    with pytest.raises(ValueError, match="repair_decisions is missing required columns"):
        stage.build_tp53_mdm2_generic_gated_contrast_blocked_summary(
            repair_rows([repair_row()]).drop("repair_decision"),
        )


def test_write_tp53_mdm2_generic_gate8_blocked_summary_writes_csv(tmp_path: Path) -> None:
    output = tmp_path / "tp53_mdm2_generic_gated_contrast_summary.csv"

    summary = stage.write_tp53_mdm2_generic_gated_contrast_blocked_summary(
        repair_decisions=repair_rows([repair_row()]),
        output=output,
    )

    assert output.exists()
    written = pl.read_csv(output)

    assert written.height == summary.height
    assert written.columns == list(gated_contrast.GATED_CONTRAST_SCHEMA)
