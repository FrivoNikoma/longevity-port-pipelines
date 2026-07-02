from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

CONSERVATIVE_CLAIM_POLICY = "no_biological_claims_until_validation"
MAXIMUM_CLAIM_STATUS = "cofolding_readiness"

READY_GATE8_CONTRAST_STATUSES = frozenset(
    {
        "technical_contrast_ready",
        "technical_contrast_limited_dry_run",
    }
)
LIMITED_GATE8_CONTRAST_STATUSES = frozenset(
    {
        "technical_contrast_limited_dry_run",
    }
)

FULLY_ROBUST_CONTRAST_STATUS = "technical_multispecies_contrast"
READY_PARTNER_CONTEXT_STATUS = "partner_context_ready"
READY_SOURCE_PROVENANCE_STATUS = "source_provenance_ready"
READY_COFOLDING_INPUT_REVIEW_STATUS = "dry_run_inputs_reviewed"
LIVE_NOT_REQUESTED_STATUS = "live_not_requested"


@dataclass(frozen=True)
class CofoldingReadinessResult:
    cofolding_readiness_status: str
    recommended_next_action: str
    cofolding_dry_run_allowed: bool
    live_cofolding_allowed: bool
    controlled_claim_allowed: bool
    claim_policy: str
    claim_status: str
    cofolding_readiness_note: str

    def as_dict(self) -> dict[str, object]:
        return {
            "cofolding_readiness_status": self.cofolding_readiness_status,
            "recommended_next_action": self.recommended_next_action,
            "cofolding_dry_run_allowed": self.cofolding_dry_run_allowed,
            "live_cofolding_allowed": self.live_cofolding_allowed,
            "controlled_claim_allowed": self.controlled_claim_allowed,
            "claim_policy": self.claim_policy,
            "claim_status": self.claim_status,
            "cofolding_readiness_note": self.cofolding_readiness_note,
        }


def _normalise_status(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


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
    cofolding_readiness_status: str,
    recommended_next_action: str,
    cofolding_dry_run_allowed: bool,
    claim_policy: str,
    cofolding_readiness_note: str,
) -> CofoldingReadinessResult:
    return CofoldingReadinessResult(
        cofolding_readiness_status=cofolding_readiness_status,
        recommended_next_action=recommended_next_action,
        cofolding_dry_run_allowed=cofolding_dry_run_allowed,
        live_cofolding_allowed=False,
        controlled_claim_allowed=False,
        claim_policy=claim_policy,
        claim_status=MAXIMUM_CLAIM_STATUS,
        cofolding_readiness_note=cofolding_readiness_note,
    )


def _blocked_result(
    *,
    cofolding_readiness_status: str,
    recommended_next_action: str,
    claim_policy: str,
    cofolding_readiness_note: str,
) -> CofoldingReadinessResult:
    return _result(
        cofolding_readiness_status=cofolding_readiness_status,
        recommended_next_action=recommended_next_action,
        cofolding_dry_run_allowed=False,
        claim_policy=claim_policy,
        cofolding_readiness_note=cofolding_readiness_note,
    )


def _required_candidate_context_present(
    *,
    candidate_id: object | None,
    pdb_id: object | None,
    chain: object | None,
    source_uniprot: object | None,
) -> bool:
    return all(
        _normalise_status(value)
        for value in [
            candidate_id,
            pdb_id,
            chain,
            source_uniprot,
        ]
    )


def _contrast_requires_limited_review(
    *,
    contrast_status: str,
    contrast_requires_review: object | None,
    robustness_status: str,
) -> bool:
    if _as_bool(contrast_requires_review):
        return True

    if contrast_status in LIMITED_GATE8_CONTRAST_STATUSES:
        return True

    return robustness_status != FULLY_ROBUST_CONTRAST_STATUS


