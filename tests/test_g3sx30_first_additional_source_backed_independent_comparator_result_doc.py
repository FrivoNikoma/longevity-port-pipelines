from pathlib import Path

DOC = Path("docs/g3sx30_first_additional_source_backed_independent_comparator_result.md")


def test_additional_comparator_result_doc_exists() -> None:
    assert DOC.is_file()


def test_additional_comparator_result_doc_records_selection_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    for required in [
        "selection_rule_frozen_before_similarity=true",
        "similarity_used_for_selection=false",
        "selection_and_result_in_same_step=true",
        "source-backed technical eligibility rule",
        "selected_comparator_reuses_previous_comparator=false",
        "was not used for the selection ranking",
    ]:
        assert required in text


def test_additional_comparator_result_doc_records_exact_result() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    for required in [
        "8bot__U1_P13010--8bot__T1_P12956_receptor_9606.npy",
        "shape=642x960",
        "human MDM2 to additional comparator cosine",
        "0.8095126148075514",
        "elephant MDM2 to additional comparator cosine",
        "0.8203721870665286",
        "0.0108595722589772",
        "0180102edc74a4cee7f82a54d337bc30079e8d9f414bfb78589620a056d62a6b",
    ]:
        assert required in text


def test_additional_comparator_result_doc_preserves_claim_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    for required in [
        "not sufficient to establish biological specificity",
        "not a validated biological negative control",
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


def test_additional_comparator_result_doc_records_next_result() -> None:
    text = DOC.read_text(encoding="utf-8-sig")

    assert (
        "add_first_two_comparator_pairwise_embedding_control_summary_before_interpretation"
    ) in text
    assert "No inventory-only" in text
