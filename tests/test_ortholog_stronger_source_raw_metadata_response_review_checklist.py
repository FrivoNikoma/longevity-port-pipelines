from __future__ import annotations

from pathlib import Path

DOC_PATH = Path("docs/ortholog_stronger_source_raw_metadata_response_review_checklist.md")
GATE_MAP_PATH = Path("docs/current_gate_map.md")


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def read_gate_map() -> str:
    return GATE_MAP_PATH.read_text(encoding="utf-8")


def test_raw_metadata_response_review_checklist_exists() -> None:
    text = read_doc()

    assert text.startswith("# Ortholog stronger-source raw metadata response review checklist")
    assert "raw metadata response review" in text
    assert "before the first real metadata ingestion sandbox" in text


def test_raw_metadata_response_review_checklist_records_required_identity_fields() -> None:
    text = read_doc()

    for field in [
        "candidate_set",
        "lane_name",
        "candidate_id",
        "request_table",
        "request_source_row_index",
        "gene_symbol",
        "source_species",
        "target_species",
        "target_species_taxid",
        "source_uniprot",
        "partner_uniprot",
        "requested_evidence_source_database",
        "requested_evidence_source_accession",
        "planned_lookup_source_type",
        "planned_lookup_source_name",
        "planned_lookup_query_identifier",
        "planned_lookup_query_taxid",
        "live_lookup_policy_decision",
        "dry_run_status",
        "dry_run_provider_mode",
        "raw_metadata_status",
        "raw_metadata_response_status",
        "raw_metadata_review_status",
        "raw_metadata_source_type",
        "raw_metadata_source_name",
        "raw_metadata_source_identifier",
        "raw_metadata_payload_ref",
    ]:
        assert field in text


def test_raw_metadata_response_review_checklist_records_dry_run_guardrail() -> None:
    text = read_doc()

    for phrase in [
        "dry-run-derived raw metadata response != real external database metadata",
        "dry-run-derived raw metadata response != source evidence",
        "dry-run-derived raw metadata response != reviewed ortholog decision",
        "dry-run-derived raw metadata response != Gate 4 / Gate 5 policy update",
        "dry-run-derived raw metadata response != Gate 8 or Gate 9 input",
        "dry-run-derived raw metadata response != biological claim",
    ]:
        assert phrase in text


def test_raw_metadata_response_review_checklist_records_review_outcomes() -> None:
    text = read_doc()

    for outcome in [
        "raw_metadata_ready_for_source_evidence_intake_later",
        "raw_metadata_insufficient_keep_blocked",
        "raw_metadata_conflict_keep_blocked_or_exclude_later",
        "raw_metadata_ambiguous_needs_second_reviewer",
        "dry_run_metadata_non_evidence_keep_blocked",
    ]:
        assert outcome in text

    assert "These are review outcomes only" in text


def test_raw_metadata_response_review_checklist_rejects_insufficient_sources() -> None:
    text = read_doc()

    for source in [
        "dry-run fake/noop provider output",
        "model output without accession-level provenance",
        "embedding similarity alone",
        "LLM-generated assertion without external source evidence",
        "downstream enrichment result",
        "Boltz, AF3, Chai, or cofolding result",
        "biological narrative without source accession evidence",
    ]:
        assert source in text


def test_raw_metadata_response_review_checklist_preserves_downstream_guardrails() -> None:
    text = read_doc()

    for phrase in [
        "does not fetch sequences",
        "does not create source evidence",
        "does not create manual review rows",
        "does not create reviewed ortholog decisions",
        "does not update Gate 4 / Gate 5",
        "does not promote Gate 8",
        "does not promote Gate 9",
        "does not call Biohub",
        "does not generate embeddings",
        "does not call Boltz, AF3, or Chai",
        "does not make biological claims",
    ]:
        assert phrase in text


def test_raw_metadata_response_review_checklist_names_next_metadata_sandbox() -> None:
    text = read_doc()

    assert "Add first real metadata ingestion sandbox for G3SX30" in text
    assert "G3SX30 only" in text
    assert "metadata only" in text
    assert "explicit live opt-in" in text
    assert "no sequence fetch" in text
    assert "no source evidence auto-creation" in text
    assert "no reviewed decision" in text
    assert "no Gate 4 / Gate 5 update" in text
    assert "no Gate 8 / Gate 9" in text
    assert "no embeddings" in text
    assert "no Boltz" in text
    assert "no biological claim" in text


def test_current_gate_map_records_raw_metadata_response_review_checklist() -> None:
    text = read_gate_map()

    assert "docs/ortholog_stronger_source_raw_metadata_response_review_checklist.md" in text
    assert (
        "raw metadata response review checklist status: `docs_only_human_review_protocol`" in text
    )
    assert "raw metadata response review checklist does not create source evidence" in text
    assert "first real metadata ingestion sandbox for G3SX30" in text
