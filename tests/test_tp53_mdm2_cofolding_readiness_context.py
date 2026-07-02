from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import cofolding_readiness_runtime
from longevity_port_pipelines.stages import tp53_mdm2_cofolding_readiness_context as context_stage
from longevity_port_pipelines.stages import tp53_mdm2_generic_gated_contrast as gate8_stage
from longevity_port_pipelines.stages.cofolding_dry_run_manifest import (
    build_blocked_generic_cofolding_dry_run_manifest,
    build_generic_cofolding_dry_run_manifest,
)
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
    "recommended_next_action": pl.Utf8,
    "repair_decision": pl.Utf8,
    "repair_priority": pl.Utf8,
    "claim_policy": pl.Utf8,
    "repair_note": pl.Utf8,
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
        "recommended_next_action": "curate_or_fetch_tp53_mdm2_source_ortholog_rows",
        "repair_decision": "repair_before_claim",
        "repair_priority": "1",
        "claim_policy": "no_biological_claims_until_validation",
        "repair_note": "TP53/MDM2 coverage remains unresolved.",
    }
    row.update(overrides)
    return row


def gate8_summary(repair_decisions: pl.DataFrame | None = None) -> pl.DataFrame:
    if repair_decisions is None:
        repair_decisions = repair_rows([repair_row()])

    return gate8_stage.build_tp53_mdm2_generic_gated_contrast_blocked_summary(repair_decisions)


def test_tp53_mdm2_cofolding_context_schema_matches_generic_context_contract() -> None:
    context = context_stage.build_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8_summary(),
        repair_context=repair_rows([repair_row()]),
    )

    assert context.columns == cofolding_readiness_runtime.CONTEXT_COLUMNS


def test_tp53_mdm2_cofolding_context_records_partner_from_repair_decisions() -> None:
    context = context_stage.build_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8_summary(),
        repair_context=repair_rows([repair_row()]),
    )

    assert context.height == 1
    row = context.row(0, named=True)

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["lane_name"] == "tp53_mdm2_elephant"
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_tp53_chain"
    assert row["pdb_id"] == "1ycr"
    assert row["chain"] == "B"
    assert row["source_uniprot"] == "P04637"
    assert row["target_species"] == "elephant"
    assert row["partner_uniprot"] == "Q00987"
    assert row["partner_context_status"] == "partner_context_ready"
    assert row["source_provenance_status"] == "source_provenance_ready"
    assert row["cofolding_input_review_status"] == "dry_run_inputs_unreviewed"
    assert row["live_opt_in_status"] == "live_not_requested"


def test_tp53_mdm2_cofolding_context_marks_missing_partner_context() -> None:
    context = context_stage.build_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8_summary(),
        repair_context=repair_rows([repair_row(partner_uniprot="")]),
    )

    row = context.row(0, named=True)

    assert row["partner_uniprot"] == ""
    assert row["partner_context_status"] == "partner_context_missing"


def test_tp53_mdm2_cofolding_context_validates_gate8_columns() -> None:
    with pytest.raises(ValueError, match="gate8_summary is missing required columns"):
        context_stage.build_tp53_mdm2_cofolding_readiness_context(
            gate8_summary=gate8_summary().drop("long_lived_species"),
            repair_context=repair_rows([repair_row()]),
        )


def test_tp53_mdm2_cofolding_context_validates_repair_context_columns() -> None:
    with pytest.raises(ValueError, match="repair_context is missing required columns"):
        context_stage.build_tp53_mdm2_cofolding_readiness_context(
            gate8_summary=gate8_summary(),
            repair_context=repair_rows([repair_row()]).drop("partner_uniprot"),
        )


def test_tp53_mdm2_cofolding_context_rejects_duplicate_repair_context_keys() -> None:
    duplicate_context = repair_rows([repair_row(), repair_row(repair_note="duplicate")])

    with pytest.raises(ValueError, match="duplicate TP53/MDM2 cofolding key"):
        context_stage.build_tp53_mdm2_cofolding_readiness_context(
            gate8_summary=gate8_summary(),
            repair_context=duplicate_context,
        )


def test_tp53_mdm2_cofolding_context_feeds_generic_gate9_as_blocked() -> None:
    gate8 = gate8_summary()
    context = context_stage.build_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8,
        repair_context=repair_rows([repair_row()]),
        cofolding_input_review_status="dry_run_inputs_reviewed",
    )

    readiness = build_generic_cofolding_readiness(gate8, context)

    assert readiness.height == 1
    row = readiness.row(0, named=True)

    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["target_species"] == "elephant"
    assert row["partner_uniprot"] == "Q00987"
    assert row["contrast_status"] == "blocked_strict_panel_not_ready"
    assert row["cofolding_input_review_status"] == "dry_run_inputs_reviewed"
    assert row["cofolding_readiness_status"] == "blocked_contrast_not_ready"
    assert row["recommended_next_action"] == "resolve_gate8_contrast_status_before_cofolding"
    assert row["cofolding_dry_run_allowed"] is False
    assert row["live_cofolding_allowed"] is False
    assert row["controlled_claim_allowed"] is False


def test_tp53_mdm2_cofolding_context_keeps_manifest_blocked() -> None:
    gate8 = gate8_summary()
    context = context_stage.build_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8,
        repair_context=repair_rows([repair_row()]),
        cofolding_input_review_status="dry_run_inputs_reviewed",
    )
    readiness = build_generic_cofolding_readiness(gate8, context)

    eligible_manifest = build_generic_cofolding_dry_run_manifest(readiness)
    blocked_manifest = build_blocked_generic_cofolding_dry_run_manifest(readiness)

    assert eligible_manifest.is_empty()
    assert blocked_manifest.height == 1

    row = blocked_manifest.row(0, named=True)
    assert row["candidate_set"] == "tp53_mdm2_elephant"
    assert row["cofolding_plan_status"] == "blocked_gate8_not_ready"
    assert row["cofolding_dry_run_allowed"] is False
    assert row["live_cofolding_allowed"] is False
    assert row["controlled_claim_allowed"] is False


def test_tp53_mdm2_cofolding_context_status_counts() -> None:
    gate8 = gate8_summary(
        repair_rows(
            [
                repair_row(candidate_id="candidate_a", partner_uniprot="Q00987"),
                repair_row(candidate_id="candidate_b", partner_uniprot=""),
            ]
        )
    )
    context = context_stage.build_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8,
        repair_context=repair_rows(
            [
                repair_row(candidate_id="candidate_a", partner_uniprot="Q00987"),
                repair_row(candidate_id="candidate_b", partner_uniprot=""),
            ]
        ),
    )

    assert context_stage.tp53_mdm2_cofolding_context_status_counts(context) == {
        "partner_context_missing": 1,
        "partner_context_ready": 1,
    }


def test_write_tp53_mdm2_cofolding_context_writes_csv(tmp_path: Path) -> None:
    output = tmp_path / "tp53_mdm2_generic_cofolding_readiness_context.csv"

    context = context_stage.write_tp53_mdm2_cofolding_readiness_context(
        gate8_summary=gate8_summary(),
        repair_context=repair_rows([repair_row()]),
        output=output,
    )

    assert output.exists()
    written = pl.read_csv(output)

    assert written.height == context.height
    assert written.columns == cofolding_readiness_runtime.CONTEXT_COLUMNS
