from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_post_live_local_artifact_status.md"


def test_g3sx30_post_live_local_artifact_status_doc_records_live_already_completed() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "already-merged guarded one-row G3SX30 live embedding",
        "The first guarded Biohub / ESMC live embedding call has already happened",
        "status = live_completed",
        "embedding_shape = 492x960",
        "live_exit_code = 0",
        "embedding_exists = true",
        "This checkpoint does not run live embedding again.",
    ]:
        assert required in text


def test_g3sx30_post_live_local_artifact_status_doc_records_artifact_status() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "local_runtime_embedding_exists = true",
        "tracked_embedding_files = none",
        "ignore_rule = .gitignore:9:data/output/*",
        "local_runtime_embedding_tracked = false",
        "local_runtime_embedding_committed = false",
        "artifact_location = local_runtime_data_output_ignored_by_git",
    ]:
        assert required in text


def test_g3sx30_post_live_local_artifact_status_doc_records_external_artifacts() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_output.txt",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence_validation.json",
        "exist outside the repository and are not committed",
    ]:
        assert required in text


def test_g3sx30_post_live_local_artifact_status_doc_records_validation_summary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "shape = 492x960",
        "dtype = float32",
        "finite = true",
        "sequence_length_matches = true",
        "biohub_esmc_called = true",
        "embedding_generation_performed = true",
        "npy_artifact_created = true",
        "data_output_artifact_committed = false",
        "ready_for_preflight_promoted = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
    ]:
        assert required in text


def test_g3sx30_post_live_local_artifact_status_doc_records_boundary_and_next_step() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "make a new Biohub / ESMC call",
        "rerun live embedding",
        "generate a new embedding",
        "commit the generated .npy artifact",
        "commit any data/output artifact",
        "commit the external FASTA artifact",
        "commit the external live log",
        "commit the external validation JSON",
        "promote ready_for_preflight",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "rerun enrichment or contrast",
        "make a biological claim",
        "do not add another generic checkpoint, review, scaffold, or decision layer",
        "Review G3SX30 local embedding artifact and decide readiness/preflight path",
        "Approve G3SX30 local embedding artifact for one-row readiness/preflight input",
    ]:
        assert required in text
