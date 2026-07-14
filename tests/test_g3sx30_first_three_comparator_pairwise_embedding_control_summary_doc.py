from pathlib import Path

DOC = Path("docs/g3sx30_first_three_comparator_pairwise_embedding_control_summary.md")


def test_three_comparator_summary_doc_exists() -> None:
    assert DOC.is_file()


def test_three_comparator_summary_doc_records_sources_and_method() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    for required in [
        "g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv#1",
        "g3sx30_first_matched_elephant_mdm2_independent_control_results.csv#1",
        "g3sx30_first_additional_source_backed_independent_comparator_results.csv#1",
        "g3sx30_first_third_source_backed_independent_comparator_results.csv#1",
        "math.fsum(values) / count",
        "does not load any `.npy` embedding array",
        "does not compute a new cosine similarity",
        "three comparator artifact references must remain distinct",
    ]:
        assert required in text


def test_three_comparator_summary_doc_records_exact_metrics() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    for required in [
        "0.9973314302339468",
        "0.7472839682873271",
        "0.7516055327169140",
        "0.7961385463476702",
        "0.8043201055240398",
        "0.8002293259358551",
        "0.0936986285013494",
        "0.1563488334452703",
        "0.2500474619466196",
        "0.0081815591763694",
        "0.0108595722589772",
        "baseline_greater_than_all_six_controls=true",
        "elephant_control_greater_than_human_control_count=3",
        "anchor_ordering_consistent_across_comparators=true",
        "all_comparator_artifact_references_distinct=true",
    ]:
        assert required in text


def test_three_comparator_summary_doc_preserves_claim_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    for required in [
        "not a validated biological negative-control panel",
        "not evidence of biological specificity",
        "not residue alignment",
        "not interface analysis",
        "not a binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
        "not a biological claim",
        "do not replace shuffled interface controls or a",
        "curated NEGATOME control",
        "does not promote Gate 8 or Gate 9",
    ]:
        assert required in text


def test_three_comparator_summary_doc_records_next_result() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    assert "add_first_tp53_mdm2_interface_ready_manifest_result" in text
    assert "exact TP53 and MDM2 chains" in text
    assert "No inventory-only" in text
