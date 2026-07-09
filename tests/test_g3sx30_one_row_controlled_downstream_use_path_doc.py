from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_controlled_downstream_use_path.md"
SCHEMA = ROOT / "data/config/g3sx30_one_row_controlled_downstream_use_path_schema.yaml"


def test_downstream_use_path_doc_records_source_and_handle() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "first controlled downstream use path",
        "concrete controlled handle",
        "This is not another decision layer.",
        "source_transition_result_table = data/input/g3sx30_one_row_readiness_preflight_transition_results.csv",
        "source_transition_result_row_index = 1",
        "source_ready_for_preflight = true",
        "controlled_downstream_use_path = first_controlled_downstream_use_path_for_one_row_ready_artifact",
        "controlled_input_status = one_row_ready_artifact_available_for_controlled_downstream_use",
        "one_row_only = true",
        "candidate_id = tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession = G3SX30",
        "ready_scope = one_row_g3sx30_elephant_mdm2_only",
    ]:
        assert required in text


def test_downstream_use_path_doc_records_boundary_and_next_step() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
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
        "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact",
    ]:
        assert required in text


def test_downstream_use_path_schema_records_required_semantics() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_one_row_controlled_downstream_use_path",
        "source_transition_result_table: data/input/g3sx30_one_row_readiness_preflight_transition_results.csv",
        'source_ready_for_preflight: "true"',
        "controlled_downstream_use_path: first_controlled_downstream_use_path_for_one_row_ready_artifact",
        "controlled_input_status: one_row_ready_artifact_available_for_controlled_downstream_use",
        'one_row_only: "true"',
        "ready_scope: one_row_g3sx30_elephant_mdm2_only",
        'gate8_promoted: "false"',
        'gate9_promoted: "false"',
        'biological_claim_made: "false"',
        "next_step: run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact",
    ]:
        assert required in text


def test_downstream_use_path_doc_records_anti_loop_rule() -> None:
    text = DOC.read_text(encoding="utf-8")
    schema = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "next_pr_must_be_actual_controlled_downstream_read_check = true",
        "no_additional_downstream_approval_before_read_check = true",
        "No additional downstream approval/review/scaffold/binding layer is allowed before that read/check.",
    ]:
        assert required in text

    for required in [
        'next_pr_must_be_actual_controlled_downstream_read_check: "true"',
        'no_additional_downstream_approval_before_read_check: "true"',
    ]:
        assert required in schema
