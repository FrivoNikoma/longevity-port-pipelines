from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts import record_sirt6_8g57_result as result

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_committed_sirt6_8g57_result_validates() -> None:
    mapped_rows, baseline_rows, disposition = result.validate_committed(REPO_ROOT)

    assert len(mapped_rows) == 5
    assert len(baseline_rows) == 5
    assert disposition["scientific_classification"] == (
        "sequence_divergence_confounding_not_resolved"
    )
    assert disposition["lane_status"] == "closed_pending_divergence_decoupling_species"


def test_committed_result_preserves_raw_ordering() -> None:
    mapped_rows, _, _ = result.validate_committed(REPO_ROOT)
    long_values = [
        float(row["enrichment_ratio"])
        for row in mapped_rows
        if row["lifespan_category"] == "long_lived"
    ]
    short_values = [
        float(row["enrichment_ratio"])
        for row in mapped_rows
        if row["lifespan_category"] == "short_lived_control"
    ]

    assert min(long_values) > max(short_values)


def test_canonical_hash_is_line_ending_invariant(tmp_path: Path) -> None:
    source = REPO_ROOT / result.RESULT_TABLE
    copy = tmp_path / source.name
    copy.write_bytes(source.read_text(encoding="utf-8").replace("\n", "\r\n").encode())

    contract = json.loads((REPO_ROOT / result.CONTRACT_PATH).read_text(encoding="utf-8"))
    assert (
        result.canonical_text_sha256(copy)
        == contract["tables"]["mapped_interface"]["canonical_text_sha256"]
    )


def test_committed_mutation_is_rejected(tmp_path: Path) -> None:
    result_source = REPO_ROOT / result.RESULT_TABLE
    baseline_source = REPO_ROOT / result.BASELINE_TABLE
    disposition_source = REPO_ROOT / result.DISPOSITION_TABLE
    contract_source = REPO_ROOT / result.CONTRACT_PATH

    result_copy = tmp_path / result_source.name
    baseline_copy = tmp_path / baseline_source.name
    disposition_copy = tmp_path / disposition_source.name
    contract_copy = tmp_path / contract_source.name

    result_copy.write_text(result_source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    baseline_copy.write_bytes(baseline_source.read_bytes())
    disposition_copy.write_bytes(disposition_source.read_bytes())
    contract_copy.write_bytes(contract_source.read_bytes())

    with pytest.raises(ValueError, match="hash mismatch"):
        result.validate_committed(
            REPO_ROOT,
            contract_path=contract_copy,
            result_path=result_copy,
            baseline_path=baseline_copy,
            disposition_path=disposition_copy,
        )


def test_documentation_keeps_claim_boundaries() -> None:
    text = (REPO_ROOT / result.DOC_PATH).read_text(encoding="utf-8")
    flattened = " ".join(text.split())

    assert "sequence_divergence_confounding_not_resolved" in text
    assert "not a phylogenetic correction" in flattened
    assert "does not establish altered SIRT6-nucleosome binding affinity" in flattened
