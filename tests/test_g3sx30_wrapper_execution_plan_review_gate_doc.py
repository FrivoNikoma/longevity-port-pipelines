from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_wrapper_execution_plan_review_gate.md"


def test_g3sx30_wrapper_execution_plan_review_gate_doc_records_status() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "execution_plan_review_status = execution_plan_review_gate_runtime_blocked",
        "execution_plan_review_decision = require_separate_review_before_any_execution",
        "help_observation_status = observed_help_only",
        "help_exit_code = 0",
        "observed_help_target = g3sx30-wrapper-dry-run",
        "observed_manifest_option = true",
        "observed_manifest_row_index_option = true",
        "observed_output_path_option = true",
        "observed_help_option = true",
        "dry_run_plan_review_required_before_execution = true",
        "non_committed_output_path_review_required = true",
        "output_path_selected_for_execution = false",
        "command_selected_for_execution = false",
        "execution_plan_materialized = false",
        "wrapper_execution_authorized = false",
        "dry_run_execution_authorized = false",
        "live_execution_authorized = false",
        "ready_for_preflight_authorized = false",
        "biohub_esmc_authorized = false",
        "embedding_generation_authorized = false",
        "runtime_still_blocked = true",
    ]:
        assert required in text


def test_g3sx30_wrapper_execution_plan_review_gate_doc_keeps_future_plan_strict() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "explicit non-committed output path",
        "no Biohub / ESMC",
        "no embedding generation",
        "no .npy artifact",
        "no committed data/output artifact",
        "ready_for_preflight remains false",
        "Gate 8 remains blocked",
        "Gate 9 remains blocked",
        "no biological claim",
    ]:
        assert required in text


def test_g3sx30_wrapper_execution_plan_review_gate_doc_rejects_execution() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "does not run `g3sx30-wrapper-dry-run`",
        "does not run the wrapper without `--help`",
        "does not execute a dry-run",
        "does not execute a live run",
        "does not read or execute the G3SX30 manifest",
        "does not select a command for execution",
        "does not select an output path for execution",
        "does not materialize an execution plan",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not write `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not make biological claims",
    ]:
        assert required in text
