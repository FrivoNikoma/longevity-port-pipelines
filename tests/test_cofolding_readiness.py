from longevity_port_pipelines.stages import cofolding_readiness as readiness


def ready_kwargs() -> dict[str, object]:
    return {
        "candidate_id": "candidate_a",
        "pdb_id": "4xhu",
        "chain": "receptor",
        "source_uniprot": "P09874",
        "target_species": "naked_mole_rat",
        "partner_uniprot": "Q9UNS1",
        "contrast_status": "technical_contrast_ready",
        "contrast_dry_run_allowed": True,
        "contrast_requires_review": False,
        "robustness_status": "technical_multispecies_contrast",
        "partner_context_status": "partner_context_ready",
        "source_provenance_status": "source_provenance_ready",
        "cofolding_input_review_status": "dry_run_inputs_reviewed",
        "live_opt_in_status": "live_not_requested",
        "claim_policy": "no_biological_claims_until_validation",
        "controlled_claim_allowed": False,
    }


def test_cofolding_readiness_ready_when_gate8_and_context_ready() -> None:
    result = readiness.cofolding_readiness_for_statuses(**ready_kwargs())

    assert result.cofolding_readiness_status == "cofolding_dry_run_ready"
    assert result.recommended_next_action == (
        "prepare_cofolding_dry_run_manifest_without_live_calls"
    )
    assert result.cofolding_dry_run_allowed is True
    assert result.live_cofolding_allowed is False
    assert result.controlled_claim_allowed is False
    assert result.claim_status == "cofolding_readiness"


def test_cofolding_readiness_limited_when_reviewed_contrast_has_caveat() -> None:
    kwargs = ready_kwargs()
    kwargs["contrast_requires_review"] = True
    kwargs["robustness_status"] = "technical_single_baseline_review"

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "cofolding_limited_dry_run_review"
    assert result.cofolding_dry_run_allowed is True
    assert result.live_cofolding_allowed is False
    assert "limited review" in result.cofolding_readiness_note


def test_cofolding_readiness_blocks_unreviewed_contrast_caveat() -> None:
    kwargs = ready_kwargs()
    kwargs["contrast_requires_review"] = True
    kwargs["cofolding_input_review_status"] = "dry_run_inputs_unreviewed"

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_contrast_requires_review"
    assert result.cofolding_dry_run_allowed is False
    assert result.recommended_next_action == "review_gate8_robustness_before_cofolding"


def test_cofolding_readiness_blocks_when_gate8_not_ready() -> None:
    kwargs = ready_kwargs()
    kwargs["contrast_status"] = "blocked_missing_short_lived_controls"
    kwargs["contrast_dry_run_allowed"] = False

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_contrast_not_ready"
    assert result.cofolding_dry_run_allowed is False
    assert result.live_cofolding_allowed is False


def test_cofolding_readiness_blocks_missing_candidate_context() -> None:
    kwargs = ready_kwargs()
    kwargs["candidate_id"] = ""

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_missing_candidate_context"
    assert result.recommended_next_action == "add_candidate_context_before_cofolding"


def test_cofolding_readiness_blocks_missing_species_context() -> None:
    kwargs = ready_kwargs()
    kwargs["target_species"] = ""

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_missing_species_context"
    assert result.recommended_next_action == "add_target_species_context_before_cofolding"


def test_cofolding_readiness_blocks_missing_partner_context() -> None:
    kwargs = ready_kwargs()
    kwargs["partner_context_status"] = "missing_partner_context"

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_missing_partner_context"
    assert result.recommended_next_action == "record_partner_context_before_cofolding"


def test_cofolding_readiness_blocks_missing_source_provenance() -> None:
    kwargs = ready_kwargs()
    kwargs["source_provenance_status"] = "missing_source_provenance"

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_missing_source_provenance"
    assert result.recommended_next_action == "record_source_provenance_before_cofolding"


def test_cofolding_readiness_blocks_unreviewed_inputs() -> None:
    kwargs = ready_kwargs()
    kwargs["cofolding_input_review_status"] = "dry_run_inputs_unreviewed"

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_unreviewed_dry_run_inputs"
    assert result.recommended_next_action == "review_cofolding_dry_run_inputs_before_manifest"


def test_cofolding_readiness_blocks_nonconservative_claim_policy() -> None:
    kwargs = ready_kwargs()
    kwargs["claim_policy"] = "uncontrolled_claim"

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_claim_policy"
    assert result.cofolding_dry_run_allowed is False


def test_cofolding_readiness_blocks_controlled_claim_allowed() -> None:
    kwargs = ready_kwargs()
    kwargs["controlled_claim_allowed"] = True

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "blocked_claim_policy"
    assert result.controlled_claim_allowed is False


def test_cofolding_readiness_never_allows_live_cofolding_request() -> None:
    kwargs = ready_kwargs()
    kwargs["live_opt_in_status"] = "live_requested_requires_separate_review"

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "needs_manual_review"
    assert result.live_cofolding_allowed is False
    assert "separate explicit review" in result.cofolding_readiness_note


def test_cofolding_readiness_can_exclude_rows() -> None:
    kwargs = ready_kwargs()
    kwargs["excluded_from_cofolding"] = True

    result = readiness.cofolding_readiness_for_statuses(**kwargs)

    assert result.cofolding_readiness_status == "excluded_from_cofolding"
    assert result.recommended_next_action == "keep_row_excluded_from_cofolding"


def test_cofolding_readiness_for_row_uses_long_lived_species_as_target() -> None:
    row = ready_kwargs()
    row.pop("target_species")
    row["long_lived_species"] = "bowhead_whale"

    result = readiness.cofolding_readiness_for_row(row)

    assert result.cofolding_readiness_status == "cofolding_dry_run_ready"


def test_cofolding_readiness_result_as_dict_records_no_live_claims() -> None:
    result = readiness.cofolding_readiness_for_statuses(**ready_kwargs())

    assert result.as_dict() == {
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
