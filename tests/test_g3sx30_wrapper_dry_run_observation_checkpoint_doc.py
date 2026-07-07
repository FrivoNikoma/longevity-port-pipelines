from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_wrapper_dry_run_observation_checkpoint.md"


def test_g3sx30_wrapper_dry_run_observation_checkpoint_doc_records_external_file() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert (
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
    ) in text
    assert "The external JSON observation is not committed." in text
    assert "It does not rerun the dry-run." in text


def test_g3sx30_wrapper_dry_run_observation_checkpoint_doc_records_observed_summary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "dry_run_executed = true",
        "manifest_row_index = 1",
        "target_accession = G3SX30",
        "target_taxid = 9785",
        "reviewed_sequence_length = 492",
        "reviewed_sequence_sha256 = e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
        "biohub_esmc_called = false",
        "embedding_generation_performed = false",
        "npy_artifact_created = false",
        "data_output_artifact_created = false",
        "ready_for_preflight_promoted = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
        "manifest_row_read = true",
        "manifest_row_validated = true",
        "sequence_fetch_performed = false",
        "live_execution_performed = false",
        "manifest_execution_performed = false",
        "curated_embedding_preflight_run = false",
        "curated_embedding_single_run = false",
        "boltz_called = false",
        "af3_called = false",
        "chai_called = false",
        "enrichment_rerun = false",
        "contrast_rerun = false",
        "claim_status = technical_checkpoint",
    ]:
        assert required in text


def test_g3sx30_wrapper_dry_run_observation_checkpoint_doc_keeps_forbidden_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for forbidden in [
        "rerun `g3sx30-wrapper-dry-run`",
        "commit the external JSON observation",
        "call Biohub / ESMC",
        "generate embeddings",
        "create `.npy` artifacts",
        "create or commit `data/output` artifacts",
        "run a live path",
        "promote `ready_for_preflight`",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "rerun enrichment or contrast",
        "make biological claims",
    ]:
        assert forbidden in text


def test_g3sx30_wrapper_dry_run_observation_checkpoint_doc_names_next_step() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "do not add another generic checkpoint, review, scaffold, or blocker layer" in text
    assert "Review G3SX30 dry-run observation and decide the next data-producing step" in text
    assert "prepare a one-row live embedding decision" in text
    assert "repair a concrete blocker found in the dry-run observation" in text
