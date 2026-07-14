from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/tp53_mdm2_first_interface_ready_manifest_result.md"
SCHEMA = ROOT / "data/config/tp53_mdm2_first_interface_ready_manifest_result_schema.yaml"


def test_interface_ready_manifest_doc_and_schema_exist() -> None:
    assert DOC.exists()
    assert SCHEMA.exists()


def test_doc_records_exact_human_reference_and_chains() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "structure id = 1YCR" in text
    assert "MDM2 chain = A" in text
    assert "MDM2 UniProt = Q00987" in text
    assert "TP53 chain = B" in text
    assert "TP53 UniProt = P04637" in text
    assert "Exact human reference and partner context" in text


def test_doc_records_interface_source_without_scoring() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "interface.py::extract_interface_residues" in text
    assert "distance cutoff = 8.0 angstrom" in text
    assert "zero-based chain-local residue indices" in text
    assert "No residue list is extracted" in text
    assert "no interface score is computed" in text


def test_doc_records_elephant_mapping_state_without_invention() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "target accession = G3SX30" in text
    assert "mapping status = reviewed_sequence_provenance" in text
    assert "target accession = unresolved" in text
    assert "blocked_pending_source_ortholog_provenance" in text
    assert "does not invent an elephant TP53 accession" in text


def test_doc_records_structure_confidence_and_claim_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "does not use pLDDT, PAE, AF3 confidence" in text
    assert "do_not_auto_classify_breakage_as_incompatibility" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "makes no biological claim" in text


def test_doc_records_next_result_bearing_action() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "add_first_tp53_mdm2_human_reference_interface_residue_extraction_result" in text
    assert "No preflight-only, inventory-only, plan-only" in text
