"""Tests for validation protocol scoring logic."""

from pathlib import Path

import polars as pl

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.validation_protocol import score_candidates


def _make_candidates() -> pl.DataFrame:
    return pl.DataFrame({
        "gene_name": ["SIRT1", "MTOR", "ELN"],
        "uniprot_id": ["Q96EB6", "P42345", "P15502"],
        "category": ["pro-longevity", "pro-longevity", "ecm/hyaluronan"],
    })


def _make_interactome(
    n_partners: list[int],
    is_hub: list[bool],
    size_kda: list[float],
    is_membrane: list[bool],
    has_glycosylation: list[bool],
) -> pl.DataFrame:
    return pl.DataFrame({
        "gene_name": ["SIRT1", "MTOR", "ELN"],
        "n_partners": n_partners,
        "is_hub": is_hub,
        "size_kda": size_kda,
        "is_membrane": is_membrane,
        "has_glycosylation": has_glycosylation,
        "top_partners": ["FOXO3, PPARG", "RPTOR, RICTOR", "FBN1"],
    })


def test_score_candidates_tier_assignment(tmp_path: Path) -> None:
    cfg = PipelineConfig(
        output_dir=tmp_path / "out",
        interim_dir=tmp_path / "interim",
    )
    cfg.ensure_dirs()

    candidates = _make_candidates()
    interactome = _make_interactome(
        n_partners=[5, 50, 3],
        is_hub=[False, True, False],
        size_kda=[40.0, 280.0, 68.0],
        is_membrane=[False, False, False],
        has_glycosylation=[False, False, True],
    )

    scores = score_candidates(candidates, interactome, cfg)
    assert scores.height == 3

    sirt1 = scores.filter(pl.col("gene_name") == "SIRT1").row(0, named=True)
    assert sirt1["priority_tier"] == "high"
    assert sirt1["can_express_cellfree"] is True

    mtor = scores.filter(pl.col("gene_name") == "MTOR").row(0, named=True)
    assert mtor["is_hub"] is True
    assert mtor["under_80kda"] is False
    assert mtor["priority_score"] < sirt1["priority_score"]

    eln = scores.filter(pl.col("gene_name") == "ELN").row(0, named=True)
    assert eln["has_glycosylation"] is True
    assert eln["can_express_cellfree"] is False


def test_score_candidates_empty_interactome(tmp_path: Path) -> None:
    cfg = PipelineConfig(
        output_dir=tmp_path / "out",
        interim_dir=tmp_path / "interim",
    )
    cfg.ensure_dirs()

    candidates = pl.DataFrame({
        "gene_name": ["UNKNOWN"],
        "uniprot_id": ["X00000"],
        "category": ["pro-longevity"],
    })
    interactome = pl.DataFrame({
        "gene_name": ["OTHER"],
        "n_partners": [0],
        "is_hub": [False],
        "size_kda": [0.0],
        "is_membrane": [False],
        "has_glycosylation": [False],
        "top_partners": [""],
    })

    scores = score_candidates(candidates, interactome, cfg)
    assert scores.height == 0
