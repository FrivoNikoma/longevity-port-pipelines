from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_first_minimal_controlled_downstream_output.md"
SCHEMA = ROOT / "data/config/g3sx30_one_row_first_minimal_controlled_downstream_output_schema.yaml"


def test_first_minimal_controlled_downstream_output_doc_records_source_and_output() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "creates the first minimal controlled downstream output",
        "creates an actual one-row artifact identity and embedding health summary",
        "This is an output record, not another non-result layer.",
        "source_read_check_result_table = data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv",
        "source_read_check_result_row_index = 1",
        "source_read_check_status = controlled_downstream_read_check_passed",
        "output_action = add_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact",
        "output_status = first_minimal_controlled_downstream_output_created",
        "output_type = one_row_artifact_identity_and_embedding_health_summary",
        "candidate_id = tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession = G3SX30",
        "target_species = Loxodonta africana",
        "gene_symbol = MDM2",
        "one_row_only = true",
        "ready_scope = one_row_g3sx30_elephant_mdm2_only",
    ]:
        assert required in text


def test_first_minimal_controlled_downstream_output_doc_records_health_and_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "candidate_identity_confirmed = true",
        "artifact_reference_confirmed = true",
        "embedding_health_confirmed = true",
        "source_embedding_shape = 492x960",
        "source_embedding_dtype = float32",
        "source_embedding_finite = true",
        "source_sequence_length = 492",
        "source_sequence_length_matches = true",
        "makes no biological claim",
        "does not make a Biohub / ESMC call",
        "rerun live embedding",
        "generate a new embedding",
        "commit the generated `.npy` artifact",
        "commit any `data/output` artifact",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "rerun enrichment or contrast",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
    ]:
        assert required in text


def test_first_minimal_controlled_downstream_output_doc_avoids_non_result_wording() -> None:
    text = DOC.read_text(encoding="utf-8").lower()

    for forbidden in [
        "prepare output",
        "approve output",
        "review output",
        "scaffold output",
    ]:
        assert forbidden not in text


def test_first_minimal_controlled_downstream_output_doc_records_next_concrete_step() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "move_toward_first_analysis_adjacent_controlled_output_or_next_concrete_biological_data_bearing_step_for_one_row_ready_g3sx30_artifact",
        "next_pr_should_be_concrete_analysis_adjacent_or_biological_data_bearing_step = true",
        "no_additional_non_result_layer_before_next_concrete_step = true",
        "Do not insert another non-result layer before that concrete step.",
    ]:
        assert required in text


def test_first_minimal_controlled_downstream_output_schema_records_required_semantics() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_one_row_first_minimal_controlled_downstream_output",
        "source_read_check_result_table: data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv",
        'source_read_check_result_row_index: "1"',
        "source_read_check_status: controlled_downstream_read_check_passed",
        "output_action: add_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact",
        "output_status: first_minimal_controlled_downstream_output_created",
        "output_type: one_row_artifact_identity_and_embedding_health_summary",
        "source_embedding_shape: 492x960",
        "source_embedding_dtype: float32",
        'source_embedding_finite: "true"',
        'source_sequence_length_matches: "true"',
        'gate8_promoted: "false"',
        'gate9_promoted: "false"',
        'biological_claim_made: "false"',
        "next_step: move_toward_first_analysis_adjacent_controlled_output_or_next_concrete_biological_data_bearing_step_for_one_row_ready_g3sx30_artifact",
        'next_pr_should_be_concrete_analysis_adjacent_or_biological_data_bearing_step: "true"',
        'no_additional_non_result_layer_before_next_concrete_step: "true"',
    ]:
        assert required in text
