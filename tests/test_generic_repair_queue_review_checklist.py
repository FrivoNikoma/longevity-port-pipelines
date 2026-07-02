from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_generic_repair_queue_review_checklist_records_blocker_first_semantics() -> None:
    text = read_doc("docs/generic_repair_queue_review_checklist.md")
    assert "blocker-first worklist" in text
    assert "An unreviewed row is not an invalid row" in text
    assert "valid blocked repair-queue item" in text
    assert "unreviewed Gate 4 / Gate 5 blocker" in text
    assert "reviewed-for-planning provenance evidence" in text


def test_generic_repair_queue_review_checklist_records_current_scope() -> None:
    text = read_doc("docs/generic_repair_queue_review_checklist.md")
    assert "data/input/sirt6_candidate_coverage_repair_decisions.csv" in text
    assert "data/input/tp53_mdm2_ortholog_repair_decisions.csv" in text
    assert "11 SIRT6/core3 repair rows" in text
    assert "2 TP53/MDM2 elephant repair rows" in text
    assert "13 total repair queue rows" in text


def test_generic_repair_queue_review_checklist_records_required_identifiers() -> None:
    text = read_doc("docs/generic_repair_queue_review_checklist.md")
    for field in [
        "candidate_set",
        "candidate_id",
        "lane_name",
        "source_table",
        "source_row_index",
        "target_species",
        "target_species_taxid",
        "source_uniprot",
        "target_uniprot_before_review",
        "repair_queue_status_before_review",
        "downstream_block_status_before_review",
    ]:
        assert field in text


def test_generic_repair_queue_review_checklist_records_evidence_boundaries() -> None:
    text = read_doc("docs/generic_repair_queue_review_checklist.md")
    for allowed_source in [
        "reviewed UniProt entry",
        "NCBI protein or gene record with species and taxid",
        "Ensembl orthology evidence",
        "OMA orthology evidence",
        "OrthoDB orthology evidence",
    ]:
        assert allowed_source in text
    for forbidden_source in [
        "model output without accession-level provenance",
        "embedding similarity alone",
        "LLM-generated assertion without external source evidence",
        "a downstream enrichment result",
        "a Boltz, AF3, Chai, or cofolding result",
    ]:
        assert forbidden_source in text


def test_generic_repair_queue_review_checklist_records_review_decisions() -> None:
    text = read_doc("docs/generic_repair_queue_review_checklist.md")
    for decision in [
        "accepted_for_planning_after_review",
        "rejected_after_review",
        "deferred_pending_source",
        "needs_second_reviewer",
    ]:
        assert decision in text
    assert (
        "this provenance blocker has reviewed evidence that may support a later "
        "explicit Gate 4 / Gate 5 policy update"
    ) in text


def test_generic_repair_queue_review_checklist_keeps_downstream_blocked() -> None:
    text = read_doc("docs/generic_repair_queue_review_checklist.md")
    for blocked_action in [
        "Gate 8 contrast",
        "Gate 9 cofolding readiness",
        "live structural compatibility",
        "decision-package promotion",
    ]:
        assert blocked_action in text
    for claim in [
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "validated ortholog",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert claim in text
