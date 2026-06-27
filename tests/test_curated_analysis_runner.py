from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

import longevity_port_pipelines.stages.curated_analysis_runner as runner_mod
from longevity_port_pipelines.stages.curated_analysis_runner import (
    DEFAULT_MODEL_NAME,
    empty_curated_ortholog_analysis_runner_report,
    run_curated_ortholog_analysis_runner,
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


def write_embedding_array(tmp_path, species_taxid: int, length: int) -> None:
    path = embedding_path(
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
        complex_id=COMPLEX_ID,
        chain="receptor",
        species_taxid=species_taxid,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, np.ones((length, 3), dtype=np.float32))


def test_empty_curated_ortholog_analysis_runner_report_has_expected_columns() -> None:
    report = empty_curated_ortholog_analysis_runner_report()

    assert report.is_empty()
    assert "status" in report.columns
    assert "reference_embedding_loaded" in report.columns
    assert "interface_residue_count" in report.columns


def test_curated_ortholog_analysis_runner_dry_run_reports_ready_plan(tmp_path) -> None:
    write_embedding_array(tmp_path, 9606, 10)
    write_embedding_array(tmp_path, 109478, 4)

    report = run_curated_ortholog_analysis_runner(
        candidate_rows(),
        selection_rows(),
        output_dir=tmp_path,
        pdb_dir=tmp_path / "pdb",
        model_name=DEFAULT_MODEL_NAME,
        yes_run=False,
    )

    assert report.height == 1
    row = report.row(0, named=True)

    assert row["run_mode"] == "dry-run"
    assert row["analysis_plan_ready"] is True
    assert row["reference_embedding_loaded"] is False
    assert row["target_embedding_loaded"] is False
    assert row["status"] == "dry_run_ready"
    assert row["blocking_reason"] == "ready"


def test_curated_ortholog_analysis_runner_dry_run_reports_blocked_plan(tmp_path) -> None:
    report = run_curated_ortholog_analysis_runner(
        candidate_rows(),
        selection_rows().filter(pl.col("pinder_id") != COMPLEX_ID),
        output_dir=tmp_path,
        pdb_dir=tmp_path / "pdb",
        model_name=DEFAULT_MODEL_NAME,
        yes_run=False,
    )

    row = report.row(0, named=True)

    assert row["run_mode"] == "dry-run"
    assert row["analysis_plan_ready"] is False
    assert row["status"] == "blocked_plan"
    assert "selection_missing" in row["blocking_reason"]


def test_curated_ortholog_analysis_runner_yes_run_loads_embeddings_and_interface(
    tmp_path,
    monkeypatch,
) -> None:
    write_embedding_array(tmp_path, 9606, 10)
    write_embedding_array(tmp_path, 109478, 4)

    def fake_download_pdb(pdb_id: str, dest_dir: Path) -> Path:
        path = dest_dir / f"{pdb_id}.pdb"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fake pdb")
        return path

    def fake_extract_interface_residues(
        pdb_path: Path,
        chain_id_r: str,
        chain_id_l: str,
        distance_cutoff: float = 8.0,
    ) -> tuple[list[int], list[int]]:
        return [1, 2, 3], [4]

    monkeypatch.setattr(runner_mod, "download_pdb", fake_download_pdb)
    monkeypatch.setattr(runner_mod, "extract_interface_residues", fake_extract_interface_residues)

    report = run_curated_ortholog_analysis_runner(
        candidate_rows(),
        selection_rows(),
        output_dir=tmp_path,
        pdb_dir=tmp_path / "pdb",
        model_name=DEFAULT_MODEL_NAME,
        yes_run=True,
    )

    row = report.row(0, named=True)

    assert row["run_mode"] == "yes-run"
    assert row["reference_embedding_loaded"] is True
    assert row["target_embedding_loaded"] is True
    assert row["reference_embedding_shape"] == "10x3"
    assert row["target_embedding_shape"] == "4x3"
    assert row["interface_residue_count"] == 3
    assert row["interface_residue_status"] == "present"
    assert row["status"] == "run_ready"
    assert row["blocking_reason"] == "ready"


def test_curated_ortholog_analysis_runner_yes_run_blocks_empty_interface(
    tmp_path,
    monkeypatch,
) -> None:
    write_embedding_array(tmp_path, 9606, 10)
    write_embedding_array(tmp_path, 109478, 4)

    def fake_download_pdb(pdb_id: str, dest_dir: Path) -> Path:
        path = dest_dir / f"{pdb_id}.pdb"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fake pdb")
        return path

    def fake_extract_interface_residues(
        pdb_path: Path,
        chain_id_r: str,
        chain_id_l: str,
        distance_cutoff: float = 8.0,
    ) -> tuple[list[int], list[int]]:
        return [], []

    monkeypatch.setattr(runner_mod, "download_pdb", fake_download_pdb)
    monkeypatch.setattr(runner_mod, "extract_interface_residues", fake_extract_interface_residues)

    report = run_curated_ortholog_analysis_runner(
        candidate_rows(),
        selection_rows(),
        output_dir=tmp_path,
        pdb_dir=tmp_path / "pdb",
        model_name=DEFAULT_MODEL_NAME,
        yes_run=True,
    )

    row = report.row(0, named=True)

    assert row["reference_embedding_loaded"] is True
    assert row["target_embedding_loaded"] is True
    assert row["interface_residue_count"] == 0
    assert row["interface_residue_status"] == "empty"
    assert row["status"] == "blocked_empty_interface"
    assert row["blocking_reason"] == "interface_residues_empty"
