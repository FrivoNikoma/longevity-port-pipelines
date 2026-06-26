from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.ortholog_inputs import (
    build_curated_ortholog_candidate_coverage,
    build_curated_ortholog_input_validation,
    empty_validation,
    filter_active_curated_ortholog_candidates,
    find_duplicate_curated_ortholog_rows,
    validate_schema,
)


def expected_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["4xhu__A1_P09874--4xhu__B1_Q9UNS1", "c2"],
            "chain": ["receptor", "receptor"],
            "target_species": ["brandts_bat", "bowhead_whale"],
            "source_uniprot": ["P09874", "P09874"],
        }
    )


def candidate_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "c2",
            ],
            "chain": ["receptor", "receptor", "receptor", "receptor"],
            "target_species": ["brandts_bat", "brandts_bat", "brandts_bat", "bowhead_whale"],
            "source_uniprot": ["P09874", "P09874", "P09874", "P09874"],
            "source_species_taxid": [9606, 9606, 9606, 9606],
            "target_species_taxid": [109478, 109478, 109478, 27622],
            "target_accession": ["EPQ16369.1", "S7NG06", "S7MYH2", "XP_036133328.1"],
            "target_accession_db": ["NCBI Protein", "UniProt", "UniProt", "NCBI Protein"],
            "target_sequence": ["AAAA", "BBBB", "CCCC", ""],
            "target_sequence_length": [4, 4, 4, 0],
            "curation_status": [
                "primary_candidate",
                "supporting_candidate",
                "rejected_candidate",
                "primary_candidate",
            ],
            "evidence_source": [
                "local_broad_probe",
                "local_broad_probe",
                "local_broad_probe",
                "local_exact_taxid_probe",
            ],
            "curation_note": [
                "PARP1-specific Brandt's bat candidate.",
                "Same-length UniProt Brandt's bat cross-check.",
                "Rejected CHD1L / chromatin remodeler hit.",
                "Rejected because sequence/header evidence is missing or unsafe.",
            ],
        }
    )


def test_validate_schema_accepts_required_columns() -> None:
    validate_schema(candidate_rows())


def test_validate_schema_rejects_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_schema(pl.DataFrame({"complex_id": ["c1"]}))


def test_empty_validation_marks_all_expected_rows_missing_input_file() -> None:
    validation = empty_validation(expected_rows())

    assert validation.height == 2
    assert set(validation["input_status"].to_list()) == {"missing_input_file"}
    assert set(validation["has_curated_ortholog_candidate"].to_list()) == {False}


def test_filter_active_curated_ortholog_candidates_requires_active_status_and_sequence() -> None:
    active = filter_active_curated_ortholog_candidates(candidate_rows())

    assert active.height == 2
    assert active["target_accession"].to_list() == ["EPQ16369.1", "S7NG06"]


def test_build_curated_ortholog_candidate_coverage_counts_active_candidates() -> None:
    coverage = build_curated_ortholog_candidate_coverage(candidate_rows())

    row = coverage.filter(
        (pl.col("complex_id") == "4xhu__A1_P09874--4xhu__B1_Q9UNS1")
        & (pl.col("chain") == "receptor")
        & (pl.col("target_species") == "brandts_bat")
        & (pl.col("source_uniprot") == "P09874")
    ).row(0, named=True)

    assert row["n_curated_ortholog_candidates"] == 2
    assert row["target_accessions"] == "EPQ16369.1;S7NG06"
    assert row["target_accession_dbs"] == "NCBI Protein;UniProt"


def test_build_curated_ortholog_input_validation_marks_present_and_missing_rows() -> None:
    validation = build_curated_ortholog_input_validation(expected_rows(), candidate_rows())

    brandts_bat = validation.filter(pl.col("target_species") == "brandts_bat").row(0, named=True)
    bowhead = validation.filter(pl.col("target_species") == "bowhead_whale").row(0, named=True)

    assert brandts_bat["n_curated_ortholog_candidates"] == 2
    assert brandts_bat["has_curated_ortholog_candidate"] is True
    assert brandts_bat["input_status"] == "has_curated_ortholog_candidate"

    assert bowhead["n_curated_ortholog_candidates"] == 0
    assert bowhead["has_curated_ortholog_candidate"] is False
    assert bowhead["input_status"] == "missing_curated_ortholog_candidate"


def test_build_curated_ortholog_input_validation_handles_missing_candidate_file() -> None:
    validation = build_curated_ortholog_input_validation(expected_rows(), None)

    assert set(validation["input_status"].to_list()) == {"missing_input_file"}


def test_find_duplicate_curated_ortholog_rows() -> None:
    candidates = pl.concat([candidate_rows(), candidate_rows().head(1)], how="vertical")
    duplicates = find_duplicate_curated_ortholog_rows(candidates)

    assert duplicates.height == 1
    assert duplicates.row(0, named=True)["target_accession"] == "EPQ16369.1"
    assert duplicates.row(0, named=True)["len"] == 2
