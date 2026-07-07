from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_wrapper_dry_run_execution_plan_review.md"


def test_g3sx30_wrapper_dry_run_execution_plan_review_doc_records_decision() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "review_status = dry_run_execution_plan_scaffold_reviewed",
        "review_scope = final_non_execution_review_before_actual_dry_run_pr",
        "review_decision = approve_selected_external_output_dry_run_for_next_pr",
        "selected_command_form_reviewed = true",
        "selected_external_output_path_reviewed = true",
        "dry_run_execution_authorized_for_next_pr = true",
        "dry_run_execution_authorized_in_this_pr = false",
        "dry_run_executed = false",
        "runtime_still_blocked_in_this_pr = true",
        "allowed_next_action_after_review = execute_g3sx30_wrapper_dry_run_with_external_output_path",
    ]:
        assert required in text


def test_g3sx30_wrapper_dry_run_execution_plan_review_doc_records_command_and_path() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert (
        "uv run g3sx30-wrapper-dry-run --manifest "
        "data/input/g3sx30_dry_run_preflight_manifest.csv "
        "--manifest-row-index 1 --output-path "
        "D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_wrapper_dry_run_execution_plan.json"
    ) in text
    assert (
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
    ) in text
    assert "approved for the next PR only" in text


def test_g3sx30_wrapper_dry_run_execution_plan_review_doc_forbids_this_pr_execution() -> None:
    text = DOC.read_text(encoding="utf-8")

    for forbidden in [
        "It does not authorize dry-run execution in this PR.",
        "run `g3sx30-wrapper-dry-run`",
        "run a dry-run",
        "run a live path",
        "execute the G3SX30 manifest in this PR",
        "create the external output file",
        "create the external output directory",
        "call Biohub / ESMC",
        "generate embeddings",
        "create `.npy` artifacts",
        "write `data/output` artifacts",
        "mark anything `ready_for_preflight`",
        "promote Gate 8 or Gate 9",
        "make biological claims",
    ]:
        assert forbidden in text


def test_g3sx30_wrapper_dry_run_execution_plan_review_doc_names_next_pr() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "do not add another blocker, review, or scaffold layer" in text
    assert "Execute G3SX30 wrapper dry-run with external output path" in text
    assert "no Biohub / ESMC, no embeddings" in text
    assert "no Gate 8 / Gate 9" in text
