import polars as pl
import pytest

from longevity_port_pipelines.stages.cofolding_dry_run_manifest import (
    BLOCKED_CLAIM_POLICY,
    BLOCKED_COFOLDING_READINESS,
    BLOCKED_GATE8_NOT_READY,
    BLOCKED_MISSING_CONTEXT,
    BLOCKED_UNREVIEWED_INPUTS,
    COFOLDING_DRY_RUN_MANIFEST_SCHEMA,
    ELIGIBLE_PLAN_STATUS,
    EXCLUDED_FROM_COFOLDING,
    REVIEW_LIMITED_CONTEXT,
    REVIEW_MANUAL_CONTEXT,
    build_blocked_generic_cofolding_dry_run_manifest,
    build_generic_cofolding_dry_run_manifest,
    cofolding_plan_status_counts,
)

READINESS_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "target_species": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "contrast_class": pl.Utf8,
    "contrast_status": pl.Utf8,
    "robustness_status": pl.Utf8,
    "cofolding_input_review_status": pl.Utf8,
    "cofolding_readiness_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "cofolding_dry_run_allowed": pl.Boolean,
    "live_cofolding_allowed": pl.Boolean,
    "controlled_claim_allowed": pl.Boolean,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "cofolding_readiness_note": pl.Utf8,
}


def readiness_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=READINESS_SCHEMA)


def readiness_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_set": "demo_set",
        "lane_name": "demo_lane",
        "candidate_id": "candidate_a",
        "pdb_id": "4xhu",
        "chain": "receptor",
        "source_uniprot": "P09874",
        "priority": "1",
        "target_species": "naked_mole_rat",
        "partner_uniprot": "Q9UNS1",
        "contrast_class": "long_lived_specific_interface_divergence",
        "contrast_status": "technical_contrast_ready",
        "robustness_status": "technical_multispecies_contrast",
        "cofolding_input_review_status": "dry_run_inputs_reviewed",
        "cofolding_readiness_status": "cofolding_dry_run_ready",
        "recommended_next_action": "prepare_cofolding_dry_run_manifest_without_live_calls",
        "cofolding_dry_run_allowed": True,
        "live_cofolding_allowed": False,
        "controlled_claim_allowed": False,
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "cofolding_readiness",
        "cofolding_readiness_note": (
            "Row is ready for cofolding dry-run planning only; no live calls or "
            "biological claims are permitted."
        ),
    }
    row.update(overrides)
    return row


def test_generic_cofolding_dry_run_manifest_has_expected_schema() -> None:
    manifest = build_generic_cofolding_dry_run_manifest(
        readiness_rows([readiness_row()]),
    )

    assert list(COFOLDING_DRY_RUN_MANIFEST_SCHEMA) == manifest.columns


def test_generic_cofolding_dry_run_manifest_includes_only_ready_rows() -> None:
    manifest = build_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(candidate_id="candidate_a"),
                readiness_row(
                    candidate_id="candidate_b",
                    cofolding_readiness_status="blocked_contrast_not_ready",
                    cofolding_dry_run_allowed=False,
                ),
            ]
        )
    )

    assert manifest.height == 1
    row = manifest.row(0, named=True)

    assert row["candidate_id"] == "candidate_a"
    assert row["cofolding_plan_status"] == ELIGIBLE_PLAN_STATUS
    assert row["cofolding_dry_run_allowed"] is True
    assert row["live_cofolding_allowed"] is False
    assert row["controlled_claim_allowed"] is False
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "cofolding_readiness"
    assert "not a Boltz input" in row["cofolding_plan_note"]


def test_generic_cofolding_dry_run_manifest_rejects_corrupted_live_allowed_row() -> None:
    manifest = build_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    live_cofolding_allowed=True,
                )
            ]
        )
    )
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    live_cofolding_allowed=True,
                )
            ]
        )
    )

    assert manifest.is_empty()
    assert blocked.height == 1
    assert blocked.row(0, named=True)["cofolding_plan_status"] == BLOCKED_COFOLDING_READINESS


def test_generic_cofolding_dry_run_manifest_rejects_unreviewed_inputs() -> None:
    manifest = build_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    cofolding_input_review_status="dry_run_inputs_unreviewed",
                    cofolding_readiness_status="blocked_unreviewed_dry_run_inputs",
                    cofolding_dry_run_allowed=False,
                )
            ]
        )
    )
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    cofolding_input_review_status="dry_run_inputs_unreviewed",
                    cofolding_readiness_status="blocked_unreviewed_dry_run_inputs",
                    cofolding_dry_run_allowed=False,
                )
            ]
        )
    )

    assert manifest.is_empty()
    row = blocked.row(0, named=True)
    assert row["cofolding_plan_status"] == BLOCKED_UNREVIEWED_INPUTS
    assert row["recommended_next_action"] == "prepare_cofolding_dry_run_manifest_without_live_calls"


