from pathlib import Path

from scripts.analyze_saved_embeddings_mapped import embedding_path


def test_embedding_path_uses_embedding_dir_directly() -> None:
    path = embedding_path(
        Path("custom/embeddings"),
        "esmc-300m-2024-12",
        "8bot__U1_P13010--8bot__T1_P12956",
        "receptor",
        9606,
    )

    assert path == Path(
        "custom/embeddings/esmc-300m-2024-12/8bot__U1_P13010--8bot__T1_P12956_receptor_9606.npy"
    )
