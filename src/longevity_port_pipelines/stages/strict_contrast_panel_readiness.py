from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

CONSERVATIVE_CLAIM_POLICY = "no_biological_claims_until_validation"
MAXIMUM_CLAIM_STATUS = "strict_panel_readiness"

MIN_LONG_LIVED_READY_SPECIES = 1
MIN_SHORT_LIVED_READY_SPECIES = 1
MIN_TOTAL_READY_SPECIES = 2

READY_COVERAGE_PREFLIGHT_STATUSES = frozenset({"coverage_preflight_ready"})
READY_CONTROL_READINESS_STATUSES = frozenset(
    {
        "controls_ready",
        "controls_accepted_for_limited_dry_run",
    }
)

LIMITED_CONTROL_READINESS_STATUSES = frozenset(
    {
        "controls_accepted_for_limited_dry_run",
    }
)

EXCLUDED_COVERAGE_PREFLIGHT_STATUSES = frozenset({"excluded_from_strict_panel"})
DEFERRED_COVERAGE_PREFLIGHT_STATUSES = frozenset(
    {
        "blocked_deferred_pending_source",
        "deferred_pending_source",
    }
)
MANUAL_REVIEW_COVERAGE_PREFLIGHT_STATUSES = frozenset(
    {
        "blocked_needs_manual_review",
        "needs_manual_review",
    }
)

READY_STRICT_PANEL_STATUSES = frozenset(
    {
        "strict_panel_ready",
        "strict_panel_accepted_for_limited_dry_run",
    }
)

BLOCKED_STRICT_PANEL_STATUSES = frozenset(
    {
        "blocked_missing_candidate_rows",
        "blocked_missing_coverage_preflight",
        "blocked_species_coverage_repair",
        "blocked_control_readiness",
        "insufficient_strict_panel_species",
        "insufficient_strict_long_lived_species",
        "insufficient_strict_short_lived_species",
        "excluded_from_strict_panel",
        "deferred_pending_source",
        "needs_manual_review",
    }
)


@dataclass(frozen=True)
class StrictPanelReadinessResult:
    strict_panel_status: str
    recommended_next_action: str
    contrast_dry_run_allowed: bool
    controlled_claim_allowed: bool
    claim_policy: str
    claim_status: str
    strict_panel_note: str

    def as_dict(self) -> dict[str, object]:
        return {
            "strict_panel_status": self.strict_panel_status,
            "recommended_next_action": self.recommended_next_action,
            "contrast_dry_run_allowed": self.contrast_dry_run_allowed,
            "controlled_claim_allowed": self.controlled_claim_allowed,
            "claim_policy": self.claim_policy,
            "claim_status": self.claim_status,
            "strict_panel_note": self.strict_panel_note,
        }