def test_blocked_generic_cofolding_dry_run_manifest_classifies_gate8_block() -> None:
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    cofolding_readiness_status="blocked_contrast_not_ready",
                    cofolding_dry_run_allowed=False,
                    recommended_next_action="resolve_gate8_contrast_status_before_cofolding",
                )
            ]
        )
    )

    row = blocked.row(0, named=True)

    assert row["cofolding_plan_status"] == BLOCKED_GATE8_NOT_READY
    assert row["cofolding_dry_run_allowed"] is False
    assert "blocked_contrast_not_ready" in row["cofolding_plan_note"]


def test_blocked_generic_cofolding_dry_run_manifest_classifies_missing_context() -> None:
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    partner_uniprot="",
                    cofolding_readiness_status="blocked_missing_partner_context",
                    cofolding_dry_run_allowed=False,
                    recommended_next_action="record_partner_context_before_cofolding",
                )
            ]
        )
    )

    row = blocked.row(0, named=True)

    assert row["cofolding_plan_status"] == BLOCKED_MISSING_CONTEXT
    assert row["partner_uniprot"] == ""


def test_blocked_generic_cofolding_dry_run_manifest_classifies_limited_review() -> None:
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    cofolding_readiness_status="cofolding_limited_dry_run_review",
                    recommended_next_action="review_limited_cofolding_dry_run_context_before_manifest",
                )
            ]
        )
    )

    row = blocked.row(0, named=True)

    assert row["cofolding_plan_status"] == REVIEW_LIMITED_CONTEXT
    assert row["cofolding_dry_run_allowed"] is True
    assert row["live_cofolding_allowed"] is False


def test_blocked_generic_cofolding_dry_run_manifest_classifies_manual_review() -> None:
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    cofolding_readiness_status="needs_manual_review",
                    cofolding_dry_run_allowed=False,
                    recommended_next_action="perform_manual_cofolding_readiness_review",
                )
            ]
        )
    )

    row = blocked.row(0, named=True)

    assert row["cofolding_plan_status"] == REVIEW_MANUAL_CONTEXT
    assert row["live_cofolding_allowed"] is False


def test_blocked_generic_cofolding_dry_run_manifest_classifies_claim_policy_block() -> None:
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    cofolding_readiness_status="blocked_claim_policy",
                    cofolding_dry_run_allowed=False,
                    claim_policy="uncontrolled_claim",
                    recommended_next_action="restore_conservative_claim_policy_before_cofolding",
                )
            ]
        )
    )

    row = blocked.row(0, named=True)

    assert row["cofolding_plan_status"] == BLOCKED_CLAIM_POLICY
    assert row["controlled_claim_allowed"] is False


def test_blocked_generic_cofolding_dry_run_manifest_classifies_excluded_rows() -> None:
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    cofolding_readiness_status="excluded_from_cofolding",
                    cofolding_dry_run_allowed=False,
                    recommended_next_action="keep_row_excluded_from_cofolding",
                )
            ]
        )
    )

    row = blocked.row(0, named=True)

    assert row["cofolding_plan_status"] == EXCLUDED_FROM_COFOLDING


def test_generic_cofolding_dry_run_manifest_counts_statuses() -> None:
    blocked = build_blocked_generic_cofolding_dry_run_manifest(
        readiness_rows(
            [
                readiness_row(
                    candidate_id="candidate_b",
                    cofolding_readiness_status="blocked_contrast_not_ready",
                    cofolding_dry_run_allowed=False,
                ),
                readiness_row(
                    candidate_id="candidate_c",
                    partner_uniprot="",
                    cofolding_readiness_status="blocked_missing_partner_context",
                    cofolding_dry_run_allowed=False,
                ),
            ]
        )
    )

    assert cofolding_plan_status_counts(blocked) == {
        BLOCKED_GATE8_NOT_READY: 1,
        BLOCKED_MISSING_CONTEXT: 1,
    }


def test_generic_cofolding_dry_run_manifest_validates_required_columns() -> None:
    with pytest.raises(ValueError, match="readiness_summary is missing required columns"):
        build_generic_cofolding_dry_run_manifest(pl.DataFrame({"candidate_id": ["candidate_a"]}))
