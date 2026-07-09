from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_local_embedding_preflight_check_result.md"
SCHEMA = ROOT / "data/config/g3sx30_one_row_local_embedding_preflight_check_result_schema.yaml"


def test_g3sx30_preflight_result_doc_records_source_binding_and_target() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "source_binding_table = data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv",
        "source_binding_row_index = 1",
        "source_binding_status = non_committed_preflight_input_reference_created",
        "candidate_id = tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession = G3SX30",
        "target_species = Loxodonta africana",
        "target_taxid = 9785",
        "gene_symbol = MDM2",
        "sequence_length = 492",
    ]:
        assert required in text


def test_g3sx30_preflight_result_doc_records_passed_local_check() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "check_name = g3sx30_one_row_local_embedding_preflight_check",
        "check_status = local_preflight_pass",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_one_row_local_embedding_preflight_check.json",
        "data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv",
        "local_runtime_embedding_exists = true",
        "local_runtime_embedding_tracked = false",
        "local_runtime_embedding_committed = false",
        "git_ignore_rule_status = data_output_ignored",
        "embedding_shape = 492x960",
        "embedding_dtype = float32",
        "embedding_finite = true",
        "sequence_length_matches = true",
    ]:
        assert required in text


def test_g3sx30_preflight_result_doc_records_no_side_effects() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "biohub_esmc_called_by_check = false",
        "live_embedding_rerun_by_check = false",
        "embedding_generation_performed_by_check = false",
        "npy_artifact_created_by_check = false",
        "data_output_artifact_committed = false",
        "external_validation_json_committed = false",
        "ready_for_preflight_promoted = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "boltz_called = false",
        "af3_called = false",
        "chai_called = false",
        "enrichment_rerun = false",
        "contrast_rerun = false",
        "biological_claim_made = false",
        "downstream_gate_unlocked = false",
    ]:
        assert required in text


def test_g3sx30_preflight_result_doc_records_interpretation_and_next_decision() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "concrete local artifact preflight pass",
        "It does not mean `ready_for_preflight = true`.",
        "It does not promote Gate 8 or Gate 9.",
        "It does not make a biological claim.",
        "next_practical_decision = approve_one_row_readiness_preflight_transition_path_or_repair_concrete_blocker",
        "pass_decision_path = approve_one_row_readiness_preflight_transition_path",
        "fail_decision_path = repair_concrete_local_preflight_blocker",
        "do not add another generic checkpoint, review, scaffold, or binding layer",
    ]:
        assert required in text


def test_g3sx30_preflight_result_schema_records_required_semantics() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_one_row_local_embedding_preflight_check_result",
        "data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_one_row_local_embedding_preflight_check.json",
        "data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv",
        "check_status: local_preflight_pass",
        "target_accession: G3SX30",
        "target_species: Loxodonta africana",
        'target_taxid: "9785"',
        "gene_symbol: MDM2",
        "embedding_shape: 492x960",
        "embedding_dtype: float32",
        "ready_for_preflight_promoted",
        "gate8_promoted",
        "biological_claim_made",
        "approve_one_row_readiness_preflight_transition_path",
        "repair_concrete_local_preflight_blocker",
    ]:
        assert required in text
