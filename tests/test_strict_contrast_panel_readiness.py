from pathlib import Path

import yaml

from longevity_port_pipelines.stages.strict_contrast_panel_readiness import (
    BLOCKED_STRICT_PANEL_STATUSES,
    READY_STRICT_PANEL_STATUSES,
    strict_panel_readiness_for_row,
    strict_panel_readiness_for_statuses,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/generic_strict_contrast_panel_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def ready_result(**overrides: object):
    inputs: dict[str, object] = {
        "n_candidate_rows": 2,
        "n_strict_long_lived_ready": 1,
        "n_strict_short_lived_ready": 1,
        "coverage_preflight_statuses": ["coverage_preflight_ready"],
        "control_readiness_statuses": ["controls_ready"],
    }
    inputs.update(overrides)
    return strict_panel_readiness_for_statuses(**inputs)


def test_strict_panel_helper_matches_schema_status_groups() -> None:
    schema = load_schema()

    assert set(schema["status_groups"]["dry_run_ready"]) == READY_STRICT_PANEL_STATUSES
    assert set(schema["status_groups"]["blocked"]) == BLOCKED_STRICT_PANEL_STATUSES
    assert set(schema["allowed_strict_panel_statuses"]) == (
        READY_STRICT_PANEL_STATUSES | BLOCKED_STRICT_PANEL_STATUSES
    )


def test_strict_panel_helper_marks_ready_panel() -> None:
    result = ready_result()

    assert result.strict_panel_status == "strict_panel_ready"
    assert result.recommended_next_action == "run_strict_contrast_dry_run_without_biological_claims"
    assert result.contrast_dry_run_allowed is True
    assert result.controlled_claim_allowed is False
    assert result.claim_policy == "no_biological_claims_until_validation"
    assert result.claim_status == "strict_panel_readiness"
    assert "not a biological claim" in result.strict_panel_note


def test_strict_panel_helper_allows_limited_dry_run_trace() -> None:
    result = ready_result(control_readiness_statuses=["controls_accepted_for_limited_dry_run"])

    assert result.strict_panel_status == "strict_panel_accepted_for_limited_dry_run"
    assert result.recommended_next_action == "run_limited_strict_contrast_dry_run_with_caveat"
    assert result.contrast_dry_run_allowed is True
    assert result.controlled_claim_allowed is False


def test_strict_panel_helper_blocks_missing_candidate_rows() -> None:
    result = ready_result(n_candidate_rows=0)

    assert result.strict_panel_status == "blocked_missing_candidate_rows"
    assert result.recommended_next_action == "add_or_rebuild_candidate_rows"
    assert result.contrast_dry_run_allowed is False


def test_strict_panel_helper_blocks_missing_coverage_preflight() -> None:
    result = ready_result(coverage_preflight_statuses=[])

    assert result.strict_panel_status == "blocked_missing_coverage_preflight"
    assert result.recommended_next_action == "run_coverage_preflight_before_strict_panel"


def test_strict_panel_helper_blocks_unresolved_coverage_repair() -> None:
    result = ready_result(
        coverage_preflight_statuses=[
            "coverage_preflight_ready",
            "blocked_pending_repair_review",
        ]
    )

    assert result.strict_panel_status == "blocked_species_coverage_repair"
    assert result.recommended_next_action == "resolve_coverage_repair_decisions"


def test_strict_panel_helper_blocks_control_readiness() -> None:
    result = ready_result(control_readiness_statuses=["blocked_missing_negatome"])

    assert result.strict_panel_status == "blocked_control_readiness"
    assert result.recommended_next_action == "resolve_control_readiness_before_strict_panel"


def test_strict_panel_helper_blocks_insufficient_panel_species() -> None:
    result = ready_result(
        n_strict_long_lived_ready=0,
        n_strict_short_lived_ready=0,
    )

    assert result.strict_panel_status == "insufficient_strict_panel_species"
    assert result.recommended_next_action == "add_ready_long_lived_and_short_lived_species"


def test_strict_panel_helper_blocks_insufficient_long_lived_species() -> None:
    result = ready_result(n_strict_long_lived_ready=0)

    assert result.strict_panel_status == "insufficient_strict_long_lived_species"
    assert result.recommended_next_action == "add_ready_long_lived_species"


def test_strict_panel_helper_blocks_insufficient_short_lived_species() -> None:
    result = ready_result(n_strict_short_lived_ready=0)

    assert result.strict_panel_status == "insufficient_strict_short_lived_species"
    assert result.recommended_next_action == "add_ready_short_lived_control_species"


def test_strict_panel_helper_blocks_excluded_rows() -> None:
    result = ready_result(coverage_preflight_statuses=["excluded_from_strict_panel"])

    assert result.strict_panel_status == "excluded_from_strict_panel"
    assert result.recommended_next_action == "keep_row_excluded_from_strict_panel"


def test_strict_panel_helper_blocks_deferred_rows() -> None:
    result = ready_result(coverage_preflight_statuses=["blocked_deferred_pending_source"])

    assert result.strict_panel_status == "deferred_pending_source"
    assert (
        result.recommended_next_action == "defer_until_stronger_coverage_or_control_source_exists"
    )


def test_strict_panel_helper_blocks_manual_review_rows() -> None:
    result = ready_result(coverage_preflight_statuses=["blocked_needs_manual_review"])

    assert result.strict_panel_status == "needs_manual_review"
    assert result.recommended_next_action == "perform_manual_strict_panel_review"


def test_strict_panel_helper_for_row_accepts_comma_separated_traces() -> None:
    result = strict_panel_readiness_for_row(
        {
            "candidate_id": "candidate_a",
            "n_strict_long_lived_ready": "1",
            "n_strict_short_lived_ready": "1",
            "coverage_preflight_statuses": "coverage_preflight_ready",
            "control_readiness_statuses": "controls_ready",
        }
    )

    assert result.strict_panel_status == "strict_panel_ready"


def test_strict_panel_helper_for_row_preserves_claim_policy() -> None:
    result = strict_panel_readiness_for_row(
        {
            "candidate_id": "candidate_a",
            "n_strict_long_lived_ready": 1,
            "n_strict_short_lived_ready": 1,
            "coverage_preflight_status": "coverage_preflight_ready",
            "control_readiness_status": "controls_ready",
            "claim_policy": "custom_no_claim_policy",
        }
    )

    assert result.claim_policy == "custom_no_claim_policy"


def test_strict_panel_helper_as_dict_uses_schema_field_names() -> None:
    result = ready_result()
    as_dict = result.as_dict()

    assert as_dict == {
        "strict_panel_status": "strict_panel_ready",
        "recommended_next_action": ("run_strict_contrast_dry_run_without_biological_claims"),
        "contrast_dry_run_allowed": True,
        "controlled_claim_allowed": False,
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "strict_panel_readiness",
        "strict_panel_note": result.strict_panel_note,
    }
