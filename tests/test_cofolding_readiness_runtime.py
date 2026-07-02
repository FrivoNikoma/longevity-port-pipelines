from pathlib import Path

import polars as pl
import yaml

from longevity_port_pipelines.stages.cofolding_readiness_runtime import (
    COFOLDING_READINESS_SCHEMA,
    build_generic_cofolding_readiness,
    cofolding_readiness_status_counts,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/generic_cofolding_readiness_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


GATE8_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "long_lived_species": pl.Utf8,
    "short_lived_species": pl.Utf8,
    "short_lived_control_count": pl.Int64,
    "long_enrichment_ratio": pl.Float64,
    "short_enrichment_ratio": pl.Float64,
    "enrichment_delta": pl.Float64,
    "enrichment_log2_ratio": pl.Float64,
    "contrast_class": pl.Utf8,
    "contrast_priority": pl.Int64,
    "has_multiple_short_lived_controls": pl.Boolean,
    "has_multiple_long_lived_species": pl.Boolean,
    "short_lived_baseline_is_single_species": pl.Boolean,
    "contrast_class_is_directional": pl.Boolean,
    "contrast_requires_review": pl.Boolean,
    "robustness_status": pl.Utf8,
    "robustness_note": pl.Utf8,
    "contrast_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "contrast_dry_run_allowed": pl.Boolean,
    "controlled_claim_allowed": pl.Boolean,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "contrast_note": pl.Utf8,
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


def gate8_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=GATE8_SCHEMA)


def context_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=CONTEXT_SCHEMA)


def gate8_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_set": "demo_set",
        "lane_name": "demo_lane",
        "candidate_id": "candidate_a",
        "pdb_id": "4xhu",
        "chain": "receptor",
        "source_uniprot": "P09874",
        "priority": "1",
        "long_lived_species": "naked_mole_rat",
        "short_lived_species": "mouse,rat",
        "short_lived_control_count": 2,
        "long_enrichment_ratio": 1.8,
        "short_enrichment_ratio": 1.0,
        "enrichment_delta": 0.8,
        "enrichment_log2_ratio": 0.8479969,
        "contrast_class": "long_lived_specific_interface_divergence",
        "contrast_priority": 1,
        "has_multiple_short_lived_controls": True,
        "has_multiple_long_lived_species": True,
        "short_lived_baseline_is_single_species": False,
        "contrast_class_is_directional": True,
        "contrast_requires_review": False,
        "robustness_status": "technical_multispecies_contrast",
        "robustness_note": (
            "Contrast has multiple short-lived controls and multiple long-lived species represented."
        ),
        "contrast_status": "technical_contrast_ready",
        "recommended_next_action": "review_technical_contrast_checkpoint_without_biological_claims",
        "contrast_dry_run_allowed": True,
        "controlled_claim_allowed": False,
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "technical_contrast_checkpoint",
        "contrast_note": "Gated contrast is ready as a technical checkpoint only.",
    }
    row.update(overrides)
    return row


def context_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_set": "demo_set",
        "lane_name": "demo_lane",
        "candidate_id": "candidate_a",
        "pdb_id": "4xhu",
        "chain": "receptor",
        "source_uniprot": "P09874",
        "target_species": "naked_mole_rat",
        "partner_uniprot": "Q9UNS1",
        "partner_context_status": "partner_context_ready",
        "source_provenance_status": "source_provenance_ready",
        "cofolding_input_review_status": "dry_run_inputs_reviewed",
        "live_opt_in_status": "live_not_requested",
    }
    row.update(overrides)
    return row


def test_cofolding_readiness_runtime_schema_matches_yaml_required_outputs() -> None:
    schema = load_schema()

    assert list(COFOLDING_READINESS_SCHEMA) == schema["required_output_fields"]


def test_build_generic_cofolding_readiness_marks_ready_row() -> None:
    summary = build_generic_cofolding_readiness(
        gate8_rows([gate8_row()]),
        context_rows([context_row()]),
    )

    assert summary.height == 1
    row = summary.row(0, named=True)

    assert row["candidate_set"] == "demo_set"
    assert row["candidate_id"] == "candidate_a"
    assert row["target_species"] == "naked_mole_rat"
    assert row["partner_uniprot"] == "Q9UNS1"
    assert row["contrast_status"] == "technical_contrast_ready"
    assert row["robustness_status"] == "technical_multispecies_contrast"
    assert row["cofolding_input_review_status"] == "dry_run_inputs_reviewed"
    assert row["cofolding_readiness_status"] == "cofolding_dry_run_ready"
    assert row["recommended_next_action"] == "prepare_cofolding_dry_run_manifest_without_live_calls"
    assert row["cofolding_dry_run_allowed"] is True
    assert row["live_cofolding_allowed"] is False
    assert row["controlled_claim_allowed"] is False
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "cofolding_readiness"
    assert "no live calls" in row["cofolding_readiness_note"]


