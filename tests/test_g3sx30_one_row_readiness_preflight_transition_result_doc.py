from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_readiness_preflight_transition_result.md"
SCHEMA = ROOT / "data/config/g3sx30_one_row_readiness_preflight_transition_result_schema.yaml"


def test_transition_result_doc_records_source_and_result() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "actual one-row G3SX30 readiness/preflight transition/check",
        "This is not another approval, review, scaffold, or binding layer.",
        "source_decision = approve_one_row_readiness_preflight_transition_path",
        "source_approved_for_next_transition_step = true",
        "source_allowed_next_action = run_one_row_g3sx30_readiness_preflight_transition",
        "transition_action = run_one_row_g3sx30_readiness_preflight_transition",
        "transition_status = one_row_readiness_preflight_transition_passed",
        "one_row_only = true",
        "candidate_id = tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession = G3SX30",
        "ready_for_preflight = true",
        "ready_scope = one_row_g3sx30_elephant_mdm2_only",
        "`ready_for_preflight = true` applies only to this one row.",
    ]:
        assert required in text


def test_transition_result_doc_records_boundary_and_next_step() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "does not make a Biohub / ESMC call",
        "rerun live embedding",
        "generate a new embedding",
        "commit the generated `.npy` artifact",
        "commit any `data/output` artifact",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "make a biological claim",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
        "add_first_controlled_downstream_use_path_for_one_row_ready_artifact",
        "not another transition approval",
    ]:
        assert required in text


def test_transition_result_schema_records_required_semantics() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_one_row_readiness_preflight_transition_result",
        "source_decision: approve_one_row_readiness_preflight_transition_path",
        'source_approved_for_next_transition_step: "true"',
        "source_allowed_next_action: run_one_row_g3sx30_readiness_preflight_transition",
        "transition_action: run_one_row_g3sx30_readiness_preflight_transition",
        "transition_status: one_row_readiness_preflight_transition_passed",
        'one_row_only: "true"',
        'ready_for_preflight: "true"',
        "ready_scope: one_row_g3sx30_elephant_mdm2_only",
        'gate8_promoted: "false"',
        'gate9_promoted: "false"',
        'biological_claim_made: "false"',
        "next_step: add_first_controlled_downstream_use_path_for_one_row_ready_artifact",
    ]:
        assert required in text
