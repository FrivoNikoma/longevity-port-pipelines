from __future__ import annotations

import polars as pl

from longevity_port_pipelines.stages.curated_analysis_preflight import (
    DEFAULT_MODEL_NAME,
    build_curated_ortholog_analysis_preflight,
    empty_curated_ortholog_analysis_preflight,
)
from longevity_port_pipelines.stages.embed import embedding_path


def candidate_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
            ],
            "chain": ["receptor", "receptor"],
            "target_species": ["brandts_bat", "brandts_bat"],
            "source_uniprot": ["P09874", "P09874"],
            "source_species_taxid": [9606, 9606],
            "target_species_taxid": [109478, 109478],
            "target_accession": ["EPQ16369.1", "S7NG06"],
            "target_accession_db": ["NCBI Protein", "UniProt"],
            "target_sequence": ["AAAA", "BBBB"],
            "target_sequence_length": [4, 4],
            "curation_status": ["primary_candidate", "supporting_candidate"],
            "evidence_source": ["manual", "manual"],
            "curation_note": ["primary", "supporting"],
        }
    )


def coverage_rows(target_uniprot: str = "EPQ16369.1") -> pl.DataFrame:
    return pl.DataFrame(
        {
            "source_uniprot": ["P09874"],
            "source_species_taxid": [9606],
            "target_uniprot": [target_uniprot],
            "target_species_taxid": [109478],
            "target_sequence": ["AAAA"],
            "is_reviewed": [False],
            "source_db": ["curated:NCBI Protein"],
        }
    )


def write_embedding_placeholder(tmp_path, species_taxid: int) -> None:
    path = embedding_path(
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        species_taxid=species_taxid,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"placeholder")


def test_empty_curated_ortholog_analysis_preflight_has_expected_columns() -> None:
    preflight = empty_curated_ortholog_analysis_preflight()

    assert preflight.is_empty()
    assert "analysis_ready" in preflight.columns
    assert "blocking_reason" in preflight.columns


def test_build_curated_ortholog_analysis_preflight_reports_ready_candidate(tmp_path) -> None:
    write_embedding_placeholder(tmp_path, 9606)
    write_embedding_placeholder(tmp_path, 109478)

    preflight = build_curated_ortholog_analysis_preflight(
        candidate_rows(),
        coverage_rows(),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    assert preflight.height == 1
    row = preflight.row(0, named=True)

    assert row["target_accession"] == "EPQ16369.1"
    assert row["coverage_match_count"] == 1
    assert row["coverage_accession_match_count"] == 1
    assert row["coverage_target_uniprot"] == "EPQ16369.1"
    assert row["coverage_source_db"] == "curated:NCBI Protein"
    assert row["reference_embedding_exists"] is True
    assert row["target_embedding_exists"] is True
    assert row["analysis_ready"] is True
    assert row["blocking_reason"] == "ready"


def test_build_curated_ortholog_analysis_preflight_blocks_missing_target_embedding(
    tmp_path,
) -> None:
    write_embedding_placeholder(tmp_path, 9606)

    preflight = build_curated_ortholog_analysis_preflight(
        candidate_rows(),
        coverage_rows(),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    row = preflight.row(0, named=True)

    assert row["reference_embedding_exists"] is True
    assert row["target_embedding_exists"] is False
    assert row["analysis_ready"] is False
    assert row["blocking_reason"] == "target_embedding_missing"


def test_build_curated_ortholog_analysis_preflight_blocks_accession_mismatch(
    tmp_path,
) -> None:
    write_embedding_placeholder(tmp_path, 9606)
    write_embedding_placeholder(tmp_path, 109478)

    preflight = build_curated_ortholog_analysis_preflight(
        candidate_rows(),
        coverage_rows(target_uniprot="WRONG_ACCESSION"),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    row = preflight.row(0, named=True)

    assert row["coverage_match_count"] == 1
    assert row["coverage_accession_match_count"] == 0
    assert row["analysis_ready"] is False
    assert row["blocking_reason"] == "coverage_accession_mismatch"
