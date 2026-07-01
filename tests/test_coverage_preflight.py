from pathlib import Path

import yaml

from longevity_port_pipelines.stages.coverage_preflight import (
    BLOCKED_REPAIR_STATUSES,
    CONSERVATIVE_CLAIM_POLICY,
    MAXIMUM_CLAIM_STATUS,
    READY_REPAIR_STATUSES,
    coverage_preflight_for_row,
    coverage_preflight_for_statuses,
)

ROOT = Path(__file__).resolve().parents[1]

ORTHOLOG_REPAIR_SCHEMA_PATH = ROOT / "data/config/ortholog_repair_decision_schema.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_coverage_preflight_allows_schema_ready_repair_statuses() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)

    assert set(schema["strict_panel_effects"]["may_enter_strict_panel"]) == READY_REPAIR_STATUSES
    assert (
        set(schema["contrast_gate_effects"]["may_enter_contrast_dry_run"]) == READY_REPAIR_STATUSES
    )

    for repair_status in READY_REPAIR_STATUSES:
        result = coverage_preflight_for_statuses(
            coverage_status="coverage_ready",
            provenance_status="standard_source_present",
            repair_status=repair_status,
        )

        assert result.strict_panel_allowed is True
        assert result.contrast_dry_run_allowed is True
        assert result.coverage_preflight_status == "coverage_preflight_ready"
        assert result.claim_status == MAXIMUM_CLAIM_STATUS


def test_coverage_preflight_blocks_schema_blocked_repair_statuses() -> None:
    schema = load_yaml(ORTHOLOG_REPAIR_SCHEMA_PATH)

    assert (
        set(schema["strict_panel_effects"]["must_not_enter_strict_panel"])
        == BLOCKED_REPAIR_STATUSES
    )
    assert (
        set(schema["contrast_gate_effects"]["blocked_contrast_coverage"]) == BLOCKED_REPAIR_STATUSES
    )

    for repair_status in BLOCKED_REPAIR_STATUSES:
        result = coverage_preflight_for_statuses(
            coverage_status="missing_source_ortholog",
            provenance_status="unresolved",
            repair_status=repair_status,
        )

        assert result.strict_panel_allowed is False
        assert result.contrast_dry_run_allowed is False
        assert result.claim_status == MAXIMUM_CLAIM_STATUS


def test_coverage_preflight_infers_ready_when_coverage_and_provenance_are_ready() -> None:
    result = coverage_preflight_for_statuses(
        coverage_status="coverage_ready",
        provenance_status="standard_source_present",
    )

    assert result.coverage_preflight_status == "coverage_preflight_ready"
    assert result.recommended_next_action == "run_strict_panel_or_contrast_gate"


def test_coverage_preflight_infers_pending_when_repair_status_is_missing() -> None:
    result = coverage_preflight_for_statuses(
        coverage_status="missing_source_ortholog",
        provenance_status="unresolved",
    )

    assert result.coverage_preflight_status == "blocked_pending_repair_review"
    assert result.recommended_next_action == "complete_ortholog_repair_decision_review"
    assert result.strict_panel_allowed is False


def test_coverage_preflight_for_row_uses_conservative_default_claim_policy() -> None:
    result = coverage_preflight_for_row(
        {
            "coverage_status": "coverage_ready",
            "provenance_status": "curated_source_present",
            "repair_status": "accepted_for_planning_after_review",
        }
    )

    assert result.claim_policy == CONSERVATIVE_CLAIM_POLICY
    assert result.as_dict()["claim_policy"] == CONSERVATIVE_CLAIM_POLICY


def test_coverage_preflight_for_row_preserves_explicit_claim_policy() -> None:
    result = coverage_preflight_for_row(
        {
            "coverage_status": "coverage_ready",
            "provenance_status": "curated_source_present",
            "repair_status": "repaired_for_planning",
            "claim_policy": "no_biological_claims_until_validation",
        }
    )

    assert result.claim_policy == "no_biological_claims_until_validation"


def test_coverage_preflight_blocks_unknown_repair_status() -> None:
    result = coverage_preflight_for_statuses(
        coverage_status="coverage_ready",
        provenance_status="standard_source_present",
        repair_status="unexpected_status",
    )

    assert result.coverage_preflight_status == "blocked_unknown_repair_status"
    assert result.recommended_next_action == "review_unknown_repair_status"
    assert result.strict_panel_allowed is False
    assert result.contrast_dry_run_allowed is False
