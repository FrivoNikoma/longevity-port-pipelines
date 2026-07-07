from pathlib import Path

from longevity_port_pipelines.stages import (
    g3sx30_wrapper_dry_run_execution_plan_review as review,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "data/config/g3sx30_wrapper_dry_run_execution_plan_review_schema.yaml"
TABLE = ROOT / "data/interim/g3sx30_wrapper_dry_run_execution_plan_review.csv"


def test_g3sx30_wrapper_dry_run_execution_plan_review_files_exist() -> None:
    assert SCHEMA.exists()
    assert TABLE.exists()


def test_g3sx30_wrapper_dry_run_execution_plan_review_row_matches_builder() -> None:
    rows = review.read_dry_run_execution_plan_review_rows(TABLE)

    assert rows == [review.build_dry_run_execution_plan_review_row()]
    assert review.validate_dry_run_execution_plan_review_row(rows[0]) == []


def test_g3sx30_wrapper_dry_run_execution_plan_review_approves_next_pr_only() -> None:
    row = review.build_dry_run_execution_plan_review_row()

    assert row["review_status"] == "dry_run_execution_plan_scaffold_reviewed"
    assert row["review_scope"] == "final_non_execution_review_before_actual_dry_run_pr"
    assert row["review_decision"] == "approve_selected_external_output_dry_run_for_next_pr"
    assert row["selected_command_form_reviewed"] == "true"
    assert row["selected_external_output_path_reviewed"] == "true"
    assert row["selected_manifest_row_reviewed"] == "true"
    assert row["dry_run_execution_authorized_for_next_pr"] == "true"
    assert row["allowed_next_action_after_review"] == (
        "execute_g3sx30_wrapper_dry_run_with_external_output_path"
    )


def test_g3sx30_wrapper_dry_run_execution_plan_review_keeps_this_pr_non_execution() -> None:
    row = review.build_dry_run_execution_plan_review_row()

    for column in [
        "dry_run_execution_authorized_in_this_pr",
        "dry_run_executed",
        "live_execution_authorized",
        "manifest_execution_authorized_in_this_pr",
        "biohub_esmc_authorized",
        "embedding_generation_authorized",
        "npy_artifact_authorized",
        "output_file_created",
        "output_directory_created",
        "data_output_artifact_commit_authorized",
        "ready_for_preflight_authorized",
        "gate8_promotion_authorized",
        "gate9_promotion_authorized",
        "biological_claim_authorized",
    ]:
        assert row[column] == "false"

    assert row["runtime_still_blocked_in_this_pr"] == "true"
    assert row["claim_status"] == "technical_checkpoint"


def test_g3sx30_wrapper_dry_run_execution_plan_review_command_and_path() -> None:
    row = review.build_dry_run_execution_plan_review_row()

    assert row["selected_future_command_form"] == (
        "uv run g3sx30-wrapper-dry-run "
        "--manifest data/input/g3sx30_dry_run_preflight_manifest.csv "
        "--manifest-row-index 1 "
        "--output-path D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_wrapper_dry_run_execution_plan.json"
    )
    assert row["selected_external_output_path"] == (
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
    )
    assert row["selected_external_output_path"].startswith(
        "D:/biohub_projects/_chatgpt_observations/"
    )
    assert "data/output" not in row["selected_external_output_path"].replace("\\", "/")
    assert not row["selected_external_output_path"].endswith(".npy")


def test_g3sx30_wrapper_dry_run_execution_plan_review_forbids_this_pr_runtime() -> None:
    row = review.build_dry_run_execution_plan_review_row()

    for forbidden in [
        "run_dry_run",
        "run_live",
        "execute_manifest_in_this_pr",
        "call_biohub",
        "call_esmc",
        "generate_embeddings",
        "create_npy_artifact",
        "create_output_file",
        "create_output_directory",
        "commit_data_output_artifact",
        "ready_for_preflight",
        "promote_gate8",
        "promote_gate9",
        "call_boltz",
        "call_af3",
        "call_chai",
        "biological_claim",
    ]:
        assert forbidden in row["forbidden_actions_this_pr"]


def test_g3sx30_wrapper_dry_run_execution_plan_review_validator_reports_tampering() -> None:
    row = review.build_dry_run_execution_plan_review_row()
    row["dry_run_executed"] = "true"

    errors = review.validate_dry_run_execution_plan_review_row(row)

    assert errors
    assert any("dry_run_executed" in error for error in errors)
