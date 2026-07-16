from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tp53_mdm2_actual_negatome_doc_records_result() -> None:
    text = (ROOT / "docs/tp53_mdm2_embedding_based_negatome_control_result.md").read_text(
        encoding="utf-8"
    )

    for required in (
        "actual_negatome_control_ratio_computed",
        "negatome_control_ratio=1.2482765910897506",
        "runtime_blocker=none",
        "G3UAZ0",
        "shape=364x960",
        "dtype=float32",
        "finite=true",
        "tracked=false",
        "ignored=true",
        "staged=false",
        "24.82765910897506%",
        "blocked_pending_control_result_integration",
        "gate7_entry_allowed_after=false",
        "npy_artifact_committed=false",
        "data_output_artifact_committed=false",
        "boltz_called=false",
        "biological_claim_made=false",
        "No additional live embedding was generated beyond G3UAZ0",
    ):
        assert required in text
