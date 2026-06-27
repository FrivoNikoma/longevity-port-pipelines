from __future__ import annotations

import polars as pl

from longevity_port_pipelines.stages.curated_analysis_plan import (
    DEFAULT_MODEL_NAME,
    build_curated_ortholog_analysis_plan,
    empty_curated_ortholog_analysis_plan,
)
from longevity_port_pipelines.stages.embed import embedding_path

COMPLEX_ID = "4xhu__A1_P09874--4xhu__B1_Q9UNS1"


def candidate_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [COMPLEX_ID, COMPLEX_ID],
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


def selection_rows(source_uniprot: str = "P09874") -> pl.DataFrame:
    return pl.DataFrame(
        {
            "pinder_id": [COMPLEX_ID],
            "pdb_id": ["4xhu"],
            "chain_R": ["A"],
            "chain_L": ["B"],
            "receptor_sequence": ["M" * 10],
            "ligand_sequence": ["N" * 5],
            "uniprot_R": [source_uniprot],
            "uniprot_L": ["Q9UNS1"],
        }
    )


def write_embedding_placeholder(tmp_path, species_taxid: int) -> None:
    path = embedding_path(
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
        complex_id=COMPLEX_ID,
        chain="receptor",
        species_taxid=species_taxid,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"placeholder")


def test_empty_curated_ortholog_analysis_plan_has_expected_columns() -> None:
    plan = empty_curated_ortholog_analysis_plan()

    assert plan.is_empty()
    assert "analysis_plan_ready" in plan.columns
    assert "interface_residue_status" in plan.columns


def test_build_curated_ortholog_analysis_plan_reports_ready_candidate(tmp_path) -> None:
    write_embedding_placeholder(tmp_path, 9606)
    write_embedding_placeholder(tmp_path, 109478)

    plan = build_curated_ortholog_analysis_plan(
        candidate_rows(),
        selection_rows(),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    assert plan.height == 1
    row = plan.row(0, named=True)

    assert row["complex_id"] == COMPLEX_ID
    assert row["chain"] == "receptor"
    assert row["selection_match_count"] == 1
    assert row["selection_id_column"] == "pinder_id"
    assert row["pdb_id"] == "4xhu"
    assert row["pdb_chain_R"] == "A"
    assert row["pdb_chain_L"] == "B"
    assert row["chain_sequence_column"] == "receptor_sequence"
    assert row["chain_uniprot_column"] == "uniprot_R"
    assert row["selection_source_uniprot"] == "P09874"
    assert row["reference_sequence_length"] == 10
    assert row["target_sequence_length"] == 4
    assert row["reference_embedding_exists"] is True
    assert row["target_embedding_exists"] is True
    assert row["interface_residue_source"] == "pdb_interface_extraction"
    assert row["interface_residue_status"] == "metadata_present"
    assert row["analysis_plan_ready"] is True
    assert row["blocking_reason"] == "ready"


def test_build_curated_ortholog_analysis_plan_blocks_missing_selection(tmp_path) -> None:
    write_embedding_placeholder(tmp_path, 9606)
    write_embedding_placeholder(tmp_path, 109478)

    plan = build_curated_ortholog_analysis_plan(
        candidate_rows(),
        selection_rows().filter(pl.col("pinder_id") != COMPLEX_ID),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    row = plan.row(0, named=True)

    assert row["selection_match_count"] == 0
    assert row["analysis_plan_ready"] is False
    assert "selection_missing" in row["blocking_reason"]


def test_build_curated_ortholog_analysis_plan_blocks_uniprot_mismatch(tmp_path) -> None:
    write_embedding_placeholder(tmp_path, 9606)
    write_embedding_placeholder(tmp_path, 109478)

    plan = build_curated_ortholog_analysis_plan(
        candidate_rows(),
        selection_rows(source_uniprot="WRONG"),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    row = plan.row(0, named=True)

    assert row["selection_source_uniprot"] == "WRONG"
    assert row["analysis_plan_ready"] is False
    assert "selection_source_uniprot_mismatch" in row["blocking_reason"]


def test_build_curated_ortholog_analysis_plan_blocks_missing_interface_metadata(
    tmp_path,
) -> None:
    write_embedding_placeholder(tmp_path, 9606)
    write_embedding_placeholder(tmp_path, 109478)

    plan = build_curated_ortholog_analysis_plan(
        candidate_rows(),
        selection_rows().drop("chain_L"),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    row = plan.row(0, named=True)

    assert row["interface_residue_status"] == "metadata_missing"
    assert row["analysis_plan_ready"] is False
    assert "interface_metadata_missing" in row["blocking_reason"]


def test_build_curated_ortholog_analysis_plan_blocks_missing_target_embedding(
    tmp_path,
) -> None:
    write_embedding_placeholder(tmp_path, 9606)

    plan = build_curated_ortholog_analysis_plan(
        candidate_rows(),
        selection_rows(),
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
    )

    row = plan.row(0, named=True)

    assert row["reference_embedding_exists"] is True
    assert row["target_embedding_exists"] is False
    assert row["analysis_plan_ready"] is False
    assert "target_embedding_missing" in row["blocking_reason"]
