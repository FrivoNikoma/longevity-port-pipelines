"""Tests for candidate CSV loading."""

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages.candidates import (
    candidates_dataframe,
)


def _write_csv(tmp_path: Path, content: str) -> None:
    (tmp_path / "candidates.csv").write_text(content)


def test_loads_valid_csv(tmp_path: Path) -> None:
    _write_csv(tmp_path, (
        "gene_name,uniprot_id,category,description\n"
        "GDF15,Q99988,pro-longevity,\"Growth differentiation factor 15\"\n"
        "FOXO3,O43524,pro-longevity,\"Forkhead TF\"\n"
    ))
    df = candidates_dataframe(tmp_path)
    assert df.height == 2
    assert set(df.get_column("gene_name").to_list()) == {"GDF15", "FOXO3"}


def test_skips_comment_lines(tmp_path: Path) -> None:
    _write_csv(tmp_path, (
        "gene_name,uniprot_id,category,description\n"
        "# this is a comment\n"
        "GDF15,Q99988,pro-longevity,\"Growth differentiation factor 15\"\n"
        "# another comment\n"
    ))
    df = candidates_dataframe(tmp_path)
    assert df.height == 1


def test_raises_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        candidates_dataframe(tmp_path)


def test_raises_on_empty_csv(tmp_path: Path) -> None:
    _write_csv(tmp_path, "gene_name,uniprot_id,category,description\n")
    with pytest.raises(ValueError):
        candidates_dataframe(tmp_path)


def test_raises_on_missing_column(tmp_path: Path) -> None:
    _write_csv(tmp_path, "gene_name,category\nFOO,pro-longevity\n")
    with pytest.raises(ValueError):
        candidates_dataframe(tmp_path)


def test_deduplicates_by_gene_name(tmp_path: Path) -> None:
    _write_csv(tmp_path, (
        "gene_name,uniprot_id,category,description\n"
        "SIRT1,Q96EB6,pro-longevity,\"first\"\n"
        "SIRT1,Q99999,pro-longevity,\"duplicate\"\n"
    ))
    df = candidates_dataframe(tmp_path)
    assert df.height == 1
    assert df.row(0, named=True)["uniprot_id"] == "Q96EB6"


def test_adds_description_column_if_missing(tmp_path: Path) -> None:
    _write_csv(tmp_path, "gene_name,uniprot_id,category\nFOXO3,O43524,pro-longevity\n")
    df = candidates_dataframe(tmp_path)
    assert "description" in df.columns


def test_real_candidates_csv() -> None:
    """Smoke test: the checked-in candidates.csv loads without error."""
    input_dir = Path("data/input")
    if not (input_dir / "candidates.csv").exists():
        pytest.skip("data/input/candidates.csv not present")
    df = candidates_dataframe(input_dir)
    assert df.height >= 20
