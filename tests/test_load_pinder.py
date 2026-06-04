"""Tests for PINDER ID parsing and candidate selection filtering."""

import polars as pl

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.load_pinder import parse_pinder_id, select_candidates


def _make_pinder_lf(
    ids: list[str],
    contacts: list[int] | None = None,
    predicted_r: list[bool] | None = None,
    predicted_l: list[bool] | None = None,
    seq_r: list[str] | None = None,
    seq_l: list[str] | None = None,
) -> pl.LazyFrame:
    n = len(ids)
    return pl.DataFrame({
        "id": ids,
        "intermolecular_contacts": contacts or [20] * n,
        "predicted_R": predicted_r or [False] * n,
        "predicted_L": predicted_l or [False] * n,
        "receptor_sequence": seq_r or ["MKTLVGAA"] * n,
        "ligand_sequence": seq_l or ["AQVGLMKT"] * n,
    }).lazy()


def test_parse_pinder_id_extracts_fields() -> None:
    lf = _make_pinder_lf(["2wyy__C2_P03521--2wyy__H3_Q12345"])
    result = parse_pinder_id(lf).collect()

    row = result.row(0, named=True)
    assert row["pdb_id"] == "2wyy"
    assert row["chain_R"] == "C2"
    assert row["uniprot_R"] == "P03521"
    assert row["chain_L"] == "H3"
    assert row["uniprot_L"] == "Q12345"


def test_parse_pinder_id_multiple_entries() -> None:
    lf = _make_pinder_lf([
        "1abc__A1_P11111--1abc__B1_P22222",
        "4xyz__X1_Q99999--4xyz__Y1_Q88888",
    ])
    result = parse_pinder_id(lf).collect()
    assert result.height == 2
    assert result.row(1, named=True)["pdb_id"] == "4xyz"


def test_select_candidates_filters_predicted_structures() -> None:
    lf = _make_pinder_lf(
        ids=[
            "1abc__A_P11111--1abc__B_P22222",
            "2def__A_P33333--2def__B_P44444",
        ],
        predicted_r=[True, False],
        predicted_l=[False, False],
    )
    cfg = PipelineConfig(selection_count=10)
    result = select_candidates(lf, cfg).collect()
    assert result.height == 1
    assert "P33333" in result.get_column("uniprot_R").to_list()


def test_select_candidates_filters_low_contacts() -> None:
    lf = _make_pinder_lf(
        ids=[
            "1abc__A_P11111--1abc__B_P22222",
            "2def__A_P33333--2def__B_P44444",
        ],
        contacts=[2, 20],
    )
    cfg = PipelineConfig(selection_count=10, min_interface_contacts=5)
    result = select_candidates(lf, cfg).collect()
    assert result.height == 1


def test_select_candidates_deduplicates_uniprot_pairs() -> None:
    lf = _make_pinder_lf(
        ids=[
            "1abc__A_P11111--1abc__B_P22222",
            "2def__A_P22222--2def__B_P11111",  # same pair, reversed
        ],
        contacts=[30, 20],
    )
    cfg = PipelineConfig(selection_count=10)
    result = select_candidates(lf, cfg).collect()
    assert result.height == 1
    assert result.row(0, named=True)["intermolecular_contacts"] == 30


def test_select_candidates_respects_selection_count() -> None:
    ids = [f"{i:04d}__A_P{i:05d}--{i:04d}__B_Q{i:05d}" for i in range(50)]
    lf = _make_pinder_lf(ids)
    cfg = PipelineConfig(selection_count=5)
    result = select_candidates(lf, cfg).collect()
    assert result.height == 5
