from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

CONSERVATIVE_CLAIM_POLICY = "no_biological_claims_until_validation"
MAXIMUM_CLAIM_STATUS = "control_readiness"

READY_CONTROL_LAYER_STATUSES = frozenset(
    {
        "present",
        "ready",
        "available",
        "complete",
        "not_needed",
    }
)

READY_CONTROL_REPAIR_STATUSES = frozenset(
    {
        "not_needed",
        "repaired_for_planning",
        "accepted_for_planning_after_review",
    }
)

BLOCKED_CONTROL_REPAIR_STATUSES = frozenset(
    {
        "pending",
        "in_review",
        "excluded_from_controlled_claims",
        "deferred_pending_source",
        "needs_manual_review",
    }
)

READY_CONTROL_READINESS_STATUSES = frozenset(
    {
        "controls_ready",
        "controls_accepted_for_limited_dry_run",
    }
)

BLOCKED_CONTROL_READINESS_STATUSES = frozenset(
    {
        "missing_controls",
        "partial_controls_ready",
        "blocked_missing_shuffled_control",
        "blocked_missing_negatome",
        "blocked_missing_curated_negative_partner",
        "blocked_pending_control_repair",
        "excluded_from_controlled_claims",
        "deferred_pending_source",
        "needs_manual_review",
    }
)


@dataclass(frozen=True)
class ControlReadinessResult:
    control_readiness_status: str
    recommended_next_action: str
    contrast_dry_run_allowed: bool
    controlled_claim_allowed: bool
    claim_policy: str
    claim_status: str
    notes: str

    def as_dict(self) -> dict[str, object]:
        return {
            "control_readiness_status": self.control_readiness_status,
            "recommended_next_action": self.recommended_next_action,
            "contrast_dry_run_allowed": self.contrast_dry_run_allowed,
            "controlled_claim_allowed": self.controlled_claim_allowed,
            "claim_policy": self.claim_policy,
            "claim_status": self.claim_status,
            "notes": self.notes,
        }


