from scripts.export_mapped_residue_deltas import parse_args


def test_export_mapped_residue_deltas_accepts_embedding_dir(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "export_mapped_residue_deltas.py",
            "--embedding-dir",
            "custom/embeddings",
        ],
    )

    args = parse_args()

    assert args.embedding_dir == "custom/embeddings"
