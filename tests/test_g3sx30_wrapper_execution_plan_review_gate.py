import csv
from pathlib import Path

from longevity_port_pipelines.stages import g3sx30_wrapper_execution_plan_review_gate as gate

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data/config/g3sx30_wrapper_execution_plan_review_gate_schema.yaml"
TABLE = ROOT / "data/interim/g3sx30_wrapper_execution_plan_review_gate.csv"


def test_g3sx30_wrapper_execution_plan_review_gate_schema_and_table_exist() -> None:
    schema_text = SCHEMA.read_text(encoding="utf-8")
    with TABLE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == list(gate.FIELDS)
    assert len(rows) == 1

    for field in gate.FIELDS:
        assert f"name: {field}" in schema_text


def test_g3sx30_wrapper_execution_plan_review_gate_row_matches_builder() -> None:
    rows = gate.read_execution_plan_review_gate_rows(TABLE)

    assert rows == [gate.build_execution_plan_review_gate_row()]
    assert gate.validate_execution_plan_review_gate_row(rows[0]) == []


def test_g3sx30_wrapper_execution_plan_review_gate_records_help_but_not_execution() -> None:
    row = gate.build_execution_plan_review_gate_row()

    assert row["help_observation_status"] == "observed_help_only"
    assert row["help_exit_code"] == "0"
    assert row["observed_help_target"] == "g3sx30-wrapper-dry-run"
    assert row["observed_manifest_option"] == "true"
    assert row["observed_manifest_row_index_option"] == "true"
    assert row["observed_output_path_option"] == "true"
    assert row["observed_help_option"] == "true"

    for field in gate.FALSE_FLAG_FIELDS:
        assert row[field] == "false"


def test_g3sx30_wrapper_execution_plan_review_gate_requires_review_before_dry_run() -> None:
    row = gate.build_execution_plan_review_gate_row()

    assert row["execution_plan_review_status"] == "execution_plan_review_gate_runtime_blocked"
    assert row["execution_plan_review_decision"] == "require_separate_review_before_any_execution"
    assert row["dry_run_plan_review_required_before_execution"] == "true"
    assert row["non_committed_output_path_review_required"] == "true"
    assert row["output_path_policy"] == "non_committed_output_path_required_before_future_dry_run"
    assert row["committed_data_output_rejected"] == "true"
    assert row["runtime_still_blocked"] == "true"
    assert row["allowed_next_action_after_review_gate"] == (
        "add_g3sx30_wrapper_execution_plan_runtime_blocker"
    )
    assert row["claim_status"] == "technical_checkpoint"


def test_g3sx30_wrapper_execution_plan_review_gate_rejects_runtime_unlocks() -> None:
    row = gate.build_execution_plan_review_gate_row()

    for forbidden in [
        "execute_wrapper",
        "run_dry_run",
        "run_live",
        "execute_manifest",
        "select_actual_command_for_execution",
        "select_output_path_for_execution",
        "materialize_execution_plan",
        "allow_biohub_call",
        "allow_esmc_call",
        "allow_embedding_generation",
        "allow_npy_artifact",
        "commit_data_output_artifact",
        "ready_for_preflight",
        "promote_gate8",
        "promote_gate9",
        "biological_claim",
    ]:
        assert forbidden in row["forbidden_next_actions"]


def test_g3sx30_wrapper_execution_plan_review_gate_validator_reports_tampering() -> None:
    row = gate.build_execution_plan_review_gate_row()
    row["dry_run_execution_authorized"] = "true"

    errors = gate.validate_execution_plan_review_gate_row(row)

    assert "dry_run_execution_authorized='true' expected 'false'" in errors
    assert "dry_run_execution_authorized must remain false" in errors