def test_build_generic_cofolding_readiness_allows_limited_review_after_input_review() -> None:
    summary = build_generic_cofolding_readiness(
        gate8_rows(
            [
                gate8_row(
                    contrast_status="technical_contrast_limited_dry_run",
                    contrast_requires_review=True,
                    robustness_status="technical_limited_dry_run_review",
                )
            ]
        ),
        context_rows([context_row()]),
    )

    row = summary.row(0, named=True)

    assert row["cofolding_readiness_status"] == "cofolding_limited_dry_run_review"
    assert row["cofolding_dry_run_allowed"] is True
    assert row["live_cofolding_allowed"] is False
    assert "limited review" in row["cofolding_readiness_note"]


def test_build_generic_cofolding_readiness_blocks_gate8_not_ready() -> None:
    summary = build_generic_cofolding_readiness(
        gate8_rows(
            [
                gate8_row(
                    contrast_status="blocked_missing_short_lived_controls",
                    contrast_dry_run_allowed=False,
                    contrast_requires_review=True,
                    robustness_status="blocked_before_robustness_review",
                )
            ]
        ),
        context_rows([context_row()]),
    )

    row = summary.row(0, named=True)

    assert row["cofolding_readiness_status"] == "blocked_contrast_not_ready"
    assert row["cofolding_dry_run_allowed"] is False
    assert row["live_cofolding_allowed"] is False
    assert row["recommended_next_action"] == "resolve_gate8_contrast_status_before_cofolding"


def test_build_generic_cofolding_readiness_blocks_missing_context_join() -> None:
    summary = build_generic_cofolding_readiness(
        gate8_rows([gate8_row()]),
        context_rows([]),
    )

    row = summary.row(0, named=True)

    assert row["partner_uniprot"] == ""
    assert row["cofolding_readiness_status"] == "blocked_missing_partner_context"
    assert row["cofolding_dry_run_allowed"] is False


def test_build_generic_cofolding_readiness_blocks_unreviewed_inputs() -> None:
    summary = build_generic_cofolding_readiness(
        gate8_rows([gate8_row()]),
        context_rows([context_row(cofolding_input_review_status="dry_run_inputs_unreviewed")]),
    )

    row = summary.row(0, named=True)

    assert row["cofolding_input_review_status"] == "dry_run_inputs_unreviewed"
    assert row["cofolding_readiness_status"] == "blocked_unreviewed_dry_run_inputs"
    assert row["recommended_next_action"] == "review_cofolding_dry_run_inputs_before_manifest"


def test_build_generic_cofolding_readiness_routes_live_intent_to_manual_review() -> None:
    summary = build_generic_cofolding_readiness(
        gate8_rows([gate8_row()]),
        context_rows([context_row(live_opt_in_status="live_requested_requires_separate_review")]),
    )

    row = summary.row(0, named=True)

    assert row["cofolding_readiness_status"] == "needs_manual_review"
    assert row["cofolding_dry_run_allowed"] is False
    assert row["live_cofolding_allowed"] is False
    assert "separate explicit review" in row["cofolding_readiness_note"]


def test_build_generic_cofolding_readiness_blocks_nonconservative_claim_policy() -> None:
    summary = build_generic_cofolding_readiness(
        gate8_rows([gate8_row(claim_policy="uncontrolled_claim")]),
        context_rows([context_row()]),
    )

    row = summary.row(0, named=True)

    assert row["cofolding_readiness_status"] == "blocked_claim_policy"
    assert row["cofolding_dry_run_allowed"] is False
    assert row["controlled_claim_allowed"] is False


def test_build_generic_cofolding_readiness_status_counts() -> None:
    summary = build_generic_cofolding_readiness(
        gate8_rows(
            [
                gate8_row(candidate_id="candidate_a", long_lived_species="naked_mole_rat"),
                gate8_row(
                    candidate_id="candidate_b",
                    long_lived_species="bowhead_whale",
                    contrast_status="blocked_missing_short_lived_controls",
                    contrast_dry_run_allowed=False,
                    contrast_requires_review=True,
                    robustness_status="blocked_before_robustness_review",
                ),
            ]
        ),
        context_rows(
            [
                context_row(candidate_id="candidate_a", target_species="naked_mole_rat"),
                context_row(candidate_id="candidate_b", target_species="bowhead_whale"),
            ]
        ),
    )

    assert cofolding_readiness_status_counts(summary) == {
        "blocked_contrast_not_ready": 1,
        "cofolding_dry_run_ready": 1,
    }
