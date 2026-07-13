from pathlib import Path

DOC_PATH = Path("docs/g3sx30_first_third_source_backed_independent_comparator_result.md")


def test_third_comparator_result_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_third_comparator_result_document_records_selection_and_metrics() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for required in [
        "First third source-backed independent comparator result",
        "selection_rule_frozen_before_similarity=true",
        "similarity_used_for_selection=false",
        "historical_inventory_file_count=216",
        "current_inventory_file_count=216",
        "source_backed_eligible_candidate_count=94",
        "7s68__D1_P09874--7s68__C1_P09874_ligand_9606.npy",
        "human MDM2 to third comparator=0.7472839682873271",
        "elephant MDM2 to third comparator=0.7516055327169140",
        "absolute human-elephant third control difference=0.0043215644295869",
        "add_first_three_comparator_pairwise_embedding_control_summary_before_interface_manifest",
    ]:
        assert required in text


def test_third_comparator_result_document_records_provenance_limit() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for required in [
        "post-selection review then found `26` exact",
        "exact_artifact_path_reference_found=false",
        "exact_artifact_basename_reference_found=false",
        "complex_role_accession_taxid_context_confirmed=true",
        "exact_embedding_byte_provenance_confirmed=false",
        "exact_sequence_hash_provenance_confirmed=false",
        "not exact embedding-byte provenance",
        "not exact sequence-hash provenance",
        "not evidence of biological specificity",
        "not interface analysis",
        "not a binding result",
        "not longevity evidence",
    ]:
        assert required in text
