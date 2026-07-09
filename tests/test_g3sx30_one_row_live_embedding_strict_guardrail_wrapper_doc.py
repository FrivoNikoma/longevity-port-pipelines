from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_live_embedding_strict_guardrail_wrapper.md"


def test_g3sx30_one_row_live_embedding_strict_guardrail_wrapper_doc_records_command() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "g3sx30-live-embedding-one-row" in text
    assert "longevity_port_pipelines.stages.g3sx30_live_embedding_one_row:app" in text
    assert "uv run g3sx30-live-embedding-one-row" in text
    assert "--yes-live --max-live-batch-size 1" in text


def test_g3sx30_one_row_live_embedding_strict_guardrail_wrapper_doc_records_sources() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "data/input/g3sx30_dry_run_preflight_manifest.csv#1" in text
    assert "D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta" in text
    assert "external FASTA is not committed" in text
    assert "docs/current_gate_map.md" in text


def test_g3sx30_one_row_live_embedding_strict_guardrail_wrapper_doc_records_guardrails() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [
        "manifest_row_index = 1",
        "candidate_id = tp53_mdm2_elephant_seed_mdm2_chain",
        "chain = mdm2",
        "target_accession = G3SX30",
        "target_taxid = 9785",
        "gene_symbol = MDM2",
        "reviewed_sequence_length = 492",
        "reviewed_sequence_sha256 = e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
        "approved_next_action = execute_one_row_g3sx30_live_embedding_with_strict_guardrails",
        "max_live_batch_size = 1",
        "explicit --yes-live for Biohub / ESMC",
        "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
    ]:
        assert required in text


def test_g3sx30_one_row_live_embedding_strict_guardrail_wrapper_doc_records_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [
        "more than one manifest row",
        "any manifest row except row #1",
        "a sequence fetch during live embedding execution",
        "a committed FASTA sequence artifact",
        "a committed `.npy` artifact",
        "a committed `data/output` artifact",
        "`ready_for_preflight` promotion",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "Boltz / AF3 / Chai calls",
        "enrichment or contrast reruns",
        "biological claims",
        "does not itself call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output`",
    ]:
        assert required in text
