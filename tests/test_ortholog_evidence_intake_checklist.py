from __future__ import annotations

from pathlib import Path

DOC_PATH = Path("docs/ortholog_evidence_intake_checklist.md")


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_ortholog_evidence_intake_checklist_exists() -> None:
    text = read_doc()
    assert text.startswith("# Ortholog evidence intake checklist")
    assert "accession-level ortholog evidence" in text
    assert "Gate 4 / Gate 5 repair-queue worklist item" in text


def test_ortholog_evidence_intake_checklist_records_required_identity_fields() -> None:
    text = read_doc()

    for field in [
        "candidate_set",
        "lane_name",
        "candidate_id",
        "source_table",
        "source_row_index",
        "gene_symbol",
        "source_species",
        "target_species",
        "target_species_taxid",
        "source_uniprot",
        "partner_uniprot",
        "target_uniprot_before_review",
        "coverage_status_before_review",
        "provenance_status_before_review",
        "repair_queue_status_before_review",
        "downstream_block_status_before_review",
        "allowed_next_action_before_review",
        "claim_policy_before_review",
    ]:
        assert field in text


def test_ortholog_evidence_intake_checklist_records_minimum_evidence_fields() -> None:
    text = read_doc()

    for phrase in [
        "evidence source type",
        "source database",
        "source accession or stable identifier",
        "target taxid",
        "target species name",
        "target gene or protein symbol",
        "target protein accession",
        "sequence length",
        "evidence URI or reproducible lookup note",
        "reviewer note",
        "ambiguity flag",
        "whether a second reviewer is required",
    ]:
        assert phrase in text


def test_ortholog_evidence_intake_checklist_matches_acceptable_sources() -> None:
    text = read_doc()

    for source in [
        "reviewed UniProt entry",
        "UniProt ortholog or taxonomy evidence",
        "NCBI protein or gene record",
        "Ensembl orthology evidence",
        "OMA orthology evidence",
        "OrthoDB orthology evidence",
        "primary literature with accession-level evidence",
        "project curated table with source accession and reviewer note",
    ]:
        assert source in text


def test_ortholog_evidence_intake_checklist_rejects_insufficient_sources() -> None:
    text = read_doc()

    for source in [
        "model output without accession-level provenance",
        "embedding similarity alone",
        "sequence similarity without species or taxid provenance",
        "LLM generated assertion without external source evidence",
        "filename or local cache path without source provenance",
        "candidate name without accession evidence",
        "downstream enrichment result",
        "Boltz, AF3, Chai, or cofolding result",
        "biological narrative without source accession evidence",
    ]:
        assert source in text


def test_ortholog_evidence_intake_checklist_has_conservative_outcomes() -> None:
    text = read_doc()

    for outcome in [
        "evidence_ready_for_review_decision",
        "evidence_insufficient_defer",
        "evidence_conflict_reject_or_exclude",
        "evidence_ambiguous_needs_second_reviewer",
        "accepted_for_planning_after_review",
        "deferred_pending_source",
        "rejected_after_review",
        "needs_second_reviewer",
    ]:
        assert outcome in text

    assert "These are intake outcomes, not downstream permissions" in text


def test_ortholog_evidence_intake_checklist_preserves_guardrails() -> None:
    text = read_doc()

    for phrase in [
        "does not fetch sequences",
        "does not curate orthologs automatically",
        "does not call Biohub",
        "does not generate embeddings",
        "does not call Boltz",
        "does not rerun enrichment or contrast",
        "does not promote Gate 8",
        "does not promote Gate 9",
        "does not make biological claims",
    ]:
        assert phrase in text


def test_ortholog_evidence_intake_checklist_forbids_downstream_claim_language() -> None:
    text = read_doc()

    for phrase in [
        "validated ortholog",
        "validated longevity signal",
        "validated biological hit",
        "confirmed binding change",
        "confirmed functional effect",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "embedding ready",
        "Boltz ready",
        "safe to port",
        "proven pro-longevity variant",
    ]:
        assert phrase in text


def test_ortholog_evidence_intake_checklist_mentions_current_lanes_without_claims() -> None:
    text = read_doc()

    assert "SIRT6/core3 repair rows" in text
    assert "TP53/MDM2 elephant repair rows" in text
    assert "beneficial-breakage logic" in text
    assert "This checklist does not evaluate that hypothesis" in text
