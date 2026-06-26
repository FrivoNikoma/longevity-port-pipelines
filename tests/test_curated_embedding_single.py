from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.curated_embedding_single import (
    build_single_curated_embedding_plan,
    run_single_curated_embedding,
    select_single_primary_curated_candidate,
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


def test_select_single_primary_curated_candidate_returns_exact_primary_row() -> None:
    row = select_single_primary_curated_candidate(
        candidate_rows(),
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        target_species_taxid=109478,
    )

    assert row["target_accession"] == "EPQ16369.1"
    assert row["curation_status"] == "primary_candidate"


def test_select_single_primary_curated_candidate_rejects_missing_row() -> None:
    with pytest.raises(ValueError, match="No primary curated ortholog candidate"):
        select_single_primary_curated_candidate(
            candidate_rows(),
            complex_id="missing",
            chain="receptor",
            target_species_taxid=109478,
        )


def test_select_single_primary_curated_candidate_rejects_multiple_primary_rows() -> None:
    candidates = candidate_rows().with_columns(
        pl.when(pl.col("target_accession") == "S7NG06")
        .then(pl.lit("primary_candidate"))
        .otherwise(pl.col("curation_status"))
        .alias("curation_status")
    )

    with pytest.raises(ValueError, match="Multiple primary curated ortholog candidates"):
        select_single_primary_curated_candidate(
            candidates,
            complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
            chain="receptor",
            target_species_taxid=109478,
        )


def test_build_single_curated_embedding_plan_reports_missing_expected_path(tmp_path) -> None:
    plan = build_single_curated_embedding_plan(
        candidate_rows(),
        output_dir=tmp_path,
        model_name="esmc-300m-2024-12",
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        target_species_taxid=109478,
    )

    expected = (
        tmp_path
        / "embeddings"
        / "esmc-300m-2024-12"
        / "4xhu__A1_P09874--4xhu__B1_Q9UNS1_receptor_109478.npy"
    )

    assert plan.target_accession == "EPQ16369.1"
    assert plan.embedding_path == expected
    assert plan.embedding_exists is False
    assert plan.sequence_length_status == "matches"


def test_run_single_curated_embedding_is_dry_run_by_default(tmp_path) -> None:
    plan = build_single_curated_embedding_plan(
        candidate_rows(),
        output_dir=tmp_path,
        model_name="esmc-300m-2024-12",
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        target_species_taxid=109478,
    )

    result = run_single_curated_embedding(
        plan,
        output_dir=tmp_path,
        api_url="https://biohub.ai",
        yes_live=False,
    )

    assert result.status == "dry_run_missing"
    assert not plan.embedding_path.exists()


def test_run_single_curated_embedding_skips_existing_file_when_requested(tmp_path) -> None:
    plan = build_single_curated_embedding_plan(
        candidate_rows(),
        output_dir=tmp_path,
        model_name="esmc-300m-2024-12",
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        target_species_taxid=109478,
    )
    plan.embedding_path.parent.mkdir(parents=True, exist_ok=True)
    plan.embedding_path.write_bytes(b"placeholder")

    refreshed_plan = build_single_curated_embedding_plan(
        candidate_rows(),
        output_dir=tmp_path,
        model_name="esmc-300m-2024-12",
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        target_species_taxid=109478,
    )

    result = run_single_curated_embedding(
        refreshed_plan,
        output_dir=tmp_path,
        api_url="https://biohub.ai",
        yes_live=True,
        skip_existing=True,
    )

    assert result.status == "skipped_existing"


def test_run_single_curated_embedding_refuses_live_length_mismatch(tmp_path) -> None:
    candidates = candidate_rows().with_columns(
        pl.when(pl.col("target_accession") == "EPQ16369.1")
        .then(pl.lit(5))
        .otherwise(pl.col("target_sequence_length"))
        .alias("target_sequence_length")
    )
    plan = build_single_curated_embedding_plan(
        candidates,
        output_dir=tmp_path,
        model_name="esmc-300m-2024-12",
        complex_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        chain="receptor",
        target_species_taxid=109478,
    )

    with pytest.raises(ValueError, match="Refusing live embedding"):
        run_single_curated_embedding(
            plan,
            output_dir=tmp_path,
            api_url="https://biohub.ai",
            yes_live=True,
        )