def _normalise_status(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalise_statuses(statuses: object | None) -> tuple[str, ...]:
    if statuses is None:
        return ()

    if isinstance(statuses, str):
        return tuple(status.strip() for status in statuses.split(",") if status.strip())

    if not isinstance(statuses, Iterable):
        status = _normalise_status(statuses)
        return (status,) if status else ()

    return tuple(status for raw_status in statuses if (status := _normalise_status(raw_status)))


def _as_int(value: object | None, default: int = 0) -> int:
    if value is None:
        return default

    if isinstance(value, int):
        return value

    if isinstance(value, float) and value.is_integer():
        return int(value)

    text = str(value).strip()
    if not text:
        return default

    return int(text)


def _result(
    *,
    strict_panel_status: str,
    recommended_next_action: str,
    contrast_dry_run_allowed: bool,
    claim_policy: str,
    strict_panel_note: str,
) -> StrictPanelReadinessResult:
    return StrictPanelReadinessResult(
        strict_panel_status=strict_panel_status,
        recommended_next_action=recommended_next_action,
        contrast_dry_run_allowed=contrast_dry_run_allowed,
        controlled_claim_allowed=False,
        claim_policy=claim_policy,
        claim_status=MAXIMUM_CLAIM_STATUS,
        strict_panel_note=strict_panel_note,
    )


def _blocked_result(
    *,
    strict_panel_status: str,
    recommended_next_action: str,
    claim_policy: str,
    strict_panel_note: str,
) -> StrictPanelReadinessResult:
    return _result(
        strict_panel_status=strict_panel_status,
        recommended_next_action=recommended_next_action,
        contrast_dry_run_allowed=False,
        claim_policy=claim_policy,
        strict_panel_note=strict_panel_note,
    )


def _all_coverage_ready(coverage_preflight_statuses: tuple[str, ...]) -> bool:
    return all(
        status in READY_COVERAGE_PREFLIGHT_STATUSES for status in coverage_preflight_statuses
    )


def _all_controls_ready_or_limited(
    control_readiness_statuses: tuple[str, ...],
) -> bool:
    return all(status in READY_CONTROL_READINESS_STATUSES for status in control_readiness_statuses)


def _has_limited_control_readiness(control_readiness_statuses: tuple[str, ...]) -> bool:
    return any(
        status in LIMITED_CONTROL_READINESS_STATUSES for status in control_readiness_statuses
    )


def _has_any_status(
    statuses: tuple[str, ...],
    status_set: frozenset[str],
) -> bool:
    return any(status in status_set for status in statuses)


def strict_panel_readiness_for_statuses(
    *,
    n_candidate_rows: int,
    n_strict_long_lived_ready: int,
    n_strict_short_lived_ready: int,
    coverage_preflight_statuses: object | None,
    control_readiness_statuses: object | None,
    claim_policy: str = CONSERVATIVE_CLAIM_POLICY,
) -> StrictPanelReadinessResult:
    coverage_statuses = _normalise_statuses(coverage_preflight_statuses)
    control_statuses = _normalise_statuses(control_readiness_statuses)

    if n_candidate_rows <= 0:
        return _blocked_result(
            strict_panel_status="blocked_missing_candidate_rows",
            recommended_next_action="add_or_rebuild_candidate_rows",
            claim_policy=claim_policy,
            strict_panel_note=(
                "No candidate rows are available for strict panel readiness; "
                "this is not a biological claim."
            ),
        )

    if not coverage_statuses:
        return _blocked_result(
            strict_panel_status="blocked_missing_coverage_preflight",
            recommended_next_action="run_coverage_preflight_before_strict_panel",
            claim_policy=claim_policy,
            strict_panel_note=(
                "Coverage preflight trace is missing; strict panel readiness cannot be evaluated."
            ),
        )

    if _has_any_status(coverage_statuses, EXCLUDED_COVERAGE_PREFLIGHT_STATUSES):
        return _blocked_result(
            strict_panel_status="excluded_from_strict_panel",
            recommended_next_action="keep_row_excluded_from_strict_panel",
            claim_policy=claim_policy,
            strict_panel_note="At least one row is explicitly excluded from strict panel planning.",
        )

    if _has_any_status(coverage_statuses, DEFERRED_COVERAGE_PREFLIGHT_STATUSES):
        return _blocked_result(
            strict_panel_status="deferred_pending_source",
            recommended_next_action=("defer_until_stronger_coverage_or_control_source_exists"),
            claim_policy=claim_policy,
            strict_panel_note=(
                "Strict panel readiness is deferred until stronger source evidence exists."
            ),
        )

    if _has_any_status(coverage_statuses, MANUAL_REVIEW_COVERAGE_PREFLIGHT_STATUSES):
        return _blocked_result(
            strict_panel_status="needs_manual_review",
            recommended_next_action="perform_manual_strict_panel_review",
            claim_policy=claim_policy,
            strict_panel_note="Manual strict panel review is required before planning.",
        )

    if not _all_coverage_ready(coverage_statuses):
        return _blocked_result(
            strict_panel_status="blocked_species_coverage_repair",
            recommended_next_action="resolve_coverage_repair_decisions",
            claim_policy=claim_policy,
            strict_panel_note=(
                "At least one coverage preflight status is not ready; strict "
                "contrast planning remains blocked."
            ),
        )

    if not control_statuses or not _all_controls_ready_or_limited(control_statuses):
        return _blocked_result(
            strict_panel_status="blocked_control_readiness",
            recommended_next_action="resolve_control_readiness_before_strict_panel",
            claim_policy=claim_policy,
            strict_panel_note=(
                "Control readiness is missing or blocked; strict contrast planning remains blocked."
            ),
        )

    total_ready = n_strict_long_lived_ready + n_strict_short_lived_ready
    if (
        total_ready < MIN_TOTAL_READY_SPECIES
        and n_strict_long_lived_ready < MIN_LONG_LIVED_READY_SPECIES
        and n_strict_short_lived_ready < MIN_SHORT_LIVED_READY_SPECIES
    ):
        return _blocked_result(
            strict_panel_status="insufficient_strict_panel_species",
            recommended_next_action="add_ready_long_lived_and_short_lived_species",
            claim_policy=claim_policy,
            strict_panel_note=(
                "Strict panel lacks enough ready long-lived and short-lived species."
            ),
        )

    if n_strict_long_lived_ready < MIN_LONG_LIVED_READY_SPECIES:
        return _blocked_result(
            strict_panel_status="insufficient_strict_long_lived_species",
            recommended_next_action="add_ready_long_lived_species",
            claim_policy=claim_policy,
            strict_panel_note="Strict panel lacks a ready long-lived species.",
        )

    if n_strict_short_lived_ready < MIN_SHORT_LIVED_READY_SPECIES:
        return _blocked_result(
            strict_panel_status="insufficient_strict_short_lived_species",
            recommended_next_action="add_ready_short_lived_control_species",
            claim_policy=claim_policy,
            strict_panel_note="Strict panel lacks a ready short-lived control species.",
        )

    if total_ready < MIN_TOTAL_READY_SPECIES:
        return _blocked_result(
            strict_panel_status="insufficient_strict_panel_species",
            recommended_next_action="add_ready_long_lived_and_short_lived_species",
            claim_policy=claim_policy,
            strict_panel_note="Strict panel lacks enough total ready species.",
        )

    if _has_limited_control_readiness(control_statuses):
        return _result(
            strict_panel_status="strict_panel_accepted_for_limited_dry_run",
            recommended_next_action="run_limited_strict_contrast_dry_run_with_caveat",
            contrast_dry_run_allowed=True,
            claim_policy=claim_policy,
            strict_panel_note=(
                "Strict panel is accepted for limited dry-run planning only; "
                "this is not a biological claim."
            ),
        )

    return _result(
        strict_panel_status="strict_panel_ready",
        recommended_next_action="run_strict_contrast_dry_run_without_biological_claims",
        contrast_dry_run_allowed=True,
        claim_policy=claim_policy,
        strict_panel_note=(
            "Strict panel is ready for technical contrast dry-run planning only; "
            "this is not a biological claim."
        ),
    )


def strict_panel_readiness_for_row(
    row: Mapping[str, object],
) -> StrictPanelReadinessResult:
    candidate_id = _normalise_status(row.get("candidate_id"))
    default_candidate_rows = 1 if candidate_id else 0

    coverage_statuses = row.get(
        "coverage_preflight_statuses",
        row.get("coverage_preflight_status"),
    )
    control_statuses = row.get(
        "control_readiness_statuses",
        row.get("control_readiness_status"),
    )

    return strict_panel_readiness_for_statuses(
        n_candidate_rows=_as_int(row.get("n_candidate_rows"), default_candidate_rows),
        n_strict_long_lived_ready=_as_int(
            row.get("n_strict_long_lived_ready", row.get("n_long_lived_ready"))
        ),
        n_strict_short_lived_ready=_as_int(
            row.get("n_strict_short_lived_ready", row.get("n_short_lived_ready"))
        ),
        coverage_preflight_statuses=coverage_statuses,
        control_readiness_statuses=control_statuses,
        claim_policy=_normalise_status(row.get("claim_policy")) or CONSERVATIVE_CLAIM_POLICY,
    )
