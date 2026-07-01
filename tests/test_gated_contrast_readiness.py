from pathlib import Path

import yaml

from longevity_port_pipelines.stages.gated_contrast_readiness import (
    BLOCKED_CONTRAST_STATUSES,
    READY_CONTRAST_STATUSES,
    gated_contrast_readiness_for_row,
    gated_contrast_readiness_for_statuses,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/generic_gated_contrast_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def ready_result(**overrides: object):
    inputs: dict[str, object] = {
        "n_enrichment_rows": 2,
        "n_long_lived_ready": 1,
        "n_short_lived_control_ready": 1,
        "strict_panel_statuses": ["strict_panel_ready"],
        "strict_panel_contrast_dry_run_allowed": True,
    }
    inputs.update(overrides)
    return gated_contrast_readiness_for_statuses(**inputs)


def test_gated_contrast_helper_matches_schema_status_groups() -> None:
    schema = load_schema()

    assert set(schema["status_groups"]["dry_run_outputs"]) == READY_CONTRAST_STATUSES
    assert set(schema["status_groups"]["blocked"]) == BLOCKED_CONTRAST_STATUSES
    assert set(schema["allowed_contrast_statuses"]) == (
        READY_CONTRAST_STATUSES | BLOCKED_CONTRAST_STATUSES
    )


def test_gated_contrast_helper_marks_ready_contrast() -> None:
    result = ready_result()

    assert result.contrast_status == "technical_contrast_ready"
    assert (
        result.recommended_next_action
        == "review_technical_contrast_checkpoint_without_biological_claims"
    )
    assert result.contrast_dry_run_allowed is True
    assert result.controlled_claim_allowed is False
    assert result.claim_policy == "no_biological_claims_until_validation"
    assert result.claim_status == "technical_contrast_checkpoint"
    assert "not a biological claim" in result.contrast_note


def test_gated_contrast_helper_allows_limited_dry_run_trace() -> None:
    result = ready_result(strict_panel_statuses=["strict_panel_accepted_for_limited_dry_run"])

    assert result.contrast_status == "technical_contrast_limited_dry_run"
    assert result.recommended_next_action == "review_limited_technical_contrast_with_caveat"
    assert result.contrast_dry_run_allowed is True
    assert result.controlled_claim_allowed is False


def test_gated_contrast_helper_blocks_missing_strict_panel_status() -> None:
    result = ready_result(strict_panel_statuses=[])

    assert result.contrast_status == "blocked_strict_panel_not_ready"
    assert result.recommended_next_action == "resolve_strict_panel_before_contrast"
    assert result.contrast_dry_run_allowed is False


def test_gated_contrast_helper_blocks_strict_panel_without_permission() -> None:
    result = ready_result(strict_panel_contrast_dry_run_allowed=False)

    assert result.contrast_status == "blocked_strict_panel_not_ready"
    assert result.recommended_next_action == "resolve_strict_panel_before_contrast"


def test_gated_contrast_helper_blocks_nonready_strict_panel_status() -> None:
    result = ready_result(strict_panel_statuses=["blocked_species_coverage_repair"])

    assert result.contrast_status == "blocked_strict_panel_not_ready"
    assert result.recommended_next_action == "resolve_strict_panel_before_contrast"


def test_gated_contrast_helper_blocks_missing_enrichment_rows() -> None:
    result = ready_result(n_enrichment_rows=0)

    assert result.contrast_status == "blocked_missing_enrichment_rows"
    assert result.recommended_next_action == "build_or_repair_enrichment_rows_before_contrast"


def test_gated_contrast_helper_blocks_missing_long_lived_rows() -> None:
    result = ready_result(n_long_lived_ready=0)

    assert result.contrast_status == "blocked_missing_long_lived_rows"
    assert result.recommended_next_action == "add_ready_long_lived_rows_before_contrast"


def test_gated_contrast_helper_blocks_missing_short_lived_controls() -> None:
    result = ready_result(n_short_lived_control_ready=0)

    assert result.contrast_status == "blocked_missing_short_lived_controls"
    assert result.recommended_next_action == "add_ready_short_lived_control_rows_before_contrast"


def test_gated_contrast_helper_blocks_missing_required_metrics() -> None:
    result = ready_result(metrics_ready=False)

    assert result.contrast_status == "blocked_missing_required_metrics"
    assert result.recommended_next_action == "compute_required_metrics_before_contrast"


def test_gated_contrast_helper_blocks_unmatched_candidate_rows() -> None:
    result = ready_result(candidate_keys_matched=False)

    assert result.contrast_status == "blocked_unmatched_candidate_rows"
    assert result.recommended_next_action == "align_strict_panel_and_metric_candidate_keys"


def test_gated_contrast_helper_for_row_accepts_comma_separated_traces() -> None:
    result = gated_contrast_readiness_for_row(
        {
            "candidate_id": "candidate_a",
            "n_long_lived_ready": "1",
            "n_short_lived_control_ready": "1",
            "strict_panel_statuses": "strict_panel_ready",
            "strict_panel_contrast_dry_run_allowed": "true",
        }
    )

    assert result.contrast_status == "technical_contrast_ready"


def test_gated_contrast_helper_for_row_preserves_claim_policy() -> None:
    result = gated_contrast_readiness_for_row(
        {
            "candidate_id": "candidate_a",
            "n_long_lived_ready": 1,
            "n_short_lived_control_ready": 1,
            "strict_panel_status": "strict_panel_ready",
            "contrast_dry_run_allowed": True,
            "claim_policy": "custom_no_claim_policy",
        }
    )

    assert result.claim_policy == "custom_no_claim_policy"


def test_gated_contrast_helper_as_dict_uses_schema_field_names() -> None:
    result = ready_result()
    as_dict = result.as_dict()

    assert as_dict == {
        "contrast_status": "technical_contrast_ready",
        "recommended_next_action": (
            "review_technical_contrast_checkpoint_without_biological_claims"
        ),
        "contrast_dry_run_allowed": True,
        "controlled_claim_allowed": False,
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "technical_contrast_checkpoint",
        "contrast_note": result.contrast_note,
    }
