from __future__ import annotations

from pathlib import Path

DOC = (
    Path(__file__).resolve().parents[1] / "docs/g3sx30_dry_run_preflight_cli_compatibility_note.md"
)
SHA = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_cli_compatibility_note_records_source_documents_and_manifest_guards() -> None:
    text = read_doc()
    for required in [
        "# G3SX30 dry-run preflight CLI compatibility note",
        "docs-only compatibility note",
        "docs/g3sx30_dry_run_preflight_execution_checklist.md",
        "docs/g3sx30_dry_run_preflight_command_discovery_note.md",
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


def test_cli_compatibility_note_records_script_names() -> None:
    text = read_doc()
    for required in [
        "curated-embedding-preflight = longevity_port_pipelines.stages.curated_embedding_preflight:app",
        "curated-embedding-single = longevity_port_pipelines.stages.curated_embedding_single:app",
        "does not run either script",
        "does not run `--help`",
    ]:
        assert required in text


def test_cli_compatibility_note_records_preflight_actual_behavior() -> None:
    text = read_doc()
    for required in [
        "Actual `curated-embedding-preflight` behavior",
        "`curated_orthologs`",
        "`output_dir`",
        "`model_name`",
        "`output`",
        "curated_orthologs=data/input/curated_ortholog_candidates.csv",
        "output_dir=data/output",
        "model_name=esmc-300m-2024-12",
        "output=data/output/curated_ortholog_embedding_preflight.csv",
        "manifest input flag | absent",
        "explicit dry-run flag | absent",
        "no-live-call/provider-disable flag | absent",
        "max-live-batch-size or zero-live-work guardrail | absent",
        "no-output-artifacts or output-disable flag | absent",
        "behavior when manifest flags are false | absent/ambiguous",
        "dry-run-only implementation | satisfied by implementation",
        "writes an output CSV by default",
        "not manifest-aware",
        "not be treated as a direct G3SX30 manifest-row execution command as-is",
    ]:
        assert required in text


def test_cli_compatibility_note_records_single_actual_behavior() -> None:
    text = read_doc()
    for required in [
        "Actual `curated-embedding-single` behavior",
        "`complex_id`",
        "`chain`",
        "`target_species_taxid`",
        "`curated_orthologs`",
        "`output_dir`",
        "`model_name`",
        "`biohub_api_url`",
        "`yes_live`",
        "`skip_existing`",
        "candidate/accession filtering flag | partially satisfied",
        "no-live-call/provider-disable flag | partially satisfied by default `yes_live=false`",
        "dry-run by default | satisfied",
        "accidental live-call risk | present if `--yes-live` is passed",
        "Biohub/ESMC call path | present behind `--yes-live`",
    ]:
        assert required in text


def test_cli_compatibility_note_records_verdict_and_absences() -> None:
    text = read_doc()
    for required in [
        "The current CLI does not match the G3SX30 dry-run preflight checklist expectations closely enough for direct execution.",
        "actual script names exist",
        "`curated-embedding-preflight` is dry-run-only by implementation",
        "`curated-embedding-single` is dry-run by default",
        "`curated-embedding-single` has a live-call gate through `--yes-live`",
        "no G3SX30 manifest input flag",
        "no direct manifest-row validation path",
        "no explicit `--dry-run` flag on `curated-embedding-preflight`",
        "no explicit `--dry-run` flag on `curated-embedding-single`",
        "no explicit `--no-live-call` flag",
        "no explicit `--max-live-batch-size 0` guardrail",
        "no explicit `--no-output-artifacts` guardrail",
        "current `curated-embedding-preflight` writes a CSV under `data/output` by default",
    ]:
        assert required in text


def test_cli_compatibility_note_records_output_path_and_adapter_implication() -> None:
    text = read_doc()
    for required in [
        "Output-path implication",
        "must not use the default `curated-embedding-preflight` output path",
        "`data/output/curated_ortholog_embedding_preflight.csv`",
        "redirect output outside committed `data/output`",
        "This compatibility note does not choose or run any output path.",
        "Adapter/wrapper implication",
        "A manifest-aware dry-run adapter or wrapper is likely needed before execution.",
        "read `data/input/g3sx30_dry_run_preflight_manifest.csv#1`",
        "require `dry_run_only=true`",
        "require `max_live_batch_size=0`",
        "refuse Biohub / ESMC calls",
        "refuse embedding generation",
        "refuse `.npy` writes",
        "refuse committed `data/output` artifacts",
        "preserve `claim_status=technical_checkpoint`",
    ]:
        assert required in text


def test_cli_compatibility_note_records_stop_conditions_and_next_options() -> None:
    text = read_doc()
    for required in [
        "Stop conditions before any actual run",
        "the command is not manifest-aware",
        "the command cannot bind to `data/input/g3sx30_dry_run_preflight_manifest.csv#1`",
        "the command cannot verify `dry_run_only=true`",
        "the command cannot enforce `max_live_batch_size=0`",
        "the command cannot enforce `ready_for_preflight_after_manifest=false`",
        "the command would write committed `data/output` artifacts",
        "the command would write `.npy`",
        "the command would require Biohub or ESMC credentials",
        "the command would call Biohub / ESMC",
        "the command would unlock the manifest runtime path",
        "the command would promote Gate 8 or Gate 9",
        "the command would call Boltz, AF3, or Chai",
        "the command would add a biological claim",
        "Recommended next PR options",
        "Add a manifest-aware dry-run preflight adapter/wrapper scaffold.",
        "Add a tiny source-level guardrail to `curated-embedding-preflight` before any G3SX30 execution.",
        "Stop and keep G3SX30 runtime-blocked because required guardrails are absent.",
    ]:
        assert required in text


def test_cli_compatibility_note_has_no_runtime_claims() -> None:
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
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
    ]:
        assert required in text