def _normalise_status(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_ready_control_layer(status: str) -> bool:
    return status in READY_CONTROL_LAYER_STATUSES


def _all_control_layers_ready(
    *,
    shuffled_control_status: str,
    negatome_control_status: str,
    curated_negative_partner_status: str,
) -> bool:
    return (
        _is_ready_control_layer(shuffled_control_status)
        and _is_ready_control_layer(negatome_control_status)
        and _is_ready_control_layer(curated_negative_partner_status)
    )


def _any_control_layer_ready(
    *,
    shuffled_control_status: str,
    negatome_control_status: str,
    curated_negative_partner_status: str,
) -> bool:
    return (
        _is_ready_control_layer(shuffled_control_status)
        or _is_ready_control_layer(negatome_control_status)
        or _is_ready_control_layer(curated_negative_partner_status)
    )


def _infer_control_repair_status(
    *,
    shuffled_control_status: str,
    negatome_control_status: str,
    curated_negative_partner_status: str,
    control_repair_status: str,
) -> str:
    if control_repair_status:
        return control_repair_status

    if _all_control_layers_ready(
        shuffled_control_status=shuffled_control_status,
        negatome_control_status=negatome_control_status,
        curated_negative_partner_status=curated_negative_partner_status,
    ):
        return "not_needed"

    return "pending"


def _missing_control_status(
    *,
    shuffled_control_status: str,
    negatome_control_status: str,
    curated_negative_partner_status: str,
) -> str:
    if not _any_control_layer_ready(
        shuffled_control_status=shuffled_control_status,
        negatome_control_status=negatome_control_status,
        curated_negative_partner_status=curated_negative_partner_status,
    ):
        return "missing_controls"

    if not _is_ready_control_layer(shuffled_control_status):
        return "blocked_missing_shuffled_control"

    if not _is_ready_control_layer(negatome_control_status):
        return "blocked_missing_negatome"

    if not _is_ready_control_layer(curated_negative_partner_status):
        return "blocked_missing_curated_negative_partner"

    return "partial_controls_ready"


def _blocked_result_for_status(
    *,
    control_readiness_status: str,
    recommended_next_action: str,
    claim_policy: str,
    notes: str,
) -> ControlReadinessResult:
    return ControlReadinessResult(
        control_readiness_status=control_readiness_status,
        recommended_next_action=recommended_next_action,
        contrast_dry_run_allowed=False,
        controlled_claim_allowed=False,
        claim_policy=claim_policy,
        claim_status=MAXIMUM_CLAIM_STATUS,
        notes=notes,
    )


def control_readiness_for_statuses(
    *,
    shuffled_control_status: str,
    negatome_control_status: str,
    curated_negative_partner_status: str,
    control_repair_status: str = "",
    claim_policy: str = CONSERVATIVE_CLAIM_POLICY,
) -> ControlReadinessResult:
    resolved_repair_status = _infer_control_repair_status(
        shuffled_control_status=shuffled_control_status,
        negatome_control_status=negatome_control_status,
        curated_negative_partner_status=curated_negative_partner_status,
        control_repair_status=control_repair_status,
    )

    if (
        _all_control_layers_ready(
            shuffled_control_status=shuffled_control_status,
            negatome_control_status=negatome_control_status,
            curated_negative_partner_status=curated_negative_partner_status,
        )
        and resolved_repair_status in READY_CONTROL_REPAIR_STATUSES
    ):
        return ControlReadinessResult(
            control_readiness_status="controls_ready",
            recommended_next_action="run_contrast_gate_without_biological_claims",
            contrast_dry_run_allowed=True,
            controlled_claim_allowed=False,
            claim_policy=claim_policy,
            claim_status=MAXIMUM_CLAIM_STATUS,
            notes="Controls are usable for planning only; this is not a biological claim.",
        )

    if resolved_repair_status == "accepted_for_planning_after_review" and _is_ready_control_layer(
        shuffled_control_status
    ):
        return ControlReadinessResult(
            control_readiness_status="controls_accepted_for_limited_dry_run",
            recommended_next_action="run_limited_contrast_dry_run_with_control_caveat",
            contrast_dry_run_allowed=True,
            controlled_claim_allowed=False,
            claim_policy=claim_policy,
            claim_status=MAXIMUM_CLAIM_STATUS,
            notes=(
                "Controls are incomplete but accepted for limited dry-run planning after review; "
                "this is not a biological claim."
            ),
        )

    missing_status = _missing_control_status(
        shuffled_control_status=shuffled_control_status,
        negatome_control_status=negatome_control_status,
        curated_negative_partner_status=curated_negative_partner_status,
    )

    if missing_status == "missing_controls":
        return _blocked_result_for_status(
            control_readiness_status="missing_controls",
            recommended_next_action="add_shuffled_and_negatome_control_inputs",
            claim_policy=claim_policy,
            notes="Control inputs are missing and must be added before controlled contrast.",
        )

    if missing_status == "blocked_missing_shuffled_control":
        return _blocked_result_for_status(
            control_readiness_status="blocked_missing_shuffled_control",
            recommended_next_action="add_or_recompute_shuffled_mask_control",
            claim_policy=claim_policy,
            notes="Shuffled-mask control is missing.",
        )

    if missing_status == "blocked_missing_negatome":
        return _blocked_result_for_status(
            control_readiness_status="blocked_missing_negatome",
            recommended_next_action="curate_or_attach_negatome_control_partner",
            claim_policy=claim_policy,
            notes="NEGATOME-style control is missing.",
        )

    if missing_status == "blocked_missing_curated_negative_partner":
        return _blocked_result_for_status(
            control_readiness_status="blocked_missing_curated_negative_partner",
            recommended_next_action="curate_negative_partner_before_controlled_contrast",
            claim_policy=claim_policy,
            notes="Curated negative partner control is missing.",
        )

    if resolved_repair_status == "pending":
        return _blocked_result_for_status(
            control_readiness_status="blocked_pending_control_repair",
            recommended_next_action="resolve_control_repair_decision",
            claim_policy=claim_policy,
            notes="Control readiness is blocked until repair decision review is complete.",
        )

    if resolved_repair_status == "in_review":
        return _blocked_result_for_status(
            control_readiness_status="blocked_pending_control_repair",
            recommended_next_action="resolve_control_repair_decision",
            claim_policy=claim_policy,
            notes="Control readiness is still under review and must not enter contrast gates.",
        )

    if resolved_repair_status == "excluded_from_controlled_claims":
        return _blocked_result_for_status(
            control_readiness_status="excluded_from_controlled_claims",
            recommended_next_action="keep_row_excluded_from_controlled_claims",
            claim_policy=claim_policy,
            notes="Row is explicitly excluded from controlled claims.",
        )

    if resolved_repair_status == "deferred_pending_source":
        return _blocked_result_for_status(
            control_readiness_status="deferred_pending_source",
            recommended_next_action="defer_until_stronger_control_source_exists",
            claim_policy=claim_policy,
            notes="Row is deferred until stronger control provenance is available.",
        )

    if resolved_repair_status == "needs_manual_review":
        return _blocked_result_for_status(
            control_readiness_status="needs_manual_review",
            recommended_next_action="perform_manual_control_review",
            claim_policy=claim_policy,
            notes="Manual control review is required before planning.",
        )

    return _blocked_result_for_status(
        control_readiness_status="blocked_unknown_control_repair_status",
        recommended_next_action="review_unknown_control_repair_status",
        claim_policy=claim_policy,
        notes=f"Unknown control repair status: {resolved_repair_status}",
    )


def control_readiness_for_row(
    row: Mapping[str, object],
) -> ControlReadinessResult:
    return control_readiness_for_statuses(
        shuffled_control_status=_normalise_status(row.get("shuffled_control_status")),
        negatome_control_status=_normalise_status(row.get("negatome_control_status")),
        curated_negative_partner_status=_normalise_status(
            row.get("curated_negative_partner_status")
        ),
        control_repair_status=_normalise_status(row.get("control_repair_status")),
        claim_policy=_normalise_status(row.get("claim_policy")) or CONSERVATIVE_CLAIM_POLICY,
    )
