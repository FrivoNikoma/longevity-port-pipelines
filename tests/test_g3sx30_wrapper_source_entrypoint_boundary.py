import json
from pathlib import Path

from longevity_port_pipelines.stages import g3sx30_wrapper_source_entrypoint_boundary as boundary

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("data/input/g3sx30_dry_run_preflight_manifest.csv")


def test_g3sx30_wrapper_source_entrypoint_boundary_status_enables_reviewed_dry_run() -> None:
    status = boundary.build_boundary_status()

    assert status["entrypoint_boundary_status"] == "reviewed_external_output_dry_run_enabled"
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
    assert status["reviewed_external_output_path"] == (
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
    )
    assert status["reviewed_command_form"] == (
        "uv run g3sx30-wrapper-dry-run "
        "--manifest data/input/g3sx30_dry_run_preflight_manifest.csv "
        "--manifest-row-index 1 "
        "--output-path D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_wrapper_dry_run_execution_plan.json"
    )


def test_g3sx30_wrapper_source_entrypoint_boundary_authorizes_only_reviewed_dry_run() -> None:
    status = boundary.build_boundary_status()

    for key in [
        "actual_command_verified",
        "command_selected_for_execution",
        "output_path_selected_for_execution",
        "execution_plan_materialized",
        "wrapper_execution_authorized",
        "dry_run_execution_authorized",
        "dry_run_output_external_only",
    ]:
        assert status[key] is True

    for key in [
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
        "ordinary_scripts_valid_as_substitutes",
    ]:
        assert status[key] is False

    assert status["runtime_still_blocked"] is False
    assert status["runtime_client_path_still_blocked"] is True


def test_g3sx30_wrapper_source_entrypoint_boundary_lists_reviewed_options() -> None:
    assert boundary.REVIEWED_DRY_RUN_OPTIONS == (
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


def test_g3sx30_wrapper_source_entrypoint_boundary_forbids_non_dry_run_actions() -> None:
    for required in [
        "live execution",
        "Biohub / ESMC call",
        "embedding generation",
        ".npy artifact creation",
        "data/output artifact commit",
        "ready_for_preflight promotion",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "Boltz call",
        "AF3 call",
        "Chai call",
        "enrichment rerun",
        "contrast rerun",
        "biological claim",
    ]:
        assert required in boundary.FORBIDDEN_NON_DRY_RUN_ACTIONS


def test_g3sx30_wrapper_source_entrypoint_boundary_validates_manifest_row() -> None:
    row = boundary.read_manifest_row(MANIFEST, 1)

    assert boundary.validate_manifest_row(row) == []
    assert row["target_accession"] == "G3SX30"
    assert row["target_taxid"] == "9785"
    assert row["reviewed_sequence_length"] == "492"
    assert row["reviewed_sequence_sha256"] == (
        "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
    )


def test_g3sx30_wrapper_source_entrypoint_boundary_rejects_unreviewed_request(
    tmp_path: Path,
) -> None:
    errors = boundary.validate_reviewed_request(
        manifest=tmp_path / "other_manifest.csv",
        manifest_row_index=2,
        output_path=tmp_path / "output.json",
    )

    assert any("manifest must be" in error for error in errors)
    assert any("manifest row index must be 1" in error for error in errors)
    assert any("output path must be the reviewed external path" in error for error in errors)


def test_g3sx30_wrapper_source_entrypoint_boundary_cli_writes_reviewed_dry_run_json(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from typer.testing import CliRunner

    reviewed_output_path = tmp_path / "observations" / "g3sx30_wrapper_dry_run_execution_plan.json"
    monkeypatch.setattr(boundary, "REVIEWED_EXTERNAL_OUTPUT_PATH", reviewed_output_path)

    runner = CliRunner()
    result = runner.invoke(
        boundary.app,
        [
            "--manifest",
            MANIFEST.as_posix(),
            "--manifest-row-index",
            "1",
            "--output-path",
            reviewed_output_path.as_posix(),
        ],
    )

    assert result.exit_code == 0
    assert "wrote reviewed external dry-run observation" in result.output
    assert "No Biohub / ESMC call" in result.output

    payload = json.loads(reviewed_output_path.read_text(encoding="utf-8"))

    assert payload["dry_run_executed"] is True
    assert payload["manifest_row_index"] == 1
    assert payload["target_accession"] == "G3SX30"
    assert payload["target_taxid"] == 9785
    assert payload["reviewed_sequence_length"] == 492
    assert payload["reviewed_sequence_sha256"] == (
        "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
    )
    assert payload["manifest_row_read"] is True
    assert payload["manifest_row_validated"] is True
    assert payload["manifest_execution_performed"] is False
    assert payload["live_execution_performed"] is False
    assert payload["sequence_fetch_performed"] is False
    assert payload["biohub_esmc_called"] is False
    assert payload["embedding_generation_performed"] is False
    assert payload["curated_embedding_preflight_run"] is False
    assert payload["curated_embedding_single_run"] is False
    assert payload["npy_artifact_created"] is False
    assert payload["data_output_artifact_created"] is False
    assert payload["ready_for_preflight_promoted"] is False
    assert payload["gate8_promoted"] is False
    assert payload["gate9_promoted"] is False
    assert payload["boltz_called"] is False
    assert payload["af3_called"] is False
    assert payload["chai_called"] is False
    assert payload["enrichment_rerun"] is False
    assert payload["contrast_rerun"] is False
    assert payload["biological_claim_made"] is False
    assert payload["output_path"] == reviewed_output_path.as_posix()
    assert payload["claim_status"] == "technical_checkpoint"


def test_g3sx30_wrapper_source_entrypoint_boundary_cli_rejects_unreviewed_output_path(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from typer.testing import CliRunner

    reviewed_output_path = tmp_path / "observations" / "reviewed.json"
    unreviewed_output_path = tmp_path / "observations" / "unreviewed.json"
    monkeypatch.setattr(boundary, "REVIEWED_EXTERNAL_OUTPUT_PATH", reviewed_output_path)

    runner = CliRunner()
    result = runner.invoke(
        boundary.app,
        [
            "--manifest",
            MANIFEST.as_posix(),
            "--manifest-row-index",
            "1",
            "--output-path",
            unreviewed_output_path.as_posix(),
        ],
    )

    assert result.exit_code == 2
    assert "output path must be the reviewed external path" in result.output
    assert not unreviewed_output_path.exists()


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
