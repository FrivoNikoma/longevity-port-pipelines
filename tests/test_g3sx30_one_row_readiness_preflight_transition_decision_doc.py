from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_readiness_preflight_transition_decision.md"
SCHEMA = ROOT / "data/config/g3sx30_one_row_readiness_preflight_transition_decision_schema.yaml"


def test_g3sx30_transition_decision_doc_records_source_result() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "source_result_table = data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv",
        "source_result_row_index = 1",
        "source_check_name = g3sx30_one_row_local_embedding_preflight_check",
        "source_check_status = local_preflight_pass",
        "source_embedding_shape = 492x960",
        "source_embedding_dtype = float32",
        "source_embedding_finite = true",
        "source_sequence_length_matches = true",
        "source_local_runtime_embedding_tracked = false",
        "source_local_runtime_embedding_committed = false",
        "candidate_id = tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession = G3SX30",
        "target_species = Loxodonta africana",
        "target_taxid = 9785",
        "gene_symbol = MDM2",
    ]:
        assert required in text


def test_g3sx30_transition_decision_doc_records_final_decision() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "data/input/g3sx30_one_row_readiness_preflight_transition_decisions.csv",
        "decision = approve_one_row_readiness_preflight_transition_path",
        "approved_for_next_transition_step = true",
        "ready_for_preflight = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
        "allowed_next_action = run_one_row_g3sx30_readiness_preflight_transition",
        "It does not mean `ready_for_preflight = true`.",
        "It does not promote Gate 8 or Gate 9.",
        "It does not make a biological claim.",
    ]:
        assert required in text


def test_g3sx30_transition_decision_doc_records_anti_loop_rule() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "final decision PR before the actual transition/check",
        "next_pr_must_be_actual_transition_check = true",
        "no_additional_decision_before_transition = true",
        "next_required_pr_title = Run one-row G3SX30 readiness/preflight transition",
        "After this PR, the next PR must run the one-row G3SX30 readiness/preflight transition.",
        "Do not add another decision, review, scaffold, or binding layer before that.",
        "No additional decision/review/scaffold/binding layer may be inserted before that transition/check.",
    ]:
        assert required in text


def test_g3sx30_transition_decision_doc_records_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "make a Biohub / ESMC call",
        "rerun live embedding",
        "generate a new embedding",
        "commit the generated `.npy` artifact",
        "commit any `data/output` artifact",
        "promote `ready_for_preflight`",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "rerun enrichment or contrast",
        "make a biological claim",
    ]:
        assert required in text


def test_g3sx30_transition_decision_schema_records_required_semantics() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_one_row_readiness_preflight_transition_decision",
        "data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv",
        "data/input/g3sx30_one_row_readiness_preflight_transition_decisions.csv",
        "source_check_status: local_preflight_pass",
        "decision: approve_one_row_readiness_preflight_transition_path",
        "approved_for_next_transition_step",
        'ready_for_preflight: "false"',
        'gate8_promoted: "false"',
        'gate9_promoted: "false"',
        'biological_claim_made: "false"',
        "allowed_next_action: run_one_row_g3sx30_readiness_preflight_transition",
        'next_pr_must_be_actual_transition_check: "true"',
        'no_additional_decision_before_transition: "true"',
        "next_required_pr_title: Run one-row G3SX30 readiness/preflight transition",
        "additional decision/review/scaffold/binding layer before transition",
    ]:
        assert required in text
