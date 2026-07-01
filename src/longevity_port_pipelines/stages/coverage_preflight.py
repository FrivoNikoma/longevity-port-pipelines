from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

CONSERVATIVE_CLAIM_POLICY = "no_biological_claims_until_validation"
MAXIMUM_CLAIM_STATUS = "repair_worklist"

READY_REPAIR_STATUSES = frozenset(
    {
        "not_needed",
        "repaired_for_planning",
        "accepted_for_planning_after_review",
    }
)

BLOCKED_REPAIR_STATUSES = frozenset(
    {
        "pending",
        "in_review",
        "excluded_from_strict_panel",
        "deferred_pending_source",
        "needs_manual_review",
    }
)

READY_PROVENANCE_STATUSES = frozenset(
    {
        "standard_source_present",
        "curated_source_present",
    }
)


@dataclass(frozen=True)
class CoveragePreflightResult:
    coverage_preflight_status: str
    recommended_next_action: str
    strict_panel_allowed: bool
    contrast_dry_run_allowed: bool
    claim_policy: str
    claim_status: str
    notes: str

    def as_dict(self) -> dict[str, object]:
        return {
            "coverage_preflight_status": self.coverage_preflight_status,
            "recommended_next_action": self.recommended_next_action,
            "strict_panel_allowed": self.strict_panel_allowed,
            "contrast_dry_run_allowed": self.contrast_dry_run_allowed,
            "claim_policy": self.claim_policy,
            "claim_status": self.claim_status,
            "notes": self.notes,
        }


def _normalise_status(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _infer_repair_status(
    *,
    coverage_status: str,
    provenance_status: str,
    repair_status: str,
) -> str:
    if repair_status:
        return repair_status

    if coverage_status == "coverage_ready" and provenance_status in READY_PROVENANCE_STATUSES:
        return "not_needed"

    if coverage_status == "excluded_from_candidate_lane":
        return "excluded_from_strict_panel"

    if provenance_status in {"manual_review_required", "external_review_required"}:
        return "needs_manual_review"

    return "pending"


def coverage_preflight_for_statuses(
    *,
    coverage_status: str,
    provenance_status: str,
    repair_status: str = "",
    claim_policy: str = CONSERVATIVE_CLAIM_POLICY,
) -> CoveragePreflightResult:
    resolved_repair_status = _infer_repair_status(
        coverage_status=coverage_status,
        provenance_status=provenance_status,
        repair_status=repair_status,
    )

    if resolved_repair_status in READY_REPAIR_STATUSES:
        return CoveragePreflightResult(
            coverage_preflight_status="coverage_preflight_ready",
            recommended_next_action="run_strict_panel_or_contrast_gate",
            strict_panel_allowed=True,
            contrast_dry_run_allowed=True,
            claim_policy=claim_policy,
            claim_status=MAXIMUM_CLAIM_STATUS,
            notes="Coverage is usable for planning only; this is not a biological claim.",
        )

    if resolved_repair_status == "pending":
        return CoveragePreflightResult(
            coverage_preflight_status="blocked_pending_repair_review",
            recommended_next_action="complete_ortholog_repair_decision_review",
            strict_panel_allowed=False,
            contrast_dry_run_allowed=False,
            claim_policy=claim_policy,
            claim_status=MAXIMUM_CLAIM_STATUS,
            notes="Coverage is blocked until repair decision review is complete.",
        )

    if resolved_repair_status == "in_review":
        return CoveragePreflightResult(
            coverage_preflight_status="blocked_in_review",
            recommended_next_action="finish_manual_provenance_review",
            strict_panel_allowed=False,
            contrast_dry_run_allowed=False,
            claim_policy=claim_policy,
            claim_status=MAXIMUM_CLAIM_STATUS,
            notes="Coverage is still under review and must not enter contrast gates.",
        )

    if resolved_repair_status == "excluded_from_strict_panel":
        return CoveragePreflightResult(
            coverage_preflight_status="excluded_from_strict_panel",
            recommended_next_action="keep_row_out_of_strict_panel",
            strict_panel_allowed=False,
            contrast_dry_run_allowed=False,
            claim_policy=claim_policy,
            claim_status=MAXIMUM_CLAIM_STATUS,
            notes="Row is explicitly excluded from strict panel and contrast planning.",
        )

    if resolved_repair_status == "deferred_pending_source":
        return CoveragePreflightResult(
            coverage_preflight_status="blocked_deferred_pending_source",
            recommended_next_action="wait_for_stronger_ortholog_source",
            strict_panel_allowed=False,
            contrast_dry_run_allowed=False,
            claim_policy=claim_policy,
            claim_status=MAXIMUM_CLAIM_STATUS,
            notes="Row is deferred until stronger ortholog provenance is available.",
        )

    if resolved_repair_status == "needs_manual_review":
        return CoveragePreflightResult(
            coverage_preflight_status="blocked_needs_manual_review",
            recommended_next_action="request_external_manual_sequence_review",
            strict_panel_allowed=False,
            contrast_dry_run_allowed=False,
            claim_policy=claim_policy,
            claim_status=MAXIMUM_CLAIM_STATUS,
            notes="Manual sequence or accession review is required before planning.",
        )

    return CoveragePreflightResult(
        coverage_preflight_status="blocked_unknown_repair_status",
        recommended_next_action="review_unknown_repair_status",
        strict_panel_allowed=False,
        contrast_dry_run_allowed=False,
        claim_policy=claim_policy,
        claim_status=MAXIMUM_CLAIM_STATUS,
        notes=f"Unknown repair status: {resolved_repair_status}",
    )


def coverage_preflight_for_row(
    row: Mapping[str, object],
) -> CoveragePreflightResult:
    return coverage_preflight_for_statuses(
        coverage_status=_normalise_status(row.get("coverage_status")),
        provenance_status=_normalise_status(row.get("provenance_status")),
        repair_status=_normalise_status(row.get("repair_status")),
        claim_policy=_normalise_status(row.get("claim_policy")) or CONSERVATIVE_CLAIM_POLICY,
    )
