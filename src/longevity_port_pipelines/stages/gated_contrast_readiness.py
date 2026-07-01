from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

CONSERVATIVE_CLAIM_POLICY = "no_biological_claims_until_validation"
MAXIMUM_CLAIM_STATUS = "technical_contrast_checkpoint"

MIN_LONG_LIVED_READY_SPECIES = 1
MIN_SHORT_LIVED_CONTROL_SPECIES = 1
MIN_TOTAL_SPECIES_GROUPS = 2

READY_STRICT_PANEL_STATUSES = frozenset(
    {
        "strict_panel_ready",
        "strict_panel_accepted_for_limited_dry_run",
    }
)

LIMITED_STRICT_PANEL_STATUSES = frozenset(
    {
        "strict_panel_accepted_for_limited_dry_run",
    }
)

READY_CONTRAST_STATUSES = frozenset(
    {
        "technical_contrast_ready",
        "technical_contrast_limited_dry_run",
    }
)

BLOCKED_CONTRAST_STATUSES = frozenset(
    {
        "blocked_strict_panel_not_ready",
        "blocked_missing_enrichment_rows",
        "blocked_missing_long_lived_rows",
        "blocked_missing_short_lived_controls",
        "blocked_missing_required_metrics",
        "blocked_unmatched_candidate_rows",
        "excluded_from_gated_contrast",
        "needs_manual_review",
    }
)


