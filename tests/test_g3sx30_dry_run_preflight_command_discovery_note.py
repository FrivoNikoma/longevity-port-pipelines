from __future__ import annotations

from pathlib import Path

DOC = (
    Path(__file__).resolve().parents[1] / "docs/g3sx30_dry_run_preflight_command_discovery_note.md"
)
SHA = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_command_discovery_note_records_source_and_manifest_guards() -> None:
    text = read_doc()
    for required in [
        "# G3SX30 dry-run preflight command discovery note",
        "docs-only command discovery note",
        "docs/g3sx30_dry_run_preflight_execution_checklist.md",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "manifest_entry_status=manifest_scaffold_ready_runtime_blocked",
        "dry_run_only=true",
        "max_live_batch_size=0",
        "ready_for_preflight_after_manifest=false",
        "sequence_fetch_allowed=false",
        "biohub_call_allowed=false",
        "esmc_call_allowed=false",
        "embedding_generation_allowed=false",
        "curated_embedding_preflight_allowed=false",
        "curated_embedding_single_allowed=false",
        "reviewed_sequence_length=492",
        f"reviewed_sequence_sha256={SHA}",
        "claim_status=technical_checkpoint",
    ]:
        assert required in text


def test_command_discovery_note_records_scripts_and_help_commands() -> None:
    text = read_doc()
    for required in [
        "Repository script entry points to inspect later",
        "`curated-embedding-preflight`",
        "`curated-embedding-single`",
        "This discovery note does not execute either script.",
        "uv run curated-embedding-preflight --help",
        "uv run curated-embedding-single --help",
        "uv run python -m longevity_port_pipelines.stages.curated_embedding_preflight --help",
        "uv run python -m longevity_port_pipelines.stages.curated_embedding_single --help",
        "must not be run in this docs-only PR",
        "paste or summarize the relevant help output",
    ]:
        assert required in text


def test_command_discovery_note_requires_help_and_search_checks() -> None:
    text = read_doc()
    for required in [
        "the real command name or module entry point",
        "the manifest input flag",
        "the candidate id or accession filtering flag",
        "the dry-run flag",
        "a no-live-call or equivalent provider-disable flag",
        "a max-live-batch-size or equivalent zero-live-work guardrail",
        "an output-disable or no-output-artifacts flag",
        "behavior when credentials are missing",
        "behavior when the manifest row has `biohub_call_allowed=false`",
        "behavior when the manifest row has `esmc_call_allowed=false`",
        "behavior when the manifest row has `embedding_generation_allowed=false`",
        "behavior when the manifest row has `curated_embedding_preflight_allowed=false`",
        "behavior when the manifest row has `curated_embedding_single_allowed=false`",
        "behavior when the manifest row has `ready_for_preflight_after_manifest=false`",
        "the Typer app definition for `curated_embedding_preflight`",
        "the Typer app definition for `curated_embedding_single`",
        "the validation path for `g3sx30_dry_run_preflight_manifest.csv`",
        "any code path that writes `.npy`",
        "any code path that writes `data/output`",
        "any code path that calls Biohub",
        "any code path that calls ESMC",
        "any code path that changes `ready_for_preflight`",
        "any code path that updates Gate 8 or Gate 9",
        "any code path that calls Boltz, AF3, or Chai",
        "document which files were inspected",
        "remains dry-run-only",
    ]:
        assert required in text


def test_command_discovery_note_keeps_this_pr_no_run() -> None:
    text = read_doc()
    for required in [
        "Required no-run proof for this PR",
        "must remain docs-only",
        "Allowed validation for this PR",
        "Forbidden validation for this PR",
        "`uv run pytest -q`",
        "`uv run curated-embedding-preflight`",
        "`uv run curated-embedding-single`",
        "`uv run python -m longevity_port_pipelines.stages.curated_embedding_preflight`",
        "`uv run python -m longevity_port_pipelines.stages.curated_embedding_single`",
        "any command that calls Biohub / ESMC",
        "any command that generates embeddings",
        "any command that writes `.npy`",
        "any command that writes `data/output`",
        "any command that changes `ready_for_preflight`",
        "any command that promotes Gate 8 or Gate 9",
        "any command that calls Boltz, AF3, or Chai",
    ]:
        assert required in text


def test_command_discovery_note_stop_conditions_and_language() -> None:
    text = read_doc()
    for required in [
        "the help text does not expose a dry-run flag",
        "the help text does not expose a no-live-call or equivalent guardrail",
        "the help text does not expose an output-disable or no-output-artifacts guardrail",
        "the command would require Biohub or ESMC credentials",
        "the command would generate embeddings",
        "the command would write `.npy`",
        "the command would write `data/output`",
        "the command would change `ready_for_preflight`",
        "the command would promote Gate 8 or Gate 9",
        "the command would call Boltz, AF3, or Chai",
        "the command would add a biological claim",
        "command discovery note",
        "help-output checklist",
        "no-run proof",
        "docs-only checkpoint",
        "runtime remains blocked",
        "no live provider",
        "no output artifacts",
        "not ready_for_preflight",
        "no Gate 8 / Gate 9 promotion",
        "no biological claim",
        "a completed preflight run",
        "a dry-run execution result",
        "a live Biohub call",
        "an ESMC embedding generation",
        "an embedding fill",
        "`ready_for_preflight`",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "Boltz ready",
        "AF3 ready",
        "Chai ready",
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert required in text


def test_command_discovery_note_has_no_runtime_claims() -> None:
    text = read_doc()
    for required in [
        "does not run `curated-embedding-preflight`",
        "does not run `curated_embedding_preflight`",
        "does not run `curated-embedding-single`",
        "does not run `curated_embedding_single`",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not make biological claims",
    ]:
        assert required in text
