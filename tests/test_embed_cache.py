from pathlib import Path

import numpy as np
import pytest

from longevity_port_pipelines.stages import embed


def test_embedding_path_matches_saved_filename_convention(tmp_path: Path) -> None:
    path = embed.embedding_path(
        output_dir=tmp_path,
        model_name="esmc-300m-2024-12",
        complex_id="1abc__A1_P11111--1abc__B1_Q22222",
        chain="receptor",
        species_taxid=9606,
    )

    assert path == (
        tmp_path
        / "embeddings"
        / "esmc-300m-2024-12"
        / "1abc__A1_P11111--1abc__B1_Q22222_receptor_9606.npy"
    )


def test_embed_or_load_sequence_reuses_existing_embedding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sequence = "ACDE"
    saved = np.ones((len(sequence), 3), dtype=np.float32)
    path = embed.embedding_path(
        output_dir=tmp_path,
        model_name="model",
        complex_id="complex",
        chain="ligand",
        species_taxid=10090,
    )
    path.parent.mkdir(parents=True)
    np.save(path, saved)

    def fail_embed_sequence(
        sequence: str,
        model: str,
        api_url: str,
        token: str,
        timeout: int = 180,
    ) -> np.ndarray:
        raise AssertionError("Biohub should not be called for existing embeddings")

    monkeypatch.setattr(embed, "embed_sequence", fail_embed_sequence)

    emb = embed.embed_or_load_sequence(
        complex_id="complex",
        chain="ligand",
        sequence=sequence,
        species_taxid=10090,
        model="model",
        api_url="https://example.invalid",
        token="token",
        output_dir=tmp_path,
    )

    assert emb.species_taxid == 10090
    assert emb.chain == "ligand"
    np.testing.assert_array_equal(emb.embeddings, saved)


def test_embed_or_load_sequence_writes_missing_embedding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sequence = "ACDE"
    generated = np.arange(len(sequence) * 2, dtype=np.float32).reshape(len(sequence), 2)

    calls: list[str] = []

    def fake_embed_sequence(
        sequence: str,
        model: str,
        api_url: str,
        token: str,
        timeout: int = 180,
    ) -> np.ndarray:
        calls.append(sequence)
        return generated

    monkeypatch.setattr(embed, "embed_sequence", fake_embed_sequence)

    emb = embed.embed_or_load_sequence(
        complex_id="complex",
        chain="receptor",
        sequence=sequence,
        species_taxid=9606,
        model="model",
        api_url="https://example.invalid",
        token="token",
        output_dir=tmp_path,
    )

    path = embed.embedding_path(
        output_dir=tmp_path,
        model_name="model",
        complex_id="complex",
        chain="receptor",
        species_taxid=9606,
    )

    assert calls == [sequence]
    assert path.exists()
    np.testing.assert_array_equal(emb.embeddings, generated)
    np.testing.assert_array_equal(np.load(path), generated)
