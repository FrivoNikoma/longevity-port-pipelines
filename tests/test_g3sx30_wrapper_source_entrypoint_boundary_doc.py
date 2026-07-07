from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_wrapper_source_entrypoint_boundary.md"


def test_g3sx30_wrapper_source_entrypoint_boundary_doc_records_status() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "entrypoint_boundary_status = source_entrypoint_boundary_runtime_blocked",
        "script_entry_point = g3sx30-wrapper-dry-run",
        "expected_command_family = curated_embedding_preflight_dry_run_wrapper",
        "actual_cli_help_observed = false",
        "actual_command_verified = false",
        "command_selected_for_execution = false",
        "output_path_selected_for_execution = false",
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


def test_g3sx30_wrapper_source_entrypoint_boundary_doc_defines_future_help_target() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "g3sx30-wrapper-dry-run =",
        "longevity_port_pipelines.stages.g3sx30_wrapper_source_entrypoint_boundary:app",
        "uv run g3sx30-wrapper-dry-run --help",
        "later PR must still be help-only",
        "must not run the command without `--help`",
        "must not execute the wrapper",
        "must not execute a dry-run",
        "must not call Biohub / ESMC",
        "must not generate embeddings",
    ]:
        assert required in text


def test_g3sx30_wrapper_source_entrypoint_boundary_doc_makes_no_help_observation_claim() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "does not run `--help`",
        "actual_cli_help_observed = true",
        "actual_command_verified = true",
        "observed_help_flags",
        "verified_cli_contract",
        "only appear in a later actual help-observation PR",
    ]:
        assert required in text


def test_g3sx30_wrapper_source_entrypoint_boundary_doc_keeps_runtime_blocked() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "intentionally runtime-blocked",
        "stops before any runtime work",
        "does not read the G3SX30 manifest",
        "does not execute a manifest row",
        "does not select an output path for execution",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not write `data/output` artifacts",
    ]:
        assert required in text


def test_g3sx30_wrapper_source_entrypoint_boundary_doc_rejects_ordinary_substitutes() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "ordinary commands remain invalid substitutes",
        "curated-embedding-preflight",
        "curated_embedding_preflight",
        "curated-embedding-single",
        "curated_embedding_single",
        "Help observation must target the new G3SX30 wrapper boundary",
    ]:
        assert required in text
