from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_wrapper_dry_run_execution_plan_scaffold.md"


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_doc_records_status() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "execution_plan_scaffold_status = dry_run_execution_plan_scaffold_non_executable",
        "future_command_form_selected = true",
        "future_non_committed_output_path_selected = true",
        "command_selected_for_execution = false",
        "output_path_selected_for_execution = false",
        "execution_plan_materialized = false",
        "dry_run_execution_authorized = false",
        "runtime_still_blocked = true",
        "claim_status = technical_checkpoint",
    ]:
        assert required in text


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_doc_records_future_command() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert (
        "uv run g3sx30-wrapper-dry-run --manifest "
        "data/input/g3sx30_dry_run_preflight_manifest.csv "
        "--manifest-row-index 1 --output-path "
        "D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_wrapper_dry_run_execution_plan.json"
    ) in text
    assert "This command form is recorded for future review only." in text
    assert "It is not run by this PR." in text


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_doc_records_external_path() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert (
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
    ) in text
    assert "outside the repository and outside `data/output`" in text
    assert "The path is not created by this PR." in text
    assert "No output directory is created by this PR." in text


def test_g3sx30_wrapper_dry_run_execution_plan_scaffold_doc_forbids_execution() -> None:
    text = DOC.read_text(encoding="utf-8")

    for forbidden in [
        "This scaffold does not run `g3sx30-wrapper-dry-run`.",
        "run a dry-run",
        "run a live path",
        "execute the G3SX30 manifest",
        "call Biohub / ESMC",
        "generate embeddings",
        "create `.npy` artifacts",
        "create the future output file",
        "create the future output directory",
        "write `data/output` artifacts",
        "mark anything `ready_for_preflight`",
        "promote Gate 8 or Gate 9",
        "make biological claims",
    ]:
        assert forbidden in text
