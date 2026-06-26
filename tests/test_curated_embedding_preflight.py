from __future__ import annotations

import polars as pl

from longevity_port_pipelines.stages.curated_embedding_preflight import (
    DEFAULT_MODEL_NAME,
    build_curated_ortholog_embedding_preflight,
    canonical_embedding_path,
    empty_curated_ortholog_embedding_preflight,
)


def candidate_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
            ],
            "chain": ["receptor", "receptor", "receptor"],
            "target_species": ["brandts_bat", "brandts_bat", "brandts_bat"],
            "source_uniprot": ["P09874", "P09874", "P09874"],
            "source_species_taxid": [9606, 9606, 9606],
            "target_species_taxid": [109478, 109478, 109478],
            "target_accession": ["EPQ16369.1", "S7NG06", "S7MYH2"],
            "target_accession_db": ["NCBI Protein", "UniProt", "UniProt"],
            "target_sequence": ["AAAA", "BBBB", "CCCC"],
            "target_sequence_length": [4, 4, 4],
            "curation_status": ["primary_candidate", "supporting_candidate", "rejected_candidate"],
            "evidence_source": ["manual", "manual", "manual"],
            "curation_note": ["primary", "supporting", "rejected"],
        }
    )


def test_empty_curated_ortholog_embedding_preflight_has_expected_columns() -> None:
    preflight = empty_curated_ortholog_embedding_preflight()

    assert preflight.is_empty()
    assert "embedding_status" in preflight.columns
    assert "embedding_path" in preflight.columns


def test_build_curated_ortholog_embedding_preflight_reports_missing_primary_candidate(
    tmp_path,
) -> None:
    preflight = build_curated_ortholog_embedding_preflight(
        candidate_rows(),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    assert preflight.height == 1
    row = preflight.row(0, named=True)

    expected_path = canonical_embedding_path(
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        species_taxid=109478,
    )

    assert row["target_accession"] == "EPQ16369.1"
    assert row["target_accession_db"] == "NCBI Protein"
    assert row["embedding_path"] == str(expected_path)
    assert row["embedding_exists"] is False
    assert row["embedding_status"] == "missing"
    assert row["sequence_length_status"] == "matches"


def test_build_curated_ortholog_embedding_preflight_reports_present_primary_candidate(
    tmp_path,
) -> None:
    path = canonical_embedding_path(
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        species_taxid=109478,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"placeholder")

    preflight = build_curated_ortholog_embedding_preflight(
        candidate_rows(),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    row = preflight.row(0, named=True)

    assert row["embedding_exists"] is True
    assert row["embedding_status"] == "present"


def test_build_curated_ortholog_embedding_preflight_flags_length_mismatch(tmp_path) -> None:
    candidates = candidate_rows().with_columns(
        pl.when(pl.col("target_accession") == "EPQ16369.1")
        .then(pl.lit(5))
        .otherwise(pl.col("target_sequence_length"))
        .alias("target_sequence_length")
    )

    preflight = build_curated_ortholog_embedding_preflight(
        candidates,
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    row = preflight.row(0, named=True)

    assert row["target_sequence_length"] == 5
    assert row["actual_sequence_length"] == 4
    assert row["sequence_length_status"] == "mismatch"
