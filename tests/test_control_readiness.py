from pathlib import Path

import yaml

from longevity_port_pipelines.stages.control_readiness import (
    BLOCKED_CONTROL_READINESS_STATUSES,
    BLOCKED_CONTROL_REPAIR_STATUSES,
    CONSERVATIVE_CLAIM_POLICY,
    MAXIMUM_CLAIM_STATUS,
    READY_CONTROL_READINESS_STATUSES,
    READY_CONTROL_REPAIR_STATUSES,
    control_readiness_for_row,
    control_readiness_for_statuses,
)

ROOT = Path(__file__).resolve().parents[1]

CONTROL_READINESS_SCHEMA_PATH = ROOT / "data/config/generic_control_readiness_schema.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_control_readiness_helper_matches_schema_ready_statuses() -> None:
    schema = load_yaml(CONTROL_READINESS_SCHEMA_PATH)

    assert set(schema["status_groups"]["dry_run_ready"]) == READY_CONTROL_READINESS_STATUSES


def test_control_readiness_helper_matches_schema_blocked_statuses() -> None:
    schema = load_yaml(CONTROL_READINESS_SCHEMA_PATH)

    assert set(schema["status_groups"]["blocked"]) == BLOCKED_CONTROL_READINESS_STATUSES


def test_control_readiness_helper_matches_schema_repair_statuses() -> None:
    schema = load_yaml(CONTROL_READINESS_SCHEMA_PATH)

    assert set(schema["allowed_control_repair_statuses"]) == (
        READY_CONTROL_REPAIR_STATUSES | BLOCKED_CONTROL_REPAIR_STATUSES
    )


def test_control_readiness_marks_complete_controls_ready() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="present",
        negatome_control_status="present",
        curated_negative_partner_status="present",
    )

    assert result.control_readiness_status == "controls_ready"
    assert result.recommended_next_action == "run_contrast_gate_without_biological_claims"
    assert result.contrast_dry_run_allowed is True
    assert result.controlled_claim_allowed is False
    assert result.claim_status == MAXIMUM_CLAIM_STATUS


def test_control_readiness_blocks_missing_controls() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="",
        negatome_control_status="",
        curated_negative_partner_status="",
    )

    assert result.control_readiness_status == "missing_controls"
    assert result.recommended_next_action == "add_shuffled_and_negatome_control_inputs"
    assert result.contrast_dry_run_allowed is False
    assert result.controlled_claim_allowed is False


def test_control_readiness_blocks_missing_shuffled_control_first() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="missing",
        negatome_control_status="present",
        curated_negative_partner_status="present",
    )

    assert result.control_readiness_status == "blocked_missing_shuffled_control"
    assert result.recommended_next_action == "add_or_recompute_shuffled_mask_control"


def test_control_readiness_blocks_missing_negatome_control() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="present",
        negatome_control_status="missing",
        curated_negative_partner_status="present",
    )

    assert result.control_readiness_status == "blocked_missing_negatome"
    assert result.recommended_next_action == "curate_or_attach_negatome_control_partner"


def test_control_readiness_blocks_missing_curated_negative_partner() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="present",
        negatome_control_status="present",
        curated_negative_partner_status="missing",
    )

    assert result.control_readiness_status == "blocked_missing_curated_negative_partner"
    assert result.recommended_next_action == "curate_negative_partner_before_controlled_contrast"


def test_control_readiness_allows_limited_dry_run_after_review() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="present",
        negatome_control_status="missing",
        curated_negative_partner_status="missing",
        control_repair_status="accepted_for_planning_after_review",
    )

    assert result.control_readiness_status == "controls_accepted_for_limited_dry_run"
    assert result.recommended_next_action == "run_limited_contrast_dry_run_with_control_caveat"
    assert result.contrast_dry_run_allowed is True
    assert result.controlled_claim_allowed is False


def test_control_readiness_blocks_explicit_pending_repair_review() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="present",
        negatome_control_status="present",
        curated_negative_partner_status="present",
        control_repair_status="pending",
    )

    assert result.control_readiness_status == "blocked_pending_control_repair"
    assert result.recommended_next_action == "resolve_control_repair_decision"
    assert result.contrast_dry_run_allowed is False


def test_control_readiness_blocks_excluded_rows() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="present",
        negatome_control_status="present",
        curated_negative_partner_status="present",
        control_repair_status="excluded_from_controlled_claims",
    )

    assert result.control_readiness_status == "excluded_from_controlled_claims"
    assert result.recommended_next_action == "keep_row_excluded_from_controlled_claims"
    assert result.controlled_claim_allowed is False


def test_control_readiness_blocks_unknown_repair_status() -> None:
    result = control_readiness_for_statuses(
        shuffled_control_status="present",
        negatome_control_status="present",
        curated_negative_partner_status="present",
        control_repair_status="unexpected_status",
    )

    assert result.control_readiness_status == "blocked_unknown_control_repair_status"
    assert result.recommended_next_action == "review_unknown_control_repair_status"
    assert result.contrast_dry_run_allowed is False


def test_control_readiness_for_row_uses_conservative_default_claim_policy() -> None:
    result = control_readiness_for_row(
        {
            "shuffled_control_status": "present",
            "negatome_control_status": "present",
            "curated_negative_partner_status": "present",
        }
    )

    assert result.claim_policy == CONSERVATIVE_CLAIM_POLICY
    assert result.as_dict()["claim_policy"] == CONSERVATIVE_CLAIM_POLICY


def test_control_readiness_for_row_preserves_explicit_claim_policy() -> None:
    result = control_readiness_for_row(
        {
            "shuffled_control_status": "present",
            "negatome_control_status": "present",
            "curated_negative_partner_status": "present",
            "claim_policy": "no_biological_claims_until_validation",
        }
    )

    assert result.claim_policy == "no_biological_claims_until_validation"


def test_control_readiness_for_row_records_no_biological_claim() -> None:
    result = control_readiness_for_row(
        {
            "shuffled_control_status": "present",
            "negatome_control_status": "present",
            "curated_negative_partner_status": "present",
        }
    )

    assert result.controlled_claim_allowed is False
    assert "not a biological claim" in result.notes
