from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_controlled_downstream_read_check_result.md"
SCHEMA = ROOT / "data/config/g3sx30_one_row_controlled_downstream_read_check_result_schema.yaml"


def test_controlled_downstream_read_check_doc_records_source_and_result() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "actual controlled downstream read/check result",
        "This is not another approval layer, scaffold, handle, or decision layer.",
        "source_downstream_use_path_table = data/input/g3sx30_one_row_controlled_downstream_use_paths.csv",
        "source_downstream_use_path_row_index = 1",
        "source_controlled_handle_id = g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle",
        "source_ready_artifact_reference = data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "source_next_pr_must_be_actual_controlled_downstream_read_check = true",
        "source_no_additional_downstream_approval_before_read_check = true",
        "read_check_action = run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact",
        "read_check_status = controlled_downstream_read_check_passed",
        "one_row_only = true",
        "ready_scope = one_row_g3sx30_elephant_mdm2_only",
    ]:
        assert required in text


def test_controlled_downstream_read_check_doc_records_artifact_check_and_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "local_runtime_embedding_exists = true",
        "local_runtime_embedding_tracked = false",
        "local_runtime_embedding_committed = false",
        "git_ignore_rule_status = data_output_ignored",
        "embedding_shape = 492x960",
        "embedding_dtype = float32",
        "embedding_finite = true",
        "sequence_length = 492",
        "sequence_length_matches = true",
        "does not make a Biohub / ESMC call",
        "rerun live embedding",
        "generate a new embedding",
        "commit the generated `.npy` artifact",
        "commit any `data/output` artifact",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "rerun enrichment or contrast",
        "make a biological claim",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
    ]:
        assert required in text


def test_controlled_downstream_read_check_doc_records_next_output_step() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "move_toward_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact",
        "next_pr_should_move_toward_first_minimal_controlled_downstream_output = true",
        "no_additional_read_check_approval_before_output = true",
        "Do not add another read/check approval, review, scaffold, handle, or decision layer before that output-oriented step.",
    ]:
        assert required in text


def test_controlled_downstream_read_check_schema_records_required_semantics() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_one_row_controlled_downstream_read_check_result",
        "source_downstream_use_path_table: data/input/g3sx30_one_row_controlled_downstream_use_paths.csv",
        'source_downstream_use_path_row_index: "1"',
        "source_controlled_handle_id: g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle",
        "source_ready_artifact_reference: data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        'source_next_pr_must_be_actual_controlled_downstream_read_check: "true"',
        'source_no_additional_downstream_approval_before_read_check: "true"',
        "read_check_action: run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact",
        "read_check_status: controlled_downstream_read_check_passed",
        "embedding_shape: 492x960",
        "embedding_dtype: float32",
        'embedding_finite: "true"',
        'gate8_promoted: "false"',
        'gate9_promoted: "false"',
        'biological_claim_made: "false"',
        "next_step: move_toward_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact",
        'next_pr_should_move_toward_first_minimal_controlled_downstream_output: "true"',
        'no_additional_read_check_approval_before_output: "true"',
    ]:
        assert required in text
