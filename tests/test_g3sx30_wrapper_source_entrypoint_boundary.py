from pathlib import Path

from longevity_port_pipelines.stages import g3sx30_wrapper_source_entrypoint_boundary as boundary


def test_g3sx30_wrapper_source_entrypoint_boundary_status_is_runtime_blocked() -> None:
    status = boundary.build_boundary_status()

    assert status["entrypoint_boundary_status"] == "source_entrypoint_boundary_runtime_blocked"
    assert status["script_entry_point"] == "g3sx30-wrapper-dry-run"
    assert status["expected_command_family"] == "curated_embedding_preflight_dry_run_wrapper"
    assert status["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert status["target_accession"] == "G3SX30"
    assert status["target_accession_db"] == "UniProtKB TrEMBL"
    assert status["target_species"] == "Loxodonta africana"
    assert status["target_taxid"] == 9785
    assert status["gene_symbol"] == "MDM2"
    assert status["reviewed_sequence_length"] == 492
    assert status["reviewed_sequence_sha256"] == (
        "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
    )
    assert status["manifest"] == "data/input/g3sx30_dry_run_preflight_manifest.csv"
    assert status["manifest_row_index"] == 1
    assert status["future_safe_observation"] == "uv run g3sx30-wrapper-dry-run --help"


def test_g3sx30_wrapper_source_entrypoint_boundary_does_not_authorize_runtime() -> None:
    status = boundary.build_boundary_status()

    for key in [
        "actual_cli_help_observed",
        "actual_command_verified",
        "command_selected_for_execution",
        "output_path_selected_for_execution",
        "execution_plan_materialized",
        "wrapper_execution_authorized",
        "dry_run_execution_authorized",
        "live_execution_authorized",
        "ready_for_preflight_authorized",
        "biohub_esmc_authorized",
        "embedding_generation_authorized",
        "npy_artifact_authorized",
        "data_output_artifact_commit_authorized",
        "gate8_promotion_authorized",
        "gate9_promotion_authorized",
        "biological_claim_authorized",
        "ordinary_scripts_valid_as_substitutes",
    ]:
        assert status[key] is False

    assert status["runtime_still_blocked"] is True


def test_g3sx30_wrapper_source_entrypoint_boundary_lists_future_options_only() -> None:
    assert boundary.FUTURE_HELP_ONLY_OPTIONS == (
        "--manifest",
        "--manifest-row-index",
        "--output-path",
    )
    assert Path("data/input/g3sx30_dry_run_preflight_manifest.csv") == boundary.DEFAULT_MANIFEST


def test_g3sx30_wrapper_source_entrypoint_boundary_rejects_substitute_commands() -> None:
    assert boundary.FORBIDDEN_SUBSTITUTE_COMMANDS == (
        "curated-embedding-preflight",
        "curated_embedding_preflight",
        "curated-embedding-single",
        "curated_embedding_single",
    )


def test_g3sx30_wrapper_source_entrypoint_boundary_forbids_runtime_actions() -> None:
    for required in [
        "wrapper execution",
        "dry-run execution",
        "live execution",
        "Biohub / ESMC call",
        "embedding generation",
        ".npy artifact creation",
        "data/output artifact commit",
        "ready_for_preflight promotion",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "biological claim",
    ]:
        assert required in boundary.FORBIDDEN_RUNTIME_ACTIONS


def test_g3sx30_wrapper_source_entrypoint_boundary_blocked_runtime_message() -> None:
    message = boundary.blocked_runtime_message()

    for required in [
        "g3sx30-wrapper-dry-run",
        "runtime-blocked source entry-point boundary",
        "Only future help observation is allowed",
        "Do not execute the wrapper",
        "do not run a dry-run",
        "do not call Biohub / ESMC",
        "do not generate embeddings",
    ]:
        assert required in message


def test_g3sx30_wrapper_source_entrypoint_boundary_cli_non_help_exits_blocked() -> None:
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(boundary.app, [])

    assert result.exit_code == 2
    assert "g3sx30-wrapper-dry-run" in result.output
    assert "runtime-blocked source entry-point boundary" in result.output
    assert "Only future help observation is allowed" in result.output
    assert "Do not execute the wrapper" in result.output
    assert "do not run a dry-run" in result.output
    assert "do not call Biohub / ESMC" in result.output
    assert "do not generate embeddings" in result.output


def test_g3sx30_wrapper_source_entrypoint_boundary_manifest_args_do_not_execute_or_write(
    tmp_path: Path,
) -> None:
    from typer.testing import CliRunner

    manifest = tmp_path / "missing_manifest.csv"
    output_path = tmp_path / "future_outputs" / "would_be_execution_plan.json"

    runner = CliRunner()
    result = runner.invoke(
        boundary.app,
        [
            "--manifest",
            str(manifest),
            "--manifest-row-index",
            "1",
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 2
    assert "runtime-blocked source entry-point boundary" in result.output
    assert "Only future help observation is allowed" in result.output

    assert not manifest.exists()
    assert not output_path.exists()
    assert not output_path.parent.exists()


def test_g3sx30_wrapper_source_entrypoint_boundary_cli_does_not_mutate_runtime_status(
    tmp_path: Path,
) -> None:
    from typer.testing import CliRunner

    status_before = boundary.build_boundary_status()

    runner = CliRunner()
    result = runner.invoke(
        boundary.app,
        [
            "--manifest",
            str(tmp_path / "manifest.csv"),
            "--manifest-row-index",
            "1",
            "--output-path",
            str(tmp_path / "plan.json"),
        ],
    )

    assert result.exit_code == 2
    assert boundary.build_boundary_status() == status_before

    status_after = boundary.build_boundary_status()
    for key in [
        "command_selected_for_execution",
        "output_path_selected_for_execution",
        "execution_plan_materialized",
        "wrapper_execution_authorized",
        "dry_run_execution_authorized",
        "live_execution_authorized",
        "ready_for_preflight_authorized",
        "biohub_esmc_authorized",
        "embedding_generation_authorized",
        "npy_artifact_authorized",
        "data_output_artifact_commit_authorized",
        "gate8_promotion_authorized",
        "gate9_promotion_authorized",
        "biological_claim_authorized",
    ]:
        assert status_after[key] is False

    assert status_after["runtime_still_blocked"] is True


def test_g3sx30_wrapper_source_entrypoint_boundary_has_no_runtime_client_imports() -> None:
    import ast

    module_path = Path(boundary.__file__)
    tree = ast.parse(module_path.read_text(encoding="utf-8"))

    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    forbidden_runtime_imports = {
        "biohub",
        "esmc",
        "esm",
        "torch",
        "numpy",
        "requests",
        "httpx",
        "urllib",
    }

    assert imported_roots.isdisjoint(forbidden_runtime_imports)
