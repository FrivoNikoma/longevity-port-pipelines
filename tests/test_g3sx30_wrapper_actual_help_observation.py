from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_wrapper_actual_help_observation.md"


def test_g3sx30_wrapper_actual_help_observation_records_help_status() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "help_observation_status = observed_help_only",
        "help_command = uv run g3sx30-wrapper-dry-run --help",
        "help_exit_code = 0",
        "observed_help_target = g3sx30-wrapper-dry-run",
        "observed_manifest_option = true",
        "observed_manifest_row_index_option = true",
        "observed_output_path_option = true",
        "observed_help_option = true",
        "actual_cli_help_observed = true",
        "actual_command_verified_for_help = true",
        "command_selected_for_execution = false",
        "output_path_selected_for_execution = false",
        "execution_plan_materialized = false",
        "wrapper_execution_authorized = false",
        "dry_run_execution_authorized = false",
        "live_execution_authorized = false",
        "biohub_esmc_authorized = false",
        "embedding_generation_authorized = false",
        "runtime_still_blocked = true",
    ]:
        assert required in text


def test_g3sx30_wrapper_actual_help_observation_records_observed_output() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "uv run g3sx30-wrapper-dry-run --help",
        "HELP_EXIT_CODE=0",
        "D:\\biohub_projects\\_chatgpt_observations\\g3sx30_wrapper_help_output.txt",
        "Usage: g3sx30-wrapper-dry-run [OPTIONS]",
        "--manifest",
        "--manifest-row-index",
        "--output-path",
        "--help",
        "interface-documentation-only controls",
        "does not read or execute the manifest",
        "does not write outputs",
    ]:
        assert required in text


def test_g3sx30_wrapper_actual_help_observation_handles_powershell_wrapper() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "PowerShell stderr wrapper note",
        "`uv` build/install warning output",
        "NativeCommandError",
        "not treated as command failure",
        "HELP_EXIT_CODE=0",
        "Typer help text was still printed",
    ]:
        assert required in text


def test_g3sx30_wrapper_actual_help_observation_records_no_runtime_artifacts() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "No-runtime-artifact proof",
        "git status -sb",
        "## observe-g3sx30-wrapper-help",
        "git ls-files --others --exclude-standard",
        "printed no untracked files",
        "did not create runtime artifacts inside the repository",
    ]:
        assert required in text


def test_g3sx30_wrapper_actual_help_observation_keeps_execution_blocked() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "observes `--help` only",
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
        "wrapper execution",
        "dry-run execution",
        "live execution",
        "Biohub / ESMC",
        "embeddings",
        "ready_for_preflight",
        "Gate 8 / Gate 9",
        "biological claim",
    ]:
        assert required in text