def cofolding_readiness_for_statuses(
    *,
    candidate_id: object | None = None,
    pdb_id: object | None = None,
    chain: object | None = None,
    source_uniprot: object | None = None,
    target_species: object | None = None,
    partner_uniprot: object | None = None,
    contrast_status: object | None = None,
    contrast_dry_run_allowed: object | None = None,
    contrast_requires_review: object | None = None,
    robustness_status: object | None = None,
    partner_context_status: object | None = None,
    source_provenance_status: object | None = None,
    cofolding_input_review_status: object | None = None,
    live_opt_in_status: object | None = LIVE_NOT_REQUESTED_STATUS,
    claim_policy: str = CONSERVATIVE_CLAIM_POLICY,
    controlled_claim_allowed: object | None = False,
    excluded_from_cofolding: object | None = False,
) -> CofoldingReadinessResult:
    claim_policy_text = _normalise_status(claim_policy) or CONSERVATIVE_CLAIM_POLICY

    if _as_bool(excluded_from_cofolding):
        return _blocked_result(
            cofolding_readiness_status="excluded_from_cofolding",
            recommended_next_action="keep_row_excluded_from_cofolding",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Row is explicitly excluded from cofolding readiness planning."
            ),
        )

    if claim_policy_text != CONSERVATIVE_CLAIM_POLICY or _as_bool(controlled_claim_allowed):
        return _blocked_result(
            cofolding_readiness_status="blocked_claim_policy",
            recommended_next_action="restore_conservative_claim_policy_before_cofolding",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Cofolding readiness requires conservative no-claims policy and "
                "controlled_claim_allowed=false."
            ),
        )

    if not _required_candidate_context_present(
        candidate_id=candidate_id,
        pdb_id=pdb_id,
        chain=chain,
        source_uniprot=source_uniprot,
    ):
        return _blocked_result(
            cofolding_readiness_status="blocked_missing_candidate_context",
            recommended_next_action="add_candidate_context_before_cofolding",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Candidate id, structure id, chain, and source UniProt are required "
                "before cofolding readiness planning."
            ),
        )

    if not _normalise_status(target_species):
        return _blocked_result(
            cofolding_readiness_status="blocked_missing_species_context",
            recommended_next_action="add_target_species_context_before_cofolding",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Target species context is required before cofolding readiness planning."
            ),
        )

    contrast_status_text = _normalise_status(contrast_status)
    if contrast_status_text not in READY_GATE8_CONTRAST_STATUSES or not _as_bool(
        contrast_dry_run_allowed
    ):
        return _blocked_result(
            cofolding_readiness_status="blocked_contrast_not_ready",
            recommended_next_action="resolve_gate8_contrast_status_before_cofolding",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Gate 8 technical contrast is not ready for cofolding dry-run planning."
            ),
        )

    if not _normalise_status(partner_uniprot) or (
        _normalise_status(partner_context_status) != READY_PARTNER_CONTEXT_STATUS
    ):
        return _blocked_result(
            cofolding_readiness_status="blocked_missing_partner_context",
            recommended_next_action="record_partner_context_before_cofolding",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Partner UniProt and reviewed partner context are required before "
                "cofolding readiness planning."
            ),
        )

    if _normalise_status(source_provenance_status) != READY_SOURCE_PROVENANCE_STATUS:
        return _blocked_result(
            cofolding_readiness_status="blocked_missing_source_provenance",
            recommended_next_action="record_source_provenance_before_cofolding",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Source provenance must be ready before cofolding readiness planning."
            ),
        )

    live_status = _normalise_status(live_opt_in_status) or LIVE_NOT_REQUESTED_STATUS
    if live_status != LIVE_NOT_REQUESTED_STATUS:
        return _blocked_result(
            cofolding_readiness_status="needs_manual_review",
            recommended_next_action="perform_manual_cofolding_readiness_review",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Live cofolding intent requires a separate explicit review step; "
                "the generic readiness helper never permits live calls."
            ),
        )

    robustness_status_text = _normalise_status(robustness_status)
    requires_limited_review = _contrast_requires_limited_review(
        contrast_status=contrast_status_text,
        contrast_requires_review=contrast_requires_review,
        robustness_status=robustness_status_text,
    )

    input_review_status = _normalise_status(cofolding_input_review_status)
    if input_review_status != READY_COFOLDING_INPUT_REVIEW_STATUS:
        if requires_limited_review:
            return _blocked_result(
                cofolding_readiness_status="blocked_contrast_requires_review",
                recommended_next_action="review_gate8_robustness_before_cofolding",
                claim_policy=claim_policy_text,
                cofolding_readiness_note=(
                    "Gate 8 contrast or robustness requires review before cofolding "
                    "dry-run planning."
                ),
            )

        return _blocked_result(
            cofolding_readiness_status="blocked_unreviewed_dry_run_inputs",
            recommended_next_action="review_cofolding_dry_run_inputs_before_manifest",
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Cofolding dry-run inputs must be reviewed before manifest planning."
            ),
        )

    if requires_limited_review:
        return _result(
            cofolding_readiness_status="cofolding_limited_dry_run_review",
            recommended_next_action="review_limited_cofolding_dry_run_context_before_manifest",
            cofolding_dry_run_allowed=True,
            claim_policy=claim_policy_text,
            cofolding_readiness_note=(
                "Cofolding dry-run planning is allowed only as a limited review "
                "checkpoint; no live calls or biological claims are permitted."
            ),
        )

    return _result(
        cofolding_readiness_status="cofolding_dry_run_ready",
        recommended_next_action="prepare_cofolding_dry_run_manifest_without_live_calls",
        cofolding_dry_run_allowed=True,
        claim_policy=claim_policy_text,
        cofolding_readiness_note=(
            "Row is ready for cofolding dry-run planning only; no live calls or "
            "biological claims are permitted."
        ),
    )


def cofolding_readiness_for_row(
    row: Mapping[str, object],
) -> CofoldingReadinessResult:
    target_species = row.get("target_species", row.get("long_lived_species"))

    return cofolding_readiness_for_statuses(
        candidate_id=row.get("candidate_id"),
        pdb_id=row.get("pdb_id"),
        chain=row.get("chain"),
        source_uniprot=row.get("source_uniprot"),
        target_species=target_species,
        partner_uniprot=row.get("partner_uniprot"),
        contrast_status=row.get("contrast_status"),
        contrast_dry_run_allowed=row.get("contrast_dry_run_allowed"),
        contrast_requires_review=row.get("contrast_requires_review"),
        robustness_status=row.get("robustness_status"),
        partner_context_status=row.get("partner_context_status"),
        source_provenance_status=row.get("source_provenance_status"),
        cofolding_input_review_status=row.get("cofolding_input_review_status"),
        live_opt_in_status=row.get("live_opt_in_status", LIVE_NOT_REQUESTED_STATUS),
        claim_policy=_normalise_status(row.get("claim_policy")) or CONSERVATIVE_CLAIM_POLICY,
        controlled_claim_allowed=row.get("controlled_claim_allowed", False),
        excluded_from_cofolding=row.get("excluded_from_cofolding", False),
    )
