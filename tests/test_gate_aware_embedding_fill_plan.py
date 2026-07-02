from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_gate_aware_embedding_fill_plan_records_statuses() -> None:
    text = read_doc("docs/gate_aware_embedding_fill_plan.md")

    assert "ready_for_preflight" in text
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
    assert "TP53/MDM2 remains a blocked calibration lane" in text
    assert "live embedding fill while coverage remains unresolved" in text


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
