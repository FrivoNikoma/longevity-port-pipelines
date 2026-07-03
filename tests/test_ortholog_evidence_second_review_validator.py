from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages import ortholog_evidence_second_review as second_review

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_second_review_schema.yaml"


def load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def committed_rows() -> pl.DataFrame:
    rows = second_review.read_second_review_rows()
    assert rows.height == 1
    return rows


def test_committed_second_review_queue_is_valid() -> None:
    rows = committed_rows()

    second_review.validate_second_review_rows(rows)

    row = rows.row(0, named=True)
    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["evidence_source_accession"] == "G3SX30"
    assert row["second_review_status"] == "pending_second_review"
    assert row["second_review_decision"] == "pending"
    assert row["downstream_block_status_after_second_review"] == (second_review.BLOCKED_GATE4_GATE5)
    assert row["claim_status_after_second_review"] == (second_review.REPAIR_WORKLIST_CLAIM_STATUS)


def test_validator_required_columns_match_schema() -> None:
    schema = load_schema()
    required_fields = set(schema["required_row_identity_fields"]) | set(
        schema["required_second_review_fields"]
    )

    assert required_fields == set(second_review.REQUIRED_COLUMNS)


def test_validator_allowed_statuses_and_decisions_match_schema() -> None:
    schema = load_schema()

    assert set(schema["allowed_intake_outcomes_before_second_review"]) == (
        second_review.ALLOWED_INTAKE_OUTCOMES_BEFORE_SECOND_REVIEW
    )
    assert set(schema["allowed_second_review_statuses"]) == (
        second_review.ALLOWED_SECOND_REVIEW_STATUSES
    )
    assert set(schema["allowed_second_review_decisions"]) == (
        second_review.ALLOWED_SECOND_REVIEW_DECISIONS
    )
    assert set(schema["second_review_decision_rules"]) == set(
        second_review.SECOND_REVIEW_DECISION_EXPECTED_VALUES
    )


def test_second_review_helpers_classify_committed_rows() -> None:
    rows = committed_rows()

    assert second_review.pending_second_review_rows(rows).height == 1
    assert second_review.completed_still_blocked_second_review_rows(rows).height == 0
    assert second_review.ready_for_later_reviewed_decision_rows(rows).height == 0


def test_validate_second_review_rows_rejects_missing_columns() -> None:
    rows = committed_rows().drop("claim_status_after_second_review")

    with pytest.raises(ValueError, match="missing required columns"):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_duplicate_keys() -> None:
    rows = pl.concat([committed_rows(), committed_rows()])

    with pytest.raises(ValueError, match="duplicate review keys"):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_invalid_intake_outcome() -> None:
    rows = committed_rows().with_columns(
        pl.lit("evidence_ready_for_review_decision").alias("intake_outcome_before_second_review")
    )

    with pytest.raises(ValueError, match="invalid values in intake_outcome_before_second_review"):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_invalid_review_status() -> None:
    rows = committed_rows().with_columns(
        pl.lit("accepted_for_planning_after_review").alias("second_review_status")
    )

    with pytest.raises(ValueError, match="invalid values in second_review_status"):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_invalid_review_decision() -> None:
    rows = committed_rows().with_columns(
        pl.lit("accepted_ortholog").alias("second_review_decision")
    )

    with pytest.raises(ValueError, match="invalid values in second_review_decision"):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_reviewed_target_uniprot() -> None:
    rows = committed_rows().with_columns(
        pl.lit("G3SX30").alias("reviewed_target_uniprot_after_second_review")
    )

    with pytest.raises(
        ValueError,
        match="invalid values in reviewed_target_uniprot_after_second_review",
    ):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_downstream_gate_promotion() -> None:
    rows = committed_rows().with_columns(
        pl.lit("reviewed_for_planning_still_policy_blocked").alias(
            "downstream_block_status_after_second_review"
        )
    )

    with pytest.raises(
        ValueError,
        match="invalid values in downstream_block_status_after_second_review",
    ):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_decision_rule_mismatch() -> None:
    rows = committed_rows().with_columns(
        pl.lit("ready_for_later_reviewed_decision_pr").alias("second_review_decision")
    )

    with pytest.raises(ValueError, match="decision-rule mismatches"):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_missing_forbidden_runtime_actions() -> None:
    rows = committed_rows().with_columns(
        pl.lit("biological claim").alias("forbidden_actions_after_second_review")
    )

    with pytest.raises(ValueError, match="missing required forbidden actions"):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_disallowed_claim_values() -> None:
    rows = committed_rows().with_columns(
        pl.lit("validated_longevity_signal").alias("reviewer_note")
    )

    with pytest.raises(ValueError, match="contains disallowed claim values"):
        second_review.validate_second_review_rows(rows)


def test_validate_second_review_rows_rejects_bad_sequence_length() -> None:
    rows = committed_rows().with_columns(pl.lit("not_a_length").alias("target_sequence_length"))

    with pytest.raises(ValueError, match="invalid target_sequence_length"):
        second_review.validate_second_review_rows(rows)


def test_default_second_review_queue_path_points_to_committed_input() -> None:
    assert (
        Path("data/input/ortholog_evidence_second_review_queue.csv")
        == second_review.DEFAULT_SECOND_REVIEW_QUEUE_PATH
    )


def test_validator_is_table_only_and_preserves_blocker_first_guardrails() -> None:
    rows = committed_rows()
    second_review.validate_second_review_rows(rows)

    for row in rows.iter_rows(named=True):
        assert second_review.forbidden_actions_present(row)
        assert row["downstream_block_status_after_second_review"] == (
            second_review.BLOCKED_GATE4_GATE5
        )
        assert row["claim_status_after_second_review"] == (
            second_review.REPAIR_WORKLIST_CLAIM_STATUS
        )
        assert row["claim_policy_after_second_review"] == (
            second_review.NO_BIOLOGICAL_CLAIMS_POLICY
        )
        assert row["reviewed_target_uniprot_after_second_review"] == "unresolved"
