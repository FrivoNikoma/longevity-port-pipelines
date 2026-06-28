from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

import longevity_port_pipelines.stages.curated_analysis_enrichment as enrichment_mod
from longevity_port_pipelines.stages.curated_analysis_enrichment import (
    DEFAULT_MODEL_NAME,
    empty_curated_ortholog_enrichment_report,
    run_curated_ortholog_enrichment,
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
            "target_sequence": ["M" * 10, "M" * 10],
            "target_sequence_length": [10, 10],
            "curation_status": ["primary_candidate", "supporting_candidate"],
            "evidence_source": ["manual", "manual"],
            "curation_note": ["primary", "supporting"],
        }
    )


def selection_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "pinder_id": [COMPLEX_ID],
            "pdb_id": ["4xhu"],
            "chain_R": ["A"],
            "chain_L": ["B"],
            "receptor_sequence": ["M" * 10],
            "ligand_sequence": ["N" * 5],
            "uniprot_R": ["P09874"],
            "uniprot_L": ["Q9UNS1"],
        }
    )


def write_embedding_array(tmp_path: Path, species_taxid: int, values: np.ndarray) -> None:
    path = embedding_path(
        output_dir=tmp_path,
        model_name=DEFAULT_MODEL_NAME,
        complex_id=COMPLEX_ID,
        chain="receptor",
        species_taxid=species_taxid,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, values.astype(np.float32))


def write_enrichment_test_embeddings(tmp_path: Path) -> None:
    reference = np.zeros((10, 3), dtype=np.float32)
    target = np.ones((10, 3), dtype=np.float32)

    target[1] = 8.0
    target[2] = 10.0
    target[3] = 12.0

    write_embedding_array(tmp_path, 9606, reference)
    write_embedding_array(tmp_path, 109478, target)


def patch_interface(monkeypatch, residues: list[int]) -> None:
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
        return residues, [0]

    monkeypatch.setattr(enrichment_mod, "download_pdb", fake_download_pdb)
    monkeypatch.setattr(
        enrichment_mod, "extract_interface_residues", fake_extract_interface_residues
    )


def write_negatome_control_pairs(tmp_path: Path) -> Path:
    path = tmp_path / "negatome_control_pairs.csv"
    pl.DataFrame(
        {
            "complex_id": [COMPLEX_ID],
            "chain": ["receptor"],
            "target_species": ["brandts_bat"],
            "source_uniprot": ["P09874"],
            "negative_partner_uniprot": ["NEG1"],
            "negative_partner_source": ["synthetic"],
            "negative_partner_sequence": ["A" * 10],
            "control_type": ["synthetic_negatome"],
        }
    ).write_csv(path)
    return path


def test_empty_curated_ortholog_enrichment_report_has_expected_columns() -> None:
    report = empty_curated_ortholog_enrichment_report()

    assert report.is_empty()
    assert "enrichment_ratio" in report.columns
    assert "control_status" in report.columns
    assert "interpretation_status" in report.columns


def test_curated_ortholog_enrichment_dry_run_reports_ready_plan(tmp_path: Path) -> None:
    write_enrichment_test_embeddings(tmp_path)

    report = run_curated_ortholog_enrichment(
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
    assert row["status"] == "dry_run_ready"
    assert row["blocking_reason"] == "ready"
    assert row["control_status"] == "not_run"
    assert row["interpretation_status"] == "not_computed"
    assert row["enrichment_ratio"] is None


def test_curated_ortholog_enrichment_dry_run_reports_blocked_plan(tmp_path: Path) -> None:
    report = run_curated_ortholog_enrichment(
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


def test_curated_ortholog_enrichment_yes_run_computes_technical_checkpoint(
    tmp_path: Path,
    monkeypatch,
) -> None:
    write_enrichment_test_embeddings(tmp_path)
    patch_interface(monkeypatch, residues=[1, 2, 3])

    report = run_curated_ortholog_enrichment(
        candidate_rows(),
        selection_rows(),
        output_dir=tmp_path,
        pdb_dir=tmp_path / "pdb",
        model_name=DEFAULT_MODEL_NAME,
        yes_run=True,
        n_permutations=20,
    )

    row = report.row(0, named=True)
    assert row["run_mode"] == "yes-run"
    assert row["status"] == "enrichment_completed"
    assert row["blocking_reason"] == "ready"
    assert row["control_status"] == "missing_negatome"
    assert row["interpretation_status"] == "preliminary_shuffled_only"
    assert row["interface_residue_count"] == 3
    assert row["reference_embedding_shape"] == "10x3"
    assert row["target_embedding_shape"] == "10x3"
    assert row["enrichment_ratio"] > 1.0
    assert row["shuffled_control_ratio"] is not None
    assert row["negatome_control_ratio"] is None
    assert row["mann_whitney_p"] is not None
    assert row["effect_size_cohens_d"] > 0.0


def test_curated_ortholog_enrichment_yes_run_blocks_empty_interface(
    tmp_path: Path,
    monkeypatch,
) -> None:
    write_enrichment_test_embeddings(tmp_path)
    patch_interface(monkeypatch, residues=[])

    report = run_curated_ortholog_enrichment(
        candidate_rows(),
        selection_rows(),
        output_dir=tmp_path,
        pdb_dir=tmp_path / "pdb",
        model_name=DEFAULT_MODEL_NAME,
        yes_run=True,
        n_permutations=20,
    )

    row = report.row(0, named=True)
    assert row["run_mode"] == "yes-run"
    assert row["status"] == "blocked_empty_interface"
    assert row["blocking_reason"] == "interface_residues_empty"
    assert row["reference_embedding_shape"] == "10x3"
    assert row["target_embedding_shape"] == "10x3"
    assert row["enrichment_ratio"] is None


def test_curated_ortholog_enrichment_yes_run_applies_negatome_control(
    tmp_path: Path,
    monkeypatch,
) -> None:
    write_enrichment_test_embeddings(tmp_path)
    pairs_path = write_negatome_control_pairs(tmp_path)
    patch_interface(monkeypatch, residues=[1, 2, 3])

    def fake_resolve_negatome_control_ratio(**kwargs) -> float:
        pair_rows = kwargs["pair_rows"]
        assert pair_rows[0]["negative_partner_uniprot"] == "NEG1"
        return 0.9

    monkeypatch.setattr(
        enrichment_mod,
        "resolve_negatome_control_ratio",
        fake_resolve_negatome_control_ratio,
    )

    report = run_curated_ortholog_enrichment(
        candidate_rows(),
        selection_rows(),
        output_dir=tmp_path,
        interim_dir=tmp_path,
        negatome_control_pairs=pairs_path,
        pdb_dir=tmp_path / "pdb",
        model_name=DEFAULT_MODEL_NAME,
        yes_run=True,
        n_permutations=20,
    )

    row = report.row(0, named=True)
    assert row["status"] == "enrichment_completed"
    assert row["control_status"] == "has_shuffled_and_negatome"
    assert row["interpretation_status"] == "controlled_pass"
    assert row["negatome_control_ratio"] == 0.9
