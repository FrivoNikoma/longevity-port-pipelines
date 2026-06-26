from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.models import OrthologMapping
from longevity_port_pipelines.stages.ortholog_inputs import (
    build_curated_ortholog_candidate_coverage,
    build_curated_ortholog_input_validation,
    curated_candidates_to_ortholog_mappings,
    empty_validation,
    filter_active_curated_ortholog_candidates,
    find_duplicate_curated_ortholog_rows,
    find_duplicate_primary_candidate_rows,
    merge_ortholog_mappings,
    ortholog_mapping_key,
    ortholog_mappings_from_frame,
    ortholog_mappings_to_frame,
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


def standard_mapping(
    *,
    target_species_taxid: int = 10090,
    target_uniprot: str = "Q921K2",
    source_db: str = "UniProt",
) -> OrthologMapping:
    return OrthologMapping(
        source_uniprot="P09874",
        source_species_taxid=9606,
        target_uniprot=target_uniprot,
        target_species_taxid=target_species_taxid,
        target_sequence="STANDARD",
        is_reviewed=True,
        source_db=source_db,
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


def test_curated_candidates_to_ortholog_mappings_uses_primary_candidates_only() -> None:
    mappings = curated_candidates_to_ortholog_mappings(candidate_rows())

    assert len(mappings) == 1
    mapping = mappings[0]
    assert mapping.source_uniprot == "P09874"
    assert mapping.source_species_taxid == 9606
    assert mapping.target_uniprot == "EPQ16369.1"
    assert mapping.target_species_taxid == 109478
    assert mapping.target_sequence == "AAAA"
    assert mapping.is_reviewed is False
    assert mapping.source_db == "curated:NCBI Protein"


def test_find_duplicate_primary_candidate_rows_detects_ambiguous_primary_candidates() -> None:
    candidates = candidate_rows().with_columns(
        pl.when(pl.col("target_accession") == "S7NG06")
        .then(pl.lit("primary_candidate"))
        .otherwise(pl.col("curation_status"))
        .alias("curation_status")
    )

    duplicates = find_duplicate_primary_candidate_rows(candidates)

    assert duplicates.height == 1
    assert duplicates.row(0, named=True)["source_uniprot"] == "P09874"
    assert duplicates.row(0, named=True)["target_species_taxid"] == 109478


def test_curated_candidates_to_ortholog_mappings_rejects_ambiguous_primary_candidates() -> None:
    candidates = candidate_rows().with_columns(
        pl.when(pl.col("target_accession") == "S7NG06")
        .then(pl.lit("primary_candidate"))
        .otherwise(pl.col("curation_status"))
        .alias("curation_status")
    )

    with pytest.raises(ValueError, match="Multiple primary curated ortholog candidates"):
        curated_candidates_to_ortholog_mappings(candidates)


def test_ortholog_mapping_key_uses_source_and_target_species() -> None:
    mapping = standard_mapping()

    assert ortholog_mapping_key(mapping) == ("P09874", 9606, 10090)


def test_ortholog_mapping_frame_roundtrip_handles_boolean_strings() -> None:
    frame = pl.DataFrame(
        {
            "source_uniprot": ["P09874"],
            "source_species_taxid": [9606],
            "target_uniprot": ["Q921K2"],
            "target_species_taxid": [10090],
            "target_sequence": ["STANDARD"],
            "is_reviewed": ["true"],
            "source_db": ["UniProt"],
        }
    )

    mappings = ortholog_mappings_from_frame(frame)
    roundtrip = ortholog_mappings_to_frame(mappings)

    assert mappings[0].is_reviewed is True
    assert roundtrip.row(0, named=True)["target_uniprot"] == "Q921K2"


def test_merge_ortholog_mappings_adds_missing_curated_mapping() -> None:
    standard = [standard_mapping(target_species_taxid=10090)]
    curated = curated_candidates_to_ortholog_mappings(candidate_rows())

    merged = merge_ortholog_mappings(standard, curated)

    assert len(merged) == 2
    assert [mapping.target_species_taxid for mapping in merged] == [10090, 109478]


def test_merge_ortholog_mappings_keeps_standard_by_default() -> None:
    standard = [standard_mapping(target_species_taxid=109478, target_uniprot="STANDARD_BAT")]
    curated = curated_candidates_to_ortholog_mappings(candidate_rows())

    merged = merge_ortholog_mappings(standard, curated)

    assert len(merged) == 1
    assert merged[0].target_uniprot == "STANDARD_BAT"
    assert merged[0].source_db == "UniProt"


def test_merge_ortholog_mappings_can_prefer_curated() -> None:
    standard = [standard_mapping(target_species_taxid=109478, target_uniprot="STANDARD_BAT")]
    curated = curated_candidates_to_ortholog_mappings(candidate_rows())

    merged = merge_ortholog_mappings(standard, curated, conflict_policy="prefer_curated")

    assert len(merged) == 1
    assert merged[0].target_uniprot == "EPQ16369.1"
    assert merged[0].source_db == "curated:NCBI Protein"


def test_merge_ortholog_mappings_can_error_on_conflict() -> None:
    standard = [standard_mapping(target_species_taxid=109478, target_uniprot="STANDARD_BAT")]
    curated = curated_candidates_to_ortholog_mappings(candidate_rows())

    with pytest.raises(ValueError, match="conflicts with standard mapping"):
        merge_ortholog_mappings(standard, curated, conflict_policy="error")


def test_merge_ortholog_mappings_rejects_duplicate_standard_mapping_keys() -> None:
    standard = [
        standard_mapping(target_species_taxid=109478, target_uniprot="STANDARD_BAT_1"),
        standard_mapping(target_species_taxid=109478, target_uniprot="STANDARD_BAT_2"),
    ]

    with pytest.raises(ValueError, match="Duplicate standard ortholog mapping key"):
        merge_ortholog_mappings(standard, [])
