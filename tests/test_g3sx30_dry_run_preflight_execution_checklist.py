from __future__ import annotations

from pathlib import Path

DOC_PATH = (
    Path(__file__).resolve().parents[1] / "docs/g3sx30_dry_run_preflight_execution_checklist.md"
)

REVIEWED_SEQUENCE_SHA256 = "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_g3sx30_dry_run_preflight_execution_checklist_records_source_row() -> None:
    text = read_doc()

    assert "# G3SX30 dry-run preflight execution checklist" in text
    assert "docs-only planning checkpoint" in text
    assert "data/input/g3sx30_dry_run_preflight_manifest.csv#1" in text
    assert "target_accession=G3SX30" in text
    assert "target_accession_db=UniProtKB TrEMBL" in text
    assert "target_species=Loxodonta africana" in text
    assert "target_taxid=9785" in text
    assert "gene_symbol=MDM2" in text
    assert (
        "source_dry_run_preflight_decision_table=data/input/g3sx30_dry_run_preflight_decisions.csv"
        in text
    )
    assert "source_dry_run_preflight_decision_row_index=1" in text
    assert "source_dry_run_preflight_decision=approve_dry_run_preflight_for_planning" in text
    assert (
        "source_dry_run_preflight_status_after_decision="
        "dry_run_preflight_planning_approved_runtime_blocked" in text
    )
    assert (
        "source_allowed_next_action_after_decision=prepare_later_dry_run_preflight_manifest_pr"
        in text
    )
    assert "source_max_live_batch_size_after_decision=0" in text
    assert "source_ready_for_preflight_after_decision=false" in text
    assert "reviewed_sequence_length=492" in text
    assert f"reviewed_sequence_sha256={REVIEWED_SEQUENCE_SHA256}" in text
    assert "manifest_entry_status=manifest_scaffold_ready_runtime_blocked" in text
    assert "dry_run_only=true" in text
    assert "max_live_batch_size=0" in text
    assert "ready_for_preflight_after_manifest=false" in text
    assert "sequence_fetch_allowed=false" in text
    assert "biohub_call_allowed=false" in text
    assert "esmc_call_allowed=false" in text
    assert "embedding_generation_allowed=false" in text
    assert "curated_embedding_preflight_allowed=false" in text
    assert "curated_embedding_single_allowed=false" in text


def test_g3sx30_dry_run_preflight_execution_checklist_includes_future_template() -> None:
    text = read_doc()

    assert "Future command template" in text
    assert "TEMPLATE ONLY" in text
    assert "do not run in this checklist PR" in text
    assert "verify the real entry point and flags" in text
    assert "uv run python -m longevity_port_pipelines.stages.curated_embedding_preflight" in text
    assert "--manifest data/input/g3sx30_dry_run_preflight_manifest.csv" in text
    assert "--candidate-id tp53_mdm2_elephant_seed_mdm2_chain" in text
    assert "--target-accession G3SX30" in text
    assert "--dry-run" in text
    assert "--max-live-batch-size 0" in text
    assert "--no-live-call" in text
    assert "--no-output-artifacts" in text
    assert "the later PR must update the command explicitly" in text


def test_g3sx30_dry_run_preflight_execution_checklist_pre_run_checks_keep_runtime_blocked() -> None:
    text = read_doc()

    assert "Required pre-run checks for the later PR" in text
    assert "The command is confirmed to be a dry-run command." in text
    assert "The command is confirmed not to require Biohub or ESMC credentials." in text
    assert "The command is confirmed not to generate embeddings." in text
    assert "The command is confirmed not to write `.npy` artifacts." in text
    assert "The command is confirmed not to write `data/output` artifacts." in text
    assert "The command is confirmed not to change any status to `ready_for_preflight`." in text


def test_g3sx30_dry_run_preflight_execution_checklist_post_run_checks_forbid_artifacts() -> None:
    text = read_doc()

    assert "Required post-run checks for the later PR" in text
    assert "No `.npy` files were created." in text
    assert "No `data/output` artifacts were created or modified." in text
    assert "No embedding files were created or modified." in text
    assert "No Biohub / ESMC logs or credentials were committed." in text
    assert "No target sequence row was mutated." in text
    assert "No reviewed target sequence provenance row was mutated." in text
    assert "No manifest row was silently converted to `ready_for_preflight`." in text
    assert "No Gate 8 or Gate 9 field was promoted." in text
    assert "No Boltz, AF3, or Chai output was created." in text
    assert "No enrichment or contrast output was created." in text
    assert "No biological claim was added." in text


def test_g3sx30_dry_run_preflight_execution_checklist_forbidden_artifacts_and_language() -> None:
    text = read_doc()

    for required in [
        "`.npy` files",
        "generated embedding arrays",
        "generated Biohub / ESMC output",
        "`data/output` artifacts",
        "Boltz output",
        "AF3 output",
        "Chai output",
        "enrichment rerun output",
        "contrast rerun output",
        "hidden credential files",
        "local cache files",
        "raw sequence fetch artifacts",
        "biological claim summaries",
    ]:
        assert required in text

    for required in [
        "planning-only dry-run preflight execution checklist",
        "runtime remains blocked",
        "no live provider",
        "no output artifacts",
        "not ready_for_preflight",
        "no Gate 8 / Gate 9 promotion",
        "no biological claim",
    ]:
        assert required in text

    for forbidden_phrase in [
        "a completed preflight run",
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
        assert forbidden_phrase in text


def test_g3sx30_dry_run_preflight_execution_checklist_has_no_runtime_claims() -> None:
    text = read_doc()

    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not create `.npy` artifacts" in text
    assert "does not commit `data/output` artifacts" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text