@dataclass(frozen=True)
class GatedContrastReadinessResult:
    contrast_status: str
    recommended_next_action: str
    contrast_dry_run_allowed: bool
    controlled_claim_allowed: bool
    claim_policy: str
    claim_status: str
    contrast_note: str

    def as_dict(self) -> dict[str, object]:
        return {
            "contrast_status": self.contrast_status,
            "recommended_next_action": self.recommended_next_action,
            "contrast_dry_run_allowed": self.contrast_dry_run_allowed,
            "controlled_claim_allowed": self.controlled_claim_allowed,
            "claim_policy": self.claim_policy,
            "claim_status": self.claim_status,
            "contrast_note": self.contrast_note,
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


def _as_bool(value: object | None, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False

    return default


def _result(
    *,
    contrast_status: str,
    recommended_next_action: str,
    contrast_dry_run_allowed: bool,
    claim_policy: str,
    contrast_note: str,
) -> GatedContrastReadinessResult:
    return GatedContrastReadinessResult(
        contrast_status=contrast_status,
        recommended_next_action=recommended_next_action,
        contrast_dry_run_allowed=contrast_dry_run_allowed,
        controlled_claim_allowed=False,
        claim_policy=claim_policy,
        claim_status=MAXIMUM_CLAIM_STATUS,
        contrast_note=contrast_note,
    )


def _blocked_result(
    *,
    contrast_status: str,
    recommended_next_action: str,
    claim_policy: str,
    contrast_note: str,
) -> GatedContrastReadinessResult:
    return _result(
        contrast_status=contrast_status,
        recommended_next_action=recommended_next_action,
        contrast_dry_run_allowed=False,
        claim_policy=claim_policy,
        contrast_note=contrast_note,
    )


def _all_strict_panel_ready(strict_panel_statuses: tuple[str, ...]) -> bool:
    return all(status in READY_STRICT_PANEL_STATUSES for status in strict_panel_statuses)


def _has_limited_strict_panel(strict_panel_statuses: tuple[str, ...]) -> bool:
    return any(status in LIMITED_STRICT_PANEL_STATUSES for status in strict_panel_statuses)


def gated_contrast_readiness_for_statuses(
    *,
    n_enrichment_rows: int,
    n_long_lived_ready: int,
    n_short_lived_control_ready: int,
    strict_panel_statuses: object | None,
    strict_panel_contrast_dry_run_allowed: object | None,
    metrics_ready: object | None = True,
    candidate_keys_matched: object | None = True,
    claim_policy: str = CONSERVATIVE_CLAIM_POLICY,
) -> GatedContrastReadinessResult:
    strict_statuses = _normalise_statuses(strict_panel_statuses)
    strict_panel_allowed = _as_bool(strict_panel_contrast_dry_run_allowed)

    if (
        not strict_statuses
        or not strict_panel_allowed
        or not _all_strict_panel_ready(strict_statuses)
    ):
        return _blocked_result(
            contrast_status="blocked_strict_panel_not_ready",
            recommended_next_action="resolve_strict_panel_before_contrast",
            claim_policy=claim_policy,
            contrast_note=(
                "Strict panel dry-run permission is missing or blocked; gated contrast cannot run."
            ),
        )

    if n_enrichment_rows <= 0:
        return _blocked_result(
            contrast_status="blocked_missing_enrichment_rows",
            recommended_next_action="build_or_repair_enrichment_rows_before_contrast",
            claim_policy=claim_policy,
            contrast_note="No enrichment rows are available for gated technical contrast.",
        )

    if n_long_lived_ready < MIN_LONG_LIVED_READY_SPECIES:
        return _blocked_result(
            contrast_status="blocked_missing_long_lived_rows",
            recommended_next_action="add_ready_long_lived_rows_before_contrast",
            claim_policy=claim_policy,
            contrast_note="Gated contrast lacks ready long-lived rows.",
        )

    if n_short_lived_control_ready < MIN_SHORT_LIVED_CONTROL_SPECIES:
        return _blocked_result(
            contrast_status="blocked_missing_short_lived_controls",
            recommended_next_action="add_ready_short_lived_control_rows_before_contrast",
            claim_policy=claim_policy,
            contrast_note="Gated contrast lacks ready short-lived control rows.",
        )

    if (n_long_lived_ready > 0) + (n_short_lived_control_ready > 0) < MIN_TOTAL_SPECIES_GROUPS:
        return _blocked_result(
            contrast_status="blocked_missing_short_lived_controls",
            recommended_next_action="add_ready_short_lived_control_rows_before_contrast",
            claim_policy=claim_policy,
            contrast_note="Gated contrast lacks long-lived-vs-short-lived group contrast.",
        )

    if not _as_bool(metrics_ready, default=True):
        return _blocked_result(
            contrast_status="blocked_missing_required_metrics",
            recommended_next_action="compute_required_metrics_before_contrast",
            claim_policy=claim_policy,
            contrast_note="Required gated contrast metric columns are missing or incomplete.",
        )

    if not _as_bool(candidate_keys_matched, default=True):
        return _blocked_result(
            contrast_status="blocked_unmatched_candidate_rows",
            recommended_next_action="align_strict_panel_and_metric_candidate_keys",
            claim_policy=claim_policy,
            contrast_note="Strict panel and metric candidate keys are not aligned.",
        )

    if _has_limited_strict_panel(strict_statuses):
        return _result(
            contrast_status="technical_contrast_limited_dry_run",
            recommended_next_action="review_limited_technical_contrast_with_caveat",
            contrast_dry_run_allowed=True,
            claim_policy=claim_policy,
            contrast_note=(
                "Gated contrast is accepted for limited technical dry-run review only; "
                "this is not a biological claim."
            ),
        )

    return _result(
        contrast_status="technical_contrast_ready",
        recommended_next_action="review_technical_contrast_checkpoint_without_biological_claims",
        contrast_dry_run_allowed=True,
        claim_policy=claim_policy,
        contrast_note=(
            "Gated contrast is ready as a technical checkpoint only; "
            "this is not a biological claim."
        ),
    )


def gated_contrast_readiness_for_row(
    row: Mapping[str, object],
) -> GatedContrastReadinessResult:
    candidate_id = _normalise_status(row.get("candidate_id"))
    default_enrichment_rows = 1 if candidate_id else 0

    strict_panel_statuses = row.get(
        "strict_panel_statuses",
        row.get("strict_panel_status"),
    )
    strict_panel_allowed = row.get(
        "strict_panel_contrast_dry_run_allowed",
        row.get("contrast_dry_run_allowed"),
    )

    return gated_contrast_readiness_for_statuses(
        n_enrichment_rows=_as_int(row.get("n_enrichment_rows"), default_enrichment_rows),
        n_long_lived_ready=_as_int(
            row.get("n_long_lived_ready", row.get("n_strict_long_lived_ready"))
        ),
        n_short_lived_control_ready=_as_int(
            row.get(
                "n_short_lived_control_ready",
                row.get("n_strict_short_lived_ready"),
            )
        ),
        strict_panel_statuses=strict_panel_statuses,
        strict_panel_contrast_dry_run_allowed=strict_panel_allowed,
        metrics_ready=row.get("metrics_ready", True),
        candidate_keys_matched=row.get("candidate_keys_matched", True),
        claim_policy=_normalise_status(row.get("claim_policy")) or CONSERVATIVE_CLAIM_POLICY,
    )
