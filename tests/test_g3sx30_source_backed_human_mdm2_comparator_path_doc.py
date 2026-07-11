from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_source_backed_human_mdm2_comparator_path.md"
SCHEMA = ROOT / "data/config/g3sx30_source_backed_human_mdm2_comparator_path_schema.yaml"


def test_comparator_document_exists_and_records_concrete_result() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [
        "first concrete comparator/blocker result",
        "data/input/tp53_mdm2_pilot_manifest.csv#2",
        "data/input/tp53_mdm2_ortholog_repair_decisions.csv#2",
        "data/input/ortholog_evidence_review_decisions.csv#1",
        "g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv#1",
        "human_reference_source_backed = true",
        "human_reference_accession = Q00987",
        "human_reference_pdb_id = 1ycr",
        "human_reference_chain = A",
        "human_embedding_available = false",
        "elephant_embedding_available = true",
        "pairwise_summary_created = false",
        "source_backed_human_mdm2_embedding_not_available",
        "not an orthology result",
        "not a protein-binding result",
        "not a beneficial-breakage result",
        "not longevity evidence",
        "generate_source_backed_human_mdm2_embedding_and_create_first_pairwise_summary",
        "no_additional_comparator_approval_before_pairwise_result = true",
        "Do not",
    ]:
        assert required in text


def test_comparator_schema_records_boundary_and_anti_loop_rule() -> None:
    text = SCHEMA.read_text(encoding="utf-8")
    for required in [
        "source_backed_human_mdm2_comparator_path_created",
        "human_elephant_mdm2_reference_identity_comparator_for_pairwise_embedding",
        "human_reference_source_backed: true",
        "human_embedding_available: false",
        "elephant_embedding_available: true",
        "pairwise_summary_created: false",
        "source_backed_human_mdm2_embedding_not_available",
        "orthology_claim: false",
        "functional_equivalence_claim: false",
        "binding_result: false",
        "beneficial_breakage_result: false",
        "biohub_esmc_call: false",
        "embedding_generation: false",
        "gate8_promotion: false",
        "gate9_promotion: false",
        "biological_claim: false",
        "runtime_scope_must_be_encoded_in_result_bearing_step: true",
        "no_additional_comparator_approval_before_pairwise_result: true",
        "no_additional_comparator_review_before_pairwise_result: true",
    ]:
        assert required in text
