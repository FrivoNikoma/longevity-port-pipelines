from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summary.md"
SCHEMA = ROOT / (
    "data/config/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summary_schema.yaml"
)


def test_analysis_adjacent_summary_document_exists_and_records_result() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "first numerical analysis-adjacent result",
        "data/input/g3sx30_one_row_first_minimal_controlled_downstream_outputs.csv#1",
        "data/input/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv",
        "summary_status = first_analysis_adjacent_controlled_embedding_summary_created",
        "summary_type = one_row_embedding_scalar_summary_statistics",
        "summary_scope = scalar_embedding_statistics_only_no_biological_claim",
        "raw_embedding_values_committed = false",
        "token_count = 492",
        "embedding_dim = 960",
        "total_values = 472320",
        "finite_value_count = 472320",
        "finite_fraction = 1.0000000000",
        "scalar summary is not a biological comparison",
        "scalar summary is not an interface result",
        "scalar summary is not a binding result",
        "scalar summary is not longevity evidence",
        "next_step = add_first_controlled_comparator_or_pairwise_embedding_summary",
        "no_additional_scalar_summary_approval_before_comparator = true",
        "Do not insert an approval",
    ]:
        assert required in text


def test_analysis_adjacent_summary_schema_records_boundary() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "one_row_embedding_scalar_summary_statistics",
        "pipeline_integration_result: true",
        "biological_comparison: false",
        "interface_result: false",
        "binding_result: false",
        "longevity_evidence: false",
        "action: add_first_controlled_comparator_or_pairwise_embedding_summary",
        "no_additional_scalar_summary_approval_before_comparator: true",
        "biohub_esmc_call: false",
        "npy_artifact_commit: false",
        "raw_embedding_values_commit: false",
        "gate8_promotion: false",
        "gate9_promotion: false",
        "biological_claim: false",
    ]:
        assert required in text
