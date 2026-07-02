from pathlib import Path

GUIDE = Path("docs/generic_repair_queue_usage_guide.md")


def read_guide() -> str:
    return GUIDE.read_text(encoding="utf-8")


def test_generic_repair_queue_usage_guide_exists() -> None:
    assert GUIDE.exists()


def test_generic_repair_queue_usage_guide_documents_command_and_inputs() -> None:
    text = read_guide()

    assert "uv run generic-repair-queue-summary" in text
    assert "data/interim/generic_repair_queue_summary.csv" in text
    assert "data/input/sirt6_candidate_coverage_repair_decisions.csv" in text
    assert "data/input/tp53_mdm2_ortholog_repair_decisions.csv" in text
    assert "11 SIRT6/core3 repair rows" in text
    assert "2 TP53/MDM2 elephant repair rows" in text
    assert "13 total repair queue rows" in text


def test_generic_repair_queue_usage_guide_explains_blocker_fields() -> None:
    text = read_guide()

    assert "repair_queue_status" in text
    assert "downstream_block_status" in text
    assert "allowed_next_action" in text
    assert "blocked_pending_manual_review" in text
    assert "blocked_pending_source_ortholog_repair" in text
    assert "blocked_gate4_gate5" in text
    assert "manual_sequence_provenance_review" in text
    assert "fetch_or_curate_source_ortholog" in text
    assert "repair-planning actions only" in text
    assert "They do not automatically perform repair" in text


def test_generic_repair_queue_usage_guide_forbids_biological_interpretations() -> None:
    text = read_guide()

    assert "validated longevity signal" in text
    assert "validated biological hit" in text
    assert "confirmed binding change" in text
    assert "confirmed functional effect" in text
    assert "validated ortholog table" in text
    assert "permission to run Gate 8 contrast" in text
    assert "permission to run Gate 9 cofolding readiness" in text
    assert "permission to run live structural compatibility calls" in text


def test_generic_repair_queue_usage_guide_forbids_runtime_actions() -> None:
    text = read_guide()

    assert "sequence fetch" in text
    assert "manual ortholog curation" in text
    assert "Biohub calls" in text
    assert "embedding generation" in text
    assert "Boltz calls" in text
    assert "enrichment reruns" in text
    assert "contrast reruns" in text
    assert "Gate 8 promotion" in text
    assert "Gate 9 promotion" in text
    assert "biological claims" in text


def test_generic_repair_queue_usage_guide_keeps_downstream_gates_blocked() -> None:
    text = read_guide()

    assert "Keep downstream gates blocked" in text
    assert "explicit ortholog/provenance evidence is reviewed" in text
    assert "makes blockers visible" in text
    assert "does not remove those blockers" in text
