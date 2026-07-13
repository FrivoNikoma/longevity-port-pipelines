from pathlib import Path

DOC = Path("docs/g3sx30_first_two_comparator_pairwise_embedding_control_summary.md")


def test_two_comparator_summary_doc_exists() -> None:
    assert DOC.is_file()


def test_two_comparator_summary_doc_records_sources_and_method() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    for required in [
        "g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv#1",
        "g3sx30_first_matched_elephant_mdm2_independent_control_results.csv#1",
        "g3sx30_first_additional_source_backed_independent_comparator_results.csv#1",
        "math.fsum(values) / count",
        "does not load any `.npy` embedding array",
        "does not compute a new cosine similarity",
    ]:
        assert required in text


def test_two_comparator_summary_doc_records_exact_metrics() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    for required in [
        "0.9973314302339468",
        "0.8205658353778419",
        "0.8306773919276025",
        "0.8256216136527222",
        "0.0314699819811251",
        "0.1563488334452703",
        "0.1878188154263953",
        "0.0101115565497607",
        "0.0108595722589772",
        "baseline_greater_than_all_four_controls=true",
        "anchor_ordering_consistent_across_comparators=true",
    ]:
        assert required in text


def test_two_comparator_summary_doc_preserves_claim_boundary() -> None:
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
        "does not promote Gate 8 or Gate 9",
    ]:
        assert required in text


def test_two_comparator_summary_doc_records_next_result() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    assert (
        "add_first_third_source_backed_independent_comparator_result_"
        "with_selection_frozen_in_same_step"
    ) in text
    assert "No inventory-only" in text
