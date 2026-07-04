from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_gate_aware_embedding_fill_plan_records_statuses() -> None:
    text = read_doc("docs/gate_aware_embedding_fill_plan.md")

    assert "ready_for_preflight" in text
    assert "planning_policy_updated_runtime_blocked" in text
    assert "needs_coverage_repair" in text
    assert "needs_source_provenance_review" in text
    assert "defer_until_gate8_ready" in text
    assert "reviewed_for_single_live_fill" in text
    assert "do_not_fill" in text


def test_gate_aware_embedding_fill_plan_keeps_live_calls_opt_in() -> None:
    text = read_doc("docs/gate_aware_embedding_fill_plan.md")

    assert "curated_embedding_preflight" in text
    assert "curated_embedding_single" in text
    assert "--yes-live" in text
    assert "Live Biohub / ESMC calls are never default behavior" in text


def test_gate_aware_embedding_fill_plan_records_lane_policy() -> None:
    text = read_doc("docs/gate_aware_embedding_fill_plan.md")

    assert "SIRT6 is the advanced calibration lane" in text
    assert "TP53/MDM2 remains runtime-blocked for embedding execution" in text
    assert "data/input/ortholog_evidence_gate45_policy_updates.csv#1" in text
    assert "planning-policy-updated but still runtime-blocked" in text
    assert "sequence fetch" in text
    assert "committed `.npy` embedding artifact" in text


def test_gate_aware_embedding_fill_plan_records_claim_guardrails() -> None:
    text = read_doc("docs/gate_aware_embedding_fill_plan.md")

    assert "validated longevity signal" in text
    assert "biological hit" in text
    assert "proven pro-longevity variant" in text
    assert "This is a planning checkpoint only" in text


def test_gate_aware_embedding_fill_plan_points_to_controlled_protocol() -> None:
    text = read_doc("docs/gate_aware_embedding_fill_plan.md")

    assert "docs/controlled_embedding_fill_protocol.md" in text
    assert "Brandt's bat `P09874` live embedding precedent" in text
    assert "no enrichment/contrast rerun by default" in text


def test_gate_aware_embedding_fill_plan_records_g3sx30_checkpoint() -> None:
    text = read_doc("docs/gate_aware_embedding_fill_plan.md")

    assert "## G3SX30 checkpoint" in text
    assert "policy_update_decision=approve_gate45_policy_update_for_planning" in text
    assert (
        "downstream_block_status_after_policy=gate45_policy_updated_still_runtime_blocked" in text
    )
    assert (
        "allowed_next_action_after_policy=prepare_later_gate_aware_embedding_fill_plan_pr" in text
    )
    assert "This checkpoint does not make G3SX30 embedding-ready" in text
    assert "no Biohub / ESMC call" in text
    assert "no embedding generation" in text
    assert "no Gate 8 or Gate 9 promotion" in text
    assert "no biological claim" in text
