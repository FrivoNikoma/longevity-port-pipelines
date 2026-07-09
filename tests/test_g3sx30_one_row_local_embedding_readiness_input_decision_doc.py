from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_local_embedding_readiness_input_decision.md"


def test_g3sx30_local_embedding_readiness_input_decision_doc_records_sources() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "docs/g3sx30_one_row_live_embedding_runtime_observation.md",
        "docs/g3sx30_post_live_local_artifact_status.md",
        "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json",
    ]:
        assert required in text


def test_g3sx30_local_embedding_readiness_input_decision_doc_records_validation() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "embedding_shape = 492x960",
        "embedding_dtype = float32",
        "embedding_finite = true",
        "sequence_length_matches = true",
        "validation_ready_for_preflight_promoted = false",
        "validation_gate8_promoted = false",
        "validation_gate9_promoted = false",
        "validation_biological_claim_made = false",
    ]:
        assert required in text


def test_g3sx30_local_embedding_readiness_input_decision_doc_records_decision() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "approved_for_one_row_readiness_preflight_input = true",
        "ready_for_preflight = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
        "approving the local artifact path as a one-row readiness/preflight input reference",
        "promoting the row to `ready_for_preflight` is not allowed in this PR",
    ]:
        assert required in text


def test_g3sx30_local_embedding_readiness_input_decision_doc_records_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "make a new Biohub / ESMC call",
        "rerun live embedding",
        "generate a new embedding",
        "commit the generated `.npy` artifact",
        "commit any `data/output` artifact",
        "commit the external FASTA artifact",
        "commit the external live log",
        "commit the external validation JSON",
        "promote `ready_for_preflight`",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "rerun enrichment or contrast",
        "make a biological claim",
        "prepare_one_row_non_committed_preflight_input_consumer_or_manifest_binding_pr",
    ]:
        assert required in text
