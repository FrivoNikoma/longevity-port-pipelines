from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = (
    ROOT
    / "docs"
    / "g3sx30_first_controlled_human_elephant_mdm2_pairwise_embedding_robustness_check.md"
)


def test_robustness_doc_records_control_result_and_metrics() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "deterministic_residue_block_jackknife_mean_pooling",
        "control_comparison_count = 20",
        "0.9973314302339468",
        "0.9896092392687877",
        "0.9974979683829747",
        "0.9949019040387004",
        "0.0023610146368762",
        "0.0077221909651590",
        "baseline_within_control_range = true",
        "first_controlled_pairwise_embedding_robustness_check_created",
        "control_result_created = true",
    ]:
        assert required in text


def test_robustness_doc_records_non_claim_and_artifact_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "not residue alignment",
        "not interface analysis",
        "not binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
        "not a biological claim",
        "biohub_esmc_called = false",
        "new_embedding_generated = false",
        "npy_artifact_committed = false",
        "data_output_artifact_committed = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
    ]:
        assert required in text
