from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
import yaml

from longevity_port_pipelines.stages import ortholog_evidence_intake as intake

ROOT = Path(__file__).resolve().parents[1]
INTAKE_SCHEMA_PATH = ROOT / "data/config/ortholog_evidence_intake_schema.yaml"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def committed_rows() -> pl.DataFrame:
    rows = intake.read_intake_rows()
    assert rows.height == 4
    return rows


def test_committed_ortholog_evidence_intake_table_is_valid() -> None:
    rows = committed_rows()

    intake.validate_intake_rows(rows)

    assert set(rows.get_column("candidate_set").to_list()) == {
        "sirt6_dna_repair",
        "tp53_mdm2_elephant",
    }
    assert set(rows.get_column("intake_outcome").to_list()) == {
        "evidence_insufficient_defer",
        "evidence_ambiguous_needs_second_reviewer",
    }
    assert set(rows.get_column("target_protein_accession").to_list()) == {"unresolved", "G3SX30"}
    assert set(rows.get_column("downstream_block_status_after_intake").to_list()) == {
        intake.BLOCKED_GATE4_GATE5
    }


def test_validator_required_columns_match_schema() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)
    required_fields = set(schema["required_row_identity_fields"]) | set(
        schema["required_evidence_fields"]
    )

    assert set(intake.REQUIRED_COLUMNS) == required_fields


def test_validator_allowed_sources_and_outcomes_match_schema() -> None:
    schema = load_yaml(INTAKE_SCHEMA_PATH)

    assert set(schema["allowed_evidence_source_types"]) == intake.ALLOWED_EVIDENCE_SOURCE_TYPES
    assert set(schema["allowed_intake_outcomes"]) == intake.ALLOWED_INTAKE_OUTCOMES
    assert (
        set(schema["status_groups"]["blocked_or_unresolved"])
        == intake.BLOCKED_OR_UNRESOLVED_INTAKE_OUTCOMES
    )


def test_blocked_and_ready_helpers_classify_committed_rows() -> None:
    rows = committed_rows()

    assert intake.blocked_or_unresolved_intake_rows(rows).height == 4
    assert intake.evidence_ready_for_review_decision_rows(rows).height == 0


def test_validate_intake_rows_rejects_missing_columns() -> None:
    rows = committed_rows().drop("claim_status_after_intake")

    with pytest.raises(ValueError, match="missing required columns"):
        intake.validate_intake_rows(rows)


def test_validate_intake_rows_rejects_duplicate_keys() -> None:
    rows = pl.concat([committed_rows(), committed_rows().head(1)])

    with pytest.raises(ValueError, match="duplicate intake keys"):
        intake.validate_intake_rows(rows)


def test_validate_intake_rows_rejects_unacceptable_evidence_source_type() -> None:
    rows = committed_rows().with_columns(
        pl.when(pl.col("candidate_id") == "tp53_mdm2_elephant_seed_tp53_chain")
        .then(pl.lit("embedding_similarity_alone"))
        .otherwise(pl.col("evidence_source_type"))
        .alias("evidence_source_type")
    )

    with pytest.raises(ValueError, match="invalid values in evidence_source_type"):
        intake.validate_intake_rows(rows)


def test_validate_intake_rows_rejects_invalid_intake_outcome() -> None:
    rows = committed_rows().with_columns(pl.lit("accepted_ortholog").alias("intake_outcome"))

    with pytest.raises(ValueError, match="invalid values in intake_outcome"):
        intake.validate_intake_rows(rows)


def test_validate_intake_rows_rejects_downstream_gate_promotion() -> None:
    rows = committed_rows().with_columns(
        pl.lit("reviewed_for_planning_still_policy_blocked").alias(
            "downstream_block_status_after_intake"
        )
    )

    with pytest.raises(ValueError, match="invalid values in downstream_block_status_after_intake"):
        intake.validate_intake_rows(rows)


def test_validate_intake_rows_rejects_outcome_rule_mismatch() -> None:
    rows = committed_rows().with_columns(
        pl.lit("evidence_ready_for_review_decision").alias("intake_outcome")
    )

    with pytest.raises(ValueError, match="outcome-rule mismatches"):
        intake.validate_intake_rows(rows)


def test_validate_intake_rows_rejects_missing_forbidden_runtime_actions() -> None:
    rows = committed_rows().with_columns(
        pl.lit("biological claim").alias("forbidden_actions_after_intake")
    )

    with pytest.raises(ValueError, match="missing required forbidden actions"):
        intake.validate_intake_rows(rows)


def test_validate_intake_rows_rejects_disallowed_claim_values() -> None:
    rows = committed_rows().with_columns(
        pl.lit("validated_longevity_signal").alias("claim_status_after_intake")
    )

    with pytest.raises(ValueError, match="invalid values in claim_status_after_intake"):
        intake.validate_intake_rows(rows)


def test_validate_intake_rows_rejects_bad_sequence_length() -> None:
    rows = committed_rows().with_columns(pl.lit("not_a_length").alias("target_sequence_length"))

    with pytest.raises(ValueError, match="invalid target_sequence_length"):
        intake.validate_intake_rows(rows)


def test_default_intake_table_path_points_to_committed_input() -> None:
    assert Path("data/input/ortholog_evidence_intake.csv") == intake.DEFAULT_INTAKE_TABLE_PATH


def test_validator_is_table_only_and_preserves_blocker_first_guardrails() -> None:
    rows = committed_rows()
    intake.validate_intake_rows(rows)

    for row in rows.iter_rows(named=True):
        assert intake.forbidden_actions_present(row)
        assert row["downstream_block_status_after_intake"] == intake.BLOCKED_GATE4_GATE5
        assert row["claim_status_after_intake"] == intake.REPAIR_WORKLIST_CLAIM_STATUS
        assert row["claim_policy_after_intake"] == intake.NO_BIOLOGICAL_CLAIMS_POLICY
