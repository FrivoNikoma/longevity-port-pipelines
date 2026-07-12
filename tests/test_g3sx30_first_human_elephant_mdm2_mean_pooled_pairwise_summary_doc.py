from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summary.md"


def test_pairwise_summary_doc_records_runtime_result_and_metrics() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "Human MDM2 Q00987 reference self-embedding runtime input",
        "live_execution_status=live_completed",
        "491x960",
        "492x960",
        "0.9973314302339468",
        "0.0026685697660532",
        "0.0609504211067301",
        "first_human_elephant_mdm2_mean_pooled_embedding_summary_created",
    ]:
        assert required in text


def test_pairwise_summary_doc_records_claim_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "not residue alignment",
        "not interface analysis",
        "not binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
        "numerical embedding-space comparison only",
    ]:
        assert required in text


def test_pairwise_summary_doc_records_forbidden_commits_and_promotions() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "`raw_sequence_committed = false`",
        "`fasta_committed = false`",
        "`runtime_csv_committed = false`",
        "`npy_artifact_committed = false`",
        "`raw_embedding_values_committed = false`",
        "`data_output_artifact_committed = false`",
        "`gate8_promoted = false`",
        "`gate9_promoted = false`",
        "`biological_claim_made = false`",
    ]:
        assert required in text
