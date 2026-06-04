"""Tests for embedding save/load roundtrip and config directory creation."""

from pathlib import Path

import numpy as np

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.embed import PerResidueEmbedding, save_embeddings


def test_save_embeddings_roundtrip(tmp_path: Path) -> None:
    emb = PerResidueEmbedding(
        complex_id="1abc_A_P12345--1abc_B_Q67890",
        chain="receptor",
        species_taxid=9606,
        model_name="esmc_600m",
        sequence="MKTLVGAA",
        embeddings=np.random.default_rng(42).normal(size=(8, 480)).astype(np.float32),
    )

    saved_path = save_embeddings(emb, tmp_path)
    assert saved_path.exists()
    assert saved_path.suffix == ".npy"

    loaded = np.load(saved_path)
    np.testing.assert_array_equal(loaded, emb.embeddings)
    assert loaded.shape == (8, 480)
    assert loaded.dtype == np.float32


def test_ensure_dirs_creates_nested_structure(tmp_path: Path) -> None:
    cfg = PipelineConfig(
        input_dir=tmp_path / "deep" / "in",
        interim_dir=tmp_path / "deep" / "interim",
        output_dir=tmp_path / "deep" / "out",
    )
    cfg.ensure_dirs()
    assert (tmp_path / "deep" / "in").is_dir()
    assert (tmp_path / "deep" / "interim").is_dir()
    assert (tmp_path / "deep" / "out").is_dir()
    assert (tmp_path / "deep" / "out" / "plots").is_dir()
