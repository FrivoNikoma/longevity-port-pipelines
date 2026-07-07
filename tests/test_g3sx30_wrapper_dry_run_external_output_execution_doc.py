from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_wrapper_dry_run_external_output_execution.md"


def test_g3sx30_wrapper_dry_run_external_output_execution_doc_records_command() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert (
        "uv run g3sx30-wrapper-dry-run --manifest "
        "data/input/g3sx30_dry_run_preflight_manifest.csv "
        "--manifest-row-index 1 --output-path "
        "D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_wrapper_dry_run_execution_plan.json"
    ) in text
    assert (
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
    ) in text
    assert "The output JSON is external and must not be committed." in text


def test_g3sx30_wrapper_dry_run_external_output_execution_doc_records_payload() -> None:
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
    ]:
        assert required in text


def test_g3sx30_wrapper_dry_run_external_output_execution_doc_keeps_forbidden_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for forbidden in [
        "Biohub / ESMC calls",
        "embedding generation",
        "`.npy` artifact creation",
        "`data/output` artifact commits",
        "live execution",
        "manifest execution beyond reading and validating reviewed row #1",
        "`ready_for_preflight`",
        "Gate 8 or Gate 9 promotion",
        "Boltz / AF3 / Chai calls",
        "enrichment or contrast reruns",
        "biological claims",
    ]:
        assert forbidden in text
