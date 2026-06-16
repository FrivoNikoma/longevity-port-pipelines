from __future__ import annotations

import numpy as np
import pytest

from longevity_port_pipelines.stages import embed


class FakeClient:
    def __init__(self, embeddings: np.ndarray) -> None:
        self._embeddings = embeddings

    def encode(self, protein: object) -> object:
        return protein

    def logits(self, protein_tensor: object, config: object) -> object:
        assert protein_tensor is not None
        assert config is not None

        class Output:
            pass

        output = Output()
        output.embeddings = self._embeddings
        return output


def test_embed_sequence_returns_per_residue_embeddings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_embeddings = np.arange(12, dtype=np.float32).reshape(3, 4)

    def fake_get_esmc_client(*args: object, **kwargs: object) -> FakeClient:
        assert args or kwargs
        return FakeClient(fake_embeddings)

    monkeypatch.setattr(embed, "get_esmc_client", fake_get_esmc_client)

    arr = embed.embed_sequence(
        sequence="ACD",
        model="esmc-test",
        api_url="https://example.invalid",
        token="fake-token",
    )

    assert arr.shape == (3, 4)
    assert arr.dtype == np.float32


def test_embed_sequence_trims_extra_special_tokens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_embeddings = np.arange(20, dtype=np.float32).reshape(5, 4)

    def fake_get_esmc_client(*args: object, **kwargs: object) -> FakeClient:
        assert args or kwargs
        return FakeClient(fake_embeddings)

    monkeypatch.setattr(embed, "get_esmc_client", fake_get_esmc_client)

    arr = embed.embed_sequence(
        sequence="ACD",
        model="esmc-test",
        api_url="https://example.invalid",
        token="fake-token",
    )

    assert arr.shape == (3, 4)


def test_embed_sequence_rejects_too_short_embeddings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_embeddings = np.arange(8, dtype=np.float32).reshape(2, 4)

    def fake_get_esmc_client(*args: object, **kwargs: object) -> FakeClient:
        assert args or kwargs
        return FakeClient(fake_embeddings)

    monkeypatch.setattr(embed, "get_esmc_client", fake_get_esmc_client)

    with pytest.raises(ValueError, match="Expected at least 3 residue embeddings"):
        embed.embed_sequence(
            sequence="ACD",
            model="esmc-test",
            api_url="https://example.invalid",
            token="fake-token",
        )
