from pathlib import Path

from longevity_port_pipelines.stages import (
    g3sx30_wrapper_dry_run_execution_plan_scaffold as scaffold,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data/config/g3sx30_wrapper_dry_run_execution_plan_scaffold_schema.yaml"
TABLE = ROOT / "data/interim/g3sx30_wrapper_dry_run_execution_plan_scaffold.csv"


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_files_exist() -> None:
    assert SCHEMA.exists()
    assert TABLE.exists()


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_row_matches_builder() -> None:
    rows = scaffold.read_dry_run_execution_plan_scaffold_rows(TABLE)

    assert rows == [scaffold.build_dry_run_execution_plan_scaffold_row()]
    assert scaffold.validate_dry_run_execution_plan_scaffold_row(rows[0]) == []


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_selects_future_form_only() -> None:
    row = scaffold.build_dry_run_execution_plan_scaffold_row()

    assert row["execution_plan_scaffold_status"] == (
        "dry_run_execution_plan_scaffold_non_executable"
    )
    assert row["future_command_form_selected"] == "true"
    assert row["future_non_committed_output_path_selected"] == "true"
    assert row["script_entry_point"] == "g3sx30-wrapper-dry-run"
    assert row["future_manifest_path"] == "data/input/g3sx30_dry_run_preflight_manifest.csv"
    assert row["future_manifest_row_index"] == "1"
    assert row["future_output_path"] == (
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
    )

    assert row["future_command_form"] == (
        "uv run g3sx30-wrapper-dry-run "
        "--manifest data/input/g3sx30_dry_run_preflight_manifest.csv "
        "--manifest-row-index 1 "
        "--output-path D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_wrapper_dry_run_execution_plan.json"
    )


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_keeps_runtime_blocked() -> None:
    row = scaffold.build_dry_run_execution_plan_scaffold_row()

    for column in [
        "output_file_created",
        "output_directory_created",
        "command_selected_for_execution",
        "output_path_selected_for_execution",
        "execution_plan_materialized",
        "wrapper_execution_authorized",
        "dry_run_execution_authorized",
        "live_execution_authorized",
        "manifest_execution_authorized",
        "ready_for_preflight_authorized",
        "biohub_esmc_authorized",
        "embedding_generation_authorized",
        "npy_artifact_authorized",
        "data_output_artifact_commit_authorized",
        "gate8_promotion_authorized",
        "gate9_promotion_authorized",
        "biological_claim_authorized",
    ]:
        assert row[column] == "false"

    assert row["runtime_still_blocked"] == "true"
    assert row["dry_run_execution_plan_scaffold_only"] == "true"
    assert row["claim_status"] == "technical_checkpoint"


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_output_policy() -> None:
    row = scaffold.build_dry_run_execution_plan_scaffold_row()
    future_output_path = row["future_output_path"]

    assert row["output_path_policy"] == "external_non_committed_observation_path_only"
    assert row["committed_data_output_rejected"] == "true"
    assert future_output_path.startswith("D:/biohub_projects/_chatgpt_observations/")
    assert "data/output" not in future_output_path.replace("\\", "/")
    assert not future_output_path.endswith(".npy")


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_forbidden_actions() -> None:
    row = scaffold.build_dry_run_execution_plan_scaffold_row()

    for forbidden in [
        "execute_wrapper",
        "run_dry_run",
        "run_live",
        "execute_manifest",
        "call_biohub",
        "call_esmc",
        "generate_embeddings",
        "create_npy_artifact",
        "write_output_file",
        "create_output_directory",
        "commit_data_output_artifact",
        "ready_for_preflight",
        "promote_gate8",
        "promote_gate9",
        "biological_claim",
    ]:
        assert forbidden in row["forbidden_next_actions"]


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_validator_reports_tampering() -> None:
    row = scaffold.build_dry_run_execution_plan_scaffold_row()
    row["dry_run_execution_authorized"] = "true"

    errors = scaffold.validate_dry_run_execution_plan_scaffold_row(row)

    assert errors
    assert any("dry_run_execution_authorized" in error for error in errors)
